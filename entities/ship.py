from panda3d.core import Vec3, Quat, CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay, BitMask32, NodePath, get_model_path
from panda3d import core as pc
from direct.showbase.DirectObject import DirectObject
import math
import os
import random
import heapq

# --- KONSTANSOK ÉS BEÁLLÍTÁSOK ---
NUM_SYSTEMS = 100
MAX_COORD = 500
NEIGHBOR_COUNT = 3
MAP_SCALE = 0.001
MAP_SIZE = 0.3

# --- MODEL ÚTVONAL BEÁLLÍTÁSA ---
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, "assets", "models")

if os.path.exists(models_dir):
    get_model_path().prepend_directory(models_dir)
else:
    get_model_path().prepend_directory(base_dir)

# Fallback generátor aszteroidákhoz
try:
    from systems.generation import AsteroidGenerator
except ImportError:
    class AsteroidGenerator:
        def generate(self, name="Box", min_scale=1.0, max_scale=1.1):
            return loader.loadModel("models/box")

# Komponens importok (MiningLaser stb.)
try:
    from .components import DamageType, MiningLaser, WeaponMount, TacticalSlot, ArmorSlot, HullAugment
except ImportError:
    class DamageType: IMPACT, THERMIC, IONIC, DETONATION = range(4)
    class MiningLaser:
        def __init__(self):
            self.range, self.resource_type, self.resource_yield = 150, "Vas", 5
    class WeaponMount: pass
    class TacticalSlot: pass
    class ArmorSlot: pass
    class HullAugment: pass

# ==============================================================================
# GALAXY MANAGER - Térkép és Útvonalkereső Logika
# ==============================================================================
class GalaxyManager:
    def __init__(self, app):
        self.app = app
        self.systems = []
        self.adjacency_list = {}
        self.connections = []
        self.path_route = []
        self.current_path_cost = 0.0
        
        # 3D Geometria (Csak pontfelhő és vonalak, nincs doboz!)
        self.galaxy_vdata = None
        self.galaxy_color_writer = None
        self.galaxy_np = None
        self.path_np_3d = render.attachNewNode("path_3d_lines")
        
        # 2D HUD
        self.map_visible = False
        self.map_root_2d = None
        self.hud_text_np = None

    def generate_galaxy(self):
        for i in range(NUM_SYSTEMS):
            pos = pc.LVector3(random.uniform(-MAX_COORD, MAX_COORD),
                              random.uniform(-MAX_COORD, MAX_COORD),
                              random.uniform(-MAX_COORD / 3, MAX_COORD / 3))
            self.systems.append({
                'id': i, 'name': f"Rendszer-{i:03d}", 'pos': pos,
                'color': pc.LVector4(random.random(), random.random(), random.random(), 1)
            })

        self.adjacency_list = {i: [] for i in range(NUM_SYSTEMS)}
        conn_set = set()
        for i in range(NUM_SYSTEMS):
            distances = sorted([((self.systems[i]['pos'] - self.systems[j]['pos']).length(), j) for j in range(NUM_SYSTEMS) if i != j])
            for k in range(min(NEIGHBOR_COUNT, len(distances))):
                neighbor_j = distances[k][1]
                self.adjacency_list[i].append((neighbor_j, distances[k][0]))
                conn_set.add(tuple(sorted((i, neighbor_j))))
        self.connections = list(conn_set)

    def create_visuals(self):
        format_star = pc.GeomVertexFormat.getV3c4()
        self.galaxy_vdata = pc.GeomVertexData('galaxy', format_star, pc.Geom.UHDynamic)
        vw = pc.GeomVertexWriter(self.galaxy_vdata, 'vertex')
        cw = pc.GeomVertexWriter(self.galaxy_vdata, 'color')
        
        star_points = pc.GeomPoints(pc.Geom.UHDynamic)
        for s in self.systems:
            vw.addData3f(s['pos'])
            cw.addData4f(s['color'])
            star_points.addVertex(s['id'])
            
        star_lines = pc.GeomLines(pc.Geom.UHDynamic)
        for i1, i2 in self.connections:
            star_lines.addVertices(i1, i2)
            
        galaxy_node = pc.GeomNode('galaxy_node')
        for prim in [star_points, star_lines]:
            geom = pc.Geom(self.galaxy_vdata)
            geom.addPrimitive(prim)
            galaxy_node.addGeom(geom)

        self.galaxy_np = render.attachNewNode(galaxy_node)
        self.galaxy_np.setTransparency(pc.TransparencyAttrib.MAlpha)
        self.galaxy_np.hide()

    def toggle_map(self):
        self.map_visible = not self.map_visible
        if self.map_visible: self.galaxy_np.show()
        else: self.galaxy_np.hide()

    def redraw_2d_map(self, current_pos, current_idx):
        # Minitérkép HUD frissítés ide jönne
        pass

# ==============================================================================
# BASE ENTITY CLASS
# ==============================================================================
class Entity(DirectObject):
    def __init__(self, manager, entity_id, name="Objektum", entity_type="Entity"):
        self.manager = manager
        self.id = entity_id
        self.name = name
        self.entity_type = entity_type
        self.model = None

    def load_model(self, path, scale=1.0, color=None):
        try:
            # Csak akkor töltünk be modellt, ha létezik az útvonal
            self.model = loader.loadModel(path)
        except Exception:
            # Ha nem sikerül, akkor rakunk ki egy KICSI jelző dobozt fallbacknek
            self.model = loader.loadModel("models/box")
            self.model.setScale(0.1) # Kicsi, hogy ne zavarjon
            print(f"[ENTITY] Hiba: Modell nem található ({path}), fallback aktív.")
            
        self.model.setScale(self.model.getScale() * scale)
        self.model.reparentTo(render)
        if color: self.model.setColor(*color)

    def get_pos(self): return self.model.getPos() if self.model else Vec3(0,0,0)
    def set_pos(self, x, y, z): 
        if self.model: self.model.setPos(x, y, z)
    def destroy(self):
        if self.model: self.model.removeNode()
        self.ignoreAll()
    def update(self, dt):
        """A bolygók statikusak, de a metódus jelenléte megakadályozza a crash-t."""
        pass
# ==============================================================================
# SHIP CLASS - JAVÍTOTT MARKER KEZELÉSSEL
# ==============================================================================
class Ship(Entity):
    def __init__(self, manager, ship_id, is_local=False, name="Ismeretlen", ship_type="Vadász"):
        super().__init__(manager, ship_id, name, ship_type)
        self.is_local = is_local
        
        self.base_stats = {'hp': 1000.0, 'shield': 500.0, 'armor': 200.0, 'capacitor': 100.0, 'speed': 40.0, 'agility': 3.0, 'shield_regen': 5.0, 'cap_regen': 2.0, 'drag': 1.5}
        self.current_values = self.base_stats.copy()
        self.effective_stats = self.base_stats.copy()
        
        self.equipment = {'core': None, 'support': None, 'system': None, 'mining': [MiningLaser()] if is_local else []}
        self.current_system_idx = 0
        self.velocity = Vec3(0, 0, 0)
        self.target_entity = None
        self.autopilot_mode = "follow"
        
        self.dragging = False
        self.last_mouse_x = self.last_mouse_y = 0.0
        self.cam_dist, self.cam_h, self.cam_p = 40.0, 0.0, -20.0

        # Modell betöltése (Ha nincs meg az egg, doboz lesz, de jelezni fogja)
        self.load_model("./assets/models/SpaceShip.egg", scale=1.0)
        
        if self.is_local:
            if self.model: self.model.setColor(1, 1, 1, 1)
            self.setup_physics_and_camera()
            self.recalculate_stats()
            self.setup_controls()
            self.accept("space", self.fire_mining_laser)
        else:
            if self.model: self.model.setCollideMask(BitMask32.bit(1))

    # --- KOMPATIBILITÁSI RÉTEG ÉS PROPERTY-K ---
    @property
    def core(self): return self.equipment['core']
    @core.setter
    def core(self, val): self.equipment['core'] = val

    # --- TÁRGY FELSZERELŐ METÓDUSOK ---
    def equip_core(self, core_obj):
        self.core = core_obj
        self.recalculate_stats()
        print(f"[SHIP] {self.name} felszerelte a magot: {core_obj.name}")

    def equip_support(self, support_obj):
        self.equipment['support'] = support_obj
        self.recalculate_stats()
        print(f"[SHIP] {self.name} felszerelte a support modult: {support_obj.name}")

    def equip_system(self, system_obj):
        self.equipment['system'] = system_obj
        self.recalculate_stats()
        print(f"[SHIP] {self.name} felszerelte a rendszert: {system_obj.name}")

    def recalculate_stats(self):
        new_stats = self.base_stats.copy()
        if self.core:
            if hasattr(self.core, 'shipMaxVelocity'):
                new_stats['speed'] *= (1.0 + self.core.shipMaxVelocity)
            if hasattr(self.core, 'shipAgility'):
                new_stats['agility'] *= (1.0 + self.core.shipAgility)
        
        # Support/System bónuszok is itt adhatók hozzá a statokhoz
        self.effective_stats = new_stats
        
        # Aktuális értékek korlátozása az új maximumokhoz
        for stat in ['hp', 'shield', 'armor', 'capacitor']:
            if stat in self.current_values and stat in self.effective_stats:
                self.current_values[stat] = min(self.current_values[stat], self.effective_stats[stat])

    def setup_controls(self):
        if hasattr(self.manager, 'window_manager'):
            self.accept("i", self.manager.window_manager.toggle_inventory)
            self.accept("m", self.manager.window_manager.toggle_market)
        
        # Térkép megnyitása (F10)
        if hasattr(self.manager, 'galaxy_manager'):
            self.accept("f10", self.manager.galaxy_manager.toggle_map)
            
        # MARKER LERAKÁSA - KIZÁRÓLAG GOMBNYOMÁSRA (B)


    def setup_physics_and_camera(self):
        self.camera_pivot = render.attachNewNode("CameraPivot")
        self.accept("mouse3", self.start_camera_drag)
        self.accept("mouse3-up", self.stop_camera_drag)
        self.accept("wheel_up", self.adjust_zoom, [-5.0])
        self.accept("wheel_down", self.adjust_zoom, [5.0])

    def start_camera_drag(self):
        self.dragging = True
        if base.mouseWatcherNode.hasMouse():
            m = base.mouseWatcherNode.getMouse()
            self.last_mouse_x, self.last_mouse_y = m.x, m.y

    def stop_camera_drag(self): self.dragging = False
    def adjust_zoom(self, amt): self.cam_dist = max(10.0, min(150.0, self.cam_dist + amt))

    def update(self, dt):
        if not self.is_local or not self.model: return
        
        # Regeneráció
        self.current_values['shield'] = min(self.effective_stats['shield'], 
            self.current_values['shield'] + self.effective_stats['shield_regen'] * dt)
        
        # Mozgás súrlódással
        if not self.target_entity:
            self.velocity *= (1.0 - self.effective_stats['drag'] * dt)
            self.model.setPos(self.model.getPos() + self.velocity * dt)
        else:
            self.run_autopilot(dt)
            
        self.update_orientation(dt)
        self.update_camera(dt)

    def update_camera(self, dt):
        if self.dragging and base.mouseWatcherNode.hasMouse():
            m = base.mouseWatcherNode.getMouse()
            dx, dy = m.x - self.last_mouse_x, m.y - self.last_mouse_y
            self.last_mouse_x, self.last_mouse_y = m.x, m.y
            self.cam_h -= dx * 100.0
            self.cam_p = max(-85, min(85, self.cam_p + dy * 100.0))

        self.camera_pivot.setPos(self.model.getPos())
        self.camera_pivot.setHpr(self.cam_h, self.cam_p, 0)
        base.camera.reparentTo(self.camera_pivot)
        base.camera.setPos(0, -self.cam_dist, 0)
        base.camera.lookAt(self.camera_pivot)

    def update_orientation(self, dt):
        if self.velocity.length() > 1.0:
            target_quat = self.get_lookat_quat(self.model.getPos() + self.velocity)
            t = min(1.0, self.effective_stats['agility'] * dt)
            new_quat = self.model.getQuat() * (1.0 - t) + target_quat * t
            new_quat.normalize()
            self.model.setQuat(new_quat)

    def get_lookat_quat(self, target_pos):
        temp = render.attachNewNode("temp")
        temp.setPos(self.model.getPos())
        temp.lookAt(target_pos)
        q = temp.getQuat()
        temp.removeNode()
        return q

    def fire_mining_laser(self): print("[SHIP] Bányász lézer tüzelés...")

    def run_autopilot(self, dt):
        diff = self.target_entity.get_pos() - self.model.getPos()
        dist = diff.length()
        dir = diff.normalized() if dist > 0 else Vec3(0,0,0)
        speed = self.effective_stats['speed']
        
        if self.autopilot_mode == "follow" and dist > 2.0:
            self.velocity = dir * (speed * 0.8)
        self.model.setPos(self.model.getPos() + self.velocity * dt)
from panda3d.core import Vec3, Quat, CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay, BitMask32, NodePath, get_model_path
from direct.showbase.DirectObject import DirectObject
import math
import os

# --- MODEL ÚTVONAL BEÁLLÍTÁSA ---
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, "assets", "models")

if os.path.exists(models_dir):
    get_model_path().prepend_directory(models_dir)
else:
    get_model_path().prepend_directory(base_dir)

# Megjegyzés: A systems.generation-t csak akkor importáljuk, ha létezik a projektben
try:
    from systems.generation import AsteroidGenerator
except ImportError:
    class AsteroidGenerator:
        def generate(self, name="Box", min_scale=1.0, max_scale=1.1):
            return loader.loadModel("models/box")

# Feltételezett komponens importok
try:
    from .components import DamageType, MiningLaser, WeaponMount, TacticalSlot, ArmorSlot, HullAugment
except ImportError:
    class DamageType:
        IMPACT, THERMIC, IONIC, DETONATION = range(4)
    class MiningLaser:
        def __init__(self):
            self.range = 150
            self.resource_type = "Vas"
            self.resource_yield = 5
    class WeaponMount: pass
    class TacticalSlot: pass
    class ArmorSlot: pass
    class HullAugment: pass

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
        model_loaded = False
        try:
            self.model = loader.loadModel(path)
            if self.model:
                 model_loaded = True
        except Exception:
            pass
        
        if not model_loaded:
            print(f"[WARNING] Fallback modell használata a következőhöz: {path}")
            if self.entity_type == "Aszteroida":
                generator = AsteroidGenerator() 
                self.model = generator.generate(name=self.name, min_scale=scale)
            else:
                self.model = loader.loadModel("models/box")
                self.model.setScale(0.5, 1.5, 0.3) 
            
        self.model.setScale(self.model.getScale() * scale)
        self.model.reparentTo(render)
        if color: self.model.setColor(*color)

    def get_pos(self):
        return self.model.getPos() if self.model else Vec3(0,0,0)

    def set_pos(self, x, y, z):
        if self.model:
            self.model.setPos(x, y, z)

    def destroy(self):
        if self.model: self.model.removeNode()
        self.ignoreAll()

    def update(self, dt):
        pass

# ==============================================================================
# SHIP CLASS - REFAKTORÁLT STAT RENDSZERREL
# ==============================================================================
class Ship(Entity):
    def __init__(self, manager, ship_id, is_local=False, name="Ismeretlen", ship_type="Vadász"):
        super().__init__(manager, ship_id, name, ship_type)
        self.is_local = is_local
        
        # --- 1. CSOPORTOSÍTOTT STATISZTIKÁK (BÁZIS ÉRTÉKEK) ---
        self.base_stats = {
            'hp': 1000.0,
            'shield': 500.0,
            'armor': 200.0,
            'capacitor': 100.0,
            'speed': 40.0,
            'agility': 3.0,
            'shield_regen': 5.0,
            'cap_regen': 2.0,
            'drag': 1.5
        }

        # --- 2. DINAMIKUS (AKTUÁLIS) ÉRTÉKEK ---
        self.current_values = {
            'hp': 1000.0,
            'shield': 500.0,
            'armor': 200.0,
            'capacitor': 100.0
        }

        # --- 3. SZÁMÍTOTT (MODIFIKÁLT) MAX ÉRTÉKEK ---
        self.effective_stats = self.base_stats.copy()

        # --- 4. ELLENÁLLÁSOK ÉS BÓNUSZOK ---
        self.resistances = {dt: 0.0 for dt in range(4)}
        self.damage_bonuses = {dt: 1.0 for dt in range(4)}
        
        # --- 5. FELSZERELÉS ---
        self.equipment = {
            'core': None,
            'support': None,
            'system': None,
            'weapons': [],
            'tactical': [],
            'armor_plating': [],
            'mining': [MiningLaser()] if is_local else []
        }

        # Fizika/Kamera állapot
        self.velocity = Vec3(0, 0, 0)
        self.target_entity = None
        self.autopilot_mode = "follow" # Alapértelmezett mód
        
        # Kamera változók
        self.dragging = False
        self.last_mouse_x = 0.0
        self.last_mouse_y = 0.0
        self.cam_dist = 40.0
        self.cam_h = 0.0 # Heading (vízszintes)
        self.cam_p = -20.0 # Pitch (függőleges)

        # Inicializálás
        self.load_model("SpaceShip.egg", scale=1.0)
        
        if self.is_local:
            if self.model: self.model.setColor(1, 1, 1, 1)
            self.setup_physics_and_camera()
            self.recalculate_stats()
            self.setup_controls()
            self.equip_test_items()
            self.accept("space", self.fire_mining_laser)
        else:
            if self.model: self.model.setCollideMask(BitMask32.bit(1))

    # --- KOMPATIBILITÁSI RÉTEG ---
    @property
    def core(self): return self.equipment['core']
    @core.setter
    def core(self, val): self.equipment['core'] = val

    @property
    def support(self): return self.equipment['support']
    @support.setter
    def support(self, val): self.equipment['support'] = val

    @property
    def system(self): return self.equipment['system']
    @system.setter
    def system(self, val): self.equipment['system'] = val

    # --- TÁRGY FELSZERELŐ METÓDUSOK ---

    def equip_core(self, core_obj):
        self.core = core_obj
        self.recalculate_stats()
        print(f"[SHIP] {self.name} felszerelte a magot: {core_obj.name}")

    def equip_support(self, support_obj):
        self.support = support_obj
        self.recalculate_stats()
        print(f"[SHIP] {self.name} felszerelte a support modult: {support_obj.name}")

    def equip_system(self, system_obj):
        self.system = system_obj
        self.recalculate_stats()
        print(f"[SHIP] {self.name} felszerelte a rendszert: {system_obj.name}")

    def setup_controls(self):
        if hasattr(self.manager, 'window_manager'):
            self.accept("i", self.manager.window_manager.toggle_inventory)
            self.accept("m", self.manager.window_manager.toggle_market)

    def equip_test_items(self):
        print(f"[SHIP] Teszt itemek előkészítve.")

    def setup_physics_and_camera(self):
        # Sugár az ütközésvizsgálathoz
        self.cTrav = CollisionTraverser()
        self.cQueue = CollisionHandlerQueue()
        self.ray = CollisionRay()
        self.ray_np = render.attachNewNode(CollisionNode('miningRay'))
        self.ray_np.node().addSolid(self.ray)
        self.ray_np.node().setFromCollideMask(BitMask32.bit(1))
        self.cTrav.addCollider(self.ray_np, self.cQueue)

        # Kamera pivot (ez követi a hajót)
        self.camera_pivot = render.attachNewNode("CameraPivot")
        
        # Egér események
        self.accept("mouse3", self.start_camera_drag)
        self.accept("mouse3-up", self.stop_camera_drag)
        self.accept("wheel_up", self.adjust_zoom, [-5.0])
        self.accept("wheel_down", self.adjust_zoom, [5.0])

    def start_camera_drag(self):
        self.dragging = True
        if base.mouseWatcherNode.hasMouse():
            m = base.mouseWatcherNode.getMouse()
            self.last_mouse_x = m.x
            self.last_mouse_y = m.y

    def stop_camera_drag(self):
        self.dragging = False

    def recalculate_stats(self):
        new_stats = self.base_stats.copy()
        
        core = self.core
        if core:
            if hasattr(core, 'shipMaxVelocity'):
                new_stats['speed'] *= (1.0 + core.shipMaxVelocity)
            if hasattr(core, 'shipAgility'):
                new_stats['agility'] *= (1.0 + core.shipAgility)

        support = self.support
        if support:
            if hasattr(support, 'shieldBoostAmount'):
                new_stats['shield'] *= (1.0 + support.shieldBoostAmount)

        self.effective_stats = new_stats
        
        for stat in ['hp', 'shield', 'armor', 'capacitor']:
            if stat in self.current_values and stat in self.effective_stats:
                self.current_values[stat] = min(self.current_values[stat], self.effective_stats[stat])

        print(f"[SHIP] Statok újraszámolva. Sebesség: {self.effective_stats['speed']:.2f}")

    def adjust_zoom(self, amt):
        self.cam_dist = max(10.0, min(150.0, self.cam_dist + amt))

    def update(self, dt):
        if not self.is_local or not self.model: return

        # Regeneráció
        self.current_values['shield'] = min(self.effective_stats['shield'], 
            self.current_values['shield'] + self.effective_stats['shield_regen'] * dt)
        
        self.current_values['capacitor'] = min(self.effective_stats['capacitor'], 
            self.current_values['capacitor'] + self.effective_stats['cap_regen'] * dt)

        # Mozgás logika
        if self.target_entity and self.target_entity.model:
            self.run_autopilot(dt)
        else:
            if self.velocity.length() > 0.1:
                self.velocity *= (1.0 - self.effective_stats['drag'] * dt)
                self.model.setPos(self.model.getPos() + self.velocity * dt)
            
        self.update_orientation(dt)
        self.update_camera(dt)

    def update_camera(self, dt):
        if self.dragging and base.mouseWatcherNode.hasMouse():
            m = base.mouseWatcherNode.getMouse()
            dx = m.x - self.last_mouse_x
            dy = m.y - self.last_mouse_y
            self.last_mouse_x = m.x
            self.last_mouse_y = m.y
            
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

    def fire_mining_laser(self):
        print("[SHIP] Bányász lézer tüzelés...")

    def run_autopilot(self, dt):
        """Autopilot mozgási logika visszatöltve."""
        if not self.target_entity or not self.target_entity.model:
            return

        target_pos = self.target_entity.get_pos()
        diff = target_pos - self.model.getPos()
        distance = diff.length()
        direction = diff.normalized() if distance > 0 else Vec3(0,0,0)
        
        # Statisztikák lekérése
        max_speed = self.effective_stats['speed']
        
        self.velocity = Vec3(0, 0, 0)
        mode = self.autopilot_mode if self.autopilot_mode else "follow"

        if mode == "follow":
            # Követés: ha messzebb van mint 2 egység, indulunk felé
            if distance > 2.0:
                self.velocity = direction * (max_speed * 0.8)
        
        elif mode == "orbit":
            # Körözés: ha messze vagyunk, közeledünk, ha közel, oldalra mozgunk
            if distance > 35.0:
                 self.velocity = direction * (max_speed * 0.8)
            else:
                # Egyszerű merőleges vektor a körözéshez (Z tengely körüli forgatás)
                orbit_vec = Vec3(-direction.y, direction.x, 0)
                self.velocity = orbit_vec * (max_speed * 0.5)

        # Pozíció frissítése
        self.model.setPos(self.model.getPos() + self.velocity * dt)
from panda3d.core import Vec3, Quat, CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay, BitMask32
from .entity import Entity
# Importáljuk a slotokat és típusokat
from .components import (
    WeaponMount, TacticalSlot, ArmorSlot, HullAugment, RelicSlot,
    DamageType, RelicType, MiningLaser
)
import math

# ==============================================================================
# SHIP CLASS
# ==============================================================================
class Ship(Entity):
    def __init__(self, manager, ship_id, is_local=False, name="Ismeretlen", ship_type="Vadász"):
        super().__init__(manager, ship_id, name, ship_type)
        self.ship_type = ship_type
        self.is_local = is_local
        
        # --- TAROLT TÁRGYAK (Tényleges felszerelés) ---
        self.core = None
        self.support = None
        self.system = None

        # --- ALAP STATISZTIKÁK ---
        self.max_hp = 1000.0
        self.hp = self.max_hp
        self.max_shield = 500.0
        self.shield = self.max_shield
        self.shield_regen = 5.0 
        self.max_armor = 200.0
        self.armor = self.max_armor
        self.max_capacitor = 100.0
        self.capacitor = self.max_capacitor
        self.capacitor_regen = 2.0 

        # --- ELLENÁLLÁSOK ÉS BÓNUSZOK ---
        self.resistance = {
            DamageType.IMPACT: 0.0,
            DamageType.THERMIC: 0.0,
            DamageType.IONIC: 0.0,
            DamageType.DETONATION: 0.0
        }
        self.damage_bonus = {
            DamageType.IMPACT: 1.0,
            DamageType.THERMIC: 1.0,
            DamageType.IONIC: 1.0,
            DamageType.DETONATION: 1.0
        }
        self.modifiers = {
            'speed': 1.0,
            'agility': 1.0,
            'scan_res': 1.0,
            'power_usage': 0
        }

        # --- FELSZERELÉS SLOTOK ---
        self.weapon_mounts = []   
        self.tactical_slots = []  
        self.armor_slots = []     
        self.hull_augments = []   
        self.relic_slots = 3
        self.relics = []     
        
        # --- BÁNYÁSZAT ---
        self.mining_lasers = [] 

        # --- FIZIKA VÁLTOZÓK ---
        self.velocity = Vec3(0, 0, 0)
        self.base_max_speed = 40.0
        self.base_turn_speed = 3.0
        self.drag = 1.5
        
        self.autopilot_mode = None
        self.target_entity = None

        # --- ÜTKÖZÉS KEZELÉS ---
        self.cTrav = CollisionTraverser()
        self.cQueue = CollisionHandlerQueue()
        self.ray = CollisionRay()
        self.ray_node = CollisionNode('miningRay')
        self.ray_node.addSolid(self.ray)
        self.ray_node.setFromCollideMask(BitMask32.bit(1))
        self.ray_node.setIntoCollideMask(BitMask32.allOff())
        self.ray_np = render.attachNewNode(self.ray_node)
        self.cTrav.addCollider(self.ray_np, self.cQueue)

        # Modell betöltése
        self.load_model("assets/models/SpaceShip", scale=1.0)
        
        if self.is_local:
            self.model.setColor(1, 1, 1, 1)
            self.setup_controls()
            self.setup_camera()
            self.equip_test_items()
            self.accept("space", self.fire_mining_laser)
        else:
            self.model.setCollideMask(BitMask32.bit(1))

    # --- TÁRGY FELSZERELŐ METÓDUSOK ---

    def equip_core(self, core_obj):
        """Felszerel egy Core tárgyat és alkalmazza a bónuszait."""
        self.core = core_obj
        # Bónuszok érvényesítése a módosítókra (pl. sebesség bónusz 0.25 -> 1.25x szorzó)
        self.modifiers['speed'] = 1.0 + core_obj.shipMaxVelocity
        self.modifiers['agility'] = 1.0 + core_obj.shipAgility
        # Itt lehetne frissíteni a HP-t/Capacitort is ha a Core adna ilyet
        print(f"[SHIP] {self.name} felszerelte a magot: {core_obj.name} (Speed bonus: {core_obj.shipMaxVelocity})")

    def equip_support(self, support_obj):
        """Felszerel egy Support tárgyat."""
        self.support = support_obj
        # Pl. Pajzs bónusz érvényesítése
        if support_obj.shieldBoostAmount > 0:
            self.max_shield *= (1.0 + support_obj.shieldBoostAmount)
            self.shield = self.max_shield
        print(f"[SHIP] {self.name} felszerelte a support modult: {support_obj.name}")

    def equip_system(self, system_obj):
        """Felszerel egy System tárgyat."""
        self.system = system_obj
        # Pl. Energiahatékonyság vagy CPU csökkentés
        self.modifiers['power_usage'] += system_obj.power_usage
        print(f"[SHIP] {self.name} felszerelte a rendszert: {system_obj.name}")

    @property
    def max_speed(self):
        return self.base_max_speed * self.modifiers.get('speed', 1.0)

    @property
    def turn_speed(self):
        return self.base_turn_speed * self.modifiers.get('agility', 1.0)

    def equip_test_items(self):
        self.weapon_mounts.append(WeaponMount("Impulzus Lézer I", damage_type=DamageType.THERMIC, damage=15, range=150))
        self.tactical_slots.append(TacticalSlot("Utánégető", effect_type="speed_boost", value=1.5))
        self.armor_slots.append(ArmorSlot("Titánium Lemez", armor_hp=200, resistance_type=DamageType.IMPACT, resistance_val=0.2))
        self.hull_augments.append(HullAugment("Raktér Bővítő", hull_hp=50))
        
        # Teszt bányász lézer
        self.mining_lasers.append(MiningLaser())
        
        print(f"[SHIP] Teszt itemek felszerelve.")

    def setup_controls(self):
        if hasattr(self.manager, 'window_manager'):
            self.accept("i", self.manager.window_manager.toggle_inventory)
            self.accept("m", self.manager.window_manager.toggle_market)

    def setup_camera(self):
        self.cam_dist = 40.0
        self.cam_h = 0.0
        self.cam_p = -20.0
        self.dragging = False
        self.last_mouse_x = 0.0
        self.last_mouse_y = 0.0
        self.camera_pivot = render.attachNewNode("CameraPivot")
        
        self.accept("mouse3", self.start_drag)
        self.accept("mouse3-up", self.stop_drag)
        self.accept("wheel_up", self.adjust_zoom, [-5.0])
        self.accept("wheel_down", self.adjust_zoom, [5.0])

    def start_drag(self):
        self.dragging = True
        if self.manager.mouseWatcherNode.hasMouse():
            m = self.manager.mouseWatcherNode.getMouse()
            self.last_mouse_x = m.x
            self.last_mouse_y = m.y

    def stop_drag(self):
        self.dragging = False

    def adjust_zoom(self, amount):
        self.cam_dist = max(10.0, min(100.0, self.cam_dist + amount))

    def fire_mining_laser(self):
        if not self.mining_lasers: return
        laser = self.mining_lasers[0]
        start_pos = self.model.getPos()
        forward_vec = self.model.getQuat().getForward()
        self.ray.setOrigin(start_pos)
        self.ray.setDirection(forward_vec)
        self.cTrav.traverse(render)
        
        if self.cQueue.getNumEntries() > 0:
            self.cQueue.sortEntries()
            entry = self.cQueue.getEntry(0)
            hit_node = entry.getIntoNodePath().getParent()
            hit_entity = None
            for entity in self.manager.remote_ships.values():
                if entity.model == hit_node:
                    hit_entity = entity
                    break
            if hit_entity and hit_entity.entity_type == "Aszteroida":
                hit_pos = entry.getSurfacePoint(render)
                distance = (hit_pos - start_pos).length()
                if distance <= laser.range:
                    if hasattr(hit_entity, 'apply_mining_damage'):
                        hit_entity.apply_mining_damage(hit_pos)
                    self.manager.window_manager.add_item(f"{laser.resource_type} Ásvány", "Nyersanyag", laser.resource_yield, 20)
                    return

    def update(self, dt):
        if not self.is_local:
            return

        if self.shield < self.max_shield:
            self.shield = min(self.max_shield, self.shield + self.shield_regen * dt)
        if self.capacitor < self.max_capacitor:
            self.capacitor = min(self.max_capacitor, self.capacitor + self.capacitor_regen * dt)

        if self.target_entity and self.target_entity.model:
            self.run_autopilot(dt)
        else:
            if self.velocity.length() > 0.1:
                self.velocity *= (1.0 - self.drag * dt)
                self.model.setPos(self.model.getPos() + self.velocity * dt)
            
        self.update_orientation(dt)
        self.update_camera(dt)

    def update_camera(self, dt):
        if self.dragging and self.manager.mouseWatcherNode.hasMouse():
            m = self.manager.mouseWatcherNode.getMouse()
            dx = m.x - self.last_mouse_x
            dy = m.y - self.last_mouse_y
            self.last_mouse_x = m.x
            self.last_mouse_y = m.y
            self.cam_h -= dx * 100.0
            self.cam_p = max(-80, min(80, self.cam_p + dy * 100.0))

        self.camera_pivot.setPos(self.model.getPos())
        self.camera_pivot.setHpr(self.cam_h, self.cam_p, 0)
        cam = self.manager.camera
        if cam.getParent() != self.camera_pivot:
            cam.reparentTo(self.camera_pivot)
        cam.setPos(0, -self.cam_dist, 0)
        cam.lookAt(self.camera_pivot)
    
    def destroy(self):
        if hasattr(self, 'camera_pivot'):
            self.camera_pivot.removeNode()
        super().destroy()

    def update_orientation(self, dt):
        target_quat = None
        current_quat = self.model.getQuat()
        if self.target_entity and self.target_entity.model:
            to_target = self.target_entity.get_pos() - self.model.getPos()
            if to_target.length_squared() > 0.1:
                temp_node = render.attachNewNode("temp")
                temp_node.setPos(self.model.getPos())
                temp_node.lookAt(self.target_entity.model)
                target_quat = temp_node.getQuat()
                temp_node.removeNode()
        elif self.velocity.length() > 1.0:
            temp_node = render.attachNewNode("temp")
            temp_node.setPos(self.model.getPos())
            temp_node.lookAt(self.model.getPos() + self.velocity)
            target_quat = temp_node.getQuat()
            temp_node.removeNode()

        if target_quat:
            t = min(1.0, self.turn_speed * dt)
            if current_quat.dot(target_quat) < 0:
                target_quat = target_quat * -1
            new_quat = current_quat * (1.0 - t) + target_quat * t
            new_quat.normalize()
            self.model.setQuat(new_quat)

    def run_autopilot(self, dt):
        if not self.target_entity.model: return
        target_pos = self.target_entity.get_pos()
        distance = (target_pos - self.model.getPos()).length()
        direction = (target_pos - self.model.getPos()).normalized()
        self.velocity = Vec3(0,0,0)
        mode = self.autopilot_mode if self.autopilot_mode else "follow"
        if mode == "follow":
            if distance > 2.0:
                self.velocity = direction * (self.max_speed * 0.8)
        elif mode == "orbit":
            if distance > 35.0:
                 self.velocity = direction * (self.max_speed * 0.8)
            else:
                orbit_vec = Vec3(-direction.y, direction.x, 0)
                self.velocity = orbit_vec * (self.max_speed * 0.5)
        self.model.setPos(self.model.getPos() + self.velocity * dt)
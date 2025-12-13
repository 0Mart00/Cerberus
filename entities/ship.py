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
            'scan_res': 1.0
        }

        # --- FELSZERELÉS SLOTOK ---
        self.weapon_mounts = []   
        self.tactical_slots = []  
        self.armor_slots = []     
        self.hull_augments = []   
        self.relic_slots = 3
        self.relics = []     
        
        # --- BÁNYÁSZAT ---
        self.mining_lasers = [] # A MiningLaser komponensek itt lesznek

        # --- FIZIKA VÁLTOZÓK ---
        self.velocity = Vec3(0, 0, 0)
        self.base_max_speed = 40.0
        self.base_turn_speed = 3.0
        self.drag = 1.5
        
        self.autopilot_mode = None
        self.target_entity = None

        # --- ÜTKÖZÉS KEZELÉS (Raycasting) ---
        self.cTrav = CollisionTraverser()
        self.cQueue = CollisionHandlerQueue()
        self.ray = CollisionRay()
        self.ray_node = CollisionNode('miningRay')
        self.ray_node.addSolid(self.ray)
        # Beállítjuk a maszkot, hogy csak az aszteroidákkal ütközzön (Bit 1)
        self.ray_node.setFromCollideMask(BitMask32.bit(1))
        self.ray_node.setIntoCollideMask(BitMask32.allOff())
        self.ray_np = render.attachNewNode(self.ray_node)
        self.cTrav.addCollider(self.ray_np, self.cQueue)


        # Modell betöltése
        self.load_model("models/SpaceShip", scale=1.0)
        
        if self.is_local:
            self.model.setColor(1, 1, 1, 1)
            self.setup_controls()
            self.setup_camera() # Ezt a hívást vizsgáljuk
            self.equip_test_items()
            
            # Gyorsgomb a bányász lézernek
            self.accept("space", self.fire_mining_laser)
        else:
            # Csak az aszteroidák kapnak ütközés detekciót, de NPC-knél is beállíthatjuk
            self.model.setCollideMask(BitMask32.bit(1))


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
        self.relics.append(RelicSlot("Ősi Pajzs Generátor", relic_type=RelicType.PASSIVE, modifiers={'shield_max': 1.2}))
        
        # Teszt bányász lézer
        self.mining_lasers.append(MiningLaser())
        
        print(f"[SHIP] Felszerelve: {len(self.weapon_mounts)} fegyver, {len(self.mining_lasers)} bányász lézer.")

    def setup_controls(self):
        # UI gyorsgombok (I, M)
        if hasattr(self.manager, 'window_manager'):
            self.accept("i", self.manager.window_manager.toggle_inventory)
            self.accept("m", self.manager.window_manager.toggle_market)

    def setup_camera(self): # <--- HIÁNYZÓ METÓDUS PÓTLÁSA
        # --- KAMERA IRÁNYÍTÁS (TPS Free Look) ---
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
        """Megpróbál bányász lézerrel lőni a célpont irányába (SPACE gomb)."""
        if not self.mining_lasers:
            print("[MINING] Nincs felszerelt bányász lézer.")
            return

        laser = self.mining_lasers[0] # Első lézer használata

        # Létrehozzuk a Ray-t a hajó orrától előre
        start_pos = self.model.getPos()
        forward_vec = self.model.getQuat().getForward()

        # Ray beállítása
        self.ray.setOrigin(start_pos)
        self.ray.setDirection(forward_vec)
        
        # Lekérdezés (Traversal)
        self.cTrav.traverse(render)
        
        # Eredmények feldolgozása
        if self.cQueue.getNumEntries() > 0:
            self.cQueue.sortEntries()
            entry = self.cQueue.getEntry(0) # Legközelebbi találat
            
            hit_node = entry.getIntoNodePath().getParent()
            
            # Megkeressük, hogy melyik Entity-hez tartozik ez a NodePath
            hit_entity = None
            # Mivel a remote_ships tartalmazza az aszteroidákat is a Hostnál:
            for entity in self.manager.remote_ships.values():
                if entity.model == hit_node:
                    hit_entity = entity
                    break

            if hit_entity and hit_entity.entity_type == "Aszteroida":
                hit_pos = entry.getSurfacePoint(render)
                distance = (hit_pos - start_pos).length()

                if distance <= laser.range:
                    # Sikeres találat és távolságon belül
                    
                    # 1. Vizuális hatás (gödör/pitting)
                    if hasattr(hit_entity, 'apply_mining_damage'):
                        hit_entity.apply_mining_damage(hit_pos)
                    
                    # 2. Erőforrás gyűjtés (logikai hatás)
                    resource_name = f"{laser.resource_type} Ásvány"
                    self.manager.window_manager.add_item(resource_name, "Nyersanyag", laser.resource_yield, 20)
                    print(f"[MINING] Bányászva {laser.resource_yield} {resource_name}.")
                    return

        print("[MINING] Nincs találat vagy a cél túl messze van/nem bányászható.")

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
        """Kezeli a hajó forgását globális térben"""
        target_quat = None
        current_quat = self.model.getQuat()

        # 1. Prioritás: Célpont felé fordulás
        if self.target_entity and self.target_entity.model:
            to_target = self.target_entity.get_pos() - self.model.getPos()
            if to_target.length_squared() > 0.1:
                # JAVÍTÁS: A render-hez (globális tér) csatoljuk az ideiglenes node-ot,
                # így a lookAt a valós, globális irányt számolja ki.
                temp_node = render.attachNewNode("temp")
                temp_node.setPos(self.model.getPos())
                temp_node.lookAt(self.target_entity.model)
                target_quat = temp_node.getQuat()
                temp_node.removeNode()
                
        # 2. Prioritás: Mozgás irányába fordulás (ha nincs célpont)
        elif self.velocity.length() > 1.0:
            temp_node = render.attachNewNode("temp")
            temp_node.setPos(self.model.getPos())
            temp_node.lookAt(self.model.getPos() + self.velocity)
            target_quat = temp_node.getQuat()
            temp_node.removeNode()

        if target_quat:
            # Interpoláció (N-Lerp)
            t = min(1.0, self.turn_speed * dt)
            
            # Legrövidebb út ellenőrzése (kvaternióknál a -Q és Q ugyanazt a forgást jelenti)
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
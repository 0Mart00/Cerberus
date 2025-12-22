import math
from direct.actor.Actor import Actor
from panda3d.core import Vec3, NodePath, CollisionNode, CollisionSphere, BitMask32, MouseButton
from entities.entity import Entity
from entities.components import Engine, Weapon, Shield, Cargo
from globals import EVENT_SHIP_DAMAGED, EVENT_SHIP_DESTROYED

class Ship(Entity):
    def __init__(self, manager, ship_id, is_local=False, name="Unknown", ship_type="Unknown"):
        # Az Entity alaposztály meghívása (manager, id, name, type)
        super().__init__(manager, ship_id, name, entity_type="Ship")
        
        self.is_local = is_local
        self.ship_type = ship_type
        
        # --- Komponens slotok ---
        self.engines = []
        self.weapons = []
        self.shields = []
        self.cargos = []
        self.core = None

        # --- Statisztikák ---
        self.max_hull = 1000.0
        self.current_hull = 1000.0
        self.max_shield = 0.0
        self.current_shield = 0.0
        self.max_armor = 0.0
        self.current_armor = 0.0
        self.speed = 0.0
        self.max_speed = 0.0
        self.turn_rate = 0.0

        # --- Mozgási állapot ---
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 0.0
        self.target_entity = None
        self.autopilot_mode = None

        # --- Vizuális elemek ---
        self.model = None

        # --- Vezérlés állapota ---
        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "roll_left": False,
            "roll_right": False
        }
        
        # Kamera forgatás adatai
        self.cam_dist = 40.0
        self.cam_pitch = 15.0
        self.cam_heading = 0.0
        self.cam_pivot = None
        self.last_mouse_pos = None # Egér előző pozíciójának tárolása
        
        # Modell betöltése a megadott útvonalról
        self.load_model()
        
        # Ütközés detektálás setup
        self.setup_collision()

        # Alapértelmezett komponensek a teszteléshez
        self.mount_component(Engine("Standard Thruster", 1, 20.0, 50.0, 3.0))
        self.mount_component(Shield("Basic Shield", 1, 500.0, 5.0))

        # Statisztikák inicializálása
        self.recalculate_stats()

        if self.is_local:
            self.setup_controls()
            # Kamera pivot létrehozása a forgatáshoz
            if self.app:
                # Letiltjuk az alapértelmezett egérkezelést
                self.app.disableMouse()
                
                # Létrehozunk egy külön pivotot a forgatáshoz
                self.cam_pivot = self.root.attachNewNode("CameraPivot")
                
                # A kamerát a pivot alá rendeljük
                self.app.camera.reparentTo(self.cam_pivot)
                self.app.camera.setPos(0, -self.cam_dist, 8)
                self.app.camera.lookAt(self.root)
                
                # Kamera frissítő task
                self.app.taskMgr.add(self.update_camera, f"update_camera_{self.id}")

    def load_model(self):
        """A hajó vizuális modelljének betöltése a megadott assets útvonalról."""
        if not self.app:
            return

        try:
            # A kért modell betöltése
            self.model = self.app.loader.loadModel("assets/models/SpaceShip.egg")
        except:
            print("[HIBA] Nem található az assets/models/SpaceShip.egg! Fallback box betöltése.")
            self.model = self.app.loader.loadModel("models/box")
        
        if self.model:
            self.model.reparentTo(self.root)
            self.model.setScale(1.0)

    def setup_collision(self):
        """Ütközési zóna beállítása."""
        coll_node = CollisionNode(f"ship_coll_{self.id}")
        coll_node.addSolid(CollisionSphere(0, 0, 0, 3))
        mask = BitMask32(0x1) 
        coll_node.setIntoCollideMask(mask)
        coll_node.setFromCollideMask(mask)
        self.c_np = self.root.attachNewNode(coll_node)

    def mount_component(self, component):
        """Alkatrészek felszerelése."""
        if isinstance(component, Engine):
            self.engines.append(component)
        elif isinstance(component, Shield):
            self.shields.append(component)
        
        component.on_mount(self)

    def recalculate_stats(self):
        """A felszerelt modulok alapján számolt maximális értékek."""
        self.max_speed = 0
        self.acceleration = 0
        self.turn_rate = 0
        self.max_shield = 0
        
        for eng in self.engines:
            self.max_speed += eng.max_speed
            self.acceleration += eng.acceleration
            self.turn_rate += eng.turn_rate
            
        for sh in self.shields:
            self.max_shield += sh.capacity
        
        self.current_shield = min(self.current_shield, self.max_shield)

    def setup_controls(self):
        """Billentyűzet események regisztrálása."""
        if not self.app: return

        self.app.accept("w", self.set_key, ["forward", True])
        self.app.accept("w-up", self.set_key, ["forward", False])
        self.app.accept("s", self.set_key, ["backward", True])
        self.app.accept("s-up", self.set_key, ["backward", False])
        self.app.accept("a", self.set_key, ["left", True])
        self.app.accept("a-up", self.set_key, ["left", False])
        self.app.accept("d", self.set_key, ["right", True])
        self.app.accept("d-up", self.set_key, ["right", False])
        self.app.accept("q", self.set_key, ["roll_left", True])
        self.app.accept("q-up", self.set_key, ["roll_left", False])
        self.app.accept("e", self.set_key, ["roll_right", True])
        self.app.accept("e-up", self.set_key, ["roll_right", False])

    def set_key(self, key, value):
        self.key_map[key] = value

    def update(self, dt):
        """A core/game.py update_loop-ja hívja meg minden frame-ben."""
        if self.is_local:
            self.handle_movement(dt)
        
        # Pajzs automatikus visszatöltése
        for shield in self.shields:
            if self.current_shield < self.max_shield:
                self.current_shield += shield.recharge_rate * dt
                self.current_shield = min(self.current_shield, self.max_shield)

    def handle_movement(self, dt):
        """TPS stílusú mozgás kezelése."""
        # 1. Forgás (Heading/Yaw)
        rotation_step = self.turn_rate * 25 * dt
        if self.key_map["left"]:
            self.root.setH(self.root.getH() + rotation_step)
        if self.key_map["right"]:
            self.root.setH(self.root.getH() - rotation_step)
            
        # 2. Dőlés (Roll)
        roll_step = self.turn_rate * 30 * dt
        if self.key_map["roll_left"]:
            self.root.setR(self.root.getR() - roll_step)
        if self.key_map["roll_right"]:
            self.root.setR(self.root.getR() + roll_step)

        # 3. Sebesség számítása
        forward_vec = self.root.getQuat().getForward()
        
        target_vel = Vec3(0, 0, 0)
        if self.key_map["forward"]:
            target_vel = forward_vec * self.max_speed
        elif self.key_map["backward"]:
            target_vel = forward_vec * (-self.max_speed * 0.5)
            
        # 4. Tehetetlenség alkalmazása
        diff = target_vel - self.velocity
        if diff.length() > 0:
            accel_val = self.acceleration * dt
            if diff.length() < accel_val:
                self.velocity = target_vel
            else:
                self.velocity += diff.normalized() * accel_val
                
        # 5. Pozíció tényleges frissítése
        self.root.setPos(self.root.getPos() + self.velocity * dt)

    def update_camera(self, task):
        """Kamera forgatása a hajó körül csak jobb egérgombbal, lokolás nélkül."""
        if not self.app or not self.cam_pivot:
            return task.cont

        # Recapture camera if parent changed
        if self.app.camera.getParent() != self.cam_pivot:
            self.app.camera.reparentTo(self.cam_pivot)
            self.app.camera.setPos(0, -self.cam_dist, 8)
            self.app.camera.lookAt(self.root)

        # Egér állapot ellenőrzése
        if self.app.mouseWatcherNode.hasMouse():
            # Csak akkor forgatunk, ha a jobb gomb le van nyomva és nem UI felett vagyunk
            if self.app.mouseWatcherNode.isButtonDown(MouseButton.three()) and \
               self.app.mouseWatcherNode.getOverRegion() is None:
                
                # Aktuális egér pozíció lekérése (relatív -1 és 1 között)
                mpos = self.app.mouseWatcherNode.getMouse()
                cur_x, cur_y = mpos.getX(), mpos.getY()

                if self.last_mouse_pos is not None:
                    # Elmozdulás számítása az előző frame óta
                    dx = (cur_x - self.last_mouse_pos[0]) * 100 # Érzékenység skálázása
                    dy = (cur_y - self.last_mouse_pos[1]) * 100

                    # Pivot értékeinek frissítése (0-360 fokban szabadon)
                    self.cam_heading -= dx * 1.5
                    self.cam_pitch = max(-89, min(89, self.cam_pitch + dy * 1.5))

                    # Forgatás alkalmazása
                    self.cam_pivot.setHpr(self.cam_heading, self.cam_pitch, 0)
                
                # Pozíció mentése a következő frame-hez
                self.last_mouse_pos = (cur_x, cur_y)
            else:
                # Ha elengedjük a gombot, töröljük az előző pozíciót
                self.last_mouse_pos = None
        
        return task.cont

    def equip_core(self, core_item):
        """Mag felszerelése."""
        self.core = core_item
        print(f"[GAME] {self.name} hajó magja frissítve: {core_item.name}")

    def take_damage(self, amount):
        """Sérüléskezelés sorrendben: Pajzs -> Páncél -> Szerkezet."""
        remaining_damage = amount

        # 1. Pajzs elnyelése
        if self.current_shield > 0:
            if self.current_shield >= remaining_damage:
                self.current_shield -= remaining_damage
                remaining_damage = 0
            else:
                remaining_damage -= self.current_shield
                self.current_shield = 0

        # 2. Páncél elnyelése
        if remaining_damage > 0 and self.current_armor > 0:
            if self.current_armor >= remaining_damage:
                self.current_armor -= remaining_damage
                remaining_damage = 0
            else:
                remaining_damage -= self.current_armor
                self.current_armor = 0

        # 3. Szerkezet (Hull) sebzése
        if remaining_damage > 0:
            self.current_hull -= remaining_damage
            
        if self.current_hull <= 0:
            self.current_hull = 0
            self.destroy()

    def destroy(self):
        """Hajó megsemmisítése."""
        if self.app:
            self.app.messenger.send(EVENT_SHIP_DESTROYED, [self.id])
        super().destroy()
from panda3d.core import Vec3, Quat, LRotation
from direct.showbase.DirectObject import DirectObject
import math

class Ship(DirectObject):
    def __init__(self, manager, ship_id, is_local=False, name="Ismeretlen", ship_type="Vadász"):
        self.manager = manager
        self.id = ship_id
        self.is_local = is_local
        self.name = name
        self.ship_type = ship_type
        
        # Modell betöltése
        self.model = loader.loadModel("models/box")
        self.model.setScale(1.5)
        self.model.reparentTo(render)
        
        if self.is_local:
            self.model.setColor(0, 1, 0, 1) # Zöld (Én)
            self.setup_controls()
        else:
            self.model.setColor(1, 0, 0, 1) # Piros (Ellenfél)

        # --- FIZIKA VÁLTOZÓK ---
        self.velocity = Vec3(0, 0, 0) # Jelenlegi sebesség vektor
        self.acceleration = 20.0      # Gyorsulás
        self.max_speed = 40.0         # Max sebesség
        self.turn_speed = 3.0         # Fordulási sebesség (Interpolációs faktor)
        self.drag = 0.5               # Légellenállás (kisebb = jobban csúszik)
        
        # Célpont és Autopilot
        self.autopilot_mode = None
        self.target_entity = None

    def setup_controls(self):
        """Csak a helyi játékosnak"""
        self.key_map = {"up": False, "down": False, "left": False, "right": False}
        self.accept("w", self.update_key, ["up", True])
        self.accept("w-up", self.update_key, ["up", False])
        self.accept("s", self.update_key, ["down", True])
        self.accept("s-up", self.update_key, ["down", False])
        self.accept("a", self.update_key, ["left", True])
        self.accept("a-up", self.update_key, ["left", False])
        self.accept("d", self.update_key, ["right", True])
        self.accept("d-up", self.update_key, ["right", False])
        
        # --- KAMERA IRÁNYÍTÁS (TPS Free Look) ---
        self.cam_dist = 40.0
        self.cam_h = 0.0
        self.cam_p = -20.0
        self.dragging = False
        self.last_mouse_x = 0.0
        self.last_mouse_y = 0.0

        # Külön pivot pont a kamerának, hogy független legyen a hajó forgásától
        self.camera_pivot = render.attachNewNode("CameraPivot")
        
        # Jobb klikk a forgatáshoz, görgő a zoomhoz
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

    def update_key(self, key, value):
        self.key_map[key] = value
        # Ha mozgásgombot nyomunk, kikapcsoljuk az autopilot mozgást (de a célpont marad!)
        if value:
            self.autopilot_mode = None

    def update(self, dt):
        """Fizikai frissítés minden frame-ben"""
        if not self.is_local:
            return

        # Ha van aktív robotpilóta
        if self.autopilot_mode and self.target_entity:
            self.run_autopilot(dt)
        else:
            self.run_physics_controls(dt)
            
        # Orientáció frissítése (Célra vagy Sebességre fordulás)
        self.update_orientation(dt)
        
        # --- KAMERA FRISSÍTÉS ---
        self.update_camera(dt)

    def update_camera(self, dt):
        """Kamera pozíció és rotáció frissítése"""
        # Egér alapú forgatás (Free Look)
        if self.dragging and self.manager.mouseWatcherNode.hasMouse():
            m = self.manager.mouseWatcherNode.getMouse()
            dx = m.x - self.last_mouse_x
            dy = m.y - self.last_mouse_y
            self.last_mouse_x = m.x
            self.last_mouse_y = m.y
            
            self.cam_h -= dx * 100.0
            self.cam_p = max(-80, min(80, self.cam_p + dy * 100.0))

        # A pivot kövesse a hajót
        self.camera_pivot.setPos(self.model.getPos())
        self.camera_pivot.setHpr(self.cam_h, self.cam_p, 0)
        
        # Biztosítjuk, hogy a kamera ehhez a pivothoz csatlakozzon
        # (Ez felülírja a game.py alapbeállítását)
        cam = self.manager.camera
        if cam.getParent() != self.camera_pivot:
            cam.reparentTo(self.camera_pivot)
            
        cam.setPos(0, -self.cam_dist, 0)
        cam.lookAt(self.camera_pivot)

    def update_orientation(self, dt):
        """Kezeli a hajó forgását (EVE Online stílus)"""
        target_quat = None
        current_quat = self.model.getQuat()

        # 1. Prioritás: Ha van CÉLPONT, forduljunk felé
        if self.target_entity and self.target_entity.model:
            to_target = self.target_entity.get_pos() - self.model.getPos()
            if to_target.length_squared() > 0.1:
                # Segéd node a forgás kiszámításához
                temp_node = self.model.attachNewNode("temp")
                temp_node.lookAt(self.target_entity.model)
                target_quat = temp_node.getQuat()
                temp_node.removeNode()

        # 2. Prioritás: Ha mozog a hajó és nincs célpont, forduljunk a MOZGÁS irányába
        elif self.velocity.length() > 1.0:
            temp_node = self.model.attachNewNode("temp")
            temp_node.lookAt(self.model.getPos() + self.velocity)
            target_quat = temp_node.getQuat()
            temp_node.removeNode()

        # Ha van új célirány, interpolálunk (N-Lerp) felé
        if target_quat:
            # JAVÍTÁS: N-Lerp (Normalized Linear Interpolation) használata slerp helyett
            # Ez elkerüli az AttributeError hibát, és ugyanazt a sima forgást eredményezi.
            t = min(1.0, self.turn_speed * dt)
            
            # Shortest path check (Legrövidebb út ellenőrzése)
            # Ha a dot product negatív, akkor a "hosszú úton" fordulna, ezért invertáljuk.
            if current_quat.dot(target_quat) < 0:
                target_quat = target_quat * -1
            
            # Linear interpolation + Normalize
            new_quat = current_quat * (1.0 - t) + target_quat * t
            new_quat.normalize()
            self.model.setQuat(new_quat)

    def run_physics_controls(self, dt):
        """Kézi irányítás fizikája"""
        
        # Irányvektorok lekérése a jelenlegi orientáció alapján
        # Mivel a hajó forgása automatikus, az A/D strafe-elni fog az aktuális nézethez képest
        quat = self.model.getQuat()
        forward = quat.getForward()
        right = quat.getRight()

        accel_vec = Vec3(0, 0, 0)

        # Gáz / Fék (Előre/Hátra)
        if self.key_map["up"]: accel_vec += forward * 1.0
        if self.key_map["down"]: accel_vec -= forward * 0.5
        
        # Oldalazás (Strafe) - A és D mostantól ezt csinálja!
        if self.key_map["right"]: accel_vec += right * 0.8
        if self.key_map["left"]: accel_vec -= right * 0.8

        # Gyorsítás alkalmazása
        self.velocity += accel_vec * (self.acceleration * dt)

        # Légellenállás (Drag)
        self.velocity *= (1.0 - self.drag * dt)

        # Max sebesség limit
        if self.velocity.length() > self.max_speed:
            self.velocity.normalize()
            self.velocity *= self.max_speed

        # Pozíció frissítése
        self.model.setPos(self.model.getPos() + self.velocity * dt)

    def run_autopilot(self, dt):
        """Egyszerű követés logika"""
        if not self.target_entity.model:
            return

        target_pos = self.target_entity.get_pos()
        my_pos = self.model.getPos()
        vector_to_target = target_pos - my_pos
        distance = vector_to_target.length()
        direction = vector_to_target.normalized()
        
        # Kezdetben nullázzuk a sebességet, és csak akkor adunk hozzá, ha mozogni kell
        self.velocity = Vec3(0,0,0) 

        if self.autopilot_mode == "follow":
            # 1 méteres távolságnál álljon meg
            if distance > 1.0:
                # Sebesség beállítása a cél felé
                self.velocity = direction * (self.max_speed * 0.8)

        elif self.autopilot_mode == "orbit":
            radius = 30.0
            if distance > radius + 5.0:
                 self.velocity = direction * (self.max_speed * 0.8)
            else:
                # Keringés
                orbit_vec = Vec3(-direction.y, direction.x, 0)
                self.velocity = orbit_vec * (self.max_speed * 0.5)
        
        # Pozíció frissítése a sebesség vektor alapján
        self.model.setPos(self.model.getPos() + self.velocity * dt)

    def get_pos(self):
        return self.model.getPos()

    def set_pos(self, x, y, z):
        self.model.setPos(x, y, z)
        
    def destroy(self):
        if self.camera_pivot:
            self.camera_pivot.removeNode()
        if self.model:
            self.model.removeNode()
        self.ignoreAll()
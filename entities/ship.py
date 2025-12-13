from panda3d.core import Vec3, Quat
from .entity import Entity
import math

# ==============================================================================
# SHIP CLASS
# ==============================================================================
class Ship(Entity):
    def __init__(self, manager, ship_id, is_local=False, name="Ismeretlen", ship_type="Vadász"):
        super().__init__(manager, ship_id, name, ship_type)
        # JAVÍTÁS: A HUD a ship_type-ot keresi, ezért ezt itt is eltároljuk,
        # még akkor is, ha az ősosztályban már van entity_type.
        self.ship_type = ship_type
        self.is_local = is_local
        
        # Modell betöltése
        self.load_model("models/box", scale=1.5)
        
        if self.is_local:
            self.model.setColor(0, 1, 0, 1) # Zöld (Én)
            self.setup_controls()
            self.setup_camera()
        else:
            self.model.setColor(1, 0, 0, 1) # Piros (Ellenfél)

        # --- FIZIKA VÁLTOZÓK ---
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 20.0
        self.max_speed = 40.0
        self.turn_speed = 3.0
        self.drag = 0.5
        
        # Célpont és Autopilot
        self.autopilot_mode = None
        self.target_entity = None

    def setup_controls(self):
        self.key_map = {"up": False, "down": False, "left": False, "right": False}
        self.accept("w", self.update_key, ["up", True])
        self.accept("w-up", self.update_key, ["up", False])
        self.accept("s", self.update_key, ["down", True])
        self.accept("s-up", self.update_key, ["down", False])
        self.accept("a", self.update_key, ["left", True])
        self.accept("a-up", self.update_key, ["left", False])
        self.accept("d", self.update_key, ["right", True])
        self.accept("d-up", self.update_key, ["right", False])
    
    def setup_camera(self):
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

    def update_key(self, key, value):
        self.key_map[key] = value
        if value:
            self.autopilot_mode = None

    def update(self, dt):
        if not self.is_local:
            return

        # Autopilot vagy Kézi vezérlés
        if self.autopilot_mode and self.target_entity:
            self.run_autopilot(dt)
        else:
            self.run_physics_controls(dt)
            
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

    # --- FIZIKA ÉS MOZGÁS LOGIKA ---
    def update_orientation(self, dt):
        target_quat = None
        current_quat = self.model.getQuat()

        if self.target_entity and self.target_entity.model:
            to_target = self.target_entity.get_pos() - self.model.getPos()
            if to_target.length_squared() > 0.1:
                temp_node = self.model.attachNewNode("temp")
                temp_node.lookAt(self.target_entity.model)
                target_quat = temp_node.getQuat()
                temp_node.removeNode()
        elif self.velocity.length() > 1.0:
            temp_node = self.model.attachNewNode("temp")
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

    def run_physics_controls(self, dt):
        quat = self.model.getQuat()
        forward = quat.getForward()
        right = quat.getRight()
        accel_vec = Vec3(0, 0, 0)

        if self.key_map["up"]: accel_vec += forward * 1.0
        if self.key_map["down"]: accel_vec -= forward * 0.5
        if self.key_map["right"]: accel_vec += right * 0.8
        if self.key_map["left"]: accel_vec -= right * 0.8

        self.velocity += accel_vec * (self.acceleration * dt)
        self.velocity *= (1.0 - self.drag * dt)
        if self.velocity.length() > self.max_speed:
            self.velocity.normalize()
            self.velocity *= self.max_speed

        self.model.setPos(self.model.getPos() + self.velocity * dt)

    def run_autopilot(self, dt):
        if not self.target_entity.model: return
        
        target_pos = self.target_entity.get_pos()
        distance = (target_pos - self.model.getPos()).length()
        direction = (target_pos - self.model.getPos()).normalized()
        
        self.velocity = Vec3(0,0,0)
        
        if self.autopilot_mode == "follow":
            if distance > 1.0:
                self.velocity = direction * (self.max_speed * 0.8)
        elif self.autopilot_mode == "orbit":
            if distance > 35.0:
                 self.velocity = direction * (self.max_speed * 0.8)
            else:
                orbit_vec = Vec3(-direction.y, direction.x, 0)
                self.velocity = orbit_vec * (self.max_speed * 0.5)
        
        self.model.setPos(self.model.getPos() + self.velocity * dt)
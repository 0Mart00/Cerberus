# Cerberus/systems/camera.py

from panda3d.core import Vec3, MouseButton
from direct.showbase.DirectObject import DirectObject

class CameraSystem(DirectObject):
    """
    Kezeli a kamera követését, az orbitális forgatást és a zoomot.
    """
    def __init__(self, base):
        self.base = base
        self.base.disableMouse()
        
        # Kamera horgony - követi a hajót
        self.camera_anchor = self.base.render.attachNewNode("CameraAnchor")
        self.base.camera.reparentTo(self.camera_anchor)
        
        # Kamera távolság és pozíció
        self.cam_dist = 50.0
        self.base.camera.setPos(0, -self.cam_dist, 15)
        self.base.camera.lookAt(0, 0, 0)
        
        self.orbit_speed = 100.0
        self.is_orbiting = False
        self.last_mouse_pos = None

        # Események: Jobb klikk a forgatáshoz, Görgő a zoomhoz
        self.accept("mouse3", self.start_orbit)
        self.accept("mouse3-up", self.stop_orbit)
        self.accept("wheel_up", self.adjust_zoom, [-5.0])
        self.accept("wheel_down", self.adjust_zoom, [5.0])

    def adjust_zoom(self, amount):
        """Zoom kezelése a cam_dist módosításával."""
        self.cam_dist = max(10.0, min(200.0, self.cam_dist + amount))
        self.base.camera.setY(-self.cam_dist)

    def start_orbit(self):
        if self.base.mouseWatcherNode.hasMouse():
            if not self.base.mouseWatcherNode.isOverRegion():
                self.is_orbiting = True
                self.last_mouse_pos = None

    def stop_orbit(self):
        self.is_orbiting = False

    def update(self, dt):
        player = getattr(self.base, 'player', None)
        if not player:
            return
            
        target_np = player.root if hasattr(player, 'root') else player
        if target_np.isEmpty():
            return

        # 1. A horgony követi a hajót
        self.camera_anchor.setPos(target_np.getPos())

        # 2. Forgatás kezelése
        if self.is_orbiting and self.base.mouseWatcherNode.hasMouse():
            mpos = self.base.mouseWatcherNode.getMouse()
            
            if self.last_mouse_pos is None:
                self.last_mouse_pos = Vec3(mpos.getX(), mpos.getY(), 0)
            
            delta_x = mpos.getX() - self.last_mouse_pos.getX()
            delta_y = mpos.getY() - self.last_mouse_pos.getY()
            
            new_h = self.camera_anchor.getH() - (delta_x * self.orbit_speed)
            new_p = self.camera_anchor.getP() + (delta_y * self.orbit_speed)
            
            # Limitáljuk a dőlésszöget
            new_p = max(-80, min(80, new_p))
            
            self.camera_anchor.setHpr(new_h, new_p, 0)
            self.last_mouse_pos = Vec3(mpos.getX(), mpos.getY(), 0)
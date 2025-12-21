from panda3d.core import Vec3, WindowProperties
from direct.showbase.DirectObject import DirectObject

class CameraSystem(DirectObject):
    def __init__(self, base):
        self.base = base
        self.base.disableMouse()  # Kikapcsoljuk az alapértelmezett Panda3D kamerát
        
        # Kamera horgony (Anchor) - ez követi a hajót, és ezt forgatjuk
        self.camera_anchor = self.base.render.attachNewNode("CameraAnchor")
        self.base.camera.reparentTo(self.camera_anchor)
        
        # Kezdeti távolság és magasság a hajótól
        self.base.camera.setPos(0, -50, 15) 
        self.base.camera.lookAt(0, 0, 0)
        
        self.orbit_speed = 100.0
        self.is_orbiting = False
        
        # Egér események figyelése
        self.accept("mouse3", self.start_orbit)     # Jobb klikk le
        self.accept("mouse3-up", self.stop_orbit)  # Jobb klikk fel
        
        self.last_mouse_pos = None

    def start_orbit(self):
        # Csak akkor engedjük a forgatást, ha nincs GUI elem alatt az egér
        if self.base.mouseWatcherNode.hasMouse():
            # Ellenőrizzük, hogy az egér épp egy DirectGUI régió felett van-e
            if not self.base.mouseWatcherNode.isOverRegion():
                self.is_orbiting = True
                self.last_mouse_pos = None

    def stop_orbit(self):
        self.is_orbiting = False

    def update(self, dt):
        ship = getattr(self.base, 'player', None)
        if not ship or ship.isEmpty():
            return

        # 1. A horgony mindig kövesse a hajót
        self.camera_anchor.setPos(ship.getPos())

        # 2. Forgatás kezelése
        if self.is_orbiting and self.base.mouseWatcherNode.hasMouse():
            mpos = self.base.mouseWatcherNode.getMouse() # -1 és 1 közötti érték
            
            if self.last_mouse_pos is None:
                self.last_mouse_pos = Vec3(mpos.getX(), mpos.getY(), 0)
            
            # Kiszámoljuk az elmozdulást
            delta_x = mpos.getX() - self.last_mouse_pos.getX()
            delta_y = mpos.getY() - self.last_mouse_pos.getY()
            
            # Vízszintes (Heading) és függőleges (Pitch) forgatás
            new_h = self.camera_anchor.getH() - (delta_x * self.orbit_speed)
            new_p = self.camera_anchor.getP() + (delta_y * self.orbit_speed)
            
            # Függőleges korlátozás, hogy ne forduljon át a kamera (opcionális)
            if new_p > 80: new_p = 80
            if new_p < -80: new_p = -80
            
            self.camera_anchor.setHpr(new_h, new_p, 0)
            
            self.last_mouse_pos = Vec3(mpos.getX(), mpos.getY(), 0)
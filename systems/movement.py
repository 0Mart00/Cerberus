from panda3d.core import Vec3

class MovingSystem:
    """
    Kezeli a játékos hajójának mozgását és forgatását.
    """
    def __init__(self, app):
        self.app = app
        
        # Billentyűzet állapotának tárolása
        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "roll_left": False,
            "roll_right": False
        }
        
        # Irányítás beállítása (WASD + QE)
        self.app.accept("w", self.update_key, ["forward", True])
        self.app.accept("w-up", self.update_key, ["forward", False])
        self.app.accept("s", self.update_key, ["backward", True])
        self.app.accept("s-up", self.update_key, ["backward", False])
        self.app.accept("a", self.update_key, ["left", True])
        self.app.accept("a-up", self.update_key, ["left", False])
        self.app.accept("d", self.update_key, ["right", True])
        self.app.accept("d-up", self.update_key, ["right", False])
        self.app.accept("q", self.update_key, ["roll_left", True])
        self.app.accept("q-up", self.update_key, ["roll_left", False])
        self.app.accept("e", self.update_key, ["roll_right", True])
        self.app.accept("e-up", self.update_key, ["roll_right", False])
        
        # Sebesség beállítások
        self.move_speed = 100.0
        self.turn_speed = 150.0

    def update_key(self, key, state):
        self.key_map[key] = state

    def update(self, dt):
        # Ha nincs játékos vagy IDLE állapot van, ne csináljon semmit
        if not self.app.player or self.app.player.isEmpty():
            return
            
        if hasattr(self.app, 'stats') and self.app.stats.is_idle:
            return

        # Forgás (Heading és Roll)
        if self.key_map["left"]:
            self.app.player.setH(self.app.player.getH() + self.turn_speed * dt)
        if self.key_map["right"]:
            self.app.player.setH(self.app.player.getH() - self.turn_speed * dt)
            
        if self.key_map["roll_left"]:
            self.app.player.setR(self.app.player.getR() - self.turn_speed * 0.5 * dt)
        if self.key_map["roll_right"]:
            self.app.player.setR(self.app.player.getR() + self.turn_speed * 0.5 * dt)

        # Mozgás (Előre/Hátra az Y tengelyen a Panda3D-ben)
        move_vec = Vec3(0, 0, 0)
        if self.key_map["forward"]:
            move_vec.setY(self.move_speed * dt)
        if self.key_map["backward"]:
            move_vec.setY(-self.move_speed * dt)
            
        # Relatív mozgás a hajó saját orientációjához képest
        self.app.player.setPos(self.app.player, move_vec)
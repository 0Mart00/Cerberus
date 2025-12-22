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
        # Ellenőrizzük, hogy a player létezik-e
        if not self.app.player:
            return

        # MEGOLDÁS: Mindig a fizikai NodePath-ot használjuk a műveletekhez
        # Ha a player egy wrapper osztály, akkor a .node attribútumot vesszük
        target_np = self.app.player.node if hasattr(self.app.player, 'node') else self.app.player
        
        if target_np.isEmpty():
            return
            
        if hasattr(self.app, 'stats') and self.app.stats.is_idle:
            return

        # Forgás (A target_np-n végezzük)
        if self.key_map["left"]:
            target_np.setH(target_np.getH() + self.turn_speed * dt)
        if self.key_map["right"]:
            target_np.setH(target_np.getH() - self.turn_speed * dt)
            
        if self.key_map["roll_left"]:
            target_np.setR(target_np.getR() - self.turn_speed * 0.5 * dt)
        if self.key_map["roll_right"]:
            target_np.setR(target_np.getR() + self.turn_speed * 0.5 * dt)

        # Mozgásvektor
        move_vec = Vec3(0, 0, 0)
        if self.key_map["forward"]:
            move_vec.setY(self.move_speed * dt)
        if self.key_map["backward"]:
            move_vec.setY(-self.move_speed * dt)
            
        # JAVÍTOTT HIVATKOZÁS: setPos(referencia_nodepath, vektor)
        target_np.setPos(target_np, move_vec)
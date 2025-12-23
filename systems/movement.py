from panda3d.core import Vec3, NodePath

class MovingSystem:
    """
    Kezeli a játékos hajójának mozgását és forgatását (WASD + QE).
    """
    def __init__(self, game):
        self.game = game
        
        # Billentyűzet állapotának tárolása
        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "roll_left": False,
            "roll_right": False
        }
        
        # Irányítás beállítása
        self.setup_controls()
        
        # Sebesség beállítások
        self.move_speed = 100.0
        self.turn_speed = 150.0

    def setup_controls(self):
        """Regisztrálja a billentyűleütéseket."""
        # Megadjuk a billentyűket és a hozzájuk tartozó akciókat
        keys = {
            "w": "forward", "s": "backward",
            "a": "left", "d": "right",
            "q": "roll_left", "e": "roll_right"
        }
        
        for key, action in keys.items():
            self.game.accept(key, self.update_key, [action, True])
            self.game.accept(f"{key}-up", self.update_key, [action, False])
            # Támogatjuk a nagybetűket is (ha be van kapcsolva a Caps Lock)
            self.game.accept(key.upper(), self.update_key, [action, True])
            self.game.accept(f"{key.upper()}-up", self.update_key, [action, False])

    def update_key(self, key, state):
        """Frissíti a belső billentyűzet-állapotot."""
        self.key_map[key] = state

    def update(self, dt):
        """
        Frissíti a játékos hajójának pozícióját és rotációját.
        """
        # 1. Játékos objektum keresése
        player_obj = None
        if hasattr(self.game, 'player') and self.game.player:
            player_obj = self.game.player
        elif hasattr(self.game, 'local_ship') and self.game.local_ship:
            player_obj = self.game.local_ship

        if not player_obj:
            return

        # 2. A tényleges Panda3D NodePath megkeresése
        target_np = None
        # A main.py-ban a PlayerShipData-ban 'node' a neve!
        if hasattr(player_obj, 'node'):
            target_np = player_obj.node
        elif hasattr(player_obj, 'root'):
            target_np = player_obj.root
        elif hasattr(player_obj, 'node_path'):
            target_np = player_obj.node_path
        elif isinstance(player_obj, NodePath):
            target_np = player_obj
        
        # 3. Ellenőrzés, hogy sikerült-e megtalálni a NodePath-ot
        if not target_np or target_np.isEmpty():
            return

        # --- MOZGÁS ÉS FORGÁS ---

        # Forgás (H: Heading / Balra-Jobbra)
        if self.key_map["left"]:
            target_np.setH(target_np.getH() + self.turn_speed * dt)
        if self.key_map["right"]:
            target_np.setH(target_np.getH() - self.turn_speed * dt)
            
        # Orsózás (R: Roll / Dőlés)
        if self.key_map["roll_left"]:
            target_np.setR(target_np.getR() - self.turn_speed * 0.5 * dt)
        if self.key_map["roll_right"]:
            target_np.setR(target_np.getR() + self.turn_speed * 0.5 * dt)

        # Mozgás előre/hátra (Relatív Y tengely)
        move_vec = Vec3(0, 0, 0)
        if self.key_map["forward"]:
            move_vec.setY(self.move_speed * dt)
        if self.key_map["backward"]:
            move_vec.setY(-self.move_speed * dt)

        # Pozíció frissítése relatív módon (önmagához képest)
        if move_vec.length_squared() > 0:
            target_np.setPos(target_np, move_vec)
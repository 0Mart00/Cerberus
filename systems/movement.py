from panda3d.core import Vec3, NodePath

class MovingSystem:
    """
    Kezeli a játékos hajójának mozgását (WASD + QE), 
    valamint a funkcióbillentyűk többes hozzárendelését (F1-F10).
    """
    def __init__(self, game):
        self.game = game
        
        # Billentyűzet állapotának tárolása a mozgáshoz
        self.key_map = {
            "forward": False, "backward": False,
            "left": False, "right": False,
            "roll_left": False, "roll_right": False
        }
        
        # Funkcióbillentyűk hozzárendelései (egy gombhoz több item ID is tartozhat)
        # Példa: "F1": ["laser_1", "laser_2"]
        self.function_key_assignments = {f"F{i}": [] for i in range(1, 11)}
        self.ctrl_key_assignments = {f"F{i}": [] for i in range(1, 11)}
        self.shift_key_assignments = {f"F{i}": [] for i in range(1, 11)}

        # Teszt jelleggel rendeljünk két lézert az F1-hez
        self.function_key_assignments["F1"] = ["laser_small_left", "laser_small_right"]
        
        # Irányítás beállítása
        self.setup_controls()
        
        self.move_speed = 100.0
        self.turn_speed = 150.0

    def setup_controls(self):
        """Regisztrálja a mozgást és a funkcióbillentyűket."""
        # Mozgás billentyűk (W, A, S, D, Q, E)
        keys = {"w": "forward", "s": "backward", "a": "left", "d": "right", "q": "roll_left", "e": "roll_right"}
        for key, action in keys.items():
            self.game.accept(key, self.update_key, [action, True])
            self.game.accept(f"{key}-up", self.update_key, [action, False])

        # F1 - F10 regisztrálása (Sima, CTRL, SHIFT)
        for i in range(1, 11):
            f_key = f"f{i}"
            self.game.accept(f_key, self.execute_function_key, [f"F{i}", self.function_key_assignments])
            self.game.accept(f"control-{f_key}", self.execute_function_key, [f"F{i}", self.ctrl_key_assignments])
            self.game.accept(f"shift-{f_key}", self.execute_function_key, [f"F{i}", self.shift_key_assignments])

    def execute_function_key(self, key_id, assignment_dict):
        """
        Végrehajtja az adott billentyűhöz rendelt összes item műveletét.
        """
        assigned_items = assignment_dict.get(key_id, [])
        
        if not assigned_items:
            print(f"[DEBUG] {key_id} lenyomva, de nincs hozzárendelve semmi.")
            return

        print(f"[ACTION] {key_id} aktiválása! Hozzárendelt elemek száma: {len(assigned_items)}")
        
        for item_id in assigned_items:
            # Itt hívhatod meg a combat vagy item rendszert
            # Példa: self.game.combat_system.fire_weapon(item_id)
            print(f"  -> {item_id} aktiválva.")

    def update_key(self, key, state):
        self.key_map[key] = state

    def update(self, dt):
        """A hajó mozgásának frissítése (Változatlan marad a korábbihoz képest)"""
        player_obj = getattr(self.game, 'player', getattr(self.game, 'local_ship', None))
        if not player_obj: return

        target_np = None
        for attr in ['node', 'root', 'node_path']:
            if hasattr(player_obj, attr):
                target_np = getattr(player_obj, attr)
                break
        if isinstance(player_obj, NodePath): target_np = player_obj
        
        if not target_np or target_np.isEmpty(): return

        if self.key_map["left"]: target_np.setH(target_np.getH() + self.turn_speed * dt)
        if self.key_map["right"]: target_np.setH(target_np.getH() - self.turn_speed * dt)
        if self.key_map["roll_left"]: target_np.setR(target_np.getR() - self.turn_speed * 0.5 * dt)
        if self.key_map["roll_right"]: target_np.setR(target_np.getR() + self.turn_speed * 0.5 * dt)

        move_vec = Vec3(0, 0, 0)
        if self.key_map["forward"]: move_vec.setY(self.move_speed * dt)
        if self.key_map["backward"]: move_vec.setY(-self.move_speed * dt)

        if move_vec.length_squared() > 0:
            target_np.setPos(target_np, move_vec)
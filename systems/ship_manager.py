# Cerberus/systems/ship_manager.py
from panda3d.core import NodePath, Vec3, TextureStage, TexGenAttrib
from entities.ship import Ship
import globals as g
import random

class ShipManager:
    def __init__(self, game_app):
        self.app = game_app
        self.ships = {}
        self.master_models = [] # Lista a betöltött modelleknek (tömb)

    def load_master_models(self, model_configs):
        """
        Tömböt vár, amiben szótárak vannak a modellekkel és textúrákkal.
        Példa: [{"model": "...", "tex": "..."}, {"model": "...", "tex": "..."}]
        """
        for config in model_configs:
            model_url = config.get("model")
            texture_url = config.get("tex")
            
            try:
                # Modell betöltése
                m_node = self.app.loader.loadModel(model_url)
                
                # Textúrázás (Projected texture setup)
                if texture_url:
                    tex = self.app.loader.loadTexture(texture_url)
                    ts = TextureStage('instanced_ts')
                    # Világkoordináta alapú textúra vetítés (ahogy kérted)
                    m_node.setTexGen(ts, TexGenAttrib.MWorldPosition)
                    m_node.setTexProjector(ts, self.app.render, m_node)
                    m_node.setTexScale(ts, 0.5, 0.5)
                    m_node.setTexture(ts, tex)
                    m_node.setShaderAuto()
                
                m_node.detachNode()
                self.master_models.append(m_node)
                print(f"[SYSTEM] Master modell hozzáadva a listához: {model_url}")
            except Exception as e:
                print(f"[ERROR] Nem sikerült betölteni a modellt ({model_url}): {e}")

    def spawn_horde(self, count=200):
        """200 (vagy semennyi) hajó legenerálása a tömbből véletlenszerűen választva."""
        if not self.master_models:
            print("[ERROR] Nincs egyetlen master modell sem betöltve! Horda elmarad.")
            return

        for i in range(count):
            ship_id = 5000 + i
            # Létrehozzuk az "üres" hajót (a Ship osztály nem tölt be semmit)
            new_ship = Ship(self.app, ship_id, name=f"Drone-{i}")
            
            # VÉLETLENSZERŰ választás a tömbből
            chosen_master = random.choice(self.master_models)
            
            # Instancing: ráakasztjuk a modellt a hajó root node-jára
            new_ship.model = chosen_master.instanceTo(new_ship.root)
            
            # Szórás az űrben
            x = random.uniform(-1500, 1500)
            y = random.uniform(-1500, 1500)
            z = random.uniform(-100, 100)
            new_ship.root.setPos(x, y, z)
            
            self.ships[ship_id] = new_ship

    def spawn_player(self, player_id, name="PlayerOne"):
        """A játékos hajójának létrehozása és vizuális felépítése a tömb első elemével."""
        player_ship = Ship(self.app, player_id, is_local=True, name=name)
        
        if self.master_models:
            # A játékos alapértelmezetten az első (0.) modellt kapja a tömbből
            player_ship.model = self.master_models[0].instanceTo(player_ship.root)
            # Biztosítjuk, hogy a modell a root alatt legyen
            player_ship.model.reparentTo(player_ship.root)
        else:
            print("[WARNING] Játékos modell nélkül jött létre (nincs master_models)!")
            
        return player_ship

    def setup_ship_visuals(self, ship_instance, model_index=0):
        """
        Ráakasztja a tömb egyik modelljét egy létező Ship példányra.
        :param model_index: Melyik modellt használja a tömbből (alapértelmezett: 0)
        """
        if not self.master_models:
            print("[ERROR] Nincs betöltve master modell tömb!")
            return

        # Ha már volt rajta modell, eltávolítjuk
        if hasattr(ship_instance, 'model') and ship_instance.model:
            ship_instance.model.removeNode()

        # Ellenőrizzük, hogy az index érvényes-e
        idx = model_index if model_index < len(self.master_models) else 0
        
        # Kiválasztott modell példányosítása
        ship_instance.model = self.master_models[idx].instanceTo(ship_instance.root)
        print(f"[SYSTEM] Vizuális megjelenítés (Index: {idx}) hozzáadva: {ship_instance.name}")

    def update(self, dt):
        """LOD alapú frissítés: csak a közelieket frissítjük minden frame-ben."""
        if not self.app.local_ship: 
            return
            
        player_pos = self.app.local_ship.get_pos()
        frame_cnt = self.app.taskMgr.getFrameCount()
        
        for ship in self.ships.values():
            # Távolság négyzete (gyorsabb, mint a sima távolság)
            dist_sq = (ship.root.getPos() - player_pos).lengthSquared()
            
            if dist_sq < 800**2:
                # KÖZEL: Teljes AI és fizikai frissítés
                ship.update(dt)
            elif dist_sq < 2500**2:
                # KÖZEPES: Csak pajzs regeneráció, mozgás nincs, és csak minden 5. frame-ben
                if frame_cnt % 5 == 0:
                    if hasattr(ship, 'current_shield') and ship.current_shield < ship.max_shield:
                        ship.current_shield = min(ship.max_shield, ship.current_shield + 1.0 * (dt * 5))
            else:
                # MESSZE: Semmilyen erőforrást nem használ
                pass

    def clear_all(self):
        """Minden kezelt hajó törlése a világból."""
        for ship in self.ships.values():
            ship.destroy()
        self.ships.clear()
# Cerberus/systems/ship_manager.py
from panda3d.core import NodePath, Vec3, TextureStage, TexGenAttrib
from entities.ship import Ship
import globals as g
import random

class ShipManager:
    def __init__(self, game_app):
        self.app = game_app
        self.ships = {}
        self.master_model = None

    def load_master_model(self, model_url, texture_url):
        """
        Itt történik a varázslat: egyszeri betöltés és textúrázás.
        """
        # 1. Modell betöltése
        self.master_model = self.app.loader.loadModel(model_url)
        
        # 2. Textúra ráhúzása (a te speciális világ-koordinátás módszereddel)
        tex = self.app.loader.loadTexture(texture_url)
        ts = TextureStage('assets/textures/ship_skin_red.png')
        self.master_model.setTexGen(ts, TexGenAttrib.MWorldPosition)
        self.master_model.setTexProjector(ts, self.app.render, self.master_model)
        self.master_model.setTexScale(ts, 0.5, 0.5)
        self.master_model.setTexture(ts, tex)
        self.master_model.setShaderAuto()
        
        # Leválasztjuk, hogy ne jelenjen meg a (0,0,0)-n feleslegesen
        self.master_model.detachNode()
        print(f"[SYSTEM] Manager betöltötte a központi modellt: {model_url}")

    def spawn_horde(self, count=10):
        if not self.master_model:
            print("[ERROR] Előbb be kell tölteni a modellt a load_master_model-lel!")
            return

        for i in range(count):
            ship_id = 5000 + i
            # Létrehozzuk az "üres" hajót
            new_ship = Ship(self.app, ship_id, name=f"Drone-{i}")
            
            # KÍVÜLRŐL adjuk oda neki a modellt (Instancing)
            new_ship.model = self.master_model.instanceTo(new_ship.root)
            
            # Elhelyezés
            x = random.uniform(-1500, 1500)
            y = random.uniform(-1500, 1500)
            z = random.uniform(-50, 50)
            new_ship.root.setPos(x, y, z)
            
            self.ships[ship_id] = new_ship
    def update(self, dt):
        if not self.app.local_ship: return
        player_pos = self.app.local_ship.get_pos()
        
        for ship in self.ships.values():
            # A hajó root NodePath-ját használjuk a távolsághoz
            dist_sq = (ship.root.getPos() - player_pos).lengthSquared()
            
            if dist_sq < 800**2:
                # KÖZEL: Teljes logika (ütközés, AI, pajzs)
                ship.update(dt)
            elif dist_sq < 2500**2:
                # MESSZE: Csak a pajzsot regeneráljuk néha, mozgás nincs
                ship.current_shield = min(ship.max_shield, ship.current_shield + 1.0 * dt)



    def spawn_ships(self, count=200):
        """Tömeges hajó generálás optimalizált módon."""
        for i in range(count):
            ship_id = f"DRONE_{i}"
            # A Ship osztályodat használjuk, de módosítjuk a betöltést
            new_ship = Ship(self.game, ship_id, is_local=False, name=f"Drone {i}")
            
            # 2. Vizuális optimalizáció: a modell lecserélése egy instance-re
            if hasattr(new_ship, 'model'):
                new_ship.model.removeNode() # Töröljük az egyedileg betöltöttet
            
            # Új példány (instance) készítése a mester modellből
            instance = self.ship_master_model.instanceTo(new_ship.root)
            new_ship.model = instance
            
            # Véletlenszerű pozíció
            pos = Vec3(g.random.uniform(-1000, 1000), 
                       g.random.uniform(-1000, 1000), 
                       g.random.uniform(-100, 100))
            new_ship.set_pos(pos)
            
            self.ships[ship_id] = new_ship

    def setup_ship_visuals(self, ship_instance):
        """
        Ráakasztja a központi modellt egy létező Ship példányra.
        Használható a játékoshoz és a drónokhoz is.
        """
        if not self.master_model:
            print("[ERROR] Nincs master modell! Hívd meg a load_master_model-t.")
            return

        # Ha már volt rajta valami, leválasztjuk
        if ship_instance.model:
            ship_instance.model.removeNode()

        # Instancing: a központi modell egy példányát adjuk oda
        ship_instance.model = self.master_model.instanceTo(ship_instance.root)
        print(f"[SYSTEM] Vizuális megjelenítés hozzáadva: {ship_instance.name}")

    def spawn_player(self, player_id, name="PlayerOne"):
        """Létrehozza a játékos hajóját és rárakja a modellt."""
        from entities.ship import Ship
        
        # Itt a self.app-ot adjuk át managernek, így nem lesz AttributeError!
        player_ship = Ship(self.app, player_id, is_local=True, name=name)
        
        # Modell hozzáadása, ha be van töltve
        if self.master_model:
            player_ship.model = self.master_model.instanceTo(player_ship.root)
            player_ship.model.reparentTo(player_ship.root)
            
        return player_ship
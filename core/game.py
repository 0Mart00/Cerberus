from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import loadPrcFile
import random

from ui.menus import MainMenu
from ui.hud import TargetListUI
# Importáljuk az új ablakkezelőt
from ui.windows import WindowManager

from net.server import GameServer
from net.client import GameClient
from net.protocol import create_pos_datagram
from entities.ship import Ship

class CerberusGame(ShowBase):
    def __init__(self):
        # Config betöltése
        loadPrcFile("config/settings.prc")
        ShowBase.__init__(self)
        self.disableMouse() # Saját kamera irányítás

        # Rendszerek
        self.server = None
        self.client = GameClient(self)
        
        # Új ablak kezelő inicializálása
        self.window_manager = WindowManager(self)
        
        self.menu = MainMenu(self)
        self.hud = TargetListUI(self) # A HUD már használja a window_manager-t
        
        # Játékállapot
        self.local_ship = None
        self.remote_ships = {} # {id: Ship}
        self.my_id = 0 

    def start_host(self):
        """Hosztolás indítása: Szerver + Helyi Kliens"""
        self.server = GameServer(self)
        if self.server.start():
            self.my_id = 1
            # Entitások generálása a Hostnak
            self.spawn_test_entities()
            self.start_gameplay()

    def spawn_test_entities(self):
        """Véletlenszerű objektumok elhelyezése a teszteléshez"""
        types = ["Aszteroida", "Roncs", "Kalóz Drón", "Teherhajó"]
        
        for i in range(5):
            entity_id = 200 + i
            e_type = random.choice(types)
            e_name = f"Objektum-{i+101}"
            
            # Létrehozunk egy 'Ship' példányt entitásként
            entity = Ship(self, entity_id, is_local=False, name=e_name, ship_type=e_type)
            
            # Véletlenszerű pozíció
            x = random.uniform(-100, 100)
            y = random.uniform(-100, 100)
            z = random.uniform(-20, 20)
            entity.set_pos(x, y, z)
            
            self.remote_ships[entity_id] = entity
            print(f"[SYSTEM] Entitás létrehozva: {e_name} ({e_type}) @ {x:.1f}, {y:.1f}")

    def join_game(self):
        """Csatlakozás kliensként"""
        ip = self.menu.ip_entry.get()
        if self.client.connect(ip):
            self.my_id = 100 + int(Task.TaskManager.globalClock.getRealTime() * 10)
            self.start_gameplay()

    def start_gameplay(self):
        self.menu.hide()
        self.hud.show() # Most jelenítjük meg a célpont listát és a menüket
        
        # Saját hajó létrehozása
        self.local_ship = Ship(self, self.my_id, is_local=True, name="Hős", ship_type="Vezérhajó")
        self.local_ship.set_pos(0, 0, 0) # 0,0,0 az űr közepe
        
        # Kamera a hajóra
        self.camera.reparentTo(self.local_ship.model)
        self.camera.setPos(0, -30, 10)
        self.camera.lookAt(self.local_ship.model)

        # Loopok
        taskMgr.add(self.update_loop, "GameUpdateLoop")

    def select_target(self, ship_id):
        """HUD hívja meg: Beállítja az aktív célpontot a hajónak"""
        if self.local_ship and ship_id in self.remote_ships:
            target = self.remote_ships[ship_id]
            self.local_ship.target_entity = target
            print(f"[GAME] Célpont befogva: {target.name}")

    def set_autopilot(self, target_id, mode):
        """Utasítás a hajónak (HUD-ról jön)"""
        if target_id in self.remote_ships:
            target_ship = self.remote_ships[target_id]
            print(f"Robotpilóta: {mode} -> {target_ship.name}")
            self.local_ship.target_entity = target_ship
            self.local_ship.autopilot_mode = mode

    def update_loop(self, task):
        dt = globalClock.getDt()
        
        if self.local_ship:
            self.local_ship.update(dt)
            
            # HUD frissítése a távoli hajókkal
            self.hud.update_list(self.local_ship, self.remote_ships)

            # Pozíció küldése hálózaton
            pos = self.local_ship.get_pos()
            dg = create_pos_datagram(self.my_id, pos.x, pos.y, pos.z)
            self.client.send(dg)
            
            if self.server and self.server.active:
                self.server.broadcast(dg)

        return Task.cont

    def update_remote_ship(self, sender_id, x, y, z):
        """Hálózatról jövő adat feldolgozása"""
        if sender_id == self.my_id:
            return 

        if sender_id not in self.remote_ships:
            print(f"Új hajó észlelve: ID {sender_id}")
            # Véletlenszerű nevet adunk neki demonstrációként
            new_ship = Ship(self, sender_id, is_local=False, name=f"Ellenség-{sender_id}", ship_type="Drón")
            self.remote_ships[sender_id] = new_ship
        
        self.remote_ships[sender_id].set_pos(x, y, z)
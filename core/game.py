from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import loadPrcFile
import random

# UI Importok
from ui.menus import MainMenu
from ui.windows import WindowManager
from systems.generation import GalaxyManager

# Hálózati Importok
from net.server import GameServer
from net.client import GameClient
from net.protocol import (
    create_pos_datagram, 
    MSG_SYNC_CORE, 
    MSG_SYNC_SUPPORT, 
    MSG_SYNC_SYSTEM
)

# Entitás Importok
from entities import Ship, Asteroid, Planet, Wreck, Stargate 

class CerberusGame(ShowBase):
    def __init__(self, item_db=None):
        """
        A Cerberus Online játékmag inicializálása.
        :param item_db: Az előre betöltött tárgy adatbázis (ItemDatabase).
        """
        # Konfigurációs fájl betöltése
        try:
            loadPrcFile("config/settings.prc")
        except:
            pass
            
        ShowBase.__init__(self)

        # Központi rendszerek
        self.item_db = item_db
        self.server = None
        self.client = GameClient(self)
        self.window_manager = WindowManager(self)
        self.galaxy_manager = WindowManager(self)
        
        # UI példányosítása
        self.menu = MainMenu(self)
        
        # Játékállapot adatok
        self.local_ship = None
        self.remote_ships = {} 
        self.my_id = 0 
        
        print("[SYSTEM] Cerberus Játékmag inicializálva.")

    def start_host(self):
        """Szerver indítása és helyi csatlakozás (Host mód)."""
        self.server = GameServer(self)
        if self.server.start():
            # A Host ID-ja fixen 1
            self.my_id = 1
            # Világ generálása (csak a Host generál entitásokat)
            self.spawn_test_entities()
            self.start_gameplay()
            return True
        return False

    def join_game(self):
        """Csatlakozás meglévő szerverhez a menüben megadott IP alapján."""
        ip = self.menu.ip_entry.get()
        if self.client.connect(ip):
            # Egyedi ID generálása az időbélyeg alapján
            self.my_id = 100 + int(Task.TaskManager.globalClock.getRealTime() * 10)
            self.start_gameplay()
            return True
        return False

    def spawn_test_entities(self):
        """Véletlenszerű objektumok elhelyezése az űrben a teszteléshez."""
        ENTITY_CLASSES = {
            "Aszteroida": Asteroid,
            "Roncs": Wreck,
            "Csillagkapu": Stargate,
            "Bolygó": Planet,
            "NPC Hajó": Ship
        }
        
        # Egy központi bolygó létrehozása
        planet_id = 1000
        planet = Planet(self, planet_id, name="Nexus Prime")
        planet.set_pos(1000, 1000, 0)
        self.remote_ships[planet_id] = planet
        
        # 10 véletlenszerű entitás szórása
        for i in range(10):
            entity_id = 200 + i
            e_type_name = random.choice(list(ENTITY_CLASSES.keys()))
            EntityClass = ENTITY_CLASSES[e_type_name]
            e_name = f"{e_type_name}-{i+1}"
            
            if EntityClass == Ship:
                entity = EntityClass(self, entity_id, is_local=False, name=e_name, ship_type="Drón")
            else:
                entity = EntityClass(self, entity_id, name=e_name)

            # Véletlenszerű koordináták
            x = random.uniform(-800, 800)
            y = random.uniform(-800, 800)
            z = random.uniform(-50, 50)
            entity.set_pos(x, y, z)
            
            self.remote_ships[entity_id] = entity
            print(f"[SYSTEM] Entitás generálva: {e_name} pozíció: {x:.1f}, {y:.1f}")

    def start_gameplay(self):
        """Menü elrejtése és a tényleges játék elindítása."""
        self.menu.hide()
        
        # Saját hajó létrehozása a világ közepén
        self.local_ship = Ship(self, self.my_id, is_local=True, name="Hős", ship_type="Vezérhajó")
        self.local_ship.set_pos(0, 0, 0)
        
        # Felszerelés betöltése az adatbázisból
        if self.item_db:
            # Alapértelmezett Core (ID: 1) felszerelése
            starter_core = self.item_db.get_core(1)
            if starter_core:
                self.local_ship.equip_core(starter_core)
                print(f"[GAME] Alapértelmezett mag felszerelve: {starter_core.name}")
            
            # Felszerelés szinkronizálása a hálózaton
            self.sync_my_equipment()

        # Kamera rögzítése a hajóhoz (TPS nézet)
        self.camera.reparentTo(self.local_ship.model)
        self.camera.setPos(0, -35, 12)
        self.camera.lookAt(self.local_ship.model)

        # Fő frissítési ciklus elindítása
        taskMgr.add(self.update_loop, "GameUpdateLoop")

    def sync_my_equipment(self):
        """Saját bónuszok (Core, Support, System) elküldése a többi játékosnak."""
        if not self.local_ship: return
        
        from direct.distributed.PyDatagram import PyDatagram
        
        # Core szinkronizálása
        if self.local_ship.core:
            dg = PyDatagram()
            dg.addUint8(MSG_SYNC_CORE)
            dg.addUint16(self.my_id)
            self.local_ship.core.pack(dg)
            self.client.send(dg)
            
        # Support/System bónuszok szinkronizálása
        if hasattr(self.local_ship, 'support') and self.local_ship.support:
            dg = PyDatagram()
            dg.addUint8(MSG_SYNC_SUPPORT)
            dg.addUint16(self.my_id)
            self.local_ship.support.pack(dg)
            self.client.send(dg)

    def update_remote_equipment(self, sender_id, type_name, equipment_obj):
        """Távoli hajó felszerelésének frissítése a hálózatról jövő adatok alapján."""
        if sender_id in self.remote_ships:
            ship = self.remote_ships[sender_id]
            if isinstance(ship, Ship):
                if type_name == "core":
                    ship.equip_core(equipment_obj)
                elif type_name == "support":
                    ship.equip_support(equipment_obj)
                elif type_name == "system":
                    ship.equip_system(equipment_obj)
                print(f"[NET] {ship.name} felszerelése frissítve: {equipment_obj.name}")

    def select_target(self, entity_id):
        """Célpont befogása (HUD vagy kattintás hívja meg)."""
        if self.local_ship and entity_id in self.remote_ships:
            target = self.remote_ships[entity_id]
            self.local_ship.target_entity = target
            print(f"[GAME] Célpont befogva: {target.name}")

    def set_autopilot(self, entity_id, mode):
        """Robotpilóta utasítások kezelése."""
        if entity_id in self.remote_ships:
            target_entity = self.remote_ships[entity_id]
            print(f"[PILOT] Robotpilóta: {mode} -> {target_entity.name}")
            self.local_ship.target_entity = target_entity
            self.local_ship.autopilot_mode = mode

    def update_loop(self, task):
        """Minden frame-ben lefutó frissítési ciklus."""
        dt = globalClock.getDt()
        
        if self.local_ship:
            # Saját hajó frissítése
            self.local_ship.update(dt)
            
            # Távoli objektumok frissítése
            for entity in self.remote_ships.values():
                entity.update(dt)
            
            # Pozíció szinkronizálása a hálózaton
            pos = self.local_ship.get_pos()
            dg = create_pos_datagram(self.my_id, pos.x, pos.y, pos.z)
            self.client.send(dg)
            
            # Ha Host vagyunk, közvetítjük az adatot a klienseknek
            if self.server and self.server.active:
                self.server.broadcast(dg)

        return Task.cont

    def update_remote_ship(self, sender_id, x, y, z):
        """Új távoli hajó létrehozása vagy meglévő pozíciójának frissítése."""
        if sender_id == self.my_id:
            return 

        if sender_id not in self.remote_ships:
            print(f"[NET] Új játékos észlelve: ID {sender_id}")
            new_ship = Ship(self, sender_id, is_local=False, name=f"Pilóta-{sender_id}", ship_type="Drón")
            self.remote_ships[sender_id] = new_ship
            
            # Ha mi vagyunk a Host, elküldjük neki a mi felszerelésünket is
            if self.server and self.server.active:
                self.sync_my_equipment()
        
        self.remote_ships[sender_id].set_pos(x, y, z)
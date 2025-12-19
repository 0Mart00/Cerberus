from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import loadPrcFile
import random

from menus import MainMenu
from windows import WindowManager

from net.server import GameServer
from net.client import GameClient
from net.protocol import create_pos_datagram, MSG_SYNC_CORE, MSG_SYNC_SUPPORT, MSG_SYNC_SYSTEM
# Importáljuk az összes entitás osztályt
from entities import Ship, Asteroid, Planet, Wreck, Stargate 

class CerberusGame(ShowBase):
    def __init__(self, item_db=None): # Módosítva: fogadja az item_db-t
        # Config betöltése
        loadPrcFile("config/settings.prc")
        ShowBase.__init__(self)
        self.disableMouse() 

        # Rendszerek
        self.item_db = item_db # Eltároljuk az adatbázist
        self.server = None
        self.client = GameClient(self)
        
        self.window_manager = WindowManager(self)
        
        # Hozzáadjuk a Base referenciát a Window Managerhez
        self.menu = MainMenu(self)
        
        # Játékállapot
        self.local_ship = None
        self.remote_ships = {} 
        self.my_id = 0 
        
        # NOTE: A zoomolás és görgetés kezelő task a HUD-ban van beállítva.

    def start_host(self):
        """Hosztolás indítása: Szerver + Helyi Kliens. Visszatérési érték: bool (sikerült-e)."""
        self.server = GameServer(self)
        if self.server.start():
            self.my_id = 1
            # Entitások generálása a Hostnak (itt hívjuk meg az új logikát)
            self.spawn_test_entities()
            self.start_gameplay()
            return True # Siker
        return False # Hiba

    def spawn_test_entities(self):
        """Véletlenszerű objektumok elhelyezése a teszteléshez"""
        
        ENTITY_CLASSES = {
            "Aszteroida": Asteroid,
            "Roncs": Wreck,
            "Csillagkapu": Stargate,
            "Bolygó": Planet,
            "NPC Hajó": Ship
        }
        
        # Statikus, nagy bolygó elhelyezése
        planet_id = 1000
        # A Planet class inicializálja a Panda3D gömb modellt.
        planet = Planet(self, planet_id, name="Nexus Bolygó")
        planet.set_pos(1000, 1000, 0)
        self.remote_ships[planet_id] = planet
        
        # Különböző entitások generálása
        for i in range(10):
            entity_id = 200 + i
            
            e_type_name = random.choice(list(ENTITY_CLASSES.keys()))
            EntityClass = ENTITY_CLASSES[e_type_name]
            
            e_name = f"{e_type_name}-{i+1}"
            
            # Entitás inicializálása a megfelelő osztállyal.
            if EntityClass == Ship:
                entity = EntityClass(self, entity_id, is_local=False, name=e_name, ship_type="Drón")
            else:
                entity = EntityClass(self, entity_id, name=e_name)

            # Véletlenszerű pozíció
            x = random.uniform(-500, 500)
            y = random.uniform(-500, 500)
            z = random.uniform(-50, 50)
            entity.set_pos(x, y, z)
            
            self.remote_ships[entity_id] = entity
            print(f"[SYSTEM] Entitás létrehozva: {e_name} ({e_type_name}) @ {x:.1f}, {y:.1f}")

    def join_game(self):
        """Csatlakozás kliensként"""
        ip = self.menu.ip_entry.get()
        if self.client.connect(ip):
            self.my_id = 100 + int(Task.TaskManager.globalClock.getRealTime() * 10)
            self.start_gameplay()

    def start_gameplay(self):
        self.menu.hide()
        
        # Saját hajó létrehozása
        self.local_ship = Ship(self, self.my_id, is_local=True, name="Hős", ship_type="Vezérhajó")
        self.local_ship.set_pos(0, 0, 0) # 0,0,0 az űr közepe
        
        # --- ÚJ: Felszerelés inicializálása az adatbázisból ---
        if self.item_db:
            # Példa: Adunk a hajónak egy alap Core-t és System-et (ID alapján)
            starter_core = self.item_db.get_core(1)
            if starter_core:
                self.local_ship.equip_core(starter_core)
            
            # Szinkronizáljuk a felszerelésünket a többiekkel
            self.sync_my_equipment()

        # Kamera a hajóra (a Ship osztályban van a kamera pivot)
        self.camera.reparentTo(self.local_ship.model)
        self.camera.setPos(0, -30, 10)
        self.camera.lookAt(self.local_ship.model)

        # Loopok
        taskMgr.add(self.update_loop, "GameUpdateLoop")

    def sync_my_equipment(self):
        """Saját felszerelés elküldése a hálózaton"""
        if not self.local_ship: return
        
        # Core küldése
        if self.local_ship.core:
            from direct.distributed.PyDatagram import PyDatagram
            dg = PyDatagram()
            dg.addUint8(MSG_SYNC_CORE)
            dg.addUint16(self.my_id)
            self.local_ship.core.pack(dg)
            self.client.send(dg)
            
    def update_remote_equipment(self, sender_id, type_name, equipment_obj):
        """Távoli hajó felszerelésének frissítése (Hálózatról érkezik)"""
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
        """HUD hívja meg: Beállítja az aktív célpontot a hajónak"""
        if self.local_ship and entity_id in self.remote_ships:
            target = self.remote_ships[entity_id]
            self.local_ship.target_entity = target
            print(f"[GAME] Célpont befogva: {target.name}")

    def set_autopilot(self, entity_id, mode):
        """Utasítás a hajónak (HUD-ról jön)"""
        if entity_id in self.remote_ships:
            target_entity = self.remote_ships[entity_id]
            # Csak a Ship objektumok tudnak robotpilótát futtatni
            if isinstance(target_entity, Ship) or target_entity.entity_type in ["Aszteroida", "Roncs", "Csillagkapu", "Bolygó"]:
                print(f"Robotpilóta: {mode} -> {target_entity.name}")
                self.local_ship.target_entity = target_entity
                self.local_ship.autopilot_mode = mode

    def update_loop(self, task):
        dt = globalClock.getDt()
        
        if self.local_ship:
            self.local_ship.update(dt)
            
            # Frissítjük az összes entitást
            for entity in self.remote_ships.values():
                entity.update(dt)
            
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
            new_ship = Ship(self, sender_id, is_local=False, name=f"Ellenség-{sender_id}", ship_type="Drón")
            self.remote_ships[sender_id] = new_ship
        
        self.remote_ships[sender_id].set_pos(x, y, z)
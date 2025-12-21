import random
import math
from panda3d.core import NodePath, Vec3

# Az eredeti entitásokat használjuk, prefix nélkül
from entities.celestial import Asteroid, Planet, Stargate

class SolarSystem:
    """
    Egy naprendszer, ami csak akkor renderelődik, ha van benne játékos.
    """
    def __init__(self, system_id, galaxy_root, manager):
        self.id = system_id
        self.galaxy_root = galaxy_root
        self.manager = manager
        
        # A rendszer saját gyökér csomópontja
        self.root = NodePath(f"System_Node_{system_id}")
        
        self.entities = []
        self.stargates = {}  # KIJAVÍTVA: Szótár a több kapu tárolásához
        
        self.is_loaded = False
        self.player_count = 0

        # Adatok generálása
        self._generate_content()

    def _generate_content(self):
        # 1. Központi égitest
        p_id = f"sys_{self.id}_planet"
        planet = Planet(self.manager, p_id, name=f"Star_{self.id}")
        planet.root.reparentTo(self.root)
        if hasattr(planet, 'model') and planet.model:
            planet.model.setColor(1, 0.8, 0.1, 1) 
        self.entities.append(planet)

        # 2. Aszteroidák
        for i in range(random.randint(20, 50)):
            a_id = f"sys_{self.id}_ast_{i}"
            ast = Asteroid(self.manager, a_id)
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(60, 180)
            pos = Vec3(math.cos(angle) * dist, math.sin(angle) * dist, random.uniform(-10, 10))
            ast.root.reparentTo(self.root)
            ast.root.setPos(pos)
            self.entities.append(ast)

        # MEGJEGYZÉS: A stargate-eket most már a Galaxy osztály hozza létre dinamikusan a szomszédok alapján!

    def player_entered(self):
        self.player_count += 1
        if not self.is_loaded:
            self.load()

    def player_left(self):
        self.player_count -= 1
        if self.player_count <= 0:
            self.player_count = 0
            self.unload()

    def load(self):
        if not self.is_loaded:
            self.root.reparentTo(self.galaxy_root)
            self.is_loaded = True
            print(f"[Galaxy] Rendszer {self.id} betöltve.")

    def unload(self):
        if self.is_loaded:
            self.root.detachNode()
            self.is_loaded = False
            print(f"[Galaxy] Rendszer {self.id} alvó állapotba került.")

class Galaxy:
    def __init__(self, render_node, manager):
        self.render_node = render_node
        self.manager = manager
        self.systems = {}
        self.current_system_id = None
        self.adj_list = {} # Gráf struktúra
        
        num_systems = 20 # Példa: 20 rendszer
        for i in range(num_systems):
            self.systems[i] = SolarSystem(i, self.render_node, self.manager)
            self.adj_list[i] = []

        # Gráf építése (véletlenszerű összekötés)
        for i in range(num_systems):
            num_conns = random.randint(1, 3)
            while len(self.adj_list[i]) < num_conns:
                target = random.randint(0, num_systems - 1)
                if target != i and target not in self.adj_list[i]:
                    self.adj_list[i].append(target)
                    self.adj_list[target].append(i)

        # Kapuk létrehozása a rendszerekben a szomszédok alapján
        for sys_id, neighbors in self.adj_list.items():
            system = self.systems[sys_id]
            for idx, neighbor_id in enumerate(neighbors):
                angle = (math.pi * 2 / len(neighbors)) * idx
                dist = 300
                pos = Vec3(math.cos(angle) * dist, math.sin(angle) * dist, 0)
                
                g_id = f"sys_{sys_id}_to_{neighbor_id}"
                gate = Stargate(self.manager, g_id)
                gate.root.reparentTo(system.root)
                gate.root.setPos(pos)
                gate.destination_system_id = neighbor_id
                
                system.entities.append(gate)
                system.stargates[neighbor_id] = gate # Ez most már működni fog!

    def warp_player(self, player_node, target_id):
        old_id = self.current_system_id
        if target_id not in self.systems: 
            return

        if old_id is not None:
            self.systems[old_id].player_left()

        new_sys = self.systems[target_id]
        new_sys.player_entered()
        self.current_system_id = target_id

        # Érkezési pozíció keresése a megfelelő kapunál
        arrival_pos = Vec3(50, 50, 0)
        if old_id in new_sys.stargates:
            arrival_pos = new_sys.stargates[old_id].root.getPos()

        player_node.setPos(arrival_pos + Vec3(20, 20, 0))
        print(f"[Galaxy] Ugrás sikeres: {target_id}. rendszer.")

    def warp_random(self, player_node):
        # Most már csak a szomszédos rendszerekbe ugrunk véletlenszerűen
        neighbors = self.adj_list.get(self.current_system_id, [])
        if neighbors:
            target = random.choice(neighbors)
            self.warp_player(player_node, target)
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
        self.stargate = None
        
        self.is_loaded = False
        self.player_count = 0

        # Adatok generálása (a modellek csak load()-nál jönnek létre/csatolódnak)
        self._generate_content()

    def _generate_content(self):
        # 1. Központi égitest
        p_id = f"sys_{self.id}_planet"
        planet = Planet(self.manager, p_id, name=f"Star_{self.id}")
        planet.root.reparentTo(self.root)
        if hasattr(planet, 'model') and planet.model:
            planet.model.setColor(1, 0.8, 0.1, 1) # Csillag szín
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

        # 3. Stargate (Csillagkapu)
        g_id = f"sys_{self.id}_gate"
        self.stargate = Stargate(self.manager, g_id)
        self.stargate.root.reparentTo(self.root)
        self.stargate.root.setPos(250, 0, 0)
        self.entities.append(self.stargate)

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
        """Optimalizáció: Csak ekkor kerül be a renderelési fába."""
        if not self.is_loaded:
            self.root.reparentTo(self.galaxy_root)
            self.is_loaded = True
            print(f"[Galaxy] Rendszer {self.id} betöltve.")

    def unload(self):
        """Optimalizáció: Kikerül a renderelésből, ha üres."""
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
        
        # 5 rendszer generálása
        for i in range(100):
            self.systems[i] = SolarSystem(i, self.render_node, self.manager)
            
        # Kapuk összekötése
        ids = list(self.systems.keys())
        for i in range(len(ids)):
            curr = self.systems[ids[i]]
            next_id = ids[(i + 1) % len(ids)]
            curr.stargate.destination_system_id = next_id

    def warp_player(self, player_node, target_id):
        if target_id not in self.systems: 
            return

        if self.current_system_id is not None:
            self.systems[self.current_system_id].player_left()

        new_sys = self.systems[target_id]
        new_sys.player_entered()
        self.current_system_id = target_id

        # Pozicionálás a kapuhoz
        gate_pos = new_sys.stargate.root.getPos()
        player_node.setPos(gate_pos + Vec3(30, 30, 0))
        print(f"[Galaxy] Ugrás sikeres: {target_id}. rendszer.")

    def warp_random(self, player_node):
        available = [sid for sid in self.systems.keys() if sid != self.current_system_id]
        if available:
            target = random.choice(available)
            self.warp_player(player_node, target)
from panda3d.core import NodePath, Vec3, CollisionNode, CollisionSphere, CollisionBox, BitMask32
import random
import math
from entities.entity import Entity
from utils.geometry_utils import AsteroidGenerator

class CelestialBody(Entity):
    """Alaposztály az égitesteknek (bolygó, kapu, roncs)."""
    def __init__(self, manager, entity_id, name, entity_type="Celestial", max_hp=1000):
        super().__init__(manager, entity_id, name, entity_type)
        self.max_hull = max_hp
        self.current_hull = max_hp
        self.load_model()

    def load_model(self):
        pass

    def take_damage(self, amount):
        """Sebzéskezelés: ha elfogy a HP, meghal."""
        self.current_hull -= amount
        print(f"[ENTITY] {self.name} HP: {self.current_hull}/{self.max_hull}")
        if self.current_hull <= 0:
            self.die()

    def die(self):
        """Alapértelmezett megsemmisülés: törlés a világból."""
        print(f"[ENTITY] {self.name} megsemmisült.")
        self.destroy()

class Asteroid(CelestialBody):
    def __init__(self, manager, entity_id, name="Asteroid", scale=None, asteroid_type="iron"):
        # Beállítjuk a HP-t (pl. 50 HP alapból, scale-el szorozva)
        s = scale if scale else random.uniform(2.0, 5.0)
        hp = 50 * s
        super().__init__(manager, entity_id, name, "Asteroid", max_hp=hp)
        
        self.asteroid_type = asteroid_type
        self.root.setScale(s)

        # 1. Mesh generálása (Nincs vertex deformáció, marad az eredeti forma)
        mesh_node = AsteroidGenerator.generate_asteroid_mesh()
        self.geom_node_path = self.root.attachNewNode(mesh_node)
        
        # Textúra alkalmazása
        try:
            tex = loader.loadTexture("assets/textures/asteroid_diffuse.png")
            self.geom_node_path.setTexture(tex, 1)
        except:
            print(f"[Warning] Asteroid textúra nem található.")

        # 2. Collision (Lövések detektálásához)
        c_node = CollisionNode(f"col_{self.id}")
        c_node.addSolid(CollisionSphere(0, 0, 0, 1.1))
        # Beállítjuk, hogy a lövedékek eltalálhassák (pl. bit 1)
        c_node.setIntoCollideMask(BitMask32.bit(1))
        self.col_np = self.root.attachNewNode(c_node)
        # Fontos: a PythonTag-be magát az objektumot tesszük, hogy a combat system elérje
        self.col_np.setPythonTag("entity", self)

    def die(self):
        """Amikor szétlövik az aszteroidát, zöld kockákat dob."""
        pos = self.root.getPos()
        drop_count = random.randint(2, 4)
        
        print(f"[GAME] Aszteroida szétrobbant! Dropok generálása...")
        
        for _ in range(drop_count):
            # Véletlenszerű szórás a dropoknak
            offset = Vec3(random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2))
            # Új Debris (Loot) entitás létrehozása a manager segítségével
            drop_id = f"drop_{self.id}_{random.randint(0,999)}"
            self.manager.add_entity(Debris(self.manager, drop_id, self.asteroid_type, pos + offset))
            
        self.destroy() # Eltávolítja az aszteroidát a játékból

class Debris(Entity):
    """Zöld kocka formájú loot, amit az aszteroida dob."""
    def __init__(self, manager, entity_id, resource_type, position):
        super().__init__(manager, entity_id, f"Loot_{resource_type}", entity_type="Loot")
        
        self.root.setPos(position)
        self.resource_type = resource_type
        
        # 1. Vizuális rész: Zöld kocka
        try:
            model = loader.loadModel("models/box")
            model.reparentTo(self.root)
            self.root.setScale(0.3)
            self.root.setColor(0, 1, 0, 1) # ZÖLD SZÍN
        except:
            print("Hiba: models/box nem található")

        # 2. Collision Detector (Trigger a játékosnak)
        c_node = CollisionNode(f"col_loot_{self.id}")
        # CollisionBox a kocka alakhoz
        c_node.addSolid(CollisionBox(Vec3(-1,-1,-1), Vec3(1,1,1)))
        # Külön maszk a loot felszedéséhez (pl. bit 2)
        c_node.setIntoCollideMask(BitMask32.bit(2))
        self.col_np = self.root.attachNewNode(c_node)
        self.col_np.setPythonTag("entity", self)
        self.col_np.setPythonTag("item_data", {"type": resource_type, "amount": 10})
        
        # Animáció: Forgás
        self.root.hprInterval(3, Vec3(360, 360, 0)).loop()

# További osztályok (Planet, Stargate, Wreck) változatlanok maradnak, 
# de most már tudnak sebezhetőek lenni a CelestialBody-n keresztül.

class Planet(CelestialBody):
    def __init__(self, manager, entity_id, name="Planet"):
        super().__init__(manager, entity_id, name, "Planet", max_hp=10000)

    def load_model(self):
        self.model = loader.loadModel("models/misc/sphere")
        self.model.reparentTo(self.root)
        self.model.setScale(30)
        self.model.setColor(0.1, 0.4, 0.8, 1)

class Stargate(CelestialBody):
    def __init__(self, manager, entity_id, name="Gate"):
        super().__init__(manager, entity_id, name, "Stargate", max_hp=5000)

    def load_model(self):
        self.model = loader.loadModel("models/misc/sphere")
        self.model.reparentTo(self.root)
        self.model.setScale(15, 1, 15)
        self.model.setColor(0.5, 0.5, 1, 0.4)

class Wreck(CelestialBody):
    """Hajóroncs, amiből alkatrészeket (scrap) lehet kinyerni."""
    def __init__(self, manager, entity_id, name="Wreck"):
        # A roncsnak fixen 200 HP-t adunk (vagy amennyit szeretnél)
        super().__init__(manager, entity_id, name, "Wreck", max_hp=200)

    def load_model(self):
        # Alapmodell betöltése
        self.model = loader.loadModel("models/box")
        if self.model:
            self.model.reparentTo(self.root)
            self.model.setScale(3, 5, 2)
            self.model.setColor(0.2, 0.2, 0.2, 1) # Sötétszürke szín

        # Ütköző a roncshoz
        c_node = CollisionNode(f"col_{self.id}")
        c_node.addSolid(CollisionBox(Vec3(-1,-1,-1), Vec3(1,1,1)))
        c_node.setIntoCollideMask(BitMask32.bit(1))
        self.col_np = self.root.attachNewNode(c_node)
        self.col_np.setPythonTag("entity", self)

    def die(self):
        """Ha a roncs HP-ja elfogy, 'scrap' (hulladék) dropokat hagy maga után."""
        print(f"[GAME] Roncs teljesen szétesett!")
        pos = self.root.getPos()
        # A roncs több dropot adhat
        for _ in range(random.randint(3, 6)):
            offset = Vec3(random.uniform(-3, 3), random.uniform(-3, 3), random.uniform(-3, 3))
            drop_id = f"scrap_{self.id}_{random.randint(0,999)}"
            self.manager.add_entity(Debris(self.manager, drop_id, "scrap", pos + offset))
        self.destroy()
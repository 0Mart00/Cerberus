from entities.entity import Entity
from utils.geometry_utils import AsteroidGenerator
from panda3d.core import CollisionNode, CollisionSphere, BitMask32
import random

class CelestialBody(Entity):
    """Base class for non-ship objects in space."""
    def __init__(self, manager, entity_id, name, entity_type="Celestial", max_hp=1000):
        super().__init__(manager, entity_id, name, entity_type)
        self.max_hull = max_hp
        self.current_hull = max_hp
        self.load_model()

    def load_model(self):
        pass

# Cerberus/entities/celestial.py


class Asteroid(Entity):
    def __init__(self, manager, entity_id, name="Asteroid", scale=None):
        super().__init__(manager, entity_id, name, entity_type="Asteroid")
        
        # Generálunk egy egyedi hálót
        mesh_node = AsteroidGenerator.generate_asteroid_mesh()
        self.geom_node_path = self.root.attachNewNode(mesh_node)
        
        # Véletlenszerű méret ha nincs megadva
        s = scale if scale else random.uniform(2.0, 5.0)
        self.root.setScale(s)
        
        # Ütközés a lézernek és a vonósugárnak
        c_node = CollisionNode(f"col_{self.id}")
        c_node.addSolid(CollisionSphere(0, 0, 0, 1.1)) # Kicsit nagyobb mint a mesh
        c_node.setIntoCollideMask(BitMask32.bit(1))    # PICKABLE maszk
        self.col_np = self.root.attachNewNode(c_node)
        self.col_np.setPythonTag("entity", self)

    def drill(self, local_impact_point):
        """Meghívja a háló deformációt."""
        AsteroidGenerator.deform_asteroid(
            self.geom_node_path.node(), 
            local_impact_point, 
            radius=0.5, 
            strength=0.2
        )

class Debris(Entity):
    """Bányászatkor keletkező törmelék (Loot)."""
    def __init__(self, manager, entity_id, name="Debris"):
        super().__init__(manager, entity_id, name, entity_type="Loot")
        # Egyszerű kocka vagy gömb lootnak
        model = loader.loadModel("models/box")
        model.reparentTo(self.root)
        self.root.setScale(0.2)
        self.root.setColor(0.8, 0.8, 0.2, 1) # Aranyos szín
        
        c_node = CollisionNode(f"col_{self.id}")
        c_node.addSolid(CollisionSphere(0, 0, 0, 1.0))
        c_node.setIntoCollideMask(BitMask32.bit(2)) # LOOT maszk
        self.col_np = self.root.attachNewNode(c_node)
        self.col_np.setPythonTag("entity", self)

class Planet(CelestialBody):
    def __init__(self, manager, entity_id, name="Planet"):
        super().__init__(manager, entity_id, name, "Planet", max_hp=10000)

    def load_model(self):
        if self.app:
            self.model = self.app.loader.loadModel("models/misc/sphere")
            if self.model:
                self.model.reparentTo(self.root)
                self.model.setScale(30)
                self.model.setColor(0.1, 0.4, 0.8, 1)

class Wreck(CelestialBody):
    def __init__(self, manager, entity_id, name="Wreck"):
        super().__init__(manager, entity_id, name, "Wreck", max_hp=200)

    def load_model(self):
        if self.app:
            self.model = self.app.loader.loadModel("models/box")
            if self.model:
                self.model.reparentTo(self.root)
                self.model.setScale(3, 5, 2)
                self.model.setColor(0.2, 0.2, 0.2, 1)

class Stargate(CelestialBody):
    def __init__(self, manager, entity_id, name="Gate"):
        super().__init__(manager, entity_id, name, "Stargate", max_hp=5000)

    def load_model(self):
        if self.app:
            self.model = self.app.loader.loadModel("models/misc/sphere")
            if self.model:
                self.model.reparentTo(self.root)
                self.model.setScale(15, 1, 15)
                self.model.setColor(0.5, 0.5, 1, 0.4)
from .entity import Entity
import random

# ==============================================================================
# CELESTIAL BODIES (Aszteroidák, Bolygók, stb.)
# ==============================================================================

class Asteroid(Entity):
    def __init__(self, manager, entity_id, name="Aszteroida"):
        super().__init__(manager, entity_id, name, "Aszteroida")
        scale = random.uniform(2.0, 5.0)
        self.load_model("models/box", scale=scale, color=(0.4, 0.4, 0.4, 1))
        self.model.setHpr(random.uniform(0, 360), random.uniform(0, 360), 0)

class Planet(Entity):
    def __init__(self, manager, entity_id, name="Bolygó"):
        super().__init__(manager, entity_id, name, "Bolygó")
        self.load_model("models/box", scale=100.0, color=(0.1, 0.3, 0.8, 1))

class Wreck(Entity):
    def __init__(self, manager, entity_id, name="Roncs"):
        super().__init__(manager, entity_id, name, "Roncs")
        self.load_model("models/box", scale=2.5, color=(0.3, 0.2, 0.1, 1))
        self.model.setHpr(random.uniform(0, 360), random.uniform(0, 360), 0)

class Stargate(Entity):
    def __init__(self, manager, entity_id, name="Csillagkapu"):
        super().__init__(manager, entity_id, name, "Csillagkapu")
        self.load_model("models/box", scale=1.0, color=(0.8, 0.8, 1.0, 1))
        self.model.setScale(10, 1, 10) # Kapu alak
        self.model.setR(90) # Felállítva
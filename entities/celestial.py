from .entity import Entity
from panda3d.core import BitMask32
import random
# Importáljuk az új generátorokat
from systems.generation import PlanetGenerator, AsteroidGenerator

# ==============================================================================
# CELESTIAL BODIES (Aszteroidák, Bolygók, stb.)
# ==============================================================================

class Asteroid(Entity):
    def __init__(self, manager, entity_id, name="Aszteroida"):
        super().__init__(manager, entity_id, name, "Aszteroida")
        # JAVÍTÁS: Kompatibilitás a HUD-dal, ami ship_type-ot vár
        self.ship_type = self.entity_type
        
        # Generátor használata a procedurális modell létrehozásához
        generator = AsteroidGenerator()
        self.model = generator.generate()
        self.model.reparentTo(render)
        self.model.setHpr(random.uniform(0, 360), random.uniform(0, 360), 0)
        
        # BEÁLLÍTÁS: Ütközés maszk a bányász lézernek
        self.model.setCollideMask(BitMask32.bit(1))
        
        self.pits = [] 

    def apply_mining_damage(self, hit_pos):
        """Vizsgálja és alkalmazza a bányászat vizuális hatását."""
        generator = AsteroidGenerator()
        if generator.apply_mining_hit(self.model, hit_pos):
            return True
        return False

class Planet(Entity):
    def __init__(self, manager, entity_id, name="Bolygó"):
        super().__init__(manager, entity_id, name, "Bolygó")
        # JAVÍTÁS: Kompatibilitás a HUD-dal, ami ship_type-ot vár
        self.ship_type = self.entity_type
        
        # Generátor használata a procedurális modell létrehozásához
        generator = PlanetGenerator()
        self.model = generator.generate(name=name, radius=100.0, base_color=(random.uniform(0.1, 1), random.uniform(0.1, 1), random.uniform(0.1, 1), 1))
        self.model.reparentTo(render)
        
        # Nincs bányászat/ütközés a bolygóval
        self.model.setCollideMask(BitMask32.allOff())

class Wreck(Entity):
    def __init__(self, manager, entity_id, name="Roncs"):
        super().__init__(manager, entity_id, name, "Roncs")
        # JAVÍTÁS: Kompatibilitás a HUD-dal, ami ship_type-ot vár
        self.ship_type = self.entity_type
        
        # load_model használata, ami fallback-el a procedurális dobozra
        self.load_model("models/box", scale=2.5, color=(0.3, 0.2, 0.1, 1))
        self.model.setHpr(random.uniform(0, 360), random.uniform(0, 360), 0)
        self.model.setCollideMask(BitMask32.allOff())

class Stargate(Entity):
    def __init__(self, manager, entity_id, name="Csillagkapu"):
        super().__init__(manager, entity_id, name, "Csillagkapu")
        # JAVÍTÁS: Kompatibilitás a HUD-dal, ami ship_type-ot vár
        self.ship_type = self.entity_type

        # load_model használata, ami fallback-el a procedurális dobozra
        self.load_model("models/box", scale=1.0, color=(0.8, 0.8, 1.0, 1))
        self.model.setScale(10, 1, 10) 
        self.model.setR(90)
        self.model.setCollideMask(BitMask32.allOff())
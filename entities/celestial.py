from .entity import Entity
from panda3d.core import BitMask32, Vec4
import random
# Import Generator classes (ezek felelnek a procedurális modellek létrehozásáért)
from systems.generation import PlanetGenerator, AsteroidGenerator

# ==============================================================================
# CELESTIAL ALAPOSZTÁLY
# ==============================================================================
class Celestial(Entity):
    """
    Base class for all celestial and static objects (Asteroids, Planets, Stargates).
    """
    def __init__(self, manager, entity_id, name, entity_type, max_hp=1000):
        # A Celestial nem használja a model_path-t, mivel procedurálisan generálódik
        super().__init__(manager, entity_id, name, entity_type)
        self.ship_type = entity_type  # Compatibility with the old HUD/Target system
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.generator = None # Generator instance if applicable

    def update(self, dt):
        # Static celestials usually don't need complex updates
        pass

# ==============================================================================
# CELESTIAL BODIES (Asteroids, Planets, etc.)
# ==============================================================================

class Asteroid(Celestial):
    def __init__(self, manager, entity_id, name="Asteroid", max_hp=500):
        super().__init__(manager, entity_id, name, "Asteroid", max_hp=max_hp)
        
        # Generator usage for procedural model creation
        self.generator = AsteroidGenerator()
        self.model = self.generator.generate(name=name)
        self.model.reparentTo(render)
        self.model.setHpr(random.uniform(0, 360), random.uniform(0, 360), 0)
        
        # SETUP: Collision mask for mining laser
        self.model.setCollideMask(BitMask32.bit(1))
        
        self.pits = [] 

    def apply_mining_damage(self, hit_pos):
        """Applies visual effect of mining."""
        if self.generator.apply_mining_hit(self.model, hit_pos):
            return True
        return False

class Planet(Celestial):
    def __init__(self, manager, entity_id, name="Planet", max_hp=999999):
        super().__init__(manager, entity_id, name, "Planet", max_hp=max_hp)
        
        # Generator usage for procedural model creation
        self.generator = PlanetGenerator()
        self.model = self.generator.generate(name=name, radius=100.0, 
                                           base_color=(random.uniform(0.1, 1), random.uniform(0.1, 1), random.uniform(0.1, 1), 1))
        self.model.reparentTo(render)
        
        # No mining/collision for planet
        self.model.setCollideMask(BitMask32.allOff())

class Wreck(Celestial):
    def __init__(self, manager, entity_id, name="Wreck", max_hp=100):
        super().__init__(manager, entity_id, name, "Wreck", max_hp=max_hp)
        
        # Use procedural box fallback for wreck
        self.model = AsteroidGenerator().generate(name=name, min_scale=2.5, max_scale=2.5) 
        self.model.reparentTo(render)
        self.model.setColor(0.3, 0.2, 0.1, 1)
        self.model.setHpr(random.uniform(0, 360), random.uniform(0, 360), 0)
        self.model.setCollideMask(BitMask32.allOff())

class Stargate(Celestial):
    def __init__(self, manager, entity_id, name="Stargate", max_hp=5000):
        super().__init__(manager, entity_id, name, "Stargate", max_hp=max_hp)

        # Use procedural box fallback for stargate
        self.model = AsteroidGenerator().generate(name=name, min_scale=1.0, max_scale=1.0)
        self.model.reparentTo(render)
        self.model.setColor(0.8, 0.8, 1.0, 1)
        self.model.setScale(10, 1, 10) 
        self.model.setR(90)
        self.model.setCollideMask(BitMask32.allOff())
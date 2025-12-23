# Cerberus/systems/generation.py

import random
import math
from panda3d.core import Vec3
from random import uniform
import Cerberus.globals as g

# Dinamikus importok az entitasokhoz a korkoros hivatkozasok elkerulesere a fuggvenyekben
# De a top-level importokat is megtartjuk, ha szukseges
from Cerberus.utils.geometry_utils import AsteroidGenerator, PlanetGenerator

class GenerationSystem:
    def __init__(self, game):
        self.game = game
        self.celestial_counter = 0

    def generate_solar_system(self):
        """
        Generál egy aszteroida mezőt és egy játékos hajót.
        """
        print("[GENERATION] Mező létrehozása...")
        
        # 1. Aszteroidák (Asteroids3.py stílusban)
        for i in range(15):
            pos = Vec3(random.uniform(-50, 50), random.uniform(20, 100), random.uniform(-10, 10))
            ast = Asteroid(self.game, f"AST_{i}", name=f"Roid-{i}")
            ast.set_pos(pos)
            # Automatikusan bekerül a g.ENTITIES-be az Entity __init__ miatt

        print(f"[GENERATION] Kész. Entitások: {len(g.ENTITIES)}")

    def spawn_debris(self, position):
        """Létrehoz egy darab lootot a megadott helyen."""
        from Cerberus.entities.celestial import Debris
        d = Debris(self.game, f"LOOT_{random.randint(0,9999)}")
        d.set_pos(position)
        return d
        
    def get_celestial_class(self, entity_type):
        """Dinamikus import az entitás osztályokhoz."""
        try:
            from Cerberus.entities.celestial import Asteroid, Wreck, Stargate, Planet
            class_map = {
                "Asteroid": Asteroid,
                "Wreck": Wreck,
                "Stargate": Stargate,
                "Planet": Planet
            }
            return class_map.get(entity_type)
        except ImportError as e:
            print(f"[ERROR] Nem sikerült importálni az entitás osztályokat: {e}")
            return None

    def generate_celestial(self, entity_type, position, scale=None, color=None):
        """Létrehoz egy égi objektumot és regisztrálja a rendszerben."""
        CelestialClass = self.get_celestial_class(entity_type)
        if CelestialClass is None:
            return None
            
        uid = f"CELESTIAL_{self.celestial_counter}"
        self.celestial_counter += 1
        
        # Objektum példányosítása - Az Entity alaposztaly regisztralja magat a g.ENTITIES-be
        celestial = CelestialClass(
            self.game,
            uid,
            name=f"{entity_type}_{self.celestial_counter}"
        )
        
        celestial.set_pos(position.x, position.y, position.z)
        
        # Modell meretezes ha szukseges (ha az entitas root-ja alatt van a modell)
        if scale and celestial.root:
            celestial.root.setScale(scale)
            
        return celestial

    def generate_solar_system(self):
        """Egy teszt naprendszer felépítése."""
        print("[GENERATION] Naprendszer generálása...")
        
        # Stargate elhelyezése
        self.generate_celestial("Stargate", Vec3(5000, 0, 0))

        # Aszteroida mező generálása
        for i in range(20):
            pos = Vec3(uniform(-10000, 10000), uniform(-10000, 10000), uniform(-1000, 1000))
            self.generate_celestial("Asteroid", pos)
        
        print(f"[GENERATION] {self.celestial_counter} objektum legenerálva.")


class GalaxyManager:
    """
    Manages the procedural or static generation of star systems, 
    celestial bodies, and static entities in the game world.
    """
    def __init__(self, base):
        self.base = base
        self.systems = {}

    def generate_test_system(self):
        """
        Generates a basic test environment.
        """
        print("[GALAXY] Teszt rendszer generálása...")
        if hasattr(self.base, 'spawn_test_entities'):
            self.base.spawn_test_entities()
        else:
            self._manual_spawn()

    def _manual_spawn(self):
        """Fallback spawning logic if not handled by game core."""
        from Cerberus.entities.celestial import Planet, Asteroid
        
        # Central Planet
        p = Planet(self.base, "PLANET_MAIN", "Nexus Prime")
        p.set_pos(1000, 1000, 0)
        # Itt a base.remote_ships-et is hasznalhatod, de az Entity __init__ mar betette a g.ENTITIES-be!
        if hasattr(self.base, 'remote_ships'):
            self.base.remote_ships["PLANET_MAIN"] = p
        
        # Some Asteroids
        for i in range(50):
            a_id = f"AST_{i}"
            a = Asteroid(self.base, a_id, f"Aszteroida-{i}")
            a.set_pos(random.uniform(-500, 500), random.uniform(200, 800), random.uniform(-20, 20))
            if hasattr(self.base, 'remote_ships'):
                self.base.remote_ships[a_id] = a
        

    def clear_system(self):
        """Removes all generated entities from the current system."""
        # Itt mar a g.ENTITIES-t is urithetjuk
        entity_ids = list(g.ENTITIES.keys())
        for eid in entity_ids:
            g.ENTITIES[eid].destroy()
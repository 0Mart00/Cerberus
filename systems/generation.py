from panda3d.core import Vec3
from random import uniform
# Feltételezve, hogy a globals létezik
from utils.geometry_utils import AsteroidGenerator, PlanetGenerator

try:
    from globals import ENTITIES
except ImportError:
    ENTITIES = {}

class GenerationSystem:
    def __init__(self, game):
        self.game = game
        self.celestial_counter = 0

    def get_celestial_class(self, entity_type):
        """Dinamikus import az entitás osztályokhoz a körkörös hivatkozás elkerülésére."""
        # Itt importáljuk az entitásokat, amikor szükség van rájuk
        try:
            from entities.celestial import Asteroid, Wreck, Stargate, Planet
            class_map = {
                "Asteroid": Asteroid,
                "Wreck": Wreck,
                "Stargate": Stargate,
                "Planet": Planet
            }
            return class_map.get(entity_type)
        except ImportError:
            print(f"[ERROR] Nem sikerült importálni az entitás osztályokat.")
            return None

    def generate_celestial(self, entity_type, position, scale=None, color=None):
        """Létrehoz egy égi objektumot és regisztrálja a rendszerben."""
        CelestialClass = self.get_celestial_class(entity_type)
        if CelestialClass is None:
            return None
            
        uid = f"CELESTIAL_{self.celestial_counter}"
        self.celestial_counter += 1
        
        # Objektum példányosítása
        celestial = CelestialClass(
            self.game,
            uid,
            name=f"{entity_type}_{self.celestial_counter}"
        )
        
        celestial.set_pos(position.x, position.y, position.z)
        if scale:
            celestial.model.setScale(scale) # Ha az entitás rendelkezik model attribútummal
            
        ENTITIES[uid] = celestial
        return celestial

    def generate_solar_system(self):
        """Egy teszt naprendszer felépítése."""
        print("[GENERATION] Naprendszer generálása...")
        
        # Stargate elhelyezése
        self.generate_celestial("Stargate", Vec3(5000, 0, 0))

        # Aszteroida mező generálása
        for i in range(20):
            pos = Vec3(uniform(-1000, 1000), uniform(-1000, 1000), uniform(-100, 100))
            self.generate_celestial("Asteroid", pos)
        
        print(f"[GENERATION] {self.celestial_counter} objektum legenerálva.")
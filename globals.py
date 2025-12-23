# Cerberus/globals.py

# Global settings and state
# Itt taroljuk a jatek allapotat es beallitasait

# Kepernyo beallitasok
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Jatekmenet konstansok
FOV = 70.0
NEAR_PLANE = 0.1
FAR_PLANE = 10000.0
DEBUG = True

# Események
EVENT_SHIP_DAMAGED = "ship-damaged"
EVENT_SHIP_DESTROYED = "ship-destroyed"
EVENT_PLAYER_JOINED = "player-joined"
EVENT_PLAYER_LEFT = "player-left"

# Entitás típusok
TYPE_STAR = "Star"
TYPE_PLANET = "Planet"
TYPE_STATION = "Station"
TYPE_ASTEROID = "Asteroid"

# Ütközési maszkok
MASK_SHIP = 0x1
MASK_PROJECTILE = 0x2
MASK_ENVIRONMENT = 0x4

# Hálózati beállítások
PORT = 9099
MAX_PLAYERS = 8
MAX_RENDER_DISTANCE = 5000.0

# Galaxis generálás
NUM_SYSTEMS = 100
MAX_COORD = 500
NEIGHBOR_COUNT = 3
MAP_SCALE = 0.001
MAP_SIZE = 0.3

# Központi entitás tároló
# Key: Entity ID (UID), Value: Entity object instance
ENTITIES = {}

def log_entity_count():
    """
    Kiírja a konzolra az aktuálisan regisztrált entitások számát.
    """
    print(f"[DEBUG] Aktuális entitások száma (ENTITIES len): {len(ENTITIES)}")

def get_entity_count():
    """
    Visszaadja az entitások számát.
    """
    return len(ENTITIES)
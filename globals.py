# Cerberus/globals.py
from panda3d.core import BitMask32

MASK_WALL = BitMask32.bit(0)
MASK_ASTEROID = BitMask32.bit(1)
MASK_SHIP = BitMask32.bit(2)
MASK_LOOT = BitMask32.bit(3)
MASK_SELECTABLE = MASK_ASTEROID | MASK_SHIP
# Globális listák a rendszerek közötti kommunikációhoz
TARGETABLE_OBJECTS = []  # Minden, amit el lehet találni
LOOT_OBJECTS = []        # Gyűjthető tárgyak listája
ACTIVE_PROJECTILES = []  # Lövedékek (ha lennének)
SELECTED_TARGET = None

LASER_DAMAGE = 1000.0
TRACTOR_SPEED = 40.0
LASER_RANGE = 500.0



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
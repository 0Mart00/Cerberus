import random
import heapq
from panda3d import core as pc
EVENT_SHIP_DAMAGED = "ship-damaged"
EVENT_SHIP_DESTROYED = "ship-destroyed"
EVENT_PLAYER_JOINED = "player-joined"
EVENT_PLAYER_LEFT = "player-left"

# Celestial Types
TYPE_STAR = "Star"
TYPE_PLANET = "Planet"
TYPE_STATION = "Station"
TYPE_ASTEROID = "Asteroid"

MASK_SHIP = 0x1
MASK_PROJECTILE = 0x2
MASK_ENVIRONMENT = 0x4
# --- Globális Entitás Tároló (Eredeti) ---
ENTITIES = {}

# --- Hálózati Konstansok (Eredeti) ---
PORT = 9099
MAX_RENDER_DISTANCE = 5000.0
MAX_PLAYERS = 8

# --- Játékos/Állapot Hivatkozások (Eredeti) ---
LOCAL_SHIP = None 
IS_HOST = False   

# --- GALAXIS KONSTANSOK ---
NUM_SYSTEMS = 100
MAX_COORD = 500
NEIGHBOR_COUNT = 3
MAP_SCALE = 0.001
MAP_SIZE = 0.3

# --- NAVIGÁCIÓS ÉS ZÓNA ADATOK (ÚJ) ---
# Itt tároljuk az összes generált csillagrendszer adatát (név, pozíció, szín)
SYSTEMS_DATA = []

# Szomszédsági lista: Meghatározza, melyik zónából hova lehet ugrani
# Formátum: { rendszer_id: [(szomszéd_id, távolság), ...] }
ADJACENCY_LIST = {}

# Aktuális helyzet: A rendszer indexe, ahol a játékos éppen tartózkodik
CURRENT_SYSTEM_INDEX = 0

# Navigációs cél: A kiválasztott célrendszer indexe
TARGET_SYSTEM_INDEX = None

# Aktuális útvonal: Az A* által kiszámított indexek listája a célig
ACTIVE_ROUTE = []

# Az aktuális útvonal összesített költsége (távolsága)
CURRENT_PATH_COST = 0.0

# --- SEGÉDFÜGGVÉNYEK ---
# Network and System Constants

# Event Names

def get_system_pos(index):
    """Visszaadja egy adott rendszer pozícióját."""
    if 0 <= index < len(SYSTEMS_DATA):
        return SYSTEMS_DATA[index]['pos']
    return pc.LVector3(0, 0, 0)

def clear_navigation():
    """Alaphelyzetbe állítja a navigációs terveket."""
    global TARGET_SYSTEM_INDEX, ACTIVE_ROUTE, CURRENT_PATH_COST
    TARGET_SYSTEM_INDEX = None
    ACTIVE_ROUTE = []
    CURRENT_PATH_COST = 0.0
import heapq
from panda3d import core as pc

# ─────────────────────────────────────────────
# GLOBÁLIS KONSTANSOK (STATIKUS)
# ─────────────────────────────────────────────

EVENT_SHIP_DAMAGED = "ship-damaged"
EVENT_SHIP_DESTROYED = "ship-destroyed"
EVENT_PLAYER_JOINED = "player-joined"
EVENT_PLAYER_LEFT = "player-left"

TYPE_STAR = "Star"
TYPE_PLANET = "Planet"
TYPE_STATION = "Station"
TYPE_ASTEROID = "Asteroid"

MASK_SHIP = 0x1
MASK_PROJECTILE = 0x2
MASK_ENVIRONMENT = 0x4

PORT = 9099
MAX_PLAYERS = 8
MAX_RENDER_DISTANCE = 5000.0

NUM_SYSTEMS = 100
MAX_COORD = 500
NEIGHBOR_COUNT = 3
MAP_SCALE = 0.001
MAP_SIZE = 0.3



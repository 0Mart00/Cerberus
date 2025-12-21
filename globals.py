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


# ─────────────────────────────────────────────
# GALAXIS (NEM GLOBÁLIS ÁLLAPOT!)
# ─────────────────────────────────────────────

class Galaxy:
    def __init__(self):
        self.systems = []              # [{id, name, pos, color}]
        self.adjacency = {}            # {id: [(neighbor_id, dist)]}
        self.current_system = 0
        self.target_system = None
        self.active_route = []
        self.current_path_cost = 0.0

    # ───────────────
    # RENDSZEREK
    # ───────────────

    def add_system(self, name, pos, color):
        sid = len(self.systems)
        self.systems.append({
            "id": sid,
            "name": name,
            "pos": pos,
            "color": color
        })
        self.adjacency[sid] = []
        return sid

    def get_system_pos(self, index):
        if 0 <= index < len(self.systems):
            return self.systems[index]["pos"]
        return pc.LVector3(0, 0, 0)

    # ───────────────
    # GRÁF
    # ───────────────

    def connect(self, a, b):
        pa = self.systems[a]["pos"]
        pb = self.systems[b]["pos"]
        d = (pa - pb).length()

        self.adjacency[a].append((b, d))
        self.adjacency[b].append((a, d))

    # ───────────────
    # NAVIGÁCIÓ
    # ───────────────

    def clear_navigation(self):
        self.target_system = None
        self.active_route.clear()
        self.current_path_cost = 0.0

    # ───────────────
    # A*
    # ───────────────

    def heuristic(self, a, b):
        pa = self.systems[a]["pos"]
        pb = self.systems[b]["pos"]
        return (pa - pb).length()

    def find_path(self, start, goal):
        open_set = [(0.0, start)]
        came_from = {}
        g_score = {start: 0.0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct(came_from, current), g_score[current]

            for neighbor, dist in self.adjacency[current]:
                tentative = g_score[current] + dist

                if neighbor not in g_score or tentative < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    f = tentative + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))

        return [], float("inf")

    def _reconstruct(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def navigate_to(self, target):
        self.target_system = target
        self.active_route, self.current_path_cost = self.find_path(
            self.current_system,
            target
        )
        return self.active_route


# ─────────────────────────────────────────────
# GAME STATE (RUNTIME)
# ─────────────────────────────────────────────

class GameState:
    def __init__(self):
        self.entities = {}
        self.local_ship = None
        self.is_host = False
        self.galaxy = Galaxy()

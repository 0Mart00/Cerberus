# Cerberus/globals.py
# Ez a fájl tárolja a fontos globális konstansokat és a központi entitás hivatkozásokat.

# --- Globális Entitás Tároló ---
# Az összes aktív entitás (hajók, aszteroidák, csillagkapuk) gyűjteménye.
# Kulcs: Entitás ID (pl. UID, vagy hálózati ID)
# Érték: Az entitás objektum (pl. Ship, Celestial példányok)
ENTITIES = {}

# --- Hálózati Konstansok (ismétlés a könnyebb eléréshez) ---
PORT = 9099
MAX_RENDER_DISTANCE = 5000.0 # Maximális láthatósági távolság

# --- Játékos/Állapot Hivatkozások (kezdetben None) ---
LOCAL_SHIP = None # Hivatkozás a helyi játékos hajójára
IS_HOST = False   # Jelzi, hogy a játékos a hoszt-e
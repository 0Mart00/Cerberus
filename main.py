import os
import sys
from panda3d.core import loadPrcFile

# Útvonalak beállítása, hogy minden modul elérhető legyen
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from net.ItemDatabase import ItemDatabase
from core.game import CerberusGame

if __name__ == "__main__":
    # 1. Adatbázis inicializálása
    item_db = ItemDatabase()
    json_path = os.path.join(current_dir, 'data', 'items.json')
    
    # 2. Adatok betöltése JSON fájlból
    try:
        if os.path.exists(json_path):
            item_db.load_from_json(json_path)
            print("[RENDSZER] Tárgy adatbázis betöltve.")
        else:
            print(f"[HIBA] Nem található az items.json itt: {json_path}")
    except Exception as e:
        print(f"[HIBA] Adatbázis hiba: {e}")

    # 3. Játék indítása az adatbázis átadásával
    app = CerberusGame(item_db=item_db)
    
    try:
        app.run()
    except Exception as e:
        print(f"Kritikus hiba a futás során: {e}")
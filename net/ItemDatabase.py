import json
import os
# Javított importok: abszolút elérési utat használunk a 'data' mappából
from .Core import ShipCore
from .System import ShipSystem
from .Support import ShipSupport

class ItemDatabase:
    def __init__(self):
        self.cores = {}
        self.systems = {}
        self.supports = {}

    def load_from_json(self, file_path):
        """Betölti az összes tárgyat a megadott JSON fájlból."""
        if not os.path.exists(file_path):
            print(f"[HIBA] Az adatfájl nem található: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                
                # Core-ok betöltése
                for item_data in data.get("cores", []):
                    new_item = ShipCore(**item_data)
                    self.cores[new_item.id] = new_item

                                    
                # System-ek betöltése
                for item_data in data.get("systems", []):
                    new_item = ShipSystem(**item_data)
                    self.systems[new_item.id] = new_item

                # Support-ok betöltése
                for item_data in data.get("supports", []):
                    new_item = ShipSupport(**item_data)
                    self.supports[new_item.id] = new_item
                
                print(f"[RENDSZER] Adatbázis betöltve: {len(self.cores)} Core, {len(self.systems)} System, {len(self.supports)} Support.")
            except Exception as e:
                print(f"[HIBA] Hiba a JSON feldolgozásakor: {e}")

    def get_core(self, item_id):
        return self.cores.get(item_id)

    def get_system(self, item_id):
        return self.systems.get(item_id)

    def get_support(self, item_id):
        return self.supports.get(item_id)
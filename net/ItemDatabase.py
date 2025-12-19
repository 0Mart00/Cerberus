import json
from .Core import Core
from .ShipSystem import ShipSystem
from .ShipSupport import ShipSupport

class ItemDatabase:
    def __init__(self):
        self.cores = {}
        self.systems = {}
        self.supports = {}

    def load_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Core-ok inicializálása
            for item_data in data.get("cores", []):
                new_item = Core(**item_data)
                self.cores[new_item.id] = new_item
                
            # System-ek inicializálása
            for item_data in data.get("systems", []):
                new_item = ShipSystem(**item_data)
                self.systems[new_item.id] = new_item

        print(f"[DB] Betöltve: {len(self.cores)} Core, {len(self.systems)} System.")

    def get_core(self, item_id):
        return self.cores.get(item_id)
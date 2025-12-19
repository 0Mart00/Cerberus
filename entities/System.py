from typing import Optional, Dict, Any
from dataclasses import dataclass, field, fields
from direct.distributed.PyDatagramIterator import PyDatagramIterator

@dataclass
class ShipSystem:
    # --- General System Info ---
    id: int = -1
    name: str = ""
    description: str = ""
    rarity: str = "Common"
    power_usage: int = 0

    # --- Propulsion & Navigation ---
    shipAgility: float = 0.0
    shipMaxVelocity: float = 0.0
    warpDriveStrength: float = 0.0
    jumpDriveConsumption: float = 0.0
    cloakingDeviceDuration: float = 0.0

    # --- Energy & Capacitor ---
    capacitorCapacity: float = 0.0
    capacitorRechargeRate: float = 0.0
    energyEfficiency: float = 0.0

    # --- Ship Systems Efficiency ---
    moduleCPUReduction: float = 0.0
    modulePowergridReduction: float = 0.0
    sensorRangeBonus: float = 0.0
    sensorStrengthBonus: float = 0.0

    # --- Survivability & Signature ---
    signatureRadiusReduction: float = 0.0
    electronicWarfareResistance: float = 0.0

    # --- Referenciák (Hálózaton nem küldjük) ---
    blueprint: Optional[Any] = None
    reprocess: Optional[Any] = None

    def __init__(self, **params):
        """
        Dinamikus inicializáló, amely támogatja a manuális példányosítást 
        és az unpack-ből jövő dictionary-t is.
        """
        # Alapértelmezett értékek beállítása
        for f in fields(self.__class__):
            if not isinstance(f.default, field().__class__):
                setattr(self, f.name, f.default)

        # Paraméterek betöltése
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"[Warning] Ismeretlen property a System-ben: {key}")

    def pack(self, dg):
        """
        A ShipSystem összes releváns mezőjének bináris becsomagolása.
        """
        for f in fields(self):
            # Kihagyjuk a komplex objektumokat, amik nem szeralizálhatóak egyszerűen
            if f.name in ["blueprint", "reprocess"]:
                continue
            
            val = getattr(self, f.name)
            
            if f.type == int:
                dg.addInt32(val)
            elif f.type == float:
                dg.addFloat64(val)
            elif f.type == str:
                dg.addString(val)

    @classmethod
    def unpack(cls, iterator: PyDatagramIterator):
        """
        A ShipSystem adatok kiolvasása a hálózati adatfolyamból.
        """
        extracted_data = {}
        for f in fields(cls):
            if f.name in ["blueprint", "reprocess"]:
                continue
                
            if f.type == int:
                extracted_data[f.name] = iterator.getInt32()
            elif f.type == float:
                extracted_data[f.name] = iterator.getFloat64()
            elif f.type == str:
                extracted_data[f.name] = iterator.getString()
        
        return cls(**extracted_data)

    def apply_to_ship(self, ship_stats: dict):
        """Alkalmazza a bónuszokat egy statisztika-szótárra."""
        ship_stats['max_velocity'] *= (1.0 + self.shipMaxVelocity)
        ship_stats['agility'] *= (1.0 + self.shipAgility)
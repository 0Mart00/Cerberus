from dataclasses import dataclass, field, fields
from typing import Optional, Any, Dict
from direct.distributed.PyDatagramIterator import PyDatagramIterator

@dataclass
class ShipSupport:
    # --- General Support Info ---
    id: int = -1
    name: str = ""
    description: str = ""
    rarity: str = "Common"
    power_usage: int = 0

    # --- Repair & Regeneration ---
    naniteRepairBeamStrength: float = 0.0
    repairSystemCycleTime: float = 0.0
    armorRepairAmount: float = 0.0
    shieldBoostAmount: float = 0.0
    hullRepairAmount: float = 0.0

    # --- Energy & Capacitor ---
    energyTransferArrayStrength: float = 0.0
    capacitorCapacityBonus: float = 0.0
    capacitorRechargeRateBonus: float = 0.0

    # --- Fleet & Utility ---
    targetPainterStrength: float = 0.0
    weaponDisablerStrength: float = 0.0
    sensorBoostBonus: float = 0.0
    signatureRadiusReduction: float = 0.0
    trackingSpeedBonus: float = 0.0

    # --- Logistics & Cargo ---
    cargoCapacityBonus: float = 0.0
    courierMissionPayoutBonus: float = 0.0
    fleetLogisticsRange: float = 0.0

    # --- Referenciák (Hálózaton nem küldjük) ---
    blueprint: Optional[Any] = None
    reprocess: Optional[Any] = None

    def __init__(self, **params):
        """
        Támogatja a keyword argument alapú és a manuális inicializálást is.
        """
        # Alapértelmezett értékek beállítása a dataclass definíció alapján
        for f in fields(self.__class__):
            if not isinstance(f.default, field().__class__):
                setattr(self, f.name, f.default)

        # Paraméterek betöltése
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"[Warning] Ismeretlen property a Support-ban: {key}")

    def pack(self, dg):
        """
        Az összes statisztika bináris becsomagolása a hálózati csomagba.
        """
        for f in fields(self):
            # A hálózati forgalom minimalizálása érdekében a komplex objektumokat kihagyjuk
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
        Egy új ShipSupport példány létrehozása a beérkező hálózati adatokból.
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

    def get_stat(self, stat_name: str) -> float:
        """Segédfüggvény a bónuszok lekéréséhez."""
        return getattr(self, stat_name, 0.0)
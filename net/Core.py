from typing import Optional, Dict, Any
import json
from dataclasses import dataclass, field, fields
from panda3d.core import NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

@dataclass
class ShipCore:
    # --- General Core Info ---
    id: int = -1
    name: str = ""
    description: str = ""
    slot_type: str = "None"  # Pl. Offensive, Defensive, Utility, Industry
    
    # --- Damage Bonuses ---
    dmgPlasmaCannon: float = 0.0
    dmgMissileLauncher: float = 0.0
    dmgRailgun: float = 0.0
    dmgIonBlaster: float = 0.0
    dmgDroneSwarm: float = 0.0
    dmgEmpEmitter: float = 0.0
    dmgQuantumTorpedo: float = 0.0
    dmgSmartbomb: float = 0.0
    dmgNaniteRepairBeam: float = 0.0

    # --- Resistance Bonuses ---
    resPlasmaCannon: float = 0.0
    resMissileLauncher: float = 0.0
    resRailgun: float = 0.0
    resIonBlaster: float = 0.0
    resDroneSwarm: float = 0.0
    resEmpEmitter: float = 0.0
    resQuantumTorpedo: float = 0.0
    resShieldGenerator: float = 0.0
    resNaniteRepairBeam: float = 0.0

    # --- Ship Performance ---
    shipAgility: float = 0.0
    shipMaxVelocity: float = 0.0
    warpDriveStrength: float = 0.0
    jumpDriveConsumption: float = 0.0

    # --- Capacitor & Systems ---
    capacitorCapacity: float = 0.0
    capacitorRechargeRate: float = 0.0
    moduleCPUReduction: float = 0.0
    modulePowergridReduction: float = 0.0

    # --- Drone Operation ---
    droneDamageBonus: float = 0.0
    droneHitpointsBonus: float = 0.0
    droneControlRange: float = 0.0
    maxActiveDrones: int = 0

    # --- Industry & Mining ---
    miningLaserYield: float = 0.0
    iceHarvesterYield: float = 0.0
    gasCloudHarvesterYield: float = 0.0
    reprocessingEfficiency: float = 0.0
    manufacturingTimeReduction: float = 0.0

    # --- Referenciák (Blueprint és Reprocess osztályok feltételezve) ---
    blueprint: Optional[Any] = None
    reprocess: Optional[Any] = None

    def __post_init__(self):
        """
        Ez a metódus fut le a példányosítás után. 
        Itt végezhetsz extra logikát, ha szükséges.
        """
        pass

    @classmethod
    def from_dict(cls, params: Dict[str, Any]):
        """
        A Godot-féle 'params' alapú inicializálás megfelelője.
        Csak azokat az értékeket állítja be, amik léteznek az osztályban.
        """
        valid_params = {k: v for k, v in params.items() if k in cls.__dataclass_fields__}
        return cls(**valid_params)


    def pack(self, dg):
        """
        Automatikusan sorbarendezi és becsomagolja a mezőket a típusaik alapján.
        Fontos: A sorrend fix, mert a dataclass fields mindig ugyanabban a sorrendben adja vissza őket.
        """
        for f in fields(self):
            # Kihagyjuk a komplex referenciákat
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
        Automatikusan kiolvassa az adatokat az iterátorból a field definíciók sorrendjében.
        """
        data = {}
        for f in fields(cls):
            if f.name in ["blueprint", "reprocess"]:
                continue
                
            if f.type == int:
                data[f.name] = iterator.getInt32()
            elif f.type == float:
                data[f.name] = iterator.getFloat64()
            elif f.type == str:
                data[f.name] = iterator.getString()
        
        return cls(**data)
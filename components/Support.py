from typing import Optional, Dict, Any
from dataclasses import dataclass, field, fields
from panda3d.core import NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

@dataclass
class ShipCore:
    # --- Alapinfók ---
    id: int = -1
    name: str = "Ismeretlen Mag"
    description: str = ""
    slot_type: str = "Core"
    
    # --- Sebzés Bónuszok ---
    dmgPlasmaCannon: float = 0.0
    dmgMissileLauncher: float = 0.0
    dmgRailgun: float = 0.0
    dmgIonBlaster: float = 0.0
    dmgDroneSwarm: float = 0.0
    dmgEmpEmitter: float = 0.0
    dmgQuantumTorpedo: float = 0.0
    dmgSmartbomb: float = 0.0
    dmgNaniteRepairBeam: float = 0.0

    # --- Ellenállás Bónuszok ---
    resPlasmaCannon: float = 0.0
    resMissileLauncher: float = 0.0
    resRailgun: float = 0.0
    resIonBlaster: float = 0.0
    resDroneSwarm: float = 0.0
    resEmpEmitter: float = 0.0
    resQuantumTorpedo: float = 0.0
    resShieldGenerator: float = 0.0
    resNaniteRepairBeam: float = 0.0

    # --- Hajó Teljesítmény ---
    shipAgility: float = 0.0
    shipMaxVelocity: float = 0.0
    warpDriveStrength: float = 0.0
    jumpDriveConsumption: float = 0.0

    # --- Energiarendszerek ---
    capacitorCapacity: float = 0.0
    capacitorRechargeRate: float = 0.0
    moduleCPUReduction: float = 0.0
    modulePowergridReduction: float = 0.0

    # --- Drónok és Ipar ---
    droneDamageBonus: float = 0.0
    miningLaserYield: float = 0.0

    def __init__(self, **params):
        """
        HALADÓ KONSTRUKTOR: 
        Dinamikusan betölti a paramétereket, alapértelmezett értékeket állít be,
        és figyelmeztet az ismeretlen mezőkre.
        """
        # Alapértelmezett értékek beállítása a dataclass definíció alapján
        for f in fields(self.__class__):
            # Csak akkor állítjuk be, ha nem speciális field objektum
            if not hasattr(f.default, 'default_factory'):
                setattr(self, f.name, f.default)

        # Átadott paraméterek betöltése
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"[Warning] Ismeretlen property a Core-ban: {key}")

    def pack(self, dg):
        """Adatok becsomagolása hálózati küldéshez."""
        for f in fields(self):
            val = getattr(self, f.name)
            if f.type == int:
                dg.addInt32(int(val))
            elif f.type == float:
                dg.addFloat64(float(val))
            elif f.type == str:
                dg.addString(str(val))

    @classmethod
    def unpack(cls, iterator: PyDatagramIterator):
        """Adatok kicsomagolása a hálózatról."""
        data = {}
        for f in fields(cls):
            try:
                if f.type == int:
                    data[f.name] = iterator.getInt32()
                elif f.type == float:
                    data[f.name] = iterator.getFloat64()
                elif f.type == str:
                    data[f.name] = iterator.getString()
            except:
                break
        return cls(**data)

@dataclass
class ShipSupport:
    # --- Alapinfók ---
    id: int = -1
    name: str = "Ismeretlen Support Modul"
    description: str = ""
    slot_type: str = "Support"
    
    # --- Speciális Support Statok ---
    shieldBoostAmount: float = 0.0
    armorRepairRate: float = 0.0
    hullIntegrityBonus: float = 0.0
    sensorRangeBonus: float = 0.0
    signatureRadiusReduction: float = 0.0
    
    def __init__(self, **params):
        """Haladó konstruktor Support modulhoz."""
        for f in fields(self.__class__):
            if not hasattr(f.default, 'default_factory'):
                setattr(self, f.name, f.default)

        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"[Warning] Ismeretlen property a Support-ban: {key}")

    def pack(self, dg):
        for f in fields(self):
            val = getattr(self, f.name)
            if f.type == int: dg.addInt32(int(val))
            elif f.type == float: dg.addFloat64(float(val))
            elif f.type == str: dg.addString(str(val))

    @classmethod
    def unpack(cls, iterator: PyDatagramIterator):
        data = {}
        for f in fields(cls):
            try:
                if f.type == int: data[f.name] = iterator.getInt32()
                elif f.type == float: data[f.name] = iterator.getFloat64()
                elif f.type == str: data[f.name] = iterator.getString()
            except: break
        return cls(**data)

@dataclass
class ShipSystem:
    # --- Alapinfók ---
    id: int = -1
    name: str = "Ismeretlen Rendszer"
    description: str = ""
    slot_type: str = "System"
    
    # --- Speciális Rendszer Statok ---
    cpuOutputBonus: float = 0.0
    powergridOutputBonus: float = 0.0
    targetingSpeedBonus: float = 0.0
    scanResolutionBonus: float = 0.0
    warpSpeedBonus: float = 0.0

    def __init__(self, **params):
        """Haladó konstruktor System modulhoz."""
        for f in fields(self.__class__):
            if not hasattr(f.default, 'default_factory'):
                setattr(self, f.name, f.default)

        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"[Warning] Ismeretlen property a System-ben: {key}")

    def pack(self, dg):
        for f in fields(self):
            val = getattr(self, f.name)
            if f.type == int: dg.addInt32(int(val))
            elif f.type == float: dg.addFloat64(float(val))
            elif f.type == str: dg.addString(str(val))

    @classmethod
    def unpack(cls, iterator: PyDatagramIterator):
        data = {}
        for f in fields(cls):
            try:
                if f.type == int: data[f.name] = iterator.getInt32()
                elif f.type == float: data[f.name] = iterator.getFloat64()
                elif f.type == str: data[f.name] = iterator.getString()
            except: break
        return cls(**data)

# --- Segédosztályok a típusossághoz ---
class DamageType:
    IMPACT = 0
    THERMIC = 1
    IONIC = 2
    DETONATION = 3

class MiningLaser:
    def __init__(self, range=150, resource_yield=10):
        self.range = range
        self.resource_yield = resource_yield
        self.resource_type = "Vas"

class WeaponMount:
    def __init__(self, name="Lézer", damage_type=DamageType.THERMIC, damage=10, range=100):
        self.name = name
        self.damage_type = damage_type
        self.damage = damage
        self.range = range

class TacticalSlot:
    def __init__(self, name="Modul", effect_type="speed", value=1.0):
        self.name = name
        self.effect_type = effect_type
        self.value = value

class ArmorSlot:
    def __init__(self, name="Páncél", armor_hp=100, resistance_type=0, resistance_val=0.1):
        self.name = name
        self.armor_hp = armor_hp
        self.resistance_type = resistance_type
        self.resistance_val = resistance_val

class HullAugment:
    def __init__(self, name="Bővítő", hull_hp=50):
        self.name = name
        self.hull_hp = hull_hp
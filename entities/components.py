# ==============================================================================
# ENUMS & CONSTANTS
# ==============================================================================
class DamageType:
    """A négy alapvető sebzéstípus"""
    IMPACT = "Impact"           # Becsapódás (Kinetikus)
    THERMIC = "Thermic"         # Hő (Lézer, Plazma)
    IONIC = "Ionic"             # Ion (Elektromágneses)
    DETONATION = "Detonation"   # Robbanás (Rakéta, Akna)

class RelicType:
    """Relic működési módok"""
    PASSIVE = "Passive"         # Állandó bónusz
    ACTIVE = "Active"           # Aktiválható képesség
    TRIGGERED = "Triggered"     # Feltételhez kötött (pl. találatkor)

# ==============================================================================
# COMPONENT CLASSES (Felszerelés Osztályok)
# ==============================================================================

class ShipComponent:
    """Alap osztály a hajó alkatrészeinek"""
    def __init__(self, name="Alkatrész"):
        self.name = name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

class WeaponMount(ShipComponent):
    """Fegyver foglalat: Sebzés, lőtáv, újratöltés"""
    def __init__(self, name="Alap Lézer", damage_type=DamageType.THERMIC, damage=10.0, range=100.0, cooldown=1.0):
        super().__init__(name)
        self.damage_type = damage_type
        self.damage = damage
        self.range = range
        self.cooldown = cooldown
        self.last_fire = 0.0

class TacticalSlot(ShipComponent):
    """Taktikai modul: Speciális effektek (pl. gyorsító, zavaró)"""
    def __init__(self, name="Szenzor Erősítő", effect_type="scan_range", value=1.5):
        super().__init__(name)
        self.effect_type = effect_type # pl. 'speed_boost', 'scan_range', 'jamming'
        self.value = value

class ArmorSlot(ShipComponent):
    """Páncélzat: Extra védelem és ellenállás"""
    def __init__(self, name="Nanofiber Páncél", armor_hp=100.0, resistance_type=DamageType.IMPACT, resistance_val=0.1):
        super().__init__(name)
        self.armor_hp = armor_hp
        # Melyik típusra ad ellenállást
        self.resistance_bonus = {resistance_type: resistance_val}

class HullAugment(ShipComponent):
    """Burkolat kiegészítő: Strukturális épség és passzív bónuszok"""
    def __init__(self, name="Szerkezeti Merevítő", hull_hp=200.0, agility_penalty=0.0):
        super().__init__(name)
        self.hull_hp = hull_hp
        self.agility_penalty = agility_penalty

class RelicSlot(ShipComponent):
    """Ősi technológia: Különleges módosítók"""
    def __init__(self, name="Ismeretlen Ereklye", relic_type=RelicType.PASSIVE, modifiers=None):
        super().__init__(name)
        self.relic_type = relic_type
        # Statisztika módosítók szótára, pl. {'shield_recharge': 1.2}
        self.modifiers = modifiers if modifiers else {}

class MiningLaser(ShipComponent):
    """Bányászati lézer: Hatótáv és hozam"""
    def __init__(self, name="Bányász Lézer", range=200.0, resource_yield=10, type="Veldspar"):
        super().__init__(name)
        self.range = range
        self.resource_yield = resource_yield
        self.resource_type = type

class Component:
    """Base class for all ship components."""
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.ship = None

    def on_mount(self, ship):
        self.ship = ship

    def on_unmount(self):
        self.ship = None

class Engine(Component):
    def __init__(self, name, level, max_speed, acceleration, turn_rate):
        super().__init__(name, level)
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.turn_rate = turn_rate

class Weapon(Component):
    def __init__(self, name, level, damage, fire_rate, range):
        super().__init__(name, level)
        self.damage = damage
        self.fire_rate = fire_rate
        self.range = range
        self.last_fired = 0

class Shield(Component):
    def __init__(self, name, level, capacity, recharge_rate):
        super().__init__(name, level)
        self.capacity = capacity
        self.recharge_rate = recharge_rate

class Cargo(Component):
    def __init__(self, name, level, capacity):
        super().__init__(name, level)
        self.capacity = capacity
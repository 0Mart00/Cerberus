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
    def __init__(self, name="Alap Lézer", damage=10.0, range=100.0, cooldown=1.0):
        super().__init__(name)
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
    def __init__(self, name="Nanofiber Páncél", armor_hp=100.0, resistance=0.1):
        super().__init__(name)
        self.armor_hp = armor_hp
        self.resistance = resistance # 0.0 - 1.0 (százalékos sebzés csökkentés)

class HullAugment(ShipComponent):
    """Burkolat kiegészítő: Strukturális épség és passzív bónuszok"""
    def __init__(self, name="Szerkezeti Merevítő", hull_hp=200.0, agility_penalty=0.0):
        super().__init__(name)
        self.hull_hp = hull_hp
        self.agility_penalty = agility_penalty # Mozgékonyság csökkenés (pl. nehéz lemezek)
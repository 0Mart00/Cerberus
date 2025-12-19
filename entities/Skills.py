import math

class Skill:
    def __init__(self, name=""):
        # General Skill Info
        self.name = name
        self.description = ""
        self.level = 0
        self.xp = 0.0
        self.max_level = 5
        self.training_time_multiplier = 1.0
        self.primary_attribute = "Intelligence"
        self.secondary_attribute = "Memory"

        # Skill Prerequisites
        self.required_skills = {} # e.g., {"Gunnery": 1}

        # --- Combat - Damage Bonuses ---
        self._dmgPlasmaCannon = 0.0
        self._dmgMissileLauncher = 0.0
        self._dmgRailgun = 0.0
        self._dmgIonBlaster = 0.0
        self._dmgDroneSwarm = 0.0
        self._dmgEmpEmitter = 0.0
        self._dmgQuantumTorpedo = 0.0
        self._dmgEnergyNeutralizer = 0.0
        self._dmgWebifier = 0.0
        self._dmgScrambler = 0.0
        self._dmgDisruptor = 0.0
        self._dmgSmartbomb = 0.0
        self._dmgBombLauncher = 0.0

        # --- Combat - Resistance & Defense ---
        self._resPlasmaCannon = 0.0
        self._resMissileLauncher = 0.0
        self._resRailgun = 0.0
        self._resIonBlaster = 0.0
        self._resDroneSwarm = 0.0
        self._resEmpEmitter = 0.0
        self._resShieldGenerator = 0.0
        self._resArmorHardener = 0.0
        self._resHullPlating = 0.0
        self._capacitorCapacity = 0.0
        self._capacitorRechargeRate = 0.0
        self._signatureRadiusReduction = 0.0
        self._trackingSpeedBonus = 0.0
        self._missileVelocityBonus = 0.0
        self._missileExplosionRadiusReduction = 0.0

        # --- Accuracy ---
        self._accuracyPlasmaCannon = 0.0
        self._accuracyRailgun = 0.0
        self._accuracyIonBlaster = 0.0

        # --- Piloting & Ship ---
        self._shipAgility = 0.0
        self._shipMaxVelocity = 0.0
        self._moduleCPUReduction = 0.0
        self._modulePowergridReduction = 0.0

    # --- Logic Methods ---

    def add_xp(self, amount):
        """Adds XP and handles level up logic."""
        self.xp += amount
        while self.xp >= self.get_xp_for_next_level() and self.level < self.max_level:
            self.xp -= self.get_xp_for_next_level()
            self.level_up()

    def level_up(self):
        """Increments level and triggers any necessary updates."""
        self.level += 1
        print(f"Skill {self.name} leveled up to {self.level}!")

    def get_xp_for_next_level(self) -> float:
        """Returns required XP using an exponential curve."""
        return math.pow(self.level + 1, 2) * 100

    def get_bonus_value(self, bonus_name: str) -> float:
        """
        Calculates the cumulative bonus based on current level.
        Example: get_bonus_value('dmgPlasmaCannon')
        """
        # We look for the internal variable (prefixed with _)
        attr_name = f"_{bonus_name}"
        if hasattr(self, attr_name):
            base_value = getattr(self, attr_name)
            return base_value * self.level
        return 0.0
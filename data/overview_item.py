from panda3d.core import Vec3
import random
import math

class OverviewItem:
    """Data model for a single entity in the Overview list."""
    def __init__(self, id, name, item_type, position, velocity_vec, angular_vel, standing, flags=None):
        self.id = id
        self.name = name
        self.type = item_type  # Ship, Drone, Structure, Wreck, Asteroid, Missile
        self.position = position
        self.velocity_vec = velocity_vec
        self.angular_vel = angular_vel
        self.standing = standing  # Enemy, Neutral, Friendly, Corp/Fleet
        self.flags = flags if flags is not None else [] # Targeted, Attacking, WithinRange
        self.distance = 0.0
        self.velocity = velocity_vec.length()

    def update_state(self, player_pos, dt=0.1):
        """Updates the entity's position and calculates distance to the player."""
        
        # Simple movement simulation
        if self.velocity > 0:
            self.position += self.velocity_vec * dt
            
            # Simple random course correction
            if random.random() < 0.03:
                rand_vec = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
                self.velocity_vec = (self.velocity_vec * 0.9 + rand_vec * 0.1).normalized() * self.velocity

        # Update distance
        self.distance = (self.position - player_pos).length()

        # Update flags based on distance
        if self.distance < 50000 and "WithinRange" not in self.flags: # 50 km
            self.flags.append("WithinRange")
        elif self.distance >= 50000 and "WithinRange" in self.flags:
            if "WithinRange" in self.flags: self.flags.remove("WithinRange")

    def get_display_data(self, player_pos):
        """Returns the current data required for UI display."""
        self.update_state(player_pos)
        return {
            'id': self.id,
            'icon': self.type[0], # Placeholder icon based on type first letter
            'name': self.name,
            'distance': self.distance,
            'velocity': self.velocity,
            'angular': self.angular_vel,
            'standing': self.standing,
            'flags': sorted(self.flags),
            'type': self.type
        }

class OverviewManager:
    """Manages all OverviewItems and the player's position."""
    def __init__(self, num_entities=30):
        # Player position in the simulation (typically (0,0,0) in the current sector)
        self.player_pos = Vec3(0, 0, 0) 
        self.items = []
        self._next_id = 1
        self._entity_types = ["Ship", "Drone", "Structure", "Wreck", "Asteroid", "Missile"]
        self._standings = ["Enemy", "Neutral", "Friendly", "Corp/Fleet"]
        self._names = ["Vargur", "Gila", "Rattlesnake", "Capsule", "Wrecked Ship", "Small Asteroid", "Citadel"]
        self._initial_spawn(num_entities)
        
    def _initial_spawn(self, num):
        """Creates random entities for testing."""
        for _ in range(num):
            item_type = random.choice(self._entity_types)
            standing = random.choice(self._standings)
            name = random.choice(self._names) + f" ({self._next_id})"

            # Random position far from the player (200-500 km range)
            pos_range = random.uniform(200000, 500000) 
            pos = Vec3(random.uniform(-pos_range, pos_range), random.uniform(-pos_range, pos_range), random.uniform(-pos_range, pos_range))

            # Velocity (m/s)
            max_vel = 500.0 if item_type in ("Ship", "Drone", "Missile") else 0.0
            vel_vec = Vec3(random.uniform(-max_vel, max_vel), random.uniform(-max_vel, max_vel), random.uniform(-max_vel, max_vel))
            vel = vel_vec.length()
            if vel > 0: vel_vec = vel_vec.normalized() * random.uniform(0.01, max_vel)
            
            flags = []
            if random.random() < 0.1: flags.append("Targeted")
            if random.random() < 0.1 and standing == "Enemy": flags.append("Attacking")

            self.items.append(OverviewItem(
                id=self._next_id,
                name=name,
                item_type=item_type,
                position=pos,
                velocity_vec=vel_vec,
                angular_vel=random.uniform(0.0, 1.0),
                standing=standing,
                flags=flags
            ))
            self._next_id += 1

    def get_all_items_data(self):
        """Returns the updated display data for all entities."""
        return [item.get_display_data(self.player_pos) for item in self.items]
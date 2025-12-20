from entities.entity import Entity

class CelestialBody(Entity):
    """Base class for non-ship objects in space."""
    def __init__(self, manager, entity_id, name, entity_type="Celestial", max_hp=1000):
        super().__init__(manager, entity_id, name, entity_type)
        self.max_hull = max_hp
        self.current_hull = max_hp
        self.load_model()

    def load_model(self):
        pass

class Asteroid(CelestialBody):
    def __init__(self, manager, entity_id, name="Asteroid"):
        super().__init__(manager, entity_id, name, "Asteroid", max_hp=500)

    def load_model(self):
        # Use self.app instead of self.manager.base
        if self.app:
            self.model = self.app.loader.loadModel("models/misc/sphere")
            if self.model:
                self.model.reparentTo(self.root)
                self.model.setScale(2)
                self.model.setColor(0.4, 0.3, 0.2, 1)

class Planet(CelestialBody):
    def __init__(self, manager, entity_id, name="Planet"):
        super().__init__(manager, entity_id, name, "Planet", max_hp=10000)

    def load_model(self):
        if self.app:
            self.model = self.app.loader.loadModel("models/misc/sphere")
            if self.model:
                self.model.reparentTo(self.root)
                self.model.setScale(30)
                self.model.setColor(0.1, 0.4, 0.8, 1)

class Wreck(CelestialBody):
    def __init__(self, manager, entity_id, name="Wreck"):
        super().__init__(manager, entity_id, name, "Wreck", max_hp=200)

    def load_model(self):
        if self.app:
            self.model = self.app.loader.loadModel("models/box")
            if self.model:
                self.model.reparentTo(self.root)
                self.model.setScale(3, 5, 2)
                self.model.setColor(0.2, 0.2, 0.2, 1)

class Stargate(CelestialBody):
    def __init__(self, manager, entity_id, name="Gate"):
        super().__init__(manager, entity_id, name, "Stargate", max_hp=5000)

    def load_model(self):
        if self.app:
            self.model = self.app.loader.loadModel("models/misc/sphere")
            if self.model:
                self.model.reparentTo(self.root)
                self.model.setScale(15, 1, 15)
                self.model.setColor(0.5, 0.5, 1, 0.4)
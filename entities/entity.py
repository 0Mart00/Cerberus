from panda3d.core import NodePath, Vec3

class Entity:
    """
    Base class for all game entities (ships, stations, celestials, etc.)
    """
    def __init__(self, manager, entity_id, name="Unknown", entity_type="Static"):
        self.manager = manager
        self.id = entity_id
        self.name = name
        self.entity_type = entity_type
        
        # Determine the ShowBase instance. 
        # If the manager is the Game (ShowBase), use it directly.
        # Otherwise, try to find a 'base' attribute.
        if hasattr(self.manager, 'loader'):
            self.app = self.manager
        else:
            self.app = getattr(self.manager, 'base', None)
        
        # Create the root node for this entity in the scene graph
        self.root = NodePath(f"Entity_{self.id}_{self.name}")
        
        # By default, attach to the main scene (render)
        if self.app:
            self.root.reparentTo(self.app.render)
            
        self.components = []
        self.is_active = True
        
        # Alapértelmezett statisztikák minden entitáshoz
        self.max_hull = 100.0
        self.current_hull = 100.0

    def update(self, dt):
        """
        Called every frame by the game loop/task manager.
        """
        pass

    def destroy(self):
        """
        Clean up resources when the entity is removed.
        """
        self.is_active = False
        if self.root:
            self.root.removeNode()
            self.root = None

    def get_pos(self):
        """Wrapper for NodePath getPos"""
        if self.root:
            return self.root.getPos()
        return Vec3(0, 0, 0)

    def set_pos(self, x, y=None, z=None):
        """Wrapper for NodePath setPos"""
        if self.root:
            if y is None and z is None:
                 # Assume x is a Vec3 or tuple
                self.root.setPos(x)
            else:
                self.root.setPos(x, y, z)

    def get_hpr(self):
        """Wrapper for NodePath getHpr"""
        if self.root:
            return self.root.getHpr()
        return Vec3(0, 0, 0)

    def look_at(self, target):
        """Wrapper for NodePath lookAt"""
        if self.root:
            # target can be a NodePath or another Entity's root
            if hasattr(target, 'root'):
                self.root.lookAt(target.root)
            else:
                self.root.lookAt(target)
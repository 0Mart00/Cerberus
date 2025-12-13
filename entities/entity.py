from panda3d.core import Vec3
from direct.showbase.DirectObject import DirectObject

# ==============================================================================
# BASE ENTITY CLASS
# ==============================================================================
class Entity(DirectObject):
    def __init__(self, manager, entity_id, name="Objektum", entity_type="Entity"):
        self.manager = manager
        self.id = entity_id
        self.name = name
        self.entity_type = entity_type
        self.model = None

    def load_model(self, path, scale=1.0, color=None):
        """Betölti a 3D modellt és beállítja az alap tulajdonságokat"""
        try:
            # A loader és render a Panda3D globális változói
            self.model = loader.loadModel(path)
        except:
            print(f"[ERROR] Nem sikerült betölteni: {path}, placeholder használata.")
            self.model = loader.loadModel("models/box")
            
        self.model.setScale(scale)
        self.model.reparentTo(render)
        
        if color:
            self.model.setColor(*color)

    def get_pos(self):
        if self.model:
            return self.model.getPos()
        return Vec3(0,0,0)

    def set_pos(self, x, y, z):
        if self.model:
            self.model.setPos(x, y, z)
    
    def destroy(self):
        if self.model:
            self.model.removeNode()
        self.ignoreAll()
    
    def update(self, dt):
        """Minden entitás frissíthető, de alapból nem csinál semmit"""
        pass
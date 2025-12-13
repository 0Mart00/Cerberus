from panda3d.core import Vec3, NodePath
from direct.showbase.DirectObject import DirectObject
# Importáljuk a procedurális doboz generálást
from systems.generation import AsteroidGenerator

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
        """Betölti a 3D modellt fájlból vagy procedurálisan fallback-el."""
        
        # Először megpróbáljuk betölteni a fájlt
        model_loaded = False
        # A loader Panda3D globális változó
        try:
            self.model = loader.loadModel(path)
            if self.model and self.model.getNumPaths() > 0:
                 model_loaded = True
        except Exception:
            pass # A fájl betöltése nem sikerült
        
        if not model_loaded:
            print(f"[ERROR] Nem sikerült betölteni a {path} fájlt, procedurális doboz fallback.")
            
            # Procedurális fallback: Használjuk a generator.py-ban lévő logikát
            generator = AsteroidGenerator() 
            # A fallback most a procedurális dobozt fogja használni
            self.model = generator.generate(name=self.name, min_scale=scale, max_scale=scale * 1.05)
            
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
from panda3d.core import (
    CollisionTraverser, 
    CollisionHandlerQueue, 
    CollisionNode, 
    CollisionRay, 
    BitMask32, 
    Vec3, 
    LineSegs,
    NodePath
)
from direct.task import Task
from globals import MASK_ASTEROID, MASK_LOOT, TARGETABLE_OBJECTS, LOOT_OBJECTS

class CombatSystem:
    def __init__(self, game):
        self.game = game
        
        # Ütközésvizsgáló setup
        self.cTrav = CollisionTraverser()
        self.collision_queue = CollisionHandlerQueue()
        
        # Sugár (Picker Ray) inicializálása a kamerához (vagy a hajóhoz)
        self.picker_node = CollisionNode('playerRay')
        self.picker_np = self.game.camera.attachNewNode(self.picker_node)
        self.picker_node.setFromCollideMask(BitMask32.bit(1) | BitMask32.bit(2))        
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.cTrav.addCollider(self.picker_np, self.collision_queue)
        
        # Vizuális lézer effekt
        self.laser_line = None
        self.laser_np = None
        
        # Állapotok
        self.laser_active = False
        self.tractor_active = False
        
        # Eseménykezelés
        self.game.accept("1", self.set_laser, [True])
        self.game.accept("1-up", self.set_laser, [False])
        self.game.accept("2", self.set_tractor, [True])
        self.game.accept("2-up", self.set_tractor, [False])

    def set_laser(self, state):
        self.laser_active = state
        if not state and self.laser_np:
            self.laser_np.removeNode()
            self.laser_np = None

    def set_tractor(self, state):
        self.tractor_active = state

    def draw_laser(self, start_pos, end_pos, color=(0, 1, 1, 1)):
        if self.laser_np:
            self.laser_np.removeNode()
        
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(color)
        segs.moveTo(start_pos)
        segs.drawTo(end_pos)
        
        self.laser_np = self.game.render.attachNewNode(segs.create())

    def update(self, dt):
        if not self.game.mouseWatcherNode.hasMouse():
            return

        # Sugár irányítása az egér felé
        mpos = self.game.mouseWatcherNode.getMouse()
        self.picker_ray.setFromLens(self.game.camNode, mpos.getX(), mpos.getY())
        
        # Vizsgálat futtatása
        self.cTrav.traverse(self.game.render)
        
        if self.laser_active:
            self.handle_laser(dt)
        
        if self.tractor_active:
            self.handle_tractor(dt)


    def handle_laser(self, dt):
        # A lézer kiindulópontja a hajó orra vagy a kamera
        start_pos = self.game.camera.getPos(self.game.render)
        
        if self.collision_queue.getNumEntries() > 0:
            self.collision_queue.sortEntries()
            entry = self.collision_queue.getEntry(0)
            hit_point = entry.getSurfacePoint(self.game.render)
            hit_node_path = entry.getIntoNodePath()
            
            # Rajzoljuk ki a lézert a találati pontig
            self.draw_laser(start_pos, hit_point, (1, 0.2, 0.2, 1))
            
            # Bányászat logika: keressük meg az entitást
            entity = hit_node_path.getPythonTag("entity")
            if entity and hasattr(entity, "drill"):
                # Itt szükség van a hit_point-ra, amit fentebb definiáltunk
                local_hit = entity.geom_node_path.getRelativePoint(self.game.render, hit_point)
                entity.drill(local_hit)
        else:
            # Ha nincs találat, lőjünk a messzeségbe
            direction = self.game.render.getRelativeVector(self.game.camera, Vec3(0, 1000, 0))
            self.draw_laser(start_pos, start_pos + direction, (1, 0, 0, 0.5))

    def handle_tractor(self, dt):
        if self.collision_queue.getNumEntries() > 0:
            self.collision_queue.sortEntries()
            entry = self.collision_queue.getEntry(0)
            
            # Itt NEM kell a hit_point, csak a NodePath és az entitás
            hit_node_path = entry.getIntoNodePath()
            entity = hit_node_path.getPythonTag("entity")
            
            # Csak a "Loot" típusú dolgokat vonzzuk (pl. Debris)
            if entity and entity.entity_type == "Loot":
                ship_pos = self.game.camera.getPos(self.game.render)
                loot_pos = entity.root.getPos(self.game.render)
                
                direction = ship_pos - loot_pos
                dist = direction.length()
                
                if dist > 2.0:
                    direction.normalize()
                    # Mozgatjuk az objektumot a hajó felé
                    new_pos = loot_pos + direction * 50.0 * dt
                    entity.root.setPos(self.game.render, new_pos)
                else:
                    print("[System] Loot begyűjtve!")
                    entity.destroy() # Vagy entity.root.removeNode()
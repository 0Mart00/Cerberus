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
from direct.showbase.DirectObject import DirectObject # Fontos az eseményekhez
import globals # Importáljuk az elején

class CombatSystem(DirectObject):
    def __init__(self, game):
        self.game = game
        
        # Ütközésvizsgáló setup
        self.cTrav = CollisionTraverser()
        self.collision_queue = CollisionHandlerQueue()
        
        # Sugár (Picker Ray) setup
        self.picker_node = CollisionNode('playerRay')
        self.picker_np = self.game.camera.attachNewNode(self.picker_node)
        
        # JAVÍTÁS: Használjuk a globals-ban definiált maszkokat
        # BitMask32.bit(1) az MASK_ASTEROID, BitMask32.bit(2) a MASK_SHIP
        self.picker_node.setFromCollideMask(globals.MASK_ASTEROID | globals.MASK_SHIP)
        # Fontos: A sugár ne ütközzön semmivel "befelé"
        self.picker_node.setIntoCollideMask(BitMask32.allOff())
        
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.cTrav.addCollider(self.picker_np, self.collision_queue)
        
        self.laser_np = None
        self.laser_active = False
        self.tractor_active = False

        # Eseménykezelés
        self.accept("mouse1", self.select_target)
        self.accept("1", self.set_laser, [True])
        self.accept("1-up", self.set_laser, [False])
        self.accept("2", self.set_tractor, [True])
        self.accept("2-up", self.set_tractor, [False])

    def select_target(self):
        """Kijelöli az objektumot, amire az egérrel kattintottunk."""
        if not self.game.mouseWatcherNode.hasMouse():
            return

        # 1. Frissítjük a sugarat az aktuális egérpozícióra
        mpos = self.game.mouseWatcherNode.getMouse()
        self.picker_ray.setFromLens(self.game.camNode, mpos.getX(), mpos.getY())
        
        # 2. Kényszerített ütközésvizsgálat (Ezt kell hívni kattintáskor!)
        self.cTrav.traverse(self.game.render)
        
        # 3. Találatok feldolgozása
        if self.collision_queue.getNumEntries() > 0:
            self.collision_queue.sortEntries()
            entry = self.collision_queue.getEntry(0)
            hit_node_path = entry.getIntoNodePath()
            
            # Megkeressük az entitást (felfelé haladva a fában, ha kell)
            entity = hit_node_path.getPythonTag("entity")
            if not entity:
                # Ha a konkrét ütközőn nincs, megnézzük a szülőknél
                entity = hit_node_path.findNetPythonTag("entity").getPythonTag("entity")
            
            if entity:
                globals.SELECTED_TARGET = entity
                print(f"[Combat] Célpont kijelölve: {getattr(entity, 'name', 'Ismeretlen')} (Típus: {entity.entity_type})")
            else:
                print("[Combat] Találat van, de nincs entitás tag!")
        else:
            globals.SELECTED_TARGET = None
            print("[Combat] Kijelölés törölve (üres terület).")

    def handle_laser(self, dt):
        import globals
        start_pos = self.game.camera.getPos(self.game.render)
        
        # Ellenőrizzük, hogy létezik-e a célpont és van-e még modellje (nincs-e törölve)
        if globals.SELECTED_TARGET and not globals.SELECTED_TARGET.root.isEmpty():
            target_pos = globals.SELECTED_TARGET.root.getPos(self.game.render)
            
            # Lézer rajzolása a célpontig
            self.draw_laser(start_pos, target_pos, (1, 0, 0, 1))
            
            # Sebzés bevitel
            if hasattr(globals.SELECTED_TARGET, "take_damage"):
                globals.SELECTED_TARGET.take_damage(globals.LASER_DAMAGE * dt)
                
            # Ha a célpont közben megsemmisült, ürítjük a kijelölést
            if globals.SELECTED_TARGET.current_hull <= 0:
                globals.SELECTED_TARGET = None
        else:
            # Ha nincs célpont, előre lő vaktában
            direction = self.game.render.getRelativeVector(self.game.camera, Vec3(0, 100, 0))
            self.draw_laser(start_pos, start_pos + direction, (0.5, 0, 0, 0.5))

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


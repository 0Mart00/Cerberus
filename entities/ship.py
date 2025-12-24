# Cerberus/entities/ship.py

import random
from panda3d.core import Vec3, CollisionNode, CollisionSphere, CollisionRay, CollisionHandlerQueue, BitMask32
from entities.entity import Entity
from entities.components import Engine, Weapon, Shield, Cargo
import globals as g
from panda3d.core import Material
from panda3d.core import TextureStage, TexGenAttrib # Fontos az új import!
class Ship(Entity):
    def __init__(self, manager, ship_id, is_local=False, name="Unknown", ship_type="Unknown"):
        # Az Entity létrehozza a self.root-ot
        super().__init__(manager, ship_id, name, entity_type="Ship")

        self.node = self.root
        self.is_local = is_local
        self.ship_type = ship_type
        self.model = None  # Kezdetben nincs vizuális megjelenés
        
        
        # --- Komponensek és Statisztikák ---
        self.engines, self.weapons, self.shields, self.cargos = [], [], [], []
        self.max_hull = 1000.0
        self.current_hull = 1000.0
        self.max_shield = 0.0
        self.current_shield = 0.0
        
        # Eszközök állapota
        self.is_mining = False
        self.is_tractoring = False
        
        # Raycast a bányászathoz/vonósugárhoz
        self.ray_queue = CollisionHandlerQueue()
        self.picker_ray = CollisionRay()
        
        self.setup_collision()
        
        # Alapfelszerelés a tesztekhez
        self.mount_component(Engine("Standard Thruster", 1, 20.0, 50.0, 3.0))
        self.mount_component(Shield("Basic Shield", 1, 500.0, 5.0))
        self.recalculate_stats()

        if self.is_local:
            self.setup_controls()
            # Sugár setup (a hajó orrából előre)
            if self.app:
                picker_node = CollisionNode('ship_ray')
                picker_node.addSolid(self.picker_ray)
                # Bit 1: Asteroids, Bit 2: Loot
                picker_node.setFromCollideMask(BitMask32.bit(1) | BitMask32.bit(2))
                picker_node.setIntoCollideMask(BitMask32.allOff())
                self.picker_np = self.root.attachNewNode(picker_node)
                self.app.cTrav.addCollider(self.picker_np, self.ray_queue)

    def setup_collision(self):
        """Ütközési zóna beállítása."""
        coll_node = CollisionNode(f"ship_coll_{self.id}")
        coll_node.addSolid(CollisionSphere(0, 0, 0, 3))
        mask = BitMask32(0x1)
        coll_node.setIntoCollideMask(mask)
        self.c_np = self.root.attachNewNode(coll_node)

    def setup_controls(self):
        """Csak a hajó-specifikus eszközök bindjai (Bányászat, Vonósugár)."""
        if not self.app: return
        self.app.accept("mouse1", self.set_mining, [True])
        self.app.accept("mouse1-up", self.set_mining, [False])
        self.app.accept("mouse3", self.set_tractoring, [True])
        self.app.accept("mouse3-up", self.set_tractoring, [False])

    def set_mining(self, val): self.is_mining = val
    def set_tractoring(self, val): self.is_tractoring = val

    def update(self, dt):
        """Hajó specifikus frissítések (bányászat, pajzs)."""
        if self.is_local:
            if self.is_mining: self.fire_laser(dt)
            if self.is_tractoring: self.use_tractor_beam(dt)
        
        # Pajzs regeneráció
        for s in self.shields:
            if self.current_shield < self.max_shield:
                self.current_shield = min(self.max_shield, self.current_shield + s.recharge_rate * dt)

    def fire_laser(self, dt):
        """Lézeres bányászat logika."""
        self.picker_ray.setOrigin(0, 0, 0)
        self.picker_ray.setDirection(0, 1, 0) # Előre (Y+)
        if self.ray_queue.getNumEntries() > 0:
            self.ray_queue.sortEntries()
            entry = self.ray_queue.getEntry(0)
            hit_np = entry.getIntoNodePath()
            entity = hit_np.getPythonTag("entity")
            if entity and entity.entity_type == "Asteroid":
                local_pt = entity.geom_node_path.getRelativePoint(entry.getFromNodePath(), entry.getSurfacePoint(entry.getFromNodePath()))
                entity.drill(local_pt)

    def use_tractor_beam(self, dt):
        """Vonósugár loot gyűjtéshez."""
        self.picker_ray.setOrigin(0, 0, 0)
        self.picker_ray.setDirection(0, 1, 0)
        if self.ray_queue.getNumEntries() > 0:
            for i in range(self.ray_queue.getNumEntries()):
                entry = self.ray_queue.getEntry(i)
                hit_np = entry.getIntoNodePath()
                entity = hit_np.getPythonTag("entity")
                if entity and entity.entity_type == "Loot":
                    direction = self.root.getPos() - entity.get_pos()
                    if direction.length() > 2.0:
                        entity.set_pos(entity.get_pos() + direction.normalized() * 15.0 * dt)
                    else: 
                        entity.destroy()
                        print("[SHIP] Loot collected!")

    def mount_component(self, c):
        """Alkatrész felszerelése."""
        if isinstance(c, Engine): self.engines.append(c)
        elif isinstance(c, Shield): self.shields.append(c)
        c.on_mount(self)

    def recalculate_stats(self):
        """Összesített statisztikák újraszámolása."""
        self.max_shield = sum(s.capacity for s in self.shields)
        self.current_shield = min(self.current_shield, self.max_shield)

    def take_damage(self, amount):
        """Sérüléskezelés sorrendje: Pajzs -> Hull."""
        if self.current_shield >= amount: 
            self.current_shield -= amount
        else:
            amount -= self.current_shield
            self.current_shield = 0
            self.current_hull = max(0, self.current_hull - amount)
        if self.current_hull <= 0: 
            self.destroy()

    def destroy(self):
        """Hajó megsemmisítése."""
        if self.app: 
            self.app.messenger.send(g.EVENT_SHIP_DESTROYED, [self.id])
        super().destroy()

    # --- NodePath Proxy Metódusok a MovingSystem hibáinak elkerülésére ---
    # Ez lehetővé teszi, hogy a Ship objektumot közvetlenül NodePath-ként kezeljük a mozgásnál.
    
    def setPos(self, *args):
        # Ha a MovingSystem 'target_np.setPos(target_np, ...)' formában hívja meg,
        # és 'target_np' maga a Ship objektum, akkor az első argumentum (args[0]) a Ship lesz.
        # Ezt ki kell cserélnünk a self.root NodePath-ra.
        if len(args) > 0:
            first_arg = args[0]
            if hasattr(first_arg, 'root'):
                # Cseréljük ki a wrappert a valódi NodePath-ra
                new_args = list(args)
                new_args[0] = first_arg.root
                self.root.setPos(*new_args)
                return
            elif hasattr(first_arg, 'node'):
                new_args = list(args)
                new_args[0] = first_arg.node
                self.root.setPos(*new_args)
                return
                
        self.root.setPos(*args)

    def setH(self, val): self.root.setH(val)
    def setR(self, val): self.root.setR(val)
    def setP(self, val): self.root.setP(val)
    def getH(self): return self.root.getH()
    def getR(self): return self.root.getR()
    def getP(self): return self.root.getP()
    def getPos(self): return self.root.getPos()
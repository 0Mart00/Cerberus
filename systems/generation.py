from panda3d.core import (
    Vec3, NodePath, GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, Geom, 
    GeomNode, Vec4, LVector3, ModelPool
)
import random
import math
from random import uniform
# Global variables are safe to import here
from globals import ENTITIES 


# --- Procedural Geometry Utility Functions ---

def create_box_geom():
    """Létrehoz egy 1x1x1 méretű doboz (box) geometriát vertexekből."""
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('box_data', format, Geom.UHStatic)
    
    # Vertex adatírás
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    
    # Box vertices (Egyszerűsített box a bányászati teszthez)
    v = [
        # Front face
        Vec3(-0.5, -0.5, -0.5), Vec3( 0.5, -0.5, -0.5), Vec3( 0.5,  0.5, -0.5), Vec3(-0.5,  0.5, -0.5), 
        # Back face
        Vec3(-0.5, -0.5,  0.5), Vec3( 0.5, -0.5,  0.5), Vec3( 0.5,  0.5,  0.5), Vec3(-0.5,  0.5,  0.5), 
    ]
    
    # Indexek
    idx = GeomTriangles(Geom.UHStatic)
    
    # Két háromszög per oldal (12 háromszög összesen)
    faces = [
        # Front (-Y)
        (0, 1, 2), (0, 2, 3),
        # Back (+Y)
        (5, 4, 7), (5, 7, 6),
        # Right (+X)
        (1, 5, 6), (1, 6, 2),
        # Left (-X)
        (4, 0, 3), (4, 3, 7),
        # Top (+Z)
        (3, 2, 6), (3, 6, 7),
        # Bottom (-Z)
        (4, 5, 1), (4, 1, 0)
    ]
    
    # Normálok
    normals = [
        LVector3(0, -1, 0), LVector3(0, 1, 0), LVector3(1, 0, 0), 
        LVector3(-1, 0, 0), LVector3(0, 0, 1), LVector3(0, 0, -1)
    ]
    
    for vi in v:
        vertex.addData3f(vi)
        color.addData4f(1, 1, 1, 1) # White
        
    for i, (v1, v2, v3) in enumerate(faces):
        idx.addVertices(v1, v2, v3)
        # Egyszerű normál beállítás
        normal_idx = i // 2 
        normal.addData3f(normals[normal_idx])
    
    geom = Geom(vdata)
    geom.addPrimitive(idx)
    
    node = GeomNode('box_geom_node')
    node.addGeom(geom)
    
    return NodePath(node)

def create_sphere_geom(num_segments=32, radius=1.0):
    """Létrehoz egy gömb (sphere) geometriát vertexekből."""
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('sphere_data', format, Geom.UHStatic)
    
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    
    indices = GeomTriangles(Geom.UHStatic)
    
    # A pólusok (legfelül és legalul) külön sorként vannak kezelve
    num_lat = num_segments
    num_lon = num_segments * 2 

    # Vertexi generálás (beleértve a pólusokat is)
    for i in range(num_lat + 1):
        lat = math.pi * (-0.5 + float(i) / num_lat)
        z = math.sin(lat) * radius
        r = math.cos(lat) * radius
        
        for j in range(num_lon):
            lon = 2 * math.pi * float(j) / num_lon
            x = math.cos(lon) * r
            y = math.sin(lon) * r
            
            v = Vec3(x, y, z)
            vertex.addData3f(v)
            
            n = v.normalized()
            normal.addData3f(n)
            color.addData4f(1, 1, 1, 1)

    # Indexek generálása 
    for i in range(num_lat):
        for j in range(num_lon):
            
            # Quaddrészek indexei:
            p1 = i * num_lon + j
            p2 = (i + 1) * num_lon + j
            p3 = i * num_lon + (j + 1) % num_lon
            p4 = (i + 1) * num_lon + (j + 1) % num_lon

            # Felső háromszög (kivéve a legfelső sapka)
            if i != 0:
                indices.addVertices(p1, p3, p2)
            
            # Alsó háromszög (kivéve a legalsó sapka)
            if i != num_lat - 1:
                indices.addVertices(p3, p4, p2)
    
    geom = Geom(vdata)
    geom.addPrimitive(indices)
    
    node = GeomNode('sphere_geom_node')
    node.addGeom(geom)
    
    return NodePath(node)


# --- Generátor osztályok ---
# Ezeket az osztályokat importálja az entities/entity.py, ezért kell, hogy itt legyenek.

class PlanetGenerator:
    """Generál egy Bolygó modellt (procedurális gömb)."""
    
    def generate(self, name="Exoplanet", radius=100.0, base_color=(0.1, 0.3, 0.8, 1)):
        # Procedurális gömb generálása
        planet = create_sphere_geom(num_segments=32, radius=radius)
        planet.setPos(0, 0, 0)
        planet.setName(name)
        
        planet.setColor(Vec4(*base_color))
        
        return planet

class AsteroidGenerator:
    """Generál egy aszteroida modellt (procedurális doboz/alapforma)."""
       
    def generate(self, name="Asteroid", min_scale=2.0, max_scale=5.0):
        # Procedurális doboz alapforma használata.
        asteroid = create_box_geom() 
        asteroid.setName(name)

        # Véletlenszerű méret és forma
        scale_x = random.uniform(min_scale, max_scale)
        scale_y = random.uniform(min_scale, max_scale)
        scale_z = random.uniform(min_scale, max_scale)
        asteroid.setScale(scale_x, scale_y, scale_z)
        
        # Grafit/szürke szín
        asteroid.setColor(random.uniform(0.3, 0.5), random.uniform(0.3, 0.5), random.uniform(0.3, 0.5), 1)
        
        return asteroid

    def apply_mining_hit(self, asteroid_model, hit_pos):
        """Szimulálja a bányászat hatását a modellre (vizuális változás)."""
        
        # Helyi koordinátákra konvertálás
        # A 'render' globalisan elérhető a ShowBase inicializálása után.
        local_hit_pos = asteroid_model.getRelativePoint(render, hit_pos) 
        
        # NodePath létrehozása a gödör szimulációhoz (procedurális box)
        dark_spot = create_box_geom()

        dark_spot.reparentTo(asteroid_model)
        dark_spot.setScale(0.1) # Kicsi lyuk
        dark_spot.setPos(local_hit_pos)
        dark_spot.setColor(0.2, 0.1, 0.05, 1) # Sötét, égett szín (kátrány)
        
        return True

# --- GENERATION SYSTEM ---

class GenerationSystem:
    def __init__(self, game):
        self.game = game
        self.celestial_counter = 0

    def get_celestial_class(self, entity_type):
        """Dynamically imports and returns the correct Celestial subclass."""
        # Fixes circular import issue by importing inside a function/method
        from entities.celestial import Asteroid, Wreck, Stargate, Planet
        
        class_map = {
            "Asteroid": Asteroid,
            "Wreck": Wreck,
            "Stargate": Stargate,
            "Planet": Planet
        }
        
        return class_map.get(entity_type, None)

    def generate_celestial(self, entity_type, position, scale, color):
        """Létrehoz egy égi objektumot és hozzáadja a globális listához."""
        
        CelestialClass = self.get_celestial_class(entity_type)
        
        if CelestialClass is None:
            # Visszaesés a Generic Celestialre, ha a Celestial főosztályt importáltuk volna
            print(f"[ERROR] Unknown celestial entity type: {entity_type}")
            return None
            
        uid = f"CELESTIAL_{self.celestial_counter}"
        self.celestial_counter += 1
        
        # Objektum létrehozása
        # Megjegyzés: A CelestialClass konstruktora most már nem várja a 'color' argumentumot,
        # mert a Celestial alosztályok maguk állítják be a modellt és a színt a generátorral.
        celestial = CelestialClass(
            self.game,
            uid,
            name=f"{entity_type} {self.celestial_counter}",
            # A többi paramétert (pos, scale, color) az alosztály konstruktora fogja beállítani
        )
        
        # Mivel a generátorok a konstruktorban futnak, itt csak a pozíciót állítjuk be
        celestial.set_pos(position.x, position.y, position.z)
        
        # Hozzáadjuk a globális entitás listához
        ENTITIES[uid] = celestial
        
        return celestial

    def generate_solar_system(self):
        """Egyszerű teszt naprendszer generálása."""
        print("[GENERATION] Naprendszer generálása...")
        
        # 1. Csillagkapu (Stargate)
        self.generate_celestial(
            "Stargate",
            Vec3(5000, 0, 0),
            Vec3(50),
            (0.5, 0.5, 1.0, 1.0)
        )

        # 2. Aszteroidák (20 darab)
        for i in range(20):
            pos = Vec3(uniform(-1000, 1000), uniform(-1000, 1000), uniform(-100, 100))
            scale = Vec3(uniform(5, 20))
            color = (0.7, 0.7, 0.7, 1.0)
            self.generate_celestial(
                "Asteroid",
                pos,
                scale,
                color
            )
        
        print("[GENERATION] Generálás befejezve.")
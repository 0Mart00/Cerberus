from panda3d.core import (
    Vec3, NodePath, GeomVertexFormat, GeomVertexData, GeomVertexWriter, 
    GeomTriangles, Geom, GeomNode, LVector3, Vec4
)
import math
import random

# --- Alacsony szintű procedurális geometria generátorok ---

def create_box_geom():
    """Létrehoz egy 1x1x1 méretű doboz (box) geometriát vertexekből."""
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('box_data', format, Geom.UHStatic)
    
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    
    v = [
        # Front face
        Vec3(-0.5, -0.5, -0.5), Vec3( 0.5, -0.5, -0.5), Vec3( 0.5,  0.5, -0.5), Vec3(-0.5,  0.5, -0.5), 
        # Back face
        Vec3(-0.5, -0.5,  0.5), Vec3( 0.5, -0.5,  0.5), Vec3( 0.5,  0.5,  0.5), Vec3(-0.5,  0.5,  0.5), 
    ]
    
    idx = GeomTriangles(Geom.UHStatic)
    faces = [
        (0, 1, 2), (0, 2, 3), # Elöl
        (5, 4, 7), (5, 7, 6), # Hátul
        (1, 5, 6), (1, 6, 2), # Jobb
        (4, 0, 3), (4, 3, 7), # Bal
        (3, 2, 6), (3, 6, 7), # Fent
        (4, 5, 1), (4, 1, 0)  # Lent
    ]
    
    normals = [
        LVector3(0, -1, 0), LVector3(0, 1, 0), LVector3(1, 0, 0), 
        LVector3(-1, 0, 0), LVector3(0, 0, 1), LVector3(0, 0, -1)
    ]
    
    for vi in v:
        vertex.addData3f(vi)
        color.addData4f(1, 1, 1, 1) # Alapértelmezett fehér szín
        
    for i, (v1, v2, v3) in enumerate(faces):
        idx.addVertices(v1, v2, v3)
        # Egyszerű normál hozzárendelés (minden face-hez 2 háromszög tartozik)
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
    num_lat, num_lon = num_segments, num_segments * 2 

    for i in range(num_lat + 1):
        lat = math.pi * (-0.5 + float(i) / num_lat)
        z, r = math.sin(lat) * radius, math.cos(lat) * radius
        for j in range(num_lon):
            lon = 2 * math.pi * float(j) / num_lon
            v = Vec3(math.cos(lon) * r, math.sin(lon) * r, z)
            vertex.addData3f(v)
            normal.addData3f(v.normalized())
            color.addData4f(1, 1, 1, 1)

    for i in range(num_lat):
        for j in range(num_lon):
            p1, p2 = i * num_lon + j, (i + 1) * num_lon + j
            p3, p4 = i * num_lon + (j + 1) % num_lon, (i + 1) * num_lon + (j + 1) % num_lon
            if i != 0: indices.addVertices(p1, p3, p2)
            if i != num_lat - 1: indices.addVertices(p3, p4, p2)
    
    geom = Geom(vdata)
    geom.addPrimitive(indices)
    node = GeomNode('sphere_geom_node')
    node.addGeom(geom)
    return NodePath(node)


# --- Játékobjektum Generátor Osztályok ---

class PlanetGenerator:
    """Bolygó modellek generátora (a fenti gömb geometriát használja)."""
    def generate(self, name="Exoplanet", radius=100.0, base_color=(0.1, 0.3, 0.8, 1)):
        planet = create_sphere_geom(num_segments=32, radius=radius)
        planet.setName(name)
        planet.setColor(Vec4(*base_color))
        return planet

class AsteroidGenerator:
    """Aszteroida modellek generátora (a fenti doboz geometriát használja)."""
    def generate(self, name="Asteroid", min_scale=2.0, max_scale=5.0):
        asteroid = create_box_geom() 
        asteroid.setName(name)
        # Véletlenszerű torzítás a természetesebb hatásért
        scale_x = random.uniform(min_scale, max_scale)
        scale_y = random.uniform(min_scale, max_scale)
        scale_z = random.uniform(min_scale, max_scale)
        asteroid.setScale(scale_x, scale_y, scale_z)
        # Sötétszürke szín beállítása
        asteroid.setColor(random.uniform(0.3, 0.5), random.uniform(0.3, 0.5), random.uniform(0.3, 0.5), 1)
        return asteroid

    def apply_mining_hit(self, asteroid_model, hit_pos, render_node):
        """Vizualizálja a bányászati találatot az aszteroidán."""
        local_hit_pos = asteroid_model.getRelativePoint(render_node, hit_pos) 
        dark_spot = create_box_geom()
        dark_spot.reparentTo(asteroid_model)
        dark_spot.setScale(0.1)
        dark_spot.setPos(local_hit_pos)
        dark_spot.setColor(0.2, 0.1, 0.05, 1) # Égett hatás
        return True
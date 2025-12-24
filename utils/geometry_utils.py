from panda3d.core import (
    Vec3, NodePath, GeomVertexFormat, GeomVertexData, GeomVertexWriter, 
    GeomTriangles, Geom, GeomNode, LVector3, Vec4, GeomVertexRewriter
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


# --- Játékobjektum Generátor Osztályok (2x méretekkel) ---

class PlanetGenerator:
    """Bolygó modellek generátora."""
    # Itt a radius 100.0-ról 200.0-ra lett növelve
    def generate(self, name="Exoplanet", radius=200.0, base_color=(0.1, 0.3, 0.8, 1)):
        planet = create_sphere_geom(num_segments=32, radius=radius)
        planet.setName(name)
        planet.setColor(Vec4(*base_color))
        return planet



class AsteroidGenerator:
    """
    Procedurális aszteroida háló generátor az Asteroids3.py alapján.
    """
    @staticmethod
    def generate_asteroid_mesh(segments=12, scale_var=0.5):
        """
        Létrehoz egy egyedi, torzított gömböt aszteroidának.
        """
        format = GeomVertexFormat.getV3n3t2()
        vdata = GeomVertexData('asteroid', format, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        
        # Gömb koordináták alapján generálunk pontokat
        for i in range(segments + 1):
            phi = math.pi * i / segments
            for j in range(segments + 1):
                theta = 2 * math.pi * j / segments
                
                # Alap gömb pont
                x = math.sin(phi) * math.cos(theta)
                y = math.sin(phi) * math.sin(theta)
                z = math.cos(phi)
                
                # Véletlenszerű torzítás (Asteroids3.py logika)
                noise = 1.0 + random.uniform(-scale_var, scale_var)
                pos = Vec3(x, y, z) * noise
                
                vertex.addData3f(pos)
                normal.addData3f(pos.normalized())
                texcoord.addData2f(j / segments, i / segments)

        # Háromszögek összeállítása
        tris = GeomTriangles(Geom.UHStatic)
        for i in range(segments):
            for j in range(segments):
                v1 = i * (segments + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (segments + 1) + j
                v4 = v3 + 1
                tris.addVertices(v1, v3, v2)
                tris.addVertices(v2, v3, v4)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        
        node = GeomNode('asteroid_geom')
        node.addGeom(geom)
        return node

    @staticmethod
    def deform_asteroid(geom_node, local_point, radius=0.3, strength=0.15):
        """
        Kráter képzése a becsapódás helyén.
        """
        for i in range(geom_node.getNumGeoms()):
            geom = geom_node.modifyGeom(i)
            vdata = geom.modifyVertexData()
            vertex = GeomVertexRewriter(vdata, 'vertex')
            
            while not vertex.isAtEnd():
                v = vertex.getData3f()
                dist = (v - local_point).length()
                
                if dist < radius:
                    falloff = (radius - dist) / radius
                    # A belseje felé toljuk a csúcsot (0,0,0 irányba)
                    # De csak egy kicsit, hogy ne lyukadjon át
                    direction_to_center = v.normalized()
                    new_v = v - (direction_to_center * strength * falloff)
                    
                    # Megtartjuk a minimális vastagságot
                    if new_v.length() < 0.2:
                        new_v = direction_to_center * 0.2
                        
                    vertex.setData3f(new_v)
import os
from get_settings import get_settings

def parse_data(mesh):
    """Parse an OBJ file for mesh data."""
    settings = get_settings()

    vertices = []
    faces = []
    normals = []

    for line in mesh:
        if line[:2] == "v ":
            vertice = parse_vector(line[2:])
            vertices.append(vertice)
        elif line[:2] == "f ":
            face = parse_faces(line[2:])
            faces.append(face)
        elif line[:3] == "vn ":
            normal = parse_vector(line[3:])
            normals.append(normal)

    origin = get_origin(vertices)

    mesh_data = {"verts": vertices,
                 "faces": faces,
                 "normals": normals,
                 "origin": origin}

    return mesh_data

def parse_vector(line):
    """Get the x, y, z values in the line."""
    x, y, z = line.strip().split(" ")
    x, y, z = float(x), float(y), float(z)
    return x, y, z

def parse_faces(line):
    """Get face and edge information from a line."""
    face = []
    normal = None
    for vert in line.split(" "):
        vert_i, norm_i = vert.split("//")
        face.append(int(vert_i) - 1)
        normal = int(norm_i) - 1

    return (face, normal)

def get_origin(vertices):
    """Get the center point of a mesh."""
    x_max = 0
    x_min = 0
    y_max = 0
    y_min = 0
    z_max = 0
    z_min = 0

    for vert in vertices:
        x, y, z = vert

        x_max = max(x_max, x)
        x_min = max(x_min, x)

        y_max = max(y_max, y)
        y_min = max(y_min, y)

        z_max = max(z_max, z)
        z_min = max(z_min, z)

    x = (x_max + x_min) / 2
    y = (y_max + y_min) / 2
    z = (z_max + z_min) / 2

    return x, y, z

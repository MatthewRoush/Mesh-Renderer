import json
from get_settings import get_settings

def main():
    """Parse an .OBJ file for mesh data."""
    settings = get_settings()
    # The key for the mesh data.
    mesh_name = settings["mesh"].title()

    vertices = ""
    faces = ""
    normals = ""

    folder = settings["folder_path"]
    with open(f"{folder}/{mesh_name.lower()}.obj", "r") as f:
        lines = f.readlines()

    for line in lines:
        if line[0:2] == "v ":
            vertices += line
        elif line[0:2] == "f ":
            faces += line
        elif line[0:3] == "vn ":
            normals += line

    verts = parse_vertices(vertices)
    faces = parse_faces(faces)
    normals = parse_normals(normals)
    face_coords = parse_face_coords(faces, verts)

    if settings["print_vertices"]:
        print("Vertices\n", verts, "\n")
    if settings["print_edges"]:
        print("Edges\n", edges, "\n")
    if settings["print_faces"]:
        print("Faces\n", faces, "\n")
    if settings["print_face_coords"]:
        print("Face Coords\n", faces, "\n")
    if settings["print_normals"]:
        print("Normals\n", normals)

    #print(len(normals), len(faces))

    with open("meshes.json", "r") as f:
        mesh_data = json.load(f)

    mesh_data[mesh_name] = {"verts": verts,
                            "faces": faces,
                            "face_coords": face_coords,
                            "normals": normals}

    with open("meshes.json", "w") as f:
        json.dump(mesh_data, f)

def parse_vertices(string):
    vert_matrix = []
    string = string.replace("v ", "")
    string = string.split("\n")
    string = string[:-1]
    for i, coord in enumerate(string):
        num_coord = []
        coord = coord.split(" ")
        vert_matrix.append([float(x) for x in coord])

    return vert_matrix

def parse_faces(string):
    face_matrix = []
    string = string.replace("f ", "")
    string = string.split("\n")
    string = string[:-1]
    for face in string:
        face = face.split(" ")
        vert_list = []
        for vert in face:
            vert_list.append(int(vert.split("//")[0])-1)

        face_matrix.append(vert_list)

    return face_matrix

def parse_normals(string):
    normal_matrix = []
    string = string.replace("vn ", "")
    string = string.split("\n")
    string = string[:-1]
    for normal in string:
        normal = normal.split(" ")
        normal_matrix.append([float(x) for x in normal])

    return normal_matrix

def parse_face_coords(faces, verts):
    face_coords_matrix = []

    for f in faces: # For face in faces.
        coords = []
        for i, p in enumerate(f): # For point in face.
            if i != len(f)-1:
                x = (verts[f[i+1]][0] + verts[p][0]) / 2 
                y = (verts[f[i+1]][1] + verts[p][1]) / 2
                z = (verts[f[i+1]][2] + verts[p][2]) / 2
            else:
                x = (verts[f[0]][0] + verts[p][0]) / 2 
                y = (verts[f[0]][1] + verts[p][1]) / 2
                z = (verts[f[0]][2] + verts[p][2]) / 2
            
            coords.append([x, y, z])

        minX = maxX = coords[0][0]
        minY = maxY = coords[0][1]
        minZ = maxZ = coords[0][2]
        for p in coords:
            minX = min(minX, p[0])
            maxX = max(maxX, p[0])
            minY = min(minY, p[1])
            maxY = max(maxY, p[1])
            minZ = min(minZ, p[2])
            maxZ = max(maxZ, p[2])

        x = (maxX + minX) / 2
        y = (maxY + minY) / 2
        z = (maxZ + minZ) / 2
        face_coords_matrix.append([x, y, z])

    return face_coords_matrix

if __name__ == '__main__':
    main()

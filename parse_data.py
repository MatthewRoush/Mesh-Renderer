import json
from get_settings import get_settings

def main():
    """Parse an .OBJ file for mesh data."""
    settings = get_settings()
    # The key for the mesh data.
    mesh_name = settings["mesh"]

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
    faces, edges = parse_faces(faces)
    normals = parse_normals(normals)

    if settings["print_vertices"]:
        print("Vertices\n", verts, "\n")
    if settings["print_edges"]:
        print("Edges\n", edges, "\n")
    if settings["print_faces"]:
        print("Faces\n", faces, "\n")
    if settings["print_normals"]:
        print("Normals\n", normals)

    #print(len(normals), len(faces))

    with open("meshes.json", "r") as f:
        mesh_data = json.load(f)

    mesh_data[mesh_name] = {"verts": verts,
                            "edges": edges,
                            "faces": faces,
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
    face_matrix, edge_matrix = [], []
    string = string.replace("f ", "")
    string = string.split("\n")
    string = string[:-1]
    for face in string:
        face = face.split(" ")
        vert_list = []
        for vert in face:
            vert_list.append(int(vert.split("//")[0])-1)

        face_matrix.append(vert_list)

        for i, v in enumerate(vert_list):
            if i == len(vert_list)-1:
                edge = [v, vert_list[0]]
            else:
                edge = [v, vert_list[i+1]]

            if [edge[1], edge[0]] not in edge_matrix:
                edge_matrix.append(edge)

    return face_matrix, edge_matrix

def parse_normals(string):
    normal_matrix = []
    string = string.replace("vn ", "")
    string = string.split("\n")
    string = string[:-1]
    for normal in string:
        normal = normal.split(" ")
        normal_matrix.append([float(x) for x in normal])

    return normal_matrix

if __name__ == '__main__':
    main()

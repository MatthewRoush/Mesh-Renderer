# Mesh-Renderer

Render meshes in a very crude manner.

## Dependencies
This program uses [pygame](https://pypi.org/project/pygame/) for graphics.

## How To Use

1. Save a mesh as an `.obj` file. Make sure you save it with vertex, face, and normal information.

2. Set the `mesh` key in `settings.cfg` to the filename of the `.obj` file.

3. Run the `parse_data.py` script. This will dump the vertex, edge, face, and normal data of the mesh to `meshes.json` to a key with the same name as the `mesh` key in `settings.cfg`.

4. Now you can run the `render_mesh.py` script to render the mesh.

## Controls

Hold left click and drag to tilt the mesh.

Hold right click and drag to move the light.

The Escape key and the close button of the window will exit the program

***Note: `render_mesh.py` needs to be refined, expect bugs and weird behavior.***

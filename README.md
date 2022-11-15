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

Hold right click and drag to move the light.

The Escape key and the close button of the window will exit the program

***Note: I made this without looking up how to actually do things like calculate light, so it's not very good. This was just an idea I had so I did it.***

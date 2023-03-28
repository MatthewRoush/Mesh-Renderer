# Mesh-Renderer

Render meshes and hope for the best.

## Dependencies

[pygame](https://pypi.org/project/pygame/) for graphics.

[numpy](https://pypi.org/project/numpy/) for data structures.

## How To Use

1. (For Blender) Export a mesh as an `.obj` file with the "Normals" option checked.

2. Provide the path to that mesh as the argument to `render_mesh.py`

## Controls

Hold left click and drag to tilt the mesh.

Hold right click and drag to move the light.

The Escape key closes the program.

***Note: Faces will draw even if they are obscured, this isn't meant to be a full proper rendering engine.***

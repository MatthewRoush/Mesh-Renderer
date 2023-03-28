import os
import sys
import math
import argparse
import numpy as np
import pygame as pg
from pygame import gfxdraw
from get_settings import get_settings
from parse_data import parse_data

def main():
    """Make a crude rendering engine."""
    global settings
    global viewport, light_source, light_brightness
    global xmod, ymod

    settings = get_settings()

    parser = argparse.ArgumentParser(
        prog = "render_mesh.py",
        description = "Render a mesh.")

    parser.add_argument("path",
                        help=("The path to a parse_data.py output file."))

    args = parser.parse_args()
    path = args.path

    if not os.path.exists(path):
        print("Path does not exist.")
        return

    # Do pygame stuff.
    pg.init()
    clock = pg.time.Clock()
    pg.event.set_allowed([ # Set the allowed events.
        pg.QUIT,
        pg.MOUSEBUTTONDOWN,
        pg.MOUSEBUTTONUP,
        pg.KEYDOWN
    ])

    screen = pg.display.set_mode(settings["window_size"], pg.NOFRAME)
    screen_rect = screen.get_rect()
    screen_width = screen_rect.width
    screen_height = screen_rect.height

    bg_color = settings["background_color"]

    with open(path, "r", encoding="UTF-8") as f:
        mesh = f.readlines()

    mesh = parse_data(mesh)

    # The mesh to render
    vertices = np.array(mesh["verts"])
    faces = np.array(mesh["faces"], dtype=object)
    normals = np.array(mesh["normals"])
    origin = np.array(mesh["origin"])

    xmod = screen_rect.centerx - origin[0]
    ymod = screen_rect.centery - origin[1]
    origin[0] += xmod
    origin[1] += ymod

    scale = settings["scale"]
    for vertex in vertices:
        vertex[0] *= scale
        vertex[1] *= scale
        vertex[2] *= scale

    active = True # Flag for the main loop.
    viewport = [0, 0, 1] # Camera position.
    # +X = right, -X = left, +Y = up, -Y = down, +Z = back, -Z = forward
    light_source = settings["light_coordinates"]
    light_brightness = settings["light_brightness"]
    light_col = settings["light_color"]
    move_light_incr = 0.05

    vertices = vertices.transpose()
    normals = normals.transpose()

    rot = 0
    tilt = 0

    lmb_hold = False
    rmb_hold = False
    prev_mouse_pos = (0, 0)

    screen.fill(bg_color) # Fill the background.

    while active:
        clock.tick(60) # Limit to 60 FPS.
        mouse_pos = pg.mouse.get_pos() # Get the position of the mouse.

        for event in pg.event.get():
            if event.type == pg.QUIT: # If the window quits.
                active = False # Close the program.
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    active = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmb_hold = True
                elif event.button == 3:
                    rmb_hold = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    lmb_hold = False
                elif event.button == 3:
                    rmb_hold = False

        if mouse_pos[0] - prev_mouse_pos[0] > 0:
            light_move_x = move_light_incr
        elif mouse_pos[0] - prev_mouse_pos[0] < 0:
            light_move_x = -move_light_incr
        else:
            light_move_x = 0

        if mouse_pos[1] - prev_mouse_pos[1] > 0:
            tilt_dir = 1
            light_move_y = move_light_incr
        elif mouse_pos[1] - prev_mouse_pos[1] < 0:
            tilt_dir = -1
            light_move_y = -move_light_incr
        else:
            tilt_dir = 0
            light_move_y = 0

        if lmb_hold:
            tilt += settings["rotation_speed"] * tilt_dir * 2

        if rmb_hold:
            light_source[0] += light_move_x
            light_source[1] += light_move_y

        rot += settings["rotation_speed"]

        verts = np.matmul(rot_tilt(rot, tilt), vertices).transpose()
        norms = np.matmul(rot_tilt(rot, tilt), normals).transpose()

        screen.fill(settings["background_color"])
        render_mesh(screen, verts, faces, norms)

        # Draw origin
        if settings["render_origin"]:
            x, y, z = origin
            s = settings["origin_size"]
            c = settings["origin_color"]
            gfxdraw.filled_circle(screen, int(x), int(y), s, c)

        prev_mouse_pos = mouse_pos
        pg.display.flip()

    pg.quit() # Quit pygame.
    sys.exit() # Exit the program.

def render_mesh(screen, verts, faces, norms):
    """Render the mesh."""
    for i, face in enumerate(faces):
        vert_i, norm_i = face

        projected = project(norms[norm_i], viewport)

        vec1 = as_spherical(projected)
        vec2 = as_spherical(viewport)

        # Check if the front of the face is visible.
        if vec1[1:] == vec2[1:]:
            points = []
            for index in vert_i:
                points.append([
                    verts[index][0] + xmod,
                    verts[index][1] + ymod])

            point = np.array(points)

            # Draw the face
            if settings["render_mesh"]:
                vec3 = as_spherical(project(norms[norm_i], light_source))
                vec4 = as_spherical(light_source)

                dist = distance(norms[norm_i], light_source)
                light = dist * light_brightness

                r, g, b = [calc_lighting(k, light) for k in range(3)]

                gfxdraw.filled_polygon(screen, points, (r, g, b))

            for k, point in enumerate(points):
                p1 = (int(point[0]), int(point[1]))
                if k != len(points)-1:
                    p2 = (int(points[k+1][0]), int(points[k+1][1]))
                else:
                    p2 = (int(points[0][0]), int(points[0][1]))

                # Draw edges.
                if settings["render_edges"]:
                    gfxdraw.line(screen, *p1, *p2, settings["edge_color"])

                # Draw vertices.
                if settings["render_vertices"]:
                    s = settings["vertice_size"]
                    c = settings["vertice_color"]
                    gfxdraw.filled_circle(screen, *p1, s, c)
                    gfxdraw.filled_circle(screen, *p2, s, c)

def magnitude(v):
    """Return the magnitude of a 3D vector."""
    x, y, z = v
    return math.sqrt(x*x + y*y + z*z)

def distance(v1, v2):
    part_sum = 0
    for i in range(3):
        diff = v2[i] - v1[i]
        part_sum += diff * diff

    return 1 / (part_sum * part_sum)

def dot_prod(v1, v2):
    """Return the dot product of two 3D vectors."""
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return x1*x2 + y1*y2 + z1*z2

def project(v1, v2):
    """Return a projected 3D vector."""
    dot = dot_prod(v1, v2)
    mag = magnitude(v2)
    normalized = (v2[0] / mag, v2[1] / mag, v2[2] / mag)
    dot_mag = dot / mag
    v3 = np.array([normalized[0]*dot_mag, 
                   normalized[1]*dot_mag,
                   normalized[2]*dot_mag])

    return v3

def as_spherical(v):
    """Return the spherical components of a 3D vector."""
    mag = magnitude(v)
    if mag == 0:
        return [0, 0, 0]
    theta = math.degrees(math.acos(v[2]/mag))
    phi = math.degrees(math.atan2(v[1], v[0]))
    return (mag, theta, phi)

def rot_tilt(rot, tilt):
    """Return rotation matrices for 3D vectors."""
    rot_matrix = np.array([[math.cos(rot), 0.0, math.sin(rot)],
                           [0.0, 1.0, 0.0],
                           [-math.sin(rot), 0.0, math.cos(rot)]
                        ])

    tilt_matrix = np.array([[1.0, 0.0, 0.0],
                            [0.0, math.cos(tilt), math.sin(tilt)],
                            [0.0, -math.sin(tilt), math.cos(tilt)]
                        ])
    
    return np.matmul(rot_matrix, tilt_matrix)

def calc_lighting(channel, light):
    """Calculate the lighting for a color channel."""
    return clamp(settings["background_color"][channel] +
                 settings["mesh_color"][channel] *
                 (settings["light_color"][0] / 255) *
                 light)

def clamp(num):
    """Make sure the provided number is within 0 to 255."""
    if num < 0:
        return 0
    elif num > 255:
        return 255
    else:
        return num

if __name__ == "__main__":
    main()

# Import required libraries.
import sys
import math
import json
import pygame as pg
from pygame import gfxdraw
from get_settings import get_settings

def main():
    """Make a crude rendering engine."""
    global settings
    global viewport, light_source, light_brightness
    global xmod, ymod

    settings = get_settings()

    # Do pygame stuff.
    pg.init()
    clock = pg.time.Clock()
    pg.event.set_allowed([ # Set the allowed events.
        pg.QUIT,
        pg.VIDEOEXPOSE,
        pg.MOUSEBUTTONDOWN,
        pg.MOUSEBUTTONUP,
        pg.KEYDOWN
    ])

    screen = pg.display.set_mode(settings["window_size"])
    screen_rect = screen.get_rect()
    screen_width = screen_rect.width
    screen_height = screen_rect.height

    screen_diagonal = math.sqrt(screen_rect.w**2 + screen_rect.h**2)

    bg_color = settings["background_color"]

    with open("meshes.json", "r") as f:
        meshes = json.load(f)

    # The mesh to render
    mesh = settings["mesh"].title()
    vertices = meshes[mesh]["verts"]
    faces = meshes[mesh]["faces"]
    edges = meshes[mesh]["edges"]
    normals = meshes[mesh]["normals"]

    minX, maxX = vertices[0][0], vertices[0][0]
    minY, maxY = vertices[0][1], vertices[0][1]
    minZ, maxZ = vertices[0][2], vertices[0][2]
    scale = settings["scale"] * (screen_diagonal/2200)
    for i, vertex in enumerate(vertices):
        vertices[i][0] *= scale
        vertices[i][1] *= scale
        vertices[i][2] *= scale

        minX = min(minX, vertices[i][0])
        maxX = max(maxX, vertices[i][0])
        minY = min(minY, vertices[i][1])
        maxY = max(maxY, vertices[i][1])
        minZ = min(minZ, vertices[i][2])
        maxZ = max(maxZ, vertices[i][2])

    origin = [(maxX+minX)/2, (maxY+minY)/2, (maxZ+minZ)/2]

    active = True # Flag for the main loop.
    viewport = [0, 0, -20]
    # X = left, -X = right, Y = up, -Y = down, Z = forward, -Z = back
    light_source = settings["light_coordinates"]
    light_brightness = settings["light_brightness"]
    bounding_rect = pg.Rect(0, 0, 1, 1)
    rendered_text_rect = pg.Rect(0, 0, 1, 1)
    vertices = transpose(vertices)
    normals = transpose(normals)

    rot = 0 #(mouse_pos[0] / screen_width) * math.tau
    tilt = 0 #(mouse_pos[1] / screen_height) * math.tau

    lmb_hold = False
    rmb_hold = False
    prev_mouse_pos = (0, 0)
    xmod = screen_rect.centerx - origin[0] + settings["adjust_mesh_x"]
    ymod = screen_rect.centery - origin[1] + settings["adjust_mesh_y"]
    origin[0] += xmod
    origin[1] += ymod

    screen.fill(bg_color) # Fill the background.

    while active:
        clock.tick(settings["fps"]) # Limit to 60 FPS.
        dirty_rects = [] # Empty the rect update list.
        mouse_pos = pg.mouse.get_pos() # Get the position of the mouse.

        for event in pg.event.get():
            if event.type == pg.QUIT: # If the window quits.
                active = False # Close the program.
            elif event.type == pg.VIDEOEXPOSE: # If un-minimizing the window.
                pg.display.update() # Update the screen.
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

        mouse_delta = [0, 0]
        mouse_delta = (mouse_pos[0] - prev_mouse_pos[0],
                            mouse_pos[1] - prev_mouse_pos[1])

        if lmb_hold:
            tilt += mouse_delta[1]/500

        if rmb_hold:
            light_source[0] -= mouse_delta[0]/100
            light_source[1] -= mouse_delta[1]/100

        rot += settings["rotation_speed"]

        verts = transpose(matrixMult(rottilt(rot, tilt), vertices))
        norms = transpose(matrixMult(rottilt(rot, tilt), normals, n=True))

        screen.fill(bg_color, bounding_rect)
        dirty_rects.append(bounding_rect)
        screen.fill(bg_color, rendered_text_rect)
        dirty_rects.append(rendered_text_rect)

        bounding_rect = render_mesh(screen, verts, faces, edges, norms)
        dirty_rects.append(bounding_rect)

        # Draw origin
        if settings["render_origin"]:
            x, y, z = origin
            s = settings["origin_size"]
            c = settings["origin_color"]
            gfxdraw.filled_circle(screen, int(x), int(y), s, c)

        if settings["show_fps"]:
            fps = str(int(clock.get_fps()))
            font = pg.font.Font(None, 50)
            rendered_text = font.render(str(fps), True, (255, 255, 255))
            rendered_text_rect = rendered_text.get_rect()
            screen.blit(rendered_text, rendered_text_rect)
            dirty_rects.append(rendered_text_rect)

        prev_mouse_pos = mouse_pos
        pg.display.update(dirty_rects) # Update the screen.

    pg.quit() # Quit pygame.
    sys.exit() # Exit the program.

def render_mesh(screen, verts, faces, edges, norms):
    """Graphs the points in a list using segments."""
    # Used for making an update rect.
    minX, maxX = verts[0][0], verts[0][0]
    minY, maxY = verts[0][1], verts[0][1]

    for i, f in enumerate(faces):
        projected = project(norms[i], viewport)

        angle1 = as_spherical(projected)
        angle1 = (angle1[1], angle1[2])
        angle2 = as_spherical(viewport)
        angle2 = (angle2[1], angle2[2])

        # Check if the front of the face is visible.
        if angle1 != angle2:
            v = []
            for p in f:
                v.append([verts[p][0], verts[p][1]])

            projected = project(norms[i], light_source)

            angle3 = as_spherical(projected)
            angle4 = as_spherical(light_source)

            # Gonna be honest, I don't really know what I'm doing here.
            theta_diff = angle4[1] - angle3[1]
            phi_diff = angle4[2] - angle3[2]
            theta_phi = theta_diff + phi_diff

            # Sketchy light calculation.
            r = (settings["mesh_color"][0] * angle3[0] *
                light_brightness * abs(theta_phi/400))
            g = (settings["mesh_color"][1] * angle3[0] *
                light_brightness * abs(theta_phi/400))
            b = (settings["mesh_color"][2] * angle3[0] *
                light_brightness * abs(theta_phi/400))

            # Make sure RGB values are within the proper range.
            if r < 0:
                r = 0
            elif r > 255:
                r = 255

            if g < 0:
                g = 0
            elif g > 255:
                g = 255

            if b < 0:
                b = 0
            elif b > 255:
                b = 255

            # Draw the face
            if settings["render_mesh"]:
                gfxdraw.filled_polygon(screen, v, (r, g, b))

            for k, point in enumerate(v):
                p1 = (int(point[0]), int(point[1]))
                if k != len(v)-1:
                    p2 = (int(v[k+1][0]), int(v[k+1][1]))
                else:
                    p2 = (int(v[0][0]), int(v[0][1]))

                # Draw edges.
                if settings["render_edges"]:
                    gfxdraw.line(screen, *p1, *p2, settings["edge_color"])

                # Draw vertices.
                if settings["render_vertices"]:
                    s = settings["vertice_size"]
                    c = settings["vertice_color"]
                    gfxdraw.filled_circle(screen, *p1, s, c)
                    gfxdraw.filled_circle(screen, *p2, s, c)

                minX, maxX = min(minX, point[0]), max(maxX, point[0])
                minY, maxY = min(minY, point[1]), max(maxY, point[1])

    # Extra padding for vertices.
    bounding_rect = pg.Rect(minX-3, minY-3, maxX-minX+8, maxY-minY+8)
    return bounding_rect

def mag(v):
    """return the magnitude of a 3D vector."""
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def dot(v1, v2):
    """return the dot product of two 3D vectors."""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def project(v1, v2):
    """Return a projected 3D vector."""
    dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    mag = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
    normalized = [v2[0]/mag, v2[1]/mag, v2[2]/mag]
    dot_mag = dot/mag
    v3 = [normalized[0]*dot_mag, normalized[1]*dot_mag, normalized[2]*dot_mag]

    return v3

def as_spherical(v):
    """Return the spherical components of a 3D vector."""
    mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if mag == 0:
        return [0, 0, 0]
    theta = math.degrees(math.acos(v[2]/mag))
    phi = math.degrees(math.atan2(v[1], v[0]))
    return [mag, theta, phi]

def rottilt(rot, tilt):
    """Return rotation matrices for 3D vectors."""
    rot_matrix_x = [[math.cos(rot), 0.0, math.sin(rot)],
                    [0.0, 1.0, 0.0],
                    [-math.sin(rot), 0.0, math.cos(rot)]]
    rot_matrix_y = [[1.0, 0.0, 0.0],
                    [0.0, math.cos(tilt), math.sin(tilt)],
                    [0.0, -math.sin(tilt), math.cos(tilt)]]
    
    return matrixMult(rot_matrix_y, rot_matrix_x, n=True)

def transpose(matrix):
    """Transpose the given matrix."""
    return_matrix = []
    rows = len(matrix)
    cols = len(matrix[0])
    
    for i in range(cols):
        return_matrix.append([])
        for j in range(rows):
            return_matrix[i].append(matrix[j][i])
    
    return return_matrix

def matrixMult(a, b, n=False):
    """Multiply two matrices. n is used as a flag for the mesh, False==mesh"""
    return_matrix = []

    rows = len(a)
    cols = len(b[0])

    for i in range(rows):
        row = []
        for j in range(cols):
            if not n:
                if i == 0:
                    sum1 = xmod
                elif i == 1:
                    sum1 = ymod
                else:
                    sum1 = 0
            else:
                sum1 = 0
            for k in range(len(b)):
                sum1 += a[i][k] * b[k][j]
            row.append(sum1)
        return_matrix.append(row)

    return return_matrix

# Run main() when the program is launched.
if __name__ == "__main__":
    main()

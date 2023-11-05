# /src/renderer/raycaster.py

import math

from src.utils import safe_tan, distance_two_points

PI = math.pi
BITS_TO_SHIFT = 0


def raycaster_2d(obj_angle, obj_x, obj_y, game_controller, num_rays=60):
    global BITS_TO_SHIFT

    color = (0, 1.0, 0)
    distance = 0
    rx = ry = xo = yo = 0.0
    ra = (obj_angle - math.radians(num_rays / 2) + 2 * PI) % (2 * PI)

    # Total size of the world (i.e. total number of 'squares' in the world)
    world_size = game_controller.world.world_scale

    # Calcualte shift value based on world scale
    if BITS_TO_SHIFT == 0:
        shift_value = int(math.log2(world_size))
        BITS_TO_SHIFT = shift_value
    else:
        shift_value = BITS_TO_SHIFT

    for r in range(num_rays):

        map_texture_vert = map_texture_horz = 0  # Vertical and horizontal map textures

        # --------------------------------------------
        # -------- Check Horizontal Lines ------------
        # --------------------------------------------
        dof = 0  # Depth of field (sight range)
        distance_h = math.inf
        hx, hy = obj_x, obj_y

        a_tan = -1 / math.tan(safe_tan(ra))

        e = 0.000001

        if ra > PI:  # Ray is looking up
            ry = ((int(obj_y) >> shift_value) << shift_value) - e
            rx = (obj_y - ry) * a_tan + obj_x
            yo = -64
            xo = -yo * a_tan

        if ra < PI:  # Ray is looking down
            ry = ((int(obj_y) >> shift_value) << shift_value) + 64
            rx = (obj_y - ry) * a_tan + obj_x
            yo = 64
            xo = -yo * a_tan

        if ra == 0 or ra == PI:  # Ray is looking parallel left or right (impossible to hit a horizontal wall)
            rx = obj_x
            ry = obj_y
            dof = 8

        while dof < 8:
            map_x = int(rx) >> shift_value
            map_y = int(ry) >> shift_value

            # Check if mx and my are within the bounds of the world
            if 0 <= map_x < game_controller.world.x and 0 <= map_y < game_controller.world.y:
                world_grid_index = map_y * game_controller.world.x + map_x

                # Hit a wall
                if 0 < world_grid_index < world_size * game_controller.world.y and \
                        game_controller.world.world_map_walls[
                            world_grid_index] > 0:  # noqa
                    hx, hy = rx, ry
                    distance_h = distance_two_points(obj_x, obj_y, hx, hy)
                    map_texture_horz = game_controller.world.world_map_walls[world_grid_index] - 1
                    dof = 8  # End the loop, we hit a wall
                else:  # Next line to check
                    rx += xo
                    ry += yo
                    dof += 1
            else:
                dof = 8

        # --------------------------------------------
        # -------- Check Vertical Lines --------------
        # --------------------------------------------
        dof = 0

        distance_v = math.inf
        vx, vy = obj_x, obj_y

        n_tan = -math.tan(safe_tan(ra))

        if (PI / 2) < ra < (3 * PI / 2):  # Ray is looking left
            rx = ((int(obj_x) >> shift_value) << shift_value) - e
            ry = (obj_x - rx) * n_tan + obj_y
            xo = -64
            yo = -xo * n_tan

        if ra < PI / 2 or ra > (3 * PI / 2):  # Ray is looking right
            rx = ((int(obj_x) >> shift_value) << shift_value) + 64
            ry = (obj_x - rx) * n_tan + obj_y
            xo = 64
            yo = -xo * n_tan

        if ra == 0 or ra == PI:  # Ray is looking straight up or down
            rx = obj_x
            ry = obj_y
            dof = 8

        while dof < 8:
            map_x = int(rx) >> shift_value
            map_y = int(ry) >> shift_value

            # Check if mx and my are within the bounds of the world
            if 0 <= map_x < game_controller.world.x and 0 <= map_y < game_controller.world.y:
                world_grid_index = map_y * game_controller.world.x + map_x

                # Hit a wall
                if 0 < world_grid_index < world_size and game_controller.world.world_map_walls[world_grid_index] > 0:
                    vx = rx
                    vy = ry
                    distance_v = distance_two_points(obj_x, obj_y, vx, vy)
                    map_texture_vert = game_controller.world.world_map_walls[world_grid_index] - 1
                    break

                else:
                    rx += xo
                    ry += yo
                    dof += 1

            else:
                break  # Exit the loop if we are out of bounds

        shade = 1.0
        # Vertical wall hit
        if distance_v < distance_h:
            # Set the color to be darker
            map_texture_horz = map_texture_vert
            shade = 0.5
            color = (0.62, 0.125, 0.941)
            # color = (0, 1, 0)
            rx = vx
            ry = vy
            distance = distance_v
        # Horizontal wall hit
        elif distance_h < distance_v:
            # Set the color to be lighter
            color = (0.52, 0.115, 0.931)
            rx = hx
            ry = hy
            distance = distance_h

        yield r, ra, rx, ry, distance, color, shade, map_texture_horz

        ra += math.radians(1)
        if ra < 0:
            ra += 2 * PI
        if ra > 2 * PI:
            ra -= 2 * PI

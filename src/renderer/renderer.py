# /src/renderer/renderer.py

import math
import time
import pprint

from collections import deque

from math import pi as PI  # noqa

from OpenGL.GL import *
from OpenGL.GLUT import *

from src.renderer.textures import ALL_TEXTURES
from src.renderer.raycaster import raycaster_2d


class Renderer:
    def __init__(self, game_controller, window_width, window_height, fps_callback=None):
        self.controller = game_controller
        self.last_frame_time = time.time()
        self.fps_list = deque(maxlen=15)
        self.display_fps = True
        self.fps_callback = fps_callback
        self.textures = ALL_TEXTURES

        # Window / screen dimensions
        self.window_width = window_width
        self.window_height = window_height

        print(f'Window width: {self.window_width}, Window height: {self.window_height}')

        # Precompute and cache vertices
        self.cached_vertices = self.precompute_vertices()

        # 3D world drawing offsets
        self.world_draw_offset_x = (self.window_width // 2) + 3  # Draw in center x of screen offset slightly right
        self.world_draw_offset_y = self.window_height // 4  # We want to start drawing the y from 1/4 of the screen

    def get_current_fps(self):
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time

        fps = (int(1 / delta_time)) if delta_time > 0 else 0
        self.fps_list.append(fps)

        average_fps = sum(self.fps_list) // len(self.fps_list)

        # Call the callback function if it is set
        if self.fps_callback:
            self.fps_callback(average_fps, delta_time)

        return average_fps

    def precompute_vertices(self):
        vertices = []
        border_thickness = 1
        print(f'\nComputing vertices...')
        pp = pprint.PrettyPrinter(indent=4)
        
        for y in range(self.controller.world.map_grid_size_y):
            for x in range(self.controller.world.map_grid_size_x):
                is_wall = self.controller.world.map_grid_walls[y * self.controller.world.map_grid_size_x + x] > 0

                x_offset = x * self.controller.world.map_grid_size
                y_offset = y * self.controller.world.map_grid_size

                # Slightly smaller coordinates for drawing the quad
                v1 = (x_offset + border_thickness, y_offset + border_thickness)
                v2 = (x_offset + border_thickness, y_offset + self.controller.world.map_grid_size - border_thickness)
                v3 = (x_offset + self.controller.world.map_grid_size - border_thickness,
                      y_offset + self.controller.world.map_grid_size - border_thickness)
                v4 = (x_offset + self.controller.world.map_grid_size - border_thickness, y_offset + border_thickness)

                print(f'\nPos: ({x}, {y})')
                pp.pprint(({
                    'is_wall': is_wall,
                    'v1': v1,
                    'v2': v2,
                    'v3': v3,
                    'v4': v4
                }))

                vertices.append((is_wall, v1, v2, v3, v4))

        print(f'\nVertices computed: {len(vertices)}')
        return vertices

    def draw_world_2d(self):
        glBegin(GL_QUADS)
        for is_wall, v1, v2, v3, v4 in self.cached_vertices:
            glColor3f(1, 1, 1) if is_wall else glColor3f(0, 0, 0)
            glVertex2i(*v1)
            glVertex2i(*v2)
            glVertex2i(*v3)
            glVertex2i(*v4)
        glEnd()

    def draw_rays_2d(self):
        player_angle = self.controller.player.angle
        player_x = self.controller.player.map_grid_size_x
        player_y = self.controller.player.map_grid_size_y

        for r, ra, rx, ry, distance, color, shade, map_texture_pos in raycaster_2d(player_angle,
                                                                                   player_x,
                                                                                   player_y,
                                                                                   self.controller,
                                                                                   num_rays=self.controller.player.FOV):
            # Draw the rays being cast
            glColor3f(0.8, 0, 0)  # Red
            glLineWidth(1)
            glBegin(GL_LINES)
            glVertex2i(int(player_x), int(player_y))
            glVertex2i(int(rx), int(ry))
            glEnd()

            self.draw_world_3d(distance, r, player_angle, ra, color, shade, map_texture_pos, rx=rx, ry=ry)

            # Store the ray data for 3D drawing
            # self.ray_data.append((distance, r, player_angle, rx))

    def draw_world_3d(self, ray_distance, ray_n, pa, ra, color, shade, map_texture_pos, rx, ry, world_height=400,
                      world_width=400):

        horizontal_offset = (self.window_width - world_width) // 2
        vertical_offset = (self.window_height - world_height) // 2

        print(f'Horizontal offset: {horizontal_offset}, Vertical offset: {vertical_offset}')

        # Horizontal offset: 352.0, Vertical offset: 176.0

        cosine_angle = (pa - ra + 2 * PI) % (
                2 * PI)  # player_angle - ray_angle, also bounds the values between 0 and 2 * PI noqa
        # Fisheye effect fix (see: https://lodev.org/cgtutor/raycasting.html)
        ray_distance = ray_distance * math.cos(cosine_angle)
        if ray_distance == 0:  # Prevent division by zero
            ray_distance = sys.float_info.min

        line_height = (self.controller.world.map_grid_size * world_height) / ray_distance

        texture_step = 32.0 / float(line_height)
        texture_offset = 0

        if line_height > world_height:
            texture_offset = (line_height - world_height) / 2
            line_height = world_height

        line_offset = (world_height - line_height) / 2  # Center the line on the vertical axis

        # Adjust line offset for vertical centering within the window
        line_offset += vertical_offset

        # Drawing textures
        ra = math.degrees(ra)
        if shade == 1:
            # Horizontal walls
            texture_x = int(rx / 2.0) % 32
            if ra < 180:
                texture_x = 31 - texture_x
        else:
            # Vertical walls
            texture_x = int(ry / 2.0) % 32
            if 90 < ra < 270:
                texture_x = 31 - texture_x
        texture_y = texture_offset * texture_step + map_texture_pos * 32

        ray_width = 8

        glPointSize(ray_width)
        glBegin(GL_POINTS)
        for y in range(int(line_height)):
            texture_color = self.textures[int(texture_y) * 32 + int(texture_x)] * shade

            # Draw walls with textures and colors
            if map_texture_pos == 0:
                glColor3f(texture_color, texture_color / 2.0, texture_color / 2.0)  # Checkerboard red
            if map_texture_pos == 1:
                glColor3f(texture_color, texture_color, texture_color / 2.0)  # Brick yellow
            if map_texture_pos == 2:
                glColor3f(texture_color / 2.0, texture_color / 2.0, texture_color)  # Window blue
            if map_texture_pos == 3:
                glColor3f(texture_color / 2.0, texture_color, texture_color / 2.0)  # Door green

            glVertex2i(ray_n * ray_width + horizontal_offset, int(y + line_offset))
            texture_y += texture_step
        glEnd()

    # self.draw_floors(line_offset, line_height, pa, self.controller.player.x, self.controller.player.x, ray_n, ra,
    #                  rx, ry, ray_distance)

    def draw_player(self):
        glColor3f(*self.controller.player.color)
        glPointSize(8)
        glBegin(GL_POINTS)
        glVertex2i(int(self.controller.player.map_grid_size_x), int(self.controller.player.map_grid_size_y))
        glEnd()

        glLineWidth(3)
        glBegin(GL_LINES)
        glVertex2i(int(self.controller.player.map_grid_size_x), int(self.controller.player.map_grid_size_y))
        glVertex2i(int(self.controller.player.map_grid_size_x + self.controller.player.dx * 5),
                   int(self.controller.player.map_grid_size_y + self.controller.player.dy * 5))
        glEnd()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_world_2d()
        self.draw_rays_2d()
        self.draw_player()
        self.draw_fps()
        glutSwapBuffers()

    def draw_fps(self):
        if self.display_fps:
            glColor3f(0, 1, 0)  # Green
            glWindowPos2i(900, 480)
            for char in f"FPS: {self.get_current_fps()}":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))  # noqa

    # def draw_ceiling(self):
    #     glColor3f(0, 1, 1)
    #     glBegin(GL_QUADS)
    #     glVertex2i(526, 0 + self.draw_offset)
    #     glVertex2i(1006, 0 + self.draw_offset)
    #     glVertex2i(1006, 160 + self.draw_offset)
    #     glVertex2i(526, 160 + self.draw_offset)
    #     glEnd()

    # def draw_floor(self):
    #     draw_offset = self.draw_offset + 30
    #     glColor3f(0, 0, 1)
    #     glBegin(GL_QUADS)
    #     glVertex2i(526, 160 + draw_offset)
    #     glVertex2i(1006, 160 + draw_offset)
    #     glVertex2i(1006, 320 + draw_offset)
    #     glVertex2i(526, 320 + draw_offset)
    #     glEnd()

    # def draw_floors(self, line_offset, line_height, pa, px, py, r, ra, rx, ry):
    #     glPointSize(8)
    #     glBegin(GL_POINTS)
    #     for y in range(int(line_offset) + int(line_height), 320 + self.draw_offset + 30):
    #         dy = y - ((320 + self.draw_offset + 30) / 2.0)
    #         deg = math.radians(ra)
    #         ra_fix = math.cos(math.radians(pa - ra))
    #
    #         tx = px / 2 + math.sin(deg) * 158 * 32 / dy / ra_fix
    #         ty = py / 2 - math.cos(deg) * 158 * 32 / dy / ra_fix
    #
    #         # mp = self.controller.world.world_map_floor[
    #         #          int(ty / 32.0) * self.controller.world.x + int(tx / 32)] * 32 * 32
    #         print(f'{(int(ty) & 31) * 32 + (int(tx) & 31)}')
    #
    #         c = self.textures[(int(ty) & 31) * 32 + (int(tx) & 31)] * 0.7
    #
    #         glColor3f(c / 1.3, c / 1.3, c)
    #         glVertex2i(r * 8 + 530, y)
    #     glEnd()

    # def draw_floors(self, line_offset, line_height, pa, px, py, r, ra, rx, ry, ray_distance):
    #     glPointSize(8)
    #     glBegin(GL_POINTS)
    #     for y in range(int(line_offset) + int(line_height), 320 + self.draw_offset + 30):
    #         dy = y - ((320 + line_offset) / 2.0)
    #         deg = math.radians(ra)
    #         ra_fix = math.cos(math.radians(pa - ra))
    #
    #         distance_to_screen = 158 * 32
    #         current_distance = distance_to_screen / (dy / ra_fix)
    #
    #         weight = current_distance / ray_distance
    #         floor_x = weight * rx + (1.0 - weight) * px
    #         floor_y = weight * ry + (1.0 - weight) * py
    #
    #         tx = int(floor_x)
    #         ty = int(floor_y)
    #
    #         c = self.textures[(int(ty) & 31) * 32 + (int(tx) & 31)] * 0.7
    #
    #         glColor3f(c / 1.3, c / 1.3, c)
    #         glVertex2i(r * 8 + 530, y)
    #     glEnd()

    def update_window_dimensions(self, window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height

    def clamp_angle(self, a):  # noqa
        if a > 359:
            a -= 360
        if a < 0:
            a += 360

        return a

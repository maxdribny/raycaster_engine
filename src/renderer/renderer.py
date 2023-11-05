# /src/renderer/renderer.py

import math
import time

from collections import deque

from math import pi as PI  # noqa

from OpenGL.GL import *
from OpenGL.GLUT import *

from src.renderer.textures import ALL_TEXTURES
from src.renderer.raycaster import raycaster_2d


class Renderer:
    def __init__(self, game_controller, fps_callback=None):
        self.controller = game_controller
        self.last_frame_time = time.time()
        self.fps_list = deque(maxlen=15)
        self.display_fps = True
        self.draw_offset = 50
        self.fps_callback = fps_callback

        # Precompute and cache vertices
        self.cached_vertices = self.precompute_vertices()

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
        for y in range(self.controller.world.y):
            for x in range(self.controller.world.x):
                is_wall = self.controller.world.world_map_walls[y * self.controller.world.x + x] > 0

                x_offset = x * self.controller.world.world_scale
                y_offset = y * self.controller.world.world_scale

                # Slightly smaller coordinates for drawing the quad
                v1 = (x_offset + border_thickness, y_offset + border_thickness)
                v2 = (x_offset + border_thickness, y_offset + self.controller.world.world_scale - border_thickness)
                v3 = (x_offset + self.controller.world.world_scale - border_thickness,
                      y_offset + self.controller.world.world_scale - border_thickness)
                v4 = (x_offset + self.controller.world.world_scale - border_thickness, y_offset + border_thickness)

                vertices.append((is_wall, v1, v2, v3, v4))

        print(f'Vertices computed: {len(vertices)}')
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
        player_x = self.controller.player.x
        player_y = self.controller.player.y

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

    def draw_world_3d(self, ray_distance, ray_n, pa, ra, color, shade, map_texture_pos, rx, ry, world_height=320,
                      world_width=160):

        world_height = world_height
        world_width = world_width
        line_offset_scale = 1.2

        cosine_angle = (pa - ra + 2 * PI) % (
                2 * PI)  # player_angle - ray_angle, also bounds the values between 0 and 2 * PI noqa

        # Fisheye effect fix (see: https://lodev.org/cgtutor/raycasting.html)
        ray_distance = ray_distance * math.cos(cosine_angle)

        if ray_distance == 0:  # Prevent division by zero
            ray_distance = sys.float_info.min

        line_height = (self.controller.world.world_scale * world_height) / ray_distance

        texture_step = 32.0 / float(line_height)
        texture_offset = 0

        if line_height > world_height:
            texture_offset = (line_height - world_height) / 2
            line_height = world_height

        line_offset = (world_width * line_offset_scale) - line_height / 2
        line_offset += self.draw_offset

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

        glPointSize(8)
        glBegin(GL_POINTS)
        for y in range(int(line_height)):
            texture_color = ALL_TEXTURES[int(texture_y) * 32 + int(texture_x)] * shade

            # Draw wall
            # glColor3f(*color)
            glColor3f(texture_color, texture_color, texture_color)
            glVertex2i(ray_n * 8 + 530, int(y + line_offset))
            texture_y += texture_step

        glEnd()

    def draw_player(self):
        glColor3f(*self.controller.player.color)
        glPointSize(8)
        glBegin(GL_POINTS)
        glVertex2i(int(self.controller.player.x), int(self.controller.player.y))
        glEnd()

        glLineWidth(3)
        glBegin(GL_LINES)
        glVertex2i(int(self.controller.player.x), int(self.controller.player.y))
        glVertex2i(int(self.controller.player.x + self.controller.player.dx * 5),
                   int(self.controller.player.y + self.controller.player.dy * 5))
        glEnd()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_world_2d()
        self.draw_ceiling()
        self.draw_floor()
        self.draw_rays_2d()
        # self.draw_world_3d(self.ray_data)  # Call this after draw_rays_2d() to draw the rays on top of the 3D world
        self.draw_player()
        self.draw_fps()
        glutSwapBuffers()

    def draw_fps(self):
        if self.display_fps:
            glColor3f(0, 1, 0)  # Green
            glWindowPos2i(900, 480)
            for char in f"FPS: {self.get_current_fps()}":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))  # noqa

    def draw_ceiling(self):
        glColor3f(0, 1, 1)
        glBegin(GL_QUADS)
        glVertex2i(526, 0 + self.draw_offset)
        glVertex2i(1006, 0 + self.draw_offset)
        glVertex2i(1006, 160 + self.draw_offset)
        glVertex2i(526, 160 + self.draw_offset)
        glEnd()

    def draw_floor(self):
        draw_offset = self.draw_offset + 30
        glColor3f(0, 0, 1)
        glBegin(GL_QUADS)
        glVertex2i(526, 160 + draw_offset)
        glVertex2i(1006, 160 + draw_offset)
        glVertex2i(1006, 320 + draw_offset)
        glVertex2i(526, 320 + draw_offset)
        glEnd()

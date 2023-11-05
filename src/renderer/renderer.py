# /src/renderer/renderer.py

import math
import time

from math import pi as PI  # noqa

from OpenGL.GL import *
from OpenGL.GLUT import *

from src.renderer.raycaster import raycaster_2d


class Renderer:
    def __init__(self, game_controller, fps_callback=None):
        self.controller = game_controller
        self.ray_data = []
        self.last_frame_time = time.time()
        self.fps_list = []
        self.display_fps = True
        self.draw_offset = 50
        self.fps_callback = fps_callback

    def get_current_fps(self):
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        fps = (int(1 / delta_time)) if delta_time > 0 else 0

        self.fps_list.append(fps)
        n = 15
        if len(self.fps_list) > n:
            self.fps_list.pop(0)

        average_fps = sum(self.fps_list) // len(self.fps_list)

        # Call the callback function if it is set
        if self.fps_callback:
            self.fps_callback(average_fps, delta_time)

        return average_fps

    def draw_world_2d(self):
        for y in range(self.controller.world.y):
            for x in range(self.controller.world.x):

                if self.controller.world.world_map[y * self.controller.world.x + x] == 1:  # Draw a wall
                    glColor3f(1, 1, 1)
                else:
                    glColor3f(0, 0, 0)

                x_offset = x * self.controller.world.world_scale
                y_offset = y * self.controller.world.world_scale

                # @formatter:off
                glBegin(GL_QUADS)
                glVertex2i(x_offset + 1                              , y_offset + 1)                               # noqa
                glVertex2i(x_offset + 1                              , y_offset + self.controller.world.world_scale - 1) # noqa
                glVertex2i(x_offset + self.controller.world.world_scale - 1,
                                                                       y_offset + self.controller.world.world_scale - 1) # noqa
                glVertex2i(x_offset + self.controller.world.world_scale - 1,
                                                                       y_offset + 1) # noqa
                glEnd()
                # @formatter:on

    def draw_world_3d(self, ray_distance, ray_n, pa, ra, color, world_height=320, world_width=160):
        world_height = world_height
        world_width = world_width
        line_offset_scale = 1.2

        cosine_angle = (pa - ra + 2 * PI) % (
                2 * PI)  # player_angle - ray_angle, also bounds the values between 0 and 2 * PI noqa

        # Fisheye effect fix (see: https://lodev.org/cgtutor/raycasting.html)
        ray_distance = ray_distance * math.cos(cosine_angle)

        if ray_distance == 0:  # Prevent division by zero
            ray_distance = sys.float_info.min

        line_height = min((self.controller.world.world_scale * world_height) / ray_distance, world_height)
        line_offset = (world_width * line_offset_scale) - line_height / 2
        line_offset += self.draw_offset

        # Draw wall
        glColor3f(*color)
        glLineWidth(8)
        glBegin(GL_LINES)
        glVertex2i(ray_n * 8 + 530, int(line_offset))
        glVertex2i(ray_n * 8 + 530, int(line_height + line_offset))
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

    def draw_rays_2d(self):
        self.ray_data = []  # Clear previous ray data
        player_angle = self.controller.player.angle
        player_x = self.controller.player.x
        player_y = self.controller.player.y

        for r, ra, rx, ry, distance, color in raycaster_2d(player_angle,
                                                           player_x,
                                                           player_y,
                                                           self.controller,
                                                           num_rays=self.controller.player.FOV):
            # Draw the rays being cast
            glColor3f(1, 0, 0)  # Red
            glLineWidth(1)
            glBegin(GL_LINES)
            glVertex2i(int(player_x), int(player_y))
            glVertex2i(int(rx), int(ry))
            glEnd()

            self.draw_world_3d(distance, r, player_angle, ra, color)

            # Store the ray data for 3D drawing
            # self.ray_data.append((distance, r, player_angle, rx))

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

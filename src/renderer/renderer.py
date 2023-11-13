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
    def __init__(self, game_controller, window_width, window_height, fps_callback=None):
        self.controller = game_controller
        self.textures = ALL_TEXTURES
        self.draw_calls = 0
        self.ray_width = 8

        # FPS display
        self.last_frame_time = time.time()
        self.fps_list = deque(maxlen=15)
        self.display_fps = True
        self.fps_callback = fps_callback

        # Window / screen dimensions
        self.window_width = window_width
        self.window_height = window_height

        # Precompute and cache vertices
        self.cached_vertices = self.precompute_vertices_2d_world()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_world_2d()
        self.draw_rays_2d()
        self.draw_player()
        self.draw_fps()
        glutSwapBuffers()

        self.draw_calls += 1
        if self.draw_calls >= 75:
            if self.controller.world.is_updated:
                self.check_for_world_has_changed()
                self.draw_calls = 0

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
            glLineWidth(1)
            glBegin(GL_LINES)
            glColor3f(0.8, 0, 0)  # Red
            glVertex2i(int(player_x), int(player_y))
            glVertex2i(int(rx), int(ry))
            glEnd()

            self.draw_world_3d(distance, r, player_angle, ra, color, shade, map_texture_pos, rx=rx, ry=ry)

    def draw_world_3d(self, ray_distance, ray_n, pa, ra, color, shade, map_texture_pos, rx, ry, world_height=400):
        world_width = self.ray_width * self.controller.player.FOV

        horizontal_offset = (self.window_width // 2) + ((self.window_width // 2) - int(world_width)) // 2 + (
                self.ray_width // 2)
        vertical_offset = (self.window_height - world_height) // 2

        cosine_angle = (pa - ra + 2 * PI) % (
                2 * PI)  # player_angle - ray_angle, also bounds the values between 0 and 2 * PI noqa

        # Fisheye effect fix (see: https://lodev.org/cgtutor/raycasting.html)
        ray_distance = ray_distance * math.cos(cosine_angle)
        ray_distance = max(ray_distance, sys.float_info.min)

        line_height = (self.controller.world.map_grid_size * world_height) / ray_distance

        texture_step = 32.0 / float(line_height)
        texture_offset = 0

        # Adjust line height and texture offset for vertical centering within the window
        if line_height > world_height:
            texture_offset = (line_height - world_height) / 2
            line_height = world_height

        line_offset = (world_height - line_height) / 2 + vertical_offset  # Adjust line for vertical centering

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

        glPointSize(self.ray_width)
        glBegin(GL_POINTS)
        for y in range(int(line_height)):
            # Prevent the 3d world from being drawn outside the window due to point size > 1
            if y + line_offset + self.ray_width > world_height + vertical_offset:
                break

            texture_color = self.textures[int(texture_y) * 32 + int(texture_x)] * shade

            # Draw walls with textures and colors
            if map_texture_pos == 0:
                glColor3f(texture_color, texture_color / 2.0, texture_color / 2.0)  # Checkerboard red
            elif map_texture_pos == 1:
                glColor3f(texture_color, texture_color, texture_color / 2.0)  # Brick yellow
            elif map_texture_pos == 2:
                glColor3f(texture_color / 2.0, texture_color / 2.0, texture_color)  # Window blue
            elif map_texture_pos == 3:
                glColor3f(texture_color / 2.0, texture_color, texture_color / 2.0)  # Door green

            # The actual width of the 3d world will always be total_ray_n * self.ray_width
            glVertex2i(ray_n * self.ray_width + horizontal_offset, int(y + line_offset))
            texture_y += texture_step
        glEnd()

        # TODO: Fix drawing floors
        # Draw floors
        for y in range(int(line_offset + line_height), int(world_height)):
            # Perspective calculation
            perspective = (y - world_height / 2.0) / (world_width / 2.0)
            distance = world_height / perspective

            # Correct angle and calculate postion
            angle = self.clamp_angle(pa - ra)
            floor_x = self.controller.player.x + math.cos(angle) * distance
            floor_y = self.controller.player.y - math.sin(angle) * distance

            # Texture mapping
            tx = int(floor_x) % 32
            ty = int(floor_y) % 32

            texture_index = (ty * 32 + tx) % len(self.textures)

            if texture_index > 1023:
                print(f'Index: {texture_index} | tx: {tx} | ty: {ty} | floor_x: {floor_x} | floor_y: {floor_y} | ')

            # Get color from texture and apply shading
            if 0 <= texture_index < len(self.textures):
                texture_color = self.textures[texture_index] * shade

                glColor3f(texture_color, texture_color, texture_color)
                glPointSize(self.ray_width)  # Adjust point size if necessary
                glBegin(GL_POINTS)
                glVertex2i(ray_n * self.ray_width + horizontal_offset, y)
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

    def precompute_vertices_2d_world(self):
        vertices = []
        border_thickness = 1
        print(f'\nComputing vertices...')

        for y in range(self.controller.world.map_grid_size_y):
            for x in range(self.controller.world.map_grid_size_x):
                is_wall = self.controller.world.map_grid_walls[y * self.controller.world.map_grid_size_x + x] > 0

                x_offset = x * self.controller.world.map_grid_size
                y_offset = y * self.controller.world.map_grid_size

                # Slightly smaller coordinates for drawing the quad
                v1 = (x_offset + border_thickness, y_offset + border_thickness)
                v2 = (
                    x_offset + border_thickness, y_offset + self.controller.world.map_grid_size - border_thickness)
                v3 = (x_offset + self.controller.world.map_grid_size - border_thickness,
                      y_offset + self.controller.world.map_grid_size - border_thickness)
                v4 = (
                    x_offset + self.controller.world.map_grid_size - border_thickness, y_offset + border_thickness)

                vertices.append((is_wall, v1, v2, v3, v4))

        print(f'\nVertices computed: {len(vertices)}')
        return vertices

    def draw_fps(self):
        if self.display_fps:
            glColor3f(0, 1, 0)  # Green
            glWindowPos2i(900, 480)
            for char in f"FPS: {self.get_current_fps()}":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))  # noqa

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

    def update_cached_world_2d(self, x, y, is_wall):
        index = y * self.controller.world.map_grid_size_x + x
        border_thickness = 1
        x_offset = x * self.controller.world.map_grid_size
        y_offset = y * self.controller.world.map_grid_size

        v1 = (x_offset + border_thickness, y_offset + border_thickness)
        v2 = (
            x_offset + border_thickness, y_offset + self.controller.world.map_grid_size - border_thickness)
        v3 = (x_offset + self.controller.world.map_grid_size - border_thickness,
              y_offset + self.controller.world.map_grid_size - border_thickness)
        v4 = (
            x_offset + self.controller.world.map_grid_size - border_thickness, y_offset + border_thickness)

        self.cached_vertices[index] = (is_wall, v1, v2, v3, v4)

    def check_for_world_has_changed(self):
        for y in range(self.controller.world.map_grid_size_y):
            for x in range(self.controller.world.map_grid_size_x):
                current_index_is_wall = self.controller.world.map_grid_walls[
                                            y * self.controller.world.map_grid_size_x + x] > 0
                cached_is_wall = self.cached_vertices[y * self.controller.world.map_grid_size_x + x][0]

                # Check if there is a difference between the current state and the cached state and update if there is
                if current_index_is_wall != cached_is_wall:
                    self.update_cached_world_2d(x, y, current_index_is_wall)

    def update_window_dimensions(self, x, y):
        self.window_width = x
        self.window_height = y

    def clamp_angle(self, a):  # noqa
        if a > 359:
            a -= 360
        if a < 0:
            a += 360

        return a

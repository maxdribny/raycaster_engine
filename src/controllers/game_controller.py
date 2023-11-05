from OpenGL.GLUT import *

from src.entities.player import Player
from src.models.world import World


class GameController:
    def __init__(self):
        self.player = Player()
        self.world = World()
        self.keys_pressed = set()  # Set to hold the current keys being pressed
        self.keys_just_pressed = set()  # Set to hold the keys that were just pressed

    def update(self, delta_time):
        self.update_player_position(delta_time)
        self.check_debug_keys()
        self.check_interaction_keys()

        if '\x1b' in self.keys_pressed:  # Escape key
            glutLeaveMainLoop()
            sys.exit("Exiting")

        glutPostRedisplay()

    def update_player_position(self, delta_time):
        # Check collision
        (is_colliding_x_forward, is_colliding_y_forward,
         is_colliding_x_backward, is_colliding_y_backward) = self.check_player_collision_forward()

        # Movement keys
        if 'a' in self.keys_pressed:
            self.player.update_angle(-0.1 * delta_time)
        if 'd' in self.keys_pressed:
            self.player.update_angle(0.1 * delta_time)
        if 'w' in self.keys_pressed:
            if not is_colliding_y_forward:
                self.player.move_forward_y(delta_time)
            if not is_colliding_x_forward:
                self.player.move_foward_x(delta_time)
        if 's' in self.keys_pressed:
            if not is_colliding_y_backward:
                self.player.move_backward_y(delta_time)
            if not is_colliding_x_backward:
                self.player.move_backward_x(delta_time)

    def check_interaction_keys(self):
        # Interaction keys
        if 'e' in self.keys_pressed:  # Open doors
            self.open_door()

    def open_door(self):
        interact_distance = self.player.interact_distance

        xo = -interact_distance if self.player.dx < 0 else (interact_distance if self.player.dx > 0 else 0)
        yo = -interact_distance if self.player.dy < 0 else (interact_distance if self.player.dy > 0 else 0)
        ipx = self.player.x / 64.0
        ipy = self.player.y / 64.0
        ipx_add_offset = int((self.player.x + xo) / 64.0)
        ipy_add_offset = int((self.player.y + yo) / 64.0)

        if self.world.world_map_walls[ipy_add_offset * self.world.x + ipx_add_offset] == 4:
            self.world.world_map_walls[ipy_add_offset * self.world.x + ipx_add_offset] = 0

    def check_player_collision_forward(self):
        offset_value = 10

        x_offset = -offset_value if self.player.dx < 0 else offset_value
        y_offset = -offset_value if self.player.dy < 0 else offset_value

        player_grid_pos_x = int(self.player.x / 64)
        player_grid_pos_x_add_offset = int((self.player.x + x_offset) / 64)
        player_grid_pos_x_sub_offset = int((self.player.x - x_offset) / 64)

        player_grid_pos_y = int(self.player.y / 64)
        player_grid_pos_y_add_offset = int((self.player.y + y_offset) / 64)
        player_grid_pos_y_sub_offset = int((self.player.y - y_offset) / 64)

        is_colliding_x_forward = self.world.world_map_walls[
                                     player_grid_pos_y * self.world.x + player_grid_pos_x_add_offset] != 0
        is_colliding_y_forward = self.world.world_map_walls[
                                     player_grid_pos_y_add_offset * self.world.x + player_grid_pos_x] != 0

        is_colliding_x_backward = self.world.world_map_walls[
                                      player_grid_pos_y * self.world.x + player_grid_pos_x_sub_offset] != 0
        is_colliding_y_backward = self.world.world_map_walls[
                                      player_grid_pos_y_sub_offset * self.world.x + player_grid_pos_x] != 0

        return is_colliding_x_forward, is_colliding_y_forward, is_colliding_x_backward, is_colliding_y_backward

    def handle_keyboard_input_down(self, key, x, y):
        key = key.decode('ascii')
        self.keys_pressed.add(key)
        self.keys_just_pressed.add(key)

    def handle_keyboard_input_up(self, key, x, y):
        key = key.decode('ascii')
        self.keys_pressed.discard(key)
        self.keys_just_pressed.discard(key)

    def check_debug_keys(self):
        # Debug keys
        if 'q' in self.keys_just_pressed:  # Just pressed
            self.keys_just_pressed.remove('q')
        if 'v' in self.keys_just_pressed:  # Just pressed
            self.keys_just_pressed.remove('v')

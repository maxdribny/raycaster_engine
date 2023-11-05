import math
from src.models.constants import (PLAYER_INITIAL_X, PLAYER_INITIAL_Y, PLAYER_INITIAL_ANGLE, PLAYER_ROTATION_SPEED,
                                  PLAYER_MOVE_SPEED, PLAYER_COLOR, RENDER_FOV)


class Player:
    def __init__(self, x=PLAYER_INITIAL_X, y=PLAYER_INITIAL_Y, angle=PLAYER_INITIAL_ANGLE):
        self.x = x
        self.y = y
        self.angle = math.radians(angle)
        self.color = PLAYER_COLOR
        self.rotation_scale = PLAYER_ROTATION_SPEED
        self.move_speed = PLAYER_MOVE_SPEED
        self.dx, self.dy = math.cos(self.angle) * 5, math.sin(self.angle) * 5
        self.FOV = RENDER_FOV

    def update_angle(self, delta_angle):
        self.angle += delta_angle * self.rotation_scale
        self.angle = math.fmod(self.angle + 2 * math.pi, 2 * math.pi)
        self.dx = math.cos(self.angle) * 5
        self.dy = math.sin(self.angle) * 5

    def move_foward_x(self, delta_time):
        self.x += self.dx * self.move_speed * delta_time

    def move_forward_y(self, delta_time):
        self.y += self.dy * self.move_speed * delta_time

    def move_foward(self, delta_time):
        self.move_foward_x(delta_time)
        self.move_forward_y(delta_time)

    def move_backward_x(self, delta_time):
        self.x -= self.dx * self.move_speed * delta_time

    def move_backward_y(self, delta_time):
        self.y -= self.dy * self.move_speed * delta_time

    def move_backward(self, delta_time):
        self.move_backward_x(delta_time)
        self.move_backward_y(delta_time)

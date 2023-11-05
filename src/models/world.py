from src.models.constants import WORLD_SCALE, WORLD_SIZE_X, WORLD_SIZE_Y
from src.exceptions.world_exceptions import *


class World:
    def __init__(self):
        self.__x = WORLD_SIZE_X
        self.__y = WORLD_SIZE_Y
        self.__scale = WORLD_SCALE
        self.__world_map_walls = [
            1, 1, 1, 1, 1, 1, 1, 1,
            1, 0, 1, 0, 0, 0, 1, 1,
            1, 0, 1, 0, 0, 0, 0, 1,
            1, 0, 0, 0, 0, 0, 0, 1,
            1, 0, 0, 2, 0, 0, 0, 1,
            1, 0, 1, 1, 0, 0, 1, 1,
            1, 0, 0, 0, 0, 0, 0, 1,
            1, 1, 1, 1, 1, 1, 1, 1,
        ]

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def world_scale(self):
        return self.__scale

    @property
    def world_map_walls(self):
        return self.__world_map_walls

    @world_map_walls.setter
    def world_map_walls(self, new_map):
        # Check that the map is not empty
        if len(new_map) == 0:
            raise WorldMapError("The map cannot be empty")

        # Check that the map is an array of integers and throw a new error if not
        if not all(isinstance(item, int) for item in new_map):
            raise WorldMapError("The map must be an array of integers")

        # Check that the world map conforms to the world size
        if len(new_map) != self.x * self.y:
            raise WorldMapError("The map must be the same size as the world, have you checked that the world map is "
                                "coherent with WORLD_SIZE_X and WORLD_SIZE_Y?")

        self.__world_map_walls = new_map

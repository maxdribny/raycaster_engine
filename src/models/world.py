from src.models.constants import MAP_GRID_SIZE, MAP_GRID_X, MAP_GRID_Y
from src.exceptions.world_exceptions import *


class World:
    def __init__(self):
        self.__x = MAP_GRID_X
        self.__y = MAP_GRID_Y
        self.__scale = MAP_GRID_SIZE
        self.__map_grid_walls = [
            2, 2, 2, 2, 2, 2, 2, 2,
            2, 0, 1, 0, 0, 2, 0, 1,
            2, 0, 1, 0, 0, 0, 0, 1,
            2, 0, 4, 0, 0, 0, 0, 1,
            2, 0, 1, 0, 0, 0, 0, 1,
            2, 0, 4, 0, 0, 1, 0, 1,
            2, 0, 1, 0, 0, 1, 0, 1,
            2, 1, 1, 1, 1, 1, 1, 1,
        ]
        self.__map_grid_floors = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 1, 1, 0, 0,
            0, 0, 0, 0, 2, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 2, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ]
        self.__is_updated = False

    @property
    def map_grid_floors(self):
        return self.__map_grid_floors

    @property
    def map_grid_size_x(self):
        return self.__x

    @property
    def map_grid_size_y(self):
        return self.__y

    @property
    def map_grid_size(self):
        return self.__scale

    @property
    def map_grid_walls(self):
        return self.__map_grid_walls

    @map_grid_walls.setter
    def map_grid_walls(self, new_map):
        # Check that the map is not empty
        if len(new_map) == 0:
            raise WorldMapError("The map cannot be empty")

        # Check that the map is an array of integers and throw a new error if not
        if not all(isinstance(item, int) for item in new_map):
            raise WorldMapError("The map must be an array of integers")

        # Check that the world map conforms to the world size
        if len(new_map) != self.map_grid_size_x * self.map_grid_size_y:
            raise WorldMapError("The map must be the same size as the world, have you checked that the world map is "
                                "coherent with WORLD_SIZE_X and WORLD_SIZE_Y?")

        self.__map_grid_walls = new_map

    @property
    def is_updated(self):
        update_return = self.__is_updated

        if self.__is_updated:
            self.__is_updated = False

        return update_return

    @is_updated.setter
    def is_updated(self, value):
        self.__is_updated = value

    def update_wall_at_position(self, x, y, new_value):
        # Check that the x and y values are within the world bounds
        if x < 0 or x > self.map_grid_size_x or y < 0 or y > self.map_grid_size_y:
            raise WorldMapError(f"Cannot update wall at position ({x}, {y}), the position is out of bounds")

        # Check that the new value is an integer
        if not isinstance(new_value, int):
            raise WorldMapError(f"Cannot update wall at position ({x}, {y}), the new value must be an integer")

        # Update the value
        self.__map_grid_walls[y * self.map_grid_size_x + x] = new_value

class WorldSizeError(Exception):
    """Raised when the world size is not valid"""
    pass


class WorldScaleError(Exception):
    """Raised when the world scale is not valid"""
    pass


class WorldMapError(Exception):
    """Raised when the world map is not valid"""
    pass


class WorldEmptyError(Exception):
    """Raised when the world map is empty"""
    pass

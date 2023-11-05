def rgb_percent_color_to_hex(r, g, b):
    """Converts a color from RGB percent to hex."""
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))


def hex_color_to_rgb_percent(color):
    """Converts a color from hex to RGB percent."""
    color = color.lstrip('#')
    return tuple(int(color[i:i + 2], 16) / 255 for i in (0, 2, 4))

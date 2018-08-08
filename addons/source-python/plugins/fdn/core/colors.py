# ../fdn/core/colors.py

# Source.Python
from colors import Color


__all__ = (
    'WHITE',
    'RED',
    'INVISIBLE'
    )


def rgb_to_long(r, g, b):
    """Convert an RGB color to a long value."""
    return b * 65536 + g * 256 + r


WHITE = rgb_to_long(255, 255, 255)
RED = rgb_to_long(255, 45, 45)
INVISIBLE = Color(255, 255, 255, 0)

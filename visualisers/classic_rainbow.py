"""Classic rainbow: The original Pimoroni rainbow example."""
import math
from .shader import shader


def classic_rainbow(x, y, step):
    i = step * 0.3
    r = (math.cos((x + i) / 2.0) + math.cos((y + i) / 2.0)) * 64.0 + 128.0
    g = (math.sin((x + i) / 1.5) + math.sin((y + i) / 2.0)) * 64.0 + 128.0
    b = (math.sin((x + i) / 2.0) + math.cos((y + i) / 1.5)) * 64.0 + 128.0
    return (r + 30, g + 30, b + 30)


def run():
    shader(classic_rainbow, 8)

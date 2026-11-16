"""Blues and twos: Flashing blue emergency-light waves."""
import math
from .display import W, H
from .shader import shader


def blues_and_twos(x, y, step):
    x -= W / 2; y -= H / 2
    scale = math.sin(step / 6.0) / 1.5
    r = math.sin(x * scale) + math.cos(y * scale)
    b = math.sin(x * scale / 2.0) + math.cos(y * scale / 2.0)
    g = max(0, r - .8)
    b -= r; b /= 1.4
    return (g * 255, (b + g) * 255, r * 255)  # swapped so it reads blue


def run():
    shader(blues_and_twos, 8)

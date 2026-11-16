"""Rainbow blinky: A rainbow that pulses out from the centre."""
import colorsys, math
from .shader import shader


def rainbow_blinky(x, y, step):
    seq = list(range(1, 10)[::-1]) + list(range(1, 10))
    z = seq[(step // 2) % len(seq)]
    fwhm = 5.0 / z
    g = math.exp(-4 * math.log(2) * ((x - 3.5) ** 2 + (y - 3.5) ** 2) / fwhm ** 2)
    r, gg, b = colorsys.hsv_to_rgb(1.0 / (x + y + 1), 0.8, g)
    return (r * 255, gg * 255, b * 255)


def run():
    shader(rainbow_blinky, 8)

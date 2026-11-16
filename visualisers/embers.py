"""Embers: Random flickering yellow-orange-red LEDs."""
import colorsys, random, time
from .display import uh, W, H


def run(sec=6):
    t0 = time.time()
    while time.time() - t0 < sec:
        for y in range(H):
            for x in range(W):
                v = random.random()
                r, g, b = colorsys.hsv_to_rgb(0.1 * v, 0.8, v)
                uh.set_pixel(x, y, int(r * 255), int(g * 255), int(b * 255))
        uh.show(); time.sleep(0.08)

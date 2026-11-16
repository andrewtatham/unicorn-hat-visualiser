"""Plasma: Overlapping sine waves, the classic demoscene plasma."""
import math, time
from .display import W, H
from .common import put, rgb, strip


def run(sec=5):
    t0 = time.time()
    while time.time() - t0 < sec:
        t = time.time()
        for y in range(H):
            for x in range(W):
                v = math.sin(x / 2 + t) + math.sin(y / 2 + t * 1.3) + math.sin((x + y) / 3 + t * 0.7)
                put(x, y, rgb(v / 6 + t * 0.05))
        strip.show(); time.sleep(0.03)

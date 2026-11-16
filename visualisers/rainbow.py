"""Rainbow wave: Smooth diagonal rainbow that drifts across the board."""
import time
from .display import W, H
from .common import put, rgb, strip


def run(sec=5):
    t0 = time.time()
    while time.time() - t0 < sec:
        t = time.time() * 0.3
        for y in range(H):
            for x in range(W):
                put(x, y, rgb(t + (x + y) / 16))
        strip.show(); time.sleep(0.03)

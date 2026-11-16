"""Ripple: Colour rings radiating out from the centre."""
import math, time
from .display import W, H
from .common import put, rgb, strip


def run(sec=5):
    t0 = time.time()
    while time.time() - t0 < sec:
        t = time.time() * 3
        for y in range(H):
            for x in range(W):
                d = math.hypot(x - 3.5, y - 3.5)
                put(x, y, rgb(d / 8 - t / 10, 1, (math.sin(d * 1.5 - t) + 1) / 2))
        strip.show(); time.sleep(0.03)

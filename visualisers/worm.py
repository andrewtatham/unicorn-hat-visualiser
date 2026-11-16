"""Worm: A rainbow worm chasing itself along the LED chain."""
import time
from .common import clear, put, rgb, strip


def run(sec=6):
    """Simple serpentine chase along the wiring order."""
    t0 = time.time(); p = 0
    while time.time() - t0 < sec:
        clear()
        for k in range(12):
            put((p - k) % 64 % 8, (p - k) % 64 // 8, rgb(p / 64 + k / 40, 1, 1 - k / 12))
        strip.show(); p += 1; time.sleep(0.05)

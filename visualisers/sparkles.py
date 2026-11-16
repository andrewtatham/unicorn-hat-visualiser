"""Sparkles: Random colourful sparkles building up."""
import random, time
from .display import uh


def run(sec=6):
    uh.clear(); t0 = time.time()
    while time.time() - t0 < sec:
        uh.set_pixel(random.randint(0, 7), random.randint(0, 7),
                     random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        uh.show(); time.sleep(0.01)

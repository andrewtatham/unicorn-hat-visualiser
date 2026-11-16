"""Snow: A gentle snowstorm."""
import random, time
from .display import uh, W, H


def run(sec=8):
    rows = [[0] * W for _ in range(H)]
    t0 = time.time()
    while time.time() - t0 < sec:
        rows.pop()                       # drop the bottom row, new flakes at top
        new = [0] * W; new[random.randint(0, W - 1)] = 50 + random.randint(0, 155)
        rows.insert(0, new)
        for y in range(H):
            for x in range(W):
                v = rows[y][x]; uh.set_pixel(x, y, v, v, v)
        uh.show(); time.sleep(0.2)

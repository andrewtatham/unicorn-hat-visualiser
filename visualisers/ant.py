"""Langton's ant: A simple ant building complex patterns."""
import random, time
from .display import uh, W
from .common import hsv, px


def run(sec=25):
    cells = [[0] * W for _ in range(W)]
    for _ in range(random.randint(0, 14)):
        cells[random.randrange(W)][random.randrange(W)] = 1
    x, y, d = random.randrange(W), random.randrange(W), random.randrange(4)
    t0 = time.time(); steps = 0
    dirs = ((0, -1), (1, 0), (0, 1), (-1, 0))
    while time.time() - t0 < sec:
        for _ in range(2):
            if cells[y][x] == 0: d = (d + 1) % 4
            else: d = (d - 1) % 4
            cells[y][x] ^= 1
            x = (x + dirs[d][0]) % W; y = (y + dirs[d][1]) % W; steps += 1
        uh.clear()
        for yy in range(W):
            for xx in range(W):
                if cells[yy][xx]: px(xx, yy, hsv(0.5 + (steps % 300) / 1500.0, 0.8, 0.45))
        px(x, y, (255, 0, 60))
        uh.show(); time.sleep(0.05)

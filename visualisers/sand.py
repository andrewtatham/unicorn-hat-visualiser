"""Falling sand: Grains pile up as gravity rotates around the board."""
import random, time
from .display import uh, W, H
from .common import hsv, px


def run(sec=28):
    grav = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    grid = {}; t0 = time.time(); k = 0; hue = 0.0
    while time.time() - t0 < sec:
        gi = int((time.time() - t0) // 6) % 4; gx, gy = grav[gi]; k += 1
        if k % 2 == 0 and len(grid) < 30:
            sx = random.choice((3, 4)) if gx == 0 else (0 if gx > 0 else 7)
            sy = random.choice((3, 4)) if gy == 0 else (0 if gy > 0 else 7)
            if (sx, sy) not in grid: grid[(sx, sy)] = hsv(hue); hue += 0.037
        for (x, y) in sorted(grid, key=lambda c: -(c[0] * gx + c[1] * gy)):
            col = grid[(x, y)]
            cand = [(x + gx, y + gy)]
            for sgn in random.sample((1, -1), 2):
                pxx, pyy = -gy * sgn, gx * sgn
                if (x + pxx, y + pyy) not in grid: cand.append((x + gx + pxx, y + gy + pyy))
            for n in cand:
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in grid:
                    del grid[(x, y)]; grid[n] = col; break
        uh.clear()
        for c, col in grid.items(): px(c[0], c[1], col)
        uh.show(); time.sleep(0.08)

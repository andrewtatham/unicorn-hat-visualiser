"""Cross: Coloured dots crossing each other's paths."""
import random, time
from .display import uh, W, H


def run(sec=8):
    pts = []; t0 = time.time()
    while time.time() - t0 < sec:
        if len(pts) < 10 and random.randint(0, 5) > 1:
            d = random.randint(1, 4)
            x, y = {1: (random.randint(0, 7), 0), 2: (0, random.randint(0, 7)),
                    3: (random.randint(0, 7), 7), 4: (7, random.randint(0, 7))}[d]
            pts.append([x, y, d, [random.randint(100, 255) for _ in range(3)]])
        uh.clear()
        for p in pts:
            uh.set_pixel(p[0], p[1], *p[3])
        uh.show()
        for p in pts[:]:
            dx, dy = {1: (0, 1), 2: (1, 0), 3: (0, -1), 4: (-1, 0)}[p[2]]
            p[0] += dx; p[1] += dy
            if not (0 <= p[0] < W and 0 <= p[1] < H):
                pts.remove(p)
        time.sleep(0.06)

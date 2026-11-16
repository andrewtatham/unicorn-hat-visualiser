"""Breakout: An AI paddle clears rows of bricks."""
import random, time
from .display import uh, W
from .common import flash, px


def run(sec=30):
    row_cols = [(255, 0, 0), (255, 140, 0), (255, 255, 0)]
    new_bricks = lambda: {(x, y) for x in range(W) for y in range(3) if random.random() > 0.12}
    bricks = new_bricks(); lives = 3; pad = random.uniform(1.5, 5.5); err = 0
    def serve():
        return random.uniform(1.5, 5.5), 5.0, random.choice((-1, 1)) * random.uniform(0.15, 0.45), -random.uniform(0.33, 0.48)
    bx, by, vx, vy = serve()
    t0 = time.time()
    while time.time() - t0 < sec:
        bx += vx; by += vy
        if bx < 0: bx, vx = -bx, -vx
        if bx > 7: bx, vx = 14 - bx, -vx
        if by < 0: by, vy = -by, abs(vy)
        cell = (int(round(bx)), int(round(by)))
        if cell in bricks:
            bricks.discard(cell); vy = -vy
        target = bx + err
        if random.random() < 0.9:
            pad += max(-1, min(1, target - pad))
        pad = max(1, min(6, pad))
        if vy > 0 and by >= 6.0:
            if abs(bx - pad) <= 1.5:
                vy = -abs(vy); by = 6.0
                vx = max(-0.6, min(0.6, vx + (bx - pad) * 0.15))
                err = random.choice((-2, -1, 0, 0, 0, 1, 2))
            elif by > 7.2:
                lives -= 1
                if lives == 0:
                    flash((255, 0, 0)); bricks = new_bricks(); lives = 3
                bx, by, vx, vy = serve()
        if not bricks:
            flash((0, 255, 0)); bricks = new_bricks(); bx, by, vx, vy = serve()
        uh.clear()
        for (x, y) in bricks: px(x, y, row_cols[y])
        for k in (-1, 0, 1): px(round(pad) + k, 7, (0, 160, 255))
        px(round(bx), round(by), (255, 255, 255))
        uh.show(); time.sleep(0.06)

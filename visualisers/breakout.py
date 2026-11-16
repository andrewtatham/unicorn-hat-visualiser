"""Breakout: An AI paddle clears rows of bricks."""
import random, time
from .display import uh, W
from .common import flash, px

ROW_COLS = [(255, 0, 0), (255, 140, 0), (255, 255, 0)]


def _draw(bricks, pad, ball=None, floor=(0, 160, 255)):
    uh.clear()
    for (x, y) in bricks: px(x, y, ROW_COLS[y])
    if floor:
        for k in (-1, 0, 1): px(round(pad) + k, 7, floor)
    if ball: px(round(ball[0]), round(ball[1]), (255, 255, 255))
    uh.show()


def _lost_ball(bricks, pad):
    """The ball fell past the paddle: flash the floor red with no ball on screen, then pause."""
    for _ in range(3):
        uh.clear()
        for (x, y) in bricks: px(x, y, ROW_COLS[y])
        for x in range(W): px(x, 7, (255, 0, 0))
        uh.show(); time.sleep(0.12)
        _draw(bricks, pad, None, floor=None); time.sleep(0.12)
    _draw(bricks, pad); time.sleep(0.4)


def _hold_ball(bricks, pad, frames=10):
    """A fresh ball sits on the paddle and blinks before it is launched."""
    for i in range(frames):
        _draw(bricks, pad, (pad, 6) if i % 2 == 0 else None); time.sleep(0.08)


def run(sec=30):
    new_bricks = lambda: {(x, y) for x in range(W) for y in range(3) if random.random() > 0.12}
    bricks = new_bricks(); lives = 3; pad = random.uniform(1.5, 5.5); err = 0
    def serve():
        return pad, 6.0, random.choice((-1, 1)) * random.uniform(0.15, 0.45), -random.uniform(0.33, 0.48)
    _hold_ball(bricks, pad)
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
        missed = False
        if vy > 0 and by >= 6.0:
            if abs(bx - pad) <= 1.5:
                vy = -abs(vy); by = 6.0
                vx = max(-0.6, min(0.6, vx + (bx - pad) * 0.15))
                err = random.choice((-2, -1, 0, 0, 0, 1, 2))
            elif by > 7.2:
                missed = True
        if missed:
            lives -= 1
            _lost_ball(bricks, pad)
            if lives == 0:
                flash((255, 0, 0)); bricks = new_bricks(); lives = 3
            _hold_ball(bricks, pad)
            bx, by, vx, vy = serve()
            continue
        if not bricks:
            flash((0, 255, 0)); bricks = new_bricks(); _hold_ball(bricks, pad); bx, by, vx, vy = serve()
            continue
        _draw(bricks, pad, (bx, by)); time.sleep(0.06)

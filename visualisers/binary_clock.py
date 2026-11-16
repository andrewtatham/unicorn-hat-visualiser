"""Binary clock: Hours, minutes and seconds in binary-coded decimal."""
import time
from .display import uh
from .common import px


def run(sec=15):
    cols = [(0, 120, 255), (0, 120, 255), (0, 255, 80), (0, 255, 80), (255, 60, 60), (255, 60, 60)]
    xs = [0, 1, 3, 4, 6, 7]
    t0 = time.time()
    while time.time() - t0 < sec:
        t = time.localtime()
        digits = [t.tm_hour // 10, t.tm_hour % 10, t.tm_min // 10, t.tm_min % 10, t.tm_sec // 10, t.tm_sec % 10]
        uh.clear()
        for x, d, c in zip(xs, digits, cols):
            for bit in range(4):
                px(x, 6 - bit, c if d & (1 << bit) else (25, 25, 25))
        px(t.tm_sec % 8, 1, (255, 255, 255))          # ticking dot
        uh.show(); time.sleep(0.1)

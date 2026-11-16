"""Matrix rain: Falling green code. Follow the white rabbit."""
import random, time
from .display import uh


def run(sec=10):
    wrd = [(154, 173, 154), (0, 255, 0), (0, 200, 0), (0, 162, 0), (0, 145, 0), (0, 96, 0), (0, 74, 0), (0, 0, 0)]
    pop = [[random.randint(0, 7), 0]]; clock = 0; t0 = time.time()
    while time.time() - t0 < sec:
        uh.clear()
        for p in pop:
            y = p[1]
            for rgb in wrd:
                if 0 <= y <= 7:
                    uh.set_pixel(p[0], y, *rgb)
                y -= 1
            p[1] += 1
        uh.show(); time.sleep(0.1); clock += 1
        if clock % 5 == 0: pop.append([random.randint(0, 7), 0])
        if clock % 7 == 0: pop.append([random.randint(0, 7), 0])
        pop = [p for p in pop if p[1] - 8 <= 8]

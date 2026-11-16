"""2048: The AI slides tiles, drawn as 2x2 pixel blocks."""
import random, time
from .display import uh
from .common import flash, px


_T2048 = {0: (0, 0, 0), 2: (50, 50, 120), 4: (60, 90, 200), 8: (0, 170, 220), 16: (0, 210, 120), 32: (130, 230, 0),
          64: (240, 220, 0), 128: (255, 150, 0), 256: (255, 80, 0), 512: (255, 0, 60), 1024: (220, 0, 160)}


def _slide_left(row):
    vals = [v for v in row if v]; out = []; gain = 0; i = 0
    while i < len(vals):
        if i + 1 < len(vals) and vals[i] == vals[i + 1]:
            out.append(vals[i] * 2); gain += vals[i] * 2; i += 2
        else:
            out.append(vals[i]); i += 1
    return out + [0] * (4 - len(out)), gain


def _move2048(b, d):
    # d: 0 left, 1 right, 2 up, 3 down
    g = [r[:] for r in b]; gain = 0
    if d in (2, 3): g = [list(r) for r in zip(*g)]
    for i in range(4):
        row = g[i][::-1] if d in (1, 3) else g[i]
        row, gn = _slide_left(row); gain += gn
        g[i] = row[::-1] if d in (1, 3) else row
    if d in (2, 3): g = [list(r) for r in zip(*g)]
    return g, gain


_W2048 = [[15, 14, 13, 12], [8, 9, 10, 11], [7, 6, 5, 4], [0, 1, 2, 3]]


def _eval2048(b):
    s = sum(_W2048[r][c] * (b[r][c] ** 1.2) for r in range(4) for c in range(4))
    return s + 40 * sum(1 for r in b for v in r if not v)


def run(sec=30):
    def spawn(b):
        e = [(r, c) for r in range(4) for c in range(4) if not b[r][c]]
        if e:
            r, c = random.choice(e); b[r][c] = 4 if random.random() < 0.1 else 2
    def show(b):
        uh.clear()
        for r in range(4):
            for c in range(4):
                col = _T2048.get(b[r][c], (255, 255, 255))
                for dx in (0, 1):
                    for dy in (0, 1): px(2 * c + dx, 2 * r + dy, col)
        uh.show()
    t0 = time.time()
    while time.time() - t0 < sec:
        b = [[0] * 4 for _ in range(4)]; spawn(b); spawn(b)
        while time.time() - t0 < sec:
            best = None
            for d in range(4):
                nb, gn = _move2048(b, d)
                if nb == b: continue
                sc = _eval2048(nb) + gn + random.random()
                if best is None or sc > best[0]: best = (sc, nb)
            if best is None: break
            b = best[1]; spawn(b); show(b); time.sleep(0.22)
        flash((255, 255, 255), 2)

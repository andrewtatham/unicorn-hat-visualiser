"""Game of Life: Conway's Life with age colours and fading ghosts."""
import colorsys, random, time
from .display import uh, W, H


def run(sec=30):
    """Standard Conway's Life on a wrapped 8x8 grid. Age-coloured cells, fading ghosts of the dead,
    reseeds when the pattern dies, stalls or falls into a short loop."""
    t0 = time.time()
    while time.time() - t0 < sec:
        alive = {(x, y) for x in range(W) for y in range(H) if random.random() < 0.35}
        age = {c: 1 for c in alive}
        ghost = {}
        history = []
        for gen in range(80):
            if time.time() - t0 > sec:
                return
            for x in range(W):
                for y in range(H):
                    if (x, y) in alive:
                        a_ = age[(x, y)]
                        h = 0.55 + min(a_, 10) * 0.04          # blue -> green-yellow as it ages
                        r, g, b = colorsys.hsv_to_rgb(h % 1.0, 0.9, 1.0)
                        uh.set_pixel(x, y, int(r * 255), int(g * 255), int(b * 255))
                    else:
                        gh = ghost.get((x, y), 0)
                        uh.set_pixel(x, y, int(90 * gh), 0, int(60 * gh))
            uh.show(); time.sleep(0.3)
            nxt = set()
            for x in range(W):
                for y in range(H):
                    n = sum((((x + i) % W, (y + j) % H) in alive)
                            for i in (-1, 0, 1) for j in (-1, 0, 1) if (i or j))
                    if n == 3 or (n == 2 and (x, y) in alive):
                        nxt.add((x, y))
            ghost = {c: v * 0.6 for c, v in ghost.items() if v > 0.15}
            for c in alive - nxt:
                ghost[c] = 1.0
            age = {c: (age[c] + 1 if c in alive else 1) for c in nxt}
            key = frozenset(nxt)
            if not nxt or key in history[-6:]:
                time.sleep(0.8)
                break
            history.append(key)
            alive = nxt

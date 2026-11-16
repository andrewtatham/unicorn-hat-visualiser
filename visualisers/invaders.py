"""Space Invaders: A tiny invasion defended by a dodging cannon."""
import random, time
from .display import uh
from .common import flash, px


def run(sec=30):
    def new_aliens():
        a = {(c * 2, r) for c in range(3) for r in range(3) if random.random() > 0.15}
        return a or {(2, 1)}
    aliens = new_aliens(); ox = random.randint(0, 3); oy = 0; dirx = random.choice((-1, 1))
    cx = random.randint(0, 7); bullets = []; bombs = []; cd = 0; lives = 3; k = 0; hit_flash = 0
    t0 = time.time()
    while time.time() - t0 < sec:
        k += 1
        abs_al = {(ox + a, oy + b) for a, b in aliens}
        if k % 6 == 0:
            nx = ox + dirx
            if nx < 0 or nx > 3: dirx = -dirx; oy += 1
            else: ox = nx
            abs_al = {(ox + a, oy + b) for a, b in aliens}
        if abs_al and max(y for _, y in abs_al) >= 6:
            flash((255, 0, 0)); aliens = new_aliens(); ox = random.randint(0, 3); oy = 0; bombs = []; bullets = []; continue
        # cannon AI
        danger = [b for b in bombs if int(b[0]) == cx and 3 <= b[1] < 7]
        if danger:
            cx += 1 if cx < 4 else -1
        elif abs_al and k % 2 == 0:
            tx = min((x for x, _ in abs_al), key=lambda x: abs(x - cx))
            cx += (tx > cx) - (tx < cx)
        cx = max(0, min(7, cx))
        cd -= 1
        if cd <= 0 and any(x == cx for x, _ in abs_al):
            bullets.append([cx, 6]); cd = 11
        # bullets
        for b in bullets[:]:
            b[1] -= 1
            if (b[0], b[1]) in abs_al:
                aliens.discard((b[0] - ox, b[1] - oy)); abs_al.discard((b[0], b[1])); bullets.remove(b)
            elif b[1] < 0: bullets.remove(b)
        # bombs
        if k % 9 == 0 and abs_al:
            ax, ay = random.choice(sorted(abs_al)); bombs.append([ax, ay + 1.0])
        for b in bombs[:]:
            b[1] += 0.5
            if int(b[1]) >= 7 and int(b[0]) == cx:
                lives -= 1; hit_flash = 4; bombs.remove(b)
            elif b[1] > 7.5: bombs.remove(b)
        if lives <= 0:
            flash((255, 0, 0)); lives = 3
        if not aliens:
            flash((0, 255, 0)); aliens = new_aliens(); ox = random.randint(0, 3); oy = 0; bombs = []
        uh.clear()
        for (x, y) in abs_al: px(x, y, (0, 255, 80) if (y - oy) % 2 == 0 else (200, 0, 255))
        for b in bullets: px(b[0], b[1], (255, 255, 255))
        for b in bombs: px(b[0], b[1], (255, 40, 0))
        px(cx, 7, (255, 0, 0) if hit_flash else (0, 200, 255)); hit_flash = max(0, hit_flash - 1)
        for i in range(lives): px(7 - i, 7, (0, 80, 0)) if False else None
        uh.show(); time.sleep(0.07)

"""More self-playing visualizers for the 8x8 Unicorn HAT (y grows downward after the global 180 rotation)."""
import collections, colorsys, math, random, time
import unicornhat as uh

W = H = 8


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        uh.set_pixel(int(x), int(y), int(c[0]), int(c[1]), int(c[2]))


def hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def flash(color, n=3):
    for _ in range(n):
        for y in range(H):
            for x in range(W):
                px(x, y, color)
        uh.show(); time.sleep(0.12)
        uh.clear(); uh.show(); time.sleep(0.12)


# ------------------------------------------------------------------ Breakout
def breakout(sec=30):
    row_cols = [(255, 0, 0), (255, 140, 0), (255, 255, 0)]
    new_bricks = lambda: {(x, y) for x in range(W) for y in range(3)}
    bricks = new_bricks(); lives = 3; pad = 3.5; err = 0
    def serve():
        return 3.5, 5.0, random.choice((-0.3, 0.3)), -0.4
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


# ------------------------------------------------------------------ Space invaders
def invaders(sec=30):
    def new_aliens(): return {(c * 2, r) for c in range(3) for r in range(3)}
    aliens = new_aliens(); ox = oy = 0; dirx = 1
    cx = 3; bullets = []; bombs = []; cd = 0; lives = 3; k = 0; hit_flash = 0
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
            flash((255, 0, 0)); aliens = new_aliens(); ox = oy = 0; bombs = []; bullets = []; continue
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
            flash((0, 255, 0)); aliens = new_aliens(); ox = oy = 0; bombs = []
        uh.clear()
        for (x, y) in abs_al: px(x, y, (0, 255, 80) if (y - oy) % 2 == 0 else (200, 0, 255))
        for b in bullets: px(b[0], b[1], (255, 255, 255))
        for b in bombs: px(b[0], b[1], (255, 40, 0))
        px(cx, 7, (255, 0, 0) if hit_flash else (0, 200, 255)); hit_flash = max(0, hit_flash - 1)
        for i in range(lives): px(7 - i, 7, (0, 80, 0)) if False else None
        uh.show(); time.sleep(0.07)


# ------------------------------------------------------------------ Maze
def maze(rounds=2):
    N = 7
    for _ in range(rounds):
        g = [[1] * N for _ in range(N)]
        g[0][0] = 0; stack = [(0, 0)]
        def draw(head=None, trail=None):
            uh.clear()
            for y in range(N):
                for x in range(N):
                    if g[y][x]: px(x, y, (0, 0, 70))
            if trail:
                for i, (x, y) in enumerate(trail): px(x, y, hsv(0.55 + i * 0.02, 1, 0.5 + 0.5 * i / max(1, len(trail))))
            if head: px(head[0], head[1], (255, 255, 255))
            uh.show()
        while stack:
            x, y = stack[-1]
            nb = [(dx, dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
                  if 0 <= x + dx < N and 0 <= y + dy < N and g[y + dy][x + dx]]
            if nb:
                dx, dy = random.choice(nb)
                g[y + dy // 2][x + dx // 2] = 0; g[y + dy][x + dx] = 0
                stack.append((x + dx, y + dy)); draw((x + dx, y + dy)); time.sleep(0.06)
            else:
                stack.pop()
        prev = {(0, 0): None}; q = collections.deque([(0, 0)])
        while q:
            c = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + dx, c[1] + dy)
                if 0 <= n[0] < N and 0 <= n[1] < N and not g[n[1]][n[0]] and n not in prev:
                    prev[n] = c; q.append(n)
        path, c = [], (N - 1, N - 1)
        while c: path.append(c); c = prev[c]
        path.reverse()
        for i in range(len(path)):
            draw(path[i], path[:i]); time.sleep(0.09)
        draw(None, path); px(N - 1, N - 1, (0, 255, 0)); uh.show(); time.sleep(1.2)


# ------------------------------------------------------------------ Falling sand (gravity rotates)
def sand(sec=28):
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


# ------------------------------------------------------------------ Langton's ant
def ant(sec=25):
    cells = [[0] * W for _ in range(W)]
    x = y = 3; d = 0; t0 = time.time(); steps = 0
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


# ------------------------------------------------------------------ 2048 AI (4x4 board, 2x2 pixels per tile)
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


def g2048(sec=30):
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


# ------------------------------------------------------------------ Sorting visualizer
def _bubble(a):
    for i in range(len(a)):
        for j in range(len(a) - 1 - i):
            yield (j, j + 1)
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]; yield (j, j + 1)


def _insertion(a):
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]; yield (j - 1, j); j -= 1


def _selection(a):
    for i in range(len(a)):
        m = i
        for j in range(i + 1, len(a)):
            yield (m, j)
            if a[j] < a[m]: m = j
        if m != i: a[i], a[m] = a[m], a[i]; yield (i, m)


def _quick(a, lo=0, hi=None):
    if hi is None: hi = len(a) - 1
    if lo >= hi: return
    p = a[hi]; i = lo
    for j in range(lo, hi):
        yield (j, hi)
        if a[j] < p:
            a[i], a[j] = a[j], a[i]; yield (i, j); i += 1
    a[i], a[hi] = a[hi], a[i]; yield (i, hi)
    yield from _quick(a, lo, i - 1)
    yield from _quick(a, i + 1, hi)


def sorting(rounds=4):
    algs = [_bubble, _insertion, _quick, _selection]
    random.shuffle(algs)
    for alg in algs[:rounds]:
        a = list(range(1, 9)); random.shuffle(a)
        def draw(hl=()):
            uh.clear()
            for i, v in enumerate(a):
                for y in range(8 - v, 8):
                    px(i, y, (255, 255, 255) if i in hl else hsv(v / 10.0, 1, 0.9))
            uh.show()
        draw(); time.sleep(0.4)
        for hl in alg(a):
            draw(hl); time.sleep(0.09)
        for i in range(8):
            draw(); px(i, 0, (0, 0, 0))
            for k in range(i + 1):
                for y in range(8 - a[k], 8): px(k, y, (0, 255, 0))
            uh.show(); time.sleep(0.05)
        time.sleep(0.5)


# ------------------------------------------------------------------ Pac-Man chase
_PAC_MAP = ["........",
            ".##..##.",
            "........",
            ".#.##.#.",
            "........",
            ".##..##.",
            "........",
            "........"]


def pacman(sec=30):
    wall = {(x, y) for y, r in enumerate(_PAC_MAP) for x, ch in enumerate(r) if ch == "#"}
    def nbrs(c):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in wall: yield n
    def bfs_first(src, goals, blocked=()):
        prev = {src: None}; q = collections.deque([src])
        while q:
            c = q.popleft()
            if c in goals and c != src:
                while prev[c] != src: c = prev[c]
                return c
            for n in nbrs(c):
                if n not in prev and n not in blocked: prev[n] = c; q.append(n)
        return None
    def reset_dots(): return {(x, y) for y in range(H) for x in range(W) if (x, y) not in wall} - {(0, 0)}
    dots = reset_dots(); pac = (0, 0); ghost = (7, 7); k = 0; t0 = time.time()
    while time.time() - t0 < sec:
        k += 1
        near = {ghost} | set(nbrs(ghost))
        nxt = bfs_first(pac, dots, near)
        if nxt is None:
            opts = [n for n in nbrs(pac) if n != ghost]
            nxt = max(opts, key=lambda n: abs(n[0] - ghost[0]) + abs(n[1] - ghost[1])) if opts else pac
        pac = nxt; dots.discard(pac)
        if k % 2 == 0:
            if random.random() < 0.75:
                g = bfs_first(ghost, {pac})
                ghost = g if g else ghost
            else:
                ghost = random.choice(list(nbrs(ghost)))
        uh.clear()
        for c in wall: px(c[0], c[1], (0, 0, 110))
        for c in dots: px(c[0], c[1], (70, 70, 70))
        px(ghost[0], ghost[1], (255, 0, 0)); px(pac[0], pac[1], (255, 220, 0))
        uh.show(); time.sleep(0.2)
        if pac == ghost:
            flash((255, 0, 0), 2); pac = (0, 0); ghost = (7, 7)
        if not dots:
            flash((255, 220, 0), 2); dots = reset_dots(); pac = (0, 0); ghost = (7, 7)


# ------------------------------------------------------------------ Pi dashboard
def _cpu_times():
    out = []
    try:
        for line in open("/proc/stat"):
            if line.startswith("cpu") and line[3].isdigit():
                v = list(map(int, line.split()[1:])); out.append((v[3] + v[4], sum(v)))
    except OSError:
        pass
    return out


def _net_bytes():
    try:
        tot = 0
        for line in list(open("/proc/net/dev"))[2:]:
            name, data = line.split(":");
            if name.strip() != "lo": tot += int(data.split()[0]) + int(data.split()[8])
        return tot
    except OSError:
        return 0


def _bar(x, level, hue_lo=0.33, hue_hi=0.0):
    level = max(0, min(8, int(round(level))))
    for i in range(level):
        px(x, 7 - i, hsv(hue_lo + (hue_hi - hue_lo) * i / 7.0, 1, 0.9))


def dashboard(sec=15):
    prev = _cpu_times(); pn = _net_bytes(); t0 = time.time(); pt = t0
    while time.time() - t0 < sec:
        time.sleep(0.5)
        cur = _cpu_times(); now = time.time(); nb = _net_bytes()
        uh.clear()
        for i, (a, b) in enumerate(zip(prev, cur)):
            idle, tot = b[0] - a[0], b[1] - a[1]
            _bar(i, 8 * (1 - idle / tot) if tot else 0)
        try: temp = int(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000.0
        except OSError: temp = 40.0
        _bar(5, (temp - 30) / 55.0 * 8)
        try:
            mi = {l.split(":")[0]: int(l.split()[1]) for l in open("/proc/meminfo")}
            mem = 1 - mi["MemAvailable"] / mi["MemTotal"]
        except (OSError, KeyError): mem = 0.3
        _bar(6, mem * 8)
        rate = (nb - pn) / max(0.01, now - pt)
        _bar(7, math.log10(rate + 1) / 6 * 8, 0.55, 0.85)
        uh.show(); prev, pn, pt = cur, nb, now


# ------------------------------------------------------------------ Binary clock
def binary_clock(sec=15):
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


def run_all():
    breakout(); invaders(); maze(); sand(); ant(); g2048(); sorting(); pacman(); dashboard(); binary_clock()

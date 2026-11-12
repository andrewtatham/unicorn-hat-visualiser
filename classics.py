"""Ports of the classic Pimoroni unicorn-hat examples as timed effects (no numpy)."""
import colorsys, math, random, time
import unicornhat as uh

W = H = 8


def _clamp(v):
    return int(max(0, min(255, v)))


# ---------- shader effects from examples/demo.py ----------
def swirl(x, y, step):
    x -= W / 2; y -= H / 2
    dist = math.sqrt(x * x + y * y) / 2.0
    angle = step / 10.0 + dist * 1.5
    s, c = math.sin(angle), math.cos(angle)
    xs = x * c - y * s; ys = x * s + y * c
    r = abs(xs + ys) * 64.0 - 20
    return (r, r + s * 130, r + c * 130)


def checker(x, y, step):
    x -= W / 2; y -= H / 2
    angle = step / 10.0
    s, c = math.sin(angle), math.cos(angle)
    xs = x * c - y * s; ys = x * s + y * c
    xs -= math.sin(step / 200.0) * 40.0
    ys -= math.cos(step / 200.0) * 40.0
    scale = math.sin(step / 50.0) / 8.0 + 0.25
    xs *= scale; ys *= scale
    xo = abs(xs) - int(abs(xs)); yo = abs(ys) - int(abs(ys))
    l = 0 if (math.floor(xs) + math.floor(ys)) % 2 else 1 if xo > .1 and yo > .1 else .5
    r, g, b = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, l)
    return (r * 255, g * 255, b * 255)


def blues_and_twos(x, y, step):
    x -= W / 2; y -= H / 2
    scale = math.sin(step / 6.0) / 1.5
    r = math.sin(x * scale) + math.cos(y * scale)
    b = math.sin(x * scale / 2.0) + math.cos(y * scale / 2.0)
    g = max(0, r - .8)
    b -= r; b /= 1.4
    return (g * 255, (b + g) * 255, r * 255)  # swapped so it reads blue


def rainbow_search(x, y, step):
    xs = math.sin(step / 100.0) * 20.0
    ys = math.cos(step / 100.0) * 20.0
    scale = (math.sin(step / 60.0) + 1.0) / 5.0 + 0.2
    r = math.sin((x + xs) * scale) + math.cos((y + xs) * scale)
    g = math.sin((x + xs) * scale) + math.cos((y + ys) * scale)
    b = math.sin((x + ys) * scale) + math.cos((y + ys) * scale)
    return (r * 255, g * 255, b * 255)


def tunnel(x, y, step):
    speed = step / 100.0
    x -= W / 2; y -= H / 2
    x += math.sin(step / 27.0) * 2
    y += math.cos(step / 18.0) * 2
    if y == 0:
        angle = -(math.pi / 2) if x < 0 else (math.pi / 2)
    else:
        angle = math.atan(x / y)
    if y > 0:
        angle += math.pi
    angle /= 2 * math.pi
    shade = min(1, math.sqrt(x * x + y * y) / 2.1)
    angle += speed
    depth = speed + math.sqrt(x * x + y * y) / 10
    col1 = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, .8)
    col2 = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, .3)
    col = col1 if int(abs(angle * 6.0)) % 2 == 0 else col2
    td = .3 if int(abs(depth * 3.0)) % 2 == 0 else 0
    return tuple((c + td) * shade * 255 for c in col)


def classic_rainbow(x, y, step):
    i = step * 0.3
    r = (math.cos((x + i) / 2.0) + math.cos((y + i) / 2.0)) * 64.0 + 128.0
    g = (math.sin((x + i) / 1.5) + math.sin((y + i) / 2.0)) * 64.0 + 128.0
    b = (math.sin((x + i) / 2.0) + math.cos((y + i) / 1.5)) * 64.0 + 128.0
    return (r + 30, g + 30, b + 30)


def rainbow_blinky(x, y, step):
    seq = list(range(1, 10)[::-1]) + list(range(1, 10))
    z = seq[(step // 2) % len(seq)]
    fwhm = 5.0 / z
    g = math.exp(-4 * math.log(2) * ((x - 3.5) ** 2 + (y - 3.5) ** 2) / fwhm ** 2)
    r, gg, b = colorsys.hsv_to_rgb(1.0 / (x + y + 1), 0.8, g)
    return (r * 255, gg * 255, b * 255)


def shader(fn, sec, fps=60):
    t0 = time.time(); step = 0
    while time.time() - t0 < sec:
        for y in range(H):
            for x in range(W):
                r, g, b = fn(x, y, step)
                uh.set_pixel(x, y, _clamp(r), _clamp(g), _clamp(b))
        uh.show(); step += 1; time.sleep(1.0 / fps)


# ---------- other examples ----------
def random_blinky(sec=6):
    t0 = time.time()
    while time.time() - t0 < sec:
        for y in range(H):
            for x in range(W):
                v = random.random()
                r, g, b = colorsys.hsv_to_rgb(0.1 * v, 0.8, v)
                uh.set_pixel(x, y, int(r * 255), int(g * 255), int(b * 255))
        uh.show(); time.sleep(0.08)


def random_sparkles(sec=6):
    uh.clear(); t0 = time.time()
    while time.time() - t0 < sec:
        uh.set_pixel(random.randint(0, 7), random.randint(0, 7),
                     random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        uh.show(); time.sleep(0.01)


def snow(sec=8):
    rows = [[0] * W for _ in range(H)]
    t0 = time.time()
    while time.time() - t0 < sec:
        rows.pop()                       # drop the bottom row, new flakes at top
        new = [0] * W; new[random.randint(0, W - 1)] = 50 + random.randint(0, 155)
        rows.insert(0, new)
        for y in range(H):
            for x in range(W):
                v = rows[y][x]; uh.set_pixel(x, y, v, v, v)
        uh.show(); time.sleep(0.2)


def cross(sec=8):
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


def _sp(x, y, r, g, b):
    uh.set_pixel(x, H - 1 - y, r, g, b)  # bucket floor at the bottom for this mounting


def drop(rounds=1):
    """Bucket that fills with randomly coloured balls."""
    def setup():
        uh.clear()
        for b in range(H): _sp(0, b, 255, 255, 255); _sp(W - 1, b, 255, 255, 255)
        for b in range(1, W - 1): _sp(b, 0, 255, 255, 255)
        uh.show()
    for _ in range(rounds):
        setup()
        heights = [0] * (W - 2)
        for _ in range((W - 2) * (H - 1)):
            cols = [c for c in range(W - 2) if heights[c] < H - 1]
            if not cols: break
            c = random.choice(cols)
            col = [random.randint(100, 255) for _ in range(3)]
            y = H - 1
            for _ in range((H - 2) - heights[c]):
                _sp(c + 1, y, *col); uh.show(); time.sleep(0.03)
                _sp(c + 1, y, 0, 0, 0); y -= 1
            _sp(c + 1, y, *col); uh.show()
            heights[c] += 1
        time.sleep(1)


def matrix(sec=10):
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


def game_of_life(sec=30):
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


def candle(sec=12):
    pal = []
    for i in range(256):
        h = i / 5.0 / 360.0
        s = max(0.0, min(1.0, 1.0 / (math.sqrt(i / 50.0) + 0.01)))
        v = i / 200.0
        if i < 60: v /= 2
        r, g, b = colorsys.hsv_to_rgb(h, s, max(0.0, min(1.0, v)))
        pal.append((int(r * 255), int(g * 255), int(b * 255)))
    # 16-wide buffer like the original so the flame can sway
    buf = [0.0] * 256; step = 0; t0 = time.time()

    def get(b, x, y):
        if x < 0 or y < 0 or x >= 16 or y >= 16: return 0
        if isinstance(x, float) and x < 15:
            f = x - int(x)
            return b[int(y) * 16 + int(x)] * (1 - f) + b[int(y) * 16 + int(x) + 1] * f
        return b[int(y) * 16 + int(x)]
    if True:
        while time.time() - t0 < sec:
            step += random.randint(0, 15)
            tmp = buf[:]
            for x in (1, 2, 3, 4):
                for y in (6, 7):
                    buf[y * 16 + x] = 500
            for x in range(8):
                for y in range(8):
                    s = math.sin(y / 30.0 + step / 10.0) * ((16 - y) / 20.0)
                    v = 0
                    for i in range(3):
                        for j in range(3):
                            v += get(buf, x + i + s - 1, y + j)
                    tmp[y * 16 + x] = v / 12
            buf = tmp
            for x in range(8):
                for y in range(8):
                    uh.set_pixel(x, y, *pal[max(0, min(255, int(get(buf, x, y))))])
            uh.show(); time.sleep(0.03)


def run_all():
    shader(classic_rainbow, 8)
    shader(rainbow_blinky, 8)
    shader(tunnel, 10)
    shader(rainbow_search, 8)
    shader(checker, 10)
    shader(swirl, 8)
    shader(blues_and_twos, 8)
    random_blinky(); random_sparkles(); snow(); cross()
    matrix(); drop(); game_of_life(); candle()

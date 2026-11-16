"""Pac-Man: Full maze, four ghosts, power pills, and an 8x8 window that scrolls with Pac-Man."""
import collections, random, time
from .display import uh, W, H
from .common import flash, px


# Each row is the left half of the maze (11 chars, last one is the centre column); it is mirrored to make 21 columns.
#   # wall   . dot   o power pill   - ghost-house door   (space) empty floor
_PAC_HALF = ["###########",
             "#o....#....",
             "#.###.#.##.",
             "#..........",
             "#.###.#.###",
             "#.....#....",
             "#####.#.##.",
             "#####.#....",
             "#####.#.##-",
             "........#  ",
             "#####.#.###",
             "#####.#....",
             "#####.#.##.",
             "#..........",
             "#.###.###.#",
             "#o..#.....",
             "###.#.#.###",
             "#.....#....",
             "#.#######.#",
             "#..........",
             "###########"]


_PAC_MAP = [r + r[-2::-1] for r in (h.ljust(11, ".") for h in _PAC_HALF)]


PW, PH = len(_PAC_MAP[0]), len(_PAC_MAP)


_PAC_EXIT = (10, 7)                                  # the cell just outside the ghost-house door


_PAC_HOUSE = [(9, 9), (10, 9), (11, 9)]


_PAC_START = (10, 15)


_PAC_SLOW = 4                                        # ghosts skip every Nth tick


_PAC_FRIGHT = 45                                     # ticks a power pill lasts


_PAC_COLS = {"blinky": (255, 0, 0), "pinky": (255, 90, 190), "inky": (0, 220, 255), "clyde": (255, 140, 0)}


_PAC_CORNER = {"blinky": (PW - 1, 0), "pinky": (0, 0), "inky": (PW - 1, PH - 1), "clyde": (0, PH - 1)}


_PAC_RELEASE = {"blinky": 0, "pinky": 12, "inky": 35, "clyde": 60}


class _PacGame:
    def __init__(self):
        self.wall = {(x, y) for y, r in enumerate(_PAC_MAP) for x, ch in enumerate(r) if ch in "#-"}
        self.dots0 = {(x, y) for y, r in enumerate(_PAC_MAP) for x, ch in enumerate(r) if ch == "."}
        self.pills0 = {(x, y) for y, r in enumerate(_PAC_MAP) for x, ch in enumerate(r) if ch == "o"}
        self.house = set(_PAC_HOUSE)
        self.lives = 3; self.level = 1
        self.new_level(); self.reset_actors()

    # ---- helpers
    def nbrs(self, c):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = ((c[0] + dx) % PW, c[1] + dy)             # columns wrap: that's the tunnel
            if 0 <= n[1] < PH and n not in self.wall and n not in self.house:
                yield n

    def new_level(self):
        self.dots = set(self.dots0); self.pills = set(self.pills0); self.dots.discard(_PAC_START)

    def reset_actors(self):
        self.pac = _PAC_START; self.dir = (-1, 0); self.fright = 0; self.tick = 0
        self.ghosts = []
        for i, name in enumerate(_PAC_COLS):
            g = dict(name=name, mode="house", pos=_PAC_HOUSE[i % 3] if i else _PAC_EXIT, prev=None,
                     timer=max(0, _PAC_RELEASE[name] - 6 * (self.level - 1)), afraid=False)
            if name == "blinky": g["mode"] = "out"
            self.ghosts.append(g)
        self.cam = None

    def dist_from(self, sources):
        d = {s: 0 for s in sources}; q = collections.deque(sources)
        while q:
            c = q.popleft()
            for n in self.nbrs(c):
                if n not in d: d[n] = d[c] + 1; q.append(n)
        return d

    # ---- Pac-Man's brain: a safe-path BFS
    def pac_move(self):
        danger = [g["pos"] for g in self.ghosts if g["mode"] == "out" and not g["afraid"]]
        dang = self.dist_from(danger) if danger else {}
        pac = self.pac
        dist = {pac: 0}; first = {}; q = collections.deque([pac])
        while q:
            c = q.popleft()
            ns = list(self.nbrs(c)); random.shuffle(ns)
            for n in ns:
                nd = dist[c] + 1
                if n not in dist and dang.get(n, 99) > nd:
                    dist[n] = nd; first[n] = n if c == pac else first[c]; q.append(n)
        def nearest(cells, limit=999):
            ok = [(dist[c], c) for c in cells if c in dist and dist[c] <= limit]
            return first[min(ok, key=lambda t: t[0])[1]] if ok else None
        threat = dang.get(pac, 99)
        step = None
        if threat <= 9 and self.pills:
            step = nearest(self.pills, 20)                          # in trouble: run for a power pill
        if step is None and self.fright > 3:
            step = nearest([g["pos"] for g in self.ghosts if g["afraid"] and g["mode"] == "out"], self.fright - 3)
        if step is None:
            step = nearest(self.dots)
        if step is None:
            step = nearest(self.pills)
        if step is None:                                            # nowhere safe to eat: put distance on the ghosts
            opts = [n for n in self.nbrs(pac)]
            if opts:
                random.shuffle(opts)
                step = max(opts, key=lambda n: dang.get(n, 99))
            else:
                step = pac
        self.dir = (max(-1, min(1, (step[0] - pac[0] + (PW // 2)) % PW - PW // 2)), step[1] - pac[1])
        self.pac = step
        self.dots.discard(step)
        if step in self.pills:
            self.pills.discard(step); self.fright = _PAC_FRIGHT
            for g in self.ghosts:
                if g["mode"] == "out": g["afraid"] = True; g["prev"] = None

    # ---- ghosts
    def target(self, g):
        px_, py_ = self.pac; dx, dy = self.dir
        scatter = self.tick % 110 < 28
        if scatter and not g["afraid"]:
            return _PAC_CORNER[g["name"]]
        n = g["name"]
        if n == "blinky": return self.pac
        if n == "pinky": return (px_ + 4 * dx, py_ + 4 * dy)
        if n == "inky":
            b = next(o for o in self.ghosts if o["name"] == "blinky")["pos"]
            return (2 * (px_ + 2 * dx) - b[0], 2 * (py_ + 2 * dy) - b[1])
        gx, gy = g["pos"]
        return self.pac if (gx - px_) ** 2 + (gy - py_) ** 2 > 64 else _PAC_CORNER["clyde"]

    def ghost_move(self, g):
        if g["mode"] == "house":
            g["timer"] -= 1
            if g["timer"] <= 0:
                g["pos"] = _PAC_EXIT; g["mode"] = "out"; g["prev"] = None; g["afraid"] = self.fright > 0
            return
        if g["mode"] == "eyes":
            if g["pos"] == _PAC_EXIT:
                g["mode"] = "house"; g["pos"] = _PAC_HOUSE[1]; g["timer"] = 10; g["afraid"] = False
                return
            d = self.dist_from([_PAC_EXIT])
            g["pos"] = min(self.nbrs(g["pos"]), key=lambda n: d.get(n, 999))
            return
        if g["afraid"] and self.tick % 2: return                   # frightened ghosts are slow
        if self.tick % _PAC_SLOW == 0: return                      # ghosts are a touch slower than Pac-Man
        cand = list(self.nbrs(g["pos"]))
        fwd = [n for n in cand if n != g["prev"]]
        cand = fwd or cand
        if g["afraid"]:
            nxt = random.choice(cand)
        else:
            t = self.target(g); random.shuffle(cand)
            nxt = min(cand, key=lambda n: (n[0] - t[0]) ** 2 + (n[1] - t[1]) ** 2)
        g["prev"] = g["pos"]; g["pos"] = nxt

    def collide(self):
        """Returns 'dead' if Pac-Man was caught; eats frightened ghosts."""
        for g in self.ghosts:
            if g["mode"] == "out" and g["pos"] == self.pac:
                if g["afraid"]: g["mode"] = "eyes"; g["afraid"] = False
                else: return "dead"
        return None

    def step(self):
        """One game tick. Returns None, 'dead' or 'clear'."""
        self.tick += 1
        old = {id(g): g["pos"] for g in self.ghosts}; old_pac = self.pac
        self.pac_move()
        r = self.collide()
        if r: return r
        for g in self.ghosts: self.ghost_move(g)
        r = self.collide()
        if r: return r
        for g in self.ghosts:                                        # passed through each other head-on
            if g["mode"] == "out" and g["pos"] == old_pac and old[id(g)] == self.pac:
                if g["afraid"]: g["mode"] = "eyes"; g["afraid"] = False
                else: return "dead"
        if self.fright:
            self.fright -= 1
            if not self.fright:
                for g in self.ghosts: g["afraid"] = False
        if not self.dots and not self.pills: return "clear"
        return None

    # ---- drawing: an 8x8 window that follows Pac-Man
    def camera(self):
        x, y = self.pac
        if self.cam is None:
            cx, cy = x - 4, y - 4
        else:
            cx, cy = self.cam
            if x < cx + 2: cx = x - 2
            if x > cx + 5: cx = x - 5
            if y < cy + 2: cy = y - 2
            if y > cy + 5: cy = y - 5
        self.cam = (max(0, min(PW - W, cx)), max(0, min(PH - H, cy)))
        return self.cam

    def draw(self):
        cx, cy = self.camera()
        uh.clear()
        def put(c, col):
            px(c[0] - cx, c[1] - cy, col)
        for c in self.wall:
            if cx <= c[0] < cx + W and cy <= c[1] < cy + H:
                put(c, (0, 0, 110) if _PAC_MAP[c[1]][c[0]] == "#" else (110, 60, 90))
        for c in self.dots: put(c, (70, 70, 70))
        pill = (255, 200, 200) if self.tick % 4 < 2 else (120, 70, 70)
        for c in self.pills: put(c, pill)
        for g in self.ghosts:
            if g["mode"] == "house": continue
            if g["mode"] == "eyes": col = (120, 120, 120)
            elif g["afraid"]: col = (255, 255, 255) if (self.fright < 14 and self.tick % 2) else (30, 30, 255)
            else: col = _PAC_COLS[g["name"]]
            put(g["pos"], col)
        put(self.pac, (255, 220, 0) if self.tick % 2 else (200, 150, 0))
        uh.show()


_pac_game = None


def run(sec=60):
    """Full Pac-Man: scrolling window over a 21x21 maze, 4 ghosts, power pills. The game carries on between runs."""
    global _pac_game
    if _pac_game is None: _pac_game = _PacGame()
    t0 = time.time()
    while time.time() - t0 < sec:
        G_ = _pac_game
        G_.draw(); time.sleep(0.17 if not G_.fright else 0.15)
        r = G_.step()
        if r == "dead":
            G_.draw(); flash((255, 0, 0), 2); G_.lives -= 1
            if G_.lives <= 0: G_.lives = 3; G_.level = 1; G_.new_level()
            G_.reset_actors()
        elif r == "clear":
            flash((255, 220, 0), 3); G_.level += 1; G_.new_level(); G_.reset_actors()

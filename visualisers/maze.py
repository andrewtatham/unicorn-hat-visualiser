"""Maze solver: Carves a big maze and loops it, then an explorer finds the goal and the shortest route lights up."""
import collections, random, time
from .display import uh, W, H
from .common import hsv, px

N = 31                                   # tiles per side; corridors sit on odd coordinates, walls on even
START, GOAL = (1, 1), (N - 2, N - 2)
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
WALL, DEAD, START_C = (0, 0, 80), (70, 6, 6), (200, 0, 160)


def _carve_steps(g):
    """Recursive-backtracker generator: yields each newly opened cell."""
    g[START[1]][START[0]] = 0; stack = [START]
    while stack:
        x, y = stack[-1]
        nb = [(dx, dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
              if 0 < x + dx < N - 1 and 0 < y + dy < N - 1 and g[y + dy][x + dx]]
        if nb:
            dx, dy = random.choice(nb)
            g[y + dy // 2][x + dx // 2] = 0; g[y + dy][x + dx] = 0
            stack.append((x + dx, y + dy))
            yield (x + dx, y + dy)
        else:
            stack.pop()


def _braid(g, fraction=0.07):
    """Knock out some walls between two corridors so there are loops and more than one route."""
    cands = [(x, y) for y in range(1, N - 1) for x in range(1, N - 1) if g[y][x]
             and ((x % 2 == 0 and y % 2 == 1 and not g[y][x - 1] and not g[y][x + 1])
                  or (x % 2 == 1 and y % 2 == 0 and not g[y - 1][x] and not g[y + 1][x]))]
    random.shuffle(cands)
    for x, y in cands[:int(len(cands) * fraction)]: g[y][x] = 0


def _open_nbrs(g, c):
    return [(c[0] + dx, c[1] + dy) for dx, dy in DIRS if not g[c[1] + dy][c[0] + dx]]


def _shortest(g):
    prev = {START: None}; q = collections.deque([START])
    while q:
        c = q.popleft()
        if c == GOAL: break
        for n in _open_nbrs(g, c):
            if n not in prev: prev[n] = c; q.append(n)
    path, c = [], GOAL
    while c: path.append(c); c = prev[c]
    return path[::-1]


def _explore_steps(g, greed):
    """Depth-first explorer that physically walks (and backtracks). greed = chance it heads towards the goal.
    Yields (position, route-so-far, dead-ends)."""
    stack = [START]; seen = {START}; dead = set()
    while stack[-1] != GOAL:
        here = stack[-1]
        nb = [n for n in _open_nbrs(g, here) if n not in seen]
        if nb:
            if random.random() < greed:
                nb.sort(key=lambda n: abs(n[0] - GOAL[0]) + abs(n[1] - GOAL[1])); nxt = nb[0]
            else:
                nxt = random.choice(nb)
            seen.add(nxt); stack.append(nxt)
        else:
            dead.add(stack.pop())
        yield stack[-1], stack, dead


def run(rounds=1):
    for _ in range(rounds):
        g = [[1] * N for _ in range(N)]
        cam = [0, 0]; tick = [0]

        def follow(c):
            x, y = c
            if x < cam[0] + 2: cam[0] = x - 2
            if x > cam[0] + W - 3: cam[0] = x - (W - 3)
            if y < cam[1] + 2: cam[1] = y - 2
            if y > cam[1] + H - 3: cam[1] = y - (H - 3)
            cam[0] = max(0, min(N - W, cam[0])); cam[1] = max(0, min(N - H, cam[1]))

        def draw(head=None, route=(), dead=(), lit=()):
            tick[0] += 1
            uh.clear()
            for wy in range(H):
                for wx in range(W):
                    c = (cam[0] + wx, cam[1] + wy)
                    if g[c[1]][c[0]]: px(wx, wy, WALL)
                    elif c in dead: px(wx, wy, DEAD)
            for i, c in enumerate(route):
                px(c[0] - cam[0], c[1] - cam[1], hsv(0.5 + 0.0035 * i, 1, 0.35 + 0.5 * min(1, i / max(1, len(route)))))
            for c in lit: px(c[0] - cam[0], c[1] - cam[1], (255, 200, 0))
            px(START[0] - cam[0], START[1] - cam[1], START_C)
            px(GOAL[0] - cam[0], GOAL[1] - cam[1], (0, 255, 0) if tick[0] % 4 < 2 else (0, 90, 0))
            if head: px(head[0] - cam[0], head[1] - cam[1], (255, 255, 255))
            uh.show()

        follow(START)
        for c in _carve_steps(g):                                    # 1. watch the maze being dug
            follow(c); draw(c); time.sleep(0.025)
        _braid(g)                                                    # 2. open a few loops
        for _ in range(3):
            draw(); time.sleep(0.12); uh.clear(); uh.show(); time.sleep(0.08)
        follow(START); draw(START); time.sleep(0.5)
        greed = random.choice((0.3, 0.6, 0.85))                      # 3. an explorer wanders in (dead ends glow red)
        for pos, route, dead in _explore_steps(g, greed):
            follow(pos); draw(pos, route, dead); time.sleep(0.03)
        time.sleep(0.4)
        best = _shortest(g); follow(START)                           # 4. reveal the shortest route
        for i, c in enumerate(best):
            follow(c); draw(c, (), (), best[:i]); time.sleep(0.05)
        for _ in range(4):
            draw(GOAL, (), (), best); time.sleep(0.15)
        time.sleep(0.8)

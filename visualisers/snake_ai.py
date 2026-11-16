"""Snake decision logic, kept display-free so it can be tested headless. Board is 8x8, y grows downward."""
import collections, random

W = H = 8
LONG = 18          # switch to the space-aware strategy once the snake is this long


def neighbors(p):
    x, y = p
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H:
            yield nx, ny


def bfs(start, goal, blocked):
    q = collections.deque([start]); prev = {start: None}
    while q:
        c = q.popleft()
        if c == goal:
            path = []
            while c != start:
                path.append(c); c = prev[c]
            return path[::-1]
        for n in neighbors(c):
            if n not in prev and n not in blocked:
                prev[n] = c; q.append(n)
    return None


def flood(start, blocked):
    seen = {start}; stack = [start]
    while stack:
        c = stack.pop()
        for m in neighbors(c):
            if m not in seen and m not in blocked:
                seen.add(m); stack.append(m)
    return seen


def after_move(snake, move, eating):
    """Snake body (head first) after taking `move`."""
    return [move] + (list(snake) if eating else list(snake)[:-1])


def tail_reachable(new):
    """Can the head still get to its own tail? (a snake that can chase its tail can never be trapped)"""
    blocked = set(new[1:-1])
    return new[-1] in flood(new[0], blocked) if len(new) > 1 else True


def hugging(cell, blocked):
    """How many of the cell's four sides are wall or body: high = tucked along an edge."""
    x, y = cell
    n = 0
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        c = (x + dx, y + dy)
        if not (0 <= c[0] < W and 0 <= c[1] < H) or c in blocked:
            n += 1
    return n


def choose(snake, food):
    """Return the next head cell, or None if trapped. `snake` is head-first."""
    snake = list(snake)
    head = snake[0]
    body_wo_tail = set(snake[:-1])
    options = [n for n in neighbors(head) if n not in body_wo_tail]
    if not options:
        return None
    long_mode = len(snake) >= LONG
    scored = []
    for m in options:
        eating = (m == food)
        new = after_move(snake, m, eating)
        blocked = set(new[1:-1])
        area = len(flood(m, blocked))
        free_total = W * H - len(new) + 1          # free cells + the cell the head sits on... (approx.)
        safe = tail_reachable(new)
        pathf = bfs(m, food, set(new[1:])) if not eating and food else None
        dist = 0 if eating else (len(pathf) if pathf else 99)
        scored.append(dict(m=m, area=area, safe=safe, dist=dist, eating=eating,
                           hug=hugging(m, set(new[1:])), cut=max(0, free_total - area)))
    safe = [s for s in scored if s["safe"]] or scored
    if not long_mode:
        # lively early game: head for the food by the shortest route if that stays safe
        pick = min(safe, key=lambda s: (s["dist"], -s["area"]))
        return pick["m"]
    # long snake: keep the most room (don't cut the board in two), hug edges, and eat only when it costs no space
    best_area = max(s["area"] for s in safe)
    roomy = [s for s in safe if s["area"] >= best_area - 1]
    def key(s):
        return (-s["cut"] * 0 + s["hug"] * 2 - s["dist"] * 0.7 + (6 if s["eating"] else 0) + random.random() * 0.1)
    return max(roomy, key=key)["m"]


def choose_old(snake, food):
    """The previous logic, kept for comparison in tests."""
    snake = list(snake)
    head = snake[0]
    body_wo_tail = set(snake[:-1])
    path = bfs(head, food, body_wo_tail)
    if path:
        return path[0]
    best, bs = None, -1
    for n in neighbors(head):
        if n in body_wo_tail:
            continue
        a = len(flood(n, body_wo_tail))
        if a > bs:
            best, bs = n, a
    return best


def play(chooser, max_steps=600, seed=None):
    """Run one headless game; returns (final_length, died)."""
    rnd = random.Random(seed)
    snake = collections.deque([(3, 4), (2, 4), (1, 4)])
    food = None
    for _ in range(max_steps):
        occ = set(snake)
        free = [(x, y) for x in range(W) for y in range(H) if (x, y) not in occ]
        if not free:
            return len(snake), False
        if food is None or food in occ:
            food = rnd.choice(free)
        m = chooser(list(snake), food)
        if m is None:
            return len(snake), True
        snake.appendleft(m)
        if m == food:
            food = None
        else:
            snake.pop()
    return len(snake), False


# ---------------------------------------------------------------- v2: virtual-snake safety + space/edge aware fallback
def bfs_hug(start, goal, blocked):
    """Shortest path, breaking ties towards cells that hug walls/body (so it travels along edges)."""
    q = collections.deque([start]); prev = {start: None}
    while q:
        c = q.popleft()
        if c == goal:
            path = []
            while c != start:
                path.append(c); c = prev[c]
            return path[::-1]
        for n in sorted(neighbors(c), key=lambda n: -hugging(n, blocked)):
            if n not in prev and n not in blocked:
                prev[n] = c; q.append(n)
    return None


def dist_map(start, blocked):
    d = {start: 0}; q = collections.deque([start])
    while q:
        c = q.popleft()
        for n in neighbors(c):
            if n not in d and n not in blocked:
                d[n] = d[c] + 1; q.append(n)
    return d


def choose2(snake, food):
    snake = list(snake)
    head, tail = snake[0], snake[-1]
    body_wo_tail = set(snake[:-1])
    # 1. eat if a full run along the shortest path leaves the tail reachable afterwards
    path = bfs_hug(head, food, body_wo_tail)
    if path:
        virt = list(snake)
        for step in path:
            virt = [step] + (virt if step == food else virt[:-1])
        if tail_reachable(virt):
            return path[0]
    # 2. otherwise stay safe: of the moves that keep the tail reachable, take the one with the most room,
    #    preferring cells that hug an edge, then the one farthest from the tail (uses the board's space)
    options = [n for n in neighbors(head) if n not in body_wo_tail]
    if not options:
        return None
    best, best_key = None, None
    for m in options:
        new = after_move(snake, m, m == food)
        blocked = set(new[1:-1])
        safe = tail_reachable(new)
        area = len(flood(m, blocked))
        far = dist_map(m, blocked).get(new[-1], 0)
        key = (safe, area, hugging(m, set(new[1:])), far, random.random())
        if best_key is None or key > best_key:
            best, best_key = m, key
    return best


def make_choose(order, hug_path=True):
    """Variant factory for benchmarking fallback key orders: tuple of names from area/hug/far."""
    def ch(snake, food):
        snake = list(snake)
        head = snake[0]
        body_wo_tail = set(snake[:-1])
        path = (bfs_hug if hug_path else bfs)(head, food, body_wo_tail)
        if path:
            virt = list(snake)
            for step in path:
                virt = [step] + (virt if step == food else virt[:-1])
            if tail_reachable(virt):
                return path[0]
        options = [n for n in neighbors(head) if n not in body_wo_tail]
        if not options:
            return None
        best, best_key = None, None
        for m in options:
            new = after_move(snake, m, m == food)
            blocked = set(new[1:-1])
            vals = dict(area=len(flood(m, blocked)), hug=hugging(m, set(new[1:])),
                        far=dist_map(m, blocked).get(new[-1], 0))
            key = (tail_reachable(new),) + tuple(vals[k] for k in order) + (random.random(),)
            if best_key is None or key > best_key:
                best, best_key = m, key
        return best
    return ch


_good = make_choose(("far", "area", "hug"))


def choose_human(snake, food, p_greedy=0.06, p_slip=0.012):
    """Good-but-fallible player. Mostly plays the careful strategy; now and then it
    (a) greedily dives for the food without checking it can escape afterwards, or
    (b) slips and takes a random legal move. Mistakes only start once the snake is a bit long."""
    snake = list(snake)
    if len(snake) >= 8:
        r = random.random()
        head = snake[0]
        body_wo_tail = set(snake[:-1])
        if r < p_slip:
            opts = [n for n in neighbors(head) if n not in body_wo_tail]
            if opts:
                return random.choice(opts)
        elif r < p_slip + p_greedy:
            path = bfs(head, food, body_wo_tail)
            if path:
                return path[0]
    return _good(snake, food)

#!/usr/bin/env python3
"""Unicorn HAT demo: patterns + self-playing snake (pimoroni unicornhat lib). Run with sudo."""
import colorsys, math, random, time, collections
import unicornhat as uh

W = H = 8
uh.set_layout(uh.AUTO)
DAY_BRIGHTNESS, NIGHT_BRIGHTNESS = 0.5, 0.2   # day = 07:00-21:00 local time
_last_check = [0.0, None]
_real_show = uh.show


def _auto_show():
    now = time.time()
    if now - _last_check[0] > 30:               # re-check the clock twice a minute
        _last_check[0] = now
        level = DAY_BRIGHTNESS if 7 <= time.localtime().tm_hour < 21 else NIGHT_BRIGHTNESS
        if level != _last_check[1]:
            _last_check[1] = level
            uh.brightness(level)
    _real_show()


uh.show = _auto_show
uh.rotation(180)  # board is mounted upside down relative to the library default
import classics
import snake_ai
import more


def Color(r, g, b):
    return (r, g, b)


class _Strip:
    def show(self): uh.show()
    def setPixelColor(self, i, c): uh.set_pixel(i % 8, i // 8, *c)


strip = _Strip()


def rgb(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return Color(int(r * 255), int(g * 255), int(b * 255))


def clear():
    uh.clear()


def put(x, y, c):
    uh.set_pixel(x, y, *c)


def rainbow(sec=5):
    t0 = time.time()
    while time.time() - t0 < sec:
        t = time.time() * 0.3
        for y in range(H):
            for x in range(W):
                put(x, y, rgb(t + (x + y) / 16))
        strip.show(); time.sleep(0.03)


def plasma(sec=5):
    t0 = time.time()
    while time.time() - t0 < sec:
        t = time.time()
        for y in range(H):
            for x in range(W):
                v = math.sin(x / 2 + t) + math.sin(y / 2 + t * 1.3) + math.sin((x + y) / 3 + t * 0.7)
                put(x, y, rgb(v / 6 + t * 0.05))
        strip.show(); time.sleep(0.03)


def ripple(sec=5):
    t0 = time.time()
    while time.time() - t0 < sec:
        t = time.time() * 3
        for y in range(H):
            for x in range(W):
                d = math.hypot(x - 3.5, y - 3.5)
                put(x, y, rgb(d / 8 - t / 10, 1, (math.sin(d * 1.5 - t) + 1) / 2))
        strip.show(); time.sleep(0.03)


def worm(sec=6):
    """Simple serpentine chase along the wiring order."""
    t0 = time.time(); p = 0
    while time.time() - t0 < sec:
        clear()
        for k in range(12):
            put((p - k) % 64 % 8, (p - k) % 64 // 8, rgb(p / 64 + k / 40, 1, 1 - k / 12))
        strip.show(); p += 1; time.sleep(0.05)


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


def snake_game(games=3):
    for g in range(games):
        snake = collections.deque([(3, 4), (2, 4), (1, 4)])  # head first
        food = None; hue = random.random(); steps = 0; died = False
        while True:
            occ = set(snake)
            free = [(x, y) for x in range(W) for y in range(H) if (x, y) not in occ]
            if not free:
                break  # filled the board!
            if food is None or food in occ:
                food = random.choice(free)
            move = snake_ai.choose_human(list(snake), food)
            if move is None:
                died = True
                break  # trapped, game over
            snake.appendleft(move)
            if move == food:
                food = None
            else:
                snake.pop()
            steps += 1
            clear()
            if food:
                put(*food, Color(255, 0, 0) if int(time.time() * 4) % 2 else Color(120, 0, 0))
            n = len(snake)
            for i, (x, y) in enumerate(snake):
                put(x, y, Color(255, 255, 255) if i == 0 else rgb(hue + i * 0.02, 1, max(0.75, 1 - i / (n * 4 + 4))))
            strip.show(); time.sleep(0.09)
            if steps > 600:
                break
        # death/finish flash
        for _ in range(3):
            for (x, y) in snake: put(x, y, Color(255, 0, 0) if died else Color(0, 255, 0))
            strip.show(); time.sleep(0.15)
            clear(); strip.show(); time.sleep(0.15)


PIECES = {
    "I": ([(0, 0), (1, 0), (2, 0), (3, 0)], (0, 255, 255)),
    "O": ([(0, 0), (1, 0), (0, 1), (1, 1)], (255, 255, 0)),
    "T": ([(0, 0), (1, 0), (2, 0), (1, 1)], (170, 0, 255)),
    "S": ([(1, 0), (2, 0), (0, 1), (1, 1)], (0, 255, 0)),
    "Z": ([(0, 0), (1, 0), (1, 1), (2, 1)], (255, 0, 0)),
    "J": ([(0, 0), (0, 1), (1, 1), (2, 1)], (0, 80, 255)),
    "L": ([(2, 0), (0, 1), (1, 1), (2, 1)], (255, 120, 0)),
}


def _rotations(cells):
    seen, out = set(), []
    for _ in range(4):
        mx = min(x for x, y in cells); my = min(y for x, y in cells)
        norm = tuple(sorted((x - mx, y - my) for x, y in cells))
        if norm not in seen:
            seen.add(norm); out.append(list(norm))
        cells = [(-y, x) for x, y in cells]
    return out


def _fits(board, cells, px, py):
    for x, y in cells:
        nx, ny = px + x, py + y
        if nx < 0 or nx >= W or ny >= H or (ny >= 0 and board[ny][nx]):
            return False
    return True


def _score(board):
    heights = []
    holes = 0
    for x in range(W):
        top = next((y for y in range(H) if board[y][x]), H)
        heights.append(H - top)
        holes += sum(1 for y in range(top, H) if not board[y][x])
    bump = sum(abs(heights[i] - heights[i + 1]) for i in range(W - 1))
    lines = sum(1 for r in board if all(r))
    return -0.5 * sum(heights) + 0.8 * lines * 3 - 0.75 * holes - 0.18 * bump - 0.3 * max(heights)


def _draw_board(board, cur=None):
    uh.clear()
    for y in range(H):
        for x in range(W):
            if board[y][x]:
                uh.set_pixel(x, y, *board[y][x])
    if cur:
        cells, px, py, col = cur
        for x, y in cells:
            if 0 <= py + y < H:
                uh.set_pixel(px + x, py + y, *col)
    uh.show()


def tetris_game(max_pieces=250):
    _tetris_game(max_pieces)


def _tetris_game(max_pieces):
    board = [[None] * W for _ in range(H)]
    bag = []
    for _ in range(max_pieces):
        if not bag:
            bag = list(PIECES); random.shuffle(bag)
        name = bag.pop()
        base, col = PIECES[name]
        rots = _rotations(base)
        start = (0, 2, -1)                      # (rotation index, x, y) spawn
        if not _fits(board, rots[0], 2, -1):
            break
        # Breadth-first search over real moves: left, right, down, rotate.
        # The piece can only reach cells it can physically travel through.
        parent = {start: None}
        queue = collections.deque([start])
        locks = []
        while queue:
            st = queue.popleft()
            ri, x, y = st
            cells = rots[ri]
            if not _fits(board, cells, x, y + 1):
                locks.append(st)
            for nxt in ((ri, x - 1, y), (ri, x + 1, y), (ri, x, y + 1), ((ri + 1) % len(rots), x, y)):
                if nxt not in parent and _fits(board, rots[nxt[0]], nxt[1], nxt[2]):
                    parent[nxt] = st
                    queue.append(nxt)
        best = None
        for st in locks:
            ri, px, py = st
            rot = rots[ri]
            if any(py + y < 0 for _, y in rot):
                continue                         # would lock above the board
            trial = [r[:] for r in board]
            for x, y in rot:
                trial[py + y][px + x] = col
            kept = [r for r in trial if not all(r)]
            cleared = H - len(kept)
            trial = [[None] * W for _ in range(cleared)] + kept
            s = _score(trial) + cleared * 2
            if best is None or s > best[0]:
                best = (s, st)
        if best is None:
            break
        # rebuild the path and animate it
        path, st = [], best[1]
        while st is not None:
            path.append(st); st = parent[st]
        path.reverse()
        for ri, x, y in path:
            _draw_board(board, (rots[ri], x, y, col)); time.sleep(0.07)
        ri, px, py = best[1]
        for cx, cy in rots[ri]:
            board[py + cy][px + cx] = col
        time.sleep(0.1)
        full = [i for i, r in enumerate(board) if all(r)]
        if full:
            for _ in range(3):
                for i in full:
                    for x in range(W): uh.set_pixel(x, i, 255, 255, 255)
                uh.show(); time.sleep(0.07)
                _draw_board(board); time.sleep(0.07)
            board = [[None] * W for _ in full] + [r for r in board if not all(r)]
            _draw_board(board)
        time.sleep(0.05)
    for _ in range(3):
        uh.clear(); uh.show(); time.sleep(0.15)
        _draw_board(board); time.sleep(0.15)


C4W, C4H = 8, 8   # board fills the whole 8x8 display
RED, YEL = (255, 0, 0), (255, 200, 0)


def _c4_lines():
    out = []
    for c in range(C4W):
        for r in range(C4H):
            for dc, dr in ((1, 0), (0, 1), (1, 1), (1, -1)):
                cells = [(c + k * dc, r + k * dr) for k in range(4)]
                if all(0 <= a < C4W and 0 <= b < C4H for a, b in cells):
                    out.append(cells)
    return out


_C4_LINES = _c4_lines()


def _c4_winner(b):
    for cells in _C4_LINES:
        v = b[cells[0][0]][cells[0][1]]
        if v and all(b[a][r] == v for a, r in cells):
            return v, cells
    return 0, None


def _c4_drop_row(b, c):
    for r in range(C4H - 1, -1, -1):       # r = 0 is top, r = C4H-1 is bottom
        if not b[c][r]:
            return r
    return None


def _c4_eval(b, me):
    sc = 0
    for cells in _C4_LINES:
        vals = [b[a][r] for a, r in cells]
        m, o = vals.count(me), vals.count(3 - me)
        if m and o:
            continue
        if m == 3: sc += 5
        elif m == 2: sc += 2
        if o == 3: sc -= 6
        elif o == 2: sc -= 2
    sc += 3 * sum(1 for r in range(C4H) if b[3][r] == me or b[4][r] == me)
    return sc


def _c4_search(b, depth, alpha, beta, player, me):
    w, _ = _c4_winner(b)
    if w:
        return (10000 + depth) if w == me else -(10000 + depth), None
    moves = [c for c in (3, 4, 2, 5, 1, 6, 0, 7) if _c4_drop_row(b, c) is not None]
    if not moves:
        return 0, None
    if depth == 0:
        return _c4_eval(b, me), None
    best_move = random.choice(moves)
    if player == me:
        best = -10 ** 9
        for c in moves:
            r = _c4_drop_row(b, c); b[c][r] = player
            v, _ = _c4_search(b, depth - 1, alpha, beta, 3 - player, me)
            b[c][r] = 0
            if v > best + random.random() * 0.5 or best == -10 ** 9:
                best, best_move = v, c
            alpha = max(alpha, best)
            if alpha >= beta: break
    else:
        best = 10 ** 9
        for c in moves:
            r = _c4_drop_row(b, c); b[c][r] = player
            v, _ = _c4_search(b, depth - 1, alpha, beta, 3 - player, me)
            b[c][r] = 0
            if v < best: best = v
            beta = min(beta, best)
            if alpha >= beta: break
    return best, best_move


def _c4_draw(b, hover=None, win=None, blink=True):
    uh.clear()
    for c in range(C4W):
        for r in range(C4H):
            v = b[c][r]
            if v:
                col = RED if v == 1 else YEL
                if win and (c, r) in win and not blink:
                    col = (255, 255, 255)
                uh.set_pixel(c, r, *col)
    if hover:
        c, y, p = hover
        uh.set_pixel(c, y, *(RED if p == 1 else YEL))
    uh.show()


def connect4(games=2):
    for _ in range(games):
        b = [[0] * C4H for _ in range(C4W)]
        player = random.choice((1, 2))
        winner, cells = 0, None
        for turn in range(C4W * C4H):
            _, c = _c4_search(b, 4, -10 ** 9, 10 ** 9, player, player)
            r = _c4_drop_row(b, c)
            # the piece falls in from the top edge of its column
            for y in range(0, r + 1):
                _c4_draw(b, (c, y, player)); time.sleep(0.05)
            b[c][r] = player
            _c4_draw(b); time.sleep(0.25)
            winner, cells = _c4_winner(b)
            if winner:
                break
            player = 3 - player
        if winner:
            win = set(cells)
            for i in range(8):
                _c4_draw(b, win=win, blink=bool(i % 2)); time.sleep(0.2)
        else:
            time.sleep(0.8)
        time.sleep(0.6)


def pong(points=5):
    """Two AI paddles (left blue, right orange); the AIs are deliberately a bit fallible so points get scored."""
    PH = 3
    score = [0, 0]
    pad = [2, 2]                                  # top y of each paddle
    err = [0, 0]                                  # each AI's current aiming error
    cols = [(0, 120, 255), (255, 130, 0)]

    def draw(bx, by, pips=False):
        uh.clear()
        for s in (0, 1):
            for k in range(PH):
                uh.set_pixel(0 if s == 0 else 7, pad[s] + k, *cols[s])
        if bx is not None:
            uh.set_pixel(min(7, max(0, int(round(bx)))), min(7, max(0, int(round(by)))), 255, 255, 255)
        if pips:
            for s in (0, 1):
                for i in range(score[s]):
                    uh.set_pixel(1 + i if s == 0 else 6 - i, 0, *cols[s])
        uh.show()

    while max(score) < points:
        bx, by = 3.5, random.uniform(2, 5)
        vx = random.choice((-0.5, 0.5))
        vy = random.choice((-0.35, -0.2, 0.2, 0.35))
        scorer = None
        while scorer is None:
            bx += vx; by += vy
            if by < 0: by, vy = -by, -vy
            if by > 7: by, vy = 14 - by, -vy
            for s in (0, 1):                      # paddle AI: chase the ball, sometimes dozing
                toward = (vx < 0) == (s == 0)
                if random.random() < (0.8 if toward else 0.3):
                    target = by - 1 + err[s]
                    if pad[s] < target - 0.5: pad[s] += 1
                    elif pad[s] > target + 0.5: pad[s] -= 1
                    pad[s] = max(0, min(8 - PH, pad[s]))
            if vx < 0 and bx <= 1:
                if pad[0] <= round(by) <= pad[0] + PH - 1:
                    bx = 2 - bx; vx = min(0.9, abs(vx) * 1.07); err[1] = random.choice((-2, -1, 0, 0, 1, 2))
                    vy = max(-0.6, min(0.6, vy + (by - (pad[0] + 1)) * 0.15))
                elif bx < 0:
                    scorer = 1
            elif vx > 0 and bx >= 6:
                if pad[1] <= round(by) <= pad[1] + PH - 1:
                    bx = 12 - bx; vx = -min(0.9, abs(vx) * 1.07); err[0] = random.choice((-2, -1, 0, 0, 1, 2))
                    vy = max(-0.6, min(0.6, vy + (by - (pad[1] + 1)) * 0.15))
                elif bx > 7:
                    scorer = 0
            draw(bx, by) if scorer is None else None
            time.sleep(0.06)
        score[scorer] += 1
        for _ in range(3):
            draw(None, None); time.sleep(0.12)
            draw(None, None, pips=True); time.sleep(0.12)
        time.sleep(0.4)
    w = 0 if score[0] > score[1] else 1
    for _ in range(4):
        uh.clear()
        for y in range(8):
            for x in range(4 * w, 4 * w + 4):
                uh.set_pixel(x, y, *cols[w])
        uh.show(); time.sleep(0.2); uh.clear(); uh.show(); time.sleep(0.2)


if __name__ == "__main__":
    try:
        while True:
            rainbow(); plasma(); ripple(); worm()
            classics.run_all()
            snake_game(3)
            tetris_game()
            connect4()
            pong()
            more.run_all()
    finally:
        uh.off()

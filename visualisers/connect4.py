"""Connect 4: Red vs yellow on a full 8x8 board."""
import random, time
from .display import uh


# Brightness is a per-channel output ceiling (0-255 PWM). Day = 07:00-21:00 local time.
# The library's own gamma table maps every input below ~22 to zero, so at low brightness it
# collapsed every colour to a pure primary. We switch it off and tone-map in software instead,
# which keeps colour ratios (an orange stays orange) even when the whole board is dim.
DAY_OUT, NIGHT_OUT = 12, 4


TONE_GAMMA = 1.4


_lut = list(range(256))


_last_check = [0.0, None]


_real_show = uh.show


def _build_lut(out_max):
    for v in range(256):
        _lut[v] = int(round(out_max * (v / 255.0) ** TONE_GAMMA))


def _auto_show():
    now = time.time()
    if now - _last_check[0] > 30:               # re-check the clock twice a minute
        _last_check[0] = now
        level = DAY_OUT if 7 <= time.localtime().tm_hour < 21 else NIGHT_OUT
        if level != _last_check[1]:
            _last_check[1] = level
            _build_lut(level)
    _real_show()


uh.show = _auto_show


C4W, C4H = 8, 8   # board fills the whole 8x8 display


RED, YEL = (255, 0, 0), (255, 255, 0)   # pure yellow: stays distinct from red when dim


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


_C4_NOISE = {1: 0.0, 2: 0.0}   # per-player evaluation noise, re-rolled every game


def _c4_eval(b, me):
    sc = random.uniform(-_C4_NOISE[me], _C4_NOISE[me])
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
    moves = [c for c in range(C4W) if _c4_drop_row(b, c) is not None]
    random.shuffle(moves)                        # random tie-breaking between equally good moves
    moves.sort(key=lambda c: abs(c - 3.5) + random.random() * 2.5)   # but still prefer the middle, loosely
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
            if v > best:
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


def run(games=2):
    for _ in range(games):
        b = [[0] * C4H for _ in range(C4W)]
        player = random.choice((1, 2))
        winner, cells = 0, None
        # each player gets a random personality this game: noisy or sharp, shallow or deep
        _C4_NOISE[1], _C4_NOISE[2] = random.uniform(0.3, 4), random.uniform(0.3, 4)
        depth = {1: random.choice((3, 4)), 2: random.choice((3, 4))}
        for turn in range(C4W * C4H):
            legal = [c for c in range(C4W) if _c4_drop_row(b, c) is not None]
            if turn < 4 and random.random() < 0.6:           # varied openings
                c = random.choice([c for c in legal if 2 <= c <= 5] or legal)
            elif random.random() < 0.06:                    # now and then, a blunder
                c = random.choice(legal)
            else:
                _, c = _c4_search(b, depth[player], -10 ** 9, 10 ** 9, player, player)
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

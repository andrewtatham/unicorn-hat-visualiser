"""Tetris: The AI plays Tetris, only using moves a real piece could make."""
import collections, random, time
from .display import uh, W, H


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


def run(max_pieces=250):
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

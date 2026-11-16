"""Pong: Two fallible AI paddles, first to five."""
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


def run(points=5):
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

"""Render a representative PNG of every visualiser by running it headless against a fake unicornhat."""
import math, os, random, struct, sys, time, types, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
OUT = os.path.join(HERE, "web", "shots")
os.makedirs(OUT, exist_ok=True)

# ---- fake display that records every shown frame ----
buf = [(0, 0, 0)] * 64
frames = []
m = types.ModuleType("unicornhat")
m.AUTO = 0
for n in ("set_layout", "brightness", "rotation"):
    setattr(m, n, lambda *a: None)


def set_pixel(x, y, r, g=None, b=None):
    if g is None:
        r, g, b = r
    assert 0 <= x < 8 and 0 <= y < 8, (x, y)
    buf[int(y) * 8 + int(x)] = (int(r), int(g), int(b))


def clear():
    global buf
    buf = [(0, 0, 0)] * 64


def show():
    frames.append(list(buf))


m.set_pixel, m.clear, m.off, m.show = set_pixel, clear, clear, show
sys.modules["unicornhat"] = m

# ---- virtual clock so timed effects finish instantly ----
clock = [1000.0]
time.time = lambda: clock[0]
time.sleep = lambda s: clock.__setitem__(0, clock[0] + s)
random.seed(7)

import registry  # noqa: E402


def png(pixels, cell=28):
    n = 8 * cell
    rows = []
    for py in range(n):
        row = bytearray([0])
        cy = py // cell
        for px in range(n):
            cx = px // cell
            ccx, ccy = cx * cell + cell / 2, cy * cell + cell / 2
            d = math.hypot(px + 0.5 - ccx, py + 0.5 - ccy)
            r, g, b = pixels[cy * 8 + cx]
            bg = (14, 16, 22)
            socket = (30, 33, 42)
            R = cell * 0.40
            col = socket if d <= R + 1.5 else bg
            if d <= R + 1.5 and (r or g or b):
                glow = max(0.0, 1 - d / (cell * 0.62)) ** 2 * 0.35
                col = tuple(min(255, int(c + v * glow)) for c, v in zip(col, (r, g, b)))
            if (r or g or b):
                a = max(0.0, min(1.0, R + 0.5 - d))
                lit = tuple(min(255, int(v * 1.0 + 8)) for v in (r, g, b))
                col = tuple(int(c * (1 - a) + l * a) for c, l in zip(col, lit))
            row += bytes(col)
        rows.append(bytes(row))
    raw = b"".join(rows)
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


for v in registry.V:
    frames.clear(); clear()
    try:
        v["fn"]()
    except Exception as e:
        print("FAILED", v["id"], repr(e)); continue
    if not frames:
        print("no frames", v["id"]); continue
    frames[:] = [f for f in frames if len(set(f)) > 1 or f[0] == (0, 0, 0)] or frames   # drop full-board flashes
    n = len(frames)
    lo, hi = int(n * max(0, v["shot"] - 0.12)), int(n * min(1, v["shot"] + 0.12)) + 1
    cand = frames[lo:hi] or frames
    lit = lambda f: sum(1 for p in f if any(p))
    best_n = max(lit(f) for f in cand)
    # prefer the frame closest to the target position among those nearly as full as the fullest
    target = int(n * v["shot"])
    pick = min((i for i in range(lo, min(hi, n)) if lit(frames[i]) >= best_n * 0.8), key=lambda i: abs(i - target))
    with open(os.path.join(OUT, v["id"] + ".png"), "wb") as f:
        f.write(png(frames[pick]))
    print("ok", v["id"], f"frame {pick}/{n} lit={lit(frames[pick])}")

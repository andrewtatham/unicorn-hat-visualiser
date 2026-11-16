"""Candle: A flickering candle flame."""
import colorsys, math, random, time
from .display import uh


def run(sec=12):
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

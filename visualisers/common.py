"""Small drawing helpers shared by the visualisers."""
import colorsys, time
from .display import uh, W, H


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


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        uh.set_pixel(int(x), int(y), int(c[0]), int(c[1]), int(c[2]))


def hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def flash(color, n=3):
    for _ in range(n):
        for y in range(H):
            for x in range(W):
                px(x, y, color)
        uh.show(); time.sleep(0.12)
        uh.clear(); uh.show(); time.sleep(0.12)

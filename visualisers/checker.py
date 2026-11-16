"""Roto-zoom checker: Rotating, zooming checkerboard."""
import colorsys, math
from .display import W, H
from .shader import shader


def checker(x, y, step):
    x -= W / 2; y -= H / 2
    angle = step / 10.0
    s, c = math.sin(angle), math.cos(angle)
    xs = x * c - y * s; ys = x * s + y * c
    xs -= math.sin(step / 200.0) * 40.0
    ys -= math.cos(step / 200.0) * 40.0
    scale = math.sin(step / 50.0) / 8.0 + 0.25
    xs *= scale; ys *= scale
    xo = abs(xs) - int(abs(xs)); yo = abs(ys) - int(abs(ys))
    l = 0 if (math.floor(xs) + math.floor(ys)) % 2 else 1 if xo > .1 and yo > .1 else .5
    r, g, b = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, l)
    return (r * 255, g * 255, b * 255)


def run():
    shader(checker, 10)

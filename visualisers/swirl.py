"""Swirl: Twisty swirly goodness."""
import math
from .display import W, H
from .shader import shader


def swirl(x, y, step):
    x -= W / 2; y -= H / 2
    dist = math.sqrt(x * x + y * y) / 2.0
    angle = step / 10.0 + dist * 1.5
    s, c = math.sin(angle), math.cos(angle)
    xs = x * c - y * s; ys = x * s + y * c
    r = abs(xs + ys) * 64.0 - 20
    return (r, r + s * 130, r + c * 130)


def run():
    shader(swirl, 8)

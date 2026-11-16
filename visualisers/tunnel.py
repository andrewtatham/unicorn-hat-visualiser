"""Tunnel: Zooming tunnel shader from demo.py."""
import colorsys, math
from .display import W, H
from .shader import shader


def tunnel(x, y, step):
    speed = step / 100.0
    x -= W / 2; y -= H / 2
    x += math.sin(step / 27.0) * 2
    y += math.cos(step / 18.0) * 2
    if y == 0:
        angle = -(math.pi / 2) if x < 0 else (math.pi / 2)
    else:
        angle = math.atan(x / y)
    if y > 0:
        angle += math.pi
    angle /= 2 * math.pi
    shade = min(1, math.sqrt(x * x + y * y) / 2.1)
    angle += speed
    depth = speed + math.sqrt(x * x + y * y) / 10
    col1 = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, .8)
    col2 = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, .3)
    col = col1 if int(abs(angle * 6.0)) % 2 == 0 else col2
    td = .3 if int(abs(depth * 3.0)) % 2 == 0 else 0
    return tuple((c + td) * shade * 255 for c in col)


def run():
    shader(tunnel, 10)

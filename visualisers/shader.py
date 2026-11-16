"""Runs a per-pixel shader function fn(x, y, step) -> (r, g, b) for `sec` seconds."""
import time
from .display import uh, W, H


def _clamp(v):
    return int(max(0, min(255, v)))


def shader(fn, sec, fps=60):
    t0 = time.time(); step = 0
    while time.time() - t0 < sec:
        for y in range(H):
            for x in range(W):
                r, g, b = fn(x, y, step)
                uh.set_pixel(x, y, _clamp(r), _clamp(g), _clamp(b))
        uh.show(); step += 1; time.sleep(1.0 / fps)

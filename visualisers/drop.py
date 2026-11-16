"""Drop: A bucket filling with randomly coloured balls."""
import random, time
from .display import uh, W, H


def _sp(x, y, r, g, b):
    uh.set_pixel(x, H - 1 - y, r, g, b)  # bucket floor at the bottom for this mounting


def run(rounds=1):
    """Bucket that fills with randomly coloured balls."""
    def setup():
        uh.clear()
        for b in range(H): _sp(0, b, 255, 255, 255); _sp(W - 1, b, 255, 255, 255)
        for b in range(1, W - 1): _sp(b, 0, 255, 255, 255)
        uh.show()
    for _ in range(rounds):
        setup()
        heights = [0] * (W - 2)
        for _ in range((W - 2) * (H - 1)):
            cols = [c for c in range(W - 2) if heights[c] < H - 1]
            if not cols: break
            c = random.choice(cols)
            col = [random.randint(100, 255) for _ in range(3)]
            y = H - 1
            for _ in range((H - 2) - heights[c]):
                _sp(c + 1, y, *col); uh.show(); time.sleep(0.03)
                _sp(c + 1, y, 0, 0, 0); y -= 1
            _sp(c + 1, y, *col); uh.show()
            heights[c] += 1
        time.sleep(1)

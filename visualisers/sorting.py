"""Sorting bars: Bubble, insertion, quick and selection sort."""
import random, time
from .display import uh
from .common import hsv, px


def _bubble(a):
    for i in range(len(a)):
        for j in range(len(a) - 1 - i):
            yield (j, j + 1)
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]; yield (j, j + 1)


def _insertion(a):
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]; yield (j - 1, j); j -= 1


def _selection(a):
    for i in range(len(a)):
        m = i
        for j in range(i + 1, len(a)):
            yield (m, j)
            if a[j] < a[m]: m = j
        if m != i: a[i], a[m] = a[m], a[i]; yield (i, m)


def _quick(a, lo=0, hi=None):
    if hi is None: hi = len(a) - 1
    if lo >= hi: return
    p = a[hi]; i = lo
    for j in range(lo, hi):
        yield (j, hi)
        if a[j] < p:
            a[i], a[j] = a[j], a[i]; yield (i, j); i += 1
    a[i], a[hi] = a[hi], a[i]; yield (i, hi)
    yield from _quick(a, lo, i - 1)
    yield from _quick(a, i + 1, hi)


def run(rounds=4):
    algs = [_bubble, _insertion, _quick, _selection]
    random.shuffle(algs)
    for alg in algs[:rounds]:
        a = list(range(1, 9)); random.shuffle(a)
        def draw(hl=()):
            uh.clear()
            for i, v in enumerate(a):
                for y in range(8 - v, 8):
                    px(i, y, (255, 255, 255) if i in hl else hsv(v / 10.0, 1, 0.9))
            uh.show()
        draw(); time.sleep(0.4)
        for hl in alg(a):
            draw(hl); time.sleep(0.09)
        for i in range(8):
            draw(); px(i, 0, (0, 0, 0))
            for k in range(i + 1):
                for y in range(8 - a[k], 8): px(k, y, (0, 255, 0))
            uh.show(); time.sleep(0.05)
        time.sleep(0.5)

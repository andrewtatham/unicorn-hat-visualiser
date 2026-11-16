"""Maze solver: Carves a maze, then a dot solves it."""
import collections, random, time
from .display import uh
from .common import hsv, px


def run(rounds=2):
    N = 7
    for _ in range(rounds):
        g = [[1] * N for _ in range(N)]
        g[0][0] = 0; stack = [(0, 0)]
        def draw(head=None, trail=None):
            uh.clear()
            for y in range(N):
                for x in range(N):
                    if g[y][x]: px(x, y, (0, 0, 70))
            if trail:
                for i, (x, y) in enumerate(trail): px(x, y, hsv(0.55 + i * 0.02, 1, 0.5 + 0.5 * i / max(1, len(trail))))
            if head: px(head[0], head[1], (255, 255, 255))
            uh.show()
        while stack:
            x, y = stack[-1]
            nb = [(dx, dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
                  if 0 <= x + dx < N and 0 <= y + dy < N and g[y + dy][x + dx]]
            if nb:
                dx, dy = random.choice(nb)
                g[y + dy // 2][x + dx // 2] = 0; g[y + dy][x + dx] = 0
                stack.append((x + dx, y + dy)); draw((x + dx, y + dy)); time.sleep(0.06)
            else:
                stack.pop()
        prev = {(0, 0): None}; q = collections.deque([(0, 0)])
        while q:
            c = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + dx, c[1] + dy)
                if 0 <= n[0] < N and 0 <= n[1] < N and not g[n[1]][n[0]] and n not in prev:
                    prev[n] = c; q.append(n)
        path, c = [], (N - 1, N - 1)
        while c: path.append(c); c = prev[c]
        path.reverse()
        for i in range(len(path)):
            draw(path[i], path[:i]); time.sleep(0.09)
        draw(None, path); px(N - 1, N - 1, (0, 255, 0)); uh.show(); time.sleep(1.2)

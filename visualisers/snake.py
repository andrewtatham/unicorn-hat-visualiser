"""Snake: A self-playing snake hunting food, with a rainbow body."""
import collections, random, time
from .display import W, H
from .common import Color, clear, put, rgb, strip
from . import snake_ai


def run(games=3):
    for g in range(games):
        snake = collections.deque([(3, 4), (2, 4), (1, 4)])  # head first
        food = None; hue = random.random(); steps = 0; died = False
        while True:
            occ = set(snake)
            free = [(x, y) for x in range(W) for y in range(H) if (x, y) not in occ]
            if not free:
                break  # filled the board!
            if food is None or food in occ:
                food = random.choice(free)
            move = snake_ai.choose_human(list(snake), food)
            if move is None:
                died = True
                break  # trapped, game over
            snake.appendleft(move)
            if move == food:
                food = None
            else:
                snake.pop()
            steps += 1
            clear()
            if food:
                put(*food, Color(255, 0, 0) if int(time.time() * 4) % 2 else Color(120, 0, 0))
            n = len(snake)
            for i, (x, y) in enumerate(snake):
                put(x, y, Color(255, 255, 255) if i == 0 else rgb(hue + i * 0.02, 1, max(0.75, 1 - i / (n * 4 + 4))))
            strip.show(); time.sleep(0.09)
            if steps > 600:
                break
        # death/finish flash
        for _ in range(3):
            for (x, y) in snake: put(x, y, Color(255, 0, 0) if died else Color(0, 255, 0))
            strip.show(); time.sleep(0.15)
            clear(); strip.show(); time.sleep(0.15)

"""Single list of every visualiser: id, title, description, category and the callable that runs it once."""
from visualisers import (
    ant, binary_clock, blues_and_twos, breakout, candle, checker, classic_rainbow, connect4, cross, dashboard,
    drop, embers, g2048, game_of_life, invaders, matrix, maze, pacman, plasma, pong, rainbow, rainbow_blinky,
    rainbow_search, ripple, sand, snake, snow, sorting, sparkles, swirl, tetris, tunnel, worm,
)

V = []


def add(id, title, desc, cat, fn, shot=0.5):
    V.append(dict(id=id, title=title, desc=desc, cat=cat, fn=fn, shot=shot))


P, C, G, T = "Patterns", "Pimoroni classics", "Games (AI plays itself)", "Toys & tools"

add('rainbow', 'Rainbow wave', 'Smooth diagonal rainbow that drifts across the board.', P, rainbow.run)
add('plasma', 'Plasma', 'Overlapping sine waves, the classic demoscene plasma.', P, plasma.run)
add('ripple', 'Ripple', 'Colour rings radiating out from the centre.', P, ripple.run)
add('worm', 'Worm', 'A rainbow worm chasing itself along the LED chain.', P, worm.run)

add('classic-rainbow', 'Classic rainbow', 'The original Pimoroni rainbow example.', C, classic_rainbow.run)
add('rainbow-blinky', 'Rainbow blinky', 'A rainbow that pulses out from the centre.', C, rainbow_blinky.run)
add('tunnel', 'Tunnel', 'Zooming tunnel shader from demo.py.', C, tunnel.run)
add('rainbow-search', 'Rainbow searchlights', 'Sweeping rainbow spotlights.', C, rainbow_search.run)
add('checker', 'Roto-zoom checker', 'Rotating, zooming checkerboard.', C, checker.run)
add('swirl', 'Swirl', 'Twisty swirly goodness.', C, swirl.run)
add('blues-and-twos', 'Blues and twos', 'Flashing blue emergency-light waves.', C, blues_and_twos.run)
add('embers', 'Embers', 'Random flickering yellow-orange-red LEDs.', C, embers.run)
add('sparkles', 'Sparkles', 'Random colourful sparkles building up.', C, sparkles.run)
add('snow', 'Snow', 'A gentle snowstorm.', C, snow.run)
add('cross', 'Cross', "Coloured dots crossing each other's paths.", C, cross.run)
add('matrix', 'Matrix rain', 'Falling green code. Follow the white rabbit.', C, matrix.run)
add('drop', 'Drop', 'A bucket filling with randomly coloured balls.', C, drop.run)
add('life', 'Game of Life', "Conway's Life with age colours and fading ghosts.", C, game_of_life.run)
add('candle', 'Candle', 'A flickering candle flame.', C, candle.run)

add('snake', 'Snake', 'A self-playing snake hunting food, with a rainbow body.', G, snake.run)
add('tetris', 'Tetris', 'The AI plays Tetris, only using moves a real piece could make.', G, tetris.run, 0.6)
add('connect4', 'Connect 4', 'Red vs yellow on a full 8x8 board.', G, connect4.run, 0.8)
add('pong', 'Pong', 'Two fallible AI paddles, first to five.', G, pong.run)
add('breakout', 'Breakout', 'An AI paddle clears rows of bricks.', G, breakout.run)
add('invaders', 'Space Invaders', 'A tiny invasion defended by a dodging cannon.', G, invaders.run)
add('2048', '2048', 'The AI slides tiles, drawn as 2x2 pixel blocks.', G, g2048.run, 0.7)
add('pacman', 'Pac-Man', 'Full maze, four ghosts, power pills, and an 8x8 window that scrolls with Pac-Man.', G, pacman.run)

add('maze', 'Maze solver', 'Carves a maze, then a dot solves it.', T, maze.run, 0.97)
add('sand', 'Falling sand', 'Grains pile up as gravity rotates around the board.', T, sand.run, 0.8)
add('ant', "Langton's ant", 'A simple ant building complex patterns.', T, ant.run, 0.8)
add('sorting', 'Sorting bars', 'Bubble, insertion, quick and selection sort.', T, sorting.run, 0.4)
add('dashboard', 'Pi dashboard', 'CPU cores, temperature, memory and network as live bars.', T, dashboard.run)
add('clock', 'Binary clock', 'Hours, minutes and seconds in binary-coded decimal.', T, binary_clock.run)

BY_ID = {v["id"]: v for v in V}

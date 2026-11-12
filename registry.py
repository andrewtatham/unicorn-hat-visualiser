"""Single list of every visualiser: id, title, description, category and the callable that runs it once."""
import snake, classics, more
from classics import shader

V = []


def add(id, title, desc, cat, fn, shot=0.5):
    V.append(dict(id=id, title=title, desc=desc, cat=cat, fn=fn, shot=shot))


P, C, G, T = "Patterns", "Pimoroni classics", "Games (AI plays itself)", "Toys & tools"

add("rainbow", "Rainbow wave", "Smooth diagonal rainbow that drifts across the board.", P, snake.rainbow)
add("plasma", "Plasma", "Overlapping sine waves, the classic demoscene plasma.", P, snake.plasma)
add("ripple", "Ripple", "Colour rings radiating out from the centre.", P, snake.ripple)
add("worm", "Worm", "A rainbow worm chasing itself along the LED chain.", P, snake.worm)

add("classic-rainbow", "Classic rainbow", "The original Pimoroni rainbow example.", C, lambda: shader(classics.classic_rainbow, 8))
add("rainbow-blinky", "Rainbow blinky", "A rainbow that pulses out from the centre.", C, lambda: shader(classics.rainbow_blinky, 8))
add("tunnel", "Tunnel", "Zooming tunnel shader from demo.py.", C, lambda: shader(classics.tunnel, 10))
add("rainbow-search", "Rainbow searchlights", "Sweeping rainbow spotlights.", C, lambda: shader(classics.rainbow_search, 8))
add("checker", "Roto-zoom checker", "Rotating, zooming checkerboard.", C, lambda: shader(classics.checker, 10))
add("swirl", "Swirl", "Twisty swirly goodness.", C, lambda: shader(classics.swirl, 8))
add("blues-and-twos", "Blues and twos", "Flashing blue emergency-light waves.", C, lambda: shader(classics.blues_and_twos, 8))
add("embers", "Embers", "Random flickering yellow-orange-red LEDs.", C, classics.random_blinky)
add("sparkles", "Sparkles", "Random colourful sparkles building up.", C, classics.random_sparkles)
add("snow", "Snow", "A gentle snowstorm.", C, classics.snow)
add("cross", "Cross", "Coloured dots crossing each other's paths.", C, classics.cross)
add("matrix", "Matrix rain", "Falling green code. Follow the white rabbit.", C, classics.matrix)
add("drop", "Drop", "A bucket filling with randomly coloured balls.", C, classics.drop)
add("life", "Game of Life", "Conway's Life with age colours and fading ghosts.", C, classics.game_of_life)
add("candle", "Candle", "A flickering candle flame.", C, classics.candle)

add("snake", "Snake", "A self-playing snake hunting food, with a rainbow body.", G, lambda: snake.snake_game(3))
add("tetris", "Tetris", "The AI plays Tetris, only using moves a real piece could make.", G, snake.tetris_game, 0.6)
add("connect4", "Connect 4", "Red vs yellow on a full 8x8 board.", G, snake.connect4, 0.8)
add("pong", "Pong", "Two fallible AI paddles, first to five.", G, snake.pong)
add("breakout", "Breakout", "An AI paddle clears rows of bricks.", G, more.breakout)
add("invaders", "Space Invaders", "A tiny invasion defended by a dodging cannon.", G, more.invaders)
add("2048", "2048", "The AI slides tiles, drawn as 2x2 pixel blocks.", G, more.g2048, 0.7)
add("pacman", "Pac-Man", "Eats the dots while a ghost gives chase.", G, more.pacman)

add("maze", "Maze solver", "Carves a maze, then a dot solves it.", T, more.maze, 0.97)
add("sand", "Falling sand", "Grains pile up as gravity rotates around the board.", T, more.sand, 0.8)
add("ant", "Langton's ant", "A simple ant building complex patterns.", T, more.ant, 0.8)
add("sorting", "Sorting bars", "Bubble, insertion, quick and selection sort.", T, more.sorting, 0.4)
add("dashboard", "Pi dashboard", "CPU cores, temperature, memory and network as live bars.", T, more.dashboard)
add("clock", "Binary clock", "Hours, minutes and seconds in binary-coded decimal.", T, more.binary_clock)

BY_ID = {v["id"]: v for v in V}

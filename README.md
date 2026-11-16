# Unicorn HAT visualiser

A loop of 33 visualisers for the original 8x8 Pimoroni Unicorn HAT on a Raspberry Pi, with a small web UI to
enable/disable each one. Most of the games are played by AIs: snake, Tetris, Connect 4, Pong, Breakout,
Space Invaders, 2048 and Pac-Man.

The web UI shows a live view of the board and a screenshot, description and on/off toggle for every visualiser.

## Files

| File | What it does |
|---|---|
| `runner.py` | Entry point. Runs the enabled visualisers in order and serves the web UI on port 8080. |
| `registry.py` | The list of visualisers (id, title, description, category). |
| `server.py` | Dependency-free web server and JSON API. Enabled state is saved in `unicorn-config.json`. |
| `visualisers/` | One module per visualiser, each exposing `run()`. Shared code: `display.py` (one-off hardware setup, brightness, tone-mapping), `common.py` (pixel helpers), `shader.py` (per-pixel shader loop). |
| `visualisers/snake_ai.py` | Snake decision logic (kept display-free so it can be tested). |
| `gen_shots.py` | Renders the screenshots in `web/shots/` by running each visualiser against a fake display. |
| `unicorn-demo.service` | systemd unit to start it at boot. |

## Pac-Man

`visualisers/pacman.py` plays a 21x21 maze (symmetric, with a wrap-around tunnel and a ghost house) through the 8x8 window,
which scrolls once Pac-Man gets within two cells of its edge. Four ghosts use the classic targeting (Blinky chases,
Pinky ambushes, Inky flanks, Clyde shies away up close) with scatter/chase phases; four power pills let Pac-Man eat
them (blue = frightened, flashing white = nearly over, grey = eyes heading home). Pac-Man runs a safe-path BFS and
heads for a pill when cornered. The game carries on between visualiser runs; tune `_PAC_SLOW` (ghost speed) and
`_PAC_FRIGHT` in `visualisers/pacman.py`. Dim pink pixels are the ghost-house door.

## Setup on the Pi

```sh
python3 -m venv ~/uh && ~/uh/bin/pip install unicornhat   # pulls in rpi_ws281x
echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/snd-blacklist.conf   # audio clashes with GPIO18 PWM
sudo cp unicorn-demo.service /etc/systemd/system/    # adjust paths/user if yours differ
sudo systemctl daemon-reload && sudo systemctl enable --now unicorn-demo
```

The LEDs need root, so the service runs as root. Open `http://<pi>:8080`. There is no login on the web UI,
so only run it on a trusted network.

## Notes

- The HAT is mounted upside down relative to the library default, so `visualisers/display.py` sets `uh.rotation(180)` once.
  Change that line if yours is the other way up.
- Brightness is a per-channel output ceiling: 12/255 by day (07:00-21:00 Pi time) and 4/255 at night. See `DAY_OUT` / `NIGHT_OUT` in `display.py`.
  The library's gamma table turns every dim colour into a pure primary, so `visualisers/display.py` disables it and tone-maps in software.
- Driving the board with raw `rpi_ws281x` only lit half of it on the test Pi; Pimoroni's `unicornhat` library works.
- Snake mistakes: `choose_human()` in `visualisers/snake_ai.py` (`p_greedy`, `p_slip`) controls how often it blunders.
- Regenerate screenshots on a PC with `python gen_shots.py`.

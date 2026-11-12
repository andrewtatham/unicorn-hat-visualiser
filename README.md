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
| `snake.py`, `classics.py`, `more.py` | The visualisers themselves. |
| `snake_ai.py` | Snake decision logic (kept display-free so it can be tested). |
| `gen_shots.py` | Renders the screenshots in `web/shots/` by running each visualiser against a fake display. |
| `unicorn-demo.service` | systemd unit to start it at boot. |

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

- The HAT is mounted upside down relative to the library default, so `snake.py` sets `uh.rotation(180)` once.
  Change that line if yours is the other way up.
- Brightness is 0.5 by day (07:00-21:00 Pi time) and 0.2 at night. See `DAY_BRIGHTNESS` / `NIGHT_BRIGHTNESS`.
- Driving the board with raw `rpi_ws281x` only lit half of it on the test Pi; Pimoroni's `unicornhat` library works.
- Snake mistakes: `choose_human()` in `snake_ai.py` (`p_greedy`, `p_slip`) controls how often it blunders.
- Regenerate screenshots on a PC with `python gen_shots.py`.

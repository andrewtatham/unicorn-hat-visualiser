"""Hardware setup, run once on first import: layout, rotation, software tone-mapping and day/night brightness.
Every visualiser imports `uh` from here so the setup is guaranteed to happen before anything is drawn."""
import time
import unicornhat as uh

W = H = 8
uh.set_layout(uh.AUTO)
# Brightness is a per-channel output ceiling (0-255 PWM). Day = 07:00-21:00 local time.
# The library's own gamma table maps every input below ~22 to zero, so at low brightness it
# collapsed every colour to a pure primary. We switch it off and tone-map in software instead,
# which keeps colour ratios (an orange stays orange) even when the whole board is dim.
DAY_OUT, NIGHT_OUT = 12, 4
TONE_GAMMA = 1.4
_HW = hasattr(uh, "disable_gamma")                # False when running against a fake display in tests
_lut = list(range(256))
_last_check = [0.0, None]
_real_show = uh.show


def _build_lut(out_max):
    for v in range(256):
        _lut[v] = int(round(out_max * (v / 255.0) ** TONE_GAMMA))


if _HW:
    uh.disable_gamma()
    uh.ws2812.setBrightness(255)                   # no hardware scaling; the cap is our output ceiling (tiny, so safe)
    _real_set_pixel = uh.set_pixel

    def _tone_set_pixel(x, y, r, g=None, b=None):
        if g is None:
            r, g, b = r
        c = lambda v: _lut[max(0, min(255, int(v)))]
        return _real_set_pixel(x, y, c(r), c(g), c(b))

    uh.set_pixel = _tone_set_pixel


def _auto_show():
    now = time.time()
    if now - _last_check[0] > 30:               # re-check the clock twice a minute
        _last_check[0] = now
        level = DAY_OUT if 7 <= time.localtime().tm_hour < 21 else NIGHT_OUT
        if level != _last_check[1]:
            _last_check[1] = level
            _build_lut(level)
    _real_show()


_build_lut(DAY_OUT)
uh.show = _auto_show
uh.rotation(180)  # board is mounted upside down relative to the library default

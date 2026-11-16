"""Pi dashboard: CPU cores, temperature, memory and network as live bars."""
import math, time
from .display import uh
from .common import hsv, px


def _cpu_times():
    out = []
    try:
        for line in open("/proc/stat"):
            if line.startswith("cpu") and line[3].isdigit():
                v = list(map(int, line.split()[1:])); out.append((v[3] + v[4], sum(v)))
    except OSError:
        pass
    return out


def _net_bytes():
    try:
        tot = 0
        for line in list(open("/proc/net/dev"))[2:]:
            name, data = line.split(":");
            if name.strip() != "lo": tot += int(data.split()[0]) + int(data.split()[8])
        return tot
    except OSError:
        return 0


def _bar(x, level, hue_lo=0.33, hue_hi=0.0):
    level = max(0, min(8, int(round(level))))
    for i in range(level):
        px(x, 7 - i, hsv(hue_lo + (hue_hi - hue_lo) * i / 7.0, 1, 0.9))


def run(sec=15):
    prev = _cpu_times(); pn = _net_bytes(); t0 = time.time(); pt = t0
    while time.time() - t0 < sec:
        time.sleep(0.5)
        cur = _cpu_times(); now = time.time(); nb = _net_bytes()
        uh.clear()
        for i, (a, b) in enumerate(zip(prev, cur)):
            idle, tot = b[0] - a[0], b[1] - a[1]
            _bar(i, 8 * (1 - idle / tot) if tot else 0)
        try: temp = int(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000.0
        except OSError: temp = 40.0
        _bar(5, (temp - 30) / 55.0 * 8)
        try:
            mi = {l.split(":")[0]: int(l.split()[1]) for l in open("/proc/meminfo")}
            mem = 1 - mi["MemAvailable"] / mi["MemTotal"]
        except (OSError, KeyError): mem = 0.3
        _bar(6, mem * 8)
        rate = (nb - pn) / max(0.01, now - pt)
        _bar(7, math.log10(rate + 1) / 6 * 8, 0.55, 0.85)
        uh.show(); prev, pn, pt = cur, nb, now

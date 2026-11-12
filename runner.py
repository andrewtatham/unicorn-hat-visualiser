#!/usr/bin/env python3
"""Entry point: runs enabled visualisers in order and serves the web UI on :8080. Run as root."""
import os, sys, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unicornhat as uh
import registry, server

# --- mirror what is on the board so the web UI can show it live ---
shadow = [[0, 0, 0] for _ in range(64)]
_sp, _clear, _off, _show = uh.set_pixel, uh.clear, uh.off, uh.show


def set_pixel(x, y, r, g=None, b=None):
    if g is None:
        r, g, b = r
    if 0 <= x < 8 and 0 <= y < 8:
        shadow[int(y) * 8 + int(x)] = [int(r), int(g), int(b)]
    return _sp(x, y, r, g, b)


def clear():
    for i in range(64):
        shadow[i] = [0, 0, 0]
    return _clear()


def off():
    for i in range(64):
        shadow[i] = [0, 0, 0]
    return _off()


def show():
    server.live["frame"] = [p[:] for p in shadow]
    return _show()


uh.set_pixel, uh.clear, uh.off, uh.show = set_pixel, clear, off, show

catalog = [{k: v[k] for k in ("id", "title", "desc", "cat")} for v in registry.V]


def pick(idx):
    with server.lock:
        if server.queue:
            return registry.BY_ID[server.queue.pop(0)], idx
    en = server.load_enabled()
    for _ in range(len(registry.V)):
        v = registry.V[idx % len(registry.V)]
        idx += 1
        if en.get(v["id"], True):
            return v, idx
    return None, idx


if __name__ == "__main__":
    server.start(catalog)
    idx = 0
    try:
        while True:
            v, idx = pick(idx)
            if v is None:
                server.live["current"] = None
                uh.clear(); uh.show(); time.sleep(1)
                continue
            server.live["current"] = v["id"]
            try:
                v["fn"]()
            except Exception:
                traceback.print_exc()
                time.sleep(1)
    finally:
        uh.off()

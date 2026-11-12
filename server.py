"""Tiny dependency-free web UI: list visualisers, enable/disable, play next, live board view."""
import json, os, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
CONFIG = os.path.join(HERE, "unicorn-config.json")
lock = threading.Lock()
queue = []                                  # ids requested via "play next"
live = {"current": None, "frame": [[0, 0, 0]] * 64}
_catalog = []                               # filled in by runner: list of dicts without fn


def load_enabled():
    try:
        with open(CONFIG) as f:
            return json.load(f).get("enabled", {})
    except (OSError, ValueError):
        return {}


def save_enabled(enabled):
    tmp = CONFIG + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"enabled": enabled}, f, indent=1)
    os.replace(tmp, CONFIG)
    try:
        st = os.stat(HERE)
        os.chown(CONFIG, st.st_uid, st.st_gid)
    except OSError:
        pass


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json", cache="no-store"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            with open(os.path.join(WEB, "index.html"), "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if path == "/api/state":
            en = load_enabled()
            items = [dict(c, enabled=en.get(c["id"], True)) for c in _catalog]
            with lock:
                return self._send(200, {"visualisers": items, "current": live["current"],
                                        "frame": live["frame"], "queue": list(queue)})
        if path.startswith("/shots/") and path.endswith(".png"):
            full = os.path.join(WEB, "shots", os.path.basename(path))
            if os.path.isfile(full):
                with open(full, "rb") as f:
                    return self._send(200, f.read(), "image/png", "public, max-age=3600")
        self._send(404, {"error": "not found"})

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self._send(400, {"error": "bad json"})
        ids = {c["id"] for c in _catalog}
        path = self.path.split("?")[0]
        with lock:
            en = load_enabled()
            if path == "/api/enable" and data.get("id") in ids:
                en[data["id"]] = bool(data.get("enabled"))
                save_enabled(en)
            elif path == "/api/bulk":
                save_enabled({i: bool(data.get("enabled")) for i in ids})
            elif path == "/api/next" and data.get("id") in ids:
                queue.append(data["id"])
            else:
                return self._send(400, {"error": "bad request"})
        self._send(200, {"ok": True})


def start(catalog, port=8080):
    _catalog[:] = catalog
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

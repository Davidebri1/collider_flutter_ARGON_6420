# Made by Claude (2026-10-21). Round 10: the phone link (collider_tunnel.py) and its key at the door.
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for: {old[:80]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("tools/collider_server.py", [
    ("import collider_imagine as cimagine\n", "import collider_imagine as cimagine\nimport collider_tunnel as ctunnel\n"),
    ("IMAGINE = None\n", "IMAGINE = None\nTUNNEL = None\n"),
    ("    global ROOT, WEB, DATA, PORT, FILES, THUMBS, IMAGINE, HIST,",
     "    global ROOT, WEB, DATA, PORT, FILES, THUMBS, IMAGINE, TUNNEL, HIST,"),
    ("""    _extend_roster()
    _init_caches()
""",
     """    _extend_roster()
    _init_caches()
    # The phone link: a private https address through Cloudflare's tunnel, when bin\\cloudflared.exe is beside the app.
    import atexit
    TUNNEL = ctunnel.Tunnel(ROOT, PORT)
    if TUNNEL.start():
        atexit.register(TUNNEL.stop)
"""),
    ("""    def do_GET(self):
        p = self.path.split("?")[0]
""",
     """    def _local(self):
        \"\"\"Asked on this computer itself (the app's own window, or a browser here).\"\"\"
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        return self.client_address[0] in ("127.0.0.1", "::1") and host in ("127.0.0.1", "localhost", "::1") \\
            and not self.headers.get("Cf-Connecting-Ip")

    def _let_in(self):
        \"\"\"Through the phone link only with its key: once in the address, then kept by the phone as a cookie.\"\"\"
        if self._local():
            return True
        import hmac
        from urllib.parse import urlparse, parse_qs
        key = TUNNEL.key if TUNNEL else ""
        if not key:
            return False
        jar = dict(c.strip().split("=", 1) for c in (self.headers.get("Cookie") or "").split(";") if "=" in c)
        if hmac.compare_digest(jar.get("collider_key", ""), key):
            return True
        given = (parse_qs(urlparse(self.path).query).get("k") or [""])[0]
        if self.command == "GET" and given and hmac.compare_digest(given, key):
            self.send_response(302)
            self.send_header("Set-Cookie", f"collider_key={key}; Path=/; Max-Age=31536000; Secure; HttpOnly; SameSite=Lax")
            self.send_header("Location", "/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        return False

    def do_GET(self):
        ok = self._let_in()
        if ok is None:
            return
        if not ok:
            return self._send(403, "text/plain", b"")
        p = self.path.split("?")[0]
        if p == "/api/phone":
            if not self._local() or not TUNNEL:
                return self._json({"link": "", "qr": ""})
            return self._json({"link": TUNNEL.link(), "qr": TUNNEL.qr()})
"""),
    ("""    def do_POST(self):
        p = self.path.split("?")[0]
""",
     """    def do_HEAD(self):
        if not self._let_in():
            return self._send(403, "text/plain", b"")
        return super().do_HEAD()

    def do_POST(self):
        if not self._let_in():
            return self._send(403, "text/plain", b"")
        p = self.path.split("?")[0]
"""),
])

edit("dev/build_exe.py", [
    ('''"--hidden-import", "collider_imagine",''', '''"--hidden-import", "collider_imagine", "--hidden-import", "collider_tunnel", "--hidden-import", "segno",'''),
])

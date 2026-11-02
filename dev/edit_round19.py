# Made by Claude (2026-10-21). Round 19: the phone link that never changes (dev/cf_phone): the tunnel tells the Worker
# its new address each time it starts, and the link given to the phone is the Worker's, with the key.
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


edit("tools/collider_tunnel.py", [
    ("""import base64, io, os, re, secrets, shutil, subprocess, threading""",
     """import base64, io, json, os, re, secrets, shutil, subprocess, threading, urllib.request"""),
    ("""    def __init__(self, root, port):
        self.root = root
        self.port = int(port)
        self.key = secrets.token_urlsafe(18)""",
     """    def __init__(self, root, port, relay=None):
        \"\"\"relay: the configuration's Phone row (collider-phone Worker): its key is the link's key, kept across starts.\"\"\"
        self.root = root
        self.port = int(port)
        self.relay = relay or {}
        self.key = (self.relay.get("key") or "").strip() or secrets.token_urlsafe(18)"""),
    ("""            if m and not self.url:
                self.url = m.group(0).decode()""",
     """            if m and not self.url:
                self.url = m.group(0).decode()
                threading.Thread(target=self._announce, daemon=True).start()

    def _announce(self):
        \"\"\"Tells the Worker where Collider is now, so the unchanging link leads here.\"\"\"
        ep = (self.relay.get("endpoint") or "").rstrip("/")
        if not ep:
            return
        for _ in range(5):
            try:
                req = urllib.request.Request(ep + "/set", data=json.dumps({"url": self.url}).encode(), headers={
                    "Content-Type": "application/json", "Authorization": "Key " + self.key, "User-Agent": "Collider/1.0"})
                urllib.request.urlopen(req, timeout=20).read()
                return
            except Exception as e:
                print("phone link not recorded yet", str(e)[:80])
                import time
                time.sleep(5)"""),
    ("""    def link(self):
        return f"{self.url}/?k={self.key}" if self.url else \"\"""",
     """    def link(self):
        if not self.url:
            return ""
        ep = (self.relay.get("endpoint") or "").rstrip("/")
        return f"{ep}/{self.key}" if ep else f"{self.url}/?k={self.key}\""""),
])

edit("tools/collider_config.py", [
    ("""def is_fal(row):""",
     """def is_phone(row):
    \"\"\"The phone link's Worker (dev/cf_phone).\"\"\"
    return "collider-phone" in (row.get("endpoint") or "").lower()


def is_fal(row):"""),
])

edit("tools/collider_server.py", [
    ("""    TUNNEL = ctunnel.Tunnel(ROOT, PORT)""",
     """    TUNNEL = ctunnel.Tunnel(ROOT, PORT, next((r for r in rows() if ccfg.is_phone(r)), None))"""),
    ("""        if ccfg.is_speech(r) or ccfg.is_fal(r) or ccfg.is_pictures(r):""",
     """        if ccfg.is_speech(r) or ccfg.is_fal(r) or ccfg.is_pictures(r) or ccfg.is_phone(r):"""),
    ("""    if ccfg.is_pictures(row):""",
     """    if ccfg.is_phone(row):
        return "The phone link: always the same address, leading to this computer (Settings > Account > Phone)"
    if ccfg.is_pictures(row):"""),
])

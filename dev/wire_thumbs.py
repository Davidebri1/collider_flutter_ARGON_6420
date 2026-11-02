# Made by Claude (2026-10-20). One-time edit: the server hands Files a preview picture of each file.
import os
root = os.path.join(os.path.dirname(__file__), "..")


def edit(rel, pairs):
    p = os.path.join(root, rel)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        if s.count(a) != 1:
            raise SystemExit(f"{rel}: expected one of {a!r}, found {s.count(a)}")
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s)


edit("tools/collider_server.py", [
    ("import collider_config as ccfg\n", "import collider_config as ccfg\nimport collider_thumbs as cthumbs\n"),
    ("FILES = None\nHIST", "FILES = None\nTHUMBS = None\nHIST"),
    ("    global ROOT, WEB, DATA, PORT, FILES, HIST,", "    global ROOT, WEB, DATA, PORT, FILES, THUMBS, HIST,"),
    ("    FILES = cfiles.Files(DATA)\n", "    FILES = cfiles.Files(DATA)\n    THUMBS = cthumbs.Thumbs(FILES.root)\n"),
    ("        if p == \"/api/files\":\n",
     "        if p == \"/api/files/thumb\":\n            return self._thumb()\n        if p == \"/api/files\":\n"),
    ("    def _part(self, path):",
     "    def _thumb(self):\n"
     "        \"\"\"A preview picture of one file in Files (collider_thumbs); 404 when it has nothing of its own to show.\"\"\"\n"
     "        from urllib.parse import urlparse, parse_qs\n"
     "        q = parse_qs(urlparse(self.path).query)\n"
     "        path = FILES.path_for((q.get(\"source\") or [\"\"])[0], (q.get(\"name\") or [\"\"])[0])\n"
     "        out = THUMBS.path_for(path) if path else None\n"
     "        if not out:\n"
     "            return self._send(404, \"text/plain\", b\"\")\n"
     "        data = open(out, \"rb\").read()\n"
     "        self.send_response(200)\n"
     "        self.send_header(\"Content-Type\", \"image/png\")\n"
     "        self.send_header(\"Cache-Control\", \"max-age=3600\")\n"
     "        self.send_header(\"Content-Length\", str(len(data)))\n"
     "        self.end_headers()\n"
     "        self.wfile.write(data)\n\n"
     "    def _part(self, path):"),
])
edit("dev/build_exe.py", [
    ("\"--hidden-import\", \"collider_config\",", "\"--hidden-import\", \"collider_config\", \"--hidden-import\", \"collider_thumbs\","),
])
print("ok")

# Made by Claude (2026-10-21). Round 13: the picture providers in the server (Cloudflare, NVIDIA, fal).
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


edit("tools/collider_config.py", [
    ("""def is_fal(row):""",
     """def is_pictures(row):
    \"\"\"Collider's own picture Worker on Cloudflare (dev/cf_imagine).\"\"\"
    return "collider-imagine" in (row.get("endpoint") or "").lower()


def is_fal(row):"""),
])

edit("tools/collider_server.py", [
    ("""    IMAGINE = cimagine.Imagine(DATA, FILES, lambda: [r for r in rows() if ccfg.is_fal(r)], lambda: CONFIG.get("imagine"))""",
     """    IMAGINE = cimagine.Imagine(DATA, FILES, _picture_rows, lambda: CONFIG.get("imagine"))"""),
    ("""def next_row(name=None, search=None):""",
     """def _picture_rows(provider):
    \"\"\"Rows with keys for a picture provider: Cloudflare (Collider's Worker), NVIDIA, fal. (Claude, 2026-10-21)\"\"\"
    if provider == "Cloudflare":
        return [r for r in rows() if ccfg.is_pictures(r)]
    if provider == "fal":
        return [r for r in rows() if ccfg.is_fal(r)]
    if provider == "NVIDIA":
        return [r for r in rows() if "integrate.api.nvidia.com" in (r.get("endpoint") or "")]
    return []


def next_row(name=None, search=None):"""),
    ("""        if ccfg.is_speech(r) or ccfg.is_fal(r):""", """        if ccfg.is_speech(r) or ccfg.is_fal(r) or ccfg.is_pictures(r):"""),
    ("""    if ccfg.is_fal(row):
        return "Discover Market: pictures and videos (/api/imagine)"
""", """    if ccfg.is_fal(row):
        return "Pictures (Grok Imagine, paid) and videos (/api/imagine)"
    if ccfg.is_pictures(row):
        return "Pictures through Collider's Cloudflare Worker, free each day up to Cloudflare's allowance (/api/imagine)"
"""),
    ("""        if p == "/api/imagine":
            return self._json({"items": IMAGINE.listing()})""",
     """        if p == "/api/imagine":
            return self._json({"items": IMAGINE.listing(), "models": IMAGINE.models()})"""),
    ("""                return self._json(IMAGINE.start(b.get("text", ""), b.get("kind", "image"), b.get("from"), b.get("replace")))""",
     """                return self._json(IMAGINE.start(b.get("text", ""), b.get("kind", "image"), b.get("from"), b.get("replace"),
                                                b.get("model"), b.get("references"), b.get("aspect"), b.get("count")))"""),
])

edit("dev/cf_imagine/wrangler.toml", [("workers_dev = true\n", "workers_dev = true\npreview_urls = false\n")])

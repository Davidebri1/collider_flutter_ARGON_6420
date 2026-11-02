# Made by Claude (2026-10-21). Round 5: Discover Market wired to fal.
# David, 20 Oct: "discover market should be wired to Fal ... whatever functionality imagine market has, discover market has."
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


# ---- Files: a made picture or video, saved as bytes with who made it ----
edit("tools/collider_files.py", [
    ("""    def print_pdf(self, name, html, replace="", model=""):""",
     """    def save_media(self, name, data, model=""):
        \"\"\"A picture or video made through fal (Discover Market), into Generated. (Claude, 2026-10-20)\"\"\"
        p = self.unique_path("generated", name)
        with open(p, "wb") as f:
            f.write(data)
        self._remember(os.path.basename(p), model)
        return os.path.basename(p)

    def print_pdf(self, name, html, replace="", model=""):"""),
])

# ---- Configuration: the fal row, taken from the keys file like the others ----
edit("tools/collider_config.py", [
    ("""THEMES = "https://collider-themes.ebridavid.workers.dev/"
""",
     """# Discover Market: pictures and videos through fal's queue. Added by Claude on 2026-10-20.
FAL_QUEUE = "https://queue.fal.run"
THEMES = "https://collider-themes.ebridavid.workers.dev/"
"""),
    ("""    rows += _speech_rows(text)
    if not rows:""",
     """    rows += _speech_rows(text)
    rows += _fal_rows(text)
    if not rows:"""),
    ("""                cfg["providers"] += _speech_rows(open(KEYS_FILE, encoding="utf-8", errors="ignore").read())
            return cfg""",
     """                cfg["providers"] += _speech_rows(open(KEYS_FILE, encoding="utf-8", errors="ignore").read())
            if not any(is_fal(r) for r in cfg["providers"]) and os.path.exists(KEYS_FILE):
                cfg["providers"] += _fal_rows(open(KEYS_FILE, encoding="utf-8", errors="ignore").read())
            return cfg"""),
    ("""def is_speech(row):""",
     """def _fal_rows(text):
    return [{"name": "fal", "endpoint": FAL_QUEUE, "key": k, "models": ""}
            for k in dict.fromkeys(re.findall(r"\\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}:[0-9a-fA-F]{32}\\b", text))]


def is_fal(row):
    return "fal.run" in (row.get("endpoint") or "").lower()


def is_speech(row):"""),
])

# ---- Server ----
edit("tools/collider_server.py", [
    ("""import collider_thumbs as cthumbs
""", """import collider_thumbs as cthumbs
import collider_imagine as cimagine
"""),
    ("""THUMBS = None
""", """THUMBS = None
IMAGINE = None
"""),
    ("""    global ROOT, WEB, DATA, PORT, FILES, THUMBS, HIST, SMARTGEN_FILE, CONFIG, _history_mem, _smartgen_mem""",
     """    global ROOT, WEB, DATA, PORT, FILES, THUMBS, IMAGINE, HIST, SMARTGEN_FILE, CONFIG, _history_mem, _smartgen_mem"""),
    ("""    THUMBS = cthumbs.Thumbs(FILES.root)
""", """    THUMBS = cthumbs.Thumbs(FILES.root)
    IMAGINE = cimagine.Imagine(DATA, FILES, lambda: [r for r in rows() if ccfg.is_fal(r)], lambda: CONFIG.get("imagine"))
"""),
    ("""        if ccfg.is_speech(r):
            continue
        for mid in ccfg.models_of(r):""",
     """        if ccfg.is_speech(r) or ccfg.is_fal(r):
            continue
        for mid in ccfg.models_of(r):"""),
    ("""        return "Voice chat: what is said, turned into text (/api/transcribe)"
""", """        return "Voice chat: what is said, turned into text (/api/transcribe)"
    if ccfg.is_fal(row):
        return "Discover Market: pictures and videos (/api/imagine)"
"""),
    ("""            "pack_price": PACK_PRICE, "tracks_per_pack": TRACKS_PER_PACK}""",
     """            "pack_price": PACK_PRICE, "tracks_per_pack": TRACKS_PER_PACK, "imagine": dict(cimagine.DEFAULTS)}"""),
    ("""    PACK_PRICE, TRACKS_PER_PACK = str(cfg["pack_price"]), int(cfg["tracks_per_pack"])
    return missing""",
     """    PACK_PRICE, TRACKS_PER_PACK = str(cfg["pack_price"]), int(cfg["tracks_per_pack"])
    missing = missing or any(k not in cfg["imagine"] for k in cimagine.DEFAULTS)
    cfg["imagine"] = {**cimagine.DEFAULTS, **cfg["imagine"]}
    return missing"""),
    ("""        if p == "/api/files":
            return self._json(FILES.listing(list(LABEL.values())))""",
     """        if p == "/api/files":
            return self._json(FILES.listing(list(LABEL.values())))
        if p == "/api/imagine":
            return self._json({"items": IMAGINE.listing()})"""),
    ("""            if p == "/api/transcribe":""",
     """            if p == "/api/imagine":
                b = self._body()
                return self._json(IMAGINE.start(b.get("text", ""), b.get("kind", "image"), b.get("from")))
            if p == "/api/transcribe":"""),
])

# ---- Launch window: the Discover Market lines shown with the rest ----
edit("tools/collider_app.py", [
    ("""pack_price:'Pack price',tracks_per_pack:'Tracks per pack'};""",
     """pack_price:'Pack price',tracks_per_pack:'Tracks per pack',imagine:'Discover Market'};"""),
    ("""['pack_price','tracks_per_pack'].forEach(k=>section(k,document.getElementById('buy')));""",
     """['pack_price','tracks_per_pack'].forEach(k=>section(k,document.getElementById('buy')));
['imagine'].forEach(k=>section(k,document.getElementById('answers')));"""),
    ("""if(/tavily/i.test((r.endpoint||'')+(r.name||'')))""",
     """if(/tavily|fal\\.run/i.test((r.endpoint||'')+(r.name||'')))"""),
])

edit("dev/build_exe.py", [
    ('''"--hidden-import", "collider_thumbs",''', '''"--hidden-import", "collider_thumbs", "--hidden-import", "collider_imagine",'''),
])

# ---- App: what Discover Market has made ----
D = ROOT / "dev" / "draft"
edit("lib/core/api/collider_api.dart", [
    ("""/// One entry in Files. Sources: uploaded, generated, purchased, downloaded.""",
     (D / "creation_class.dart").read_text(encoding="utf-8").rstrip() + "\n\n/// One entry in Files. Sources: uploaded, generated, purchased, downloaded."),
    ("""  String fileUrl(ColliderFile f) =>""",
     (D / "api_additions.dart").read_text(encoding="utf-8").rstrip() + "\n\n  String fileUrl(ColliderFile f) =>"),
])

MS = ROOT / "lib/features/market/screens/market_screen.dart"
old = MS.read_text(encoding="utf-8")
cut = old.index("/// A feed tile:")
MS.write_text((D / "market_screen_head.dart").read_text(encoding="utf-8").rstrip() + "\n\n" + old[cut:].rstrip() + "\n\n"
              + (D / "market_additions.dart").read_text(encoding="utf-8"), encoding="utf-8")
print("assembled market_screen.dart")

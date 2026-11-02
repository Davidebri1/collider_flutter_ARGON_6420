"""Collider Files: a preview picture of each file itself. Made by Claude (2026-10-20).

David: "i want the specific item thumbnail, not a generic placeholder ... stls should show the 3d model's specific
thumbnail image. pdf should show the document page preview. images show the thumbnail image. videos show the
thumbnail shot."

Each preview is made once and kept in data\\files\\.thumbs (named for the file, its size and its time, so an edited
file gets a new one). How each kind is drawn:
  pictures       the picture, scaled down (Pillow); SVG drawn by Edge
  PDF            its first page (PDFium)
  video          the frame Windows itself shows for it (the Windows thumbnail service, as in File Explorer)
  songs          the cover kept inside the file; else the one Windows shows
  STL, OBJ       the model drawn here, lit, from above at an angle; 3MF its own saved picture
  Word, Excel,   the picture Office keeps inside the file; else the one Windows shows; else its first page drawn
  PowerPoint     from its contents by Edge
  text, code,    the start of the file set as a page and drawn by Edge
  Markdown, HTML
  programs       their own icon, from Windows
Archives and anything with nothing of its own to show keep the coloured tile in the app.
"""
import hashlib, html, io, os, re, shutil, subprocess, tempfile, threading, zipfile

SIZE = 640  # longest side of a preview; Files shows it small, so it stays sharp on any screen
PICTURES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".ico"}
VIDEOS = {".mp4", ".m4v", ".mov", ".webm", ".mkv", ".avi", ".wmv", ".mpg", ".mpeg", ".3gp"}
SONGS = {".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wav", ".wma"}
OFFICE = {".docx", ".xlsx", ".pptx", ".docm", ".xlsm", ".pptm"}
TEXTS = {".txt", ".log", ".csv", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".py", ".dart", ".js", ".ts",
         ".css", ".sql", ".sh", ".bat", ".ps1", ".c", ".cpp", ".h", ".java", ".go", ".rs"}
PROGRAMS = {".exe", ".msi", ".lnk", ".appref-ms"}
NONE = {".zip", ".7z", ".rar", ".gz", ".tar"}

_locks = {}
_locks_guard = threading.Lock()
_edge_slots = threading.Semaphore(2)


class Thumbs:
    def __init__(self, files_root):
        self.dir = os.path.join(files_root, ".thumbs")
        os.makedirs(self.dir, exist_ok=True)

    def path_for(self, path):
        """The preview of the file at [path] (made now if needed), or None when it has nothing of its own to show."""
        st = os.stat(path)
        key = hashlib.sha1(f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}".encode("utf-8", "ignore")).hexdigest()
        out = os.path.join(self.dir, key + ".png")
        miss = os.path.join(self.dir, key + ".none")
        if os.path.isfile(out):
            return out
        if os.path.isfile(miss):
            return None
        with _locks_guard:
            lock = _locks.setdefault(key, threading.Lock())
        with lock:
            if os.path.isfile(out):
                return out
            try:
                img = make(path)
            except Exception:
                img = None
            if img is None:
                open(miss, "w").close()
                return None
            img.save(out + ".tmp", "PNG", optimize=True)
            os.replace(out + ".tmp", out)
            return out


def _fit(img):
    from PIL import Image
    img = img.convert("RGBA") if img.mode not in ("RGB", "RGBA") else img
    img.thumbnail((SIZE, SIZE), Image.LANCZOS)
    return img


def make(path):
    from PIL import Image
    ext = os.path.splitext(path)[1].lower()
    if ext in NONE:
        return None
    if ext in PICTURES:
        with Image.open(path) as im:
            im.seek(0)
            return _fit(im.copy())
    if ext == ".svg":
        return _edge_shot(path, 640, 640, trim=True)
    if ext == ".pdf":
        return _pdf(path)
    if ext in (".stl", ".obj"):
        return _model(path)
    if ext == ".3mf":
        return _zip_picture(path, ("Metadata/thumbnail.png", "Metadata/plate_1.png", "Auxiliaries/.thumbnails/thumbnail_middle.png"))
    if ext in SONGS:
        return _song_cover(path) or _windows(path, thumbnail_only=True)
    if ext in VIDEOS:
        return _windows(path, thumbnail_only=True)
    if ext in OFFICE:
        return (_zip_picture(path, ("docProps/thumbnail.jpeg", "docProps/thumbnail.png", "docProps/thumbnail.wmf"))
                or _windows(path, thumbnail_only=True) or _office_page(path, ext))
    if ext in (".md", ".markdown"):
        import markdown
        text = open(path, encoding="utf-8", errors="ignore").read(60000)
        return _page(markdown.markdown(text, extensions=["tables", "fenced_code"]), small=True)
    if ext in (".html", ".htm"):
        return _edge_shot(path, 1280, 960)
    if ext == ".csv":
        import csv
        rows = list(csv.reader(open(path, encoding="utf-8", errors="ignore").read(20000).splitlines()))[:30]
        return _page("<table>" + "".join("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in r[:10]) + "</tr>" for r in rows) + "</table>", small=True)
    if ext in TEXTS:
        lines = open(path, encoding="utf-8", errors="ignore").read(20000).splitlines()[:70]
        return _page(f"<pre>{html.escape(chr(10).join(lines))}</pre>", small=True)
    if ext in PROGRAMS:
        return _windows(path, thumbnail_only=False)
    return _windows(path, thumbnail_only=True)


# ---------------- PDF ----------------
def _pdf(path):
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(path)
    try:
        page = doc[0]
        w, h = page.get_size()
        img = page.render(scale=SIZE / max(w, h)).to_pil()
        return _fit(img)
    finally:
        doc.close()


# ---------------- pictures kept inside zip-based files (Office, 3MF) ----------------
def _zip_picture(path, names):
    from PIL import Image
    try:
        with zipfile.ZipFile(path) as z:
            have = {n.lower(): n for n in z.namelist()}
            for n in names:
                real = have.get(n.lower())
                if real and not real.lower().endswith(".wmf"):
                    return _fit(Image.open(io.BytesIO(z.read(real))))
    except Exception:
        pass
    return None


# ---------------- song covers ----------------
def _song_cover(path):
    from PIL import Image
    try:
        import mutagen
        f = mutagen.File(path)
        if f is None:
            return None
        data = None
        tags = getattr(f, "tags", None)
        if tags is not None:
            for k in list(tags.keys()):
                if str(k).startswith("APIC"):
                    data = tags[k].data
                    break
            if data is None and "covr" in tags:
                data = bytes(tags["covr"][0])
        if data is None and getattr(f, "pictures", None):
            data = f.pictures[0].data
        if data is None and tags is not None and "metadata_block_picture" in tags:
            import base64
            from mutagen.flac import Picture
            data = Picture(base64.b64decode(tags["metadata_block_picture"][0])).data
        return _fit(Image.open(io.BytesIO(data))) if data else None
    except Exception:
        return None


# ---------------- 3D models ----------------
def _mesh(path):
    import numpy as np
    raw = open(path, "rb").read()
    if path.lower().endswith(".obj"):
        text = raw.decode("utf-8", "ignore")
        v = np.array([[float(x) for x in l.split()[1:4]] for l in text.splitlines() if l.startswith("v ")], dtype=np.float32)
        tris = []
        for l in text.splitlines():
            if l.startswith("f "):
                idx = [int(p.split("/")[0]) for p in l.split()[1:]]
                idx = [i - 1 if i > 0 else len(v) + i for i in idx]
                for k in range(1, len(idx) - 1):
                    tris.append((idx[0], idx[k], idx[k + 1]))
        return v[np.array(tris, dtype=np.int64)] if tris else None
    if len(raw) >= 84:
        n = int.from_bytes(raw[80:84], "little")
        if 84 + 50 * n == len(raw):
            dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
            return np.frombuffer(raw, dtype=dt, count=n, offset=84)["v"].astype(np.float32)
    pts = re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", raw)
    if not pts:
        return None
    return np.array(pts, dtype=np.float32).reshape(-1, 3, 3)


def _model(path):
    """Draws the model lit from the upper left, seen from above at an angle, the near faces over the far ones."""
    import numpy as np
    from PIL import Image, ImageDraw
    tri = _mesh(path)
    if tri is None or len(tri) == 0:
        return None
    pts = tri.reshape(-1, 3)
    centre = (pts.min(0) + pts.max(0)) / 2
    tri = tri - centre
    # Z is up in most printing files; look from the front-right, 30 degrees above
    az, el = np.radians(-35), np.radians(28)
    rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]], dtype=np.float32)
    rx = np.array([[1, 0, 0], [0, np.cos(el), -np.sin(el)], [0, np.sin(el), np.cos(el)]], dtype=np.float32)
    # into view space: x right, y up, z towards the viewer
    to_view = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=np.float32)
    t = tri @ rz.T @ to_view.T @ rx.T
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ln = np.linalg.norm(n, axis=1)
    keep = (ln > 0) & (n[:, 2] > 0)
    t, n = t[keep], n[keep] / ln[keep, None]
    if len(t) == 0:
        return None
    light = np.array([-0.45, 0.6, 0.66], dtype=np.float32)
    light /= np.linalg.norm(light)
    shade = 0.32 + 0.68 * np.clip(n @ light, 0, 1)
    order = np.argsort(t[:, :, 2].mean(1))
    xy = t[:, :, :2]
    lo, hi = xy.reshape(-1, 2).min(0), xy.reshape(-1, 2).max(0)
    span = float(max(hi - lo)) or 1.0
    S = SIZE * 2
    scale = S * 0.86 / span
    off = (S - (hi - lo) * scale) / 2
    px = (xy - lo) * scale + off
    px[:, :, 1] = S - px[:, :, 1]
    base = np.array([196, 206, 222], dtype=np.float32)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cols = (base[None, :] * shade[:, None]).astype(np.uint8)
    for i in order:
        p = px[i]
        c = tuple(int(x) for x in cols[i]) + (255,)
        d.polygon([(p[0, 0], p[0, 1]), (p[1, 0], p[1, 1]), (p[2, 0], p[2, 1])], fill=c, outline=c)
    return _fit(img.resize((SIZE, SIZE), Image.LANCZOS))


# ---------------- Windows' own thumbnails (as File Explorer shows them) ----------------
def _windows(path, thumbnail_only=True):
    import ctypes
    from ctypes import wintypes as wt
    from PIL import Image
    if os.name != "nt":
        return None
    ole32, shell32, gdi32, user32 = ctypes.windll.ole32, ctypes.windll.shell32, ctypes.windll.gdi32, ctypes.windll.user32
    user32.GetDC.restype = ctypes.c_void_p
    user32.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    gdi32.GetDIBits.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,
                                ctypes.c_void_p, ctypes.c_uint]
    gdi32.GetObjectW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    gdi32.DeleteObject.argtypes = [ctypes.c_void_p]

    class GUID(ctypes.Structure):
        _fields_ = [("a", ctypes.c_uint32), ("b", ctypes.c_uint16), ("c", ctypes.c_uint16), ("d", ctypes.c_ubyte * 8)]

    class SIZE_(ctypes.Structure):
        _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

    class BITMAP(ctypes.Structure):
        _fields_ = [("bmType", ctypes.c_long), ("bmWidth", ctypes.c_long), ("bmHeight", ctypes.c_long),
                    ("bmWidthBytes", ctypes.c_long), ("bmPlanes", wt.WORD), ("bmBitsPixel", wt.WORD), ("bmBits", ctypes.c_void_p)]

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long), ("biPlanes", wt.WORD),
                    ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                    ("biXPelsPerMeter", ctypes.c_long), ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wt.DWORD),
                    ("biClrImportant", wt.DWORD)]

    iid = GUID(0xBCC18B79, 0xBA16, 0x442F, (ctypes.c_ubyte * 8)(0x80, 0xC4, 0x8A, 0x59, 0xC3, 0x0C, 0x46, 0x3B))
    ole32.CoInitializeEx(None, 2)
    factory = ctypes.c_void_p()
    shell32.SHCreateItemFromParsingName.argtypes = [wt.LPCWSTR, ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
    if shell32.SHCreateItemFromParsingName(os.path.abspath(path), None, ctypes.byref(iid), ctypes.byref(factory)) != 0 or not factory:
        return None
    vtbl = ctypes.cast(ctypes.cast(factory, ctypes.POINTER(ctypes.c_void_p))[0], ctypes.POINTER(ctypes.c_void_p))
    GetImage = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, SIZE_, ctypes.c_int, ctypes.POINTER(wt.HBITMAP))(vtbl[3])
    Release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtbl[2])
    hbm = wt.HBITMAP()
    flags = 0x8 if thumbnail_only else 0x0  # SIIGBF_THUMBNAILONLY, or the item's own icon allowed
    try:
        if GetImage(factory, SIZE_(SIZE, SIZE), flags | 0x1, ctypes.byref(hbm)) != 0 or not hbm:
            return None
        bm = BITMAP()
        gdi32.GetObjectW(hbm, ctypes.sizeof(bm), ctypes.byref(bm))
        w, h = bm.bmWidth, abs(bm.bmHeight)
        bi = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
        buf = ctypes.create_string_buffer(w * h * 4)
        dc = user32.GetDC(None)
        gdi32.GetDIBits(dc, hbm, 0, h, buf, ctypes.byref(bi), 0)
        user32.ReleaseDC(None, dc)
        img = Image.frombuffer("RGBA", (w, h), buf.raw, "raw", "BGRA", 0, 1)
        if img.getchannel("A").getextrema() == (0, 0):
            img = img.convert("RGB")
        return _fit(img.copy())
    finally:
        if hbm:
            gdi32.DeleteObject(hbm)
        Release(factory)


# ---------------- pages drawn by Edge ----------------
PAGE_CSS = """@page{margin:0}html,body{margin:0;background:#fff}body{width:816px;padding:56px 64px;box-sizing:border-box;
color:#1d1d1f;font:15px/1.55 'Segoe UI',system-ui,sans-serif}h1{font-size:28px;margin:.2em 0 .4em}h2{font-size:22px}
h3{font-size:18px}img{max-width:100%}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid #d1d1d6;
padding:4px 6px;text-align:left;vertical-align:top}th{background:#f2f2f7}pre,code{font:13px/1.45 'Cascadia Mono',Consolas,monospace}
pre{margin:0;white-space:pre-wrap;word-break:break-word}blockquote{border-left:3px solid #d1d1d6;margin:0;padding-left:12px;color:#48484a}"""


def _page(body, small=False):
    """A page of [body]. small: a narrower page, so short notes and code read at thumbnail size."""
    w, h = (520, 693) if small else (816, 1056)
    css = PAGE_CSS.replace("width:816px;padding:56px 64px", f"width:{w}px;padding:{36 if small else 56}px {40 if small else 64}px")
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "page.html")
        open(p, "w", encoding="utf-8").write(f"<!doctype html><meta charset='utf-8'><style>{css}</style><body>{body}</body>")
        return _edge_shot(p, w, h)


def _office_page(path, ext):
    if ext in (".docx", ".docm"):
        import mammoth
        with open(path, "rb") as f:
            body = mammoth.convert_to_html(f, convert_image=mammoth.images.data_uri).value
        return _page(body)
    if ext in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.worksheets[0]
        rows = []
        for r in ws.iter_rows(max_row=40, max_col=12, values_only=True):
            rows.append("<tr>" + "".join(f"<td>{html.escape('' if v is None else str(v))}</td>" for v in r) + "</tr>")
        wb.close()
        return _page(f"<table>{''.join(rows)}</table>")
    if ext in (".pptx", ".pptm"):
        with zipfile.ZipFile(path) as z:
            xml = z.read("ppt/slides/slide1.xml").decode("utf-8", "ignore") if "ppt/slides/slide1.xml" in z.namelist() else ""
        parts = [html.unescape(t) for t in re.findall(r"<a:t>([^<]*)</a:t>", xml)]
        if not parts:
            return None
        body = f"<h1>{html.escape(parts[0])}</h1>" + "".join(f"<p>{html.escape(t)}</p>" for t in parts[1:12])
        return _page(body)
    return None


def _edge():
    for p in (shutil.which("msedge"),
              os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
              os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")):
        if p and os.path.isfile(p):
            return p
    return None


def _edge_shot(path, w, h, trim=False):
    """A picture of [path] as Edge draws it, at w x h (its own, separate profile; nothing of the user's is touched)."""
    from PIL import Image
    edge = _edge()
    if not edge:
        return None
    with _edge_slots, tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "shot.png")
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars", "--mute-audio",
                        "--force-device-scale-factor=1", f"--window-size={w},{h}", "--virtual-time-budget=2500",
                        "--user-data-dir=" + os.path.join(tmp, "profile"), "--screenshot=" + out,
                        "file:///" + os.path.abspath(path).replace("\\", "/")],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if not os.path.isfile(out):
            return None
        img = Image.open(out)
        img.load()
        if trim:
            bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
            from PIL import ImageChops
            box = ImageChops.difference(img, bg).getbbox()
            if box:
                img = img.crop(box)
        return _fit(img.copy())

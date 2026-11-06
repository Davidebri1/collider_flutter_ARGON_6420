# Collider ARGON 6420 permanent online host entry point (Hugging Face Docker Space + Cloudflare R2 argon6420_* store).
import io, json, os, sys, tarfile, threading, time, urllib.request
from http.server import ThreadingHTTPServer

os.environ["COLLIDER_PUBLIC_HOST"] = "1"

APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP, "data")
WEB = os.path.join(APP, "build", "web")
STORE = json.load(open(os.path.join(APP, "store.json")))
PORT = int(os.environ.get("PORT") or 7860)
SKIP = ("window", "window-browser", "collider_app.log", ".cache")
DATA_ARCHIVE = "argon6420_data.tar.gz"
WEB_ARCHIVE = "argon6420_web.tar.gz"


def _req(name, body=None):
    r = urllib.request.Request(
        STORE["url"].rstrip("/") + "/o/" + name,
        data=body,
        method="PUT" if body is not None else "GET",
        headers={"X-Key": STORE["key"], "User-Agent": "Collider-Argon-6420/1.0"},
    )
    return urllib.request.urlopen(r, timeout=120).read()


def _pack(folder):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        t.add(
            folder,
            arcname=".",
            filter=lambda i: None if any(p in SKIP for p in i.name.split("/")) or i.name.endswith(".log") else i,
        )
    return buf.getvalue()


os.makedirs(DATA, exist_ok=True)
os.makedirs(WEB, exist_ok=True)
for name, folder in ((DATA_ARCHIVE, DATA), (WEB_ARCHIVE, WEB)):
    try:
        with tarfile.open(fileobj=io.BytesIO(_req(name)), mode="r:gz") as t:
            t.extractall(folder, filter="data")
        print(name, "restored", flush=True)
    except Exception as e:
        print(name, "not restored:", str(e)[:200], flush=True)

sys.path.insert(0, os.path.join(APP, "tools"))
import collider_config as ccfg  # noqa: E402
import collider_server as cs  # noqa: E402

cfg = ccfg.load(DATA)
cs.setup(APP, WEB, DATA, PORT, cfg)
server = ThreadingHTTPServer(("0.0.0.0", PORT), cs.Handler)


def state():
    out = []
    for d, dirs, files in os.walk(DATA):
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".")]
        for f in files:
            if f in SKIP or f.endswith(".log"):
                continue
            p = os.path.join(d, f)
            try:
                st = os.stat(p)
                out.append((p, st.st_size, int(st.st_mtime)))
            except OSError:
                pass
    return sorted(out)


def keep():
    """Writes ARGON 6420 data back to R2 (argon6420_data.tar.gz) within a minute of any change."""
    last = state()
    while True:
        time.sleep(60)
        now = state()
        if now == last:
            continue
        try:
            _req(DATA_ARCHIVE, _pack(DATA))
            last = now
            print("argon6420 data kept", flush=True)
        except Exception as e:
            print("argon6420 data not kept yet:", str(e)[:200], flush=True)


threading.Thread(target=keep, daemon=True).start()
print("Collider ARGON 6420 online on", PORT, flush=True)
server.serve_forever()

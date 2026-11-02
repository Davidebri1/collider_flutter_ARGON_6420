# Made by Claude (2026-10-23). Collider online: the same server Collider.exe runs, reachable from anywhere at one address.
# David, 23 Oct: "we arent going to run anything off my pc ... host online" and "make sure that the app is always
# accessible". The host's own disk is emptied whenever it restarts, so what must last is kept on David's Cloudflare
# R2 (bucket collider-data, through the collider-store Worker; its address and key are in store.json beside this
# file, in the private repository):
#  - data.tar.gz: the configuration with the providers and keys, history, Files, made pictures. Read at start, written
#    back within a minute of any change, so a restart loses nothing;
#  - web.tar.gz: the app's web build, put there by dev/deploy_online.py.
# The unchanging phone link (collider-phone Worker) is pointed here at start.
import io, json, os, sys, tarfile, threading, time, urllib.request
from http.server import ThreadingHTTPServer

APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP, "data")
WEB = os.path.join(APP, "build", "web")
STORE = json.load(open(os.path.join(APP, "store.json")))
PORT = int(os.environ.get("PORT") or 7860)
SKIP = ("window", "window-browser", "collider_app.log", ".cache")


def _req(name, body=None):
    r = urllib.request.Request(STORE["url"].rstrip("/") + "/o/" + name, data=body, method="PUT" if body is not None else "GET",
                               headers={"X-Key": STORE["key"], "User-Agent": "Collider/1.0"})
    return urllib.request.urlopen(r, timeout=120).read()


def _pack(folder):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        t.add(folder, arcname=".", filter=lambda i: None if any(p in SKIP for p in i.name.split("/")) or i.name.endswith(".log") else i)
    return buf.getvalue()


os.makedirs(DATA, exist_ok=True)
os.makedirs(WEB, exist_ok=True)
for name, folder in (("data.tar.gz", DATA), ("web.tar.gz", WEB)):
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


def announce():
    """Points the phone link at this server."""
    here = os.environ.get("RENDER_EXTERNAL_URL") or ("https://" + os.environ["SPACE_HOST"] if os.environ.get("SPACE_HOST") else "")
    relay = next((r for r in cs.rows() if ccfg.is_phone(r)), None)
    if not here or not relay:
        return
    for _ in range(10):
        try:
            req = urllib.request.Request(relay["endpoint"].rstrip("/") + "/set", data=json.dumps({"url": here.rstrip("/")}).encode(),
                                         headers={"Content-Type": "application/json", "Authorization": "Key " + relay["key"].strip(),
                                                  "User-Agent": "Collider/1.0"})
            print("phone link:", urllib.request.urlopen(req, timeout=20).read()[:80], flush=True)
            return
        except Exception as e:
            print("phone link not set yet:", str(e)[:120], flush=True)
            time.sleep(10)


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
    """Writes the data back to R2 within a minute of any change."""
    last = state()
    while True:
        time.sleep(60)
        now = state()
        if now == last:
            continue
        try:
            _req("data.tar.gz", _pack(DATA))
            last = now
            print("data kept", flush=True)
        except Exception as e:
            print("data not kept yet:", str(e)[:200], flush=True)


threading.Thread(target=announce, daemon=True).start()
threading.Thread(target=keep, daemon=True).start()
print("Collider online on", PORT, flush=True)
server.serve_forever()

# Made by Claude (2026-10-23). Puts what Collider online reads into David's Cloudflare R2 (bucket collider-data, through
# the collider-store Worker): --web the app's web build (after every build), --data this PC's data folder (once, to start
# the online copy from it; after that the online server keeps its own). Usage: python dev\deploy_online.py --web [--data]
import io, json, os, sys, tarfile, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = json.load(open(os.path.join(ROOT, "dev", "space", "store.json")))
SKIP = ("window", "window-browser", ".cache", "desktop.ini")


def pack(folder):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        t.add(folder, arcname=".", filter=lambda i: None if any(p in SKIP for p in i.name.split("/")) or i.name.endswith(".log")
              or "collider_config.before_" in i.name else i)
    return buf.getvalue()


def put(name, body):
    r = urllib.request.Request(STORE["url"].rstrip("/") + "/o/" + name, data=body, method="PUT",
                               headers={"X-Key": STORE["key"], "User-Agent": "Collider/1.0"})
    print(name, len(body) // 1024, "KB", urllib.request.urlopen(r, timeout=300).read().decode())


if "--web" in sys.argv:
    put("web.tar.gz", pack(os.path.join(ROOT, "build", "web")))
if "--data" in sys.argv:
    put("data.tar.gz", pack(os.path.join(ROOT, "data")))

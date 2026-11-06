# Uploads Collider ARGON 6420's web build (argon6420_web.tar.gz) and data folder (argon6420_data.tar.gz)
# into Cloudflare R2 via collider-store Worker, completely isolated from other projects.
import io, json, os, sys, tarfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = json.load(open(os.path.join(ROOT, "dev", "space", "store.json")))
SKIP = ("window", "window-browser", ".cache", "desktop.ini")


def pack(folder):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        t.add(
            folder,
            arcname=".",
            filter=lambda i: None
            if any(p in SKIP for p in i.name.split("/"))
            or i.name.endswith(".log")
            or "collider_config.before_" in i.name
            else i,
        )
    return buf.getvalue()


def put(name, body):
    r = urllib.request.Request(
        STORE["url"].rstrip("/") + "/o/" + name,
        data=body,
        method="PUT",
        headers={"X-Key": STORE["key"], "User-Agent": "Collider-Argon-6420/1.0"},
    )
    print(name, len(body) // 1024, "KB", urllib.request.urlopen(r, timeout=300).read().decode())


if "--web" in sys.argv:
    put("argon6420_web.tar.gz", pack(os.path.join(ROOT, "build", "web")))
if "--data" in sys.argv:
    put("argon6420_data.tar.gz", pack(os.path.join(ROOT, "data")))

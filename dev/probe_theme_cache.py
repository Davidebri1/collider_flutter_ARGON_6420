# Made by Claude (2026-10-21). The theme files through collider-media: kept for a year, byte ranges for video, CORS.
import json, time, urllib.request, urllib.parse
UA = {"User-Agent": "Collider/1.0", "Origin": "https://example.trycloudflare.com"}
items = json.loads(urllib.request.urlopen(urllib.request.Request("https://collider-themes.ebridavid.workers.dev/", headers=UA), timeout=30).read())
M = "https://collider-media.ebridavid.workers.dev/"
for kind in ("image", "video", "audio"):
    t = next(i for i in items if i.get("kind") == kind)
    u = M + urllib.parse.quote(t["name"])
    t0 = time.time()
    r = urllib.request.urlopen(urllib.request.Request(u, headers={**UA, "Range": "bytes=0-1023"}), timeout=60)
    print(kind, r.status, r.headers.get("Content-Range"), "|", r.headers.get("Cache-Control"), "|",
          r.headers.get("Access-Control-Allow-Origin"), "|", r.headers.get("Content-Type"), f"{time.time() - t0:.2f}s")
    t0 = time.time()
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120)
    n = len(r.read())
    print("   whole", r.status, n == t["size"], f"{time.time() - t0:.2f}s")

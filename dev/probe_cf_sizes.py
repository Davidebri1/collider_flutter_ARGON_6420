# Made by Claude (2026-10-23). Which picture sizes Cloudflare's FLUX.2 klein makes: 2K and 4K in the phone's shape.
import json, os, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import collider_config as ccfg
cfg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "collider_config.json"), encoding="utf-8"))
row = next(r for r in cfg["providers"] if ccfg.is_pictures(r))
for w, h in [(int(a), int(b)) for a, b in (s.split("x") for s in (sys.argv[1:] or ["1440x2560", "2160x3840"]))]:
    body = {"model": "@cf/black-forest-labs/flux-2-klein-4b", "prompt": "a lighthouse at dusk, photograph", "width": w, "height": h, "seed": 7}
    req = urllib.request.Request(row["endpoint"], data=json.dumps(body).encode(), headers={
        "Content-Type": "application/json", "Authorization": "Key " + row["key"].strip(), "User-Agent": "Collider/1.0"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            data = r.read()
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(data))
        print(f"{w}x{h}: made {im.size[0]}x{im.size[1]}, {len(data)//1024} KB, {time.time()-t:.0f}s")
    except urllib.error.HTTPError as e:
        print(f"{w}x{h}: {e.code} {e.read()[:300]}")

# Made by Claude (2026-10-21). Why the picture Worker answered 502: one request, printing the Worker's own words.
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import collider_config as ccfg
cfg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "collider_config.json"), encoding="utf-8"))
row = next(r for r in cfg["providers"] if ccfg.is_pictures(r))
for model in ["@cf/black-forest-labs/flux-2-klein-4b", "@cf/black-forest-labs/flux-1-schnell"]:
    body = {"model": model, "prompt": "a lighthouse at dusk", "width": 768, "height": 1344, "seed": 7, "references": []}
    req = urllib.request.Request(row["endpoint"], data=json.dumps(body).encode(), headers={
        "Content-Type": "application/json", "Authorization": "Key " + row["key"].strip(), "User-Agent": "Collider/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            print(model, r.status, r.headers.get("Content-Type"), len(r.read()))
    except urllib.error.HTTPError as e:
        print(model, e.code, e.read()[:400])

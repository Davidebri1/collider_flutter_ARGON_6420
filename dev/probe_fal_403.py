# Made by Claude (2026-10-21). What fal says when it refuses; the key is never printed.
import sys, os, json, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import collider_config as ccfg
key = ccfg._fal_rows(open(ccfg.KEYS_FILE, encoding="utf-8", errors="ignore").read())[0]["key"]
for url, body in (("https://queue.fal.run/xai/grok-imagine-image/v2.0/text-to-image", {"prompt": "a lighthouse", "num_images": 1}),
                  ("https://queue.fal.run/fal-ai/flux/schnell", {"prompt": "a lighthouse"})):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Key " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(url.split("run/")[1], r.status, r.read()[:300])
    except urllib.error.HTTPError as e:
        print(url.split("run/")[1], e.code, e.read()[:400])

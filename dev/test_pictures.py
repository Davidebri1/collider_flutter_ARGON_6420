# Made by Claude (2026-10-21). One picture from Cloudflare (FLUX.2 klein 4B, 1080x1920) and one from NVIDIA (FLUX.1 dev,
# its largest size) with the same words, saved to dev/editor/test_out. Prints no key.
import base64, json, os, sys, time, urllib.request, urllib.error
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "tools"))
import collider_config as ccfg
cfg = ccfg.load(os.path.join(here, "..", "data"))
WORDS = "a lighthouse on a cliff at dusk, warm light in its window, calm sea, cinematic, sharp detail"
out = os.path.join(here, "editor", "test_out")


def post(url, body, headers, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "User-Agent": "Collider/1.0", **headers})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), r.headers.get("Content-Type", ""), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, e.read(), "", time.time() - t


cf = next(r for r in cfg["providers"] if "collider-imagine" in r.get("endpoint", ""))
for model, w, h in (("@cf/black-forest-labs/flux-2-klein-4b", 1080, 1920), ("@cf/black-forest-labs/flux-2-dev", 1080, 1920)):
    code, data, ctype, secs = post(cf["endpoint"], {"model": model, "prompt": WORDS, "width": w, "height": h}, {"Authorization": "Key " + cf["key"]})
    name = "pic_cf_" + model.split("/")[-1] + (".jpg" if "jpeg" in ctype else ".png")
    if code == 200:
        open(os.path.join(out, name), "wb").write(data)
    print("cloudflare", model, code, f"{secs:.1f}s", len(data), ctype, data[:160] if code != 200 else "")

nv = next(r for r in cfg["providers"] if "nvidia" in (r.get("endpoint") or "") and r.get("key"))
for w, h in ((768, 1344), (1024, 1024)):
    code, data, ctype, secs = post("https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev",
                                   {"prompt": WORDS, "mode": "base", "cfg_scale": 3.5, "width": w, "height": h, "seed": 0, "steps": 50},
                                   {"Authorization": "Bearer " + nv["key"], "Accept": "application/json"})
    if code == 200:
        art = (json.loads(data).get("artifacts") or [{}])[0]
        img = base64.b64decode(art.get("base64", ""))
        open(os.path.join(out, f"pic_nv_flux1dev_{w}x{h}.jpg"), "wb").write(img)
        print("nvidia flux.1-dev", w, h, code, f"{secs:.1f}s", len(img), art.get("finishReason"))
    else:
        print("nvidia flux.1-dev", w, h, code, f"{secs:.1f}s", data[:200])

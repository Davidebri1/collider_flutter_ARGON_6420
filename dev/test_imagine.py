# Made by Claude (2026-10-21). Pictures through the server: the default order (Cloudflare first), then NVIDIA by name.
import json, sys, time, urllib.request
base = f"http://127.0.0.1:{sys.argv[1]}"
print("models", [m["id"] for m in json.load(urllib.request.urlopen(base + "/api/imagine"))["models"]])
ids = []
for body in ({"text": "a red fox asleep in fresh snow, morning light", "kind": "image", "count": 2},
             {"text": "a red fox asleep in fresh snow, morning light", "kind": "image", "count": 1, "model": "NVIDIA:black-forest-labs/flux.1-dev"}):
    req = urllib.request.Request(base + "/api/imagine", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    ids.append(json.load(urllib.request.urlopen(req))["id"])
t = time.time()
while time.time() - t < 150:
    items = {i["id"]: i for i in json.load(urllib.request.urlopen(base + "/api/imagine"))["items"]}
    if all(items[i]["status"] != "making" for i in ids):
        break
    time.sleep(3)
for i in ids:
    it = items[i]
    print(it["status"], it.get("label"), it.get("error"), [(m["name"], m["width"], m["height"]) for m in it["media"]], f"{time.time() - t:.0f}s")
files = json.load(urllib.request.urlopen(base + "/api/files"))["generated"]
print("in Files:", [(f["name"], f["model"]) for f in files if "fox" in f["name"].lower()])

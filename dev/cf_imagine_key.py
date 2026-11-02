# Made by Claude (2026-10-21). Gives the Cloudflare picture Worker its key and puts the matching provider row into the
# configuration beside Collider.exe (and the test copy's). The key is never printed.
import json, os, secrets, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
ENDPOINT = "https://collider-imagine.ebridavid.workers.dev"
MODELS = "@cf/black-forest-labs/flux-2-klein-4b, @cf/black-forest-labs/flux-2-dev, @cf/black-forest-labs/flux-1-schnell"

cfgp = os.path.join(root, "data", "collider_config.json")
cfg = json.load(open(cfgp, encoding="utf-8"))
row = next((r for r in cfg["providers"] if ENDPOINT in (r.get("endpoint") or "")), None)
key = row["key"] if row and row.get("key") else secrets.token_urlsafe(32)
p = subprocess.run("npx -y wrangler@4 secret put COLLIDER_KEY", input=key.encode(), shell=True, capture_output=True,
                   cwd=os.path.join(here, "cf_imagine"))
print("secret put:", p.returncode, b"Success" in p.stdout + p.stderr)
for path in (cfgp, os.path.join(here, "test_app", "data", "collider_config.json")):
    if not os.path.exists(path):
        continue
    c = json.load(open(path, encoding="utf-8"))
    c["providers"] = [r for r in c["providers"] if ENDPOINT not in (r.get("endpoint") or "")]
    c["providers"].append({"name": "Cloudflare", "endpoint": ENDPOINT, "key": key, "models": MODELS})
    tmp = path + ".tmp"
    json.dump(c, open(tmp, "w", encoding="utf-8"), indent=2)
    os.replace(tmp, path)
    print("row in", os.path.relpath(path, root))

# Made by Claude (2026-10-23). Sets up Collider online's storage on Cloudflare: deploys the collider-store Worker (R2
# bucket collider-data) and gives it its key. The key is made here once, kept in dev/space/store.json (the repository is
# private) and never printed.
import json, os, secrets, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CF = os.path.join(ROOT, "dev", "cf_store")
P = os.path.join(ROOT, "dev", "space", "store.json")
if not os.path.exists(P):
    json.dump({"url": "https://collider-store.ebridavid.workers.dev", "key": secrets.token_urlsafe(32)}, open(P, "w"), indent=1)
key = json.load(open(P))["key"]
npx = "npx.cmd" if os.name == "nt" else "npx"
r = subprocess.run([npx, "--yes", "wrangler", "deploy"], cwd=CF, capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
print("deploy", r.returncode, (r.stdout + r.stderr)[-300:])
r = subprocess.run([npx, "--yes", "wrangler", "secret", "put", "STORE_KEY"], cwd=CF, input=key, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("secret", r.returncode, (r.stdout + r.stderr).replace(key, "***")[-300:])

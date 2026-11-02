# Made by Claude (2026-10-21). Gives the phone-link Worker its key, deploys it, and puts the matching Phone row into
# the configuration beside Collider.exe (and the phone copy's). The key is never printed.
import json, os, secrets, subprocess
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
ENDPOINT = "https://collider-phone.ebridavid.workers.dev"
cfgp = os.path.join(root, "data", "collider_config.json")
cfg = json.load(open(cfgp, encoding="utf-8"))
row = next((r for r in cfg["providers"] if ENDPOINT in (r.get("endpoint") or "")), None)
key = row["key"] if row and row.get("key") else secrets.token_urlsafe(18)
w = os.path.join(here, "cf_phone")
d = subprocess.run("npx -y wrangler@4 deploy", shell=True, capture_output=True, cwd=w)
print("deploy:", d.returncode, b"collider-phone.ebridavid.workers.dev" in d.stdout + d.stderr)
p = subprocess.run("npx -y wrangler@4 secret put PHONE_KEY", input=key.encode(), shell=True, capture_output=True, cwd=w)
print("secret put:", p.returncode, b"Success" in p.stdout + p.stderr)
for path in (cfgp, os.path.join(here, "phone_app", "data", "collider_config.json")):
    if not os.path.exists(path):
        continue
    c = json.load(open(path, encoding="utf-8"))
    c["providers"] = [r for r in c["providers"] if ENDPOINT not in (r.get("endpoint") or "")]
    c["providers"].append({"name": "Phone", "endpoint": ENDPOINT, "key": key, "models": ""})
    tmp = path + ".tmp"
    json.dump(c, open(tmp, "w", encoding="utf-8"), indent=2)
    os.replace(tmp, path)
    print("row in", os.path.relpath(path, root))

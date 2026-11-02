# Made by Claude (2026-10-21). Where the keys file and keys.json mention Cloudflare. Secrets are masked.
import json, os, re
d = r"C:\Users\D\Documents\00_Config_and_Secrets"
mask = lambda s: re.sub(r"[A-Za-z0-9_\-]{12,}", lambda m: m.group(0)[:4] + "…(" + str(len(m.group(0))) + ")", s)
lines = open(os.path.join(d, "API KEYS.txt"), encoding="utf-8", errors="ignore").read().splitlines()
for i, l in enumerate(lines):
    if re.search(r"cloudflare|workers|cf[_ ]|account", l, re.I):
        for j in range(max(0, i - 1), min(len(lines), i + 3)):
            print(j, mask(lines[j])[:160])
        print("--")
try:
    k = json.load(open(os.path.join(d, "keys.json"), encoding="utf-8"))
    def walk(o, path=""):
        if isinstance(o, dict):
            for a, b in o.items():
                walk(b, path + "/" + a)
        elif isinstance(o, list):
            for i, b in enumerate(o):
                walk(b, f"{path}[{i}]")
        elif re.search(r"cloudflare|cf|account|worker", path, re.I):
            print("keys.json", path, mask(str(o))[:80])
    walk(k)
except Exception as e:
    print("keys.json", e)

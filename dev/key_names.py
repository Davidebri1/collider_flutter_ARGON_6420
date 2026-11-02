# Made by Claude (2026-10-20). Lists which providers have a key, by name only; never prints a key.
import json, os, re
folder = r"C:\Users\D\Documents\00_Config_and_Secrets"
try:
    print("keys.json:", sorted(json.load(open(os.path.join(folder, "keys.json"), encoding="utf-8")).keys()))
except Exception as e:
    print("keys.json:", type(e).__name__)
try:
    names = []
    for line in open(os.path.join(folder, "API KEYS.txt"), encoding="utf-8", errors="ignore"):
        m = re.match(r"\s*([A-Za-z][A-Za-z0-9 _\-]{1,40}?)\s*[:=]", line)
        if m:
            names.append(m.group(1).strip())
    print("API KEYS.txt:", sorted(set(names)))
except Exception as e:
    print("API KEYS.txt:", type(e).__name__)

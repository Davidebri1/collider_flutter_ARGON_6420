# Made by Claude (2026-10-20). Is there a fal.ai key on this computer? Prints where and its shape only, never the key.
import os, re
paths = [r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt", r"C:\Users\D\Documents\00_Config_and_Secrets\keys.json"]
for p in paths:
    try:
        t = open(p, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        print(p, type(e).__name__)
        continue
    for i, line in enumerate(t.splitlines()):
        if re.search(r"\bfal\b|fal\.ai|fal_key|FAL", line, re.I):
            label = re.split(r"[:=]", line)[0][:40]
            print(os.path.basename(p), "line", i + 1, "label:", label.strip())
    # fal keys look like <uuid>:<hex>
    n = len(re.findall(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:[0-9a-f]{32}\b", t))
    print(os.path.basename(p), "fal-shaped keys:", n)

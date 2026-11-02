# Made by Claude (2026-10-20). Asks fal which models it offers for pictures and video (no generation, no cost).
# Prints model ids and names only; never the key.
import json, re, sys, urllib.parse, urllib.request
t = open(r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt", encoding="utf-8", errors="ignore").read()
key = re.findall(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:[0-9a-f]{32}\b", t)[0]


def get(url):
    req = urllib.request.Request(url, headers={"Authorization": "Key " + key, "User-Agent": "Collider/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())


for cat in sys.argv[1:] or ["text-to-image", "text-to-video", "image-to-video", "image-to-image"]:
    try:
        d = get("https://api.fal.ai/v1/models?" + urllib.parse.urlencode({"category": cat, "limit": 40, "status": "active"}))
        ms = d.get("models") or d.get("items") or d
        print("==", cat, len(ms))
        for m in ms[:40]:
            meta = m.get("metadata") or {}
            print(" ", m.get("endpoint_id"), "|", meta.get("display_name"), "|", meta.get("date") or meta.get("updated_at") or "", "|", (meta.get("tags") or [])[:3])
    except urllib.error.HTTPError as e:
        print(cat, "HTTP", e.code, e.read()[:200])
    except Exception as e:
        print(cat, "ERR", e)

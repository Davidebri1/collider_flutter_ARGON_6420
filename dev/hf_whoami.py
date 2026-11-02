# Made by Claude (2026-10-23). Finds a Hugging Face token in David's keys file and asks Hugging Face whose it is and
# whether it may write. Never prints the token.
import json, re, urllib.request
p = r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt"
text = open(p, encoding="utf-8", errors="ignore").read()
toks = list(dict.fromkeys(re.findall(r"\bhf_[A-Za-z0-9]{30,}\b", text)))
print("tokens found:", len(toks))
for i, t in enumerate(toks):
    try:
        r = urllib.request.urlopen(urllib.request.Request("https://huggingface.co/api/whoami-v2",
                                                          headers={"Authorization": "Bearer " + t}), timeout=20)
        j = json.loads(r.read())
        auth = j.get("auth", {}).get("accessToken", {})
        print(i, j.get("name"), auth.get("role"), auth.get("fineGrained", {}).get("scoped", "")[:1] if auth.get("fineGrained") else "")
    except Exception as e:
        print(i, "error", str(e)[:80])

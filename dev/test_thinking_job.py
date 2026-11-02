# Made by Claude (2026-10-21). A real question through the test copy with thinking on: answers, lines and the
# consensus must come back with no thinking in them.
import json, sys, time, urllib.request
port = sys.argv[1]
base = f"http://127.0.0.1:{port}"
body = {"line": 28, "prompt": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much is the ball?",
        "attachments": [], "models": ["google/gemma-4-31b-it", "openai/gpt-oss-20b", "z-ai/glm-5.3", "meta/muse-glimmer-30b",
                                      "nvidia/nemotron-3.5-lightning-30b-a3b"], "mode": "chat", "autosave": False, "incognito": True}
req = urllib.request.Request(base + "/api/ask", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
jid = json.load(urllib.request.urlopen(req))["id"]
t = time.time()
while time.time() - t < 240:
    j = json.load(urllib.request.urlopen(f"{base}/api/job/{jid}"))
    if j.get("status") in ("done", "error"):
        break
    time.sleep(3)
print("status", j.get("status"), "stage", j.get("stage"), f"{time.time() - t:.0f}s")
bad = ("we need", "let's", "the user", "thinking", "<think", "first, ", "okay,")
for m, r in (j.get("results") or {}).items():
    text = r.get("text") or ""
    print(f"{m:40s} {r.get('status'):8s} line={r.get('line')!r}  leak={any(b in text.lower()[:200] for b in bad)}  start={text[:80]!r}")
c = j.get("consensus") or {}
print("consensus", c.get("status"), "|", (c.get("summary") or "")[:120])

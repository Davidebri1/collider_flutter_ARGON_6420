# Made by Claude (2026-10-21). Which models think, and how they are asked to. Prints no key.
# For each model: a plain request, then one asking for thinking (chat_template_kwargs). Reports whether reasoning
# came back (and where), how long the answer is, and the time.
import json, os, sys, time, urllib.request, urllib.error, concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import collider_config as ccfg

here = os.path.dirname(os.path.abspath(__file__))
cfg = ccfg.load(os.path.join(here, "..", "data"))
key = next(r["key"] for r in cfg["providers"] if "nvidia" in (r.get("endpoint") or "") and r.get("key"))
Q = "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much is the ball? Answer in one sentence."


def ask(model, extra):
    body = {"model": model, "messages": [{"role": "user", "content": Q}], "max_tokens": 4000, "temperature": 0.6, **extra}
    req = urllib.request.Request(ccfg.NVIDIA_CHAT, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            m = json.load(r)["choices"][0]["message"]
        c = m.get("content") or ""
        rc = m.get("reasoning_content") or m.get("reasoning") or ""
        return f"{time.time() - t:5.1f}s reasoning_field={len(rc):5d} think_tags={'<think>' in c} answer={c.split('</think>')[-1].strip()[:70]!r}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code} {e.read()[:120]!r}"
    except Exception as e:
        return f"error {str(e)[:80]}"


models = [m["id"] for m in cfg["models"]]
asks = [("plain", {}), ("kwargs", {"chat_template_kwargs": {"enable_thinking": True, "thinking": True}})]
with cf.ThreadPoolExecutor(8) as pool:
    jobs = {(m, n): pool.submit(ask, m, x) for m in models for n, x in asks}
    for (m, n), f in jobs.items():
        print(f"{m:45s} {n:7s} {f.result()}")

# Made by Claude (2026-10-23). Checks the online configuration page: the server serves /config with every agent's
# instruction in it, Smart Gen's included. Runs on a copy of the data folder, so nothing of David's changes.
import json, os, shutil, sys, threading, urllib.request
from http.server import ThreadingHTTPServer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "dev", "online_test", "data_cfg")
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)
shutil.copy(os.path.join(ROOT, "data", "collider_config.json"), TMP)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import collider_config as ccfg, collider_server as cs  # noqa
cfg = ccfg.load(TMP)
cs.setup(ROOT, os.path.join(ROOT, "build", "web"), TMP, 47993, cfg)
srv = ThreadingHTTPServer(("127.0.0.1", 47993), cs.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
html = urllib.request.urlopen("http://127.0.0.1:47993/config", timeout=20).read().decode()
for w in ("Consensus agent instruction", "One-line agent instruction", "Smart Gen agent instruction", "/api/config"):
    print(w, w in html)
r = urllib.request.Request("http://127.0.0.1:47993/api/config", method="POST", headers={"Content-Type": "application/json"},
                           data=json.dumps({"providers": cfg["providers"], "themes": cfg.get("themes", ""), "bypass": True,
                                            "settings": {"smartgen_prompt": cs.SMARTGEN_PROMPT + " "}}).encode())
print("save", urllib.request.urlopen(r, timeout=20).read().decode(), "applied", cs.SMARTGEN_PROMPT.endswith(" "))
srv.shutdown()

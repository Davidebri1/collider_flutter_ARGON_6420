# Made by Claude (2026-10-21). Checks the fal wiring without printing any key.
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import collider_config as ccfg
import collider_server as srv

text = open(ccfg.KEYS_FILE, encoding="utf-8", errors="ignore").read() if os.path.exists(ccfg.KEYS_FILE) else ""
fal = ccfg._fal_rows(text)
print("fal keys found in keys file:", len(fal))
tmp = tempfile.mkdtemp()
cfg = ccfg._first_run()
srv.setup(srv.ROOT, srv.WEB, tmp, 0, cfg)
print("fal rows in server:", len([r for r in srv.rows() if ccfg.is_fal(r)]))
print("imagine lines:", json.dumps(cfg.get("imagine")))
print("uses:", [srv.uses(r) for r in cfg["providers"] if ccfg.is_fal(r)][:1])
print("roster has no fal:", not any(m.get("via") == "fal" for m in srv.ROSTER))
print("listing:", srv.IMAGINE.listing())

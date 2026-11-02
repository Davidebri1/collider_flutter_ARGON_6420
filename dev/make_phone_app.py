# Made by Claude (2026-10-21). The copy David opens on his phone: dev\phone_app, the same as the test copy but on a
# fixed host number (47801) and with the tunnel program, and never restarted by Claude's tests (those use dev\test_app).
import os, shutil
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "make_test_app.py"), encoding="utf-8").read()
src = src.replace('os.path.join(here, "test_app")', 'os.path.join(here, "phone_app")').replace('cfg["host"] = None', 'cfg["host"] = 47801')
assert 'phone_app' in src and '47801' in src
exec(compile(src, "make_test_app.py (phone)", "exec"), {"__file__": os.path.join(here, "make_test_app.py"), "__name__": "__main__"})
os.makedirs(os.path.join(here, "phone_app", "bin"), exist_ok=True)
try:  # a hard link to the one cloudflared.exe, not a 53 MB copy (Claude, 2026-10-21)
    os.link(os.path.join(here, "..", "bin", "cloudflared.exe"), os.path.join(here, "phone_app", "bin", "cloudflared.exe"))
except OSError:
    shutil.copy(os.path.join(here, "..", "bin", "cloudflared.exe"), os.path.join(here, "phone_app", "bin", "cloudflared.exe"))
print("phone copy ready")

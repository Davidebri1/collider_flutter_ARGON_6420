# Made by Claude (2026-10-23). Round 23: the server also runs on Linux (Collider online): Chromium where Edge is not.
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
p = ROOT / "tools" / "collider_files.py"
s = p.read_text(encoding="utf-8")
old = 'edge = shutil.which("msedge") or next('
new = 'edge = shutil.which("msedge") or shutil.which("chromium") or shutil.which("chromium-browser") or next('
assert s.count(old) == 2, s.count(old)
s = s.replace(old, new)
old2 = '[edge, "--headless=new", "--disable-gpu",'
new2 = '[edge, *_SANDBOX, "--headless=new", "--disable-gpu",'
assert s.count(old2) == 2, s.count(old2)
s = s.replace(old2, new2)
anchor = "_render_gate = threading.Semaphore(2)\n"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + "# Chromium in a Linux container (Collider online) runs without its sandbox (Claude, 2026-10-23).\n"
              "_SANDBOX = [] if os.name == \"nt\" else [\"--no-sandbox\", \"--disable-dev-shm-usage\"]\n")
# print_pdf runs before _SANDBOX is defined in the file, but only when called, after the module has loaded: fine.
p.write_text(s, encoding="utf-8")
print("edited", p)

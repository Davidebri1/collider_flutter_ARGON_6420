# Made by Claude (2026-10-21). Round 11: the launch window in Apple's grouped-settings layout (style only; every line
# and what it does stays as it was).
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
p = ROOT / "tools" / "collider_app.py"
s = p.read_text(encoding="utf-8")
a = s.index("<style>")
z = s.index("</style>") + len("</style>")
new = (ROOT / "dev" / "draft" / "launch_style.css").read_text(encoding="utf-8").strip()
s = s[:a] + new + s[z:]
p.write_text(s, encoding="utf-8")
print("edited tools/collider_app.py")

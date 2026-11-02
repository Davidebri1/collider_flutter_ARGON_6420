# Made by Claude (2026-10-20). A throwaway copy of the app in dev\test_app with sample files, so Files can be checked
# without putting anything into David's own Files. Never used by Collider.exe.
import json, os, shutil
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.dirname(here)
dst = os.path.join(here, "test_app")
shutil.rmtree(dst, ignore_errors=True)
shutil.copytree(os.path.join(src, "tools"), os.path.join(dst, "tools"), ignore=shutil.ignore_patterns("__pycache__"))
shutil.copytree(os.path.join(src, "build", "web"), os.path.join(dst, "build", "web"))
os.makedirs(os.path.join(dst, "data"), exist_ok=True)
cfg = json.load(open(os.path.join(src, "data", "collider_config.json"), encoding="utf-8"))
cfg["host"] = None  # a free port each time, never the app's own
json.dump(cfg, open(os.path.join(dst, "data", "collider_config.json"), "w", encoding="utf-8"), indent=1)
f = os.path.join(dst, "data", "files")
for s in ("uploaded", "generated", "downloaded"):
    os.makedirs(os.path.join(f, s), exist_ok=True)
gen = {
    "GLM 5.3 - launch plan.md": "# Launch plan\n",
    "Research - lantern history - Gemma 4 31B.md": "# Lanterns\n",
    "Nemotron 3 Ultra - pricing notes.md": "# Pricing\n",
    "Quarterly plan.docx": None,
}
for n, t in gen.items():
    p = os.path.join(f, "generated", n)
    if t is None:
        shutil.copy(os.path.join(here, "editor", "test_out", next(x for x in os.listdir(os.path.join(here, "editor", "test_out")) if x.endswith(".docx"))), p)
    else:
        open(p, "w", encoding="utf-8").write(t)
shutil.copy(os.path.join(src, "assets", "themes", "premium", "tracks", "track1_driftwood.mp3"), os.path.join(f, "generated", "Night drive.mp3"))
json.dump({"Quarterly plan.docx": "Documents", "Night drive.mp3": "Gemma 4 31B"}, open(os.path.join(f, ".models.json"), "w"))
up = os.path.join(f, "uploaded")
open(os.path.join(up, "budget.csv"), "w").write("a,b\n1,2\n")
open(os.path.join(up, "settings.json"), "w").write("{}")
open(os.path.join(up, "script.py"), "w").write("print(1)\n")
shutil.copy(os.path.join(src, "assets", "icons", "apps", "claude_app_discover.png"), os.path.join(up, "picture.png"))
pdf = next((x for x in os.listdir(os.path.join(here, "editor", "test_out")) if x.endswith(".pdf")), None)
if pdf:
    shutil.copy(os.path.join(here, "editor", "test_out", pdf), os.path.join(up, "report.pdf"))
shutil.copy(os.path.join(src, "assets", "themes", "premium", "aurora_drift.mp4"), os.path.join(up, "aurora.mp4"))
shutil.copy(os.path.join(src, "assets", "themes", "premium", "tracks", "track1_driftwood.mp3"), os.path.join(up, "driftwood.mp3"))
open(os.path.join(up, "notes.md"), "w").write("# Launch notes\n\n- Ship the editor\n- Colour icons\n\n| Item | Owner |\n|---|---|\n| Files | Claude |\n")
open(os.path.join(up, "page.html"), "w").write("<html><body style='font:20px Segoe UI;background:#eef'><h1>Hello page</h1><p>A web page in Files.</p></body></html>")
open(os.path.join(up, "logo.svg"), "w").write("<svg xmlns='http://www.w3.org/2000/svg' width='200' height='120'><rect width='200' height='120' rx='20' fill='#0091FF'/><circle cx='60' cy='60' r='30' fill='#FFD600'/></svg>")
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
for r in [["Month", "Sales", "Cost"], ["Jan", 120, 80], ["Feb", 140, 90], ["Mar", 180, 95]]:
    ws.append(r)
wb.save(os.path.join(up, "sales.xlsx"))
# a printable part: a ring with a hole, as a binary STL
import math, struct
tris = []
R, r, N, M = 30.0, 10.0, 48, 24
P = lambda i, j: ((R + r * math.cos(2 * math.pi * j / M)) * math.cos(2 * math.pi * i / N),
                  (R + r * math.cos(2 * math.pi * j / M)) * math.sin(2 * math.pi * i / N), r * math.sin(2 * math.pi * j / M))
for i in range(N):
    for j in range(M):
        a, b, c, d = P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)
        tris += [(a, b, c), (a, c, d)]
with open(os.path.join(up, "ring.stl"), "wb") as s:
    s.write(bytes(80) + struct.pack("<I", len(tris)))
    for t in tris:
        s.write(struct.pack("<3f", 0, 0, 0) + b"".join(struct.pack("<3f", *v) for v in t) + b"\0\0")
# a second name for the same exe on disk (a hard link), not a 43 MB copy (Claude, 2026-10-21)
try:
    os.link(os.path.join(src, "Collider.exe"), os.path.join(f, "downloaded", "Collider.exe"))
except OSError:
    shutil.copy(os.path.join(src, "Collider.exe"), os.path.join(f, "downloaded", "Collider.exe"))
open(os.path.join(f, "downloaded", "archive.zip"), "wb").write(b"PK\x05\x06" + bytes(18))
open(os.path.join(f, "downloaded", "deck.pptx"), "wb").write(b"PK")
print("ok", dst)

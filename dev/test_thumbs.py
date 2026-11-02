# Made by Claude (2026-10-20). Makes a preview of every sample file in dev\test_app and lays them out on one sheet.
import os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "tools"))
import collider_thumbs as ct
from PIL import Image, ImageDraw
files = os.path.join(here, "test_app", "data", "files")
t = ct.Thumbs(files)
cells = []
for src in ("uploaded", "generated", "downloaded"):
    for n in sorted(os.listdir(os.path.join(files, src))):
        p = os.path.join(files, src, n)
        if not os.path.isfile(p) or n.startswith("."):
            continue
        s = time.time()
        out = t.path_for(p)
        print(f"{n:45s} {'preview' if out else 'none':8s} {time.time() - s:5.1f}s")
        cells.append((n, out))
W = 200
sheet = Image.new("RGB", (W * 6, (len(cells) + 5) // 6 * (W + 30)), (40, 42, 50))
d = ImageDraw.Draw(sheet)
for k, (n, out) in enumerate(cells):
    x, y = k % 6 * W, k // 6 * (W + 30)
    if out:
        im = Image.open(out).convert("RGBA")
        im.thumbnail((W - 16, W - 16))
        sheet.paste(im, (x + (W - im.width) // 2, y + (W - im.height) // 2), im)
    d.text((x + 8, y + W + 6), n[:30], fill=(230, 230, 235))
sheet.save(os.path.join(here, "editor", "test_out", "thumbs_sheet.png"))
print("sheet saved")

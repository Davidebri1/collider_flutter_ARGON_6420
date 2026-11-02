# Made by Claude (2026-10-21). Sizes of the project's folders, two levels deep, largest first.
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def size(p):
    t = 0
    for d, _, fs in os.walk(p):
        for f in fs:
            try:
                t += os.path.getsize(os.path.join(d, f))
            except OSError:
                pass
    return t


rows = []
for a in os.listdir(root):
    pa = os.path.join(root, a)
    if os.path.isdir(pa):
        rows.append((size(pa), a))
        if a in ("dev", "build", "data"):
            for b in os.listdir(pa):
                pb = os.path.join(pa, b)
                rows.append((size(pb) if os.path.isdir(pb) else os.path.getsize(pb), a + "\\" + b))
    else:
        rows.append((os.path.getsize(pa), a))
print("TOTAL", round(sum(s for s, n in rows if "\\" not in n) / 2**20), "MB")
for s, n in sorted(rows, reverse=True)[:30]:
    print(f"{s / 2**20:8.0f} MB  {n}")

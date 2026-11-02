# Made by Claude (2026-10-21). The largest files ever stored in the project's git history, and the big parts of dev\editor and dev\exe.
import os, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
g = lambda *a: subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout
print(g("count-objects", "-vH"))
objs = g("rev-list", "--objects", "--all").splitlines()
names = {l.split(" ", 1)[0]: (l.split(" ", 1)[1] if " " in l else "") for l in objs}
info = subprocess.run(["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"], cwd=root,
                      input="\n".join(names), capture_output=True, text=True).stdout.splitlines()
blobs = sorted(((int(s), names[o]) for o, t, s in (l.split() for l in info) if t == "blob"), reverse=True)
by = {}
for s, n in blobs:
    by.setdefault(n, [0, 0])
    by[n][0] += s
    by[n][1] += 1
print("largest paths in history (all versions):")
for n, (s, c) in sorted(by.items(), key=lambda x: -x[1][0])[:15]:
    print(f"{s / 2**20:8.1f} MB  x{c}  {n}")


def size(p):
    return sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(p) for f in fs)


for top in ("dev\\editor", "dev\\exe", "data\\window"):
    print(top)
    for b in os.listdir(os.path.join(root, top)):
        p = os.path.join(root, top, b)
        s = size(p) if os.path.isdir(p) else os.path.getsize(p)
        if s > 5 * 2**20:
            print(f"   {s / 2**20:8.0f} MB  {b}")

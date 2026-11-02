# Made by Claude (2026-10-20). Collider.exe for this folder as one file: the web build inside, minus the renderers it
# never loads and debug symbols. Wallpapers, posters and songs stay in the Cloudflare bucket.
import os, shutil, subprocess, sys
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(W, "dev", ".venv-build", "Scripts", "python.exe")
X = os.path.join(W, "dev", "exe")
LOG = os.path.join(W, "dev", "exe_log.txt")
os.makedirs(X, exist_ok=True)
web = os.path.join(X, "web")
shutil.rmtree(web, ignore_errors=True)
skip = lambda d, names: [n for n in names if n == "webparagraph" or n.startswith(("skwasm", "wimp")) or n.endswith(".symbols")]
shutil.copytree(os.path.join(W, "build", "web"), web, ignore=skip)
ico = os.path.join(X, "collider.ico")
with open(LOG, "w", encoding="utf-8") as log:
    subprocess.run([PY, "-c", "import sys; from PIL import Image; Image.open(sys.argv[1]).convert('RGBA').save(sys.argv[2], "
                    "sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])",
                    os.path.join(W, "web", "icons", "Icon-512.png"), ico], stdout=log, stderr=log, stdin=subprocess.DEVNULL)
    code = subprocess.run([PY, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--name", "Collider", "--windowed",
                           "--icon", ico, "--paths", os.path.join(W, "tools"),
                           "--hidden-import", "collider_server", "--hidden-import", "collider_files", "--hidden-import", "collider_config", "--hidden-import", "collider_thumbs", "--hidden-import", "collider_imagine", "--hidden-import", "collider_tunnel", "--hidden-import", "segno",
                           "--add-data", f"{web};web", "--distpath", os.path.join(X, "dist"), "--workpath", os.path.join(X, "work"),
                           "--specpath", X, os.path.join(W, "tools", "collider_app.py")],
                          stdout=log, stderr=log, stdin=subprocess.DEVNULL, cwd=X).returncode
    out = os.path.join(X, "dist", "Collider.exe")
    if code == 0 and os.path.isfile(out):
        target = os.path.join(W, "Collider.exe")
        try:
            shutil.copy2(out, target)
        except PermissionError:
            # Collider is open: a running program can be moved aside though not written over; the open window keeps
            # running from its new place and the next start is the new build (Claude, 2026-10-21).
            aside = os.path.join(X, "replaced")
            os.makedirs(aside, exist_ok=True)
            import time
            os.replace(target, os.path.join(aside, time.strftime("Collider %Y%m%d-%H%M%S.exe")))
            shutil.copy2(out, target)
        log.write(f"EXE MB {os.path.getsize(os.path.join(W, 'Collider.exe')) / 1048576:.1f}\n")
    log.write(f"EXE_EXIT {code}\n")
print("EXE_EXIT", code)
sys.exit(code)

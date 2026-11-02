# Made by Claude (2026-10-23). Runs Collider online's start (dev/space/start.py) on this PC in a scratch folder, the way
# the host will: data and app fetched from Hugging Face. Then checks it answers, and stops it.
import os, re, shutil, subprocess, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stage = os.path.join(ROOT, "dev", "online_test")
shutil.rmtree(stage, ignore_errors=True)
os.makedirs(stage)
shutil.copytree(os.path.join(ROOT, "tools"), os.path.join(stage, "tools"), ignore=shutil.ignore_patterns("__pycache__"))
shutil.copy(os.path.join(ROOT, "dev", "space", "start.py"), stage)
token = re.findall(r"\bhf_[A-Za-z0-9]{30,}\b", open(r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt", encoding="utf-8", errors="ignore").read())[0]
env = {**os.environ, "HF_TOKEN": token, "PORT": "47999"}
log = open(os.path.join(stage, "log.txt"), "w")
p = subprocess.Popen([sys.executable, "start.py"], cwd=stage, env=env, stdout=log, stderr=log, stdin=subprocess.DEVNULL)
try:
    for _ in range(90):
        time.sleep(2)
        try:
            body = urllib.request.urlopen("http://127.0.0.1:47999/api/models", timeout=5).read()
            print("models answered:", len(body), "bytes")
            page = urllib.request.urlopen("http://127.0.0.1:47999/", timeout=5).read()
            print("app page:", len(page), "bytes", b"flutter" in page.lower())
            files = urllib.request.urlopen("http://127.0.0.1:47999/api/files", timeout=10).read()
            print("files listing:", len(files), "bytes")
            break
        except Exception:
            pass
finally:
    p.terminate()
    time.sleep(1)
    log.close()
    print(open(os.path.join(stage, "log.txt"), encoding="utf-8", errors="ignore").read()[-800:])

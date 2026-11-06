# Deploys Collider ARGON 6420 to a dedicated, permanent 24/7 Hugging Face Docker Space:
# https://zelljr-collider-argon-6420.hf.space/ (and /config)
import json, os, re, shutil, subprocess, tempfile, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPACE_NAME = "collider-argon-6420"


def hf_token():
    for p in (
        r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt",
        r"C:\Users\D\Documents\API KEYS.txt",
    ):
        if os.path.isfile(p):
            m = re.search(r"hf_[A-Za-z0-9]{20,}", open(p, encoding="utf-8", errors="ignore").read())
            if m:
                return m.group(0)
    raise RuntimeError("No Hugging Face token found")


def api(path, token, data=None, method=None):
    req = urllib.request.Request(
        "https://huggingface.co" + path,
        data=json.dumps(data).encode() if data is not None else None,
        method=method or ("POST" if data is not None else "GET"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


token = hf_token()
user = api("/api/whoami-v2", token)["name"]
repo = f"{user}/{SPACE_NAME}"
try:
    api(
        "/api/repos/create",
        token,
        {"type": "space", "name": SPACE_NAME, "sdk": "docker", "private": False},
    )
    print("Created Space:", repo)
except urllib.error.HTTPError as e:
    if e.code != 409:
        raise
    print("Updating existing Space:", repo)

stage = tempfile.mkdtemp(prefix="collider_argon6420_space_")
try:
    with open(os.path.join(stage, "README.md"), "w", encoding="utf-8") as f:
        f.write(
            "---\ntitle: Collider Argon 6420\nemoji: ⚡\ncolorFrom: gray\ncolorTo: blue\nsdk: docker\napp_port: 7860\n---\n"
        )
    shutil.copy2(os.path.join(ROOT, "dev", "space", "Dockerfile"), os.path.join(stage, "Dockerfile"))
    os.makedirs(os.path.join(stage, "dev", "space"), exist_ok=True)
    shutil.copy2(os.path.join(ROOT, "dev", "space", "start.py"), os.path.join(stage, "dev", "space", "start.py"))
    shutil.copy2(os.path.join(ROOT, "dev", "space", "store.json"), os.path.join(stage, "dev", "space", "store.json"))
    shutil.copytree(
        os.path.join(ROOT, "tools"),
        os.path.join(stage, "tools"),
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    for cmd in (
        ["git", "init", "-b", "main"],
        ["git", "config", "user.email", "collider@local"],
        ["git", "config", "user.name", "Collider"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", "Deploy Collider Argon 6420 online"],
        ["git", "push", "--force", f"https://{user}:{token}@huggingface.co/spaces/{repo}", "main"],
    ):
        subprocess.run(cmd, cwd=stage, check=True)
finally:
    shutil.rmtree(stage, ignore_errors=True)

host = f"https://{user.lower()}-{SPACE_NAME}.hf.space"
print("Permanent live URL:", host)
print("Permanent live Config URL:", host + "/config")

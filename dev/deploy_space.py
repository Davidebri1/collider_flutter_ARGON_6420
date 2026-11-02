# Made by Claude (2026-10-23). Puts Collider online: its data into a private Hugging Face dataset, and its server and
# app into a Hugging Face Space (free; built by Hugging Face from dev\space\Dockerfile). The token is read from David's
# keys file and never printed. Usage: python dev\deploy_space.py [--data] [--app]  (both when neither is given)
import os, re, shutil, sys
from huggingface_hub import HfApi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt"
token = re.findall(r"\bhf_[A-Za-z0-9]{30,}\b", open(KEYS, encoding="utf-8", errors="ignore").read())[0]
api = HfApi(token=token)
user = api.whoami()["name"]
DATA_REPO, SPACE = f"{user}/collider-data", f"{user}/collider"
which = set(sys.argv[1:]) or {"--data", "--app"}

if "--data" in which:
    api.create_repo(DATA_REPO, repo_type="dataset", private=True, exist_ok=True)
    api.upload_folder(folder_path=os.path.join(ROOT, "data"), repo_id=DATA_REPO, repo_type="dataset",
                      commit_message="Collider data, from the PC (Claude)",
                      ignore_patterns=["window/**", "window-browser/**", "*.log", "collider_config.before_*", ".cache/**"])
    print("data in", DATA_REPO)

if "--web" in which:  # the app's web build, read by Collider online at start (dev/space/start.py)
    WEB_REPO = f"{user}/collider-web"
    api.create_repo(WEB_REPO, repo_type="dataset", private=True, exist_ok=True)
    api.upload_folder(folder_path=os.path.join(ROOT, "build", "web"), repo_id=WEB_REPO, repo_type="dataset",
                      commit_message="Collider web build (Claude)", ignore_patterns=["desktop.ini"], delete_patterns=["*"])
    print("web in", WEB_REPO)

if "--app" in which:
    stage = os.path.join(ROOT, "dev", "space_stage")
    shutil.rmtree(stage, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "dev", "space"), stage)
    shutil.copytree(os.path.join(ROOT, "tools"), os.path.join(stage, "tools"), ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(os.path.join(ROOT, "build", "web"), os.path.join(stage, "web"), ignore=shutil.ignore_patterns("desktop.ini"))
    api.create_repo(SPACE, repo_type="space", space_sdk="docker", private=False, exist_ok=True)
    api.add_space_secret(SPACE, "HF_TOKEN", token)
    api.add_space_variable(SPACE, "COLLIDER_DATA_REPO", DATA_REPO)
    api.upload_folder(folder_path=stage, repo_id=SPACE, repo_type="space", commit_message="Collider online (Claude)")
    print("app in", SPACE, "->", f"https://{user.lower()}-collider.hf.space")

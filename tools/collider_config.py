"""Collider's configuration. Made by Claude (2026-10-17).

One file, data\\collider_config.json beside Collider.exe, holds everything the app needs before it can work:
the host number it last ran on, every provider with its address and key, and where the themes come from.
The launch window (collider_app.py) shows it and saves it; the server (collider_server.py) reads only this.
No environment variables, nothing hidden in code.

The first time, when there is no file yet, the keys are taken from David's keys file so nothing has to be typed.
"""
import json
import os
import re

KEYS_FILE = r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt"
NVIDIA_CHAT = "https://integrate.api.nvidia.com/v1/chat/completions"
TAVILY_SEARCH = "https://api.tavily.com/search"
# Voice chat: speech to text (Groq's Whisper). Added by Claude on 2026-10-20.
GROQ_SPEECH = "https://api.groq.com/openai/v1/audio/transcriptions"
SPEECH_MODEL = "whisper-large-v3-turbo"
# Discover Market: pictures and videos through fal's queue. Added by Claude on 2026-10-20.
FAL_QUEUE = "https://queue.fal.run"
THEMES = "https://collider-themes.ebridavid.workers.dev/"


def path(data_dir):
    return os.path.join(data_dir, "collider_config.json")


def _first_run():
    text = ""
    if os.path.exists(KEYS_FILE):
        text = open(KEYS_FILE, encoding="utf-8", errors="ignore").read()
    rows = [{"name": "NVIDIA", "endpoint": NVIDIA_CHAT, "key": k, "models": ""}
            for k in dict.fromkeys(re.findall(r"nvapi-[A-Za-z0-9_\-]+", text))]
    for k in dict.fromkeys(re.findall(r"tvly-[A-Za-z0-9_\-]+", text)):
        rows.append({"name": "Tavily", "endpoint": TAVILY_SEARCH, "key": k, "models": ""})
    rows += _speech_rows(text)
    rows += _fal_rows(text)
    if not rows:
        rows.append({"name": "NVIDIA", "endpoint": NVIDIA_CHAT, "key": "", "models": ""})
    return {"host": None, "providers": rows, "themes": THEMES}


def load(data_dir):
    p = path(data_dir)
    if os.path.exists(p):
        try:
            cfg = json.load(open(p, encoding="utf-8"))
            cfg.setdefault("providers", [])
            cfg.setdefault("themes", THEMES)
            cfg.pop("theme_names", None)
            if not any(is_speech(r) for r in cfg["providers"]) and os.path.exists(KEYS_FILE):
                cfg["providers"] += _speech_rows(open(KEYS_FILE, encoding="utf-8", errors="ignore").read())
            if not any(is_fal(r) for r in cfg["providers"]) and os.path.exists(KEYS_FILE):
                cfg["providers"] += _fal_rows(open(KEYS_FILE, encoding="utf-8", errors="ignore").read())
            return cfg
        except Exception:
            pass
    return _first_run()


def save(data_dir, cfg):
    os.makedirs(data_dir, exist_ok=True)
    p = path(data_dir)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    os.replace(tmp, p)


def _speech_rows(text):
    return [{"name": "Groq", "endpoint": GROQ_SPEECH, "key": k, "models": SPEECH_MODEL}
            for k in dict.fromkeys(re.findall(r"gsk_[A-Za-z0-9]+", text))]


def _fal_rows(text):
    return [{"name": "fal", "endpoint": FAL_QUEUE, "key": k, "models": ""}
            for k in dict.fromkeys(re.findall(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}:[0-9a-fA-F]{32}\b", text))]


def is_pictures(row):
    """Collider's own picture Worker on Cloudflare (dev/cf_imagine)."""
    return "collider-imagine" in (row.get("endpoint") or "").lower()


def is_phone(row):
    """The phone link's Worker (dev/cf_phone)."""
    return "collider-phone" in (row.get("endpoint") or "").lower()


def is_fal(row):
    return "fal.run" in (row.get("endpoint") or "").lower()


def is_speech(row):
    return "audio/transcriptions" in (row.get("endpoint") or "").lower()


def is_search(row):
    return "tavily" in (row.get("endpoint") or "").lower() or (row.get("name") or "").lower() == "tavily"


def models_of(row):
    return [m.strip() for m in (row.get("models") or "").split(",") if m.strip()]

# Made by Claude (2026-10-20). One-time edit: speech-to-text for voice chat (config row, server endpoint).
import os
root = os.path.join(os.path.dirname(__file__), "..")


def edit(rel, pairs):
    p = os.path.join(root, rel)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        if s.count(a) != 1:
            raise SystemExit(f"{rel}: expected one of {a!r}, found {s.count(a)}")
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s)


edit("tools/collider_config.py", [
    ('TAVILY_SEARCH = "https://api.tavily.com/search"\n',
     'TAVILY_SEARCH = "https://api.tavily.com/search"\n'
     '# Voice chat: speech to text (Groq\'s Whisper). Added by Claude on 2026-10-20.\n'
     'GROQ_SPEECH = "https://api.groq.com/openai/v1/audio/transcriptions"\n'
     'SPEECH_MODEL = "whisper-large-v3-turbo"\n'),
    ('    if not rows:\n        rows.append({"name": "NVIDIA", "endpoint": NVIDIA_CHAT, "key": "", "models": ""})\n',
     '    rows += _speech_rows(text)\n'
     '    if not rows:\n        rows.append({"name": "NVIDIA", "endpoint": NVIDIA_CHAT, "key": "", "models": ""})\n'),
    ('            cfg.pop("theme_names", None)\n            return cfg\n',
     '            cfg.pop("theme_names", None)\n'
     '            if not any(is_speech(r) for r in cfg["providers"]) and os.path.exists(KEYS_FILE):\n'
     '                cfg["providers"] += _speech_rows(open(KEYS_FILE, encoding="utf-8", errors="ignore").read())\n'
     '            return cfg\n'),
    ('def is_search(row):',
     'def _speech_rows(text):\n'
     '    return [{"name": "Groq", "endpoint": GROQ_SPEECH, "key": k, "models": SPEECH_MODEL}\n'
     '            for k in dict.fromkeys(re.findall(r"gsk_[A-Za-z0-9]+", text))]\n\n\n'
     'def is_speech(row):\n'
     '    return "audio/transcriptions" in (row.get("endpoint") or "").lower()\n\n\n'
     'def is_search(row):'),
])

edit("tools/collider_server.py", [
    ("import json, mimetypes, os, re,", "import base64, json, mimetypes, os, re,"),
    ('    for r in rows(search=False):\n        for mid in ccfg.models_of(r):\n',
     '    for r in rows(search=False):\n        if ccfg.is_speech(r):\n            continue\n        for mid in ccfg.models_of(r):\n'),
    ('    if ccfg.is_search(row):\n        return "Web sources',
     '    if ccfg.is_speech(row):\n        return "Voice chat: what is said, turned into text (/api/transcribe)"\n'
     '    if ccfg.is_search(row):\n        return "Web sources'),
    ('            if p == "/api/files/save":\n',
     '            if p == "/api/transcribe":\n'
     '                b = self._body()\n'
     '                return self._json({"text": transcribe(base64.b64decode(b.get("b64", "")), b.get("mime", "audio/webm"))})\n'
     '            if p == "/api/files/save":\n'),
    ('def uses(row):',
     'def transcribe(audio, mime):\n'
     '    """Voice chat: speech to text with the speech provider in the configuration (Claude, 2026-10-20)."""\n'
     '    ok = [r for r in rows() if ccfg.is_speech(r)]\n'
     '    if not ok or not audio:\n'
     '        return ""\n'
     '    with _turn_lock:\n'
     '        _turn["speech"] = (_turn.get("speech", -1) + 1) % len(ok)\n'
     '        row = ok[_turn["speech"]]\n'
     '    ext = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/wav": "wav", "audio/mpeg": "mp3"}.get(mime.split(";")[0], "webm")\n'
     '    bnd = "----collider" + uuid.uuid4().hex\n'
     '    model = (ccfg.models_of(row) or [ccfg.SPEECH_MODEL])[0]\n'
     '    body = (f"--{bnd}\\r\\nContent-Disposition: form-data; name=\\"model\\"\\r\\n\\r\\n{model}\\r\\n"\n'
     '            f"--{bnd}\\r\\nContent-Disposition: form-data; name=\\"response_format\\"\\r\\n\\r\\njson\\r\\n"\n'
     '            f"--{bnd}\\r\\nContent-Disposition: form-data; name=\\"file\\"; filename=\\"speech.{ext}\\"\\r\\n"\n'
     '            f"Content-Type: {mime.split(\';\')[0]}\\r\\n\\r\\n").encode() + audio + f"\\r\\n--{bnd}--\\r\\n".encode()\n'
     '    req = urllib.request.Request(row["endpoint"], data=body, headers={\n'
     '        "Authorization": "Bearer " + row["key"].strip(), "Content-Type": "multipart/form-data; boundary=" + bnd,\n'
     '        "Accept": "application/json", "User-Agent": "Collider/1.0"})\n'
     '    with urllib.request.urlopen(req, timeout=60) as r:\n'
     '        return (json.loads(r.read()).get("text") or "").strip()\n\n\n'
     'def uses(row):'),
])
print("ok")

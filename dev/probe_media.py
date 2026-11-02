# Made by Claude (2026-10-20). Finds which picture models answer with David's NVIDIA key and whether Groq can turn
# speech into text. Prints status and timings only; never a key.
import base64, io, json, os, re, struct, sys, time, urllib.request, urllib.error, wave, math

root = os.path.join(os.path.dirname(__file__), "..")
cfg = json.load(open(os.path.join(root, "data", "collider_config.json"), encoding="utf-8"))
nv = next((r["key"] for r in cfg["providers"] if "nvidia" in (r.get("endpoint") or "").lower() and r.get("key")), "")
text = open(r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt", encoding="utf-8", errors="ignore").read()
groq = (re.findall(r"gsk_[A-Za-z0-9]+", text) or [""])[0]


def post(url, body, key, ctype="application/json", timeout=120):
    req = urllib.request.Request(url, data=body if isinstance(body, bytes) else json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": ctype, "Accept": "application/json",
                                          "User-Agent": "Collider/1.0"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300], time.time() - t
    except Exception as e:
        return 0, repr(e)[:200].encode(), time.time() - t


which = sys.argv[1:] or ["images", "speech"]
if "images" in which:
    tries = [
        ("black-forest-labs/flux.1-schnell", {"prompt": "a glass lantern on a mossy stone, morning light", "width": 1024, "height": 1024, "seed": 0, "steps": 4}),
        ("black-forest-labs/flux.1-dev", {"prompt": "a glass lantern on a mossy stone, morning light", "mode": "base", "cfg_scale": 3.5, "width": 1024, "height": 1024, "seed": 0, "steps": 30}),
        ("stabilityai/stable-diffusion-3-medium", {"prompt": "a glass lantern on a mossy stone, morning light", "cfg_scale": 5, "aspect_ratio": "1:1", "seed": 0, "steps": 30}),
        ("black-forest-labs/flux.2-klein-4b", {"prompt": "a glass lantern on a mossy stone, morning light", "width": 1024, "height": 1024, "seed": 0, "steps": 4}),
    ]
    os.makedirs(os.path.join(root, "dev", "probe_out"), exist_ok=True)
    for model, body in tries:
        code, data, secs = post("https://ai.api.nvidia.com/v1/genai/" + model, body, nv)
        info = ""
        if code == 200:
            j = json.loads(data)
            art = (j.get("artifacts") or [{}])[0]
            b = base64.b64decode(art.get("base64", "")) if art.get("base64") else b""
            if b[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", b[16:24]); info = f"png {w}x{h}"
            elif b[:2] == b"\xff\xd8":
                info = "jpeg"
            info += f" {len(b)} bytes finish={art.get('finishReason')}"
            open(os.path.join(root, "dev", "probe_out", model.split("/")[1] + ".img"), "wb").write(b)
        else:
            info = data[:160].decode(errors="ignore")
        print(f"{model}: {code} {secs:.1f}s {info}")
if "speech" in which:
    # one second of a quiet tone as WAV, just to see the endpoint answer
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b"".join(struct.pack("<h", int(800 * math.sin(i / 8))) for i in range(16000)))
    bnd = "----collider"
    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-large-v3-turbo\r\n"
            f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\nContent-Type: audio/wav\r\n\r\n").encode() + buf.getvalue() + f"\r\n--{bnd}--\r\n".encode()
    code, data, secs = post("https://api.groq.com/openai/v1/audio/transcriptions", body, groq, "multipart/form-data; boundary=" + bnd)
    print(f"groq whisper: {code} {secs:.1f}s {'key found' if groq else 'no key'} {data[:120].decode(errors='ignore')}")

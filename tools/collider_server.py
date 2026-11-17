# E.D. — Collider — Signed: Claude (2026-10-20), Gemini 4 Argon (2026-10-24)
"""Collider local server.

Serves the built app, the model API, the Launch Configurator (/config), and the theme catalog.
Every provider, key, model, and setting comes from data\\collider_config.json, which uses 100% self-explanatory,
unit-explicit keys grouped by functional scope.
Run:  python tools/collider_server.py   (asks nothing; uses the saved localhost_port, or a free one)
"""
import base64, json, mimetypes, os, re, sys, threading, time, uuid, urllib.request, urllib.error, webbrowser
import concurrent.futures as cf
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collider_files as cfiles
import collider_config as ccfg
import collider_thumbs as cthumbs
import collider_imagine as cimagine
import collider_tunnel as ctunnel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "build", "web")
DATA = os.path.join(ROOT, "data")
PORT = 0
FILES = None
THUMBS = None
IMAGINE = None
TUNNEL = None
HIST = ""
SMARTGEN_FILE = ""
CONFIG = {"api_providers_and_keys": []}
_turn = {}
_turn_lock = threading.Lock()
_history_mem = None
_smartgen_mem = None


def setup(root, web, data, port, config):
    """Points the server at its folders, localhost_port, and configuration. Called once before serving."""
    global ROOT, WEB, DATA, PORT, FILES, THUMBS, IMAGINE, TUNNEL, HIST, SMARTGEN_FILE, CONFIG, _history_mem, _smartgen_mem
    ROOT, WEB, DATA, PORT, CONFIG = root, web, data, int(port), config
    os.makedirs(DATA, exist_ok=True)
    FILES = cfiles.Files(DATA)
    THUMBS = cthumbs.Thumbs(FILES.root)
    IMAGINE = cimagine.Imagine(DATA, FILES, _picture_rows, lambda: CONFIG.get("discover_market_image_generation"))
    HIST = os.path.join(DATA, "history.json")
    SMARTGEN_FILE = os.path.join(DATA, "smartgen_cards.json")
    if apply_settings(CONFIG):
        try:
            ccfg.save(DATA, CONFIG)
        except Exception as e:
            print("config save failed", e)
    _extend_roster()
    _init_caches()
    import atexit
    TUNNEL = ctunnel.Tunnel(ROOT, PORT, next((r for r in rows() if ccfg.is_phone(r)), None))
    if TUNNEL.start():
        atexit.register(TUNNEL.stop)


def _dedupe_theme_list(items):
    """Ensures every theme has a distinct display name and replaces corrupted 062 Blue Cove.jpg poster."""
    counts = {}
    numerals = ("", " II", " III", " IV", " V")
    out = []
    for item in items or []:
        t = dict(item)
        base_name = re.sub(r"\s+(II|III|IV|V)$", "", (t.get("name") or "").strip())
        idx = counts.get(base_name, 0)
        counts[base_name] = idx + 1
        suffix = numerals[idx] if idx < len(numerals) else f" {idx + 1}"
        t["name"] = base_name + suffix
        poster = t.get("poster") or ""
        if "062%20Blue%20Cove.jpg" in poster or "062 Blue Cove.jpg" in poster:
            t["poster"] = poster.replace("062%20Blue%20Cove.jpg", "063%20Blue%20Cove.jpg").replace("062 Blue Cove.jpg", "063 Blue Cove.jpg")
        out.append(t)
    return out


def _init_caches():
    """Preload themes_cache.json, history.json (sanitizing any legacy reasoning leaks), and smartgen_cards.json into RAM."""
    global _history_mem, _smartgen_mem
    cache_path = os.path.join(DATA, "themes_cache.json")
    if os.path.isfile(cache_path):
        try:
            raw_themes = json.load(open(cache_path, encoding="utf-8"))
            deduped = _dedupe_theme_list(raw_themes)
            with _themes_lock:
                _themes_cache["data"] = deduped
                _themes_cache["at"] = time.time()
            if deduped != raw_themes:
                json.dump(deduped, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception:
            pass
    threading.Thread(target=_refresh_themes_bg, daemon=True).start()

    try:
        raw_hist = json.load(open(HIST, encoding="utf-8")) if os.path.isfile(HIST) else []
    except Exception:
        raw_hist = []
    dirty = False
    for sess in raw_hist:
        if "line_chars" in sess:
            sess.pop("line_chars", None)
            dirty = True
        prompt = sess.get("prompt") or ""
        cons = sess.get("consensus") or {}
        if "status" in cons:
            cons.pop("status", None)
            dirty = True
        cons_summary = sanitize_model_output((cons.get("summary") or "").strip())
        if cons_summary != (cons.get("summary") or "").strip():
            cons["summary"] = plain(cons_summary)
            dirty = True
        res = sess.get("results") or {}
        done_count = 0
        for mid, r in res.items():
            if r.get("status") == "done" and r.get("error"):
                r.pop("error", None)
                dirty = True
            txt = r.get("text") or ""
            cleaned = sanitize_model_output(txt)
            if txt and not cleaned and cons_summary:
                cleaned = cons_summary
            if cleaned != txt:
                r["text"] = cleaned
                r["essence"] = self_essence_fallback(cleaned) if cleaned else ""
                r["line"] = clean_line(r["essence"] or cleaned) if (r["essence"] or cleaned) else ""
                r.pop("error", None)
                dirty = True
            if r.get("messages"):
                for m_entry in r["messages"]:
                    if m_entry.get("role") == "assistant":
                        mc = sanitize_model_output(m_entry.get("content") or "")
                        if mc and mc != m_entry.get("content"):
                            m_entry["content"] = mc
                            dirty = True
            cur_line = r.get("line") or ""
            source_for_line = r.get("essence") or r.get("text") or cons_summary
            if source_for_line and ("thinking process" in cur_line.lower() or "line 1:" in cur_line.lower() or not cur_line):
                new_line = clean_line(source_for_line)
                if new_line and new_line != cur_line:
                    r["line"] = new_line
                    dirty = True
            if not r.get("messages") and r.get("status") == "done" and r.get("text"):
                r["messages"] = [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": r["text"]},
                ]
                dirty = True
            if r.get("status") == "done" and r.get("text"):
                done_count += 1
        if cons.get("essences"):
            for mid, e in list(cons["essences"].items()):
                ce = sanitize_model_output(e)
                if "internal monologue" in ce.lower() or "incomplete" in ce.lower():
                    ce = cons_summary or ce
                if ce != e:
                    cons["essences"][mid] = plain(ce)
                    dirty = True
                if mid in res and cons["essences"].get(mid) and not res[mid].get("line"):
                    res[mid]["line"] = clean_line(cons["essences"][mid])
                    dirty = True
        if cons_summary and cons.get("line") != cons_summary:
            cons["line"] = cons_summary
            dirty = True
        if cons.get("score") and "/" in str(cons.get("score")) and done_count > 0:
            parts = str(cons["score"]).split("/", 1)
            if parts[0].strip().isdigit() and parts[1].strip().isdigit():
                num, den = int(parts[0].strip()), int(parts[1].strip())
                if den < done_count:
                    groups = cons.get("groups") or []
                    win_len = max((len(g) for g in groups), default=num)
                    cons["score"] = f"{max(num, win_len)}/{done_count}"
                    dirty = True
        if cons.get("dissent"):
            new_dissent = [
                plain(sanitize_model_output(d))
                for d in cons["dissent"]
                if "internal monologue" not in d.lower() and "incomplete" not in d.lower()
            ]
            if new_dissent != cons["dissent"]:
                cons["dissent"] = new_dissent
                dirty = True
        if session_id := sess.get("id"):
            JOBS[session_id] = {**sess, "status": "done", "stage": "done"}
    _history_mem = raw_hist
    if dirty:
        try:
            json.dump(_history_mem[:TUNING["history_kept"]], open(HIST, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception:
            pass

    try:
        _smartgen_mem = json.load(open(SMARTGEN_FILE, encoding="utf-8")) if os.path.isfile(SMARTGEN_FILE) else []
    except Exception:
        _smartgen_mem = []


def _all_provider_rows():
    return CONFIG.get("api_providers_and_keys") or CONFIG.get("providers") or []


def rows(name=None, search=None):
    """Provider rows from the configuration that have a key, optionally only one provider's or only search."""
    out = []
    for raw_r in _all_provider_rows():
        r = ccfg.normalize_provider_row(raw_r)
        if not r["api_key"]:
            continue
        if search is not None and ccfg.is_search(r) != search:
            continue
        if name is not None and r["provider_name"].lower() != name.lower():
            continue
        out.append(r)
    return out


def _picture_rows(provider):
    """Rows with keys for a picture provider: Cloudflare (Collider's Worker), NVIDIA, fal."""
    if provider == "Cloudflare":
        return [r for r in rows() if ccfg.is_pictures(r)]
    if provider == "fal":
        return [r for r in rows() if ccfg.is_fal(r)]
    if provider == "NVIDIA":
        return [r for r in rows() if "integrate.api.nvidia.com" in r["api_endpoint_url"]]
    return []


def next_row(name=None, search=None):
    """Round-robin over the keys of one provider, so several keys share the load."""
    rs = rows(name, search)
    if not rs:
        return None
    k = (name or "").lower() + ("/s" if search else "")
    with _turn_lock:
        _turn[k] = (_turn.get(k, -1) + 1) % len(rs)
        return rs[_turn[k]]


# Built-in Ticker Response Models
DEFAULT_TICKER_MODELS = [
    {"id": "nvidia/nemotron-3.5-bolt-e4b", "label": "Nemotron 3.5 Bolt", "short": "NBLT", "provider": "NVIDIA", "via": "NVIDIA", "color": "#76B900"},
    {"id": "nvidia/nemotron-3.5-super-vl-120b-a12b", "label": "Nemotron 3.5 Super", "short": "N35S", "provider": "NVIDIA", "via": "NVIDIA", "color": "#22C55E"},
    {"id": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", "label": "Nemotron 3 Nano", "short": "N3N", "provider": "NVIDIA", "via": "NVIDIA", "color": "#34D399"},
    {"id": "nvidia/nemotron-3-ultra-550b-a55b", "label": "Nemotron 3 Ultra", "short": "NU3", "provider": "NVIDIA", "via": "NVIDIA", "color": "#4ADE80"},
    {"id": "mistralai/mistral-large-4-1t-a52b", "label": "Mistral Large 4", "short": "ML4", "provider": "Mistral", "via": "NVIDIA", "color": "#FB923C"},
    {"id": "minimaxai/minimax-m3.1-flash", "label": "MiniMax M3.1 Flash", "short": "MM31", "provider": "MiniMax", "via": "NVIDIA", "color": "#F472B6"},
    {"id": "nvidia/nemotron-3-nano-30b-a3b", "label": "Nemotron 3 Nano 30B", "short": "NN30", "provider": "NVIDIA", "via": "NVIDIA", "color": "#10B981"},
    {"id": "nvidia/nemotron-3-super-120b-a12b", "label": "Nemotron 3 Super", "short": "NS3", "provider": "NVIDIA", "via": "NVIDIA", "color": "#76B900"},
    {"id": "nvidia/nemotron-3.5-lightning-30b-a3b", "label": "Nemotron 3.5 Lightning", "short": "NL35", "provider": "NVIDIA", "via": "NVIDIA", "color": "#A3E635"},
    {"id": "z-ai/glm-5.3", "label": "GLM 5.3", "short": "GLM", "provider": "Z.ai", "via": "NVIDIA", "color": "#60A5FA"},
    {"id": "z-ai/glm-5.3-flash", "label": "GLM 5.3 Flash", "short": "GLMF", "provider": "Z.ai", "via": "NVIDIA", "color": "#93C5FD"},
    {"id": "google/gemma-4-31b-it", "label": "Gemma 4 31B", "short": "G4", "provider": "Google", "via": "NVIDIA", "color": "#FBBF24"},
    {"id": "openai/gpt-oss-20b", "label": "GPT OSS 20B", "short": "OSS", "provider": "OpenAI", "via": "NVIDIA", "color": "#34D399"},
    {"id": "meta/muse-glimmer-30b", "label": "Muse Glimmer 30B", "short": "MG", "provider": "Meta", "via": "NVIDIA", "color": "#818CF8"},
    {"id": "deepseek-ai/deepseek-v4.1-flash", "label": "DeepSeek V4.1 Flash", "short": "DS4", "provider": "DeepSeek", "via": "NVIDIA", "color": "#38BDF8"},
    {"id": "meta/llama-3.2-90b-vision-instruct", "label": "Llama 3.2 90B Vision", "short": "L90", "provider": "Meta", "via": "NVIDIA", "color": "#A78BFA"},
    {"id": "meta/llama-3.2-11b-vision-instruct", "label": "Llama 3.2 11B Vision", "short": "L11", "provider": "Meta", "via": "NVIDIA", "color": "#C4B5FD"},
]
ROSTER = [dict(m) for m in DEFAULT_TICKER_MODELS]
CONSENSUS_AGENT = "google/gemma-4-31b-it"
LABEL = {m["id"]: m["label"] for m in ROSTER}
_BUILT_IN = len(ROSTER)
_COLORS = ["#F59E0B", "#EC4899", "#14B8A6", "#8B5CF6", "#EF4444", "#22D3EE", "#84CC16", "#F97316"]

# Full catalog of selectable LLM models across providers for the Launch Configurator dropdowns
MODEL_CATALOG = [
    {"model_id": "nvidia/nemotron-3.5-bolt-e4b", "display_name": "Nemotron 3.5 Bolt", "ticker_badge": "NBLT", "model_creator": "NVIDIA", "api_provider_route": "NVIDIA", "badge_color_hex": "#76B900", "consequence": "Ultra-fast NVIDIA Nemotron 3.5 Bolt responder & consensus agent"},
    {"model_id": "nvidia/nemotron-3.5-super-vl-120b-a12b", "display_name": "Nemotron 3.5 Super", "ticker_badge": "N35S", "model_creator": "NVIDIA", "api_provider_route": "NVIDIA", "badge_color_hex": "#22C55E", "consequence": "Nemotron 3.5 Super VL 120B multimodal & general reasoning"},
    {"model_id": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", "display_name": "Nemotron 3 Nano", "ticker_badge": "N3N", "model_creator": "NVIDIA", "api_provider_route": "NVIDIA", "badge_color_hex": "#34D399", "consequence": "Nemotron 3 Nano 30B omni reasoning responder"},
    {"model_id": "nvidia/nemotron-3-nano-30b-a3b", "display_name": "Nemotron 3 Nano 30B", "ticker_badge": "NN30", "model_creator": "NVIDIA", "api_provider_route": "NVIDIA", "badge_color_hex": "#10B981", "consequence": "Nemotron 3 Nano 30B A3B fast reasoning model"},
    {"model_id": "mistralai/mistral-large-4-1t-a52b", "display_name": "Mistral Large 4", "ticker_badge": "ML4", "model_creator": "Mistral", "api_provider_route": "NVIDIA", "badge_color_hex": "#FB923C", "consequence": "Mistral Large 4 MoE flagship reasoning via NVIDIA"},
    {"model_id": "minimaxai/minimax-m3.1-flash", "display_name": "MiniMax M3.1 Flash", "ticker_badge": "MM31", "model_creator": "MiniMax", "api_provider_route": "NVIDIA", "badge_color_hex": "#F472B6", "consequence": "MiniMax M3.1 Flash fast long-context synthesis via NVIDIA"},
    {"model_id": "google/gemma-4-31b-it", "display_name": "Gemma 4 31B", "ticker_badge": "G4", "model_creator": "Google", "api_provider_route": "NVIDIA", "badge_color_hex": "#FBBF24", "consequence": "Fast, balanced general reasoning & structured JSON (Recommended Primary Judge)"},
    {"model_id": "nvidia/nemotron-3-super-120b-a12b", "display_name": "Nemotron 3 Super", "ticker_badge": "NS3", "model_creator": "NVIDIA", "api_provider_route": "NVIDIA", "badge_color_hex": "#76B900", "consequence": "High-depth analytical reasoning (120B MoE, 12B active) — strong backup judge"},
    {"model_id": "nvidia/nemotron-3-ultra-550b-a55b", "display_name": "Nemotron 3 Ultra", "ticker_badge": "NU3", "model_creator": "NVIDIA", "api_provider_route": "NVIDIA", "badge_color_hex": "#A3E635", "consequence": "Maximum-scale flagship reasoning (550B MoE, 55B active) — deepest synthesis"},
    {"model_id": "nvidia/nemotron-3.5-lightning-30b-a3b", "display_name": "Nemotron 3.5 Lightning", "ticker_badge": "NL35", "model_creator": "NVIDIA", "api_provider_route": "NVIDIA", "badge_color_hex": "#4ADE80", "consequence": "Ultra-low-latency fast responder (30B MoE, 3B active)"},
    {"model_id": "z-ai/glm-5.3", "display_name": "GLM 5.3", "ticker_badge": "GLM", "model_creator": "Z.ai", "api_provider_route": "NVIDIA", "badge_color_hex": "#60A5FA", "consequence": "Flagship bilingual & coding synthesis — reliable backup judge"},
    {"model_id": "z-ai/glm-5.3-flash", "display_name": "GLM 5.3 Flash", "ticker_badge": "GLMF", "model_creator": "Z.ai", "api_provider_route": "NVIDIA", "badge_color_hex": "#93C5FD", "consequence": "High-speed lightweight reasoning & quick summarization"},
    {"model_id": "openai/gpt-oss-20b", "display_name": "GPT OSS 20B", "ticker_badge": "OSS", "model_creator": "OpenAI", "api_provider_route": "NVIDIA", "badge_color_hex": "#34D399", "consequence": "Compact open-weight instruction model with clean direct prose"},
    {"model_id": "meta/muse-glimmer-30b", "display_name": "Muse Glimmer 30B", "ticker_badge": "MG", "model_creator": "Meta", "api_provider_route": "NVIDIA", "badge_color_hex": "#818CF8", "consequence": "Nuanced creative & conversational synthesis (30B)"},
    {"model_id": "deepseek-ai/deepseek-v4.1-flash", "display_name": "DeepSeek V4.1 Flash", "ticker_badge": "DS4", "model_creator": "DeepSeek", "api_provider_route": "NVIDIA", "badge_color_hex": "#38BDF8", "consequence": "Fast chain-of-thought logic, math & code verification"},
    {"model_id": "meta/llama-3.2-90b-vision-instruct", "display_name": "Llama 3.2 90B Vision", "ticker_badge": "L90", "model_creator": "Meta", "api_provider_route": "NVIDIA", "badge_color_hex": "#A78BFA", "consequence": "High-accuracy multimodal image + text analysis (90B)"},
    {"model_id": "meta/llama-3.2-11b-vision-instruct", "display_name": "Llama 3.2 11B Vision", "ticker_badge": "L11", "model_creator": "Meta", "api_provider_route": "NVIDIA", "badge_color_hex": "#C4B5FD", "consequence": "Fast multimodal image + text analysis (11B)"},
    {"model_id": "minimaxai/minimax-m3", "display_name": "MiniMax M3", "ticker_badge": "MM3", "model_creator": "MiniMax", "api_provider_route": "NVIDIA", "badge_color_hex": "#F472B6", "consequence": "Long-context reasoning & structured synthesis via NVIDIA"},
    {"model_id": "opencode/gpt-5.6-luna", "display_name": "GPT 5.6 Luna", "ticker_badge": "LUNA", "model_creator": "OpenCode", "api_provider_route": "OpenCode Zen", "badge_color_hex": "#F59E0B", "consequence": "OpenCode Zen flagship reasoning model (requires OpenCode Zen provider row)"},
    {"model_id": "deepseek-v4-flash", "display_name": "DeepSeek V4 Flash (Zen)", "ticker_badge": "DSZ", "model_creator": "DeepSeek", "api_provider_route": "OpenCode Zen", "badge_color_hex": "#06B6D4", "consequence": "Fast DeepSeek V4 Flash via OpenCode Zen"},
    {"model_id": "qwen3.5-plus", "display_name": "Qwen 3.5 Plus", "ticker_badge": "QW35", "model_creator": "Alibaba", "api_provider_route": "OpenCode Zen", "badge_color_hex": "#8B5CF6", "consequence": "Qwen 3.5 Plus coding & general assistant via OpenCode Zen"},
    {"model_id": "anthropic/claude-3.7-sonnet", "display_name": "Claude 3.7 Sonnet", "ticker_badge": "C37", "model_creator": "Anthropic", "api_provider_route": "OpenRouter", "badge_color_hex": "#D97706", "consequence": "Anthropic flagship coding & writing model (requires OpenRouter provider row)"},
    {"model_id": "google/gemini-2.5-pro", "display_name": "Gemini 2.5 Pro", "ticker_badge": "G25P", "model_creator": "Google", "api_provider_route": "OpenRouter", "badge_color_hex": "#2563EB", "consequence": "Google 1M-context reasoning model (requires OpenRouter or Google Gemini row)"},
    {"model_id": "openai/gpt-4.1", "display_name": "GPT-4.1", "ticker_badge": "G41", "model_creator": "OpenAI", "api_provider_route": "OpenRouter", "badge_color_hex": "#10B981", "consequence": "OpenAI flagship instruction model (requires OpenRouter or OpenAI row)"},
    {"model_id": "grok-3", "display_name": "Grok 3", "ticker_badge": "GRK3", "model_creator": "xAI", "api_provider_route": "xAI", "badge_color_hex": "#EF4444", "consequence": "xAI Grok 3 direct model (requires xAI provider row)"},
]


def _model_to_descriptive(m):
    return {
        "model_id": str(m.get("model_id") or m.get("id") or "").strip(),
        "display_name": str(m.get("display_name") or m.get("label") or "").strip(),
        "ticker_badge": str(m.get("ticker_badge") or m.get("short") or "").strip(),
        "model_creator": str(m.get("model_creator") or m.get("provider") or "").strip(),
        "api_provider_route": str(m.get("api_provider_route") or m.get("via") or "NVIDIA").strip(),
        "badge_color_hex": str(m.get("badge_color_hex") or m.get("color") or "#8B90A0").strip(),
        "custom_temperature": m.get("custom_temperature") if "custom_temperature" in m else m.get("temperature", ""),
        "custom_system_instruction": str(m.get("custom_system_instruction") if "custom_system_instruction" in m else m.get("system", "")),
    }


def _model_to_runtime(m):
    d = _model_to_descriptive(m)
    return {
        "id": d["model_id"],
        "label": d["display_name"] or d["model_id"].split("/")[-1],
        "short": d["ticker_badge"] or (d["display_name"] or d["model_id"])[:4].upper(),
        "provider": d["model_creator"] or d["api_provider_route"],
        "via": d["api_provider_route"] or "NVIDIA",
        "color": d["badge_color_hex"] or "#8B90A0",
        "temperature": d["custom_temperature"],
        "system": d["custom_system_instruction"],
    }


def _extend_roster():
    """Models listed in extra_model_ids against a provider join the runtime roster, answered through that provider."""
    del ROSTER[_BUILT_IN:]
    known = {m["id"] for m in ROSTER}
    for r in rows(search=False):
        if ccfg.is_speech(r) or ccfg.is_fal(r) or ccfg.is_pictures(r) or ccfg.is_phone(r):
            continue
        pname = r["provider_name"]
        for mid in ccfg.models_of(r):
            if mid in known:
                continue
            known.add(mid)
            label = mid.split("/")[-1]
            ROSTER.append({"id": mid, "label": label, "short": label[:4].upper(), "provider": pname, "via": pname,
                           "color": _COLORS[len(ROSTER) % len(_COLORS)], "temperature": "", "system": ""})
            LABEL[mid] = label


def transcribe(audio, mime):
    """Voice chat: speech to text with the Groq Whisper speech provider in the configuration."""
    ok = [r for r in rows() if ccfg.is_speech(r)]
    if not ok or not audio:
        return ""
    with _turn_lock:
        _turn["speech"] = (_turn.get("speech", -1) + 1) % len(ok)
        row = ok[_turn["speech"]]
    ext = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/wav": "wav", "audio/mpeg": "mp3"}.get(mime.split(";")[0], "webm")
    bnd = "----collider" + uuid.uuid4().hex
    model = (ccfg.models_of(row) or [ccfg.SPEECH_MODEL])[0]
    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{model}\r\n"
            f"--{bnd}\r\nContent-Disposition: form-data; name=\"response_format\"\r\n\r\njson\r\n"
            f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"speech.{ext}\"\r\n"
            f"Content-Type: {mime.split(';')[0]}\r\n\r\n").encode() + audio + f"\r\n--{bnd}--\r\n".encode()
    req = urllib.request.Request(row["api_endpoint_url"], data=body, headers={
        "Authorization": "Bearer " + row["api_key"].strip(), "Content-Type": "multipart/form-data; boundary=" + bnd,
        "Accept": "application/json", "User-Agent": "Collider/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return (json.loads(r.read()).get("text") or "").strip()


def uses(raw_row):
    """Where in the app a provider row is read, for the launch window and data\\collider_config.json."""
    row = ccfg.normalize_provider_row(raw_row)
    if not row["api_key"]:
        return "Inactive: no API key selected"
    if ccfg.is_speech(row):
        return "Voice Chat Speech-to-Text: transcribes microphone audio into text (/api/transcribe)"
    if ccfg.is_fal(row):
        return "Discover Market 2K Image Generation: runs high-resolution 2K image generation (/api/imagine)"
    if ccfg.is_phone(row):
        return "Permanent Mobile Tunnel: routes your unchanging phone link to this PC (Settings > Account)"
    if ccfg.is_pictures(row):
        return "Discover Market Free Daily Image Generation: runs FLUX.2 Klein 4B / Dev / Schnell on Cloudflare Workers AI (/api/imagine)"
    if ccfg.is_search(row):
        return "Live Web Search: fetches cited web sources for Internet, Research, and Deep Research (/api/ask) and In-App Browser (/api/page)"
    name = row["provider_name"]
    ms = [m["label"] for m in ROSTER if m.get("via", "").lower() == name.lower()]
    ms += [m.split("/")[-1] for m in ccfg.models_of(row) if m.split("/")[-1] not in ms]
    if not ms:
        return f"Ready for {name} models: assign Ticker Response Models to route '{name}' or list extra_model_ids"
    parts = [f"Answers {len(ms)} Ticker Response Models (/api/ask, /api/reply)"]
    agent = next((m for m in ROSTER if m["id"] == CONSENSUS_AGENT), None)
    if agent and agent.get("via", "").lower() == name.lower():
        parts.append(f"runs Primary Consensus & Smart Gen Judge ({agent['label']})")
    if "integrate.api.nvidia.com" in row["api_endpoint_url"].lower():
        parts.append("runs NVIDIA FLUX.1 Dev image generation")
    return "; ".join(parts) + ": " + ", ".join(ms)


DEPTH = {
    "chat": "Answer directly and concisely. Plain language, no jargon.",
    "internet": "Answer directly using the web sources provided. Cite sources inline as [n]. Plain language, no jargon.",
    "research": ("Write a research report: a one-paragraph answer first, then short sections with headings covering the evidence, "
                 "the trade-offs and a clear recommendation. Cite sources inline as [n] and end with a numbered source list. "
                 "Plain language, no jargon."),
    "deep": ("Write an annotated research paper: an abstract that states the answer, then numbered sections in which every claim "
             "carries its source [n] and a short note on why it matters or how strong the evidence is, a section on where the "
             "sources disagree, and a conclusion with practical next steps. More insight, no jargon: explain anything technical "
             "in everyday words. End with a numbered source list."),
}
SEARCH = {"internet": ("basic", 5), "research": ("advanced", 8), "deep": ("advanced", 12)}
MAX_TOKENS = {"chat": 900, "internet": 1200, "research": 2400, "deep": 4000}
SOURCE_CHARS = {"internet": 1200, "research": 1200, "deep": 1200}

_LEAK_RE = re.compile(
    r"(?im)^(let'?s\s+count\s+characters|wait,\s+the\s+prompt|begin\s+your\s+reply\s+with\s+one\s+line|"
    r"character\s+count\s*:|let'?s\s+check\s+length|drafting\s+the\s+one-liner|the\s+user\s+wants\s+one\s+line|"
    r"here'?s\s+a\s+thinking\s+process|line\s+1\s*:\s*max|then\s+an\s+empty\s+line|then\s+the\s+full\s+answer).*$"
)


def sanitize_model_output(text):
    """Strips <think> tags and internal chain-of-thought leakage."""
    if not text:
        return ""
    s = re.sub(r"<think>.*?</think>", "", str(text), flags=re.S).strip()
    if "<think>" in s:
        s = s.split("<think>", 1)[0].strip()
    for marker in ("Then the full answer:\n", "Then the full answer:", "Let me draft:", "Let's just write:"):
        if marker in s:
            s = s.rsplit(marker, 1)[-1].strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", s) if p.strip()]
    clean_paras = []
    for p in paras:
        low = p.lower()
        if any(k in low for k in (
            "begin your reply with one line",
            "line 1: max",
            "then an empty line",
            "then the full answer",
            "let's check the character count",
            "let's make a short line 1",
            "1,2,3,4,5",
            "prompt asks:",
            "constraints:",
            "let's count",
            "count characters",
            "count: ",
            "let's check the length",
            "characters, spaces included",
            "wait, let's count",
            "analyze user input:",
            "identify key requirements:",
            "we need to produce answer",
            "we need first line",
            "so first line max",
            "need <=",
            "too long.",
            "the user is asking",
            "let me think about",
            "the instruction says:",
            "format considerations:",
            "that's a good structure.",
            "that's pretty good. should i use",
            "here's a thinking process",
            "chars)",
            "characters)",
            "full stop at the end",
            "no period at the end",
        )):
            continue
        clean_paras.append(p)
    s = "\n\n".join(clean_paras) if clean_paras else ""
    s = _LEAK_RE.sub("", s).strip()
    return s


def _sanitize_messages(messages):
    """Ensures alternating roles and non-empty content so multi-turn LLM calls never fail with HTTP 400."""
    out = []
    for m in messages or []:
        role = str(m.get("role") or "user").strip().lower()
        if role not in ("system", "user", "assistant"):
            role = "user"
        content = str(m.get("content") or "").strip()
        if not content:
            continue
        if out and out[-1]["role"] == role and role != "system":
            out[-1]["content"] = out[-1]["content"] + "\n\n" + content
        else:
            out.append({"role": role, "content": content})
    return out


def post_json(url, payload, headers, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def search_results(query, n=None):
    """Plain web results for the in-app browser."""
    n = n or TUNING["browser_search_results"]
    try:
        row = next_row(search=True)
        r = post_json(row["api_endpoint_url"], {"api_key": row["api_key"].strip(), "query": query, "search_depth": TUNING["browser_search_depth"], "max_results": n}, {}, TUNING["browser_search_timeout"])
        return [{"title": x.get("title", ""), "url": x.get("url", ""), "content": x.get("content") or ""} for x in r.get("results", [])]
    except Exception:
        return []


def _search_once(query, depth, n, chars):
    row = next_row(search=True)
    if not row:
        return []
    try:
        r = post_json(row["api_endpoint_url"], {"api_key": row["api_key"].strip(), "query": query, "search_depth": depth, "max_results": n}, {}, TUNING["search_timeout"])
        return [{"title": x.get("title", ""), "url": x.get("url", ""), "content": (x.get("content") or "")[:chars]}
                for x in r.get("results", []) if x.get("url")]
    except Exception as e:
        print("search error", query[:60], e)
        return []


def web_search(query, mode, job=None):
    if mode not in SEARCH or not rows(search=True):
        return []
    depth, n = SEARCH[mode]
    chars = SOURCE_CHARS.get(mode, 1200)
    queries = [query]
    if job is not None:
        job["stage"] = "searching"
        job["queries"] = queries
    found = list(POOL.map(lambda q: _search_once(q, depth, n, chars), queries))
    out, seen = [], set()
    for i in range(max((len(f) for f in found), default=0)):
        for f in found:
            if i < len(f) and f[i]["url"] not in seen and len(out) < n:
                seen.add(f[i]["url"])
                out.append(f[i])
    return out


THINK = {"enable_thinking": False, "thinking": False}

MODEL_ALIAS = {
    "nvidia/nemotron-3-super-120b-a12b": "nvidia/nemotron-3.5-super-vl-120b-a12b",
    "nvidia/nemotron-3.5-lightning": "nvidia/nemotron-3.5-lightning-30b-a3b",
    "nvidia/nemotron-3-ultra": "nvidia/nemotron-3-ultra-550b-a55b",
    "z-ai/glm-5.3": "nvidia/nemotron-3.5-super-vl-120b-a12b",
    "z-ai/glm-5.3-flash": "nvidia/nemotron-3.5-bolt-e4b",
    "google/gemma-4-31b-it": "google/diffusiongemma-26b-a4b-it",
    "openai/gpt-oss-20b": "poolside/laguna-xs-2.1",
    "deepseek-ai/deepseek-v4.1-flash": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "meta/llama-3.2-11b-vision-instruct": "meta/llama-3.2-90b-vision-instruct",
}


def _resolve_nim_model(model):
    return MODEL_ALIAS.get(model, model)


def call_model(model, messages, max_tokens, timeout=None):
    timeout = min(timeout or TUNING["answer_timeout"], 35)
    via = next((m.get("via") for m in ROSTER if m["id"] == model), "NVIDIA")
    api_model = _resolve_nim_model(model)
    clean_msgs = _sanitize_messages(messages)
    last = None
    for _ in range(TUNING["retries"]):
        row = next_row(via, search=False)
        if not row:
            raise RuntimeError(f"no key for {via}")
        try:
            r = post_json(row["api_endpoint_url"], {"model": api_model, "messages": clean_msgs, "max_tokens": max_tokens,
                                                    "temperature": temperature_of(model), "chat_template_kwargs": THINK},
                          {"Authorization": "Bearer " + row["api_key"].strip()}, timeout)
            msg = r["choices"][0]["message"]
            raw_txt = msg.get("content") or msg.get("reasoning_content") or ""
            text = sanitize_model_output(raw_txt)
            if text:
                return text
            last = "empty reply"
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
        except Exception as e:
            last = str(e)[:80]
            if "timed out" in last:
                break
        time.sleep(TUNING["retry_wait"])
    raise RuntimeError(last or "no reply")


def draft_clean(s):
    s = re.sub(r"<think>.*?</think>", "", s or "", flags=re.S)
    i = s.find("<think>")
    return (s[:i] if i >= 0 else s).lstrip()


def stream_model(model, messages, max_tokens, on_text=None, timeout=None):
    timeout = min(timeout or SILENCE, 28)
    via = next((m.get("via") for m in ROSTER if m["id"] == model), "NVIDIA")
    api_model = _resolve_nim_model(model)
    row = next_row(via, search=False)
    if not row:
        raise RuntimeError(f"no key for {via}")
    payload = {"model": api_model, "messages": _sanitize_messages(messages), "max_tokens": max_tokens,
               "temperature": temperature_of(model), "stream": True, "chat_template_kwargs": THINK}
    req = urllib.request.Request(row["api_endpoint_url"], data=json.dumps(payload).encode(), headers={
        "Content-Type": "application/json", "Accept": "text/event-stream", "Authorization": "Bearer " + row["api_key"].strip()})
    parts = []
    reasoning_parts = []
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            for raw in r:
                line = raw.decode("utf-8", "ignore").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    d_obj = json.loads(data)["choices"][0].get("delta") or {}
                    delta = d_obj.get("content")
                    r_delta = d_obj.get("reasoning_content")
                except Exception:
                    continue
                if delta:
                    parts.append(delta)
                    if on_text:
                        on_text("".join(parts))
                elif r_delta:
                    reasoning_parts.append(r_delta)
    except Exception as e:
        if "timed out" in str(e) and not parts and not reasoning_parts:
            return call_model(model, messages, max_tokens, 20)
        if isinstance(e, urllib.error.HTTPError) and e.code == 410:
            raise RuntimeError("retired by the provider")
        if not parts and not reasoning_parts:
            print("stream failed, asking without streaming", model, str(e)[:80])
            return call_model(model, messages, max_tokens, timeout)
    combined = "".join(parts) or "".join(reasoning_parts)
    text = sanitize_model_output(combined)
    return text or call_model(model, messages, max_tokens, timeout)


def sources_block(sources):
    if not sources:
        return ""
    lines = [f"[{i + 1}] {s['title']} — {s['url']}\n{s['content']}" for i, s in enumerate(sources)]
    return "Web sources:\n\n" + "\n\n".join(lines)


# ---------------- Consensus & Smart Gen Agents ----------------
AGENT_CHAIN = [CONSENSUS_AGENT, "nvidia/nemotron-3-super-120b-a12b", "z-ai/glm-5.3"]
AGENT_PROMPT = "Inputs:\n-User's prompt\n-response messages\n\nFrom this\nFill the following fields:\nConsensus Ratio: number of responses with the same sentiment / number of total responses\nConsensus Summary: For each response message, use the prompt message to derive need and message intent. This will simplify each message to its base minimal distinction/sentiment; this is the actionable portion of the message. Resolve democratically by counting the number of duplicates of each unique sentiment. The sentiment with the biggest count is the consensus summary verbatim.\n\nIn the table, indicate which responses are grouped with which sentiments, and indicate the consensus sentiment\n\nAccuracy and confidence and all subjective interpretations of a response are irrelevant. You are only recording reality, not advising. This is what makes this objectively valuable and universally desired.\n\nRecap:\n\nProvide the following:\nConsensus Ratio\nConsensus Summary, as derived (unique actionable takeaway, sentiment, point, intent, summary)"
CHAIN_PROMPT = 'Inputs:\n-User\'s prompt\n-response messages\n\nFor each response:\nCalculate, from the full response text and its service to the observed need, the depth (aka length) of the logical chain in the message. This count should include explicit and implicit logical chains. Explicit logical chains are all sequential clarifications/simplifications. They extend logic, not activity. And they serve the purpose by providing capability and independence to the prompter. Accuracy (not precision) never becomes a factor, as logic is independent of facts. In fact, logic forms facts. It can never be wrong or even evaluated on such. Only facts can, trivia.\n\n1. Logical chain: If you fall, THEN it\'s not your fault\n2. Not a logical chain: If you fall, THEN you can file a claim\n\n1 is a clarification of meaning and drives understanding and decision-making. 2 is giving instruction, which provides only procedure, not logic. No decision-making or simplification is offered.\n\nImplicit logical chains count as well. These are definitions, statements, stories, or any narrative element that directly support a logical conclusion. They can be evidentiary after the fact. Or preemptive, before the fact. The point will either immediately precede or supersede them. If not, the chain is broken, or adlibbing has delayed the expression of the point. It becomes obvious either way.\n\nYou can also count logical chains by simply reading until the next clause/sentence is not logically dependent on the previous. This extends beyond formatting so paragraphs and structure are irrelevant. An entire paragraph can be considered one logical chain if it is one narrative in service of one larger point: evidentiary, or it can be multiple logical chains if the depth of understanding is further developed within the paragraph. "Because," "Why," "Therefore," "Meaning," "Thus," and "therefore" are all contextual indicators but cannot be counted in a vacuum. This is why you derive intent first, based on the prompt message and its need, and you frame each response message in its purpose to serve that need. From there, you can resolve all logical clarifications because they appear as explanations and they provide rationale.\n\nYou will find that the count is not important. Only your definition and your ability to identify them are important. So whatever definition you create for a logical chain will hold up consistently, so long as it is legitimate in its observation of logic. Semantically counting words is not a legitimate observation of logic, by definition. Regex counts trivia. Logical chains count meaning.\n\nImplied logical chains are defined by their usage of a definition as a datum to demonstrate logic or provide clarification of a logical point\n\nImplied Logical Chain examples:\nLogical chain: \'A house is a structure. So..."\nLogical Chain: \'A house is a structure. A shed is a structure..."\nLogical chain: \'A house is a structure. It should be..."\nLogical Chain: \'A house is a structure. If you..."\nLogical Chain: [Implied need for definition] -> "A house is a structure."\nLogical chain: "A house is a structure. The streets are..."\n\nNot logical chains: definitions that are attached to no logical purpose\nNot a logical chain: \'A house is a structure.\'\nNot a logical chain: \'Because why?\' Regex search would count this as 2 logical chains. When in reality, in logical purpose, it is just two words with no intended purpose. It could be a quote. Or a question. Neither of which extends logic on its own or is a logical point.\n\nThe dictionary would be full of logical chains. But it has 0. Because the definitions exist outside of logical framing, aka need. But if you are playing Scrabble and you ask what the best word to make with your letters is, the meaning of the word (its existence) serves a logical need and therefore becomes a logical chain.\nIf you are reading a sentence in a document and you write a prompt asking for the meaning of a word, the intent is derived to be to support your need for understanding. Therefore, responses providing the meaning of a word are now considered logical chains, because the meaning of the word directly supports the prompt\'s derived intent. The prompt need not include the context of "reading a book," "I don\'t understand this word," or "I\'m playing Scrabble" to derive the intent and serve it. Logic is independent of context. Any request for definition or any derived need for definition directly supports the logical basis and counts as a chain. Which can be further extended by further explanation, even if not requested.\n\nCount the total logical chains (explicit + implicit) for each response message and provide the number in a format for this mapping. perhaps JSON, naming each claim by its source name, its indexed value, or its superficial callouts, as you choose to distinguish them. Identification as distinct observations is all that is necessary to be conveyed. Along with their max chain length. Max length is used to distinguish relevant and novel insight/clarification from repetitive, duplicated, or semantic insight. Technical definitions will never extend a logical chain beyond 1. Even if there are 100 of them. They can serve nothing more than immediate understanding on their own. To extend, they must attach to a bigger logical point, and that chain can of course continue on. Split chains don\'t exist. an apparent split, is logical clarification, and counts. It provides further definition and meaningful texture. Everything that furthers understanding is an additional logical chain. Not separate chains. There\'s one request, one chain. One prompt, one chain. One problem, one chain. Outside of that is ad libbing, theorizing, or ponderance. Unless these are requested, they cannot provide further understanding. They only show lack of understanding.\n\nAlso include in the logical chain length table a line for consensus summary and use the max length chain of all its members as its logical chain length value.\n\nAccuracy and confidence and all subjective interpretations of a response are irrelevant. You are only recording reality, not advising. This is what makes this objectively valuable and universally desired.\n\nRecap:\n\nProvide the following:\nLogical Chain Length Table'
AGENT_FORMAT = 'Reply with JSON only, in this shape, so the app can show it:\n{"need": "the need and intent derived from the prompt message",\n "summaries": {"R1": "...", "R2": "..."},\n "groups": [["R1", "R3"], ["R2"]],\n "consensus_summary": "..."}\nsummaries: each response\'s base minimal distinction/sentiment (the actionable portion of the message). Responses with the same sentiment have the same words.\ngroups: the responses grouped with each sentiment.\nconsensus_summary: the sentiment with the biggest count, verbatim.'
CHAIN_FORMAT = 'Reply with JSON only, in this shape, so the app can show it:\n{"chains": {"R1": 0, "R2": 0}}\nchains: each response\'s total logical chains (explicit + implicit). The consensus summary\'s line is filled in where the two consensus agents\' results meet: the max length chain of all its members.'


def parse_json(text):
    text = re.sub(r"```(?:json)?", "", text)
    starts = [i for i, ch in enumerate(text) if ch == "{"]
    for s in starts:
        depth = 0
        for j in range(s, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[s:j + 1])
                        if isinstance(obj, dict) and ("summaries" in obj or "chains" in obj or "create" in obj):
                            return obj
                    except Exception:
                        pass
                    break
    raise ValueError("no json")


def _agent(system, prompt, answers, tags, need_key):
    body = "\n\n".join(f"{t}:\n{answers[mid][:TUNING['agent_answer_chars']]}" for t, mid in tags.items())
    msgs = [{"role": "system", "content": system},
            {"role": "user", "content": f"User's prompt:\n{prompt}\n\nResponse messages:\n\n{body}"}]
    fast_chain = ["nvidia/nemotron-3.5-super-vl-120b-a12b", "nvidia/nemotron-3.5-lightning-30b-a3b", "nvidia/nemotron-3-ultra-550b-a55b"]
    for a in AGENT_CHAIN:
        if a not in fast_chain:
            fast_chain.append(a)
    for agent in fast_chain:
        try:
            out = parse_json(call_model(agent, msgs, TUNING["agent_tokens"], timeout=22))
            if out.get(need_key):
                return agent, out
        except Exception as e:
            print("consensus agent failed", need_key, agent, e)
    return None, {}


def run_consensus(prompt, answers):
    ids = list(answers.keys())
    tags = {f"R{i + 1}": mid for i, mid in enumerate(ids)}
    f1 = POOL.submit(_agent, AGENT_PROMPT + "\n\n" + AGENT_FORMAT, prompt, answers, tags, "summaries")
    f2 = POOL.submit(_agent, CHAIN_PROMPT + "\n\n" + CHAIN_FORMAT, prompt, answers, tags, "chains")
    agent, out = f1.result()
    _, out2 = f2.result()
    summaries = {tags[t]: plain(v) for t, v in (out.get("summaries") or {}).items() if t in tags and str(v).strip()}
    for mid in ids:
        if mid not in summaries or not summaries[mid]:
            summaries[mid] = clean_line(self_essence_fallback(answers[mid]))
    if not summaries:
        return None
    groups = [[tags[t] for t in g if t in tags] for g in out.get("groups") or []]
    groups = [g for g in groups if g]
    seen = {m for g in groups for m in g}
    groups += [[m] for m in summaries if m not in seen]
    groups.sort(key=len, reverse=True)
    chains = {}
    for t, v in (out2.get("chains") or {}).items():
        try:
            if t in tags:
                chains[tags[t]] = int(v)
        except (TypeError, ValueError):
            pass
    for mid in ids:
        if mid not in chains or chains[mid] <= 0:
            chains[mid] = max(1, len([s for s in re.split(r"[.!?]+", answers[mid]) if s.strip()]))
    win = groups[0] if groups else ids
    consensus = plain(out.get("consensus_summary") or (summaries.get(win[0]) if win else ""))
    return {"agent": agent or "nvidia/nemotron-3.5-super-vl-120b-a12b", "need": out.get("need", ""), "essences": summaries, "lines": dict(summaries),
            "chains": chains, "consensus_chain": max((chains.get(m, 0) for m in win), default=1),
            "groups": groups, "summary": consensus, "score": f"{len(win)}/{len(ids)}",
            "dissent": [summaries[g[0]] for g in groups[1:] if g and g[0] in summaries], "tie_basis": ""}


def plain(s):
    return re.sub(r"^\s*(#+|[-*>])\s+", "", re.sub(r"\*\*|__|`", "", str(s or ""))).strip()


def self_essence_fallback(answer):
    paras = [p.strip() for p in str(answer or "").strip().split("\n") if p.strip()]
    target = paras[0] if paras else ""
    return re.split(r"(?<=[.!?])\s", plain(target), maxsplit=1)[0].strip()


def clean_line(t):
    t = plain(str(t or "").strip().split("\n")[0]).strip(" \"'")
    return t.replace("\u2026", "").replace("...", "").strip()


# ---------------- History & SmartGen ----------------
_hist_lock = threading.Lock()


def load_history():
    global _history_mem
    if _history_mem is not None:
        return _history_mem
    try:
        _history_mem = json.load(open(HIST, encoding="utf-8"))
        return _history_mem
    except Exception:
        _history_mem = []
        return _history_mem


def _save_smartgen():
    if _smartgen_mem is None or not SMARTGEN_FILE:
        return
    try:
        json.dump(_smartgen_mem[:TUNING["smartgen_kept"]], open(SMARTGEN_FILE, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass


def _smartgen_agent(job):
    global _smartgen_mem
    if _smartgen_mem is None:
        _smartgen_mem = []
    results = job.get("results") or {}
    said = "\n\n".join(f"{LABEL.get(m, m)}:\n{(r.get('text') or '')[:TUNING['agent_answer_chars']]}"
                        for m, r in results.items() if r.get("status") == "done" and r.get("text"))
    have = "\n".join(f"- {c.get('id')}: {c.get('type') or 'card'} | {c.get('project') or ''} | {c.get('title') or ''}"
                     for c in _smartgen_mem[:TUNING["smartgen_kept"]])
    user = f"Existing items:\n{have or '(none)'}\n\nUser's message:\n{job.get('prompt') or ''}\n\nResponses:\n\n{said}"
    msgs = [{"role": "system", "content": SMARTGEN_PROMPT + "\n\n" + SMARTGEN_FORMAT}, {"role": "user", "content": user}]
    for agent in AGENT_CHAIN:
        try:
            out = parse_json(call_model(agent, msgs, TUNING["agent_tokens"], timeout=TUNING["agent_timeout"]))
            changed = False
            for i, it in enumerate(out.get("create") or []):
                title = str(it.get("title") or "").strip()
                if not title:
                    continue
                _smartgen_mem.insert(0, {
                    "id": f"sg_{job['id']}_{i}", "session_id": job["id"], "type": str(it.get("type") or "task").strip().lower(),
                    "list": "Active", "title": title, "content": str(it.get("content") or "").strip(),
                    "due": str(it.get("due") or "").strip(), "project": str(it.get("project") or "").strip(),
                    "prompt": job.get("prompt") or "", "mode": job.get("mode") or "chat", "created": time.time()})
                changed = True
            for it in out.get("update") or []:
                for c in _smartgen_mem:
                    if c.get("id") == it.get("id"):
                        for k in ("title", "content", "due"):
                            if str(it.get(k) or "").strip():
                                c[k] = str(it[k]).strip()
                        changed = True
            if changed:
                _save_smartgen()
            return
        except Exception as e:
            print("smartgen agent failed", agent, e)


def save_session(job):
    global _history_mem
    with _hist_lock:
        h = list(load_history())
        h = [s for s in h if s.get("id") != job["id"]]
        entry = {k: job.get(k) for k in ("id", "prompt", "mode", "created", "models", "results", "consensus", "sources")}
        h.insert(0, entry)
        _history_mem = h[:TUNING["history_kept"]]
        try:
            json.dump(_history_mem, open(HIST, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception:
            pass


# ---------------- Jobs ----------------
JOBS = {}
POOL = cf.ThreadPoolExecutor(32)


def run_job(job, prior_threads=None):
    prompt, mode = job["prompt"], job["mode"]
    if mode in SEARCH:
        job["stage"] = "searching"
        job["sources"] = web_search(prompt, mode, job)
    job["stage"] = "answering"
    system = DEPTH.get(mode, DEPTH["chat"])
    src = sources_block(job["sources"])
    attached = FILES.attachment_text(job.get("attachments"))
    asked = prompt + ("\n\n" + attached if attached else "")
    prior_threads = prior_threads or {}

    def one(mid):
        t0 = time.time()
        history_msgs = list(prior_threads.get(mid) or [])
        msgs = [{"role": "system", "content": own_system(mid) + system + ("\n\n" + src if src else "")}] + history_msgs + [{"role": "user", "content": asked}]

        def drafted(s):
            if job["results"][mid]["status"] == "pending":
                job["results"][mid].update(text=draft_clean(s).strip())

        try:
            text = stream_model(mid, msgs, MAX_TOKENS.get(mode, 1200), drafted).strip()
            line = clean_line(self_essence_fallback(text))
            updated_thread = _sanitize_messages(history_msgs + [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": text},
            ])
            job["results"][mid].update(
                status="done",
                text=text,
                line=line,
                essence=line,
                messages=updated_thread,
                ms=int((time.time() - t0) * 1000),
            )
            job["results"][mid].pop("error", None)
        except Exception as e:
            fallback_thread = _sanitize_messages(history_msgs + [{"role": "user", "content": prompt}])
            job["results"][mid].update(
                status="error",
                text="",
                error=str(e),
                messages=fallback_thread,
                ms=int((time.time() - t0) * 1000),
            )

    deadline = DEADLINE.get(mode, 120)
    futs = [POOL.submit(one, m) for m in job["models"]]
    cf.wait(futs, timeout=deadline)
    for m, r in job["results"].items():
        if r["status"] == "pending":
            r.update(status="error", error="no answer in time")
    answers = {m: r["text"] for m, r in job["results"].items() if r["status"] == "done" and r["text"]}
    job["stage"] = "consensus"
    cons = run_consensus(prompt, answers) if answers else None
    if cons:
        for mid, e in cons["essences"].items():
            job["results"][mid]["essence"] = e
        for mid, e in (cons.pop("lines", None) or {}).items():
            if mid in job["results"]:
                job["results"][mid]["line"] = e
        cons["line"] = cons.get("summary", "")
        job["consensus"] = cons
    else:
        job["consensus"] = {"summary": "", "score": "", "dissent": []}
    if mode in ("research", "deep") and not job.get("incognito"):
        save_reports(job)
    job["stage"] = "done"
    job["status"] = "done"
    if job.get("save") and not job.get("incognito"):
        save_session(job)
        POOL.submit(_smartgen_agent, job)


def report_text(text, sources):
    listed = "\n".join(f"{i + 1}. [{s.get('title') or s['url']}]({s['url']})" for i, s in enumerate(sources or []))
    return text.strip() + ("\n\n## Sources\n\n" + listed if listed else "") + "\n"


def save_reports(job):
    kind = "Deep Research" if job["mode"] == "deep" else "Research"
    words = " ".join(re.sub(r"[^\w\s-]", " ", job["prompt"]).split()[:8]) or kind
    for mid, r in job["results"].items():
        if r.get("status") != "done" or not r.get("text"):
            continue
        try:
            r["file"] = FILES.save_generated(f"{kind} - {words} - {LABEL.get(mid, mid)}.md", report_text(r["text"], job.get("sources")), LABEL.get(mid, mid))
        except Exception as e:
            print("report save failed", mid, e)


def _normalize_roster_id(mid):
    if mid in LABEL:
        return mid
    aliased = MODEL_ALIAS.get(mid)
    if aliased and aliased in LABEL:
        return aliased
    for k in LABEL:
        if k.startswith(mid) or mid.startswith(k):
            return k
    return None


def new_job(body):
    raw_models = body.get("models", [])
    models = []
    for m in raw_models:
        nm = _normalize_roster_id(m)
        if nm and nm not in models:
            models.append(nm)
    if not models:
        models = [ROSTER[0]["id"]]
    session_id = (body.get("session_id") or "").strip()
    prior_sess = None
    if session_id:
        prior_sess = JOBS.get(session_id) or next((x for x in load_history() if x.get("id") == session_id), None)

    prior_threads = {}
    if prior_sess:
        prev_prompt = prior_sess.get("prompt") or ""
        for m, r in (prior_sess.get("results") or {}).items():
            if r.get("messages"):
                prior_threads[m] = list(r["messages"])
            elif r.get("text"):
                prior_threads[m] = [
                    {"role": "user", "content": prev_prompt},
                    {"role": "assistant", "content": r["text"]},
                ]

    jid = prior_sess["id"] if prior_sess else uuid.uuid4().hex[:12]
    prompt = body.get("prompt", "").strip()
    job = {
        "id": jid,
        "prompt": prompt,
        "mode": body.get("mode", "chat"),
        "created": time.time(),
        "models": models,
        "status": "running",
        "stage": "queued",
        "sources": [],
        "results": {
            m: {
                "status": "pending",
                "text": "",
                "essence": "",
                "line": "",
                "messages": _sanitize_messages(list(prior_threads.get(m) or []) + [{"role": "user", "content": prompt}]),
            }
            for m in models
        },
        "consensus": {"summary": "", "score": "", "dissent": []},
        "save": body.get("autosave", True),
        "incognito": body.get("incognito", False),
        "attachments": [str(a) for a in body.get("attachments", [])][:TUNING["attachments_max"]],
    }
    JOBS[job["id"]] = job
    threading.Thread(target=run_job, args=(job, prior_threads), daemon=True).start()
    return job


REPLIES = {}


def start_reply(body):
    rid = uuid.uuid4().hex[:12]
    rec = {"id": rid, "status": "running", "text": "", "line": "", "messages": []}
    REPLIES[rid] = rec

    def work():
        try:
            out = reply(body, lambda line, text: rec.update(line=line, text=text))
            rec.update(out, status="done" if out.get("text") else "error")
        except Exception as e:
            rec.update(status="error", error=str(e)[:200])

    POOL.submit(work)
    return rec


def reply(body, on_draft=None):
    mid = body.get("model")
    raw_messages = _sanitize_messages(body.get("messages") or [])
    msgs = [{"role": "system", "content": own_system(mid) + DEPTH.get(body.get("mode", "chat"), DEPTH["chat"])}] + [dict(m) for m in raw_messages]
    attached = FILES.attachment_text(body.get("attachments"))
    if attached and msgs and msgs[-1].get("role") == "user":
        msgs[-1] = {"role": "user", "content": msgs[-1]["content"] + "\n\n" + attached}
    drafted = (lambda s: on_draft("", draft_clean(s).strip())) if on_draft else None
    text = stream_model(mid, msgs, TUNING["reply_tokens"], drafted).strip()
    asked = next((m["content"] for m in reversed(raw_messages) if m.get("role") == "user"), "")
    c = run_consensus(asked, {mid: text}) if text else None
    line = ((c or {}).get("lines") or {}).get(mid, "") or self_essence_fallback(text)
    updated_thread = _sanitize_messages(raw_messages + [{"role": "assistant", "content": text}])

    job_id = (body.get("job_id") or body.get("session_id") or "").strip()
    target_sess = None
    if job_id:
        target_sess = JOBS.get(job_id) or next((x for x in load_history() if x.get("id") == job_id), None)
    if target_sess and mid in (target_sess.get("results") or {}):
        res_entry = target_sess["results"][mid]
        res_entry["status"] = "done"
        res_entry["text"] = text
        res_entry["line"] = line
        res_entry["essence"] = line
        res_entry["messages"] = updated_thread
        res_entry.pop("error", None)
        JOBS[target_sess["id"]] = target_sess
        if target_sess.get("save", True) and not target_sess.get("incognito", False):
            save_session(target_sess)

    return {"ok": True, "text": text, "essence": line, "line": line, "messages": updated_thread}


# ---------------- Themes ----------------
_themes_cache = {"at": 0, "data": []}
_themes_lock = threading.Lock()
_NUMBERED = re.compile(r"^(\d{3}) (.+)\.([A-Za-z0-9]+)$")


def _get_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Collider"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


PACK_PRICE = "$4.99"
TRACKS_PER_PACK = 5
THEMES_URL = ccfg.THEMES
STORE_BYPASS = False


def _refresh_themes_bg():
    cache = os.path.join(DATA, "themes_cache.json")
    try:
        listing = _get_json(THEMES_URL or ccfg.THEMES)
    except Exception:
        return
    parts = {}
    for o in listing:
        m = _NUMBERED.match(o["name"])
        if not m:
            continue
        t = parts.setdefault(m.group(1), {"title": m.group(2)})
        t.setdefault(o.get("kind"), o)

    def kind(tags):
        return next((x for x in tags or [] if x not in ("live wallpaper", "mp4") and not re.match(r"^\d+p$", x)), "")

    songs = [(int(n), parts[n]["title"], parts[n]["audio"]["url"], kind((parts[n].get("video") or {}).get("tags")))
             for n in sorted(parts) if parts[n].get("audio")]
    out = []
    for num in sorted(parts):
        t = parts[num]
        v = t.get("video")
        if not v:
            continue
        k, n = kind(v.get("tags")), int(num)
        picks = sorted(songs, key=lambda s: (s[0] != n, s[3] != k, abs(s[0] - n)))[:TRACKS_PER_PACK]
        out.append({
            "id": num,
            "name": t["title"],
            "video": v["url"],
            "poster": t["image"]["url"] if t.get("image") else None,
            "tags": v.get("tags") or [],
            "price": PACK_PRICE,
            "productId": "collider.theme." + num,
            "tracks": [{"title": s[1], "url": s[2]} for s in picks],
        })
    out = _dedupe_theme_list(out)
    with _themes_lock:
        _themes_cache.update(at=time.time(), data=out)
    try:
        json.dump(out, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass


R2_PUBLIC = "https://pub-6263d41408f145baa5b058378744d787.r2.dev/"
MEDIA_EDGE = "https://collider-media.ebridavid.workers.dev/"


def _edge(u):
    return MEDIA_EDGE + u[len(R2_PUBLIC):] if isinstance(u, str) and u.startswith(R2_PUBLIC) else u


def themes():
    return [{**t, "video": _edge(t.get("video")), "poster": _edge(t.get("poster")),
             "tracks": [{**s, "url": _edge(s.get("url"))} for s in t.get("tracks") or []]} for t in (_themes() or [])]


def _themes():
    with _themes_lock:
        if _themes_cache["data"]:
            if time.time() - _themes_cache["at"] >= TUNING["themes_refresh"]:
                _themes_cache["at"] = time.time()
                threading.Thread(target=_refresh_themes_bg, daemon=True).start()
            return _themes_cache["data"]
    cache = os.path.join(DATA, "themes_cache.json")
    if os.path.isfile(cache):
        try:
            data = _dedupe_theme_list(json.load(open(cache, encoding="utf-8")))
            with _themes_lock:
                _themes_cache.update(at=time.time(), data=data)
            threading.Thread(target=_refresh_themes_bg, daemon=True).start()
            return data
        except Exception:
            pass
    _refresh_themes_bg()
    with _themes_lock:
        return _themes_cache["data"]


# ---------------- Descriptive Settings Structure (Zero Ambiguity) ----------------
DEADLINE = {"chat": 100, "internet": 120, "research": 180, "deep": 240}
SILENCE = 45
SMARTGEN_PROMPT = 'Smart Gen holds projects, tasks, reminders, memories, and artifacts.\nCreates the item when the conversation already contains it, unless that item exists for the same project, type, and model. A timed reminder also lands on the calendar.\nWhen ongoing conversation modifies facts/dates of an existing task or project, Smart Gen automatically updates existing records rather than duplicating.\nArtifacts, reminders, tasks, projects, and memories can be bidirectionally attached and embedded in any combination.'
SMARTGEN_FORMAT = 'Reply with JSON only, in this shape, so the app can file it:\n{"create": [{"type": "project | task | reminder | memory | artifact", "title": "...", "content": "...", "due": "date and time, or empty", "project": "..."}],\n "update": [{"id": "an existing item\'s id", "title": "...", "content": "...", "due": "..."}]}\nThe existing items are listed with their ids. Empty lists when the conversation contains no item.'
TUNING = {
    "thinking_tokens": 4000,
    "temperature": 0.4,
    "answer_timeout": 150,
    "retries": 2,
    "retry_wait": 1.5,
    "reply_tokens": 1400,
    "agent_answer_chars": 2200,
    "agent_tokens": 2500,
    "agent_backup_tokens": 9000,
    "agent_timeout": 110,
    "search_timeout": 40,
    "browser_search_depth": "basic",
    "browser_search_results": 10,
    "browser_search_timeout": 30,
    "attachments_max": 12,
    "history_kept": 200,
    "smartgen_kept": 100,
    "themes_refresh": 600,
}

SETTINGS = (
    "global_system_instruction",
    "custom_option_lists",
    "ticker_response_models",
    "consensus_and_smartgen_agents",
    "prompt_modes_configuration",
    "model_execution_and_stream_limits",
    "in_app_browser_and_storage_limits",
    "discover_market_image_generation",
    "live_wallpaper_themes_and_store",
)


def own_system(mid):
    g = str(CONFIG.get("global_system_instruction") or "").strip()
    t = next((str(m.get("system") or "").strip() for m in ROSTER if m["id"] == mid), "")
    parts = [p for p in (g, t) if p]
    return "\n\n".join(parts) + "\n\n" if parts else ""


def temperature_of(mid):
    v = next((m.get("temperature") for m in ROSTER if m["id"] == mid), None)
    try:
        return float(v) if v not in (None, "") else float(TUNING["temperature"])
    except (TypeError, ValueError):
        return float(TUNING["temperature"])


def settings_defaults():
    return {
        "global_system_instruction": "",
        "custom_option_lists": {},
        "ticker_response_models": [_model_to_descriptive(m) for m in DEFAULT_TICKER_MODELS],
        "consensus_and_smartgen_agents": {
            "primary_judge_model_id": CONSENSUS_AGENT,
            "fallback_judge_model_ids": list(AGENT_CHAIN),
            "consensus_summary_and_ratio_instruction": AGENT_PROMPT,
            "consensus_json_format_instruction": AGENT_FORMAT,
            "logical_chain_length_instruction": CHAIN_PROMPT,
            "logical_chain_json_format_instruction": CHAIN_FORMAT,
            "smartgen_task_extraction_instruction": SMARTGEN_PROMPT,
            "smartgen_json_format_instruction": SMARTGEN_FORMAT,
            "agent_input_max_chars_per_model_response": 2200,
            "primary_judge_max_output_tokens": 2500,
            "fallback_judge_max_output_and_thinking_tokens": 9000,
            "judge_model_timeout_seconds": 110,
        },
        "prompt_modes_configuration": {
            "chat": {
                "response_style_instruction": DEPTH["chat"],
                "max_response_output_tokens": 900,
                "max_response_wait_timeout_seconds": 100,
            },
            "internet": {
                "response_style_instruction": DEPTH["internet"],
                "web_search_depth": "basic",
                "web_sources_fetched_count": 5,
                "max_chars_per_web_source_excerpt": 1200,
                "max_response_output_tokens": 1200,
                "max_response_wait_timeout_seconds": 120,
            },
            "research": {
                "response_style_instruction": DEPTH["research"],
                "web_search_depth": "advanced",
                "web_sources_fetched_count": 8,
                "max_chars_per_web_source_excerpt": 1200,
                "max_response_output_tokens": 2400,
                "max_response_wait_timeout_seconds": 180,
            },
            "deep": {
                "response_style_instruction": DEPTH["deep"],
                "web_search_depth": "advanced",
                "web_sources_fetched_count": 12,
                "max_chars_per_web_source_excerpt": 1200,
                "max_response_output_tokens": 4000,
                "max_response_wait_timeout_seconds": 240,
            },
        },
        "model_execution_and_stream_limits": {
            "default_model_temperature": 0.4,
            "max_internal_thinking_tokens_per_model": 4000,
            "max_followup_reply_output_tokens": 1400,
            "max_stream_silence_stall_timeout_seconds": 45,
            "non_streaming_fallback_timeout_seconds": 150,
            "failed_request_max_retry_attempts": 2,
            "retry_wait_delay_seconds": 1.5,
            "web_search_request_timeout_seconds": 40,
        },
        "in_app_browser_and_storage_limits": {
            "browser_fallback_search_depth": "basic",
            "browser_fallback_search_max_results": 10,
            "browser_fallback_search_timeout_seconds": 30,
            "max_attached_files_per_prompt": 12,
            "max_saved_history_sessions": 200,
            "max_saved_smartgen_items": 100,
        },
        "discover_market_image_generation": dict(cimagine.DEFAULTS),
        "live_wallpaper_themes_and_store": {
            "theme_catalog_worker_url": ccfg.THEMES,
            "theme_catalog_auto_refresh_seconds": 600,
            "premium_theme_pack_display_price": "$4.99",
            "music_tracks_per_theme_pack_count": 5,
            "bypass_purchase_paywall_for_testing": False,
        },
    }


def apply_settings(cfg):
    """Migrates any legacy cryptic keys into the self-explanatory schema, removes all dead/ambiguous keys,
    and binds the active server globals to data\\collider_config.json."""
    global CONSENSUS_AGENT, AGENT_CHAIN, DEPTH, SEARCH, MAX_TOKENS, DEADLINE, SILENCE
    global AGENT_PROMPT, AGENT_FORMAT, CHAIN_PROMPT, CHAIN_FORMAT, PACK_PRICE, TRACKS_PER_PACK, _BUILT_IN, SOURCE_CHARS
    global TUNING, SMARTGEN_PROMPT, SMARTGEN_FORMAT, THEMES_URL, STORE_BYPASS

    defaults = settings_defaults()
    changed = False

    if "global_system_instruction" not in cfg:
        cfg["global_system_instruction"] = ""
        changed = True
    if not isinstance(cfg.get("custom_option_lists"), dict):
        cfg["custom_option_lists"] = {}
        changed = True

    # 1. Host port migration
    if "host" in cfg:
        if "localhost_port" not in cfg:
            cfg["localhost_port"] = cfg.get("host")
        cfg.pop("host", None)
        changed = True
    cfg.setdefault("localhost_port", 37418)

    # 2. Providers migration & purpose_in_app annotation
    raw_provs = cfg.get("api_providers_and_keys") if "api_providers_and_keys" in cfg else cfg.get("providers", [])
    norm_provs = [ccfg.normalize_provider_row(r) for r in raw_provs]
    if cfg.get("api_providers_and_keys") != norm_provs or "providers" in cfg:
        cfg["api_providers_and_keys"] = norm_provs
        cfg.pop("providers", None)
        changed = True

    # 3. Ticker Response Models migration
    raw_models = cfg.get("ticker_response_models") if "ticker_response_models" in cfg else cfg.get("models")
    if not raw_models:
        raw_models = defaults["ticker_response_models"]
        changed = True
    desc_models = [_model_to_descriptive(m) for m in raw_models if (m.get("model_id") or m.get("id"))]
    if cfg.get("ticker_response_models") != desc_models or "models" in cfg:
        cfg["ticker_response_models"] = desc_models
        cfg.pop("models", None)
        changed = True

    # 4. Consensus & Smart Gen Agents migration
    old_tuning = cfg.get("tuning") or {}
    csa = dict(defaults["consensus_and_smartgen_agents"])
    if isinstance(cfg.get("consensus_and_smartgen_agents"), dict):
        csa.update(cfg["consensus_and_smartgen_agents"])
    else:
        if "consensus_agent" in cfg:
            csa["primary_judge_model_id"] = cfg["consensus_agent"]
        if "agent_chain" in cfg:
            csa["fallback_judge_model_ids"] = cfg["agent_chain"]
        if "agent_prompt" in cfg and not str(cfg["agent_prompt"]).startswith("You are the Collider consensus agent"):
            csa["consensus_summary_and_ratio_instruction"] = cfg["agent_prompt"]
        if "chain_prompt" in cfg:
            csa["logical_chain_length_instruction"] = cfg["chain_prompt"]
        if "smartgen_prompt" in cfg and not str(cfg["smartgen_prompt"]).startswith("From the finished multi-model conversation"):
            csa["smartgen_task_extraction_instruction"] = cfg["smartgen_prompt"]
        if "agent_answer_chars" in old_tuning:
            csa["agent_input_max_chars_per_model_response"] = int(old_tuning["agent_answer_chars"])
        if "agent_tokens" in old_tuning:
            csa["primary_judge_max_output_tokens"] = int(old_tuning["agent_tokens"])
        if "agent_backup_tokens" in old_tuning:
            csa["fallback_judge_max_output_and_thinking_tokens"] = int(old_tuning["agent_backup_tokens"])
        if "agent_timeout" in old_tuning:
            csa["judge_model_timeout_seconds"] = int(old_tuning["agent_timeout"])
        changed = True
    if cfg.get("consensus_and_smartgen_agents") != csa:
        cfg["consensus_and_smartgen_agents"] = csa
        changed = True

    # 5. Prompt Modes Configuration migration
    pmc = json.loads(json.dumps(defaults["prompt_modes_configuration"]))
    if isinstance(cfg.get("prompt_modes_configuration"), dict):
        for mode_k, mode_def in pmc.items():
            if isinstance(cfg["prompt_modes_configuration"].get(mode_k), dict):
                mode_def.update(cfg["prompt_modes_configuration"][mode_k])
    else:
        old_depth = cfg.get("depth") or {}
        old_search = cfg.get("search") or {}
        old_sc = cfg.get("source_chars") or {}
        old_mt = cfg.get("max_tokens") or {}
        old_dl = cfg.get("deadline") or {}
        for mode_k in ("chat", "internet", "research", "deep"):
            if mode_k in old_depth:
                pmc[mode_k]["response_style_instruction"] = str(old_depth[mode_k])
            if mode_k in old_mt:
                pmc[mode_k]["max_response_output_tokens"] = int(old_mt[mode_k])
            if mode_k in old_dl:
                pmc[mode_k]["max_response_wait_timeout_seconds"] = int(old_dl[mode_k])
            if mode_k in ("internet", "research", "deep"):
                if mode_k in old_search and isinstance(old_search[mode_k], (list, tuple)) and len(old_search[mode_k]) >= 2:
                    pmc[mode_k]["web_search_depth"] = str(old_search[mode_k][0])
                    pmc[mode_k]["web_sources_fetched_count"] = int(old_search[mode_k][1])
                if mode_k in old_sc:
                    pmc[mode_k]["max_chars_per_web_source_excerpt"] = int(old_sc[mode_k])
        changed = True
    if cfg.get("prompt_modes_configuration") != pmc:
        cfg["prompt_modes_configuration"] = pmc
        changed = True

    # 6. Model Execution & Stream Limits migration
    mel = dict(defaults["model_execution_and_stream_limits"])
    if isinstance(cfg.get("model_execution_and_stream_limits"), dict):
        mel.update(cfg["model_execution_and_stream_limits"])
    else:
        if "temperature" in old_tuning:
            mel["default_model_temperature"] = float(old_tuning["temperature"])
        if "thinking_tokens" in old_tuning:
            mel["max_internal_thinking_tokens_per_model"] = int(old_tuning["thinking_tokens"])
        if "reply_tokens" in old_tuning:
            mel["max_followup_reply_output_tokens"] = int(old_tuning["reply_tokens"])
        if "silence" in cfg:
            mel["max_stream_silence_stall_timeout_seconds"] = int(cfg["silence"])
        if "answer_timeout" in old_tuning:
            mel["non_streaming_fallback_timeout_seconds"] = int(old_tuning["answer_timeout"])
        if "retries" in old_tuning:
            mel["failed_request_max_retry_attempts"] = int(old_tuning["retries"])
        if "retry_wait" in old_tuning:
            mel["retry_wait_delay_seconds"] = float(old_tuning["retry_wait"])
        if "search_timeout" in old_tuning:
            mel["web_search_request_timeout_seconds"] = int(old_tuning["search_timeout"])
        changed = True
    if cfg.get("model_execution_and_stream_limits") != mel:
        cfg["model_execution_and_stream_limits"] = mel
        changed = True

    # 7. In-App Browser & Storage Limits migration
    bsl = dict(defaults["in_app_browser_and_storage_limits"])
    if isinstance(cfg.get("in_app_browser_and_storage_limits"), dict):
        bsl.update(cfg["in_app_browser_and_storage_limits"])
    else:
        if "browser_search_depth" in old_tuning:
            bsl["browser_fallback_search_depth"] = str(old_tuning["browser_search_depth"])
        if "browser_search_results" in old_tuning:
            bsl["browser_fallback_search_max_results"] = int(old_tuning["browser_search_results"])
        if "browser_search_timeout" in old_tuning:
            bsl["browser_fallback_search_timeout_seconds"] = int(old_tuning["browser_search_timeout"])
        if "attachments_max" in old_tuning:
            bsl["max_attached_files_per_prompt"] = int(old_tuning["attachments_max"])
        if "history_kept" in old_tuning:
            bsl["max_saved_history_sessions"] = int(old_tuning["history_kept"])
        if "smartgen_kept" in old_tuning:
            bsl["max_saved_smartgen_items"] = int(old_tuning["smartgen_kept"])
        changed = True
    if cfg.get("in_app_browser_and_storage_limits") != bsl:
        cfg["in_app_browser_and_storage_limits"] = bsl
        changed = True

    # 8. Discover Market Image Generation migration
    raw_im = cfg.get("discover_market_image_generation") if "discover_market_image_generation" in cfg else cfg.get("imagine")
    norm_im = cimagine.normalize_imagine_settings(raw_im)
    if cfg.get("discover_market_image_generation") != norm_im or "imagine" in cfg:
        cfg["discover_market_image_generation"] = norm_im
        cfg.pop("imagine", None)
        changed = True

    # 9. Live Wallpaper Themes & Store migration
    lts = dict(defaults["live_wallpaper_themes_and_store"])
    if isinstance(cfg.get("live_wallpaper_themes_and_store"), dict):
        lts.update(cfg["live_wallpaper_themes_and_store"])
    else:
        if "themes" in cfg:
            lts["theme_catalog_worker_url"] = str(cfg["themes"])
        if "themes_refresh" in old_tuning:
            lts["theme_catalog_auto_refresh_seconds"] = int(old_tuning["themes_refresh"])
        if "pack_price" in cfg:
            lts["premium_theme_pack_display_price"] = str(cfg["pack_price"])
        if "tracks_per_pack" in cfg:
            lts["music_tracks_per_theme_pack_count"] = int(cfg["tracks_per_pack"])
        if "store_bypass" in cfg:
            lts["bypass_purchase_paywall_for_testing"] = bool(cfg["store_bypass"])
        changed = True
    if cfg.get("live_wallpaper_themes_and_store") != lts:
        cfg["live_wallpaper_themes_and_store"] = lts
        changed = True

    # 10. Remove all legacy cryptic or dead top-level keys
    for obsolete in (
        "lines_prompt", "essence_prompt", "line_rule", "plan_prompt", "plan_queries", "line_length",
        "consensus_agent", "agent_chain", "agent_prompt", "chain_prompt", "smartgen_prompt",
        "depth", "search", "source_chars", "max_tokens", "deadline", "silence", "tuning",
        "pack_price", "tracks_per_pack", "themes", "store_bypass", "imagine", "models", "providers",
    ):
        if cfg.pop(obsolete, None) is not None:
            changed = True

    # 11. Bind runtime globals from the clean descriptive config
    CONSENSUS_AGENT = str(csa["primary_judge_model_id"]).strip()
    AGENT_CHAIN = [m for m in dict.fromkeys([CONSENSUS_AGENT] + [str(x).strip() for x in csa["fallback_judge_model_ids"]]) if m]
    AGENT_PROMPT = str(csa["consensus_summary_and_ratio_instruction"])
    if csa.get("consensus_json_format_instruction"):
        AGENT_FORMAT = str(csa["consensus_json_format_instruction"])
    CHAIN_PROMPT = str(csa["logical_chain_length_instruction"])
    if csa.get("logical_chain_json_format_instruction"):
        CHAIN_FORMAT = str(csa["logical_chain_json_format_instruction"])
    SMARTGEN_PROMPT = str(csa["smartgen_task_extraction_instruction"])
    if csa.get("smartgen_json_format_instruction"):
        SMARTGEN_FORMAT = str(csa["smartgen_json_format_instruction"])

    ROSTER[:] = [_model_to_runtime(m) for m in desc_models]
    _BUILT_IN = len(ROSTER)
    LABEL.clear()
    LABEL.update({m["id"]: m["label"] for m in ROSTER})

    # Refresh purpose_in_app on provider rows now that ROSTER and CONSENSUS_AGENT are updated
    for r in cfg["api_providers_and_keys"]:
        new_p = uses(r)
        if r.get("purpose_in_app") != new_p:
            r["purpose_in_app"] = new_p
            changed = True

    for mode_k in ("chat", "internet", "research", "deep"):
        m_cfg = pmc[mode_k]
        DEPTH[mode_k] = str(m_cfg["response_style_instruction"])
        MAX_TOKENS[mode_k] = int(m_cfg["max_response_output_tokens"])
        DEADLINE[mode_k] = int(m_cfg["max_response_wait_timeout_seconds"])
        if mode_k in ("internet", "research", "deep"):
            SEARCH[mode_k] = (str(m_cfg["web_search_depth"]), int(m_cfg["web_sources_fetched_count"]))
            SOURCE_CHARS[mode_k] = int(m_cfg["max_chars_per_web_source_excerpt"])

    SILENCE = int(mel["max_stream_silence_stall_timeout_seconds"])
    TUNING.update({
        "temperature": float(mel["default_model_temperature"]),
        "thinking_tokens": int(mel["max_internal_thinking_tokens_per_model"]),
        "reply_tokens": int(mel["max_followup_reply_output_tokens"]),
        "answer_timeout": int(mel["non_streaming_fallback_timeout_seconds"]),
        "retries": int(mel["failed_request_max_retry_attempts"]),
        "retry_wait": float(mel["retry_wait_delay_seconds"]),
        "search_timeout": int(mel["web_search_request_timeout_seconds"]),
        "agent_answer_chars": int(csa["agent_input_max_chars_per_model_response"]),
        "agent_tokens": int(csa["primary_judge_max_output_tokens"]),
        "agent_backup_tokens": int(csa["fallback_judge_max_output_and_thinking_tokens"]),
        "agent_timeout": int(csa["judge_model_timeout_seconds"]),
        "browser_search_depth": str(bsl["browser_fallback_search_depth"]),
        "browser_search_results": int(bsl["browser_fallback_search_max_results"]),
        "browser_search_timeout": int(bsl["browser_fallback_search_timeout_seconds"]),
        "attachments_max": int(bsl["max_attached_files_per_prompt"]),
        "history_kept": int(bsl["max_saved_history_sessions"]),
        "smartgen_kept": int(bsl["max_saved_smartgen_items"]),
        "themes_refresh": int(lts["theme_catalog_auto_refresh_seconds"]),
    })

    THEMES_URL = str(lts["theme_catalog_worker_url"]).strip() or ccfg.THEMES
    PACK_PRICE = str(lts["premium_theme_pack_display_price"])
    TRACKS_PER_PACK = int(lts["music_tracks_per_theme_pack_count"])
    STORE_BYPASS = bool(lts["bypass_purchase_paywall_for_testing"])

    return changed


def build_form_initial(host_val):
    """Builds the complete INITIAL payload for tools/collider_form.py, including the API Keys catalog and Model catalog."""
    apply_settings(CONFIG)
    provs = CONFIG.get("api_providers_and_keys", [])
    return {
        "host": host_val,
        "providers": provs,
        "uses": [uses(r) for r in provs],
        "key_catalog": ccfg.key_catalog(provs),
        "model_catalog": MODEL_CATALOG,
        "settings": {k: CONFIG[k] for k in SETTINGS if k in CONFIG},
    }


# ---------------- HTTP ----------------
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=WEB, **k)

    def end_headers(self):
        if any(self.path.split('?')[0].endswith(ext) for ext in ('.js', '.html', '.json', '/')):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _sse(self, get):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        last, until = None, time.time() + 900
        try:
            while time.time() < until:
                obj = get()
                if obj is None:
                    self.wfile.write(b"event: gone\ndata: {}\n\n")
                    self.wfile.flush()
                    return
                try:
                    s = json.dumps(obj, ensure_ascii=False)
                except RuntimeError:
                    time.sleep(0.03)
                    continue
                if s != last:
                    self.wfile.write(("data: " + s + "\n\n").encode("utf-8"))
                    self.wfile.flush()
                    last = s
                if obj.get("status", "done") in ("done", "error"):
                    self.wfile.write(b"event: end\ndata: {}\n\n")
                    self.wfile.flush()
                    return
                time.sleep(0.08)
        except OSError:
            pass

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def _local(self):
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        return self.client_address[0] in ("127.0.0.1", "::1") and host in ("127.0.0.1", "localhost", "::1") \
            and not self.headers.get("Cf-Connecting-Ip")

    def _let_in(self):
        if self._local():
            return True
        import hmac
        from urllib.parse import urlparse, parse_qs
        key = TUNNEL.key if TUNNEL else ""
        if not key:
            return False
        jar = dict(c.strip().split("=", 1) for c in (self.headers.get("Cookie") or "").split(";") if "=" in c)
        if hmac.compare_digest(jar.get("collider_key", ""), key):
            return True
        given = (parse_qs(urlparse(self.path).query).get("k") or [""])[0]
        if self.command == "GET" and given and hmac.compare_digest(given, key):
            self.send_response(302)
            self.send_header("Set-Cookie", f"collider_key={key}; Path=/; Max-Age=31536000; Secure; HttpOnly; SameSite=Lax")
            self.send_header("Location", "/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        return False

    def do_GET(self):
        ok = self._let_in()
        if ok is None:
            return
        if not ok:
            return self._send(403, "text/plain", b"")
        p = self.path.split("?")[0]
        if p == "/api/phone":
            if not self._local() or not TUNNEL:
                return self._json({"link": "", "qr": ""})
            return self._json({"link": TUNNEL.link(), "qr": TUNNEL.qr()})
        if p == "/api/whoami":
            return self._json({"root": ROOT, "port": PORT})
        if p == "/api/models":
            return self._json({"models": ROSTER, "agent": CONSENSUS_AGENT, "search": bool(rows(search=True)), "keys": len(rows(search=False))})
        if p == "/api/themes":
            return self._json(themes())
        if p == "/api/store":
            return self._json({"bypass": bool(STORE_BYPASS)})
        if p.startswith("/api/stream/r/"):
            return self._sse(lambda: REPLIES.get(p.rsplit("/", 1)[-1]))
        if p.startswith("/api/stream/"):
            jid = p.rsplit("/", 1)[-1]
            return self._sse(lambda: JOBS.get(jid) or next((x for x in load_history() if x.get("id") == jid), None))
        if p.startswith("/api/reply/"):
            rec = REPLIES.get(p.rsplit("/", 1)[-1])
            return self._json(rec or {"error": "not found"}, 200 if rec else 404)
        if p.startswith("/api/job/"):
            jid = p.rsplit("/", 1)[-1]
            job = JOBS.get(jid) or next((x for x in load_history() if x.get("id") == jid), None)
            return self._json(job or {"error": "not found"}, 200 if job else 404)
        if p == "/api/jobs":
            return self._json([{"id": j["id"], "stage": j["stage"], "status": j["status"], "save": j.get("save"),
                                "results": {m: r["status"] for m, r in j["results"].items()}} for j in JOBS.values()])
        if p == "/api/history":
            return self._json({"sessions": load_history()})
        if p == "/api/smartgen":
            return self._json({"cards": _smartgen_mem or []})
        if p in ("/config", "/configurator.html"):
            return self._config_page()
        if p == "/api/config/data":
            return self._json(build_form_initial(PORT))
        if p == "/api/page":
            return self._page()
        if p == "/api/fetch":
            return self._fetch()
        if p == "/api/files/thumb":
            return self._thumb()
        if p == "/api/files":
            return self._json(FILES.listing(list(LABEL.values())))
        if p == "/api/imagine":
            return self._json({"items": IMAGINE.listing(), "models": IMAGINE.models()})
        if p.startswith("/files/"):
            return self._file(p)
        static = self.translate_path(self.path)
        if self.headers.get("Range") and os.path.isfile(static) and self._part(static):
            return
        return super().do_GET()

    def _thumb(self):
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(self.path).query)
        path = FILES.path_for((q.get("source") or [""])[0], (q.get("name") or [""])[0])
        out = THUMBS.path_for(path) if path else None
        if not out:
            return self._send(404, "text/plain", b"")
        data = open(out, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Cache-Control", "max-age=3600")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _part(self, path):
        m = re.match(r"bytes=(\d*)-(\d*)$", (self.headers.get("Range") or "").strip())
        if not m or (m.group(1) == "" and m.group(2) == ""):
            return False
        size = os.path.getsize(path)
        if m.group(1) == "":
            start, end = max(0, size - int(m.group(2))), size - 1
        else:
            start, end = int(m.group(1)), min(int(m.group(2)) if m.group(2) else size - 1, size - 1)
        if start > end or start >= size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return True
        with open(path, "rb") as f:
            f.seek(start)
            data = f.read(end - start + 1)
        self.send_response(206)
        self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        return True

    def _file(self, p):
        parts = p.split("/", 3)
        path = FILES.path_for(parts[2], parts[3]) if len(parts) == 4 else None
        if not path:
            return self._json({"error": "not found"}, 404)
        if self.headers.get("Range") and self._part(path):
            return
        data = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send(self, code, ctype, data):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _target(self):
        from urllib.parse import urlparse, parse_qs
        url = (parse_qs(urlparse(self.path).query).get("url") or [""])[0]
        url = url if re.match(r"^https?://", url) else "https://" + url
        m = re.match(r"^https?://(?:www\.)?duckduckgo\.com/\?(.*)$", url)
        return "https://html.duckduckgo.com/html/?" + m.group(1) if m else url

    def _mobile(self):
        return "collider_ua=mobile" in (self.headers.get("Cookie") or "")

    def _fetch(self, method="GET"):
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0)) if method != "GET" else None
        try:
            code, _, headers, data = cfiles.fetch(self._target(), method, body, self.headers.get("Content-Type"), mobile=self._mobile())
            self._send(code or 200, headers.get("Content-Type") or "application/octet-stream", data)
        except Exception as e:
            self._send(502, "text/plain; charset=utf-8", str(e)[:200].encode())

    def _page(self, method="GET"):
        url = self._target()
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0)) if method != "GET" else None
        try:
            code, final, headers, data = cfiles.fetch_page(url, method, body, self.headers.get("Content-Type"), mobile=self._mobile())
        except Exception as e:
            return self._send(200, "text/html; charset=utf-8", cfiles.error_page(url, str(e)).encode())
        ctype = headers.get("Content-Type") or "text/html"
        if cfiles.is_download(headers):
            name = FILES.save_download(cfiles.download_name(final, headers, data), data)
            return self._send(200, "text/html; charset=utf-8", cfiles.saved_page(name).encode())
        if "html" in ctype.lower():
            text = cfiles.decode_html(data, headers)
            if cfiles.needs_script(final, text):
                text = cfiles.render_page(final, mobile=self._mobile()) or text
            if rows(search=True) and cfiles.is_search_challenge(final, text):
                q = cfiles.search_query(final, body)
                found = search_results(q) if q else []
                if found:
                    text = cfiles.results_page(q, found)
            html = cfiles.prepare_html(text, final.replace('"', "%22"))
            return self._send(200, "text/html; charset=utf-8", html.encode("utf-8"))
        self._send(200, ctype, data)

    def _config_page(self):
        from collider_form import FORM
        initial = build_form_initial(PORT if self._local() else "")
        html = FORM.replace("WHERE", json.dumps(ccfg.path(DATA))).replace("INITIAL", json.dumps(initial))
        return self._send(200, "text/html; charset=utf-8", html.encode("utf-8"))

    def _config_save(self, b):
        cfg = dict(CONFIG)
        raw_provs = b.get("providers") if "providers" in b else b.get("api_providers_and_keys", [])
        cfg["api_providers_and_keys"] = [
            ccfg.normalize_provider_row(r)
            for r in raw_provs
            if any((r.get(k) or "").strip() for k in ("provider_name", "api_endpoint_url", "api_key", "name", "endpoint", "key"))
        ]
        if b.get("host"):
            try:
                cfg["localhost_port"] = int(b["host"])
            except (TypeError, ValueError):
                pass
        cfg.update(b.get("settings") or {})
        apply_settings(cfg)
        ccfg.save(DATA, cfg)
        CONFIG.clear()
        CONFIG.update(cfg)
        _extend_roster()
        return {"ok": True, "uses": [uses(r) for r in CONFIG["api_providers_and_keys"]]}

    def do_HEAD(self):
        if not self._let_in():
            return self._send(403, "text/plain", b"")
        return super().do_HEAD()

    def do_POST(self):
        if not self._let_in():
            return self._send(403, "text/plain", b"")
        p = self.path.split("?")[0]
        try:
            if p == "/api/config":
                return self._json(self._config_save(self._body()))
            if p == "/api/ask":
                job = new_job(self._body())
                return self._json({"id": job["id"]})
            if p == "/api/reply/start":
                return self._json({"id": start_reply(self._body())["id"]})
            if p == "/api/reply":
                return self._json(reply(self._body()))
            if p == "/api/page":
                return self._page("POST")
            if p == "/api/fetch":
                return self._fetch("POST")
            if p == "/api/files/upload":
                b = self._body()
                return self._json({"name": FILES.save_upload(b.get("name", "file"), b.get("b64", ""))})
            if p == "/api/files/generated":
                b = self._body()
                return self._json({"name": FILES.save_generated(b.get("name", "note.md"), b.get("text", ""), b.get("model", ""))})
            if p == "/api/imagine":
                b = self._body()
                return self._json(IMAGINE.start(b.get("text", ""), b.get("kind", "image"), b.get("from"), b.get("replace"),
                                                b.get("model"), b.get("references"), b.get("aspect"), b.get("count")))
            if p == "/api/transcribe":
                b = self._body()
                return self._json({"text": transcribe(base64.b64decode(b.get("b64", "")), b.get("mime", "audio/webm"))})
            if p == "/api/files/save":
                b = self._body()
                return self._json({"name": FILES.save_bytes(b.get("name", "document.docx"), b.get("b64", ""), b.get("replace", ""), "Documents")})
            if p == "/api/files/pdf":
                b = self._body()
                name = FILES.print_pdf(b.get("name", "document.pdf"), b.get("html", ""), b.get("replace", ""), "Documents")
                return self._json({"name": name} if name else {"error": "pdf"}, 200 if name else 500)
            if p == "/api/files/openwith":
                b = self._body()
                path = FILES.path_for(b.get("source", ""), b.get("name", "")) if self._local() else None
                if not path:
                    return self._json({"ok": False}, 404)
                import subprocess
                subprocess.Popen(["rundll32.exe", "shell32.dll,OpenAs_RunDLL", path], stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return self._json({"ok": True})
            if p == "/api/files/download":
                url = self._body().get("url", "")
                code, final, headers, data = cfiles.fetch(url)
                if code and code >= 400:
                    return self._json({"error": f"HTTP {code}"}, 502)
                return self._json({"name": FILES.save_download(cfiles.download_name(final, headers), data)})
        except Exception as e:
            return self._json({"error": str(e)}, 500)
        self._json({"error": "unknown"}, 404)


def main():
    import socket
    cfg = ccfg.load(DATA)
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", int(os.environ.get("PORT") or cfg.get("localhost_port") or cfg.get("host") or 6420)))
    except (OSError, ValueError):
        s.close()
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    setup(ROOT, WEB, DATA, port, cfg)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Collider running at {url}")
    if "--no-open" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    srv.serve_forever()


if __name__ == "__main__":
    main()

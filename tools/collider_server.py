"""Collider local server. Made by Claude. Signed: Claude (2026-10-20).

Serves the built app, the model API and the theme catalog. Every provider, key and address comes from
data\\collider_config.json, which the launch window shows and saves (collider_config.py); keys never
leave this computer and the app only talks to this server.
Run:  python tools/collider_server.py   (asks nothing; uses the saved host number, or a free one)
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

# Set by setup(): the launch window passes the folder, the built app, the data folder and the host number.
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
CONFIG = {"providers": []}
_turn = {}
_turn_lock = threading.Lock()
_history_mem = None
_smartgen_mem = None


def setup(root, web, data, port, config):
    """Points the server at its folders, host number and configuration. Called once before serving."""
    global ROOT, WEB, DATA, PORT, FILES, THUMBS, IMAGINE, TUNNEL, HIST, SMARTGEN_FILE, CONFIG, _history_mem, _smartgen_mem
    ROOT, WEB, DATA, PORT, CONFIG = root, web, data, int(port), config
    os.makedirs(DATA, exist_ok=True)
    FILES = cfiles.Files(DATA)
    THUMBS = cthumbs.Thumbs(FILES.root)
    IMAGINE = cimagine.Imagine(DATA, FILES, _picture_rows, lambda: CONFIG.get("imagine"))
    HIST = os.path.join(DATA, "history.json")
    SMARTGEN_FILE = os.path.join(DATA, "smartgen_cards.json")
    if apply_settings(CONFIG):
        try:
            ccfg.save(DATA, CONFIG)  # the file then shows every line
        except Exception as e:
            print("config save failed", e)
    _extend_roster()
    _init_caches()
    # The phone link: a private https address through Cloudflare's tunnel, when bin\cloudflared.exe is beside the app.
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
        old_n = sess.get("line_chars") or 0
        n = line_budget(max(old_n, LINE_DEFAULT))
        if sess.get("line_chars") != n:
            sess["line_chars"] = n
            dirty = True
        prompt = sess.get("prompt") or ""
        cons = sess.get("consensus") or {}
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
                r["line"] = fit_words(r["essence"] or cleaned, n) if (r["essence"] or cleaned) else ""
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
            if source_for_line and (
                "thinking process" in cur_line.lower()
                or "line 1:" in cur_line.lower()
                or len(cur_line) > n
                or (len(cur_line) <= 38 and len(source_for_line) > len(cur_line) + 6)
            ):
                new_line = fit_words(source_for_line, n)
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
                if mid in res and cons["essences"].get(mid):
                    re_line = fit_words(cons["essences"][mid], n)
                    if re_line and len(res[mid].get("line") or "") <= 38 and len(re_line) > len(res[mid].get("line") or ""):
                        res[mid]["line"] = re_line
                        dirty = True
        if cons_summary:
            new_cons_line = fit_words(cons_summary, n)
            if new_cons_line and new_cons_line != cons.get("line"):
                cons["line"] = new_cons_line
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



def rows(name=None, search=None):
    """Provider rows from the configuration that have a key, optionally only one provider's or only search."""
    out = []
    for r in CONFIG.get("providers", []):
        if not (r.get("key") or "").strip():
            continue
        if search is not None and ccfg.is_search(r) != search:
            continue
        if name is not None and (r.get("name") or "").strip().lower() != name.lower():
            continue
        out.append(r)
    return out


def _picture_rows(provider):
    """Rows with keys for a picture provider: Cloudflare (Collider's Worker), NVIDIA, fal. (Claude, 2026-10-21)"""
    if provider == "Cloudflare":
        return [r for r in rows() if ccfg.is_pictures(r)]
    if provider == "fal":
        return [r for r in rows() if ccfg.is_fal(r)]
    if provider == "NVIDIA":
        return [r for r in rows() if "integrate.api.nvidia.com" in (r.get("endpoint") or "")]
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


# Every NVIDIA chat model that answered on this account.
ROSTER = [
    {"id": "nvidia/nemotron-3-super-120b-a12b", "label": "Nemotron 3 Super", "short": "NS3", "provider": "NVIDIA", "via": "NVIDIA", "color": "#76B900"},
    {"id": "nvidia/nemotron-3-ultra-550b-a55b", "label": "Nemotron 3 Ultra", "short": "NU3", "provider": "NVIDIA", "via": "NVIDIA", "color": "#A3E635"},
    {"id": "nvidia/nemotron-3.5-lightning-30b-a3b", "label": "Nemotron 3.5 Lightning", "short": "NL35", "provider": "NVIDIA", "via": "NVIDIA", "color": "#4ADE80"},
    {"id": "z-ai/glm-5.3", "label": "GLM 5.3", "short": "GLM", "provider": "Z.ai", "via": "NVIDIA", "color": "#60A5FA"},
    {"id": "z-ai/glm-5.3-flash", "label": "GLM 5.3 Flash", "short": "GLMF", "provider": "Z.ai", "via": "NVIDIA", "color": "#93C5FD"},
    {"id": "google/gemma-4-31b-it", "label": "Gemma 4 31B", "short": "G4", "provider": "Google", "via": "NVIDIA", "color": "#FBBF24"},
    {"id": "openai/gpt-oss-20b", "label": "GPT OSS 20B", "short": "OSS", "provider": "OpenAI", "via": "NVIDIA", "color": "#34D399"},
    {"id": "meta/muse-glimmer-30b", "label": "Muse Glimmer 30B", "short": "MG", "provider": "Meta", "via": "NVIDIA", "color": "#818CF8"},
    {"id": "deepseek-ai/deepseek-v4.1-flash", "label": "DeepSeek V4.1 Flash", "short": "DS4", "provider": "DeepSeek", "via": "NVIDIA", "color": "#38BDF8"},
    {"id": "meta/llama-3.2-90b-vision-instruct", "label": "Llama 3.2 90B Vision", "short": "L90", "provider": "Meta", "via": "NVIDIA", "color": "#A78BFA"},
    {"id": "meta/llama-3.2-11b-vision-instruct", "label": "Llama 3.2 11B Vision", "short": "L11", "provider": "Meta", "via": "NVIDIA", "color": "#C4B5FD"},
    # Mistral Nemotron and Kimi K3 were removed on 2026-10-19: NVIDIA answers both with HTTP 410 Gone (retired).
]
CONSENSUS_AGENT = "google/gemma-4-31b-it"
LABEL = {m["id"]: m["label"] for m in ROSTER}
_BUILT_IN = len(ROSTER)
_COLORS = ["#F59E0B", "#EC4899", "#14B8A6", "#8B5CF6", "#EF4444", "#22D3EE", "#84CC16", "#F97316"]


def _extend_roster():
    """Models listed against a provider in the configuration join the roster, answered through that provider."""
    del ROSTER[_BUILT_IN:]
    known = {m["id"] for m in ROSTER}
    for r in rows(search=False):
        if ccfg.is_speech(r) or ccfg.is_fal(r) or ccfg.is_pictures(r) or ccfg.is_phone(r):
            continue
        for mid in ccfg.models_of(r):
            if mid in known:
                continue
            known.add(mid)
            label = mid.split("/")[-1]
            ROSTER.append({"id": mid, "label": label, "short": label[:4].upper(), "provider": r["name"], "via": r["name"],
                           "color": _COLORS[len(ROSTER) % len(_COLORS)]})
            LABEL[mid] = label


def transcribe(audio, mime):
    """Voice chat: speech to text with the speech provider in the configuration (Claude, 2026-10-20)."""
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
    req = urllib.request.Request(row["endpoint"], data=body, headers={
        "Authorization": "Bearer " + row["key"].strip(), "Content-Type": "multipart/form-data; boundary=" + bnd,
        "Accept": "application/json", "User-Agent": "Collider/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return (json.loads(r.read()).get("text") or "").strip()


def uses(row):
    """Where in the app a provider row is read, for the launch window."""
    if ccfg.is_speech(row):
        return "Voice chat: what is said, turned into text (/api/transcribe)"
    if ccfg.is_fal(row):
        return "Pictures (Grok Imagine, paid) and videos (/api/imagine)"
    if ccfg.is_phone(row):
        return "The phone link: always the same address, leading to this computer (Settings > Account > Phone)"
    if ccfg.is_pictures(row):
        return "Pictures through Collider's Cloudflare Worker, free each day up to Cloudflare's allowance (/api/imagine)"
    if ccfg.is_search(row):
        return "Web sources for Internet, Research and Deep Research (/api/ask); search answers in the browser (/api/page)"
    name = (row.get("name") or "").strip()
    ms = [m["label"] for m in ROSTER if m.get("via", "").lower() == name.lower()]
    ms += [m.split("/")[-1] for m in ccfg.models_of(row) if m.split("/")[-1] not in ms]
    if not ms:
        return "Nothing yet: list model names in Models"
    parts = [f"{len(ms)} models' answers (/api/ask) and replies (/api/reply)"]
    agent = next((m for m in ROSTER if m["id"] == CONSENSUS_AGENT), None)
    if agent and agent.get("via", "").lower() == name.lower():
        parts.append("the consensus and two-line summaries (/api/lines)")
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
# Research and Deep Research (Claude, 2026-10-20): searches planned beyond the question itself, and source length kept.
PLAN_QUERIES = {"research": 4, "deep": 8}
SOURCE_CHARS = {"internet": 1200, "research": 1200, "deep": 1200}
PLAN_PROMPT = ("Split the question into {k} web searches that together cover what a thorough answer "
               "needs: the facts, the evidence for and against, recent developments, and expert disagreement. Each search is "
               "a short query a search engine understands. Return ONLY JSON: {\"queries\": [\"...\"]}")

_LEAK_RE = re.compile(
    r"(?im)^(let'?s\s+count\s+characters|wait,\s+the\s+prompt|begin\s+your\s+reply\s+with\s+one\s+line|"
    r"character\s+count\s*:|let'?s\s+check\s+length|drafting\s+the\s+one-liner|the\s+user\s+wants\s+one\s+line|"
    r"here'?s\s+a\s+thinking\s+process|line\s+1\s*:\s*max|then\s+an\s+empty\s+line|then\s+the\s+full\s+answer).*$"
)


def sanitize_model_output(text):
    """Strips <think> tags and internal chain-of-thought character-counting leakage."""
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
    n = n or TUNING["browser_search_results"]
    """Plain web results for the in-app browser."""
    try:
        row = next_row(search=True)
        r = post_json(row["endpoint"], {"api_key": row["key"].strip(), "query": query, "search_depth": TUNING["browser_search_depth"], "max_results": n}, {}, TUNING["browser_search_timeout"])
        return [{"title": x.get("title", ""), "url": x.get("url", ""), "content": x.get("content") or ""} for x in r.get("results", [])]
    except Exception:
        return []


def _search_once(query, depth, n, chars):
    row = next_row(search=True)
    if not row:
        return []
    try:
        r = post_json(row["endpoint"], {"api_key": row["key"].strip(), "query": query, "search_depth": depth, "max_results": n}, {}, TUNING["search_timeout"])
        return [{"title": x.get("title", ""), "url": x.get("url", ""), "content": (x.get("content") or "")[:chars]}
                for x in r.get("results", []) if x.get("url")]
    except Exception as e:
        print("search error", query[:60], e)
        return []


def plan_queries(question, k):
    """Research and Deep Research (Claude, 2026-10-20): the consensus agent splits the question into k searches that
    together cover what a thorough answer needs. Falls back to the question itself."""
    msgs = [{"role": "system", "content": PLAN_PROMPT.replace("{k}", str(k))}, {"role": "user", "content": question}]
    for agent in AGENT_CHAIN:
        try:
            raw = call_model(agent, msgs, TUNING["plan_tokens"] if agent == CONSENSUS_AGENT else TUNING["plan_backup_tokens"], timeout=TUNING["plan_timeout"])
            m = re.search(r"\{.*\}", re.sub(r"```(?:json)?", "", raw), flags=re.S)
            qs = [str(q).strip() for q in (json.loads(m.group(0)).get("queries") or []) if str(q).strip()]
            if qs:
                return qs[:k]
        except Exception as e:
            print("plan failed", agent, e)
    return []


def web_search(query, mode, job=None):
    """Internet: one search. Research and Deep Research: the question and its planned searches, run together,
    sources merged without repeats, up to the mode's number."""
    if mode not in SEARCH or not rows(search=True):
        return []
    depth, n = SEARCH[mode]
    chars = SOURCE_CHARS.get(mode, 1200)
    k = PLAN_QUERIES.get(mode, 0)
    queries = [query]
    if k:
        if job is not None:
            job["stage"] = "planning"
        queries += plan_queries(query, k)
    if job is not None:
        job["stage"] = "searching"
        job["queries"] = queries
    per = n if len(queries) == 1 else max(TUNING["search_fanout_min"],
                                         -(-n * TUNING["search_fanout_factor"] // len(queries)))
    found = list(POOL.map(lambda q: _search_once(q, depth, per, chars), queries))
    out, seen = [], set()
    for i in range(max((len(f) for f in found), default=0)):  # round-robin so every search contributes
        for f in found:
            if i < len(f) and f[i]["url"] not in seen and len(out) < n:
                seen.add(f[i]["url"])
                out.append(f[i])
    return out


# Every model is asked to think (Claude, 2026-10-21; David: thinking is "mandatory").
THINK = {"enable_thinking": True, "thinking": True}


def call_model(model, messages, max_tokens, timeout=None):
    timeout = timeout or TUNING["answer_timeout"]
    via = next((m.get("via") for m in ROSTER if m["id"] == model), "NVIDIA")
    clean_msgs = _sanitize_messages(messages)
    last = None
    for attempt in range(TUNING["retries"]):
        row = next_row(via, search=False)
        if not row:
            raise RuntimeError(f"no key for {via}")
        try:
            r = post_json(row["endpoint"], {"model": model, "messages": clean_msgs, "max_tokens": max_tokens + TUNING["thinking_tokens"],
                                            "temperature": temperature_of(model), "chat_template_kwargs": THINK},
                          {"Authorization": "Bearer " + row["key"].strip()}, timeout)
            msg = r["choices"][0]["message"]
            text = sanitize_model_output(msg.get("content") or "")  # the answer only; the thinking stays out
            if text:
                return text
            last = "empty reply"
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
        except Exception as e:
            last = str(e)[:TUNING["error_chars"]]
            if "timed out" in last:
                break  # a slow model is not retried; the others carry on
        time.sleep(TUNING["retry_wait"])
    raise RuntimeError(last or "no reply")


def draft_clean(s):
    """Text drafted so far, without thinking: a closed <think> block goes, an open one hides the rest until it closes."""
    s = re.sub(r"<think>.*?</think>", "", s or "", flags=re.S)
    i = s.find("<think>")
    return (s[:i] if i >= 0 else s).lstrip()


def draft_split(s, n):
    """Text drafted so far -> (its summary line once complete, the answer drafted so far)."""
    s = draft_clean(s)
    if "\n" in s:
        first, rest = s.split("\n", 1)
        first = clean_line(first)
        if first and len(first) <= n:
            return first, rest.strip()
        return "", s.strip()
    return "", (s.strip() if len(s) > n + TUNING["draft_extra_chars"] else "")


def stream_model(model, messages, max_tokens, on_text=None, timeout=None):
    """The streamed form of call_model (Claude, 2026-10-19): the OpenAI-compatible "stream": true that every chat
    template uses (Vercel AI SDK among them). on_text receives the text drafted so far as tokens arrive. Anything that
    goes wrong before the first token falls back to call_model, so an answer still comes.
    timeout: the longest silence allowed (the configuration's "silence"; measured 2026-10-19: a queued model's first
    byte comes within 30 s, a stalled one never comes)."""
    timeout = timeout or SILENCE
    via = next((m.get("via") for m in ROSTER if m["id"] == model), "NVIDIA")
    row = next_row(via, search=False)
    if not row:
        raise RuntimeError(f"no key for {via}")
    payload = {"model": model, "messages": _sanitize_messages(messages), "max_tokens": max_tokens + TUNING["thinking_tokens"],
               "temperature": temperature_of(model), "stream": True, "chat_template_kwargs": THINK}
    req = urllib.request.Request(row["endpoint"], data=json.dumps(payload).encode(), headers={
        "Content-Type": "application/json", "Accept": "text/event-stream", "Authorization": "Bearer " + row["key"].strip()})
    parts = []
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
                    delta = (json.loads(data)["choices"][0].get("delta") or {}).get("content")
                except Exception:
                    continue
                if delta:
                    parts.append(delta)
                    if on_text:
                        on_text("".join(parts))
    except Exception as e:
        if "timed out" in str(e) and not parts:
            raise RuntimeError("no answer in time")
        if isinstance(e, urllib.error.HTTPError) and e.code == 410:
            raise RuntimeError("retired by the provider")
        if not parts:
            print("stream failed, asking without streaming", model, str(e)[:TUNING["error_chars"]])
            return call_model(model, messages, max_tokens, timeout)
    text = sanitize_model_output("".join(parts))
    return text or call_model(model, messages, max_tokens, timeout)


def sources_block(sources):
    if not sources:
        return ""
    lines = [f"[{i + 1}] {s['title']} — {s['url']}\n{s['content']}" for i, s in enumerate(sources)]
    return "Web sources:\n\n" + "\n\n".join(lines)


# ---------------- Consensus agent (Consensus Map v3: a headcount of essences) ----------------
# Primary agent answers in plain JSON; the reasoning models are backups with room to think.
AGENT_CHAIN = [CONSENSUS_AGENT, "nvidia/nemotron-3-super-120b-a12b", "z-ai/glm-5.3"]
AGENT_PROMPT = 'Inputs:\n-User\'s prompt\n-response messages\n\nFrom this\nFill the following fields:\nConsensus Ratio: number of responses with the same sentiment / number of total responses\nConsensus Summary: For each response message, use the prompt message to derive need and message intent. This will simplify each message to its base minimal distinction/sentiment; this is the actionable portion of the message. Resolve democratically by counting the number of duplicates of each unique sentiment. The sentiment with the biggest count is the consensus summary verbatim.\n\nFor each response:\nCalculate, from the full response text and its service to the observed need, the depth (aka length) of the logical chain in the message. This count should include explicit and implicit logical chains. Explicit logical chains are all sequential clarifications/simplifications. They extend logic, not activity. And they serve the purpose by providing capability and independence to the prompter. Accuracy (not precision) never becomes a factor, as logic is independent of facts. In fact, logic forms facts. It can never be wrong or even evaluated on such a basis. Only facts can, trivia.\n\n1. Logical chain: If you fall, THEN it\'s not your fault\n2. Not a logical chain: If you fall, THEN you can file a claim\n\n1 is a clarification of meaning and drives understanding and decision-making. 2 is giving instruction, which provides only procedure, not logic. No decision-making or simplification is offered.\n\nImplicit logical chains count as well. These are definitions, statements, stories, or any narrative element that directly support a logical conclusion. They can be evidentiary after the fact. Or preemptive, before the fact. The point will either immediately precede or supersede them. If not, the chain is broken, or adlibbing has delayed the expression of the point. It becomes obvious either way.\n\nYou can also count logical chains by simply reading until the next clause/sentence is not logically dependent on the previous. This extends beyond formatting so paragraphs and structure are irrelevant. An entire paragraph can be considered one logical chain if it is one narrative in service of one larger point: evidentiary, or it can be multiple logical chains if the depth of understanding is further developed within the paragraph. "Because," "Why," "Therefore," "Meaning," "Thus," and "therefore" are all contextual indicators but cannot be counted in a vacuum. This is why you derive intent first, based on the prompt message and its need, and you frame each response message in its purpose to serve that need. From there, you can resolve all logical clarifications because they appear as explanations and they provide rationale.\n\nYou will find that the count is not important. Only your definition and your ability to identify them are important. So whatever definition you create for a logical chain will hold up consistently, so long as it is legitimate in its observation of logic. Semantically counting words is not a legitimate observation of logic, by definition. Regex counts trivia. Logical chains count meaning.\n\nImplied logical chains are defined by their usage of a definition as a datum to demonstrate logic or provide clarification of a logical point\n\nImplied Logical Chain examples:\nLogical chain: \'A house is a structure. So..."\nLogical Chain: \'A house is a structure. A shed is a structure..."\nLogical chain: \'A house is a structure. It should be..."\nLogical Chain: \'A house is a structure. If you..."\nLogical Chain: [Implied need for definition] -> "A house is a structure."\nLogical chain: "A house is a structure. The streets are..."\n\nNot logical chains: definitions that are attached to no logical purpose\nNot a logical chain: \'A house is a structure.\'\nNot a logical chain: \'Because why?\' Regex search would count this as 2 logical chains. When in reality, in logical purpose, it is just two words with no intended purpose. It could be a quote. Or a question. Neither of which extends logic on its own or is a logical point.\n\nThe dictionary would be full of logical chains. But it has 0. Because the definitions exist outside of logical framing, aka need. But if you are playing Scrabble and you ask what the best word to make with your letters is, the meaning of the word (its existence) serves a logical need and therefore becomes a logical chain.\nIf you are reading a sentence in a document and you write a prompt asking for the meaning of a word, the intent is derived to be to support your need for understanding. Therefore, responses providing the meaning of a word are now considered logical chains, because the meaning of the word directly supports the prompt\'s derived intent. The prompt need not include the context of "reading a book," "I don\'t understand this word," or "I\'m playing Scrabble" to derive the intent and serve it. Logic is independent of context. Any request for definition or any derived need for definition directly supports the logical basis and counts as a chain. Which can be further extended by further explanation, even if not requested.\n\nCount the total logical chains (explicit + implicit) for each response message and provide the number in a format for this mapping. perhaps JSON, naming each claim by its source name, its indexed value, or its superficial callouts, as you choose to distinguish them. Identification as distinct observations is all that is necessary to be conveyed. Along with their max chain length. Max length is used to distinguish relevant and novel insight/clarification from repetitive, duplicated, or semantic insight. Technical definitions will never extend a logical chain beyond 1. Even if there are 100 of them. They can serve nothing more than immediate understanding on their own. To extend, they must attach to a bigger logical point, and that chain can of course continue on. Split chains don\'t exist. an apparent split, is logical clarification, and counts. It provides further definition and meaningful texture. Everything that furthers understanding is an additional logical chain. Not separate chains. There\'s one request, one chain. One prompt, one chain. One problem, one chain. Outside of that is ad libbing, theorizing, or ponderance. Unless these are requested, they cannot provide further understanding. They only show lack of understanding.\n\nAlso include in the logical chain length table a line for consensus summary and use the max length chain of all its members as its logical chain length value.\n\nIn the table, indicate which responses are grouped with which sentiments, and indicate the consensus sentiment\n\nAccuracy and confidence and all subjective interpretations of a response are irrelevant. You are only recording reality, not advising. This is what makes this objectively valuable and universally desired.\n\nRecap:\n\nProvide the following:\nConsensus Ratio\nConsensus Summary, as derived (unique actionable takeaway, sentiment, point, intent, summary)\nLogical Chain Length Table'
AGENT_FORMAT = 'Reply with JSON only, in this shape, so the app can show it:\n{"need": "the need and intent derived from the prompt",\n "sentiments": {"R1": "...", "R2": "..."},\n "groups": [["R1", "R3"], ["R2"]],\n "consensus": "the consensus summary, verbatim",\n "chains": {"R1": 0, "R2": 0}}\nsentiments: each response\'s base minimal distinction/sentiment, at most {n} characters. Responses with the same sentiment have it word for word.\ngroups: the responses grouped with each sentiment.\nchains: each response\'s logical chain length.'


def parse_json(text):
    text = re.sub(r"```(?:json)?", "", text)
    starts = [i for i, ch in enumerate(text) if ch == "{"]
    for s in starts:  # first balanced object that parses
        depth = 0
        for j in range(s, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[s:j + 1])
                        if isinstance(obj, dict) and ("sentiments" in obj or "essences" in obj or "create" in obj):
                            return obj
                    except Exception:
                        pass
                    break
    raise ValueError("no json")


def run_consensus(prompt, answers, n=None):
    """The consensus agent, by David's instruction (AGENT_PROMPT). answers: {model_id: text}.
    Returns the need, each response's sentiment, the groups, the consensus summary, the ratio and the chain lengths."""
    n = n or LINE_DEFAULT
    ids = list(answers.keys())
    tags = {f"R{i + 1}": mid for i, mid in enumerate(ids)}
    body = "\n\n".join(f"{t}:\n{answers[mid][:TUNING['agent_answer_chars']]}" for t, mid in tags.items())
    msgs = [{"role": "system", "content": AGENT_PROMPT + "\n\n" + AGENT_FORMAT.replace("{n}", str(n))},
            {"role": "user", "content": f"User's prompt:\n{prompt}\n\nResponse messages:\n\n{body}"}]
    for agent in AGENT_CHAIN:
        try:
            out = parse_json(call_model(agent, msgs, TUNING["agent_tokens"] if agent == CONSENSUS_AGENT else TUNING["agent_backup_tokens"], timeout=TUNING["agent_timeout"]))
            sent = {tags[t]: plain(e) for t, e in (out.get("sentiments") or out.get("essences") or {}).items() if t in tags}
            if not sent:
                raise ValueError("no sentiments")
            groups = [[tags[t] for t in g if t in tags] for g in out.get("groups") or []]
            groups = [g for g in groups if g]
            seen = {m for g in groups for m in g}
            groups += [[m] for m in sent if m not in seen]
            groups.sort(key=len, reverse=True)
            chains = {}
            for t, v in (out.get("chains") or {}).items():
                try:
                    if t in tags:
                        chains[tags[t]] = int(v)
                except (TypeError, ValueError):
                    pass
            summary = plain(out.get("consensus") or out.get("summary") or (sent.get(groups[0][0]) if groups else ""))
            win = groups[0] if groups else []
            return {"status": "done", "agent": agent, "need": out.get("need", ""), "essences": sent, "lines": dict(sent),
                    "chains": chains, "consensus_chain": max((chains.get(m, 0) for m in win), default=0),
                    "groups": groups, "summary": summary, "score": f"{len(win)}/{len(ids)}",
                    "dissent": [sent[g[0]] for g in groups[1:] if g and g[0] in sent], "tie_basis": ""}
        except Exception as e:
            print("consensus agent failed", agent, e)
    return None


def plain(s):
    """A summary sentence without markdown marks."""
    return re.sub(r"^\s*(#+|[-*>])\s+", "", re.sub(r"\*\*|__|`", "", str(s or ""))).strip()


def self_essence_fallback(answer):
    paras = [p.strip() for p in str(answer or "").strip().split("\n") if p.strip()]
    target = paras[1] if len(paras) > 1 and len(paras[0]) <= TUNING["essence_short_line"] else (paras[0] if paras else "")
    first = re.split(r"(?<=[.!?])\s", plain(target), maxsplit=1)[0]
    return first[:TUNING["essence_fallback_chars"]]


# ---------------- Two-line Summary ----------------
# Every ticker row and the consensus preview shows up to TWO lines (~115 chars): the complete answer, never cut, fitting its box.
LINE_DEFAULT = 115


def line_budget(v):
    try:
        return max(TUNING["line_min"], min(TUNING["line_max"], int(v)))
    except Exception:
        return LINE_DEFAULT


def clean_line(t):
    t = plain(str(t or "").strip().split("\n")[0]).strip(" \"'")
    return t.replace("\u2026", "").replace("...", "").rstrip(". ").strip()


def fit_words(t, n):
    """Clause-aware summary fitter: prefers complete clauses before punctuation, then whole words without dangling prepositions."""
    t = clean_line(t)
    if len(t) <= n:
        return t
    window = t[:n + 1]
    for sep in (". ", "; ", " — ", " – ", ": ", ", "):
        idx = window.rfind(sep)
        if idx >= max(18, n // 2):
            window = window[:idx]
            break
    else:
        window = window[:window.rfind(" ")] if " " in window else t[:n]
    cut = window.strip().rstrip(".")
    while True:
        new = re.sub(
            r"(?i)[\s,;:(\-\u2013\u2014]+$|\s+(and|or|but|the|a|an|to|of|for|with|in|on|at|by|from|as|into|than|"
            r"is|are|was|were|be|been|has|have|had|will|would|can|could|should|may|might|"
            r"that|which|who|whom|whose|where|when|while|because|since|unless|although|if|not|no|so|yet)$",
            "",
            cut,
        ).strip()
        if new == cut or not new:
            return cut
        cut = new


def split_line(text, n):
    """A model's reply -> (its own summary line, the full answer). The line is taken only when it fits."""
    cleaned = sanitize_model_output(text)
    rows = str(cleaned or "").strip().split("\n")
    first = clean_line(rows[0])
    rest = "\n".join(rows[1:]).strip()
    if first and len(first) <= n:
        return first, (rest or first)
    sentence = re.split(r"(?<=[.!?])\s", plain(rows[0]).strip(), maxsplit=1)[0]
    return fit_words(sentence, n), str(cleaned or "").strip()


def agent_lines(prompt, answers, n, groups=None):
    """Each response's summary, for sessions saved without one: the consensus agent's sentiment for it."""
    c = run_consensus(prompt, answers, n)
    return {m: v for m, v in ((c or {}).get("lines") or {}).items() if v}


def consensus_line(sess, n):
    """The consensus preview is the winning group's line, verbatim, so it matches a card word for word."""
    cons, results = sess.get("consensus") or {}, sess.get("results") or {}
    has = lambda m: bool((results.get(m) or {}).get("line")) and len(results[m]["line"]) <= n
    for m, e in (cons.get("essences") or {}).items():
        if plain(e) == plain(cons.get("summary")) and has(m):
            return results[m]["line"]
    groups = sorted(cons.get("groups") or [], key=len, reverse=True)
    for m in (groups[0] if groups else []):
        if has(m):
            return results[m]["line"]
    return fit_words(cons.get("summary", ""), n)


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
    """The Smart Gen agent, by David's spec (SMARTGEN_PROMPT, in the configuration): creates an item only when the
    conversation contains one and it is not already there, and updates an item the conversation changes."""
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
        entry = {k: job.get(k) for k in ("id", "prompt", "mode", "created", "models", "results", "consensus", "sources", "line_chars")}
        h.insert(0, entry)
        _history_mem = h[:TUNING["history_kept"]]
        try:
            json.dump(_history_mem, open(HIST, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception:
            pass


def ensure_lines(body):
    """Fills in the summary line form where a session has none, or has one made for a different box. Answers stay as they are."""
    n, sid = line_budget(body.get("line")), body.get("id")
    job = JOBS.get(sid)
    sess = job or next((x for x in load_history() if x.get("id") == sid), None)
    if not sess:
        return {"error": "not found"}
    res = sess.get("results") or {}
    done = {m: r["text"] for m, r in res.items() if r.get("status") == "done" and r.get("text")}
    todo = [m for m in done if not (res[m].get("line") and len(res[m]["line"]) <= n)]
    cons = sess.get("consensus") or {}
    need_cons_line = cons.get("status") == "done" and (todo or not (cons.get("line") and len(cons["line"]) <= n))
    if not todo and not need_cons_line:
        return {**{k: sess.get(k) for k in ("id", "prompt", "mode", "created", "results", "consensus", "sources")}, "status": "done"}
    if todo:
        got = agent_lines(sess.get("prompt", ""), done, n, cons.get("groups"))
        for m in todo:
            res[m]["line"] = got.get(m) or res[m].get("essence") or ""
    if need_cons_line:
        cons["line"] = consensus_line(sess, n)
    sess["line_chars"] = n
    save_session(sess)
    return {**{k: sess.get(k) for k in ("id", "prompt", "mode", "created", "results", "consensus", "sources")}, "status": "done"}


# ---------------- Jobs ----------------
JOBS = {}
POOL = cf.ThreadPoolExecutor(32)


def run_job(job, prior_threads=None):
    prompt, mode = job["prompt"], job["mode"]
    if mode in SEARCH:
        job["stage"] = "searching"
        job["sources"] = web_search(prompt, mode, job)
    job["stage"] = "answering"
    n = job["line_chars"]
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
            text, line = stream_model(mid, msgs, MAX_TOKENS.get(mode, 1200), drafted).strip(), ""
            updated_thread = _sanitize_messages(history_msgs + [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": text},
            ])
            job["results"][mid].update(
                status="done",
                text=text,
                line=line,
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

    # Every model gets the same deadline; one slow model never holds the others back.
    deadline = DEADLINE.get(mode, 120)
    futs = [POOL.submit(one, m) for m in job["models"]]
    cf.wait(futs, timeout=deadline)
    for m, r in job["results"].items():
        if r["status"] == "pending":
            r.update(status="error", error="no answer in time")
    answers = {m: r["text"] for m, r in job["results"].items() if r["status"] == "done" and r["text"]}
    job["stage"] = "consensus"
    cons = run_consensus(prompt, answers, n) if answers else None
    if cons:
        for mid, e in cons["essences"].items():
            job["results"][mid]["essence"] = e
        for mid, e in (cons.pop("lines", None) or {}).items():
            if mid in job["results"]:
                job["results"][mid]["line"] = e
        cons["line"] = cons.get("summary", "")
        job["consensus"] = cons
    else:
        job["consensus"] = {"status": "unavailable", "summary": "", "score": "", "dissent": []}
    if mode in PLAN_QUERIES and not job.get("incognito"):
        save_reports(job)
    job["stage"] = "done"
    job["status"] = "done"
    if job.get("save") and not job.get("incognito"):
        save_session(job)
        POOL.submit(_smartgen_agent, job)


def report_text(text, sources):
    """A report as a document: the model's text, then the sources it was given, numbered as it cites them."""
    listed = "\n".join(f"{i + 1}. [{s.get('title') or s['url']}]({s['url']})" for i, s in enumerate(sources or []))
    return text.strip() + ("\n\n## Sources\n\n" + listed if listed else "") + "\n"


def save_reports(job):
    """Research and Deep Research (Claude, 2026-10-20): every report is kept as a document in Files > Generated."""
    kind = "Deep Research" if job["mode"] == "deep" else "Research"
    words = " ".join(re.sub(r"[^\w\s-]", " ", job["prompt"]).split()[:TUNING["report_words"]]) or kind
    for mid, r in job["results"].items():
        if r.get("status") != "done" or not r.get("text"):
            continue
        try:
            r["file"] = FILES.save_generated(f"{kind} - {words} - {LABEL.get(mid, mid)}.md", report_text(r["text"], job.get("sources")), LABEL.get(mid, mid))
        except Exception as e:
            print("report save failed", mid, e)


def new_job(body):
    models = [m for m in body.get("models", []) if m in LABEL] or [ROSTER[0]["id"]]
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
        "line_chars": line_budget(body.get("line")),
        "consensus": {"status": "pending"},
        "save": body.get("autosave", True),
        "incognito": body.get("incognito", False),
        "attachments": [str(a) for a in body.get("attachments", [])][:TUNING["attachments_max"]],
    }
    JOBS[job["id"]] = job
    threading.Thread(target=run_job, args=(job, prior_threads), daemon=True).start()
    return job


REPLIES = {}


def start_reply(body):
    """A reply that drafts: the app watches /api/stream/r/<id> while the model writes."""
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
    n = line_budget(body.get("line"))
    raw_messages = _sanitize_messages(body.get("messages") or [])
    msgs = [{"role": "system", "content": own_system(mid) + DEPTH.get(body.get("mode", "chat"), DEPTH["chat"])}] + [dict(m) for m in raw_messages]
    attached = FILES.attachment_text(body.get("attachments"))
    if attached and msgs and msgs[-1].get("role") == "user":
        msgs[-1] = {"role": "user", "content": msgs[-1]["content"] + "\n\n" + attached}
    drafted = (lambda s: on_draft("", draft_clean(s).strip())) if on_draft else None
    text = stream_model(mid, msgs, TUNING["reply_tokens"], drafted).strip()
    asked = next((m["content"] for m in reversed(raw_messages) if m.get("role") == "user"), "")
    c = run_consensus(asked, {mid: text}, n) if text else None
    line = ((c or {}).get("lines") or {}).get(mid, "")
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
# The live wallpapers live in David's Cloudflare R2 bucket "collider-themes"; its Worker lists every object (name, kind,
# public URL, tags). Each wallpaper is numbered and titled in the bucket itself (Claude, 2026-10-17):
#   "007 Late Night on the Phone.mp4"   the wallpaper
#   "007 Late Night on the Phone.jpg"   its poster, beside it so the bucket shows it
#   "007 Late Night on the Phone.m4a"   its song, when it has one
# The number keeps the three together and sets the order; the app shows the title only.
_themes_cache = {"at": 0, "data": []}
_themes_lock = threading.Lock()
_NUMBERED = re.compile(r"^(\d{3}) (.+)\.([A-Za-z0-9]+)$")


def _get_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Collider"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


PACK_PRICE = "$4.99"      # shown until the store returns its own, local price
TRACKS_PER_PACK = 5


def _refresh_themes_bg():
    """Fetches the remote Cloudflare R2 theme manifest in the background and updates _themes_cache + disk cache."""
    cache = os.path.join(DATA, "themes_cache.json")
    try:
        listing = _get_json(CONFIG.get("themes") or ccfg.THEMES)
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


# The theme store's files come through Cloudflare's edge (collider-media), which tells every browser to keep them, so a
# wallpaper, live wallpaper or song is downloaded once and then played from the phone's or PC's own cache; the store's
# r2.dev address is kept by no cache. (Claude, 2026-10-21; David: "are we going to be doing any caching of these files")
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


# ---------------- Settings (Claude, 2026-10-20) ----------------
# Every line that decides how the app answers lives in data\collider_config.json beside the exe, shown in the launch
# window. The values below are only what a configuration starts with; from then on the file is what is read.
DEADLINE = {"chat": 100, "internet": 120, "research": 180, "deep": 240}
SILENCE = 45
SMARTGEN_PROMPT = 'Smart Gen holds projects, tasks, reminders, memories, and artifacts.\nCreates the item when the conversation already contains it, unless that item exists for the same project, type, and model. A timed reminder also lands on the calendar.\nWhen ongoing conversation modifies facts/dates of an existing task or project, Smart Gen automatically updates existing records rather than duplicating.\nArtifacts, reminders, tasks, projects, and memories can be bidirectionally attached and embedded in any combination.'
SMARTGEN_FORMAT = 'Reply with JSON only, in this shape, so the app can file it:\n{"create": [{"type": "project | task | reminder | memory | artifact", "title": "...", "content": "...", "due": "date and time, or empty", "project": "..."}],\n "update": [{"id": "an existing item\'s id", "title": "...", "content": "...", "due": "..."}]}\nThe existing items are listed with their ids. Empty lists when the conversation contains no item.'
# Every other number the server works by. These are the values it has always run on.
TUNING = {
    "thinking_tokens": 4000,
    "temperature": 0.4, "answer_timeout": 150, "retries": 2, "retry_wait": 1.5, "reply_tokens": 1400,
    "agent_answer_chars": 2200, "agent_tokens": 2500, "agent_backup_tokens": 9000, "agent_timeout": 110,
    "lines_tokens": 900, "lines_backup_tokens": 6000, "lines_timeout": 90, "line_min": 60, "line_max": 140,
    "essence_answer_chars": 3500, "essence_tokens": 200, "essence_timeout": 60,
    "plan_tokens": 400, "plan_backup_tokens": 3000, "plan_timeout": 60, "search_timeout": 40,
    "browser_search_depth": "basic", "browser_search_results": 10, "browser_search_timeout": 30,
    "attachments_max": 12, "history_kept": 200, "smartgen_kept": 100, "themes_refresh": 600,
    # read by code another session added in the old folder at 08:53 on 2026-10-20 without listing them here;
    # these are the values that code had before it was moved into the configuration
    "smartgen_backfill": 12, "search_fanout_min": 3, "search_fanout_factor": 2, "error_chars": 80,
    "draft_extra_chars": 8, "essence_short_line": 45, "essence_fallback_chars": 240, "smartgen_title_chars": 64,
    "report_words": 8,
}
SETTINGS = ("consensus_agent", "agent_chain", "agent_prompt", "plan_prompt", "models",
            "depth", "line_length", "search", "plan_queries", "source_chars", "max_tokens", "deadline",
            "silence", "tuning", "pack_price", "tracks_per_pack", "smartgen_prompt")


def own_system(mid):
    """A model's own instruction from the configuration, placed before the mode's instruction. Empty: none."""
    t = next((str(m.get("system") or "").strip() for m in ROSTER if m["id"] == mid), "")
    return t + "\n\n" if t else ""


def temperature_of(mid):
    """A model's own temperature from the configuration, or the general one."""
    v = next((m.get("temperature") for m in ROSTER if m["id"] == mid), None)
    try:
        return float(v) if v not in (None, "") else float(TUNING["temperature"])
    except (TypeError, ValueError):
        return float(TUNING["temperature"])


def settings_defaults():
    return {"consensus_agent": CONSENSUS_AGENT, "agent_chain": list(AGENT_CHAIN),
            "models": [{**m, "system": m.get("system", ""), "temperature": m.get("temperature", "")} for m in ROSTER[:_BUILT_IN]],
            "tuning": dict(TUNING),
            "depth": dict(DEPTH), "line_length": LINE_DEFAULT,
            "search": {k: list(v) for k, v in SEARCH.items()}, "max_tokens": dict(MAX_TOKENS), "deadline": dict(DEADLINE),
            "silence": SILENCE, "plan_queries": dict(PLAN_QUERIES), "plan_prompt": PLAN_PROMPT,
            "source_chars": dict(SOURCE_CHARS), "agent_prompt": AGENT_PROMPT,
            "smartgen_prompt": SMARTGEN_PROMPT,
            "pack_price": PACK_PRICE, "tracks_per_pack": TRACKS_PER_PACK, "imagine": dict(cimagine.DEFAULTS)}


def apply_settings(cfg):
    """Fills any missing line with its starting value, then makes the file's values the ones the server runs on.
    Returns True when a line was missing (the file is then saved complete)."""
    global CONSENSUS_AGENT, AGENT_CHAIN, DEPTH, LINE_DEFAULT, SEARCH, MAX_TOKENS, DEADLINE, SILENCE
    global AGENT_PROMPT, PACK_PRICE, TRACKS_PER_PACK, _BUILT_IN, PLAN_QUERIES, SOURCE_CHARS, PLAN_PROMPT
    global TUNING, SMARTGEN_PROMPT
    missing = False
    # Lines that are no longer used leave the file; instructions written before David's own words came in are replaced
    # by his (Claude, 2026-10-23).
    for gone in ("lines_prompt", "essence_prompt", "line_rule"):
        if cfg.pop(gone, None) is not None:
            missing = True
    if str(cfg.get("agent_prompt", "")).startswith("You are the Collider consensus agent"):
        cfg["agent_prompt"] = AGENT_PROMPT
        missing = True
    if str(cfg.get("smartgen_prompt", "")).startswith("From the finished multi-model conversation"):
        cfg["smartgen_prompt"] = SMARTGEN_PROMPT
        missing = True
    for k, v in settings_defaults().items():
        if k not in cfg:
            cfg[k] = v
            missing = True
    if int(cfg.get("line_length") or 0) < 60:
        cfg["line_length"] = 115
        missing = True
    CONSENSUS_AGENT = str(cfg["consensus_agent"]).strip()
    AGENT_CHAIN = [m for m in dict.fromkeys([CONSENSUS_AGENT] + [str(x).strip() for x in cfg["agent_chain"]]) if m]
    ROSTER[:] = [dict(m) for m in cfg["models"] if m.get("id")]
    _BUILT_IN = len(ROSTER)
    LABEL.clear()
    LABEL.update({m["id"]: m.get("label") or m["id"] for m in ROSTER})
    DEPTH, LINE_DEFAULT = dict(cfg["depth"]), int(cfg["line_length"])
    SEARCH = {k: (v[0], int(v[1])) for k, v in cfg["search"].items()}
    MAX_TOKENS = {k: int(v) for k, v in cfg["max_tokens"].items()}
    DEADLINE = {k: int(v) for k, v in cfg["deadline"].items()}
    SILENCE = int(cfg["silence"])
    PLAN_QUERIES = {k: int(v) for k, v in cfg["plan_queries"].items()}
    SOURCE_CHARS = {k: int(v) for k, v in cfg["source_chars"].items()}
    PLAN_PROMPT = str(cfg["plan_prompt"])
    SMARTGEN_PROMPT = str(cfg["smartgen_prompt"])
    for m in cfg["models"]:  # every model row shows its own instruction and temperature, empty until set
        if "system" not in m or "temperature" not in m:
            missing = True
        m.setdefault("system", "")
        m.setdefault("temperature", "")
    missing = missing or any(k not in cfg["tuning"] for k in TUNING)
    TUNING = {**TUNING, **cfg["tuning"]}
    if int(TUNING.get("line_max") or 0) < 115:
        TUNING["line_min"] = 60
        TUNING["line_max"] = 140
        missing = True
    if int(TUNING.get("smartgen_title_chars") or 0) < 48:
        TUNING["smartgen_title_chars"] = 64
        missing = True
    cfg["tuning"] = dict(TUNING)
    AGENT_PROMPT = str(cfg["agent_prompt"])
    PACK_PRICE, TRACKS_PER_PACK = str(cfg["pack_price"]), int(cfg["tracks_per_pack"])
    missing = missing or any(k not in cfg["imagine"] for k in cimagine.DEFAULTS)
    cfg["imagine"] = {**cimagine.DEFAULTS, **cfg["imagine"]}
    return missing


# ---------------- HTTP ----------------
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=WEB, **k)

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
        """Server-sent events: the whole state each time it changes, until it is done (Claude, 2026-10-19)."""
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
                except RuntimeError:  # changed while being read; the next look gets it
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
        """Asked on this computer itself (the app's own window, or a browser here)."""
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        return self.client_address[0] in ("127.0.0.1", "::1") and host in ("127.0.0.1", "localhost", "::1") \
            and not self.headers.get("Cf-Connecting-Ip")

    def _let_in(self):
        """Through the phone link only with its key: once in the address, then kept by the phone as a cookie."""
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
            return self._json({"bypass": bool(CONFIG.get("store_bypass", True))})
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
        if p == "/config":
            return self._config_page()
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
        """A preview picture of one file in Files (collider_thumbs); 404 when it has nothing of its own to show."""
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
        """Sound and video jump to a point in the file by asking for part of it."""
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
        # DuckDuckGo's script page meets the loader with a bot puzzle; its HTML page gives the same results.
        m = re.match(r"^https?://(?:www\.)?duckduckgo\.com/\?(.*)$", url)
        return "https://html.duckduckgo.com/html/?" + m.group(1) if m else url

    def _mobile(self):
        """The app says in a cookie when its window is phone-sized; sites are then asked for their phone pages."""
        return "collider_ua=mobile" in (self.headers.get("Cookie") or "")

    def _fetch(self, method="GET"):
        """Script requests made by a proxied page come through here so they are not blocked as cross-site."""
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0)) if method != "GET" else None
        try:
            code, _, headers, data = cfiles.fetch(self._target(), method, body, self.headers.get("Content-Type"), mobile=self._mobile())
            self._send(code or 200, headers.get("Content-Type") or "application/octet-stream", data)
        except Exception as e:
            self._send(502, "text/plain; charset=utf-8", str(e)[:200].encode())

    def _page(self, method="GET"):
        """In-app browser: fetch the page here so sites that refuse framing still render, keep links, forms
        and script requests inside the app, and save anything that is a file to Files > Downloaded."""
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
                # The search engine is asking for a puzzle; answer the search from the web-search key instead.
                q = cfiles.search_query(final, body)
                found = search_results(q) if q else []
                if found:
                    text = cfiles.results_page(q, found)
            html = cfiles.prepare_html(text, final.replace('"', "%22"))
            return self._send(200, "text/html; charset=utf-8", html.encode("utf-8"))
        self._send(200, ctype, data)

    def _config_page(self):
        """The configuration form, online (Claude, 2026-10-23): the same page as the launch window, without the host."""
        from collider_form import FORM
        provs = CONFIG.get("providers", [])
        initial = {"host": "", "providers": provs, "themes": CONFIG.get("themes") or ccfg.THEMES,
                   "bypass": bool(CONFIG.get("store_bypass", True)),
                   "uses": [uses(r) if (r.get("key") or "").strip() else "Not read: no key" for r in provs],
                   "settings": {k: CONFIG[k] for k in SETTINGS if k in CONFIG}}
        html = FORM.replace("WHERE", json.dumps(ccfg.path(DATA))).replace("INITIAL", json.dumps(initial))
        return self._send(200, "text/html; charset=utf-8", html.encode("utf-8"))

    def _config_save(self, b):
        """Saves the form and runs on it at once."""
        cfg = dict(CONFIG)
        cfg["providers"] = [r for r in b.get("providers", []) if any((r.get(k) or "").strip() for k in ("name", "endpoint", "key"))]
        cfg["themes"] = (b.get("themes") or "").strip() or ccfg.THEMES
        cfg["store_bypass"] = bool(b.get("bypass", True))
        cfg.update(b.get("settings") or {})
        ccfg.save(DATA, cfg)
        CONFIG.clear()
        CONFIG.update(cfg)
        apply_settings(CONFIG)
        _extend_roster()
        return {"ok": True}

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
            if p == "/api/lines":
                return self._json(ensure_lines(self._body()))
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
                # Windows' own app picker for a file in Files; only from this computer's own window.
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
    """Run from the project folder without the launch window: the saved configuration and host number, or a free one."""
    import socket
    cfg = ccfg.load(DATA)
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", int(cfg.get("host") or 0)))
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

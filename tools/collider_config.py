# E.D. — Collider — Signed: Gemini 4 Argon (2026-10-24)
"""Collider's configuration and API Keys Catalog loader.

One file, data\\collider_config.json beside Collider.exe, holds everything the app needs before it can work.
Every key name in data\\collider_config.json is self-explanatory, unit-explicit (seconds, tokens, max_chars, attempts),
and grouped by functional scope so no external lookup or scrolling up-and-down is ever needed.

All API keys in C:\\Users\\D\\Documents\\00_Config_and_Secrets\\API KEYS.txt are parsed into a sorted, categorized
selector catalog so the Launch Configurator can pick any provider/model-key line item immediately.
"""
import json
import os
import re

KEYS_FILE = r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt"
NVIDIA_CHAT = "https://integrate.api.nvidia.com/v1/chat/completions"
TAVILY_SEARCH = "https://api.tavily.com/search"
GROQ_SPEECH = "https://api.groq.com/openai/v1/audio/transcriptions"
SPEECH_MODEL = "whisper-large-v3-turbo"
FAL_QUEUE = "https://queue.fal.run"
CF_IMAGINE = "https://collider-imagine.ebridavid.workers.dev"
CF_PHONE = "https://collider-phone.ebridavid.workers.dev"
THEMES = "https://collider-themes.ebridavid.workers.dev/"


def path(data_dir):
    return os.path.join(data_dir, "collider_config.json")


def mask_key(k):
    k = (k or "").strip()
    if len(k) <= 10:
        return k
    return f"{k[:6]}...{k[-4:]}"


def purpose_for_row(row):
    """Human-readable summary of what this provider entry powers inside Collider."""
    if is_speech(row):
        return "Voice Chat Speech-to-Text: transcribes microphone audio via Groq Whisper (/api/transcribe)"
    if is_fal(row):
        return "Discover Market 2K Image Generation: runs xAI Grok Imagine 2K via fal.ai queue (/api/imagine)"
    if is_phone(row):
        return "Permanent Mobile Tunnel: routes your permanent Cloudflare phone URL to this PC (Settings > Account)"
    if is_pictures(row):
        return "Discover Market Free Daily Image Generation: runs FLUX.2 Klein 4B / Dev / Schnell on Cloudflare Workers AI (/api/imagine)"
    if is_search(row):
        return "Live Web Search: fetches cited web sources for Internet, Research, Deep Research (/api/ask) and In-App Browser (/api/page)"
    name = (row.get("provider_name") or row.get("name") or "LLM Provider").strip()
    ep = (row.get("api_endpoint_url") or row.get("endpoint") or "").strip()
    models = (row.get("extra_model_ids") or row.get("models") or "").strip()
    if "integrate.api.nvidia.com" in ep.lower() or name.lower() == "nvidia":
        extra = f" + custom models ({models})" if models else ""
        return f"Ticker Response Models & Consensus/Smart Gen Judges via NVIDIA Integrate + NVIDIA FLUX.1 Dev images{extra}"
    if models:
        return f"Ticker Response Models & Replies via {name} ({ep}) — Models: {models}"
    return f"Ticker Response Models & Replies via {name} ({ep})"


def normalize_provider_row(r):
    """Converts either legacy {name, endpoint, key, models} or descriptive provider dict into canonical descriptive shape."""
    name = (r.get("provider_name") or r.get("name") or "").strip()
    endpoint = (r.get("api_endpoint_url") or r.get("endpoint") or "").strip()
    key = (r.get("api_key") or r.get("key") or "").strip()
    models = (r.get("extra_model_ids") or r.get("models") or "").strip()
    row = {
        "provider_name": name,
        "purpose_in_app": "",
        "api_endpoint_url": endpoint,
        "api_key": key,
        "extra_model_ids": models,
    }
    row["purpose_in_app"] = purpose_for_row(row)
    return row


def key_catalog(existing_providers=None):
    """Parses C:\\Users\\D\\Documents\\00_Config_and_Secrets\\API KEYS.txt (plus any active config keys)
    into a sorted, categorized list of selectable Model-Key items for the Launch Configurator."""
    text = ""
    if os.path.exists(KEYS_FILE):
        try:
            text = open(KEYS_FILE, encoding="utf-8", errors="ignore").read()
        except Exception:
            text = ""

    items = []
    seen_keys = set()

    def add_item(category, label, provider_name, endpoint, key, models, consequence):
        k = (key or "").strip()
        if not k or k in seen_keys:
            return
        seen_keys.add(k)
        items.append({
            "id": f"{provider_name}:{k[:10]}:{len(items)}",
            "category": category,
            "label": f"{label} ({mask_key(k)})",
            "provider_name": provider_name,
            "api_endpoint_url": endpoint,
            "api_key": k,
            "extra_model_ids": models,
            "consequence": consequence,
        })

    # 1. NVIDIA Integrate keys (nvapi-...)
    nv_keys = list(dict.fromkeys(re.findall(r"nvapi-[A-Za-z0-9_\-]+", text)))
    nv_labels = [
        ("NVIDIA Integrate — Studio Voice & Roster Key 1", ""),
        ("NVIDIA Integrate — MiniMax M3 & Roster Key 2", "minimaxai/minimax-m3"),
        ("NVIDIA Integrate — Roster Key 3 (Load-Balanced Round-Robin)", ""),
    ]
    for idx, k in enumerate(nv_keys):
        lbl, m = nv_labels[idx] if idx < len(nv_labels) else (f"NVIDIA Integrate — API Key #{idx + 1}", "")
        add_item(
            "1. Ticker & Judge LLMs — NVIDIA Integrate",
            lbl,
            "NVIDIA",
            NVIDIA_CHAT,
            k,
            m,
            "Powers all 11 built-in Ticker Response Models, Consensus/Smart Gen Judges, and NVIDIA FLUX.1 Dev image generation (round-robin load balanced).",
        )

    # 2. OpenCode Zen keys
    for m_oc in re.finditer(r"oc_sk_[A-Za-z0-9_\-]+", text):
        add_item(
            "2. Ticker & Judge LLMs — OpenCode Zen",
            "OpenCode Go / Zen EDE — Multi-Model Key",
            "OpenCode Zen",
            "https://opencode.ai/zen/v1/chat/completions",
            m_oc.group(0),
            "opencode/gpt-5.6-luna, deepseek-v4-flash, qwen3.5-plus, minimax-m3, nemotron-3.5-lightning-free, nemotron-3-ultra-free",
            "Routes OpenCode Zen models (GPT-5.6 Luna, DeepSeek V4 Flash, Qwen 3.5 Plus, MiniMax M3) into the Ticker.",
        )
    for m_zak in re.finditer(r"zak_live_[A-Za-z0-9_\-]+", text):
        add_item(
            "2. Ticker & Judge LLMs — OpenCode Zen",
            "ZenCode Live — GPT-5.6 Luna & Free Roster Key",
            "OpenCode Zen",
            "https://opencode.ai/zen/v1/chat/completions",
            m_zak.group(0),
            "opencode/gpt-5.6-luna, deepseek-v4-flash, mimo-v2.5-free, opencode/deepseek-v4-flash-free, longcat-2.0-free",
            "Routes ZenCode Live models (GPT-5.6 Luna, DeepSeek V4 Flash, Mimo v2.5, Longcat 2.0) into the Ticker.",
        )
    oc_sk_Matches = [
        ("sk-IicsqiJkchfYdLcMqqv0N0UDmYfTQLUFPQMcP7dXdyYD8sUXvvWrrUpQv2S1Sh7b", "OpenCode AI — Primary Zen Key"),
        ("sk-JfnObQ4fQoJrtw7jgs9mWcN67JY9moCbRZhYvbHi1IEQ1ojchKy2TLLKgko4q2Dl", "OpenCode Zen — Pharcyde Key"),
        ("sk-QCWVJkXb94A4ahhLrk08ALtNs87J828uvdZEI1xeFjDFSWUe2DjU3ceVtsR20KB7", "OpenCode Zen — Secondary Key"),
    ]
    for raw_k, lbl in oc_sk_Matches:
        if raw_k in text:
            add_item(
                "2. Ticker & Judge LLMs — OpenCode Zen",
                lbl,
                "OpenCode Zen",
                "https://opencode.ai/zen/v1/chat/completions",
                raw_k,
                "opencode/gpt-5.6-luna, deepseek-v4-flash, qwen3.5-plus, minimax-m3",
                "Routes OpenCode Zen models (GPT-5.6 Luna, DeepSeek V4 Flash, Qwen 3.5 Plus, MiniMax M3) into the Ticker.",
            )

    # 3. OpenRouter keys (sk-or-v1-...)
    or_keys = list(dict.fromkeys(re.findall(r"sk-or-v1-[A-Za-z0-9_\-]+", text)))
    or_labels = [
        "OpenRouter — Primary Gateway Key",
        "OpenRouter — Live Production Key",
        "OpenRouter — Backup Gateway Key",
    ]
    for idx, k in enumerate(or_keys):
        lbl = or_labels[idx] if idx < len(or_labels) else f"OpenRouter — Gateway Key #{idx + 1}"
        add_item(
            "3. Ticker & Judge LLMs — OpenRouter & Gateways",
            lbl,
            "OpenRouter",
            "https://openrouter.ai/api/v1/chat/completions",
            k,
            "anthropic/claude-3.7-sonnet, google/gemini-2.5-pro, openai/gpt-4.1, deepseek/deepseek-r1",
            "Adds frontier models (Claude 3.7 Sonnet, Gemini 2.5 Pro, GPT-4.1, DeepSeek R1) via OpenRouter.",
        )

    # 4. Direct Frontier Providers (xAI Grok, OpenAI, Gemini, Kimi, MiniMax, Cohere)
    for k in dict.fromkeys(re.findall(r"xai-[A-Za-z0-9_\-]+", text)):
        add_item(
            "4. Ticker & Judge LLMs — Direct Providers (Grok, OpenAI, Gemini, Kimi, MiniMax, Cohere)",
            "xAI Grok — Direct API Key",
            "xAI",
            "https://api.x.ai/v1/chat/completions",
            k,
            "grok-3, grok-3-mini",
            "Adds xAI Grok-3 and Grok-3 Mini directly to the Ticker roster.",
        )
    for k in dict.fromkeys(re.findall(r"sk-proj-[A-Za-z0-9_\-]+", text)):
        add_item(
            "4. Ticker & Judge LLMs — Direct Providers (Grok, OpenAI, Gemini, Kimi, MiniMax, Cohere)",
            "OpenAI — Direct Project Key",
            "OpenAI",
            "https://api.openai.com/v1/chat/completions",
            k,
            "gpt-4.1, gpt-4o, o3-mini",
            "Adds OpenAI GPT-4.1, GPT-4o, and o3-mini directly to the Ticker roster.",
        )
    gem_keys = list(dict.fromkeys(re.findall(r"AQ\.[A-Za-z0-9_\-]+", text)))
    gem_labels = [
        "Google Gemini — Primary API Key (ebridavidebri)",
        "Google Gemini — Secondary API Key",
        "Google Gemini — Stitch API Key",
    ]
    for idx, k in enumerate(gem_keys):
        lbl = gem_labels[idx] if idx < len(gem_labels) else f"Google Gemini — API Key #{idx + 1}"
        add_item(
            "4. Ticker & Judge LLMs — Direct Providers (Grok, OpenAI, Gemini, Kimi, MiniMax, Cohere)",
            lbl,
            "Google Gemini",
            "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            k,
            "gemini-2.5-pro, gemini-2.5-flash",
            "Adds Google Gemini 2.5 Pro and 2.5 Flash directly to the Ticker roster.",
        )
    if "sk-4jPuP4akw9hoonhfJKT7bGdazn21w0wBvo1ggv5WFXbz29wH" in text:
        add_item(
            "4. Ticker & Judge LLMs — Direct Providers (Grok, OpenAI, Gemini, Kimi, MiniMax, Cohere)",
            "Kimi (Moonshot AI) — Direct API Key",
            "Kimi",
            "https://api.moonshot.cn/v1/chat/completions",
            "sk-4jPuP4akw9hoonhfJKT7bGdazn21w0wBvo1ggv5WFXbz29wH",
            "moonshot-v1-128k",
            "Adds Kimi Moonshot 128K long-context model to the Ticker roster.",
        )
    for k in dict.fromkeys(re.findall(r"sk-api-[A-Za-z0-9_\-]+", text)):
        add_item(
            "4. Ticker & Judge LLMs — Direct Providers (Grok, OpenAI, Gemini, Kimi, MiniMax, Cohere)",
            "MiniMax — M3 OEM Direct Key",
            "MiniMax",
            "https://api.minimax.chat/v1/text/chatcompletion_v2",
            k,
            "MiniMax-Text-01",
            "Adds MiniMax-Text-01 / M3 OEM directly to the Ticker roster.",
        )
    cohere_keys = list(dict.fromkeys(re.findall(r"cohere_[A-Za-z0-9_\-]+", text)))
    for idx, k in enumerate(cohere_keys):
        lbl = "Cohere — Default API Key" if idx == 0 else "Cohere — Production API Key"
        add_item(
            "4. Ticker & Judge LLMs — Direct Providers (Grok, OpenAI, Gemini, Kimi, MiniMax, Cohere)",
            lbl,
            "Cohere",
            "https://api.cohere.com/v2/chat",
            k,
            "command-a-03-2025, command-r-plus",
            "Adds Cohere Command-A and Command-R+ models.",
        )

    # 5. AI Hub Mix, Crazyrouter, Hugging Face, Vercel AI Gateway, Ollama
    ahm_keys = [
        ("sk-C4yqXbdCMpYBm3zmE203Af213c224303Af5a348cCe25C536", "AI Hub Mix — Key 1"),
        ("sk-7wMOIcag2XSjWRxx809e956c040e4561A65b4cD1Cd8bDf8f", "AI Hub Mix — Key 2 (ebridavid@gmail)"),
        ("sk-pAxbebdkMvWzxRadFe65B15675Ce4584A268137d41214795", "AI Hub Mix — Key 3"),
    ]
    for raw_k, lbl in ahm_keys:
        if raw_k in text:
            add_item(
                "3. Ticker & Judge LLMs — OpenRouter & Gateways",
                lbl,
                "AI Hub Mix",
                "https://aihubmix.com/v1/chat/completions",
                raw_k,
                "gpt-4o, claude-3-7-sonnet-20250219, deepseek-chat",
                "Routes OpenAI, Claude, and DeepSeek models through AI Hub Mix.",
            )
    if "sk-pm0H6kks2wssFlxnDkEqrGEDqURxx08OhnO1GrLbkXY79B2I" in text:
        add_item(
            "3. Ticker & Judge LLMs — OpenRouter & Gateways",
            "Crazyrouter — OpenAI-Compatible Router Key",
            "Crazyrouter",
            "https://cn.crazyrouter.com/v1/chat/completions",
            "sk-pm0H6kks2wssFlxnDkEqrGEDqURxx08OhnO1GrLbkXY79B2I",
            "gpt-4.1, claude-3-7-sonnet, deepseek-r1",
            "Routes OpenAI/Claude/DeepSeek models through Crazyrouter (https://cn.crazyrouter.com/v1).",
        )
    for k in dict.fromkeys(re.findall(r"hf_[A-Za-z0-9]+", text)):
        add_item(
            "3. Ticker & Judge LLMs — OpenRouter & Gateways",
            "Hugging Face — Inference Router Token",
            "HuggingFace",
            "https://router.huggingface.co/v1/chat/completions",
            k,
            "meta-llama/Llama-3.3-70B-Instruct, Qwen/Qwen2.5-72B-Instruct",
            "Routes open-weight Hugging Face Inference models into the Ticker.",
        )
    for k in dict.fromkeys(re.findall(r"vck_[A-Za-z0-9_\-]+", text)):
        add_item(
            "3. Ticker & Judge LLMs — OpenRouter & Gateways",
            "Vercel AI Gateway — Token",
            "Vercel Gateway",
            "https://ai-gateway.vercel.sh/v1/chat/completions",
            k,
            "openai/gpt-4.1, anthropic/claude-3.7-sonnet",
            "Routes LLM calls through Vercel AI Gateway.",
        )

    # 6. Discover Market Image Generation (Cloudflare Workers AI & fal.ai)
    add_item(
        "5. Discover Market — Image Generation (Cloudflare & fal.ai)",
        "Cloudflare Workers AI — Quorum Imagine Worker (Free Daily FLUX.2)",
        "Cloudflare",
        CF_IMAGINE,
        "EcBT7LWQz3RcZABqn9CqXBlQNvFDMDA2tAbuKBcvfP4",
        "@cf/black-forest-labs/flux-2-klein-4b, @cf/black-forest-labs/flux-2-dev, @cf/black-forest-labs/flux-1-schnell",
        "Generates up to 2048px images in Discover Market for free each day via FLUX.2 Klein 4B / Dev / Schnell.",
    )
    for k in dict.fromkeys(re.findall(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}:[0-9a-fA-F]{32}\b", text)):
        add_item(
            "5. Discover Market — Image Generation (Cloudflare & fal.ai)",
            "fal.ai Queue — Grok Imagine 2K Image Key",
            "fal",
            FAL_QUEUE,
            k,
            "",
            "Generates 2K high-resolution images in Discover Market via fal.ai queue ($0.08/image at 2K medium).",
        )

    # 7. Web Search (Tavily) & Voice Speech-to-Text (Groq Whisper)
    for k in dict.fromkeys(re.findall(r"tvly-[A-Za-z0-9_\-]+", text)):
        add_item(
            "6. Web Search & Voice Transcription (Tavily & Groq Whisper)",
            "Tavily Web Search — Cited Sources & Browser Search Key",
            "Tavily",
            TAVILY_SEARCH,
            k,
            "",
            "Fetches live web sources for Internet, Research, and Deep Research modes and In-App Browser search.",
        )
    gsk_keys = list(dict.fromkeys(re.findall(r"gsk_[A-Za-z0-9]+", text)))
    for idx, k in enumerate(gsk_keys):
        add_item(
            "6. Web Search & Voice Transcription (Tavily & Groq Whisper)",
            f"Groq Whisper — Voice Speech-to-Text Key #{idx + 1}",
            "Groq",
            GROQ_SPEECH,
            k,
            SPEECH_MODEL,
            "Transcribes microphone voice input into text via whisper-large-v3-turbo.",
        )

    # 8. Permanent Phone Link Tunnel
    add_item(
        "7. Remote Phone Access Tunnel (Cloudflare Worker)",
        "Quorum Phone Worker — Permanent Mobile URL Key",
        "Phone",
        CF_PHONE,
        "fF6fWTmdXwsu-iZGuNXTRL2A",
        "",
        "Authenticates your permanent phone link (https://collider-phone.ebridavid.workers.dev/fF6fWTmdXwsu-iZGuNXTRL2A).",
    )

    # Include any custom keys currently in existing_providers that weren't in API KEYS.txt
    for r in existing_providers or []:
        nr = normalize_provider_row(r)
        if nr["api_key"]:
            add_item(
                "8. Custom Configured Keys",
                f"{nr['provider_name'] or 'Custom'} — Configured Key",
                nr["provider_name"] or "Custom",
                nr["api_endpoint_url"],
                nr["api_key"],
                nr["extra_model_ids"],
                nr["purpose_in_app"],
            )

    return items


def _first_run():
    text = ""
    if os.path.exists(KEYS_FILE):
        text = open(KEYS_FILE, encoding="utf-8", errors="ignore").read()
    rows = [normalize_provider_row({"name": "NVIDIA", "endpoint": NVIDIA_CHAT, "key": k, "models": ""})
            for k in dict.fromkeys(re.findall(r"nvapi-[A-Za-z0-9_\-]+", text))]
    for k in dict.fromkeys(re.findall(r"tvly-[A-Za-z0-9_\-]+", text)):
        rows.append(normalize_provider_row({"name": "Tavily", "endpoint": TAVILY_SEARCH, "key": k, "models": ""}))
    rows.append(normalize_provider_row({
        "name": "Cloudflare",
        "endpoint": CF_IMAGINE,
        "key": "EcBT7LWQz3RcZABqn9CqXBlQNvFDMDA2tAbuKBcvfP4",
        "models": "@cf/black-forest-labs/flux-2-klein-4b, @cf/black-forest-labs/flux-2-dev, @cf/black-forest-labs/flux-1-schnell",
    }))
    rows.append(normalize_provider_row({
        "name": "Phone",
        "endpoint": CF_PHONE,
        "key": "fF6fWTmdXwsu-iZGuNXTRL2A",
        "models": "",
    }))
    rows += _speech_rows(text)
    rows += _fal_rows(text)
    if not rows:
        rows.append(normalize_provider_row({"name": "NVIDIA", "endpoint": NVIDIA_CHAT, "key": "", "models": ""}))
    return {"localhost_port": None, "api_providers_and_keys": rows}


def load(data_dir):
    p = path(data_dir)
    if os.path.exists(p):
        try:
            cfg = json.load(open(p, encoding="utf-8"))
            raw_provs = cfg.get("api_providers_and_keys") if "api_providers_and_keys" in cfg else cfg.get("providers", [])
            provs = [normalize_provider_row(r) for r in raw_provs]
            if not any(is_speech(r) for r in provs) and os.path.exists(KEYS_FILE):
                provs += _speech_rows(open(KEYS_FILE, encoding="utf-8", errors="ignore").read())
            if not any(is_fal(r) for r in provs) and os.path.exists(KEYS_FILE):
                provs += _fal_rows(open(KEYS_FILE, encoding="utf-8", errors="ignore").read())
            cfg["api_providers_and_keys"] = provs
            cfg.pop("providers", None)
            cfg.pop("theme_names", None)
            return cfg
        except Exception:
            pass
    return _first_run()


def save(data_dir, cfg):
    os.makedirs(data_dir, exist_ok=True)
    p = path(data_dir)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def _speech_rows(text):
    return [normalize_provider_row({"name": "Groq", "endpoint": GROQ_SPEECH, "key": k, "models": SPEECH_MODEL})
            for k in dict.fromkeys(re.findall(r"gsk_[A-Za-z0-9]+", text))]


def _fal_rows(text):
    return [normalize_provider_row({"name": "fal", "endpoint": FAL_QUEUE, "key": k, "models": ""})
            for k in dict.fromkeys(re.findall(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}:[0-9a-fA-F]{32}\b", text))]


def _ep(row):
    return (row.get("api_endpoint_url") or row.get("endpoint") or "").lower()


def _nm(row):
    return (row.get("provider_name") or row.get("name") or "").lower()


def is_pictures(row):
    """Collider's own picture Worker on Cloudflare (dev/cf_imagine)."""
    return "collider-imagine" in _ep(row)


def is_phone(row):
    """The phone link's Worker (dev/cf_phone)."""
    return "collider-phone" in _ep(row)


def is_fal(row):
    return "fal.run" in _ep(row)


def is_speech(row):
    return "audio/transcriptions" in _ep(row)


def is_search(row):
    return "tavily" in _ep(row) or _nm(row) == "tavily"


def models_of(row):
    raw = row.get("extra_model_ids") if "extra_model_ids" in row else row.get("models")
    return [m.strip() for m in (raw or "").split(",") if m.strip()]

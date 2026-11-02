# Made by Claude (2026-10-21). Round 12: thinking on, always.
# David, 21 Oct: "What is detailed thinking off? ... Why should anyone turn off thinking? ... It's mandatory".
# Claude had written "detailed thinking off" into its own three instructions (planning, consensus, one line) for speed.
# Measured today (dev/probe_thinking.py): Gemma 4 31B, the consensus agent, thinks only when asked through
# chat_template_kwargs; the others think by default; every model accepts the request. The thinking comes back in its
# own field (reasoning_content), apart from the answer, so it never reaches an answer or a line. The fallback that
# took the last paragraph of the thinking as an answer when the answer was empty is removed; the thinking gets its own
# token allowance instead (tuning: thinking_tokens), so the answer is not crowded out.
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for: {old[:80]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("tools/collider_server.py", [
    ('PLAN_PROMPT = ("detailed thinking off\\nSplit the question', 'PLAN_PROMPT = ("Split the question'),
    ('AGENT_PROMPT = """detailed thinking off\n', 'AGENT_PROMPT = """'),
    ('LINES_PROMPT = """detailed thinking off\n', 'LINES_PROMPT = """'),
    ('''            r = post_json(row["endpoint"], {"model": model, "messages": clean_msgs, "max_tokens": max_tokens, "temperature": temperature_of(model)},''',
     '''            r = post_json(row["endpoint"], {"model": model, "messages": clean_msgs, "max_tokens": max_tokens + TUNING["thinking_tokens"],
                                            "temperature": temperature_of(model), "chat_template_kwargs": THINK},'''),
    ('''            text = sanitize_model_output(msg.get("content") or "")
            if not text:
                raw_reasoning = sanitize_model_output(msg.get("reasoning_content") or "")
                if raw_reasoning and "{" in raw_reasoning and "}" in raw_reasoning:
                    text = raw_reasoning
                elif raw_reasoning:
                    paras = [p.strip() for p in raw_reasoning.split("\\n\\n") if p.strip()]
                    text = paras[-1] if paras else ""
            if text:''',
     '''            text = sanitize_model_output(msg.get("content") or "")  # the answer only; the thinking stays out
            if text:'''),
    ('''    payload = {"model": model, "messages": _sanitize_messages(messages), "max_tokens": max_tokens, "temperature": temperature_of(model), "stream": True}''',
     '''    payload = {"model": model, "messages": _sanitize_messages(messages), "max_tokens": max_tokens + TUNING["thinking_tokens"],
               "temperature": temperature_of(model), "stream": True, "chat_template_kwargs": THINK}'''),
    ('''def call_model(model, messages, max_tokens, timeout=None):''',
     '''# Every model is asked to think (Claude, 2026-10-21; David: thinking is "mandatory").
THINK = {"enable_thinking": True, "thinking": True}


def call_model(model, messages, max_tokens, timeout=None):'''),
    ('''TUNING = {
    "temperature": 0.4,''', '''TUNING = {
    "thinking_tokens": 4000,
    "temperature": 0.4,'''),
])

# The saved configuration holds its own copies of the three instructions: the line goes from them too.
for rel in ("data/collider_config.json", "dev/test_app/data/collider_config.json"):
    p = ROOT / rel
    if not p.exists():
        continue
    cfg = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for k in ("agent_prompt", "lines_prompt", "plan_prompt"):
        v = cfg.get(k)
        if isinstance(v, str) and v.startswith("detailed thinking off\n"):
            cfg[k] = v[len("detailed thinking off\n"):]
            n += 1
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    tmp.replace(p)
    print("config", rel, "lines removed:", n)

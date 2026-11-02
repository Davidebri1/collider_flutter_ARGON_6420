# Made by Claude (2026-10-23). Round 33. David: "both of the consensus agents should have accessible prompts in the
# config. and smart gen agent".
#  - Smart Gen gets an agent: the consensus agent writes each card from the finished conversation, by its own
#    instruction, smartgen_prompt, which is in the configuration and the form beside the other agents' instructions.
#  - The configuration form also opens online at <address>/config (behind the same key as the app), since Collider
#    online reads its own copy of the configuration; Save applies it at once.
#  - Code that deleted Smart Gen cards on its own (by a list of "trivial" questions and one card's title) is removed:
#    nothing the user made is removed except by the user.
import re

T = "tools/"


def rd(p):
    return open(T + p, encoding="utf-8").read()


def wr(p, s):
    open(T + p, "w", encoding="utf-8").write(s)


def one(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90])
    return s.replace(a, b)


# ---------- the form, shared by the launch window and the online page ----------
app = rd("collider_app.py")
if "from collider_form import FORM" not in app:
    a = app.index('FORM = r"""')
    b = app.index('"""', a + len('FORM = r"""')) + 3
    form = app[a:b]
    app = app[:a] + "from collider_form import FORM  # noqa: E402  (the form is shared with Collider online's /config page)" + app[b:]
    wr("collider_app.py", app)
    wr("collider_form.py", "# Made by Claude. The configuration form: the launch window's page on the PC, and <address>/config online\n"
                           "# (Claude, 2026-10-23: moved here from collider_app.py so Collider online can show it too).\n" + form + "\n")
f = rd("collider_form.py")
f = one(f, "lines_prompt:'One-line agent instruction',", "lines_prompt:'One-line agent instruction',smartgen_prompt:'Smart Gen agent instruction',")
f = one(f, "['consensus_agent','agent_chain','agent_prompt','lines_prompt','essence_prompt','plan_prompt','models']",
        "['consensus_agent','agent_chain','agent_prompt','lines_prompt','essence_prompt','plan_prompt','smartgen_prompt','models']")
f = one(f, "H.value=C.host;", "H.value=C.host;if(!C.host){document.querySelector('.host').style.display='none';document.querySelector('.go').textContent='Save';}")
f = one(f, "document.getElementById('f').onsubmit=async e=>{e.preventDefault();if(busy||!window.pywebview)return;busy=true;",
        """document.getElementById('f').onsubmit=async e=>{e.preventDefault();if(busy)return;
if(!window.pywebview){busy=true;const g=document.querySelector('.go');try{const r=await fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({providers:rows,themes:document.getElementById('themes').value,bypass:document.getElementById('bypass').checked,settings:S})});g.textContent=r.ok?'Saved':'Save';setTimeout(()=>{g.textContent='Save';},1600);}finally{busy=false;}return;}
busy=true;""")
wr("collider_form.py", f)

# ---------- the server ----------
s = rd("collider_server.py")
s = one(s, """ESSENCE_PROMPT = ("Reduce the answer below""", """SMARTGEN_PROMPT = \"\"\"From the finished multi-model conversation below, write one Smart Gen card.
title: what was settled, in at most {n} characters.
content: the consensus, then any dissent, in plain words.
Return ONLY JSON: {"title": "...", "content": "..."}\"\"\"
ESSENCE_PROMPT = ("Reduce the answer below""")
s = one(s, """            "silence", "tuning", "pack_price", "tracks_per_pack")""",
        """            "silence", "tuning", "pack_price", "tracks_per_pack", "smartgen_prompt")""")
s = one(s, """"source_chars": dict(SOURCE_CHARS), "agent_prompt": AGENT_PROMPT, "lines_prompt": LINES_PROMPT,""",
        """"source_chars": dict(SOURCE_CHARS), "agent_prompt": AGENT_PROMPT, "lines_prompt": LINES_PROMPT,
            "smartgen_prompt": SMARTGEN_PROMPT,""")
s = one(s, """    global ESSENCE_PROMPT, TUNING
""", """    global ESSENCE_PROMPT, TUNING, SMARTGEN_PROMPT
""")
s = one(s, """    ESSENCE_PROMPT = str(cfg["essence_prompt"])
""", """    ESSENCE_PROMPT = str(cfg["essence_prompt"])
    SMARTGEN_PROMPT = str(cfg["smartgen_prompt"])
""")

# no card removed by the app
a = s.index("    def _is_trivial_prompt(p_str):")
b = s.index("    if not _smartgen_mem and _history_mem:")
s = s[:a] + s[b:]
s = one(s, """        for sess in reversed(_history_mem[:TUNING["smartgen_backfill"]]):
            if not _is_trivial_prompt(sess.get("prompt")):
                _extract_smartgen_card(sess, save=False)""", """        for sess in reversed(_history_mem[:TUNING["smartgen_backfill"]]):
            _extract_smartgen_card(sess, save=False)""")
s = one(s, """    if prompt_text.lower().rstrip("?.!") in ("who are you", "what is 2+2", "what is 2 + 2", "hi", "hello", "test"):
        return
""", "")

# the Smart Gen agent
s = one(s, """def save_session(job):""", '''def _smartgen_agent(job, card_id):
    """The Smart Gen agent (Claude, 2026-10-23): the consensus agent writes the card by SMARTGEN_PROMPT, which is in the
    configuration. Until it has, or if it cannot, the card keeps what was made from the consensus directly."""
    cons, results = job.get("consensus") or {}, job.get("results") or {}
    each = "\\n".join(f"- {LABEL.get(m, m)}: {r.get('essence') or ''}" for m, r in results.items() if r.get("essence"))
    user = (f"Question:\\n{job.get('prompt') or ''}\\n\\nConsensus ({cons.get('score') or ''}):\\n{cons.get('summary') or ''}"
            f"\\n\\nDissent:\\n" + "\\n".join(str(d) for d in (cons.get("dissent") or [])) + f"\\n\\nEach model:\\n{each}")
    n = TUNING["smartgen_title_chars"]
    msgs = [{"role": "system", "content": SMARTGEN_PROMPT.replace("{n}", str(n))}, {"role": "user", "content": user}]
    for agent in AGENT_CHAIN:
        try:
            raw = call_model(agent, msgs, TUNING["agent_tokens"], timeout=TUNING["agent_timeout"])
            m = re.search(r"\\{.*\\}", re.sub(r"```(?:json)?", "", raw), flags=re.S)
            out = json.loads(m.group(0)) if m else {}
            title, content = str(out.get("title") or "").strip(), str(out.get("content") or "").strip()
            if not (title or content):
                continue
            for c in _smartgen_mem or []:
                if c.get("id") == card_id:
                    if title:
                        c["title"] = fit_words(title, n)
                    if content:
                        c["content"] = content
            _save_smartgen()
            return
        except Exception as e:
            print("smartgen agent failed", agent, e)


def save_session(job):''')
s = one(s, """    _smartgen_mem = [c for c in _smartgen_mem if c.get("id") != card["id"]]
    _smartgen_mem.insert(0, card)
    if save:
        _save_smartgen()""", """    _smartgen_mem = [c for c in _smartgen_mem if c.get("id") != card["id"]]
    _smartgen_mem.insert(0, card)
    if save:
        _save_smartgen()
        threading.Thread(target=_smartgen_agent, args=(job, card["id"]), daemon=True).start()""")

# the form online
s = one(s, """        if p == "/api/page":
            return self._page()""", """        if p == "/config":
            return self._config_page()
        if p == "/api/page":
            return self._page()""")
s = one(s, """            if p == "/api/ask":
                job = new_job(self._body())""", """            if p == "/api/config":
                return self._json(self._config_save(self._body()))
            if p == "/api/ask":
                job = new_job(self._body())""")
s = one(s, """    def do_HEAD(self):""", '''    def _config_page(self):
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

    def do_HEAD(self):''')
wr("collider_server.py", s)
print("round 33 applied")

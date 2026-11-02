# Made by Claude (2026-10-23). Round 34: the agents in David's words.
# David: "essence instruction? that didnt come from me or my spec ... one line agent also not my language. i also said
# this was the consensus agent's responsibility. double check the consensus agent file."
#  - The consensus agent's instruction is now David's "Consensus Agent.md" (Google Drive), word for word, with only a
#    short note after it saying how to hand the result to the app. It gives the consensus ratio, the consensus summary,
#    each response's sentiment (the ticker's summary for that response) and the logical chain length table.
#  - The essence instruction, the one-line agent and the "begin your reply with a summary line" rule are gone: those
#    were not his, and the summaries are the consensus agent's work.
#  - The Smart Gen agent's instruction is now his spec's own rows (PRD R21, R22, R54, R55): it creates an item only when
#    the conversation contains one, never a duplicate, and updates an item when the conversation changes it. The card
#    the app made from every conversation's consensus is no longer made (existing cards stay).
#  - The configuration's labels say plainly what each line is.
T = "tools/"


def rd(p):
    return open(T + p, encoding="utf-8").read()


def wr(p, s):
    open(T + p, "w", encoding="utf-8").write(s)


def one(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:100])
    return s.replace(a, b)


def cut(s, start, end, new):
    a = s.index(start)
    b = s.index(end, a)
    return s[:a] + new + s[b:]


AGENT_MD = '''Inputs:
-User's prompt
-response messages

From this
Fill the following fields:
Consensus Ratio: number of responses with the same sentiment / number of total responses
Consensus Summary: For each response message, use the prompt message to derive need and message intent. This will simplify each message to its base minimal distinction/sentiment; this is the actionable portion of the message. Resolve democratically by counting the number of duplicates of each unique sentiment. The sentiment with the biggest count is the consensus summary verbatim.

For each response:
Calculate, from the full response text and its service to the observed need, the depth (aka length) of the logical chain in the message. This count should include explicit and implicit logical chains. Explicit logical chains are all sequential clarifications/simplifications. They extend logic, not activity. And they serve the purpose by providing capability and independence to the prompter. Accuracy (not precision) never becomes a factor, as logic is independent of facts. In fact, logic forms facts. It can never be wrong or even evaluated on such a basis. Only facts can, trivia.

1. Logical chain: If you fall, THEN it's not your fault
2. Not a logical chain: If you fall, THEN you can file a claim

1 is a clarification of meaning and drives understanding and decision-making. 2 is giving instruction, which provides only procedure, not logic. No decision-making or simplification is offered.

Implicit logical chains count as well. These are definitions, statements, stories, or any narrative element that directly support a logical conclusion. They can be evidentiary after the fact. Or preemptive, before the fact. The point will either immediately precede or supersede them. If not, the chain is broken, or adlibbing has delayed the expression of the point. It becomes obvious either way.

You can also count logical chains by simply reading until the next clause/sentence is not logically dependent on the previous. This extends beyond formatting so paragraphs and structure are irrelevant. An entire paragraph can be considered one logical chain if it is one narrative in service of one larger point: evidentiary, or it can be multiple logical chains if the depth of understanding is further developed within the paragraph. "Because," "Why," "Therefore," "Meaning," "Thus," and "therefore" are all contextual indicators but cannot be counted in a vacuum. This is why you derive intent first, based on the prompt message and its need, and you frame each response message in its purpose to serve that need. From there, you can resolve all logical clarifications because they appear as explanations and they provide rationale.

You will find that the count is not important. Only your definition and your ability to identify them are important. So whatever definition you create for a logical chain will hold up consistently, so long as it is legitimate in its observation of logic. Semantically counting words is not a legitimate observation of logic, by definition. Regex counts trivia. Logical chains count meaning.

Implied logical chains are defined by their usage of a definition as a datum to demonstrate logic or provide clarification of a logical point

Implied Logical Chain examples:
Logical chain: 'A house is a structure. So..."
Logical Chain: 'A house is a structure. A shed is a structure..."
Logical chain: 'A house is a structure. It should be..."
Logical Chain: 'A house is a structure. If you..."
Logical Chain: [Implied need for definition] -> "A house is a structure."
Logical chain: "A house is a structure. The streets are..."

Not logical chains: definitions that are attached to no logical purpose
Not a logical chain: 'A house is a structure.'
Not a logical chain: 'Because why?' Regex search would count this as 2 logical chains. When in reality, in logical purpose, it is just two words with no intended purpose. It could be a quote. Or a question. Neither of which extends logic on its own or is a logical point.

The dictionary would be full of logical chains. But it has 0. Because the definitions exist outside of logical framing, aka need. But if you are playing Scrabble and you ask what the best word to make with your letters is, the meaning of the word (its existence) serves a logical need and therefore becomes a logical chain.
If you are reading a sentence in a document and you write a prompt asking for the meaning of a word, the intent is derived to be to support your need for understanding. Therefore, responses providing the meaning of a word are now considered logical chains, because the meaning of the word directly supports the prompt's derived intent. The prompt need not include the context of "reading a book," "I don't understand this word," or "I'm playing Scrabble" to derive the intent and serve it. Logic is independent of context. Any request for definition or any derived need for definition directly supports the logical basis and counts as a chain. Which can be further extended by further explanation, even if not requested.

Count the total logical chains (explicit + implicit) for each response message and provide the number in a format for this mapping. perhaps JSON, naming each claim by its source name, its indexed value, or its superficial callouts, as you choose to distinguish them. Identification as distinct observations is all that is necessary to be conveyed. Along with their max chain length. Max length is used to distinguish relevant and novel insight/clarification from repetitive, duplicated, or semantic insight. Technical definitions will never extend a logical chain beyond 1. Even if there are 100 of them. They can serve nothing more than immediate understanding on their own. To extend, they must attach to a bigger logical point, and that chain can of course continue on. Split chains don't exist. an apparent split, is logical clarification, and counts. It provides further definition and meaningful texture. Everything that furthers understanding is an additional logical chain. Not separate chains. There's one request, one chain. One prompt, one chain. One problem, one chain. Outside of that is ad libbing, theorizing, or ponderance. Unless these are requested, they cannot provide further understanding. They only show lack of understanding.

Also include in the logical chain length table a line for consensus summary and use the max length chain of all its members as its logical chain length value.

In the table, indicate which responses are grouped with which sentiments, and indicate the consensus sentiment

Accuracy and confidence and all subjective interpretations of a response are irrelevant. You are only recording reality, not advising. This is what makes this objectively valuable and universally desired.

Recap:

Provide the following:
Consensus Ratio
Consensus Summary, as derived (unique actionable takeaway, sentiment, point, intent, summary)
Logical Chain Length Table'''

# How the app reads the result. Kept apart from the instruction so the instruction stays David's own words.
AGENT_FORMAT = '''Reply with JSON only, in this shape, so the app can show it:
{"need": "the need and intent derived from the prompt",
 "sentiments": {"R1": "...", "R2": "..."},
 "groups": [["R1", "R3"], ["R2"]],
 "consensus": "the consensus summary, verbatim",
 "chains": {"R1": 0, "R2": 0}}
sentiments: each response's base minimal distinction/sentiment, at most {n} characters. Responses with the same sentiment have it word for word.
groups: the responses grouped with each sentiment.
chains: each response's logical chain length.'''

SMARTGEN_SPEC = '''Smart Gen holds projects, tasks, reminders, memories, and artifacts.
Creates the item when the conversation already contains it, unless that item exists for the same project, type, and model. A timed reminder also lands on the calendar.
When ongoing conversation modifies facts/dates of an existing task or project, Smart Gen automatically updates existing records rather than duplicating.
Artifacts, reminders, tasks, projects, and memories can be bidirectionally attached and embedded in any combination.'''

SMARTGEN_FORMAT = '''Reply with JSON only, in this shape, so the app can file it:
{"create": [{"type": "project | task | reminder | memory | artifact", "title": "...", "content": "...", "due": "date and time, or empty", "project": "..."}],
 "update": [{"id": "an existing item's id", "title": "...", "content": "...", "due": "..."}]}
The existing items are listed with their ids. Empty lists when the conversation contains no item.'''

s = rd("collider_server.py")

# ---------- the consensus agent ----------
s = cut(s, "AGENT_PROMPT = \"\"\"You are the Collider consensus agent.", "def parse_json(text):",
        "AGENT_PROMPT = " + repr(AGENT_MD) + "\nAGENT_FORMAT = " + repr(AGENT_FORMAT) + "\n\n\n")
s = one(s, """                        if isinstance(obj, dict) and "essences" in obj:""",
        """                        if isinstance(obj, dict) and ("sentiments" in obj or "essences" in obj or "create" in obj):""")
s = cut(s, "def run_consensus(prompt, answers, n=None):", "def plain(s):", '''def run_consensus(prompt, answers, n=None):
    """The consensus agent, by David's instruction (AGENT_PROMPT). answers: {model_id: text}.
    Returns the need, each response's sentiment, the groups, the consensus summary, the ratio and the chain lengths."""
    n = n or LINE_DEFAULT
    ids = list(answers.keys())
    tags = {f"R{i + 1}": mid for i, mid in enumerate(ids)}
    body = "\\n\\n".join(f"{t}:\\n{answers[mid][:TUNING['agent_answer_chars']]}" for t, mid in tags.items())
    msgs = [{"role": "system", "content": AGENT_PROMPT + "\\n\\n" + AGENT_FORMAT.replace("{n}", str(n))},
            {"role": "user", "content": f"User's prompt:\\n{prompt}\\n\\nResponse messages:\\n\\n{body}"}]
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


''')

# no essence instruction, no one-line agent, no summary-line rule
s = cut(s, "def self_essence(model, prompt, answer):", "# ---------------- Two-line Summary ----------------", "")
s = cut(s, "LINE_RULE = (\"Begin your reply", "def line_budget(v):", "\n\n")
s = cut(s, "def agent_lines(prompt, answers, n, groups=None):", "def consensus_line(sess, n):", '''def agent_lines(prompt, answers, n, groups=None):
    """Each response's summary, for sessions saved without one: the consensus agent's sentiment for it."""
    c = run_consensus(prompt, answers, n)
    return {m: v for m, v in ((c or {}).get("lines") or {}).items() if v}


''')
s = one(s, """            res[m]["line"] = got.get(m) or fit_words(res[m].get("essence") or done[m], n)""",
        """            res[m]["line"] = got.get(m) or res[m].get("essence") or \"\"""")
s = s.replace("""ESSENCE_PROMPT = ("Reduce the answer below to its essence: one standalone sentence stating what it says, "
                  "in service of the question's need. Never mention who wrote it. Reply with the sentence only.")
""", "")

# the responses: no summary line asked of the models; the consensus agent writes the summaries
s = one(s, """    system = DEPTH.get(mode, DEPTH["chat"]) + "\\n\\n" + LINE_RULE.replace("{n}", str(n))""",
        """    system = DEPTH.get(mode, DEPTH["chat"])""")
s = one(s, """            if job["results"][mid]["status"] == "pending":
                l, t = draft_split(s, n)
                job["results"][mid].update(line=l, text=t)""", """            if job["results"][mid]["status"] == "pending":
                job["results"][mid].update(text=draft_clean(s).strip())""")
s = one(s, """            line, text = split_line(stream_model(mid, msgs, MAX_TOKENS.get(mode, 1200), drafted), n)""",
        """            text, line = stream_model(mid, msgs, MAX_TOKENS.get(mode, 1200), drafted).strip(), \"\"""")
s = cut(s, "    cons = run_consensus(prompt, answers, n) if answers else None\n", "    if mode in PLAN_QUERIES and not job.get(\"incognito\"):", '''    cons = run_consensus(prompt, answers, n) if answers else None
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
''')
s = one(s, """    if job.get("save") and not job.get("incognito"):
        save_session(job)


def report_text""", """    if job.get("save") and not job.get("incognito"):
        save_session(job)
        POOL.submit(_smartgen_agent, job)


def report_text""")

# a reply to one model: its summary is the consensus agent's sentiment for that response
s = one(s, """    msgs = [{"role": "system", "content": own_system(mid) + DEPTH.get(body.get("mode", "chat"), DEPTH["chat"]) + "\\n\\n" + LINE_RULE.replace("{n}", str(n))}] + [dict(m) for m in raw_messages]""",
        """    msgs = [{"role": "system", "content": own_system(mid) + DEPTH.get(body.get("mode", "chat"), DEPTH["chat"])}] + [dict(m) for m in raw_messages]""")
s = one(s, """    drafted = (lambda s: on_draft(*draft_split(s, n))) if on_draft else None
    line, text = split_line(stream_model(mid, msgs, TUNING["reply_tokens"], drafted), n)""",
        """    drafted = (lambda s: on_draft("", draft_clean(s).strip())) if on_draft else None
    text = stream_model(mid, msgs, TUNING["reply_tokens"], drafted).strip()
    asked = next((m["content"] for m in reversed(raw_messages) if m.get("role") == "user"), "")
    c = run_consensus(asked, {mid: text}, n) if text else None
    line = ((c or {}).get("lines") or {}).get(mid, "")""")
s = one(s, """        res_entry["essence"] = self_essence_fallback(text) or line""", """        res_entry["essence"] = line""")

# ---------- Smart Gen ----------
a = s.index("SMARTGEN_PROMPT = ")
b = s.index('"""', s.index('"""', a) + 3) + 3
s = s[:a] + "SMARTGEN_PROMPT = " + repr(SMARTGEN_SPEC) + "\nSMARTGEN_FORMAT = " + repr(SMARTGEN_FORMAT) + s[b:]
s = cut(s, "    if not _smartgen_mem and _history_mem:\n", "def rows(name=None, search=None):", "\n\n")
s = cut(s, "def _extract_smartgen_card(job, save=True):", "def save_session(job):", '''def _smartgen_agent(job):
    """The Smart Gen agent, by David's spec (SMARTGEN_PROMPT, in the configuration): creates an item only when the
    conversation contains one and it is not already there, and updates an item the conversation changes."""
    global _smartgen_mem
    if _smartgen_mem is None:
        _smartgen_mem = []
    results = job.get("results") or {}
    said = "\\n\\n".join(f"{LABEL.get(m, m)}:\\n{(r.get('text') or '')[:TUNING['agent_answer_chars']]}"
                        for m, r in results.items() if r.get("status") == "done" and r.get("text"))
    have = "\\n".join(f"- {c.get('id')}: {c.get('type') or 'card'} | {c.get('project') or ''} | {c.get('title') or ''}"
                     for c in _smartgen_mem[:TUNING["smartgen_kept"]])
    user = f"Existing items:\\n{have or '(none)'}\\n\\nUser's message:\\n{job.get('prompt') or ''}\\n\\nResponses:\\n\\n{said}"
    msgs = [{"role": "system", "content": SMARTGEN_PROMPT + "\\n\\n" + SMARTGEN_FORMAT}, {"role": "user", "content": user}]
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


''')
s = one(s, """    try:
        _extract_smartgen_card(job, save=True)
    except Exception:
        pass
""", "")

# ---------- configuration ----------
s = one(s, """SETTINGS = ("consensus_agent", "agent_chain", "agent_prompt", "lines_prompt", "essence_prompt", "plan_prompt", "models",
            "depth", "line_rule", "line_length",""", """SETTINGS = ("consensus_agent", "agent_chain", "agent_prompt", "plan_prompt", "models",
            "depth", "line_length",""")
s = one(s, """            "essence_prompt": ESSENCE_PROMPT, "tuning": dict(TUNING),""", """            "tuning": dict(TUNING),""")
s = one(s, """            "depth": dict(DEPTH), "line_rule": LINE_RULE, "line_length": LINE_DEFAULT,""", """            "depth": dict(DEPTH), "line_length": LINE_DEFAULT,""")
s = one(s, """"source_chars": dict(SOURCE_CHARS), "agent_prompt": AGENT_PROMPT, "lines_prompt": LINES_PROMPT,""",
        """"source_chars": dict(SOURCE_CHARS), "agent_prompt": AGENT_PROMPT,""")
s = one(s, """    global CONSENSUS_AGENT, AGENT_CHAIN, DEPTH, LINE_RULE, LINE_DEFAULT, SEARCH, MAX_TOKENS, DEADLINE, SILENCE
    global AGENT_PROMPT, LINES_PROMPT, PACK_PRICE, TRACKS_PER_PACK, _BUILT_IN, PLAN_QUERIES, SOURCE_CHARS, PLAN_PROMPT
    global ESSENCE_PROMPT, TUNING, SMARTGEN_PROMPT
    missing = False""", """    global CONSENSUS_AGENT, AGENT_CHAIN, DEPTH, LINE_DEFAULT, SEARCH, MAX_TOKENS, DEADLINE, SILENCE
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
        missing = True""")
s = one(s, """    DEPTH, LINE_RULE, LINE_DEFAULT = dict(cfg["depth"]), str(cfg["line_rule"]), int(cfg["line_length"])""",
        """    DEPTH, LINE_DEFAULT = dict(cfg["depth"]), int(cfg["line_length"])""")
s = one(s, """    ESSENCE_PROMPT = str(cfg["essence_prompt"])
""", "")
s = one(s, """    AGENT_PROMPT, LINES_PROMPT = str(cfg["agent_prompt"]), str(cfg["lines_prompt"])""", """    AGENT_PROMPT = str(cfg["agent_prompt"])""")
wr("collider_server.py", s)

# ---------- the form: plain labels ----------
f = rd("collider_form.py")
a = f.index("const N={")
b = f.index("};", a) + 2
f = f[:a] + ("const N={consensus_agent:'Consensus agent model',agent_chain:'Consensus agent backups',agent_prompt:'Consensus agent instruction',"
             "smartgen_prompt:'Smart Gen agent instruction',plan_prompt:'Search planning instruction',models:'Models',"
             "depth:'Response instruction by mode',line_length:'Summary length (characters)',search:'Web search by mode',"
             "plan_queries:'Planned searches by mode',source_chars:'Source length by mode (characters)',max_tokens:'Response length by mode (tokens)',"
             "deadline:'Response wait by mode (seconds)',silence:'Longest silence while streaming (seconds)',tuning:'Tuning',"
             "pack_price:'Pack price',tracks_per_pack:'Tracks per pack',imagine:'Discover Market'};") + f[b:]
f = one(f, "['consensus_agent','agent_chain','agent_prompt','lines_prompt','essence_prompt','plan_prompt','smartgen_prompt','models']",
        "['consensus_agent','agent_chain','agent_prompt','smartgen_prompt','plan_prompt','models']")
f = one(f, "['depth','line_rule','line_length',", "['depth','line_length',")
wr("collider_form.py", f)
print("round 34 applied")

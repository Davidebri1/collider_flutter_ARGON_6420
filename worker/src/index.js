// Collider ARGON 6420 on Cloudflare Workers + Assets: permanent 24/7 live cloud host.
// Serves the Flutter web app, /config, /dashboard.html, and all /api/* endpoints from one origin.
import themesCache from "../themes.json";
import formBundle from "../form.json";

const DEFAULT_ROSTER = [
  { id: "nvidia/nemotron-3.5-bolt-e4b", label: "Nemotron 3.5 Bolt", short: "NBLT", provider: "NVIDIA", via: "NVIDIA", color: "#76B900", system: "", temperature: "" },
  { id: "nvidia/nemotron-3.5-super-vl-120b-a12b", label: "Nemotron 3.5 Super", short: "N35S", provider: "NVIDIA", via: "NVIDIA", color: "#22C55E", system: "", temperature: "" },
  { id: "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", label: "Nemotron 3 Nano", short: "N3N", provider: "NVIDIA", via: "NVIDIA", color: "#34D399", system: "", temperature: "" },
  { id: "nvidia/nemotron-3-ultra-550b-a55b", label: "Nemotron 3 Ultra", short: "N3U", provider: "NVIDIA", via: "NVIDIA", color: "#4ADE80", system: "", temperature: "" },
  { id: "mistralai/mistral-large-4-1t-a52b", label: "Mistral Large 4", short: "ML4", provider: "Mistral", via: "NVIDIA", color: "#FB923C", system: "", temperature: "" },
  { id: "minimaxai/minimax-m3.1-flash", label: "MiniMax M3.1 Flash", short: "MM31", provider: "MiniMax", via: "NVIDIA", color: "#F472B6", system: "", temperature: "" },
  { id: "nvidia/nemotron-3.5-lightning-30b-a3b", label: "Nemotron 3.5 Lightning", short: "N35L", provider: "NVIDIA", via: "NVIDIA", color: "#A3E635", system: "", temperature: "" },
  { id: "google/gemma-4-31b-it", label: "Gemma 4 31B", short: "G4", provider: "Google", via: "NVIDIA", color: "#FBBF24", system: "", temperature: "" },
  { id: "meta/llama-3.2-90b-vision-instruct", label: "Llama 3.2 90B Vision", short: "L90", provider: "Meta", via: "NVIDIA", color: "#818CF8", system: "", temperature: "" },
  { id: "meta/muse-glimmer-30b", label: "Muse Glimmer 30B", short: "MG30", provider: "Meta", via: "NVIDIA", color: "#A78BFA", system: "", temperature: "" },
  { id: "stepfun-ai/step-5-preview", label: "Step 5 Preview", short: "S5", provider: "StepFun", via: "NVIDIA", color: "#38BDF8", system: "", temperature: "" },
];

const CONSENSUS_AGENT = "nvidia/nemotron-3.5-bolt-e4b";
const AGENT_CHAIN = [CONSENSUS_AGENT, "nvidia/nemotron-3-ultra-550b-a55b", "mistralai/mistral-large-4-1t-a52b", "google/gemma-4-31b-it"];

const DEPTH = {
  chat: "Answer directly and concisely. Plain language, no jargon.",
  internet: "Answer directly using the web sources provided. Cite sources inline as [n]. Plain language, no jargon.",
  research:
    "Write a research report: a one-paragraph answer first, then short sections with headings covering the evidence, the trade-offs and a clear recommendation. Cite sources inline as [n] and end with a numbered source list. Plain language, no jargon.",
  deep:
    "Write an annotated research paper: an abstract that states the answer, then numbered sections in which every claim carries its source [n] and a short note on why it matters or how strong the evidence is, a section on where the sources disagree, and a conclusion with practical next steps. More insight, no jargon: explain anything technical in everyday words. End with a numbered source list.",
};
const SEARCH = { internet: ["basic", 5], research: ["advanced", 8], deep: ["advanced", 12] };
const MAX_TOKENS = { chat: 900, internet: 1200, research: 2400, deep: 4000 };
const SOURCE_CHARS = { internet: 1200, research: 1200, deep: 1200 };
const DEADLINE = { chat: 60000, internet: 80000, research: 100000, deep: 120000 };

const THINKING_TOKENS = 4000;
const TEMPERATURE = 0.4;
const RETRIES = 2;
const AGENT_CHARS = 2200;
const AGENT_TOKENS = 2500;
const AGENT_TIMEOUT = 110000;
const REPLY_TOKENS = 1400;
const HISTORY_KEPT = 200;

const AGENT_PROMPT = `Inputs:
-User's prompt
-response messages

Derive, for each response, the need and intent behind it, then reduce it to its base minimal distinction/sentiment: the actionable position it takes.

Group responses that take the SAME position, even when they word it differently. Two responses belong in one group when someone could act on either one and get the same thing.

Accuracy and confidence and all subjective interpretations of a response are irrelevant. You are only recording reality, not advising.`;

const AGENT_FORMAT = `Reply with JSON only, in this shape, so the app can show it:
{"need": "the need and intent derived from the prompt message",
 "sentiments": {"R1": "...", "R2": "..."},
 "groups": [["R1","R2","R4"],["R3"]],
 "consensus": "the consensus summary, verbatim",
 "chains": {"R1": 1, "R2": 1}}
sentiments: each response's base minimal distinction/sentiment (the actionable portion of the message). Responses with the same sentiment have it word for word.
groups: the responses grouped by shared position, biggest group first.
consensus: the sentiment with the biggest count, verbatim.`;

const LEAK_RE =
  /^(let'?s\s+count\s+characters|wait,\s+the\s+prompt|begin\s+your\s+reply\s+with\s+one\s+line|character\s+count\s*:|let'?s\s+check\s+length|drafting\s+the\s+one-liner|the\s+user\s+wants\s+one\s+line|here'?s\s+a\s+thinking\s+process|line\s+1\s*:\s*max|then\s+an\s+empty\s+line|then\s+the\s+full\s+answer).*$/gim;

const KILL_PHRASES = [
  "begin your reply with one line", "line 1: max", "then an empty line", "then the full answer",
  "let's check the character count", "let's make a short line 1", "1,2,3,4,5", "prompt asks:",
  "constraints:", "let's count", "count characters", "count: ", "let's check the length",
  "characters, spaces included", "wait, let's count", "analyze user input:", "identify key requirements:",
  "we need to produce answer", "we need first line", "so first line max", "need <=", "too long.",
  "the user is asking", "let me think about", "the instruction says:", "format considerations:",
  "that's a good structure.", "that's pretty good. should i use", "here's a thinking process", "chars)",
  "characters)", "full stop at the end", "no period at the end",
];

function sanitize(text) {
  if (!text) return "";
  let s = String(text).replace(/<think>[\s\S]*?<\/think>/g, "").trim();
  const cut = s.indexOf("<think>");
  if (cut >= 0) s = s.slice(0, cut).trim();
  for (const marker of ["Then the full answer:\n", "Then the full answer:", "Let me draft:", "Let's just write:"]) {
    const at = s.lastIndexOf(marker);
    if (at >= 0) s = s.slice(at + marker.length).trim();
  }
  const paras = s.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
  const kept = paras.filter((p) => {
    const low = p.toLowerCase();
    return !KILL_PHRASES.some((k) => low.includes(k));
  });
  s = kept.join("\n\n");
  s = s.replace(LEAK_RE, "").trim();
  return s;
}

function plain(s) {
  return String(s || "").replace(/\*\*|__|`/g, "").replace(/^\s*(#+|[-*>])\s+/, "").trim();
}

function selfEssence(answer) {
  const paras = String(answer || "").trim().split("\n").map((p) => plain(p).trim()).filter(Boolean);
  const target = paras.length > 1 && paras[0].length <= 45 ? paras[1] : (paras[0] || "");
  return target.split(/(?<=[.!?])\s+/)[0].trim().slice(0, 240);
}

function sanitizeMessages(messages) {
  const out = [];
  for (const m of messages || []) {
    let role = String(m && m.role ? m.role : "user").trim().toLowerCase();
    if (!["system", "user", "assistant"].includes(role)) role = "user";
    const content = String((m && m.content) || "").trim();
    if (!content) continue;
    if (out.length && out[out.length - 1].role === role && role !== "system") {
      out[out.length - 1].content += "\n\n" + content;
    } else {
      out.push({ role, content });
    }
  }
  return out;
}

function parseJsonLoose(text) {
  const cleaned = String(text || "").replace(/```(?:json)?/g, "");
  for (let i = 0; i < cleaned.length; i++) {
    if (cleaned[i] !== "{") continue;
    let depth = 0;
    for (let j = i; j < cleaned.length; j++) {
      if (cleaned[j] === "{") depth++;
      else if (cleaned[j] === "}") {
        depth--;
        if (depth === 0) {
          try {
            const obj = JSON.parse(cleaned.slice(i, j + 1));
            if (obj && typeof obj === "object" && ("sentiments" in obj || "summaries" in obj || "essences" in obj || "create" in obj)) return obj;
          } catch (_) {}
          break;
        }
      }
    }
  }
  throw new Error("no json");
}

// ---------- live configuration (KV argon6420:config + env.PROVIDERS_JSON fallback) ----------
async function loadLiveConfig(env) {
  let kvCfg = null;
  try {
    const raw = await env.STATE.get("argon6420:config");
    if (raw) kvCfg = JSON.parse(raw);
  } catch (_) {}

  let envProviders = [];
  try {
    envProviders = JSON.parse(env.PROVIDERS_JSON || "[]");
  } catch (_) {}

  const defs = (formBundle && formBundle.defaults) || {};
  const provs = (kvCfg && Array.isArray(kvCfg.providers) && kvCfg.providers.length)
    ? kvCfg.providers
    : envProviders.map((p) => ({
        name: p.name || "NVIDIA",
        endpoint: p.endpoint || p.url || "",
        key: p.key || "",
        models: Array.isArray(p.models) ? p.models.join(", ") : (p.models || ""),
      }));

  const merged = {
    ...defs,
    ...(kvCfg || {}),
    providers: provs,
    models: (kvCfg && Array.isArray(kvCfg.models) && kvCfg.models.length) ? kvCfg.models : DEFAULT_ROSTER,
    themes: (kvCfg && kvCfg.themes) || "https://collider-themes.ebridavid.workers.dev",
    store_bypass: Boolean(kvCfg && kvCfg.store_bypass),
  };
  if (merged.tuning && typeof merged.tuning === "object") {
    for (const k of [
      "lines_tokens", "lines_backup_tokens", "lines_timeout", "line_min", "line_max",
      "essence_answer_chars", "essence_tokens", "essence_timeout", "essence_short_line", "essence_fallback_chars"
    ]) {
      delete merged.tuning[k];
    }
  }
  return merged;
}

function normalizeProvider(r) {
  const ep = String(r.endpoint || r.url || "").trim();
  const low = ep.toLowerCase();
  const nameLow = String(r.name || "").trim().toLowerCase();
  return {
    name: r.name || "NVIDIA",
    url: ep,
    endpoint: ep,
    key: String(r.key || "").trim(),
    search: low.includes("tavily") || nameLow === "tavily",
    speech: low.includes("audio/transcriptions"),
    imagine: low.includes("fal.run") || low.includes("collider-imagine"),
    phone: low.includes("collider-phone") || nameLow === "phone",
    models: typeof r.models === "string" ? r.models.split(",").map((s) => s.trim()).filter(Boolean) : (r.models || []),
  };
}

function providerUses(r, roster) {
  const p = normalizeProvider(r);
  if (!p.key) return "Not read: no key";
  if (p.speech) return "Voice chat: speech turned into text (/api/transcribe)";
  if (p.phone) return "Phone relay key";
  if (p.imagine) return "Pictures and videos (/api/imagine)";
  if (p.search) return "Web sources for Internet, Research and Deep Research (/api/ask)";
  const ms = roster.filter((m) => String(m.via || "NVIDIA").toLowerCase() === String(p.name || "").toLowerCase()).map((m) => m.label);
  return ms.length ? `${ms.length} models' answers (/api/ask) and consensus: ${ms.join(", ")}` : "Active LLM provider";
}

const turn = {};
function nextRow(provs, via) {
  const want = String(via || "NVIDIA").toLowerCase();
  const all = provs.map(normalizeProvider).filter((p) => p.key && !p.search && !p.speech && !p.imagine && !p.phone && /chat\/completions|messages/.test(p.url));
  let hit = all.filter((p) => String(p.name || "").toLowerCase() === want);
  if (!hit.length) hit = all.filter((p) => /nvidia/i.test(p.url));
  if (!hit.length) return null;
  turn[want] = ((turn[want] ?? -1) + 1) % hit.length;
  return hit[turn[want]];
}

async function callModel(cfg, model, messages, maxTokens, timeoutMs = 150000) {
  const roster = cfg.models || DEFAULT_ROSTER;
  const def = roster.find((m) => m.id === model);
  const via = (def && def.via) || "NVIDIA";
  const temp = def && def.temperature !== "" && def.temperature != null ? Number(def.temperature) || TEMPERATURE : TEMPERATURE;
  const clean = sanitizeMessages(messages);
  let last = "no reply";
  for (let attempt = 0; attempt < RETRIES; attempt++) {
    const row = nextRow(cfg.providers || [], via);
    if (!row) throw new Error("no key for " + via);
    try {
      const r = await fetch(row.url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + String(row.key).trim() },
        body: JSON.stringify({
          model,
          messages: clean,
          max_tokens: maxTokens + THINKING_TOKENS,
          temperature: temp,
          chat_template_kwargs: { enable_thinking: true, thinking: true },
        }),
        signal: AbortSignal.timeout(timeoutMs),
      });
      if (!r.ok) {
        last = "HTTP " + r.status;
        await r.text();
        continue;
      }
      const j = await r.json();
      const text = sanitize((((j.choices || [])[0] || {}).message || {}).content || "");
      if (text) return text;
      last = "empty reply";
    } catch (e) {
      last = String((e && e.message) || e).slice(0, 90);
      if (/timed out|abort/i.test(last)) break;
    }
  }
  throw new Error(last);
}

async function webSearch(cfg, query, mode) {
  const searcher = (cfg.providers || []).map(normalizeProvider).find((p) => p.search && p.key);
  if (!searcher || !SEARCH[mode]) return [];
  const [depth, n] = SEARCH[mode];
  const chars = SOURCE_CHARS[mode] || 1200;
  try {
    const r = await fetch(searcher.url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: String(searcher.key).trim(), query, search_depth: depth, max_results: n }),
      signal: AbortSignal.timeout(40000),
    });
    const j = await r.json();
    return (j.results || [])
      .filter((x) => x && x.url)
      .slice(0, n)
      .map((x) => ({ title: x.title || "", url: x.url, content: String(x.content || "").slice(0, chars) }));
  } catch (_) {
    return [];
  }
}

function sourcesBlock(sources) {
  if (!sources || !sources.length) return "";
  return "Web sources:\n\n" + sources.map((s, i) => `[${i + 1}] ${s.title} — ${s.url}\n${s.content}`).join("\n\n");
}

// ---------- consensus (Consensus Agent.md: one base minimal distinction/sentiment verbatim) ----------
async function runConsensus(cfg, prompt, answers) {
  const ids = Object.keys(answers);
  if (!ids.length) return null;
  const tags = {};
  ids.forEach((mid, i) => (tags["R" + (i + 1)] = mid));
  const body = ids.map((mid, i) => `R${i + 1}:\n${String(answers[mid]).slice(0, AGENT_CHARS)}`).join("\n\n");
  const sysPrompt = (cfg.agent_prompt || AGENT_PROMPT) + "\n\n" + AGENT_FORMAT;
  const msgs = [
    { role: "system", content: sysPrompt },
    { role: "user", content: `User's prompt:\n${prompt}\n\nResponse messages:\n\n${body}` },
  ];
  const chain = Array.isArray(cfg.agent_chain) && cfg.agent_chain.length ? cfg.agent_chain : AGENT_CHAIN;
  let agent = null;
  let out = null;
  for (const a of chain) {
    try {
      const text = await callModel(cfg, a, msgs, AGENT_TOKENS, AGENT_TIMEOUT);
      const parsed = parseJsonLoose(text);
      if (parsed && (parsed.sentiments || parsed.summaries || parsed.essences)) {
        agent = a;
        out = parsed;
        break;
      }
    } catch (_) {}
  }
  if (!out) return null;
  const rawSent = out.sentiments || out.summaries || out.essences || {};
  const sentiments = {};
  for (const [t, v] of Object.entries(rawSent)) {
    if (tags[t] && String(v).trim()) sentiments[tags[t]] = plain(v);
  }
  if (!Object.keys(sentiments).length) return null;
  let groups = (out.groups || []).map((g) => (g || []).map((t) => tags[t]).filter(Boolean)).filter((g) => g.length);
  const seen = new Set(groups.flat());
  for (const mid of Object.keys(sentiments)) if (!seen.has(mid)) groups.push([mid]);
  groups.sort((a, b) => b.length - a.length);
  const chains = {};
  for (const [t, v] of Object.entries(out.chains || {})) {
    if (tags[t] && Number.isFinite(Number(v))) chains[tags[t]] = Number(v);
  }
  const win = groups[0] || [];
  // Per Consensus Agent.md: "The sentiment with the biggest count is the consensus summary verbatim."
  const consensus = plain((win.length ? sentiments[win[0]] : "") || out.consensus || out.consensus_summary || "");
  return {
    status: "done",
    agent,
    need: out.need || "",
    essences: sentiments,
    lines: { ...sentiments },
    chains,
    consensus_chain: win.reduce((mx, m) => Math.max(mx, chains[m] || 0), 0),
    groups,
    summary: consensus,
    line: consensus,
    score: `${win.length}/${ids.length}`,
    dissent: groups.slice(1).map((g) => sentiments[g[0]]).filter(Boolean),
    tie_basis: "",
  };
}

function newJob(cfg, body, priorSess) {
  const roster = cfg.models || DEFAULT_ROSTER;
  const known = new Set(roster.map((m) => m.id));
  const models = (body.models || []).filter((m) => known.has(m));
  const chosen = models.length ? models : [roster[0].id];
  const priorThreads = {};
  for (const [mid, r] of Object.entries((priorSess && priorSess.results) || {})) {
    if (r.messages && r.messages.length) priorThreads[mid] = r.messages;
    else if (r.text) priorThreads[mid] = [
      { role: "user", content: priorSess.prompt || "" },
      { role: "assistant", content: r.text },
    ];
  }
  const prompt = String(body.prompt || "").trim();
  const job = {
    id: priorSess ? priorSess.id : crypto.randomUUID().replace(/-/g, "").slice(0, 12),
    prompt,
    mode: body.mode || "chat",
    created: Date.now() / 1000,
    models: chosen,
    status: "running",
    stage: "queued",
    sources: [],
    results: Object.fromEntries(
      chosen.map((m) => [
        m,
        {
          status: "pending",
          text: "",
          essence: "",
          line: "",
          messages: sanitizeMessages([...(priorThreads[m] || []), { role: "user", content: prompt }]),
        },
      ]),
    ),
    consensus: { status: "pending", summary: "", line: "", score: "", dissent: [] },
    save: body.autosave !== false,
    incognito: body.incognito === true,
    attachments: (body.attachments || []).slice(0, 12),
  };
  return { job, priorThreads };
}

async function runJob(env, cfg, job, priorThreads, onUpdate) {
  const prompt = job.prompt;
  const mode = job.mode;
  const roster = cfg.models || DEFAULT_ROSTER;
  if (SEARCH[mode]) {
    job.stage = "searching";
    onUpdate();
    job.sources = await webSearch(cfg, prompt, mode);
  }
  job.stage = "answering";
  onUpdate();
  const system = (cfg.depth && cfg.depth[mode]) || DEPTH[mode] || DEPTH.chat;
  const src = sourcesBlock(job.sources);

  await Promise.all(
    job.models.map(async (mid) => {
      const prior = job.results[mid];
      if (prior && prior.status === "done" && prior.text) return;
      const t0 = Date.now();
      const historyMsgs = priorThreads[mid] || [];
      const ownSys = ((roster.find((m) => m.id === mid) || {}).system || "").trim();
      const msgs = [
        { role: "system", content: (ownSys ? ownSys + "\n\n" : "") + system + (src ? "\n\n" + src : "") },
        ...historyMsgs,
        { role: "user", content: prompt },
      ];
      try {
        const text = await callModel(cfg, mid, msgs, MAX_TOKENS[mode] || 1200, DEADLINE[mode] || 100000);
        const ess = selfEssence(text);
        job.results[mid].status = "done";
        job.results[mid].text = text;
        job.results[mid].essence = ess;
        job.results[mid].line = ess;
        job.results[mid].messages = sanitizeMessages([
          ...historyMsgs,
          { role: "user", content: prompt },
          { role: "assistant", content: text },
        ]);
        job.results[mid].ms = Date.now() - t0;
        delete job.results[mid].error;
      } catch (e) {
        job.results[mid].status = "error";
        job.results[mid].error = String((e && e.message) || e).slice(0, 200);
        job.results[mid].ms = Date.now() - t0;
      }
      onUpdate();
    }),
  );

  if (!job.consensus_done) {
    job.stage = "consensus";
    onUpdate();
    const answers = Object.fromEntries(
      Object.entries(job.results)
        .filter(([, r]) => r.status === "done" && r.text)
        .map(([m, r]) => [m, r.text]),
    );
    const cons = Object.keys(answers).length ? await runConsensus(cfg, prompt, answers) : null;
    if (cons) {
      for (const [mid, e] of Object.entries(cons.essences)) {
        if (job.results[mid]) {
          job.results[mid].essence = e;
          job.results[mid].line = e;
        }
      }
      cons.line = cons.summary || "";
      job.consensus = cons;
    } else {
      job.consensus = { status: "unavailable", summary: "", line: "", score: "", dissent: [] };
    }
    job.consensus_done = true;
  }
  job.stage = "done";
  job.status = "done";
  onUpdate();
  if (job.save && !job.incognito) await saveSession(env, job);
}

async function saveSession(env, job) {
  const hist = await loadHistory(env);
  const entry = Object.fromEntries(
    ["id", "prompt", "mode", "created", "models", "results", "consensus", "sources"].map((k) => [k, job[k]]),
  );
  const next = [entry, ...hist.filter((s) => s.id !== job.id)].slice(0, HISTORY_KEPT);
  await env.STATE.put("argon6420:history", JSON.stringify(next));
}

async function loadHistory(env) {
  try {
    const raw = (await env.STATE.get("argon6420:history")) || (await env.STATE.get("history"));
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  } catch (_) {
    return [];
  }
}

async function loadSmartgen(env) {
  try {
    const raw = (await env.STATE.get("argon6420:smartgen")) || (await env.STATE.get("smartgen"));
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  } catch (_) {
    return [];
  }
}

async function makeReply(cfg, body) {
  const mid = body.model;
  const roster = cfg.models || DEFAULT_ROSTER;
  const ownSys = ((roster.find((m) => m.id === mid) || {}).system || "").trim();
  const raw = sanitizeMessages(body.messages || []);
  const msgs = [
    { role: "system", content: (ownSys ? ownSys + "\n\n" : "") + (DEPTH[body.mode || "chat"] || DEPTH.chat) },
    ...raw.map((m) => ({ ...m })),
  ];
  const text = (await callModel(cfg, mid, msgs, REPLY_TOKENS, 150000)).trim();
  const asked = [...raw].reverse().find((m) => m.role === "user");
  let essence = "";
  try {
    const c = text ? await runConsensus(cfg, (asked && asked.content) || "", { [mid]: text }) : null;
    essence = (c && c.essences && c.essences[mid]) || "";
  } catch (_) {}
  if (!essence) essence = selfEssence(text);
  const updated = sanitizeMessages([...raw, { role: "assistant", content: text }]);
  return { ok: true, text, essence, line: essence, messages: updated };
}

const json = (obj, code = 200) =>
  new Response(JSON.stringify(obj), {
    status: code,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });

const sseHeaders = {
  "Content-Type": "text/event-stream; charset=utf-8",
  "Cache-Control": "no-store",
  "X-Accel-Buffering": "no",
};

function sseFrom(streamFactory) {
  return new Response(new ReadableStream({ start: streamFactory }), { headers: sseHeaders });
}

const stripThreads = (o) => {
  const { priorThreads, ...rest } = o;
  return rest;
};
const stripBody = (o) => {
  const { body, ...rest } = o;
  return rest;
};

function edge(url) {
  const R2 = "https://pub-6263d41408f145baa5b058378744d787.r2.dev/";
  const MEDIA = "https://collider-media.ebridavid.workers.dev/";
  let u = typeof url === "string" && url.startsWith(R2) ? MEDIA + url.slice(R2.length) : url;
  if (typeof u === "string") {
    u = u.replace("062%20Blue%20Cove.jpg", "063%20Blue%20Cove.jpg").replace("062 Blue Cove.jpg", "063 Blue Cove.jpg");
  }
  return u;
}

function themeList() {
  const counts = {};
  const numerals = ["", " II", " III", " IV", " V"];
  return (themesCache || []).map((t) => {
    const base = String(t.name || "").replace(/\s+(II|III|IV|V)$/, "").trim();
    const idx = counts[base] || 0;
    counts[base] = idx + 1;
    const suffix = idx < numerals.length ? numerals[idx] : ` ${idx + 1}`;
    return {
      ...t,
      name: base + suffix,
      video: edge(t.video),
      poster: edge(t.poster),
      tracks: (t.tracks || []).map((s) => ({ ...s, url: edge(s.url) })),
    };
  });
}

function describeModels(cfg) {
  const provs = (cfg.providers || []).map(normalizeProvider);
  return {
    models: cfg.models || DEFAULT_ROSTER,
    agent: cfg.consensus_agent || CONSENSUS_AGENT,
    search: provs.some((p) => p.search && p.key),
    keys: provs.filter((p) => p.key && !p.search && !p.speech && !p.imagine && !p.phone).length,
  };
}

const SETTINGS_KEYS = [
  "consensus_agent", "agent_chain", "agent_prompt", "plan_prompt", "models",
  "depth", "line_length", "search", "plan_queries", "source_chars", "max_tokens", "deadline",
  "silence", "tuning", "pack_price", "tracks_per_pack", "smartgen_prompt",
  "consensus_agent_and_synthesis", "smartgen_extraction", "depth_modes_and_search",
  "imagine_and_media_generation", "theme_pack_and_server_tuning",
];

function buildFormInitial(cfg) {
  const defInit = (formBundle && formBundle.defaultInitial) || {};
  const defSettings = defInit.settings || {};
  const provs = (cfg.providers || []).map((r) => ({
    provider_name: r.provider_name || r.name || "NVIDIA",
    api_endpoint_url: r.api_endpoint_url || r.endpoint || r.url || "",
    api_key: r.api_key || r.key || "",
    extra_model_ids: Array.isArray(r.extra_model_ids || r.models)
      ? (r.extra_model_ids || r.models).join(", ")
      : String(r.extra_model_ids || r.models || ""),
    name: r.provider_name || r.name || "NVIDIA",
    endpoint: r.api_endpoint_url || r.endpoint || r.url || "",
    key: r.api_key || r.key || "",
    models: Array.isArray(r.extra_model_ids || r.models)
      ? (r.extra_model_ids || r.models).join(", ")
      : String(r.extra_model_ids || r.models || ""),
  }));
  const roster = cfg.models || defSettings.models || DEFAULT_ROSTER;
  const settingsObj = { ...defSettings };
  for (const k of SETTINGS_KEYS) {
    if (k in cfg && cfg[k] !== undefined) settingsObj[k] = cfg[k];
  }
  return {
    host: cfg.localhost_port || defInit.host || 6420,
    providers: provs,
    themes: cfg.themes || "https://collider-themes.ebridavid.workers.dev",
    bypass: Boolean(cfg.store_bypass),
    uses: provs.map((r) => providerUses(r, roster)),
    key_catalog: (Array.isArray(cfg.key_catalog) && cfg.key_catalog.length) ? cfg.key_catalog : (defInit.key_catalog || []),
    model_catalog: (Array.isArray(cfg.model_catalog) && cfg.model_catalog.length) ? cfg.model_catalog : (defInit.model_catalog || []),
    settings: settingsObj,
  };
}

// ---------- KV File Library & Imagine ----------
const FILE_SOURCES = ["uploaded", "generated", "downloaded"];
const FILE_TEXT_EXT = new Set([
  ".txt", ".md", ".markdown", ".csv", ".json", ".xml", ".yaml", ".yml", ".html", ".htm", ".py", ".dart", ".js", ".ts",
  ".css", ".sql", ".log", ".ini", ".toml", ".sh", ".bat", ".ps1", ".c", ".cpp", ".h", ".java", ".go", ".rs",
]);
const FILE_KINDS = {
  image: [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"],
  audio: [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"],
  video: [".mp4", ".webm", ".mov", ".mkv"],
  pdf: [".pdf"],
};
const MIME = {
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
  ".bmp": "image/bmp", ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg",
  ".m4a": "audio/mp4", ".flac": "audio/flac", ".aac": "audio/aac", ".mp4": "video/mp4", ".webm": "video/webm",
  ".mov": "video/quicktime", ".mkv": "video/x-matroska", ".pdf": "application/pdf", ".md": "text/markdown; charset=utf-8",
  ".markdown": "text/markdown; charset=utf-8", ".txt": "text/plain; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".csv": "text/csv; charset=utf-8", ".html": "text/html; charset=utf-8", ".htm": "text/html; charset=utf-8",
};

function safeName(name) {
  const base = String(name || "").replace(/\\/g, "/").split("/").pop().trim() || "file";
  return base.replace(/[<>:"/\\|?*\x00-\x1f]/g, "_").slice(0, 120) || "file";
}
function extOf(name) {
  const s = String(name || "");
  const i = s.lastIndexOf(".");
  return i > 0 ? s.slice(i).toLowerCase() : "";
}
function fileKind(name) {
  const e = extOf(name);
  for (const [k, list] of Object.entries(FILE_KINDS)) if (list.includes(e)) return k;
  return FILE_TEXT_EXT.has(e) ? "text" : "file";
}
const mimeFor = (name) => MIME[extOf(name)] || "application/octet-stream";

function b64decode(text) {
  const bin = atob(String(text || "").replace(/\s+/g, ""));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function uniqueName(env, source, name) {
  const clean = safeName(name);
  const dot = clean.lastIndexOf(".");
  const base = dot > 0 ? clean.slice(0, dot) : clean;
  const ext = dot > 0 ? clean.slice(dot) : "";
  let candidate = clean;
  for (let i = 2; i < 100; i++) {
    const found = await env.STATE.list({ prefix: "file:" + source + "/" + candidate, limit: 1 }).catch(() => null);
    if (!found || !(found.keys || []).some((k) => k.name === "file:" + source + "/" + candidate)) return candidate;
    candidate = `${base} (${i})${ext}`;
  }
  return `${base} (${Date.now().toString(36)})${ext}`;
}

async function putFile(env, source, name, bytes, model = "") {
  const clean = safeName(name);
  const size = bytes.byteLength ?? bytes.length ?? 0;
  const value = bytes instanceof Uint8Array ? bytes.slice().buffer : bytes;
  await env.STATE.put("file:" + source + "/" + clean, value, {
    metadata: { size, modified: Date.now() / 1000, kind: fileKind(clean), model: String(model || "") },
  });
  return clean;
}

async function saveFile(env, source, name, bytes, model = "") {
  return putFile(env, source, await uniqueName(env, source, name), bytes, model);
}

async function listFiles(env) {
  const out = { uploaded: [], generated: [], downloaded: [] };
  let cursor;
  do {
    const page = await env.STATE.list({ prefix: "file:", cursor });
    for (const k of page.keys || []) {
      const rest = k.name.slice(5);
      const at = rest.indexOf("/");
      if (at < 0) continue;
      const source = rest.slice(0, at);
      if (!out[source]) continue;
      const name = rest.slice(at + 1);
      const md = k.metadata || {};
      out[source].push({
        name,
        source,
        size: md.size || 0,
        modified: md.modified || 0,
        kind: md.kind || fileKind(name),
        url: "/files/" + source + "/" + encodeURIComponent(name),
        model: md.model || "",
      });
    }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  for (const s of FILE_SOURCES) out[s].sort((a, b) => b.modified - a.modified);
  return out;
}

async function fileBytes(env, source, name) {
  if (!FILE_SOURCES.includes(source)) return null;
  try {
    return await env.STATE.get("file:" + source + "/" + safeName(name), "arrayBuffer");
  } catch (_) {
    return null;
  }
}

async function serveFile(env, source, name, request) {
  const buf = await fileBytes(env, source, name);
  if (!buf) return new Response("", { status: 404 });
  const clean = safeName(name);
  const size = buf.byteLength;
  const headers = {
    "Content-Type": mimeFor(clean),
    "Cache-Control": "private, max-age=3600",
    "Accept-Ranges": "bytes",
    "Content-Length": String(size),
  };
  return new Response(buf, { headers });
}

// ---------- In-App Browser Proxy (/api/page & /api/fetch) ----------
const BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";

const PAGE_SCRIPT_TEMPLATE = `<script>(function(){
var REAL=__REAL__,O=location.origin,P=O+'/api/page?url=',F=O+'/api/fetch?url=';
function abs(u){try{return new URL(u,REAL).toString()}catch(e){return u}}
function go(u){location.href=P+encodeURIComponent(abs(u))}
function report(){try{parent.postMessage({collider:'nav',url:REAL,title:document.title||''},'*')}catch(e){}}
report();document.addEventListener('DOMContentLoaded',report);window.addEventListener('load',report);
document.addEventListener('click',function(e){
 if(e.defaultPrevented||e.button)return;
 var a=e.target&&e.target.closest&&e.target.closest('a[href]');if(!a)return;
 var h=a.getAttribute('href');if(!h||/^(javascript|mailto|tel|data|blob):/i.test(h))return;
 if(h.charAt(0)==='#'){e.preventDefault();var t=document.getElementById(h.slice(1))||document.getElementsByName(h.slice(1))[0];if(t)t.scrollIntoView();return}
 var u=abs(h);if(!/^https?:/.test(u))return;
 e.preventDefault();e.stopPropagation();go(u);
},true);
document.addEventListener('submit',function(e){
 var f=e.target,m=(f.getAttribute('method')||'get').toLowerCase(),act=abs(f.getAttribute('action')||REAL);
 e.preventDefault();
 if(m==='get'||/(^|\\.)duckduckgo\\.com$/.test(new URL(act).hostname)){var u=new URL(act);u.search='';new FormData(f).forEach(function(v,k){if(typeof v==='string')u.searchParams.append(k,v)});go(u.toString())}
 else{var pf=document.createElement('form');pf.method='post';pf.action=P+encodeURIComponent(act);pf.style.display='none';
  new FormData(f).forEach(function(v,k){if(typeof v==='string'){var i=document.createElement('input');i.type='hidden';i.name=k;i.value=v;pf.appendChild(i)}});
  document.documentElement.appendChild(pf);sub.call(pf)}
},true);
window.open=function(u){if(u)go(u);return null};
var sub=HTMLFormElement.prototype.submit;HTMLFormElement.prototype.submit=function(){var e=new Event('submit',{bubbles:true,cancelable:true});if(this.dispatchEvent(e))sub.call(this)};
if(window.navigation)navigation.addEventListener('navigate',function(e){var u=e.destination&&e.destination.url;if(e.cancelable&&u&&/^https?:/.test(u)&&u.indexOf(O)!==0){e.preventDefault();go(u)}});
['pushState','replaceState'].forEach(function(k){var o=history[k];history[k]=function(s,t){try{return o.call(history,s,t)}catch(e){}}});
function via(u){var a=abs(u);return(/^https?:/.test(a)&&a.indexOf(O)!==0)?F+encodeURIComponent(a):u}
var of=window.fetch;if(of){window.fetch=function(i,n){try{if(typeof i==='string')i=via(i);else if(i&&i.url)i=new Request(via(i.url),i)}catch(e){}return of.call(window,i,n)}}
var oo=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u){try{arguments[1]=via(u)}catch(e){}return oo.apply(this,arguments)};
})();</script>`;

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function prepareHtml(html, finalUrl) {
  let out = String(html || "")
    .replace(/<meta[^>]+http-equiv=["']?Content-Security-Policy[^>]*>/gi, "")
    .replace(/<base\b[^>]*>/gi, "");
  const safeFinal = String(finalUrl || "").replace(/"/g, "%22");
  const bars = "<style>html{scrollbar-width:none}html::-webkit-scrollbar,body::-webkit-scrollbar{width:0;height:0;display:none}</style>";
  const inject = `<base href="${safeFinal}">` + bars + PAGE_SCRIPT_TEMPLATE.replace("__REAL__", JSON.stringify(finalUrl));
  const m = /<head[^>]*>/i.exec(out);
  if (m) {
    const idx = m.index + m[0].length;
    return out.slice(0, idx) + inject + out.slice(idx);
  }
  return inject + out;
}

function searchHomePage() {
  return (
    '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>Google</title><style>' +
    'body{margin:0;padding:36px 18px 24px;font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#202124;background:#fff;display:flex;flex-direction:column;align-items:center}' +
    '.logo{font-size:42px;font-weight:700;letter-spacing:-1px;margin:18px 0 22px;user-select:none}' +
    '.logo span:nth-child(1){color:#4285F4}.logo span:nth-child(2){color:#EA4335}.logo span:nth-child(3){color:#FBBC05}' +
    '.logo span:nth-child(4){color:#4285F4}.logo span:nth-child(5){color:#34A853}.logo span:nth-child(6){color:#EA4335}' +
    'form{width:100%;max-width:480px;display:flex;gap:8px;margin-bottom:26px}' +
    'input{flex:1;min-width:0;font:16px inherit;padding:12px 16px;border:1px solid #dfe1e5;border-radius:24px;outline:none;box-shadow:0 1px 6px rgba(32,33,36,.12)}' +
    'button{padding:0 18px;border-radius:24px;border:1px solid #dadce0;background:#f8f9fa;color:#3c4043;font:600 14px inherit;cursor:pointer}' +
    '.grid{width:100%;max-width:480px;display:grid;grid-template-columns:repeat(2,1fr);gap:10px}' +
    '.card{display:flex;flex-direction:column;padding:12px 14px;border-radius:14px;background:#f8f9fa;border:1px solid #eef0f2;text-decoration:none;color:#202124}' +
    '.card b{font-size:14px;color:#1a73e8;margin-bottom:2px}.card span{font-size:12px;color:#5f6368}' +
    '</style></head><body>' +
    '<div class="logo"><span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span></div>' +
    '<form action="https://www.google.com/search" method="get"><input name="q" placeholder="Search the web or enter a topic..." autofocus><button type="submit">Search</button></form>' +
    '<div class="grid">' +
    '<a class="card" href="https://en.wikipedia.org/wiki/Main_Page"><b>Wikipedia</b><span>Free Encyclopedia</span></a>' +
    '<a class="card" href="https://news.ycombinator.com/"><b>Hacker News</b><span>Tech &amp; Startup News</span></a>' +
    '<a class="card" href="https://www.google.com/search?q=spatial+computing+visionOS"><b>Spatial Computing</b><span>Search visionOS &amp; Optics</span></a>' +
    '<a class="card" href="https://arxiv.org/"><b>arXiv.org</b><span>Open-Access Research</span></a>' +
    '</div></body></html>'
  );
}

function resultsPage(query, results) {
  const rows = (results || [])
    .filter((r) => r && r.url)
    .map((r) => {
      let host = "";
      try {
        host = new URL(r.url).hostname;
      } catch (_) {}
      const excerpt = String(r.content || "")
        .replace(/[#*`|>]+/g, " ")
        .replace(/\s+/g, " ")
        .trim()
        .slice(0, 220);
      return `<div class="r"><a href="${escapeHtml(r.url)}">${escapeHtml(r.title || r.url)}</a><div class="u">${escapeHtml(host)}</div><p>${escapeHtml(excerpt)}</p></div>`;
    })
    .join("");
  return (
    '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    `<title>${escapeHtml(query)} - Search</title><style>` +
    'body{margin:0;padding:14px 16px;font:15px/1.45 system-ui,"Segoe UI",sans-serif;color:#222;background:#f7f7f7}' +
    'form{display:flex;margin:0 0 14px}input{flex:1;min-width:0;font:inherit;padding:10px 12px;border:1px solid #d0d0d0;border-radius:6px;background:#fff}' +
    '.r{background:#fff;border-radius:8px;padding:12px 14px;margin:0 0 10px}.r a{color:#1a3fb0;font-size:17px;text-decoration:none}' +
    '.u{color:#20692b;font-size:13px;margin:2px 0 4px;overflow-wrap:anywhere}.r p{margin:0;color:#444}</style></head><body>' +
    `<form action="https://www.google.com/search" method="get"><input name="q" value="${escapeHtml(query)}" placeholder="Search the web..."></form>` +
    rows +
    "</body></html>"
  );
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // ---- Interactive /config page (online permanent configuration UI) ----
    if ((path === "/config" || path === "/configurator.html") && request.method === "GET") {
      const cfg = await loadLiveConfig(env);
      const initial = buildFormInitial(cfg);
      const html = formBundle.form
        .replace("WHERE", JSON.stringify("Cloudflare Edge KV (collider-argon-6420)"))
        .replace("INITIAL", JSON.stringify(initial));
      return new Response(html, {
        status: 200,
        headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
      });
    }

    if (path === "/api/config/data" && request.method === "GET") {
      const cfg = await loadLiveConfig(env);
      return json(buildFormInitial(cfg));
    }

    if (path === "/api/config" && request.method === "POST") {
      const b = await request.json().catch(() => ({}));
      const cur = await loadLiveConfig(env);
      const rawProvs = Array.isArray(b.providers)
        ? b.providers
        : Array.isArray(b.api_providers_and_keys)
          ? b.api_providers_and_keys
          : cur.providers;
      const cleanProvs = (rawProvs || [])
        .filter((r) => r && (r.provider_name || r.api_endpoint_url || r.api_key || r.name || r.endpoint || r.key))
        .map((r) => ({
          provider_name: r.provider_name || r.name || "NVIDIA",
          api_endpoint_url: r.api_endpoint_url || r.endpoint || r.url || "",
          api_key: r.api_key || r.key || "",
          extra_model_ids: r.extra_model_ids || r.models || "",
          name: r.provider_name || r.name || "NVIDIA",
          endpoint: r.api_endpoint_url || r.endpoint || r.url || "",
          key: r.api_key || r.key || "",
          models: r.extra_model_ids || r.models || "",
        }));
      const next = {
        ...cur,
        ...(b.settings || {}),
        localhost_port: Number(b.host) || cur.localhost_port || 6420,
        providers: cleanProvs,
        themes: String(b.themes || "").trim() || cur.themes,
        store_bypass: Boolean(b.bypass),
      };
      await env.STATE.put("argon6420:config", JSON.stringify(next));
      const roster = next.models || DEFAULT_ROSTER;
      return json({ ok: true, uses: cleanProvs.map((r) => providerUses(r, roster)) });
    }

    // ---- API ----
    if (path === "/api/whoami") return json({ root: "cloudflare-argon-6420", port: 443 });
    if (path === "/api/phone") return json({ link: url.origin, qr: "" });
    if (path === "/api/themes") return json(themeList());
    if (path === "/api/models") {
      const cfg = await loadLiveConfig(env);
      return json(describeModels(cfg));
    }
    if (path === "/api/store") {
      const cfg = await loadLiveConfig(env);
      return json({ bypass: Boolean(cfg.store_bypass) });
    }
    if (path === "/api/history") return json({ sessions: await loadHistory(env) });
    if (path === "/api/smartgen") return json({ cards: await loadSmartgen(env) });
    if (path === "/api/jobs") return json([]);

    if (path === "/api/lines" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const sid = body.id;
      const raw = await env.STATE.get("argon6420:job:" + sid);
      const found = raw ? JSON.parse(raw) : (await loadHistory(env)).find((s) => s.id === sid);
      return found ? json({ ...stripThreads(found), status: "done" }) : json({ error: "not found" }, 404);
    }

    if (path.startsWith("/api/job/")) {
      const jid = path.split("/").pop();
      const raw = await env.STATE.get("argon6420:job:" + jid);
      if (raw) return json(stripThreads(JSON.parse(raw)));
      const found = (await loadHistory(env)).find((s) => s.id === jid);
      return found ? json({ ...found, status: "done", stage: "done" }) : json({ error: "not found" }, 404);
    }

    if (path === "/api/ask" && request.method === "POST") {
      const cfg = await loadLiveConfig(env);
      const body = await request.json().catch(() => ({}));
      let prior = null;
      const sid = String(body.session_id || "").trim();
      if (sid) {
        const raw = await env.STATE.get("argon6420:job:" + sid);
        prior = raw ? JSON.parse(raw) : (await loadHistory(env)).find((s) => s.id === sid) || null;
      }
      const { job, priorThreads } = newJob(cfg, body, prior);
      await env.STATE.put("argon6420:job:" + job.id, JSON.stringify({ ...job, priorThreads }), { expirationTtl: 86400 });
      return json({ id: job.id, ...job });
    }

    if (path.startsWith("/api/stream/") && !path.startsWith("/api/stream/r/")) {
      const jid = path.split("/").pop();
      const raw = await env.STATE.get("argon6420:job:" + jid);
      let job = raw ? JSON.parse(raw) : null;
      if (!job) {
        const found = (await loadHistory(env)).find((s) => s.id === jid);
        if (found) job = { ...found, status: "done", stage: "done" };
      }
      if (!job) {
        return sseFrom((c) => {
          c.enqueue(new TextEncoder().encode("event: gone\ndata: {}\n\n"));
          c.close();
        });
      }
      const cfg = await loadLiveConfig(env);
      return sseFrom((controller) => {
        const enc = new TextEncoder();
        let closed = false;
        const send = (t) => {
          if (closed) return;
          try {
            controller.enqueue(enc.encode(t));
          } catch (_) {
            closed = true;
          }
        };
        send(": open\n\n");
        (async () => {
          let last = "";
          const push = () => {
            const s = JSON.stringify(stripThreads(job));
            if (s === last) return;
            last = s;
            send("data: " + s + "\n\n");
          };
          const persist = async () => {
            try {
              await env.STATE.put("argon6420:job:" + job.id, JSON.stringify({ ...job, priorThreads: job.priorThreads || {} }), {
                expirationTtl: 86400,
              });
            } catch (_) {}
          };
          push();
          if (job.status !== "done" && job.status !== "error") {
            const hb = setInterval(() => send(": ping\n\n"), 5000);
            try {
              await runJob(env, cfg, job, job.priorThreads || {}, () => {
                push();
                persist();
              });
            } catch (e) {
              job.status = "error";
              job.stage = "done";
              job.error = String((e && e.message) || e).slice(0, 200);
            } finally {
              clearInterval(hb);
              await persist();
            }
          }
          push();
          send("event: end\ndata: {}\n\n");
          closed = true;
          try {
            controller.close();
          } catch (_) {}
        })();
      });
    }

    if (path === "/api/reply" && request.method === "POST") {
      const cfg = await loadLiveConfig(env);
      const body = await request.json().catch(() => ({}));
      try {
        return json(await makeReply(cfg, body));
      } catch (e) {
        return json({ ok: false, error: String((e && e.message) || e).slice(0, 200) }, 200);
      }
    }

    if (path === "/api/reply/start" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const rid = crypto.randomUUID().replace(/-/g, "").slice(0, 12);
      const rec = { id: rid, status: "running", created: Date.now() / 1000, text: "", line: "", messages: [], body };
      await env.STATE.put("argon6420:reply:" + rid, JSON.stringify(rec), { expirationTtl: 86400 });
      return json({ id: rid, status: "running", text: "", line: "", messages: [] });
    }

    if (path.startsWith("/api/stream/r/")) {
      const rid = path.split("/").pop();
      const raw = await env.STATE.get("argon6420:reply:" + rid);
      if (!raw) {
        return sseFrom((c) => {
          c.enqueue(new TextEncoder().encode("event: gone\ndata: {}\n\n"));
          c.close();
        });
      }
      const rec = JSON.parse(raw);
      const cfg = await loadLiveConfig(env);
      return sseFrom((controller) => {
        const enc = new TextEncoder();
        let closed = false;
        const send = (t) => {
          if (closed) return;
          try {
            controller.enqueue(enc.encode(t));
          } catch (_) {
            closed = true;
          }
        };
        send(": open\n\n");
        (async () => {
          let current = rec;
          if (rec.status !== "done" && rec.status !== "error") {
            const hb = setInterval(() => send(": ping\n\n"), 5000);
            try {
              const out = await makeReply(cfg, rec.body || {});
              current = { id: rid, status: "done", ...out };
            } catch (e) {
              current = { id: rid, status: "error", error: String((e && e.message) || e).slice(0, 200), text: "", line: "", messages: [] };
            } finally {
              clearInterval(hb);
            }
            try {
              await env.STATE.put("argon6420:reply:" + rid, JSON.stringify(current), { expirationTtl: 86400 });
            } catch (_) {}
          }
          send("data: " + JSON.stringify(stripBody(current)) + "\n\n");
          send("event: end\ndata: {}\n\n");
          closed = true;
          try {
            controller.close();
          } catch (_) {}
        })();
      });
    }

    if (path.startsWith("/api/reply/") && request.method === "GET") {
      const raw = await env.STATE.get("argon6420:reply:" + path.split("/").pop());
      return raw ? json(JSON.parse(raw)) : json({ error: "not found" }, 404);
    }

    if (path === "/api/transcribe" && request.method === "POST") {
      const cfg = await loadLiveConfig(env);
      const body = await request.json().catch(() => ({}));
      const speech = (cfg.providers || []).map(normalizeProvider).find((p) => p.speech && p.key);
      if (!speech || !body.b64) return json({ text: "" });
      try {
        const bytes = Uint8Array.from(atob(body.b64), (ch) => ch.charCodeAt(0));
        const mime = String(body.mime || "audio/webm").split(";")[0];
        const ext = { "audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/wav": "wav", "audio/mpeg": "mp3" }[mime] || "webm";
        const form = new FormData();
        form.append("model", String((speech.models && speech.models[0]) || "whisper-large-v3-turbo"));
        form.append("response_format", "json");
        form.append("file", new Blob([bytes], { type: mime }), "speech." + ext);
        const r = await fetch(speech.url, {
          method: "POST",
          headers: { Authorization: "Bearer " + String(speech.key).trim() },
          body: form,
          signal: AbortSignal.timeout(60000),
        });
        const j = await r.json();
        return json({ text: String(j.text || "").trim() });
      } catch (_) {
        return json({ text: "" });
      }
    }

    // ---- Files: upload, generated notes, downloads, listing, serving ----
    if (path === "/api/files" && request.method === "GET") {
      return json(await listFiles(env));
    }

    if (path === "/api/files/thumb" && request.method === "GET") {
      const source = url.searchParams.get("source") || "";
      const name = safeName(url.searchParams.get("name") || "");
      if (!FILE_SOURCES.includes(source) || fileKind(name) !== "image") return new Response("", { status: 404 });
      const buf = await fileBytes(env, source, name);
      if (!buf) return new Response("", { status: 404 });
      return new Response(buf, { headers: { "Content-Type": mimeFor(name), "Cache-Control": "private, max-age=3600" } });
    }

    if (path === "/api/files/upload" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      try {
        const bytes = b64decode(body.b64 || "");
        if (!bytes.length) return json({ error: "empty" }, 400);
        const name = await saveFile(env, "uploaded", body.name || "file", bytes, "");
        return json({ name });
      } catch (e) {
        return json({ error: String((e && e.message) || e).slice(0, 120) }, 500);
      }
    }

    if (path === "/api/files/generated" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      try {
        const bytes = new TextEncoder().encode(String(body.text || ""));
        const name = await saveFile(env, "generated", body.name || "note.md", bytes, String(body.model || ""));
        return json({ name });
      } catch (e) {
        return json({ error: String((e && e.message) || e).slice(0, 120) }, 500);
      }
    }

    if (path === "/api/files/save" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      try {
        const bytes = b64decode(body.b64 || "");
        const wanted = safeName(body.name || "document.docx");
        const name = await saveFile(env, "generated", wanted, bytes, String(body.model || "Documents"));
        return json({ name });
      } catch (e) {
        return json({ error: String((e && e.message) || e).slice(0, 120) }, 500);
      }
    }

    if (path === "/api/files/download" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      let target = String(body.url || "").trim();
      if (!target) return json({ error: "bad url" }, 400);
      if (!/^https?:\/\//i.test(target)) {
        target = new URL(target.startsWith("/") ? target : "/assets/" + target, url.origin).toString();
      }
      try {
        let r;
        const targetUrl = new URL(target);
        if (targetUrl.origin === url.origin && env.ASSETS) {
          r = await env.ASSETS.fetch(new Request(targetUrl.toString()));
        } else {
          r = await fetch(target, {
            headers: { "User-Agent": BROWSER_UA },
            signal: AbortSignal.timeout(60000),
          });
        }
        if (!r.ok) return json({ error: "HTTP " + r.status }, 502);
        const bytes = new Uint8Array(await r.arrayBuffer());
        let name = "";
        const disp = r.headers.get("Content-Disposition") || "";
        const m = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(disp);
        if (m) {
          try {
            name = decodeURIComponent(m[1]);
          } catch (_) {
            name = m[1];
          }
        }
        if (!name) {
          try {
            const pathname = new URL(r.url || target).pathname;
            name = decodeURIComponent(pathname.split("/").filter(Boolean).pop() || "");
          } catch (_) {}
        }
        if (!extOf(name)) {
          const ct = (r.headers.get("Content-Type") || "").toLowerCase();
          if (ct.includes("jpeg") || ct.includes("jpg")) name = (name || "image") + ".jpg";
          else if (ct.includes("png")) name = (name || "image") + ".png";
          else if (ct.includes("webp")) name = (name || "image") + ".webp";
        }
        const saved = await saveFile(env, "downloaded", name || "download.jpg", bytes, "");
        return json({ name: saved });
      } catch (e) {
        return json({ error: String((e && e.message) || e).slice(0, 120) }, 502);
      }
    }

    if (path.startsWith("/files/")) {
      const bits = path.slice(7).split("/");
      let source = "", name = "";
      try {
        source = decodeURIComponent(bits.shift() || "");
        name = decodeURIComponent(bits.join("/") || "");
      } catch (_) {
        return new Response("", { status: 400 });
      }
      return serveFile(env, source, name, request);
    }

    if (path.startsWith("/api/files/")) return json({ ok: true });

    if (path === "/api/imagine") {
      try {
        const raw = await env.STATE.get("imagine");
        const items = raw ? JSON.parse(raw) : [];
        return json({ items: Array.isArray(items) ? items : [], models: [] });
      } catch (_) {
        return json({ items: [], models: [] });
      }
    }

    // ---- In-App Browser (/api/fetch & /api/page) ----
    if (path === "/api/fetch") {
      let target = url.searchParams.get("url") || "";
      if (!target) return new Response("", { status: 400 });
      if (!/^https?:\/\//i.test(target)) target = "https://" + target;
      try {
        const r = await fetch(target, {
          method: request.method,
          headers: { "User-Agent": BROWSER_UA, Accept: "*/*" },
          body: request.method !== "GET" && request.method !== "HEAD" ? await request.arrayBuffer() : undefined,
          signal: AbortSignal.timeout(25000),
        });
        return new Response(await r.arrayBuffer(), {
          status: r.status || 200,
          headers: {
            "Content-Type": r.headers.get("Content-Type") || "application/octet-stream",
            "Cache-Control": "no-store",
            "Access-Control-Allow-Origin": "*",
          },
        });
      } catch (e) {
        return new Response(String((e && e.message) || e).slice(0, 200), { status: 502 });
      }
    }

    if (path === "/api/page") {
      let target = (url.searchParams.get("url") || "").trim();
      if (!target) return new Response("", { status: 400 });
      if (!/^https?:\/\//i.test(target)) target = "https://" + target;
      const ddgMatch = /^https?:\/\/(?:www\.)?duckduckgo\.com\/\?(.*)$/i.exec(target);
      if (ddgMatch) target = "https://html.duckduckgo.com/html/?" + ddgMatch[1];

      try {
        let parsedTarget = new URL(target);
        if (parsedTarget.hostname.endsWith("duckduckgo.com") && parsedTarget.pathname.startsWith("/l/")) {
          const uddg = parsedTarget.searchParams.get("uddg");
          if (uddg) {
            target = uddg;
            parsedTarget = new URL(target);
          }
        }
      } catch (_) {}

      let origQuery = "";
      let isBareSearchHome = false;
      try {
        const parsedOrig = new URL(target);
        const oh = parsedOrig.hostname.toLowerCase();
        origQuery = parsedOrig.searchParams.get("q") || "";
        if (
          (oh === "google.com" || oh === "www.google.com" || oh === "duckduckgo.com" || oh === "www.duckduckgo.com") &&
          (parsedOrig.pathname === "/" || parsedOrig.pathname === "" || parsedOrig.pathname === "/webhp") &&
          !origQuery
        ) {
          isBareSearchHome = true;
        }
      } catch (_) {}

      if (isBareSearchHome) {
        const html = prepareHtml(searchHomePage(), "https://www.google.com/");
        return new Response(html, {
          status: 200,
          headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
        });
      }

      if (origQuery) {
        try {
          const parsedOrig = new URL(target);
          const oh = parsedOrig.hostname.toLowerCase();
          if (oh.includes("google.") || oh.endsWith("duckduckgo.com")) {
            const cfg = await loadLiveConfig(env);
            const found = await webSearch(cfg, origQuery, "internet");
            if (found && found.length) {
              const html = prepareHtml(resultsPage(origQuery, found), target);
              return new Response(html, {
                status: 200,
                headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
              });
            }
          }
        } catch (_) {}
      }

      try {
        const r = await fetch(target, {
          method: request.method,
          headers: {
            "User-Agent": BROWSER_UA,
            "Accept-Language": "en-US,en;q=0.9",
            Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          },
          body: request.method !== "GET" && request.method !== "HEAD" ? await request.arrayBuffer() : undefined,
          signal: AbortSignal.timeout(30000),
        });
        const finalUrl = r.url || target;
        const ctype = r.headers.get("Content-Type") || "text/html";
        if (ctype.toLowerCase().includes("html")) {
          let text = await r.text();
          let host = "";
          let q = origQuery;
          try {
            const u = new URL(finalUrl);
            host = u.hostname.toLowerCase();
            if (!q) q = u.searchParams.get("q") || "";
            if (!q && u.searchParams.get("continue")) {
              const cont = new URL(u.searchParams.get("continue"));
              q = cont.searchParams.get("q") || "";
            }
          } catch (_) {}
          const isChallenge =
            (host.endsWith("duckduckgo.com") && (text.includes("anomaly-modal") || text.includes("bots use DuckDuckGo"))) ||
            (host.includes("google.") && (text.includes("/httpservice/retry/enablejs") || text.includes("unusual traffic") || text.includes("g-recaptcha") || finalUrl.includes("/sorry/")));
          if (isChallenge) {
            if (q) {
              const cfg = await loadLiveConfig(env);
              const found = await webSearch(cfg, q, "internet");
              if (found && found.length) {
                text = resultsPage(q, found);
              } else {
                text = searchHomePage();
              }
            } else {
              text = searchHomePage();
            }
          }
          const html = prepareHtml(text, finalUrl);
          return new Response(html, {
            status: 200,
            headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
          });
        }
        return new Response(await r.arrayBuffer(), {
          status: 200,
          headers: { "Content-Type": ctype, "Cache-Control": "no-store" },
        });
      } catch (e) {
        const errHtml =
          "<html><body style='font:15px system-ui;padding:24px;color:#464652;background:#E1E8EB'>" +
          `<div>${escapeHtml(target)}</div><div style='color:#7F7F7F;margin-top:8px'>${escapeHtml(String((e && e.message) || e).slice(0, 160))}</div>` +
          `<script>try{parent.postMessage({collider:'nav',url:${JSON.stringify(target)},title:''},'*')}catch(e){}</script></body></html>`;
        return new Response(errHtml, {
          status: 200,
          headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
        });
      }
    }

    // ---- Static Flutter Web App & Dashboard Assets ----
    return env.ASSETS.fetch(request);
  },
};

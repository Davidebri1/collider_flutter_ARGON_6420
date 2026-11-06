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

  return {
    ...defs,
    ...(kvCfg || {}),
    providers: provs,
    models: (kvCfg && Array.isArray(kvCfg.models) && kvCfg.models.length) ? kvCfg.models : DEFAULT_ROSTER,
    themes: (kvCfg && kvCfg.themes) || "https://collider-themes.ebridavid.workers.dev",
    store_bypass: Boolean(kvCfg && kvCfg.store_bypass),
  };
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
];

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // ---- Interactive /config page (online permanent configuration UI) ----
    if (path === "/config" && request.method === "GET") {
      const cfg = await loadLiveConfig(env);
      const provs = cfg.providers || [];
      const roster = cfg.models || DEFAULT_ROSTER;
      const settingsObj = {};
      for (const k of SETTINGS_KEYS) {
        if (k in cfg) settingsObj[k] = cfg[k];
      }
      const initial = {
        host: "",
        providers: provs,
        themes: cfg.themes || "https://collider-themes.ebridavid.workers.dev",
        bypass: Boolean(cfg.store_bypass),
        uses: provs.map((r) => providerUses(r, roster)),
        settings: settingsObj,
      };
      const html = formBundle.form
        .replace("WHERE", JSON.stringify("Cloudflare Edge KV (collider-argon-6420)"))
        .replace("INITIAL", JSON.stringify(initial));
      return new Response(html, {
        status: 200,
        headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
      });
    }

    if (path === "/api/config" && request.method === "POST") {
      const b = await request.json().catch(() => ({}));
      const cur = await loadLiveConfig(env);
      const next = {
        ...cur,
        ...(b.settings || {}),
        providers: Array.isArray(b.providers)
          ? b.providers.filter((r) => r && (r.name || r.endpoint || r.key))
          : cur.providers,
        themes: String(b.themes || "").trim() || cur.themes,
        store_bypass: Boolean(b.bypass),
      };
      await env.STATE.put("argon6420:config", JSON.stringify(next));
      return json({ ok: true });
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

    if (path === "/api/files") return json({ uploaded: [], generated: [], downloaded: [] });
    if (path === "/api/files/thumb") return new Response("", { status: 404 });
    if (path.startsWith("/api/files/")) return json({ ok: true });
    if (path === "/api/imagine") {
      if (request.method === "POST") return json({ ok: true, items: [] });
      return json({ items: [], models: [] });
    }

    if (path === "/api/page") {
      const target = url.searchParams.get("url") || "";
      if (!/^https?:\/\//i.test(target)) return new Response("", { status: 400 });
      try {
        const r = await fetch(target, {
          headers: { "User-Agent": "Mozilla/5.0 (compatible; Collider/1.0)", Accept: "text/html,*/*" },
          signal: AbortSignal.timeout(30000),
        });
        const bodyText = await r.text();
        return new Response(bodyText, {
          status: 200,
          headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
        });
      } catch (_) {
        return new Response("", { status: 502 });
      }
    }

    // ---- Static Flutter Web App & Dashboard Assets ----
    return env.ASSETS.fetch(request);
  },
};

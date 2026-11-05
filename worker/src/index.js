// Collider on Cloudflare: the app's assets and its API, one origin.
// A port of tools/collider_server.py to a Worker: same endpoints, same JSON shapes, same SSE contract.
import themesCache from "../themes.json";

// Only models this account can actually answer with: each id below was called and replied.
const ROSTER = [
  { id: "nvidia/nemotron-3.5-bolt-e4b", label: "Nemotron 3.5 Bolt", short: "NBLT", provider: "NVIDIA", via: "NVIDIA", color: "#76B900" },
  { id: "nvidia/nemotron-3.5-lightning-30b-a3b", label: "Nemotron 3.5 Lightning", short: "N35L", provider: "NVIDIA", via: "NVIDIA", color: "#A3E635" },
  { id: "nvidia/nemotron-3-ultra-550b-a55b", label: "Nemotron 3 Ultra", short: "N3U", provider: "NVIDIA", via: "NVIDIA", color: "#4ADE80" },
  { id: "nvidia/nemotron-3.5-super-vl-120b-a12b", label: "Nemotron 3.5 Super", short: "N35S", provider: "NVIDIA", via: "NVIDIA", color: "#22C55E" },
  { id: "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", label: "Nemotron 3 Nano", short: "N3N", provider: "NVIDIA", via: "NVIDIA", color: "#34D399" },
  { id: "meta/muse-glimmer-30b", label: "Muse Glimmer 30B", short: "MG30", provider: "Meta", via: "NVIDIA", color: "#A78BFA" },
  { id: "meta/llama-3.2-90b-vision-instruct", label: "Llama 3.2 90B Vision", short: "L90", provider: "Meta", via: "NVIDIA", color: "#818CF8" },
  { id: "minimaxai/minimax-m3.1-flash", label: "MiniMax M3.1 Flash", short: "MM31", provider: "MiniMax", via: "NVIDIA", color: "#F472B6" },
  { id: "mistralai/mistral-large-4-1t-a52b", label: "Mistral Large 4", short: "ML4", provider: "Mistral", via: "NVIDIA", color: "#FB923C" },
  { id: "stepfun-ai/step-5-preview", label: "Step 5 Preview", short: "S5", provider: "StepFun", via: "NVIDIA", color: "#38BDF8" },
];
const CONSENSUS_AGENT = "nvidia/nemotron-3.5-bolt-e4b";
const AGENT_CHAIN = [CONSENSUS_AGENT, "nvidia/nemotron-3-ultra-550b-a55b", "mistralai/mistral-large-4-1t-a52b"];
const LABEL = Object.fromEntries(ROSTER.map((m) => [m.id, m.label]));

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
 "summaries": {"R1": "...", "R2": "..."},
 "groups": [["R1","R2","R4"],["R3"]],
 "consensus_summary": "..."}
summaries: each response's base minimal distinction/sentiment (the actionable portion of the message).
groups: the responses grouped by shared position, biggest group first.
consensus_summary: the position with the most responses, written in one line.`;

// ---------- text hygiene (same rules as the Python server) ----------
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

function cleanLine(t) {
  const first = plain(String(t || "").trim().split("\n")[0]).replace(/^["']|["']$/g, "").trim();
  return first.replace(/\u2026/g, "").replace(/\.\.\./g, "").trim();
}

function selfEssence(answer) {
  const paras = String(answer || "").trim().split("\n").map((p) => p.trim()).filter(Boolean);
  const target = paras[0] || "";
  return plain(target).split(/(?<=[.!?])\s/)[0].trim();
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
            if (obj && typeof obj === "object" && ("summaries" in obj || "chains" in obj || "create" in obj)) return obj;
          } catch (_) {}
          break;
        }
      }
    }
  }
  throw new Error("no json");
}

// ---------- providers ----------
let PROVIDERS = null;
function providers(env) {
  if (PROVIDERS) return PROVIDERS;
  try {
    PROVIDERS = JSON.parse(env.PROVIDERS_JSON || "[]");
  } catch (_) {
    PROVIDERS = [];
  }
  return PROVIDERS;
}

const turn = {};
function rowsFor(env, via) {
  const want = String(via || "NVIDIA").toLowerCase();
  const all = providers(env).filter((p) => {
    if (!p.key) return false;
    if (p.search || p.speech || p.imagine || p.phone) return false;
    return /chat\/completions|messages/.test(p.url || "");
  });
  let hit = all.filter((p) => String(p.name || "").toLowerCase() === want);
  if (!hit.length) hit = all.filter((p) => /nvidia/i.test(p.url || ""));
  return hit;
}

function nextRow(env, via) {
  const rs = rowsFor(env, via);
  if (!rs.length) return null;
  const k = String(via || "").toLowerCase();
  turn[k] = ((turn[k] ?? -1) + 1) % rs.length;
  return rs[turn[k]];
}

const VIA = Object.fromEntries(ROSTER.map((m) => [m.id, m.via || "NVIDIA"]));
const SYSTEM_OF = Object.fromEntries(ROSTER.map((m) => [m.id, m.system || ""]));

async function callModel(env, model, messages, maxTokens, timeoutMs = 150000) {
  const via = VIA[model] || "NVIDIA";
  const clean = sanitizeMessages(messages);
  let last = "no reply";
  for (let attempt = 0; attempt < RETRIES; attempt++) {
    const row = nextRow(env, via);
    if (!row) throw new Error("no key for " + via);
    try {
      const r = await fetch(row.url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + String(row.key).trim() },
        body: JSON.stringify({
          model,
          messages: clean,
          max_tokens: maxTokens + THINKING_TOKENS,
          temperature: TEMPERATURE,
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
      // A timed-out call is not worth a second full deadline: fail fast so the
      // rest of the job and the consensus are not held hostage.
      if (/timed out|abort/i.test(last)) break;
    }
  }
  throw new Error(last);
}

async function webSearch(env, query, mode) {
  const searcher = providers(env).find((p) => p.search && p.key);
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

// ---------- consensus ----------
async function runConsensus(env, prompt, answers) {
  const ids = Object.keys(answers);
  if (!ids.length) return null;
  const tags = {};
  ids.forEach((mid, i) => (tags["R" + (i + 1)] = mid));
  const body = ids.map((mid, i) => `R${i + 1}:\n${String(answers[mid]).slice(0, AGENT_CHARS)}`).join("\n\n");
  const msgs = [
    { role: "system", content: AGENT_PROMPT + "\n\n" + AGENT_FORMAT },
    { role: "user", content: `User's prompt:\n${prompt}\n\nResponse messages:\n\n${body}` },
  ];
  let agent = null;
  let out = null;
  for (const a of AGENT_CHAIN) {
    try {
      const text = await callModel(env, a, msgs, AGENT_TOKENS, AGENT_TIMEOUT);
      const parsed = parseJsonLoose(text);
      if (parsed && parsed.summaries) {
        agent = a;
        out = parsed;
        break;
      }
    } catch (_) {
      /* try the next judge */
    }
  }
  if (!out) return null;
  const summaries = {};
  for (const [t, v] of Object.entries(out.summaries || {})) {
    if (tags[t] && String(v).trim()) summaries[tags[t]] = plain(v);
  }
  if (!Object.keys(summaries).length) return null;
  let groups = (out.groups || []).map((g) => (g || []).map((t) => tags[t]).filter(Boolean)).filter((g) => g.length);
  const seen = new Set(groups.flat());
  for (const mid of Object.keys(summaries)) if (!seen.has(mid)) groups.push([mid]);
  groups.sort((a, b) => b.length - a.length);
  const win = groups[0] || [];
  const consensus = plain(out.consensus_summary || (win.length ? summaries[win[0]] : ""));
  return {
    agent,
    need: out.need || "",
    essences: summaries,
    lines: { ...summaries },
    chains: {},
    consensus_chain: 0,
    groups,
    summary: consensus,
    score: `${win.length}/${ids.length}`,
    dissent: groups.slice(1).map((g) => summaries[g[0]]).filter(Boolean),
    tie_basis: "",
  };
}

// ---------- jobs ----------
function newJob(body, priorSess) {
  const models = (body.models || []).filter((m) => LABEL[m]);
  const chosen = models.length ? models : [ROSTER[0].id];
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
    consensus: { summary: "", score: "", dissent: [] },
    save: body.autosave !== false,
    incognito: body.incognito === true,
    attachments: (body.attachments || []).slice(0, 12),
  };
  return { job, priorThreads };
}

async function runJob(env, job, priorThreads, onUpdate) {
  const prompt = job.prompt;
  const mode = job.mode;
  if (SEARCH[mode]) {
    job.stage = "searching";
    onUpdate();
    job.sources = await webSearch(env, prompt, mode);
  }
  job.stage = "answering";
  onUpdate();
  const system = DEPTH[mode] || DEPTH.chat;
  const src = sourcesBlock(job.sources);

  await Promise.all(
    job.models.map(async (mid) => {
      const prior = job.results[mid];
      // A reconnect resumes: what already answered is kept, not asked again.
      if (prior && prior.status === "done" && prior.text) return;
      const t0 = Date.now();
      const historyMsgs = priorThreads[mid] || [];
      const msgs = [
        { role: "system", content: (SYSTEM_OF[mid] ? SYSTEM_OF[mid] + "\n\n" : "") + system + (src ? "\n\n" + src : "") },
        ...historyMsgs,
        { role: "user", content: prompt },
      ];
      try {
        const text = await callModel(env, mid, msgs, MAX_TOKENS[mode] || 1200, DEADLINE[mode] || 100000);
        job.results[mid].status = "done";
        job.results[mid].text = text;
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
    const cons = Object.keys(answers).length ? await runConsensus(env, prompt, answers) : null;
    if (cons) {
      for (const [mid, e] of Object.entries(cons.essences)) if (job.results[mid]) job.results[mid].essence = e;
      for (const [mid, e] of Object.entries(cons.lines || {})) if (job.results[mid]) job.results[mid].line = e;
      cons.line = cons.summary || "";
      job.consensus = cons;
    } else {
      job.consensus = { summary: "", score: "", dissent: [] };
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
  await env.STATE.put("history", JSON.stringify(next));
}

async function loadHistory(env) {
  try {
    const raw = await env.STATE.get("history");
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  } catch (_) {
    return [];
  }
}

// ---------- replies ----------
async function makeReply(env, body, onUpdate, rec) {
  const mid = body.model;
  const raw = sanitizeMessages(body.messages || []);
  const msgs = [
    { role: "system", content: (SYSTEM_OF[mid] ? SYSTEM_OF[mid] + "\n\n" : "") + (DEPTH[body.mode || "chat"] || DEPTH.chat) },
    ...raw.map((m) => ({ ...m })),
  ];
  const text = (await callModel(env, mid, msgs, REPLY_TOKENS, 150000)).trim();
  const asked = [...raw].reverse().find((m) => m.role === "user");
  let line = "";
  try {
    const c = text ? await runConsensus(env, (asked && asked.content) || "", { [mid]: text }) : null;
    line = (c && c.lines && c.lines[mid]) || "";
  } catch (_) {}
  if (!line) line = selfEssence(text);
  const updated = sanitizeMessages([...raw, { role: "assistant", content: text }]);
  return { ok: true, text, essence: line, line, messages: updated };
}

// ---------- helpers ----------
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
  return typeof url === "string" && url.startsWith(R2) ? MEDIA + url.slice(R2.length) : url;
}

function themeList() {
  return (themesCache || []).map((t) => ({
    ...t,
    video: edge(t.video),
    poster: edge(t.poster),
    tracks: (t.tracks || []).map((s) => ({ ...s, url: edge(s.url) })),
  }));
}

function describeModels(env) {
  return {
    models: ROSTER,
    agent: CONSENSUS_AGENT,
    search: providers(env).some((p) => p.search && p.key),
    keys: providers(env).filter((p) => p.key && !p.search && !p.speech && !p.imagine && !p.phone).length,
  };
}

// ---------- the app-key gate (same behaviour as the local server) ----------
function gate(request, env, url) {
  const key = env.APP_KEY;
  if (!key) return null;
  if (url.searchParams.get("k") === key) return "ok";
  const cookie = request.headers.get("Cookie") || "";
  if (cookie.split(/;\s*/).includes("ck=" + key)) return "ok";
  return "denied";
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    const verdict = gate(request, env, url);
    const setCookie =
      verdict === "ok" && env.APP_KEY && url.searchParams.get("k") === env.APP_KEY
        ? { "Set-Cookie": `ck=${env.APP_KEY}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=31536000` }
        : {};

    if (verdict === "denied") {
      if (path.startsWith("/api/")) return json({ error: "key required" }, 403);
      return new Response("Collider: open this app with its link, which carries the key.", {
        status: 403,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    }

    const withCookie = (res) => {
      if (!Object.keys(setCookie).length) return res;
      const out = new Response(res.body, res);
      out.headers.set("Set-Cookie", setCookie["Set-Cookie"]);
      return out;
    };

    // ---- API ----
    if (path === "/api/whoami") return json({ root: "cloudflare", port: 0 });
    if (path === "/api/phone") return json({ link: "", qr: "" });
    if (path === "/api/models") return json(describeModels(env));
    if (path === "/api/themes") return json(themeList());
    if (path === "/api/store") return json({ bypass: false });
    if (path === "/api/history") return json({ sessions: await loadHistory(env) });
    if (path === "/api/smartgen") {
      const raw = await env.STATE.get("smartgen");
      return json({ cards: raw ? JSON.parse(raw) : [] });
    }
    if (path === "/api/jobs") return json([]);

    if (path.startsWith("/api/job/")) {
      const jid = path.split("/").pop();
      const raw = await env.STATE.get("job:" + jid);
      if (raw) return json(JSON.parse(raw));
      const found = (await loadHistory(env)).find((s) => s.id === jid);
      return found ? json({ ...found, status: "done", stage: "done" }) : json({ error: "not found" }, 404);
    }

    if (path === "/api/ask" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      let prior = null;
      const sid = String(body.session_id || "").trim();
      if (sid) {
        const raw = await env.STATE.get("job:" + sid);
        prior = raw ? JSON.parse(raw) : (await loadHistory(env)).find((s) => s.id === sid) || null;
      }
      const { job, priorThreads } = newJob(body, prior);
      await env.STATE.put("job:" + job.id, JSON.stringify({ ...job, priorThreads }), { expirationTtl: 86400 });
      return json(job);
    }

    if (path.startsWith("/api/stream/") && !path.startsWith("/api/stream/r/")) {
      const jid = path.split("/").pop();
      const raw = await env.STATE.get("job:" + jid);
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
      // The job runs inside this streaming request, which is what keeps the Worker
      // alive for it. Progress is written to KV, so a reconnect resumes where it stopped.
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
              await env.STATE.put("job:" + job.id, JSON.stringify({ ...job, priorThreads: job.priorThreads || {} }), {
                expirationTtl: 86400,
              });
            } catch (_) {}
          };
          push();
          if (job.status === "done" || job.status === "error") {
            // Already finished: nothing to run, just hand back the result.
          } else {
            const hb = setInterval(() => send(": ping\n\n"), 5000);
            try {
              await runJob(env, job, job.priorThreads || {}, () => {
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
      const body = await request.json().catch(() => ({}));
      try {
        return json(await makeReply(env, body));
      } catch (e) {
        return json({ ok: false, error: String((e && e.message) || e).slice(0, 200) }, 200);
      }
    }

    if (path === "/api/reply/start" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const rid = crypto.randomUUID().replace(/-/g, "").slice(0, 12);
      const rec = { id: rid, status: "running", created: Date.now() / 1000, text: "", line: "", messages: [], body };
      await env.STATE.put("reply:" + rid, JSON.stringify(rec), { expirationTtl: 86400 });
      return json({ id: rid, status: "running", text: "", line: "", messages: [] });
    }

    if (path.startsWith("/api/stream/r/")) {
      const rid = path.split("/").pop();
      const raw = await env.STATE.get("reply:" + rid);
      if (!raw) {
        return sseFrom((c) => {
          c.enqueue(new TextEncoder().encode("event: gone\ndata: {}\n\n"));
          c.close();
        });
      }
      const rec = JSON.parse(raw);
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
              const out = await makeReply(env, rec.body || {});
              current = { id: rid, status: "done", ...out };
            } catch (e) {
              current = { id: rid, status: "error", error: String((e && e.message) || e).slice(0, 200), text: "", line: "", messages: [] };
            } finally {
              clearInterval(hb);
            }
            try {
              await env.STATE.put("reply:" + rid, JSON.stringify(current), { expirationTtl: 86400 });
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
      const raw = await env.STATE.get("reply:" + path.split("/").pop());
      return raw ? json(JSON.parse(raw)) : json({ error: "not found" }, 404);
    }

    if (path === "/api/transcribe" && request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      const speech = providers(env).find((p) => p.speech && p.key);
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
      } catch (e) {
        return new Response("", { status: 502 });
      }
    }

    // ---- assets ----
    const res = await env.ASSETS.fetch(request);
    return withCookie(res);
  },
};

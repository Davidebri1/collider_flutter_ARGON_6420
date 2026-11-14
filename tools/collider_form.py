# E.D. — Collider — Signed: Gemini 4 Argon (2026-10-24)
"""The Collider Launch Configurator Form (Desktop Launch Window & <address>/config).

Redesigned so that:
1. Only relevant fields that actively govern app behavior are shown (zero dead or mystery fields).
2. Every field has an explicit, unambiguous title, unit (Seconds, Max Tokens, Max Characters, Attempts),
   and a plain-English consequence summary right at the form entry.
3. Decision-making uses dropdown selectors, ordered array selectors, color pickers, and a sorted, filterable
   API Keys & Models selector loaded directly from C:\\Users\\D\\Documents\\00_Config_and_Secrets\\API KEYS.txt.
"""

FORM = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Quorum — Launch Configurator</title>
<style>
:root {
  color-scheme: light dark;
  --bg: #F2F2F7;
  --card: #FFFFFF;
  --card-alt: #F9F9FB;
  --text: #111114;
  --sub: #5E5E66;
  --sep: rgba(60, 60, 67, 0.14);
  --field: #EFEFF4;
  --accent: #007AFF;
  --accent-soft: rgba(0, 122, 255, 0.11);
  --green: #34C759;
  --red: #FF3B30;
  --badge-bg: rgba(0, 122, 255, 0.12);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0B0C10;
    --card: #16181F;
    --card-alt: #1E2029;
    --text: #F5F5F7;
    --sub: #9898A2;
    --sep: rgba(255, 255, 255, 0.10);
    --field: #242731;
    --accent: #0A84FF;
    --accent-soft: rgba(10, 132, 255, 0.16);
    --green: #30D158;
    --red: #FF453A;
    --badge-bg: rgba(10, 132, 255, 0.18);
  }
}
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font: 14px/1.45 "Segoe UI Variable Text", "Segoe UI", -apple-system, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--sep);
  padding: 10px 18px;
}
.topbar-inner {
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand h1 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.brand span {
  font-size: 12px;
  color: var(--sub);
}
.nav-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.nav-pills a {
  text-decoration: none;
  color: var(--sub);
  background: var(--card);
  border: 1px solid var(--sep);
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 500;
}
.nav-pills a:hover {
  color: var(--text);
  border-color: var(--accent);
}
form {
  max-width: 860px;
  margin: 0 auto;
  padding: 16px 18px 48px;
}
.sec-head {
  margin: 26px 4px 8px;
}
.sec-head h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
}
.sec-head p {
  margin: 3px 0 0;
  font-size: 12.5px;
  color: var(--sub);
}
.card {
  background: var(--card);
  border: 1px solid var(--sep);
  border-radius: 14px;
  padding: 14px 16px;
  margin-bottom: 12px;
}
.host-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.host-left {
  flex: 1;
  min-width: 240px;
}
.host-left .lbl {
  font-weight: 600;
  font-size: 14.5px;
}
.host-left .desc {
  font-size: 12.5px;
  color: var(--sub);
  margin-top: 2px;
}
.host-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}
input.host-inp {
  font: 700 22px/1.1 "Segoe UI Variable Display", "Segoe UI", system-ui, sans-serif;
  width: 120px;
  text-align: center;
  background: var(--field);
  border: 1px solid var(--sep);
  border-radius: 10px;
  color: var(--text);
  padding: 7px 10px;
  outline: none;
}
input.host-inp:focus { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-soft); }
input.host-inp.bad { border-color: var(--red); color: var(--red); }

.btn {
  background: var(--field);
  color: var(--text);
  border: 1px solid var(--sep);
  border-radius: 9px;
  padding: 7px 12px;
  font: 600 12.5px/1.2 inherit;
  cursor: pointer;
}
.btn:hover { border-color: var(--accent); }
.btn-accent {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.btn-accent:hover { opacity: 0.92; }
.btn-danger {
  background: transparent;
  color: var(--red);
  border: 1px solid rgba(255, 59, 48, 0.3);
  padding: 5px 10px;
}
.btn-danger:hover { background: rgba(255, 59, 48, 0.1); }

input.f, select.f, textarea.f {
  width: 100%;
  background: var(--field);
  border: 1px solid var(--sep);
  border-radius: 9px;
  color: var(--text);
  padding: 8px 10px;
  font: 13.5px/1.4 inherit;
  outline: none;
}
input.f:focus, select.f:focus, textarea.f:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-soft);
}
textarea.f {
  resize: vertical;
  min-height: 68px;
}
.catalog-box {
  background: var(--accent-soft);
  border: 1px solid var(--accent);
  border-radius: 14px;
  padding: 14px 16px;
  margin-bottom: 14px;
}
.catalog-title {
  font-weight: 700;
  font-size: 13.5px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.catalog-sub {
  font-size: 12px;
  color: var(--sub);
  margin-bottom: 10px;
}
.filter-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}
.pill {
  background: var(--card);
  color: var(--sub);
  border: 1px solid var(--sep);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.pill.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.catalog-row {
  display: grid;
  grid-template-columns: 180px 1fr auto;
  gap: 8px;
  align-items: center;
}
@media (max-width: 640px) {
  .catalog-row { grid-template-columns: 1fr; }
}
.catalog-preview {
  margin-top: 8px;
  padding: 8px 10px;
  background: var(--card);
  border-radius: 9px;
  font-size: 12px;
  color: var(--sub);
  border: 1px solid var(--sep);
}
.catalog-preview strong { color: var(--text); }

.prov-card {
  background: var(--card);
  border: 1px solid var(--sep);
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 10px;
}
.prov-top {
  display: grid;
  grid-template-columns: 170px 1fr auto;
  gap: 8px;
  align-items: end;
}
.prov-mid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 8px;
}
@media (max-width: 640px) {
  .prov-top, .prov-mid { grid-template-columns: 1fr; }
}
.field-lbl {
  display: block;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--sub);
  margin-bottom: 3px;
}
.consequence-bar {
  margin-top: 9px;
  padding: 7px 10px;
  border-radius: 8px;
  background: var(--card-alt);
  border-left: 3px solid var(--accent);
  font-size: 12px;
  color: var(--text);
}
.consequence-bar span {
  color: var(--sub);
  font-weight: 600;
  margin-right: 4px;
}

.model-card {
  background: var(--card-alt);
  border: 1px solid var(--sep);
  border-radius: 11px;
  padding: 11px 12px;
  margin-bottom: 9px;
}
.model-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr 76px 115px 52px 1.2fr auto;
  gap: 7px;
  align-items: end;
}
@media (max-width: 760px) {
  .model-grid { grid-template-columns: 1fr 1fr; }
}
input.color-inp {
  width: 100%;
  height: 35px;
  padding: 2px;
  border-radius: 8px;
  border: 1px solid var(--sep);
  background: var(--field);
  cursor: pointer;
}
.model-sys {
  margin-top: 7px;
}
.model-sys input.f {
  font-size: 12.5px;
  padding: 6px 9px;
}

.setting-row {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 14px;
  align-items: center;
  padding: 11px 0;
  border-bottom: 1px solid var(--sep);
}
.setting-row:first-child { padding-top: 2px; }
.setting-row:last-child { border-bottom: 0; padding-bottom: 2px; }
@media (max-width: 640px) {
  .setting-row { grid-template-columns: 1fr; gap: 6px; }
}
.setting-info .stitle {
  font-weight: 600;
  font-size: 13.5px;
  color: var(--text);
}
.setting-info .sdesc {
  font-size: 12px;
  color: var(--sub);
  margin-top: 2px;
}
.setting-full {
  padding: 11px 0;
  border-bottom: 1px solid var(--sep);
}
.setting-full:last-child { border-bottom: 0; }
.setting-full .stitle {
  font-weight: 600;
  font-size: 13.5px;
  margin-bottom: 2px;
}
.setting-full .sdesc {
  font-size: 12px;
  color: var(--sub);
  margin-bottom: 7px;
}

.chain-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}
.chain-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--field);
  border: 1px solid var(--sep);
  border-radius: 8px;
  padding: 5px 9px;
  font-size: 12.5px;
  font-weight: 600;
}
.chain-chip button {
  background: none;
  border: 0;
  color: var(--sub);
  cursor: pointer;
  padding: 0 2px;
  font-size: 13px;
}
.chain-chip button:hover { color: var(--text); }

.mode-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
@media (max-width: 720px) {
  .mode-grid { grid-template-columns: 1fr; }
}
.mode-card {
  background: var(--card);
  border: 1px solid var(--sep);
  border-radius: 13px;
  padding: 13px 15px;
}
.mode-card h3 {
  margin: 0 0 3px;
  font-size: 14px;
  font-weight: 700;
}
.mode-card .msub {
  font-size: 12px;
  color: var(--sub);
  margin-bottom: 10px;
}
.mode-kv {
  margin-bottom: 9px;
}

.footer-bar {
  position: sticky;
  bottom: 12px;
  z-index: 40;
  margin-top: 22px;
  background: color-mix(in srgb, var(--card) 92%, transparent);
  backdrop-filter: blur(14px);
  border: 1px solid var(--sep);
  border-radius: 14px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
}
.where {
  color: var(--sub);
  font-size: 12px;
  word-break: break-all;
}
.go {
  min-width: 210px;
  padding: 11px 22px;
  border: 0;
  border-radius: 11px;
  background: var(--accent);
  color: #fff;
  font: 700 15px/1.2 inherit;
  cursor: pointer;
}
.go:active { opacity: 0.85; }
</style>
</head>
<body>
<div class="topbar">
  <div class="topbar-inner">
    <div class="brand">
      <h1>Quorum Launch Configurator</h1>
      <span>All decisions bound to data\collider_config.json</span>
    </div>
    <nav class="nav-pills">
      <a href="#sec-host">1. Host Port</a>
      <a href="#sec-keys">2. API Keys &amp; Providers</a>
      <a href="#sec-models">3. Ticker Models</a>
      <a href="#sec-agents">4. Consensus &amp; Smart Gen</a>
      <a href="#sec-modes">5. Prompt Modes</a>
      <a href="#sec-limits">6. Execution Limits</a>
      <a href="#sec-browser">7. Browser &amp; Storage</a>
      <a href="#sec-market">8. Discover Market &amp; Themes</a>
    </nav>
  </div>
</div>

<form id="f" autocomplete="off">
  <!-- 1. HOST PORT -->
  <div id="sec-host" class="sec-head">
    <h2>1. Session Localhost Port</h2>
    <p>Local port number (http://127.0.0.1:&lt;port&gt;/) used by this Collider desktop &amp; mobile viewport session.</p>
  </div>
  <div class="card host-row" id="host-card">
    <div class="host-left">
      <div class="lbl">Localhost Port Number (1024 – 65535)</div>
      <div class="desc" id="host-preview">Serves the app at http://127.0.0.1:37418/ and Fixed Mobile Viewport at http://127.0.0.1:37418/mobile.html</div>
    </div>
    <div class="host-controls">
      <input id="host" class="host-inp" inputmode="numeric" autofocus>
      <button type="button" class="btn" id="btn-rand-port">Pick Random Port</button>
    </div>
  </div>

  <!-- 2. API PROVIDERS & KEYS -->
  <div id="sec-keys" class="sec-head">
    <h2>2. API Providers &amp; Keys (Loaded from API KEYS.txt)</h2>
    <p>Select any Model–Key item from your master API KEYS.txt catalog below to add or update a provider row, or switch keys directly inside any active row. Multiple keys for the same provider automatically share load in round-robin.</p>
  </div>

  <div class="catalog-box">
    <div class="catalog-title">
      <span>Master API Keys &amp; Model Selector (C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt)</span>
      <span id="cat-count" style="font-size:12px;color:var(--sub)"></span>
    </div>
    <div class="catalog-sub">Filter by functional category or search by provider/model/key, then pick a line item to add or activate it immediately.</div>
    <div class="filter-pills" id="cat-pills"></div>
    <div class="catalog-row">
      <input type="text" class="f" id="cat-search" placeholder="Filter keys (e.g. NVIDIA, Grok, Whisper, OpenCode, FLUX, Tavily)...">
      <select class="f" id="cat-select"></select>
      <button type="button" class="btn btn-accent" id="cat-add-btn">+ Add Selected Key Row</button>
    </div>
    <div class="catalog-preview" id="cat-preview"></div>
  </div>

  <div id="provider-rows"></div>
  <button type="button" class="btn" id="add-blank-prov" style="width:100%;padding:10px">+ Add Blank Custom Provider Row</button>

  <!-- 3. TICKER RESPONSE MODELS -->
  <div id="sec-models" class="sec-head">
    <h2>3. Ticker Response Models (Models That Answer User Prompts in the Main Ticker)</h2>
    <p>Exclusive scope: These are the AI models that run in parallel when you submit a prompt on the Home Ticker. Each model below gets its own response row in the Ticker and casts a vote in Consensus.</p>
  </div>
  <div class="card">
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid var(--sep)">
      <div style="flex:1;min-width:240px">
        <label class="field-lbl">Quick-Add Verified Model from Catalog</label>
        <select class="f" id="quick-add-model-sel"></select>
      </div>
      <div style="padding-top:16px">
        <button type="button" class="btn btn-accent" id="quick-add-model-btn">+ Add Model to Ticker</button>
      </div>
    </div>
    <div id="ticker-models-box"></div>
  </div>

  <!-- 4. CONSENSUS & SMART GEN AGENTS -->
  <div id="sec-agents" class="sec-head">
    <h2>4. Consensus &amp; Smart Gen Judge Agents</h2>
    <p>Controls which judge models read the completed Ticker responses to compute the Consensus Ratio, Consensus Summary, Logical Chain Lengths, and Smart Gen tasks/projects.</p>
  </div>
  <div class="card" id="agents-box"></div>

  <!-- 5. PROMPT MODES CONFIGURATION -->
  <div id="sec-modes" class="sec-head">
    <h2>5. Prompt Modes Configuration (Chat, Internet, Research, Deep Research)</h2>
    <p>All settings for each composer mode in one place: response style instruction, web search depth, number of cited web sources fetched, max characters per web source excerpt, max output tokens, and mode timeout.</p>
  </div>
  <div class="mode-grid" id="modes-box"></div>

  <!-- 6. MODEL EXECUTION & STREAM LIMITS -->
  <div id="sec-limits" class="sec-head">
    <h2>6. Model Execution, Reasoning &amp; Stream Timeouts</h2>
    <p>Global execution behavior for Ticker streaming, internal &lt;think&gt; reasoning budgets, single-model follow-up replies, and automatic API key retry failover.</p>
  </div>
  <div class="card" id="limits-box"></div>

  <!-- 7. IN-APP BROWSER & STORAGE LIMITS -->
  <div id="sec-browser" class="sec-head">
    <h2>7. In-App Browser &amp; Local Storage Retention Limits</h2>
    <p>Controls fallback search inside the In-App Browser, maximum file attachments per prompt, and how many past sessions and Smart Gen cards are kept on disk.</p>
  </div>
  <div class="card" id="browser-box"></div>

  <!-- 8. DISCOVER MARKET IMAGE GENERATION & THEME STORE -->
  <div id="sec-market" class="sec-head">
    <h2>8. Discover Market Image Generation &amp; Live Wallpaper Store</h2>
    <p>Discover Market is strictly Images-Only (PRD R27 / D2). Configure image provider priority order, FLUX / 2K models, default batch size, aspect ratio, and Live Wallpaper Theme Store settings.</p>
  </div>
  <div class="card" id="market-box"></div>
  <div class="card" id="themes-box"></div>

  <div class="footer-bar">
    <div class="where" id="where"></div>
    <button class="go" type="submit" id="go-btn">Save &amp; Launch Collider</button>
  </div>
</form>

<script>
const C = INITIAL;
const KEY_CATALOG = C.key_catalog || [];
const MODEL_CATALOG = C.model_catalog || [];
const S = JSON.parse(JSON.stringify(C.settings));
let rows = (C.providers || []).map(r => ({
  provider_name: r.provider_name || r.name || 'NVIDIA',
  purpose_in_app: r.purpose_in_app || '',
  api_endpoint_url: r.api_endpoint_url || r.endpoint || 'https://integrate.api.nvidia.com/v1/chat/completions',
  api_key: r.api_key || r.key || '',
  extra_model_ids: r.extra_model_ids !== undefined ? r.extra_model_ids : (r.models || '')
}));

const H = document.getElementById('host');
const hostPreview = document.getElementById('host-preview');
function updateHostPreview() {
  const p = H.value.trim() || '37418';
  hostPreview.textContent = `Serves the app at http://127.0.0.1:${p}/ and Fixed Mobile Viewport at http://127.0.0.1:${p}/mobile.html`;
}
H.value = C.host || '';
if (!C.host) {
  document.getElementById('sec-host').style.display = 'none';
  document.getElementById('host-card').style.display = 'none';
  document.getElementById('go-btn').textContent = 'Save Configuration';
}
H.addEventListener('input', () => { H.classList.remove('bad'); updateHostPreview(); });
document.getElementById('btn-rand-port').onclick = () => {
  H.value = String(Math.floor(20000 + Math.random() * 40000));
  updateHostPreview();
};
updateHostPreview();
document.getElementById('where').textContent = 'Configuration File: ' + WHERE;

// Standard Provider Presets (so user never has to look up endpoint URLs)
const PROVIDER_PRESETS = [
  { name: 'NVIDIA', endpoint: 'https://integrate.api.nvidia.com/v1/chat/completions', role: 'Ticker & Judge LLMs + FLUX.1 Image Gen' },
  { name: 'OpenCode Zen', endpoint: 'https://opencode.ai/zen/v1/chat/completions', role: 'Ticker & Judge LLMs (GPT-5.6 Luna, DeepSeek V4, Qwen 3.5)' },
  { name: 'OpenRouter', endpoint: 'https://openrouter.ai/api/v1/chat/completions', role: 'Ticker & Judge LLMs (Claude 3.7, Gemini 2.5, GPT-4.1)' },
  { name: 'xAI', endpoint: 'https://api.x.ai/v1/chat/completions', role: 'Ticker & Judge LLMs (Grok 3 & Grok Vision)' },
  { name: 'OpenAI', endpoint: 'https://api.openai.com/v1/chat/completions', role: 'Ticker & Judge LLMs (GPT-4.1, GPT-4o, o3-mini)' },
  { name: 'Google Gemini', endpoint: 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions', role: 'Ticker & Judge LLMs (Gemini 2.5 Pro & Flash)' },
  { name: 'Kimi', endpoint: 'https://api.moonshot.cn/v1/chat/completions', role: 'Ticker & Judge LLMs (Moonshot Kimi 128K)' },
  { name: 'MiniMax', endpoint: 'https://api.minimax.chat/v1/text/chatcompletion_v2', role: 'Ticker & Judge LLMs (MiniMax M3 OEM)' },
  { name: 'Cohere', endpoint: 'https://api.cohere.com/v2/chat', role: 'Ticker & Judge LLMs (Command-A & Command-R+)' },
  { name: 'AI Hub Mix', endpoint: 'https://aihubmix.com/v1/chat/completions', role: 'Multi-Provider OpenAI-Compatible Aggregator' },
  { name: 'Crazyrouter', endpoint: 'https://cn.crazyrouter.com/v1/chat/completions', role: 'Multi-Provider OpenAI-Compatible Router' },
  { name: 'HuggingFace', endpoint: 'https://router.huggingface.co/v1/chat/completions', role: 'Open-Weight Hugging Face Inference Router' },
  { name: 'Vercel Gateway', endpoint: 'https://ai-gateway.vercel.sh/v1/chat/completions', role: 'Vercel Unified AI Gateway' },
  { name: 'Cloudflare', endpoint: 'https://collider-imagine.ebridavid.workers.dev', role: 'Discover Market Free Daily FLUX.2 Image Worker' },
  { name: 'fal', endpoint: 'https://queue.fal.run', role: 'Discover Market High-Res 2K Image Queue' },
  { name: 'Tavily', endpoint: 'https://api.tavily.com/search', role: 'Live Web Search (Internet, Research, Deep Research & Browser)' },
  { name: 'Groq', endpoint: 'https://api.groq.com/openai/v1/audio/transcriptions', role: 'Voice Chat Speech-to-Text (Whisper Large v3 Turbo)' },
  { name: 'Phone', endpoint: 'https://collider-phone.ebridavid.workers.dev', role: 'Permanent Phone Access URL Tunnel' }
];

function computePurpose(r) {
  const ep = (r.api_endpoint_url || '').toLowerCase();
  const nm = (r.provider_name || '').trim();
  if (!r.api_key || !r.api_key.trim()) return 'Inactive: select an API key from the dropdown to activate this provider.';
  if (ep.includes('audio/transcriptions')) return 'Voice Chat Speech-to-Text: transcribes microphone voice input via Groq Whisper (/api/transcribe).';
  if (ep.includes('fal.run')) return 'Discover Market 2K Image Generation: generates 2K resolution images via fal.ai queue (/api/imagine).';
  if (ep.includes('collider-phone')) return 'Permanent Mobile Tunnel: routes your unchanging mobile link (https://collider-phone.ebridavid.workers.dev/' + r.api_key.trim() + ') to this PC.';
  if (ep.includes('collider-imagine')) return 'Discover Market Free Daily Image Generation: runs FLUX.2 Klein 4B / Dev / Schnell on Cloudflare Workers AI (/api/imagine).';
  if (ep.includes('tavily') || nm.toLowerCase() === 'tavily') return 'Live Web Search: fetches cited web sources for Internet, Research, and Deep Research modes (/api/ask) and In-App Browser search (/api/page).';
  const matchingModels = (S.ticker_response_models || []).filter(m => (m.api_provider_route || 'NVIDIA').toLowerCase() === nm.toLowerCase()).map(m => m.display_name || m.model_id);
  const extra = (r.extra_model_ids || '').split(',').map(x => x.trim()).filter(Boolean);
  const allM = [...new Set([...matchingModels, ...extra])];
  let out = allM.length ? `Answers ${allM.length} Ticker Models (${allM.slice(0, 6).join(', ')}${allM.length > 6 ? '...' : ''})` : `Ready for ${nm} models`;
  if (ep.includes('integrate.api.nvidia.com')) out += ' + runs Consensus/Smart Gen Judges + NVIDIA FLUX.1 Dev images.';
  return out;
}

// ---------------- 2. MASTER API KEYS CATALOG SELECTOR ----------------
let activeCatFilter = 'ALL';
const catGroups = ['ALL', ...new Set(KEY_CATALOG.map(k => k.category))];
const pillsBox = document.getElementById('cat-pills');
const catSearch = document.getElementById('cat-search');
const catSelect = document.getElementById('cat-select');
const catPreview = document.getElementById('cat-preview');

function renderCatalogSelector() {
  pillsBox.innerHTML = '';
  const shortCatName = c => c === 'ALL' ? `All Keys (${KEY_CATALOG.length})` : c.replace(/^\d+\.\s*/, '');
  catGroups.forEach(c => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'pill' + (activeCatFilter === c ? ' active' : '');
    b.textContent = shortCatName(c);
    b.onclick = () => { activeCatFilter = c; renderCatalogSelector(); };
    pillsBox.appendChild(b);
  });

  const q = (catSearch.value || '').trim().toLowerCase();
  const filtered = KEY_CATALOG.filter(item => {
    if (activeCatFilter !== 'ALL' && item.category !== activeCatFilter) return false;
    if (!q) return true;
    return (item.label + ' ' + item.provider_name + ' ' + item.extra_model_ids + ' ' + item.consequence + ' ' + item.api_endpoint_url).toLowerCase().includes(q);
  });

  document.getElementById('cat-count').textContent = `${filtered.length} of ${KEY_CATALOG.length} keys shown`;
  catSelect.innerHTML = '';
  const byCat = {};
  filtered.forEach(it => { (byCat[it.category] = byCat[it.category] || []).push(it); });
  Object.keys(byCat).forEach(cat => {
    const og = document.createElement('optgroup');
    og.label = cat;
    byCat[cat].forEach(it => {
      const opt = document.createElement('option');
      opt.value = it.id;
      const alreadyActive = rows.some(r => (r.api_key || '').trim() === it.api_key);
      opt.textContent = (alreadyActive ? '✓ [Active] ' : '') + it.label + (it.extra_model_ids ? ` → Models: ${it.extra_model_ids}` : '');
      og.appendChild(opt);
    });
    catSelect.appendChild(og);
  });
  updateCatalogPreview();
}

function updateCatalogPreview() {
  const chosen = KEY_CATALOG.find(k => k.id === catSelect.value);
  if (!chosen) {
    catPreview.innerHTML = 'No matching key in current filter.';
    return;
  }
  const active = rows.some(r => (r.api_key || '').trim() === chosen.api_key);
  catPreview.innerHTML = `<strong>${chosen.provider_name}</strong> (${chosen.api_endpoint_url}) — <strong>Status:</strong> ${active ? '<span style="color:var(--green)">Already Active in Provider Rows Below</span>' : 'Ready to Add'}<br><strong>Consequence:</strong> ${chosen.consequence}${chosen.extra_model_ids ? '<br><strong>Bundled Models:</strong> ' + chosen.extra_model_ids : ''}`;
}
catSearch.addEventListener('input', renderCatalogSelector);
catSelect.addEventListener('change', updateCatalogPreview);

document.getElementById('cat-add-btn').onclick = () => {
  const chosen = KEY_CATALOG.find(k => k.id === catSelect.value);
  if (!chosen) return;
  const existingIdx = rows.findIndex(r => (r.api_key || '').trim() === chosen.api_key);
  if (existingIdx >= 0) {
    rows[existingIdx].provider_name = chosen.provider_name;
    rows[existingIdx].api_endpoint_url = chosen.api_endpoint_url;
    if (chosen.extra_model_ids && !rows[existingIdx].extra_model_ids) {
      rows[existingIdx].extra_model_ids = chosen.extra_model_ids;
    }
  } else {
    rows.push({
      provider_name: chosen.provider_name,
      purpose_in_app: chosen.consequence,
      api_endpoint_url: chosen.api_endpoint_url,
      api_key: chosen.api_key,
      extra_model_ids: chosen.extra_model_ids || ''
    });
  }
  drawProviders();
  renderCatalogSelector();
};

function drawProviders() {
  const box = document.getElementById('provider-rows');
  box.innerHTML = '';
  rows.forEach((r, idx) => {
    r.purpose_in_app = computePurpose(r);
    const card = document.createElement('div');
    card.className = 'prov-card';

    // Top row: Provider Selector + Key Selector from API KEYS.txt + Remove button
    const top = document.createElement('div');
    top.className = 'prov-top';

    // 1. Provider Selector
    const pWrap = document.createElement('div');
    pWrap.innerHTML = `<label class="field-lbl">Service / Provider</label>`;
    const pSel = document.createElement('select');
    pSel.className = 'f';
    let foundPreset = false;
    PROVIDER_PRESETS.forEach(p => {
      const o = document.createElement('option');
      o.value = p.name;
      o.textContent = `${p.name} — ${p.role.split('(')[0].trim()}`;
      if (p.name.toLowerCase() === (r.provider_name || '').toLowerCase()) {
        o.selected = true;
        foundPreset = true;
      }
      pSel.appendChild(o);
    });
    if (!foundPreset && r.provider_name) {
      const o = document.createElement('option');
      o.value = r.provider_name;
      o.textContent = r.provider_name;
      o.selected = true;
      pSel.appendChild(o);
    }
    pWrap.appendChild(pSel);

    // 2. API Key Selector (populated from API KEYS.txt, sorted with matching provider first)
    const kWrap = document.createElement('div');
    kWrap.innerHTML = `<label class="field-lbl">Select API Key from API KEYS.txt (or Paste Below)</label>`;
    const kSel = document.createElement('select');
    kSel.className = 'f';
    const matchingKeys = KEY_CATALOG.filter(k => k.provider_name.toLowerCase() === (r.provider_name || '').toLowerCase());
    const otherKeys = KEY_CATALOG.filter(k => k.provider_name.toLowerCase() !== (r.provider_name || '').toLowerCase());
    let keyMatched = false;

    if (matchingKeys.length) {
      const og1 = document.createElement('optgroup');
      og1.label = `Recommended Keys for ${r.provider_name} (from API KEYS.txt)`;
      matchingKeys.forEach(k => {
        const o = document.createElement('option');
        o.value = k.api_key;
        o.textContent = k.label;
        if (k.api_key === (r.api_key || '').trim()) { o.selected = true; keyMatched = true; }
        og1.appendChild(o);
      });
      kSel.appendChild(og1);
    }
    const og2 = document.createElement('optgroup');
    og2.label = 'All Other Keys in API KEYS.txt';
    otherKeys.forEach(k => {
      const o = document.createElement('option');
      o.value = k.api_key;
      o.textContent = `${k.label} [${k.provider_name}]`;
      if (k.api_key === (r.api_key || '').trim()) { o.selected = true; keyMatched = true; }
      og2.appendChild(o);
    });
    kSel.appendChild(og2);
    if (!keyMatched) {
      const o = document.createElement('option');
      o.value = r.api_key || '';
      o.textContent = r.api_key ? `Custom Key (${r.api_key.slice(0, 6)}...${r.api_key.slice(-4)})` : '— Select an API Key —';
      o.selected = true;
      kSel.insertBefore(o, kSel.firstChild);
    }
    kWrap.appendChild(kSel);

    // 3. Remove button
    const delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.className = 'btn btn-danger';
    delBtn.textContent = 'Remove';
    delBtn.onclick = () => {
      rows.splice(idx, 1);
      drawProviders();
      renderCatalogSelector();
    };

    top.appendChild(pWrap);
    top.appendChild(kWrap);
    top.appendChild(delBtn);
    card.appendChild(top);

    // Middle row: API Endpoint URL + Extra Model IDs (or exact key value input)
    const mid = document.createElement('div');
    mid.className = 'prov-mid';

    const epWrap = document.createElement('div');
    epWrap.innerHTML = `<label class="field-lbl">API Endpoint URL (Auto-Filled by Provider)</label>`;
    const epInp = document.createElement('input');
    epInp.className = 'f';
    epInp.value = r.api_endpoint_url || '';
    epInp.addEventListener('input', () => {
      r.api_endpoint_url = epInp.value;
      conseq.innerHTML = `<span>App Consequence:</span> ${computePurpose(r)}`;
    });
    epWrap.appendChild(epInp);

    const modWrap = document.createElement('div');
    const hideModels = /tavily|fal\.run|collider-phone/i.test((r.api_endpoint_url || '') + (r.provider_name || ''));
    modWrap.innerHTML = `<label class="field-lbl">${hideModels ? 'Raw API Key String' : 'Bundled / Extra Model IDs on This Provider'}</label>`;
    const modInp = document.createElement('input');
    modInp.className = 'f';
    if (hideModels) {
      modInp.value = r.api_key || '';
      modInp.placeholder = 'API key string';
      modInp.addEventListener('input', () => { r.api_key = modInp.value; });
    } else {
      modInp.value = r.extra_model_ids || '';
      modInp.placeholder = 'Optional extra model IDs (comma-separated) or leave blank for built-in Ticker roster';
      modInp.addEventListener('input', () => {
        r.extra_model_ids = modInp.value;
        conseq.innerHTML = `<span>App Consequence:</span> ${computePurpose(r)}`;
      });
    }
    modWrap.appendChild(modInp);

    mid.appendChild(epWrap);
    mid.appendChild(modWrap);
    card.appendChild(mid);

    const conseq = document.createElement('div');
    conseq.className = 'consequence-bar';
    conseq.innerHTML = `<span>App Consequence:</span> ${r.purpose_in_app}`;
    card.appendChild(conseq);

    pSel.onchange = () => {
      r.provider_name = pSel.value;
      const preset = PROVIDER_PRESETS.find(p => p.name === pSel.value);
      if (preset) r.api_endpoint_url = preset.endpoint;
      const firstKey = KEY_CATALOG.find(k => k.provider_name.toLowerCase() === pSel.value.toLowerCase());
      if (firstKey) {
        r.api_key = firstKey.api_key;
        if (firstKey.extra_model_ids && !r.extra_model_ids) r.extra_model_ids = firstKey.extra_model_ids;
      }
      drawProviders();
      renderCatalogSelector();
    };

    kSel.onchange = () => {
      r.api_key = kSel.value;
      const catItem = KEY_CATALOG.find(k => k.api_key === kSel.value);
      if (catItem) {
        r.provider_name = catItem.provider_name;
        r.api_endpoint_url = catItem.api_endpoint_url;
        if (catItem.extra_model_ids) r.extra_model_ids = catItem.extra_model_ids;
      }
      drawProviders();
      renderCatalogSelector();
    };

    box.appendChild(card);
  });
}

document.getElementById('add-blank-prov').onclick = () => {
  rows.push({
    provider_name: 'NVIDIA',
    purpose_in_app: '',
    api_endpoint_url: 'https://integrate.api.nvidia.com/v1/chat/completions',
    api_key: '',
    extra_model_ids: ''
  });
  drawProviders();
};

// ---------------- 3. TICKER RESPONSE MODELS ----------------
const quickModelSel = document.getElementById('quick-add-model-sel');
function populateQuickAddModelSelector() {
  quickModelSel.innerHTML = '';
  MODEL_CATALOG.forEach(mc => {
    const o = document.createElement('option');
    o.value = mc.model_id;
    const inTicker = (S.ticker_response_models || []).some(m => m.model_id === mc.model_id);
    o.textContent = `${inTicker ? '✓ [In Ticker] ' : ''}${mc.display_name} (${mc.model_id} via ${mc.api_provider_route}) — ${mc.consequence}`;
    quickModelSel.appendChild(o);
  });
}

document.getElementById('quick-add-model-btn').onclick = () => {
  const mc = MODEL_CATALOG.find(x => x.model_id === quickModelSel.value);
  if (!mc) return;
  if (!(S.ticker_response_models || []).some(m => m.model_id === mc.model_id)) {
    S.ticker_response_models.push({
      model_id: mc.model_id,
      display_name: mc.display_name,
      ticker_badge: mc.ticker_badge,
      model_creator: mc.model_creator,
      api_provider_route: mc.api_provider_route,
      badge_color_hex: mc.badge_color_hex,
      custom_temperature: '',
      custom_system_instruction: ''
    });
    drawTickerModels();
    drawAgents();
  }
};

const TEMP_OPTIONS = [
  { val: '', label: 'Use Global Default (Balanced)' },
  { val: 0.0, label: '0.0 — Deterministic (Exact facts/code)' },
  { val: 0.2, label: '0.2 — High Precision (Tight grounding)' },
  { val: 0.4, label: '0.4 — Balanced Standard' },
  { val: 0.7, label: '0.7 — Creative & Expansive' },
  { val: 1.0, label: '1.0 — Maximum Variety' }
];

function drawTickerModels() {
  populateQuickAddModelSelector();
  const box = document.getElementById('ticker-models-box');
  box.innerHTML = '';
  (S.ticker_response_models || []).forEach((m, idx) => {
    const card = document.createElement('div');
    card.className = 'model-card';
    const grid = document.createElement('div');
    grid.className = 'model-grid';

    // 1. Model Selector Dropdown
    const idWrap = document.createElement('div');
    idWrap.innerHTML = `<label class="field-lbl">Model ID &amp; Capability</label>`;
    const idSel = document.createElement('select');
    idSel.className = 'f';
    let matched = false;
    MODEL_CATALOG.forEach(mc => {
      const o = document.createElement('option');
      o.value = mc.model_id;
      o.textContent = `${mc.display_name} (${mc.model_id}) — ${mc.consequence}`;
      if (mc.model_id === m.model_id) { o.selected = true; matched = true; }
      idSel.appendChild(o);
    });
    if (!matched && m.model_id) {
      const o = document.createElement('option');
      o.value = m.model_id;
      o.textContent = `${m.display_name || m.model_id} (${m.model_id})`;
      o.selected = true;
      idSel.insertBefore(o, idSel.firstChild);
    }
    idSel.onchange = () => {
      const mc = MODEL_CATALOG.find(x => x.model_id === idSel.value);
      if (mc) {
        m.model_id = mc.model_id;
        m.display_name = mc.display_name;
        m.ticker_badge = mc.ticker_badge;
        m.model_creator = mc.model_creator;
        m.api_provider_route = mc.api_provider_route;
        m.badge_color_hex = mc.badge_color_hex;
        drawTickerModels();
        drawAgents();
      }
    };
    idWrap.appendChild(idSel);

    // 2. Display Name
    const lblWrap = document.createElement('div');
    lblWrap.innerHTML = `<label class="field-lbl">Ticker Display Name</label>`;
    const lblInp = document.createElement('input');
    lblInp.className = 'f';
    lblInp.value = m.display_name || '';
    lblInp.oninput = () => { m.display_name = lblInp.value; };
    lblWrap.appendChild(lblInp);

    // 3. Short Badge
    const shWrap = document.createElement('div');
    shWrap.innerHTML = `<label class="field-lbl">Badge</label>`;
    const shInp = document.createElement('input');
    shInp.className = 'f';
    shInp.value = m.ticker_badge || '';
    shInp.oninput = () => { m.ticker_badge = shInp.value; };
    shWrap.appendChild(shInp);

    // 4. API Route Selector
    const viaWrap = document.createElement('div');
    viaWrap.innerHTML = `<label class="field-lbl">API Route Provider</label>`;
    const viaSel = document.createElement('select');
    viaSel.className = 'f';
    const routeNames = [...new Set(['NVIDIA', 'OpenCode Zen', 'OpenRouter', 'xAI', 'OpenAI', 'Google Gemini', 'Kimi', 'MiniMax', 'Cohere', 'AI Hub Mix', 'Crazyrouter', ...rows.map(r => r.provider_name)])];
    routeNames.forEach(rn => {
      if (!rn) return;
      const o = document.createElement('option');
      o.value = rn;
      o.textContent = rn;
      if (rn.toLowerCase() === (m.api_provider_route || 'NVIDIA').toLowerCase()) o.selected = true;
      viaSel.appendChild(o);
    });
    viaSel.onchange = () => { m.api_provider_route = viaSel.value; drawProviders(); };
    viaWrap.appendChild(viaSel);

    // 5. Color Swatch Picker
    const colWrap = document.createElement('div');
    colWrap.innerHTML = `<label class="field-lbl">Color</label>`;
    const colInp = document.createElement('input');
    colInp.type = 'color';
    colInp.className = 'color-inp';
    colInp.value = /^#[0-9a-fA-F]{6}$/.test(m.badge_color_hex || '') ? m.badge_color_hex : '#60A5FA';
    colInp.oninput = () => { m.badge_color_hex = colInp.value; };
    colWrap.appendChild(colInp);

    // 6. Custom Temperature Dropdown
    const tmpWrap = document.createElement('div');
    tmpWrap.innerHTML = `<label class="field-lbl">Model Creativity (Temp)</label>`;
    const tmpSel = document.createElement('select');
    tmpSel.className = 'f';
    TEMP_OPTIONS.forEach(to => {
      const o = document.createElement('option');
      o.value = String(to.val);
      o.textContent = to.label;
      if (String(m.custom_temperature ?? '') === String(to.val)) o.selected = true;
      tmpSel.appendChild(o);
    });
    tmpSel.onchange = () => {
      m.custom_temperature = tmpSel.value === '' ? '' : Number(tmpSel.value);
    };
    tmpWrap.appendChild(tmpSel);

    // 7. Remove button
    const rmWrap = document.createElement('div');
    const rmBtn = document.createElement('button');
    rmBtn.type = 'button';
    rmBtn.className = 'btn btn-danger';
    rmBtn.textContent = '×';
    rmBtn.title = 'Remove from Ticker';
    rmBtn.onclick = () => {
      S.ticker_response_models.splice(idx, 1);
      drawTickerModels();
    };
    rmWrap.appendChild(rmBtn);

    grid.appendChild(idWrap);
    grid.appendChild(lblWrap);
    grid.appendChild(shWrap);
    grid.appendChild(viaWrap);
    grid.appendChild(colWrap);
    grid.appendChild(tmpWrap);
    grid.appendChild(rmWrap);
    card.appendChild(grid);

    // Optional per-model system prompt
    const sysDiv = document.createElement('div');
    sysDiv.className = 'model-sys';
    const sysInp = document.createElement('input');
    sysInp.className = 'f';
    sysInp.placeholder = 'Optional Custom System Instruction for ' + (m.display_name || m.model_id) + ' (prepended before the Mode instruction; leave empty for standard)';
    sysInp.value = m.custom_system_instruction || '';
    sysInp.oninput = () => { m.custom_system_instruction = sysInp.value; };
    sysDiv.appendChild(sysInp);
    card.appendChild(sysDiv);

    box.appendChild(card);
  });
}

// Helper to build a labeled dropdown setting row
function makeSelectRow(title, desc, currentVal, options, onChange) {
  const row = document.createElement('div');
  row.className = 'setting-row';
  const info = document.createElement('div');
  info.className = 'setting-info';
  const st = document.createElement('div');
  st.className = 'stitle';
  st.textContent = title;
  const sd = document.createElement('div');
  sd.className = 'sdesc';
  sd.textContent = desc;
  info.appendChild(st);
  info.appendChild(sd);
  const ctrl = document.createElement('div');
  const sel = document.createElement('select');
  sel.className = 'f';
  let matched = false;
  options.forEach(opt => {
    const o = document.createElement('option');
    o.value = String(opt.val);
    o.textContent = opt.label;
    if (String(opt.val) === String(currentVal)) { o.selected = true; matched = true; }
    sel.appendChild(o);
  });
  if (!matched && currentVal !== undefined) {
    const o = document.createElement('option');
    o.value = String(currentVal);
    o.textContent = `${currentVal} (Current Custom Value)`;
    o.selected = true;
    sel.insertBefore(o, sel.firstChild);
  }
  sel.onchange = () => onChange(sel.value);
  ctrl.appendChild(sel);
  row.appendChild(info);
  row.appendChild(ctrl);
  return row;
}

function makeTextareaBlock(title, desc, currentVal, onChange) {
  const wrap = document.createElement('div');
  wrap.className = 'setting-full';
  const st = document.createElement('div');
  st.className = 'stitle';
  st.textContent = title;
  const sd = document.createElement('div');
  sd.className = 'sdesc';
  sd.textContent = desc;
  wrap.appendChild(st);
  wrap.appendChild(sd);
  const ta = document.createElement('textarea');
  ta.className = 'f';
  ta.rows = Math.max(3, Math.min(10, (currentVal || '').split('\n').length + 1));
  ta.value = currentVal || '';
  ta.oninput = () => onChange(ta.value);
  wrap.appendChild(ta);
  return wrap;
}

// ---------------- 4. CONSENSUS & SMART GEN JUDGE AGENTS ----------------
function allSelectableJudgeModels() {
  const map = new Map();
  MODEL_CATALOG.forEach(m => map.set(m.model_id, `${m.display_name} (${m.model_id}) — ${m.consequence}`));
  (S.ticker_response_models || []).forEach(m => {
    if (!map.has(m.model_id)) map.set(m.model_id, `${m.display_name || m.model_id} (${m.model_id})`);
  });
  return Array.from(map.entries()).map(([val, label]) => ({ val, label }));
}

function drawAgents() {
  const box = document.getElementById('agents-box');
  box.innerHTML = '';
  const csa = S.consensus_and_smartgen_agents;
  const judgeOptions = allSelectableJudgeModels();

  // 1. Primary Judge Model Dropdown
  box.appendChild(makeSelectRow(
    'Primary Consensus & Smart Gen Judge Model',
    'The primary AI model that reads all completed Ticker responses to compute the Consensus Ratio, Consensus Summary, Logical Chain Lengths, and Smart Gen tasks.',
    csa.primary_judge_model_id,
    judgeOptions,
    val => { csa.primary_judge_model_id = val; }
  ));

  // 2. Fallback Judge Model Chain (Interactive Ordered Pill Array + Add Dropdown)
  const chainRow = document.createElement('div');
  chainRow.className = 'setting-full';
  chainRow.innerHTML = `<div class="stitle">Fallback Judge Model Chain (Ordered Backups if Primary Times Out or Fails)</div>
    <div class="sdesc">Tried in order if the Primary Judge Model takes longer than the Judge Timeout or returns invalid JSON.</div>`;
  const chips = document.createElement('div');
  chips.className = 'chain-chips';
  (csa.fallback_judge_model_ids || []).forEach((mid, idx) => {
    const chip = document.createElement('span');
    chip.className = 'chain-chip';
    const mc = MODEL_CATALOG.find(x => x.model_id === mid);
    const name = mc ? mc.display_name : mid;
    chip.innerHTML = `<span>#${idx + 1}: ${name} <small style="color:var(--sub)">(${mid})</small></span>`;
    if (idx > 0) {
      const up = document.createElement('button');
      up.type = 'button';
      up.textContent = '↑';
      up.title = 'Move Earlier in Chain';
      up.onclick = () => {
        const tmp = csa.fallback_judge_model_ids[idx - 1];
        csa.fallback_judge_model_ids[idx - 1] = csa.fallback_judge_model_ids[idx];
        csa.fallback_judge_model_ids[idx] = tmp;
        drawAgents();
      };
      chip.appendChild(up);
    }
    const rm = document.createElement('button');
    rm.type = 'button';
    rm.textContent = '×';
    rm.title = 'Remove Backup Model';
    rm.onclick = () => {
      csa.fallback_judge_model_ids.splice(idx, 1);
      drawAgents();
    };
    chip.appendChild(rm);
    chips.appendChild(chip);
  });
  chainRow.appendChild(chips);

  const addChainBar = document.createElement('div');
  addChainBar.style.cssText = 'display:flex;gap:8px;align-items:center';
  const addSel = document.createElement('select');
  addSel.className = 'f';
  judgeOptions.forEach(jo => {
    const o = document.createElement('option');
    o.value = jo.val;
    o.textContent = jo.label;
    addSel.appendChild(o);
  });
  const addBtn = document.createElement('button');
  addBtn.type = 'button';
  addBtn.className = 'btn';
  addBtn.textContent = '+ Add Backup Judge';
  addBtn.onclick = () => {
    if (!csa.fallback_judge_model_ids.includes(addSel.value)) {
      csa.fallback_judge_model_ids.push(addSel.value);
      drawAgents();
    }
  };
  addChainBar.appendChild(addSel);
  addChainBar.appendChild(addBtn);
  chainRow.appendChild(addChainBar);
  box.appendChild(chainRow);

  // 3. Agent Input Character Limit per Model Response
  box.appendChild(makeSelectRow(
    'Consensus & Smart Gen Input Character Limit per Model Response (Max Characters)',
    'Maximum characters taken from each Ticker model response and passed into the Judge Agents. Keeps synthesis fast and prevents context overflow.',
    csa.agent_input_max_chars_per_model_response,
    [
      { val: 1200, label: '1,200 Max Characters (~200 words per model — Fastest synthesis)' },
      { val: 2200, label: '2,200 Max Characters (~350 words per model — Recommended balance)' },
      { val: 4000, label: '4,000 Max Characters (~650 words per model — Full long-form answers)' },
      { val: 8000, label: '8,000 Max Characters (~1,300 words per model — Maximum detail)' }
    ],
    val => { csa.agent_input_max_chars_per_model_response = Number(val); }
  ));

  // 4. Primary Judge Max Output Tokens
  box.appendChild(makeSelectRow(
    'Primary Judge Max Output Length (Max Tokens)',
    'Maximum JSON output token budget allocated to the Primary Consensus & Smart Gen Judge Model.',
    csa.primary_judge_max_output_tokens,
    [
      { val: 1500, label: '1,500 Max Tokens (Compact JSON output)' },
      { val: 2500, label: '2,500 Max Tokens (Recommended — fits 11 model summaries + sentiment groups)' },
      { val: 4000, label: '4,000 Max Tokens (Expanded JSON output)' }
    ],
    val => { csa.primary_judge_max_output_tokens = Number(val); }
  ));

  // 5. Fallback Judge Max Output + Thinking Tokens
  box.appendChild(makeSelectRow(
    'Fallback Judge Max Output + Reasoning Length (Max Tokens)',
    'Larger token budget granted when failing over to a heavy reasoning model (e.g. Nemotron 3 Super or GLM 5.3) so its internal <think> chain never truncates the JSON.',
    csa.fallback_judge_max_output_and_thinking_tokens,
    [
      { val: 4000, label: '4,000 Max Tokens (Standard)' },
      { val: 6000, label: '6,000 Max Tokens (Extended)' },
      { val: 9000, label: '9,000 Max Tokens (Recommended — prevents <think> truncation on 120B+ models)' },
      { val: 12000, label: '12,000 Max Tokens (Maximum budget)' }
    ],
    val => { csa.fallback_judge_max_output_and_thinking_tokens = Number(val); }
  ));

  // 6. Judge Timeout (Seconds)
  box.appendChild(makeSelectRow(
    'Consensus & Smart Gen Judge Timeout (Seconds)',
    'Maximum seconds to wait for the current Judge Model before automatically switching to the next model in the Fallback Judge Chain.',
    csa.judge_model_timeout_seconds,
    [
      { val: 45, label: '45 Seconds (Fast failover to backup judge)' },
      { val: 75, label: '75 Seconds (Balanced failover)' },
      { val: 110, label: '110 Seconds (Recommended — allows full synthesis across 11 models)' },
      { val: 180, label: '180 Seconds (3 Minutes — Extended patience)' }
    ],
    val => { csa.judge_model_timeout_seconds = Number(val); }
  ));

  // 7. Instructions
  box.appendChild(makeTextareaBlock(
    'Consensus Summary & Ratio Judge Instruction',
    'System prompt instructing Judge Agent #1 how to derive each model response\'s minimal actionable sentiment, group identical sentiments, and elect the democratic Consensus Summary.',
    csa.consensus_summary_and_ratio_instruction,
    val => { csa.consensus_summary_and_ratio_instruction = val; }
  ));

  box.appendChild(makeTextareaBlock(
    'Logical Chain Length Judge Instruction',
    'System prompt instructing Judge Agent #2 how to count explicit and implicit logical chains for each response and record the Consensus Summary\'s max chain depth.',
    csa.logical_chain_length_instruction,
    val => { csa.logical_chain_length_instruction = val; }
  ));

  box.appendChild(makeTextareaBlock(
    'Smart Gen Autonomous Task & Artifact Extraction Instruction',
    'System prompt instructing the Smart Gen Agent how to create or update projects, tasks, timed calendar reminders, memories, and artifacts from ongoing conversations.',
    csa.smartgen_task_extraction_instruction,
    val => { csa.smartgen_task_extraction_instruction = val; }
  ));
}

// ---------------- 5. PROMPT MODES CONFIGURATION ----------------
const MODE_META = {
  chat: { title: 'Chat Mode (Direct Answer, No Web Search)', sub: 'Fastest mode: models answer directly from their weights without querying Tavily web search.' },
  internet: { title: 'Internet Mode (Live Web Search + Inline Citations)', sub: 'Runs a fast live web search first and instructs models to answer concisely with [n] inline source citations.' },
  research: { title: 'Research Mode (Structured Multi-Section Report)', sub: 'Runs an advanced web search, synthesizes evidence & trade-offs with [n] citations, and auto-saves a Markdown report to Files > Generated.' },
  deep: { title: 'Deep Research Mode (Annotated Research Paper)', sub: 'Runs an exhaustive 12-source advanced search, evaluates evidence strength & source disagreements, and saves the full paper to Files > Generated.' }
};

function drawModes() {
  const box = document.getElementById('modes-box');
  box.innerHTML = '';
  const pmc = S.prompt_modes_configuration;
  ['chat', 'internet', 'research', 'deep'].forEach(mk => {
    const m = pmc[mk];
    const meta = MODE_META[mk];
    const card = document.createElement('div');
    card.className = 'mode-card';
    card.innerHTML = `<h3>${meta.title}</h3><div class="msub">${meta.sub}</div>`;

    if (mk !== 'chat') {
      // Web Search Depth selector
      const dDiv = document.createElement('div');
      dDiv.className = 'mode-kv';
      dDiv.innerHTML = `<label class="field-lbl">Web Search Depth (Tavily API)</label>`;
      const dSel = document.createElement('select');
      dSel.className = 'f';
      [
        { val: 'basic', label: 'Basic Search — Fast snippet lookup (~1–2s latency, 1 API credit)' },
        { val: 'advanced', label: 'Advanced Search — Deep full-page extraction (~3–5s latency, 2 API credits, higher completeness)' }
      ].forEach(o => {
        const opt = document.createElement('option');
        opt.value = o.val;
        opt.textContent = o.label;
        if (m.web_search_depth === o.val) opt.selected = true;
        dSel.appendChild(opt);
      });
      dSel.onchange = () => { m.web_search_depth = dSel.value; };
      dDiv.appendChild(dSel);
      card.appendChild(dDiv);

      // Web Sources Count selector
      const cDiv = document.createElement('div');
      cDiv.className = 'mode-kv';
      cDiv.innerHTML = `<label class="field-lbl">Cited Web Sources Fetched per Prompt (Source Count)</label>`;
      const cSel = document.createElement('select');
      cSel.className = 'f';
      [
        { val: 3, label: '3 Web Sources (Fastest, minimal context)' },
        { val: 5, label: '5 Web Sources (Recommended for Internet Mode)' },
        { val: 8, label: '8 Web Sources (Recommended for Research Mode)' },
        { val: 12, label: '12 Web Sources (Recommended for Deep Research Mode)' },
        { val: 15, label: '15 Web Sources (Maximum cross-verification)' }
      ].forEach(o => {
        const opt = document.createElement('option');
        opt.value = String(o.val);
        opt.textContent = o.label;
        if (Number(m.web_sources_fetched_count) === o.val) opt.selected = true;
        cSel.appendChild(opt);
      });
      cSel.onchange = () => { m.web_sources_fetched_count = Number(cSel.value); };
      cDiv.appendChild(cSel);
      card.appendChild(cDiv);

      // Max Chars per Web Source Excerpt selector
      const sDiv = document.createElement('div');
      sDiv.className = 'mode-kv';
      sDiv.innerHTML = `<label class="field-lbl">Max Excerpt Length per Web Source (Max Characters)</label>`;
      const sSel = document.createElement('select');
      sSel.className = 'f';
      [
        { val: 600, label: '600 Max Characters per Source (~100 words — Compact context)' },
        { val: 1200, label: '1,200 Max Characters per Source (~200 words — Recommended standard excerpt)' },
        { val: 2400, label: '2,400 Max Characters per Source (~400 words — Extended passage)' },
        { val: 4000, label: '4,000 Max Characters per Source (~650 words — Full article context)' }
      ].forEach(o => {
        const opt = document.createElement('option');
        opt.value = String(o.val);
        opt.textContent = o.label;
        if (Number(m.max_chars_per_web_source_excerpt) === o.val) opt.selected = true;
        sSel.appendChild(opt);
      });
      sSel.onchange = () => { m.max_chars_per_web_source_excerpt = Number(sSel.value); };
      sDiv.appendChild(sSel);
      card.appendChild(sDiv);
    }

    // Max Response Output Tokens selector
    const tDiv = document.createElement('div');
    tDiv.className = 'mode-kv';
    tDiv.innerHTML = `<label class="field-lbl">Max Model Answer Length (Max Output Tokens)</label>`;
    const tSel = document.createElement('select');
    tSel.className = 'f';
    [
      { val: 600, label: '600 Max Tokens (~450 words — Brief answer)' },
      { val: 900, label: '900 Max Tokens (~650 words — Recommended for Chat Mode)' },
      { val: 1200, label: '1,200 Max Tokens (~900 words — Recommended for Internet Mode)' },
      { val: 2400, label: '2,400 Max Tokens (~1,800 words — Recommended for Research Report)' },
      { val: 4000, label: '4,000 Max Tokens (~3,000 words — Recommended for Deep Research Paper)' },
      { val: 6000, label: '6,000 Max Tokens (~4,500 words — Maximum long-form treatise)' }
    ].forEach(o => {
      const opt = document.createElement('option');
      opt.value = String(o.val);
      opt.textContent = o.label;
      if (Number(m.max_response_output_tokens) === o.val) opt.selected = true;
      tSel.appendChild(opt);
    });
    tSel.onchange = () => { m.max_response_output_tokens = Number(tSel.value); };
    tDiv.appendChild(tSel);
    card.appendChild(tDiv);

    // Max Response Wait Timeout (Seconds)
    const wDiv = document.createElement('div');
    wDiv.className = 'mode-kv';
    wDiv.innerHTML = `<label class="field-lbl">Mode Overall Response Deadline (Seconds)</label>`;
    const wSel = document.createElement('select');
    wSel.className = 'f';
    [
      { val: 60, label: '60 Seconds (1 min — Fast cutoff)' },
      { val: 100, label: '100 Seconds (1 min 40 sec — Standard Chat deadline)' },
      { val: 120, label: '120 Seconds (2 min — Standard Internet deadline)' },
      { val: 180, label: '180 Seconds (3 min — Standard Research deadline)' },
      { val: 240, label: '240 Seconds (4 min — Standard Deep Research deadline)' },
      { val: 300, label: '300 Seconds (5 min — Extended patience for 550B models)' }
    ].forEach(o => {
      const opt = document.createElement('option');
      opt.value = String(o.val);
      opt.textContent = o.label;
      if (Number(m.max_response_wait_timeout_seconds) === o.val) opt.selected = true;
      wSel.appendChild(opt);
    });
    wSel.onchange = () => { m.max_response_wait_timeout_seconds = Number(wSel.value); };
    wDiv.appendChild(wSel);
    card.appendChild(wDiv);

    // Response Style Instruction
    const iDiv = document.createElement('div');
    iDiv.className = 'mode-kv';
    iDiv.innerHTML = `<label class="field-lbl">Mode System Instruction Sent to All Ticker Models</label>`;
    const ta = document.createElement('textarea');
    ta.className = 'f';
    ta.rows = 4;
    ta.value = m.response_style_instruction || '';
    ta.oninput = () => { m.response_style_instruction = ta.value; };
    iDiv.appendChild(ta);
    card.appendChild(iDiv);

    box.appendChild(card);
  });
}

// ---------------- 6. MODEL EXECUTION & STREAM LIMITS ----------------
function drawLimits() {
  const box = document.getElementById('limits-box');
  box.innerHTML = '';
  const mel = S.model_execution_and_stream_limits;

  box.appendChild(makeSelectRow(
    'Default Model Creativity / Temperature (0.0 to 1.0)',
    'Default sampling temperature applied to all Ticker Response Models that do not specify a custom override.',
    mel.default_model_temperature,
    [
      { val: 0.0, label: '0.0 — Strictly Deterministic (Exact facts & code, zero variation)' },
      { val: 0.2, label: '0.2 — High Precision (Tightly grounded factual responses)' },
      { val: 0.4, label: '0.4 — Balanced Default (Accurate reasoning with natural phrasing)' },
      { val: 0.7, label: '0.7 — Creative & Expansive (Varied phrasing & brainstorming)' },
      { val: 1.0, label: '1.0 — Maximum Creativity (High diversity, less predictable)' }
    ],
    val => { mel.default_model_temperature = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Max Internal Reasoning (<think>) Token Budget per Model (Max Tokens)',
    'Extra token budget granted to reasoning models for hidden chain-of-thought before writing their visible answer (automatically stripped before display).',
    mel.max_internal_thinking_tokens_per_model,
    [
      { val: 1000, label: '1,000 Max Thinking Tokens (Brief internal thought — faster first token)' },
      { val: 2000, label: '2,000 Max Thinking Tokens (Moderate internal reasoning)' },
      { val: 4000, label: '4,000 Max Thinking Tokens (Recommended — full multi-step reasoning without truncating answer)' },
      { val: 8000, label: '8,000 Max Thinking Tokens (Extended deep reasoning budget)' }
    ],
    val => { mel.max_internal_thinking_tokens_per_model = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Max Follow-Up Reply Length in Single-Model Thread (Max Tokens)',
    'Maximum output length when you send a follow-up reply directly to a specific model inside its expanded response card.',
    mel.max_followup_reply_output_tokens,
    [
      { val: 800, label: '800 Max Tokens (~600 words — Concise reply)' },
      { val: 1400, label: '1,400 Max Tokens (~1,050 words — Recommended detailed reply)' },
      { val: 2400, label: '2,400 Max Tokens (~1,800 words — Long-form reply)' },
      { val: 4000, label: '4,000 Max Tokens (~3,000 words — Exhaustive reply)' }
    ],
    val => { mel.max_followup_reply_output_tokens = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Max Stream Silence / Stall Timeout Before Fallback (Seconds)',
    'Longest silence allowed while waiting for a streaming model\'s next token. If exceeded, the stalled stream is aborted and retried as a single request.',
    mel.max_stream_silence_stall_timeout_seconds,
    [
      { val: 20, label: '20 Seconds (Aggressive stall cutoff)' },
      { val: 30, label: '30 Seconds (Fast stall cutoff)' },
      { val: 45, label: '45 Seconds (Recommended — allows 30s queue wait + thinking pause)' },
      { val: 60, label: '60 Seconds (Patient stall cutoff)' },
      { val: 90, label: '90 Seconds (Maximum patience for heavy reasoning models)' }
    ],
    val => { mel.max_stream_silence_stall_timeout_seconds = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Non-Streaming Fallback Request Timeout (Seconds)',
    'Maximum seconds to wait when a model falls back from SSE streaming to a standard single HTTP completion call.',
    mel.non_streaming_fallback_timeout_seconds,
    [
      { val: 60, label: '60 Seconds (1 Minute)' },
      { val: 120, label: '120 Seconds (2 Minutes)' },
      { val: 150, label: '150 Seconds (2.5 Minutes — Recommended)' },
      { val: 240, label: '240 Seconds (4 Minutes)' }
    ],
    val => { mel.non_streaming_fallback_timeout_seconds = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Failed Request Max Retry Attempts Across API Keys (Attempts)',
    'Number of attempts made when a provider returns an HTTP error (automatically rotating to the next API key in round-robin on each retry).',
    mel.failed_request_max_retry_attempts,
    [
      { val: 1, label: '1 Attempt (No retries — fail immediately on error)' },
      { val: 2, label: '2 Attempts (Recommended — 1 automatic retry on next API key)' },
      { val: 3, label: '3 Attempts (Up to 2 automatic retries across API keys)' },
      { val: 4, label: '4 Attempts (Maximum resilience across key pool)' }
    ],
    val => { mel.failed_request_max_retry_attempts = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Wait Delay Between Retry Attempts (Seconds)',
    'Pause duration in seconds between failed request attempts so transient provider rate-limits can clear.',
    mel.retry_wait_delay_seconds,
    [
      { val: 0.5, label: '0.5 Seconds (Near-instant retry)' },
      { val: 1.5, label: '1.5 Seconds (Recommended brief pause)' },
      { val: 3.0, label: '3.0 Seconds (Standard rate-limit cooldown)' },
      { val: 5.0, label: '5.0 Seconds (Extended rate-limit cooldown)' }
    ],
    val => { mel.retry_wait_delay_seconds = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Prompt Web Search API Timeout (Seconds)',
    'Maximum seconds to wait for Tavily web search results during Internet, Research, and Deep Research modes.',
    mel.web_search_request_timeout_seconds,
    [
      { val: 15, label: '15 Seconds (Fast cutoff)' },
      { val: 30, label: '30 Seconds (Standard timeout)' },
      { val: 40, label: '40 Seconds (Recommended for 12-source Advanced searches)' },
      { val: 60, label: '60 Seconds (Extended timeout)' }
    ],
    val => { mel.web_search_request_timeout_seconds = Number(val); }
  ));
}

// ---------------- 7. IN-APP BROWSER & STORAGE LIMITS ----------------
function drawBrowserAndStorage() {
  const box = document.getElementById('browser-box');
  box.innerHTML = '';
  const bsl = S.in_app_browser_and_storage_limits;

  box.appendChild(makeSelectRow(
    'In-App Browser Fallback Search Depth',
    'Tavily search depth used when the In-App Browser renders clean search results (e.g. when a search engine serves a bot challenge).',
    bsl.browser_fallback_search_depth,
    [
      { val: 'basic', label: 'Basic Search — Fast ~1s results page (1 API credit — Recommended)' },
      { val: 'advanced', label: 'Advanced Search — Deep snippet extraction (~3s, 2 API credits)' }
    ],
    val => { bsl.browser_fallback_search_depth = val; }
  ));

  box.appendChild(makeSelectRow(
    'In-App Browser Search Results Count (Max Results)',
    'Number of web search results displayed per query inside the In-App Browser.',
    bsl.browser_fallback_search_max_results,
    [
      { val: 5, label: '5 Results per Page' },
      { val: 10, label: '10 Results per Page (Recommended standard)' },
      { val: 15, label: '15 Results per Page' },
      { val: 20, label: '20 Results per Page' }
    ],
    val => { bsl.browser_fallback_search_max_results = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'In-App Browser Search Timeout (Seconds)',
    'Maximum seconds to wait for fallback search results inside the In-App Browser.',
    bsl.browser_fallback_search_timeout_seconds,
    [
      { val: 15, label: '15 Seconds' },
      { val: 30, label: '30 Seconds (Recommended)' },
      { val: 45, label: '45 Seconds' }
    ],
    val => { bsl.browser_fallback_search_timeout_seconds = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Max Attached Files per Prompt Message (Max Files)',
    'Maximum number of documents/images from the File Manager that can be attached to a single prompt.',
    bsl.max_attached_files_per_prompt,
    [
      { val: 4, label: '4 Attached Files Max' },
      { val: 8, label: '8 Attached Files Max' },
      { val: 12, label: '12 Attached Files Max (Recommended)' },
      { val: 20, label: '20 Attached Files Max' }
    ],
    val => { bsl.max_attached_files_per_prompt = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Max Saved Conversation Sessions in History (Max Sessions)',
    'Maximum number of past prompt sessions retained in data\\history.json before the oldest sessions are automatically pruned.',
    bsl.max_saved_history_sessions,
    [
      { val: 50, label: '50 Saved Sessions' },
      { val: 100, label: '100 Saved Sessions' },
      { val: 200, label: '200 Saved Sessions (Recommended)' },
      { val: 500, label: '500 Saved Sessions' },
      { val: 1000, label: '1,000 Saved Sessions' }
    ],
    val => { bsl.max_saved_history_sessions = Number(val); }
  ));

  box.appendChild(makeSelectRow(
    'Max Saved Smart Gen Cards & Tasks (Max Items)',
    'Maximum number of Smart Gen projects, tasks, reminders, memories, and artifacts retained in data\\smartgen_cards.json.',
    bsl.max_saved_smartgen_items,
    [
      { val: 50, label: '50 Smart Gen Items' },
      { val: 100, label: '100 Smart Gen Items (Recommended)' },
      { val: 250, label: '250 Smart Gen Items' },
      { val: 500, label: '500 Smart Gen Items' }
    ],
    val => { bsl.max_saved_smartgen_items = Number(val); }
  ));
}

// ---------------- 8. DISCOVER MARKET IMAGE GENERATION & THEME STORE ----------------
function drawMarketAndThemes() {
  const mBox = document.getElementById('market-box');
  mBox.innerHTML = '';
  const dm = S.discover_market_image_generation;

  const orderStr = (dm.image_provider_priority_order || ['Cloudflare', 'NVIDIA', 'fal']).join(',');
  mBox.appendChild(makeSelectRow(
    'Discover Market Image Provider Priority & Failover Order',
    'Order in which image providers are tried when generating images. If the first provider is out of daily quota or down, the next provider takes over automatically.',
    orderStr,
    [
      { val: 'Cloudflare,NVIDIA,fal', label: '1st Cloudflare (Free Daily 2048px) → 2nd NVIDIA (Free FLUX.1) → 3rd fal.ai (Paid 2K) [Recommended]' },
      { val: 'NVIDIA,Cloudflare,fal', label: '1st NVIDIA (Free FLUX.1) → 2nd Cloudflare (Free Daily 2048px) → 3rd fal.ai (Paid 2K)' },
      { val: 'fal,Cloudflare,NVIDIA', label: '1st fal.ai (Paid 2K High-Res $0.08/img) → 2nd Cloudflare → 3rd NVIDIA' },
      { val: 'Cloudflare,NVIDIA', label: 'Free Providers Only: 1st Cloudflare → 2nd NVIDIA (Never call paid fal.ai)' }
    ],
    val => { dm.image_provider_priority_order = val.split(','); }
  ));

  mBox.appendChild(makeSelectRow(
    'Cloudflare Workers AI Image Model',
    'FLUX model executed on your Cloudflare Imagine Worker (up to 2048px on the long side, supports reference images, free daily allowance).',
    dm.cloudflare_flux_model_id,
    [
      { val: '@cf/black-forest-labs/flux-2-klein-4b', label: 'FLUX.2 Klein 4B — Fastest high-detail 2048px generation + reference images (Recommended)' },
      { val: '@cf/black-forest-labs/flux-2-dev', label: 'FLUX.2 Dev — Heavier step weight, slower generation' },
      { val: '@cf/black-forest-labs/flux-1-schnell', label: 'FLUX.1 Schnell — Ultra-fast 4-step draft generation' }
    ],
    val => { dm.cloudflare_flux_model_id = val; }
  ));

  mBox.appendChild(makeSelectRow(
    'NVIDIA GenAI Image Model',
    'FLUX model executed via your NVIDIA API keys (50-step base CFG 3.5, up to 1344px).',
    dm.nvidia_flux_model_id,
    [
      { val: 'black-forest-labs/flux.1-dev', label: 'FLUX.1 Dev (black-forest-labs/flux.1-dev) — 50-step photorealistic & artistic synthesis (Recommended)' }
    ],
    val => { dm.nvidia_flux_model_id = val; }
  ));

  mBox.appendChild(makeSelectRow(
    'fal.ai Queue Image Model',
    'High-resolution model executed on fal.ai when selected or when free daily providers are exhausted.',
    dm.fal_image_model_id,
    [
      { val: 'xai/grok-imagine-image/v2.0/text-to-image', label: 'xAI Image v2.0 (2K Native Resolution, strong prompt adherence — Recommended)' }
    ],
    val => { dm.fal_image_model_id = val; }
  ));

  mBox.appendChild(makeSelectRow(
    'Default Images Generated per Prompt (Image Count)',
    'Number of image variations generated in parallel each time you submit an image prompt in Discover Market.',
    dm.default_images_per_prompt_count,
    [
      { val: 1, label: '1 Image per Prompt (Fastest, minimum quota usage)' },
      { val: 2, label: '2 Images per Prompt (Side-by-side comparison pair)' },
      { val: 4, label: '4 Images per Prompt (Recommended 2×2 batch grid)' },
      { val: 6, label: '6 Images per Prompt (Expanded batch)' },
      { val: 8, label: '8 Images per Prompt (Maximum parallel batch)' }
    ],
    val => { dm.default_images_per_prompt_count = Number(val); }
  ));

  mBox.appendChild(makeSelectRow(
    'Default Image Aspect Ratio',
    'Default canvas shape for newly generated Discover Market images.',
    dm.default_image_aspect_ratio,
    [
      { val: '9:16', label: '9:16 — Vertical Phone Portrait (1152×2048 Cloudflare / 768×1344 NVIDIA — Recommended)' },
      { val: '3:4', label: '3:4 — Editorial Portrait Card (1536×2048 Cloudflare / 896×1152 NVIDIA)' },
      { val: '1:1', label: '1:1 — Square Format (2048×2048 Cloudflare / 1024×1024 NVIDIA)' },
      { val: '4:3', label: '4:3 — Standard Landscape (2048×1536 Cloudflare / 1152×896 NVIDIA)' },
      { val: '16:9', label: '16:9 — Widescreen Cinema (2048×1152 Cloudflare / 1344×768 NVIDIA)' }
    ],
    val => { dm.default_image_aspect_ratio = val; }
  ));

  mBox.appendChild(makeSelectRow(
    'fal.ai Output Resolution Tier',
    'Target pixel resolution when generating images through fal.ai.',
    dm.fal_image_resolution_tier,
    [
      { val: '1k', label: '1K Standard (1024px — Faster, lower cost)' },
      { val: '2k', label: '2K Ultra-Crisp (2048px — Recommended high-DPI quality)' }
    ],
    val => { dm.fal_image_resolution_tier = val; }
  ));

  mBox.appendChild(makeSelectRow(
    'fal.ai Rendering Quality Tier',
    'Balances rendering step density vs. per-image cost on fal.ai.',
    dm.fal_image_quality_tier,
    [
      { val: 'low', label: 'Low — Fast Draft Quality (Lowest cost)' },
      { val: 'medium', label: 'Medium — Balanced Production Quality ($0.08/image at 2K — Recommended)' },
      { val: 'high', label: 'High — Maximum Step Density (Slower, highest cost)' }
    ],
    val => { dm.fal_image_quality_tier = val; }
  ));

  mBox.appendChild(makeSelectRow(
    'Max Image Generation Wait Timeout (Seconds)',
    'Maximum total time to wait for queued image generation before marking the request as timed out.',
    dm.max_image_generation_wait_timeout_seconds,
    [
      { val: 180, label: '180 Seconds (3 Minutes)' },
      { val: 300, label: '300 Seconds (5 Minutes)' },
      { val: 600, label: '600 Seconds (10 Minutes — Recommended for busy queues)' }
    ],
    val => { dm.max_image_generation_wait_timeout_seconds = Number(val); }
  ));

  // Theme Store Card
  const tBox = document.getElementById('themes-box');
  tBox.innerHTML = '';
  const lts = S.live_wallpaper_themes_and_store;

  tBox.appendChild(makeSelectRow(
    'Live Wallpaper & Audio Catalog Worker URL',
    'Cloudflare R2 Worker endpoint serving the 4K/60fps live wallpapers, posters, and streaming audio packs.',
    lts.theme_catalog_worker_url,
    [
      { val: 'https://collider-themes.ebridavid.workers.dev/', label: 'Official Collider Cloudflare R2 Theme Catalog (https://collider-themes.ebridavid.workers.dev/)' }
    ],
    val => { lts.theme_catalog_worker_url = val; }
  ));

  tBox.appendChild(makeSelectRow(
    'Live Wallpaper Catalog Auto-Refresh Interval (Seconds)',
    'How often the server checks the Cloudflare R2 Theme Worker in the background for new wallpaper packs and audio tracks.',
    lts.theme_catalog_auto_refresh_seconds,
    [
      { val: 300, label: '300 Seconds (Every 5 Minutes)' },
      { val: 600, label: '600 Seconds (Every 10 Minutes — Recommended)' },
      { val: 1800, label: '1,800 Seconds (Every 30 Minutes)' },
      { val: 3600, label: '3,600 Seconds (Every 1 Hour)' }
    ],
    val => { lts.theme_catalog_auto_refresh_seconds = Number(val); }
  ));

  tBox.appendChild(makeSelectRow(
    'Premium Theme Pack Display Price (Fallback Price Badge)',
    'Price badge shown on Premium Theme packs before native App Store / Play Billing localized pricing loads.',
    lts.premium_theme_pack_display_price,
    [
      { val: '$1.99', label: '$1.99 per Theme Pack' },
      { val: '$2.99', label: '$2.99 per Theme Pack' },
      { val: '$4.99', label: '$4.99 per Theme Pack (Recommended PRD Standard)' },
      { val: '$6.99', label: '$6.99 per Theme Pack' },
      { val: '$9.99', label: '$9.99 per Theme Pack' }
    ],
    val => { lts.premium_theme_pack_display_price = val; }
  ));

  tBox.appendChild(makeSelectRow(
    'Music Tracks Bundled per Theme Pack (Track Count)',
    'Number of matching ambient/spatial audio tracks paired with each live wallpaper pack in the Theme Music Player.',
    lts.music_tracks_per_theme_pack_count,
    [
      { val: 1, label: '1 Track per Theme Pack' },
      { val: 3, label: '3 Tracks per Theme Pack' },
      { val: 5, label: '5 Tracks per Theme Pack (Recommended PRD Standard — 5 tracks per pack)' },
      { val: 8, label: '8 Tracks per Theme Pack' },
      { val: 10, label: '10 Tracks per Theme Pack' }
    ],
    val => { lts.music_tracks_per_theme_pack_count = Number(val); }
  ));

  tBox.appendChild(makeSelectRow(
    'In-App Purchase Paywall Mode (Store Checkout vs. Developer Testing Bypass)',
    'Controls whether clicking Buy on a Premium Theme Pack requires StoreKit / Play Billing receipt verification or unlocks immediately for free testing.',
    String(Boolean(lts.bypass_purchase_paywall_for_testing)),
    [
      { val: 'false', label: 'OFF — Production Paywall Enabled (Require StoreKit / Play Billing Checkout)' },
      { val: 'true', label: 'ON — Developer Testing Bypass (Unlock All Premium Themes Immediately on Click)' }
    ],
    val => { lts.bypass_purchase_paywall_for_testing = (val === 'true'); }
  ));
}

// Initial Render
renderCatalogSelector();
drawProviders();
drawTickerModels();
drawAgents();
drawModes();
drawLimits();
drawBrowserAndStorage();
drawMarketAndThemes();

let busy = false;
document.getElementById('f').onsubmit = async e => {
  e.preventDefault();
  if (busy) return;
  const payload = {
    host: H.value,
    providers: rows,
    settings: S
  };
  if (!window.pywebview) {
    busy = true;
    const g = document.getElementById('go-btn');
    const prevText = g.textContent;
    try {
      const r = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      g.textContent = r.ok ? '✓ Saved to data\\collider_config.json' : 'Save Failed';
      setTimeout(() => { g.textContent = prevText; }, 2000);
    } finally {
      busy = false;
    }
    return;
  }
  busy = true;
  try {
    const r = await pywebview.api.launch(payload);
    if (r && r.error) {
      H.classList.add('bad');
      H.focus();
      H.select();
    }
  } finally {
    busy = false;
  }
};
</script>
</body>
</html>"""

# E.D. — Collider — Signed: Gemini 4 Argon (2026-11-17)
"""Collider Preferences & Launch Configurator (macOS System Settings / Linear / Raycast convention).

- Two-pane layout: compact left category sidebar + clean right preference groups.
- Zero page clutter: concise labels on the left; detailed explanations and model capabilities live in hover tooltips (ⓘ).
- Universal Editable Selection Lists: every setting, model, parameter, and system/agent instruction is presented as a
  clean selection dropdown (<select>) paired with inline write-in / edit (✎), Update, + Add, and Remove (×) controls
  so any value or instruction wording can be customized on the fly, updated in place, or saved as a new selectable option.
"""

FORM = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Collider — Preferences &amp; Configuration</title>
<style>
:root {
  color-scheme: dark light;
  --bg: #0f1012;
  --sidebar: #141518;
  --surface: #18191d;
  --surface-hover: #1f2025;
  --field: #111215;
  --border: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.16);
  --text: #f2f3f5;
  --muted: #9498a1;
  --faint: #5e626b;
  --accent: #0a84ff;
  --accent-soft: rgba(10, 132, 255, 0.14);
  --green: #30d158;
  --red: #ff453a;
  --radius: 8px;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #f5f5f7;
    --sidebar: #ebebed;
    --surface: #ffffff;
    --surface-hover: #f9f9fb;
    --field: #f2f2f5;
    --border: rgba(0, 0, 0, 0.08);
    --border-strong: rgba(0, 0, 0, 0.16);
    --text: #1d1d1f;
    --muted: #6e6e73;
    --faint: #98989d;
    --accent: #0066cc;
    --accent-soft: rgba(0, 102, 204, 0.10);
    --green: #1d9bf0;
    --red: #d93025;
  }
}
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI Variable Text", "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
  display: flex;
  overflow: hidden;
}

/* Sidebar (macOS System Settings / Linear style) */
.sidebar {
  width: 220px;
  min-width: 220px;
  height: 100vh;
  background: var(--sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 14px 10px;
  user-select: none;
}
.brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 8px 12px;
}
.brand-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.brand-port {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 5px;
  background: var(--accent-soft);
  color: var(--accent);
}
.side-search {
  margin: 0 4px 10px;
}
.side-search input {
  width: 100%;
  background: var(--field);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 9px;
  color: var(--text);
  font: 12px inherit;
  outline: none;
}
.side-search input:focus { border-color: var(--accent); }
.nav-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  border-radius: 6px;
  color: var(--muted);
  font-weight: 500;
  font-size: 12.5px;
  cursor: pointer;
  border: 0;
  background: transparent;
  text-align: left;
  width: 100%;
}
.nav-item:hover { background: var(--surface-hover); color: var(--text); }
.nav-item.active {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}
.nav-badge {
  font-size: 10.5px;
  color: var(--faint);
  font-variant-numeric: tabular-nums;
}
.nav-item.active .nav-badge { color: var(--accent); }
.side-footer {
  padding-top: 10px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.save-status {
  font-size: 11px;
  color: var(--muted);
  padding: 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Main Content Area */
.main {
  flex: 1;
  height: 100vh;
  overflow-y: auto;
  padding: 24px 32px 80px;
}
.main-inner {
  max-width: 820px;
  margin: 0 auto;
}
.pane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.pane-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.pane-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Preference Groups & Rows */
.pref-section { margin-bottom: 26px; }
.pref-section.hidden { display: none; }
.group-title {
  font-size: 11.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
  margin: 0 0 8px 2px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.pref-group {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: visible;
}
.pref-row {
  display: grid;
  grid-template-columns: minmax(190px, 38%) 1fr;
  gap: 14px;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
}
.pref-row:last-child { border-bottom: 0; }
.pref-row.stack {
  grid-template-columns: 1fr;
  gap: 8px;
}

/* Labels & Hover Tooltips */
.lbl-wrap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}
.lbl-text {
  font-weight: 500;
  font-size: 13px;
  color: var(--text);
}
.tip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  border: 1px solid var(--border-strong);
  color: var(--muted);
  font-size: 10px;
  font-weight: 600;
  cursor: help;
  position: relative;
  flex-shrink: 0;
}
.tip:hover { color: var(--text); border-color: var(--accent); }
.tip[data-tip]:hover::after {
  content: attr(data-tip);
  position: absolute;
  left: 22px;
  top: 50%;
  transform: translateY(-50%);
  width: max-content;
  max-width: 320px;
  background: #1c1d22;
  color: #f2f3f5;
  border: 1px solid rgba(255,255,255,0.16);
  box-shadow: 0 8px 24px rgba(0,0,0,0.45);
  padding: 7px 10px;
  border-radius: 6px;
  font: 400 11.5px/1.4 -apple-system, BlinkMacSystemFont, sans-serif;
  z-index: 999;
  pointer-events: none;
  white-space: normal;
}

/* Controls & Universal Editable Combo */
.ctrl-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}
select.f, input.f, textarea.f {
  background: var(--field);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 9px;
  font: 12.5px/1.35 inherit;
  outline: none;
}
select.f { flex: 1; min-width: 0; cursor: pointer; }
input.f { flex: 1; min-width: 0; }
textarea.f {
  width: 100%;
  resize: vertical;
  min-height: 76px;
  font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  line-height: 1.45;
}
select.f:focus, input.f:focus, textarea.f:focus {
  border-color: var(--accent);
}

.btn {
  background: var(--field);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 5px 9px;
  font: 500 12px/1.2 inherit;
  cursor: pointer;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.btn:hover { border-color: var(--border-strong); background: var(--surface-hover); }
.btn-icon {
  padding: 5px 7px;
  color: var(--muted);
}
.btn-icon:hover { color: var(--text); }
.btn-icon.active { color: var(--accent); border-color: var(--accent); background: var(--accent-soft); }
.btn-primary {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
  font-weight: 600;
}
.btn-primary:hover { opacity: 0.92; background: var(--accent); }
.btn-danger {
  color: var(--red);
  border-color: rgba(255, 69, 58, 0.28);
}
.btn-danger:hover { background: rgba(255, 69, 58, 0.10); border-color: var(--red); }

/* Inline Write-In / List Editor Drawer inside Row */
.inline-editor {
  grid-column: 1 / -1;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  margin-top: 4px;
  display: none;
  flex-direction: column;
  gap: 6px;
}
.inline-editor.open { display: flex; }
.inline-editor-row {
  display: flex;
  gap: 6px;
  align-items: center;
}

/* Compact Table Rows for Providers & Models */
.item-row {
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.item-row:last-child { border-bottom: 0; }
.item-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}
.swatch {
  width: 24px;
  height: 24px;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: 5px;
  background: transparent;
  cursor: pointer;
  flex-shrink: 0;
}
.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 5px;
  background: var(--field);
  border: 1px solid var(--border);
  font-size: 11.5px;
}
.chip button {
  border: 0;
  background: none;
  color: var(--muted);
  cursor: pointer;
  padding: 0 2px;
  font-size: 12px;
}
.chip button:hover { color: var(--text); }

/* Mode Tabs inside Section 5 */
.subtabs {
  display: inline-flex;
  background: var(--field);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 2px;
  gap: 2px;
}
.subtab {
  border: 0;
  background: transparent;
  color: var(--muted);
  padding: 4px 11px;
  border-radius: 4px;
  font: 500 12px inherit;
  cursor: pointer;
}
.subtab.active {
  background: var(--surface);
  color: var(--text);
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

@media (max-width: 720px) {
  body { flex-direction: column; overflow: auto; }
  .sidebar { width: 100%; height: auto; border-right: 0; border-bottom: 1px solid var(--border); }
  .nav-list { flex-direction: row; overflow-x: auto; }
  .main { height: auto; padding: 16px; }
  .pref-row { grid-template-columns: 1fr; gap: 6px; }
  .item-main { flex-wrap: wrap; }
}
</style>
</head>
<body>

<aside class="sidebar">
  <div class="brand">
    <span class="brand-title">Preferences</span>
    <span class="brand-port" id="port-badge">6420</span>
  </div>
  <div class="side-search">
    <input type="text" id="global-filter" placeholder="Filter settings...">
  </div>
  <nav class="nav-list" id="side-nav">
    <button type="button" class="nav-item active" data-sec="all"><span>All Settings</span><span class="nav-badge">8</span></button>
    <button type="button" class="nav-item" data-sec="sec-host"><span>General &amp; Host</span></button>
    <button type="button" class="nav-item" data-sec="sec-keys"><span>Providers &amp; Keys</span><span class="nav-badge" id="badge-keys"></span></button>
    <button type="button" class="nav-item" data-sec="sec-models"><span>Ticker Models</span><span class="nav-badge" id="badge-models"></span></button>
    <button type="button" class="nav-item" data-sec="sec-agents"><span>Agents &amp; Prompts</span><span class="nav-badge">6</span></button>
    <button type="button" class="nav-item" data-sec="sec-modes"><span>Modes &amp; Search</span><span class="nav-badge">4</span></button>
    <button type="button" class="nav-item" data-sec="sec-limits"><span>Execution</span></button>
    <button type="button" class="nav-item" data-sec="sec-browser"><span>Browser &amp; Storage</span></button>
    <button type="button" class="nav-item" data-sec="sec-market"><span>Media &amp; Themes</span></button>
  </nav>
  <div class="side-footer">
    <div class="save-status" id="where"></div>
    <button type="button" class="btn btn-primary" id="side-save-btn" style="width:100%;padding:7px">Save Changes</button>
    <a href="/" class="btn" style="width:100%;text-decoration:none">← Open Collider App</a>
  </div>
</aside>

<main class="main">
  <form id="f" class="main-inner" autocomplete="off">
    <div class="pane-header">
      <div>
        <h1 id="pane-title">All Settings</h1>
      </div>
      <div class="pane-header-actions">
        <span id="save-pill" style="font-size:12px;color:var(--muted)">Ready</span>
        <a href="/" class="btn" style="text-decoration:none">← Open App</a>
        <button type="submit" class="btn btn-primary" id="go-btn">Save &amp; Apply Live</button>
      </div>
    </div>

    <!-- 1. GENERAL & HOST -->
    <section class="pref-section" id="sec-host">
      <div class="group-title"><span>General &amp; Session Host</span></div>
      <div class="pref-group" id="host-box"></div>
    </section>

    <!-- 2. PROVIDERS & KEYS -->
    <section class="pref-section" id="sec-keys">
      <div class="group-title">
        <span>API Providers &amp; Keys</span>
        <div style="display:flex;gap:6px;align-items:center">
          <select class="f" id="cat-select" style="width:220px;padding:3px 7px;font-size:11.5px"></select>
          <button type="button" class="btn btn-primary" id="cat-add-btn" style="padding:3px 8px;font-size:11.5px">+ Add Key</button>
          <button type="button" class="btn" id="add-blank-prov" style="padding:3px 8px;font-size:11.5px">+ Custom Row</button>
        </div>
      </div>
      <div class="pref-group" id="provider-rows"></div>
    </section>

    <!-- 3. TICKER MODELS -->
    <section class="pref-section" id="sec-models">
      <div class="group-title">
        <span>Ticker Models &amp; Per-Model Instructions</span>
        <div style="display:flex;gap:6px;align-items:center">
          <select class="f" id="quick-add-model-sel" style="width:220px;padding:3px 7px;font-size:11.5px"></select>
          <button type="button" class="btn btn-primary" id="quick-add-model-btn" style="padding:3px 8px;font-size:11.5px">+ Add Model</button>
          <button type="button" class="btn" id="add-custom-model-btn" style="padding:3px 8px;font-size:11.5px">+ Custom ID</button>
        </div>
      </div>
      <div class="pref-group" id="global-model-prompt-box" style="margin-bottom:10px"></div>
      <div class="pref-group" id="ticker-models-box"></div>
    </section>

    <!-- 4. AGENTS & PROMPTS -->
    <section class="pref-section" id="sec-agents">
      <div class="group-title"><span>Consensus &amp; Smart Gen Agents (Models, Limits &amp; System Instructions)</span></div>
      <div class="pref-group" id="agents-box"></div>
    </section>

    <!-- 5. MODES & SEARCH -->
    <section class="pref-section" id="sec-modes">
      <div class="group-title">
        <span>Prompt Modes &amp; Instructions</span>
        <div class="subtabs" id="mode-tabs">
          <button type="button" class="subtab active" data-mode="chat">Chat</button>
          <button type="button" class="subtab" data-mode="internet">Internet</button>
          <button type="button" class="subtab" data-mode="research">Research</button>
          <button type="button" class="subtab" data-mode="deep">Deep Research</button>
        </div>
      </div>
      <div class="pref-group" id="modes-box"></div>
    </section>

    <!-- 6. EXECUTION -->
    <section class="pref-section" id="sec-limits">
      <div class="group-title"><span>Execution, Reasoning &amp; Failover</span></div>
      <div class="pref-group" id="limits-box"></div>
    </section>

    <!-- 7. BROWSER & STORAGE -->
    <section class="pref-section" id="sec-browser">
      <div class="group-title"><span>In-App Browser &amp; Storage</span></div>
      <div class="pref-group" id="browser-box"></div>
    </section>

    <!-- 8. MEDIA & THEMES -->
    <section class="pref-section" id="sec-market">
      <div class="group-title"><span>Image Generation &amp; Wallpaper Store</span></div>
      <div class="pref-group" id="market-box" style="margin-bottom:10px"></div>
      <div class="pref-group" id="themes-box"></div>
    </section>
  </form>
</main>

<script>
const C = INITIAL || {};
const KEY_CATALOG = C.key_catalog || [];
const MODEL_CATALOG = C.model_catalog || [];

// Default Agent & Mode Instructions (so nothing is ever missing even if KV or disk config is partial)
const DEFAULT_AGENT_PROMPT = "Inputs:\n-User's prompt\n-response messages\n\nFrom this\nFill the following fields:\nConsensus Ratio: number of responses with the same sentiment / number of total responses\nConsensus Summary: For each response message, use the prompt message to derive need and message intent. This will simplify each message to its base minimal distinction/sentiment; this is the actionable portion of the message. Resolve democratically by counting the number of duplicates of each unique sentiment. The sentiment with the biggest count is the consensus summary verbatim.\n\nIn the table, indicate which responses are grouped with which sentiments, and indicate the consensus sentiment\n\nAccuracy and confidence and all subjective interpretations of a response are irrelevant. You are only recording reality, not advising. This is what makes this objectively valuable and universally desired.\n\nRecap:\n\nProvide the following:\nConsensus Ratio\nConsensus Summary, as derived (unique actionable takeaway, sentiment, point, intent, summary)";

const DEFAULT_AGENT_FORMAT = 'Reply with JSON only, in this shape, so the app can show it:\n{"need": "the need and intent derived from the prompt message",\n "summaries": {"R1": "...", "R2": "..."},\n "groups": [["R1", "R3"], ["R2"]],\n "consensus_summary": "..."}\nsummaries: each response\'s base minimal distinction/sentiment (the actionable portion of the message). Responses with the same sentiment have the same words.\ngroups: the responses grouped with each sentiment.\nconsensus_summary: the sentiment with the biggest count, verbatim.';

const DEFAULT_CHAIN_PROMPT = "Inputs:\n-User's prompt\n-response messages\n\nFor each response:\nCalculate, from the full response text and its service to the observed need, the depth (aka length) of the logical chain in the message. This count should include explicit and implicit logical chains. Explicit logical chains are all sequential clarifications/simplifications. They extend logic, not activity. And they serve the purpose by providing capability and independence to the prompter.\n\nCount the total logical chains (explicit + implicit) for each response message and provide the number in JSON. Also include in the logical chain length table a line for consensus summary and use the max length chain of all its members as its logical chain length value.";

const DEFAULT_CHAIN_FORMAT = 'Reply with JSON only, in this shape, so the app can show it:\n{"chains": {"R1": 0, "R2": 0}}\nchains: each response\'s total logical chains (explicit + implicit).';

const DEFAULT_SMARTGEN_PROMPT = "Smart Gen holds projects, tasks, reminders, memories, and artifacts.\nCreates the item when the conversation already contains it, unless that item exists for the same project, type, and model. A timed reminder also lands on the calendar.\nWhen ongoing conversation modifies facts/dates of an existing task or project, Smart Gen automatically updates existing records rather than duplicating.\nArtifacts, reminders, tasks, projects, and memories can be bidirectionally attached and embedded in any combination.";

const DEFAULT_SMARTGEN_FORMAT = 'Reply with JSON only, in this shape, so the app can file it:\n{"create": [{"type": "project | task | reminder | memory | artifact", "title": "...", "content": "...", "due": "date and time, or empty", "project": "..."}],\n "update": [{"id": "an existing item\'s id", "title": "...", "content": "...", "due": "..."}]}\nThe existing items are listed with their ids. Empty lists when the conversation contains no item.';

const rawS = C.settings || {};
const S = {
  global_system_instruction: rawS.global_system_instruction || '',
  custom_option_lists: rawS.custom_option_lists || {},
  ticker_response_models: Array.isArray(rawS.ticker_response_models) && rawS.ticker_response_models.length
    ? rawS.ticker_response_models
    : (MODEL_CATALOG.slice(0, 11).map(m => ({
        model_id: m.model_id,
        display_name: m.display_name,
        ticker_badge: m.ticker_badge,
        model_creator: m.model_creator,
        api_provider_route: m.api_provider_route || 'NVIDIA',
        badge_color_hex: m.badge_color_hex || '#60A5FA',
        custom_temperature: '',
        custom_system_instruction: ''
      }))),
  consensus_and_smartgen_agents: Object.assign({
    primary_judge_model_id: 'google/gemma-4-31b-it',
    fallback_judge_model_ids: ['google/gemma-4-31b-it', 'nvidia/nemotron-3-super-120b-a12b', 'z-ai/glm-5.3'],
    consensus_summary_and_ratio_instruction: DEFAULT_AGENT_PROMPT,
    consensus_json_format_instruction: DEFAULT_AGENT_FORMAT,
    logical_chain_length_instruction: DEFAULT_CHAIN_PROMPT,
    logical_chain_json_format_instruction: DEFAULT_CHAIN_FORMAT,
    smartgen_task_extraction_instruction: DEFAULT_SMARTGEN_PROMPT,
    smartgen_json_format_instruction: DEFAULT_SMARTGEN_FORMAT,
    agent_input_max_chars_per_model_response: 2200,
    primary_judge_max_output_tokens: 2500,
    fallback_judge_max_output_and_thinking_tokens: 9000,
    judge_model_timeout_seconds: 110
  }, rawS.consensus_and_smartgen_agents || {}),
  prompt_modes_configuration: {
    chat: Object.assign({
      response_style_instruction: 'Answer directly and concisely. Plain language, no jargon.',
      max_response_output_tokens: 900,
      max_response_wait_timeout_seconds: 100
    }, (rawS.prompt_modes_configuration && rawS.prompt_modes_configuration.chat) || {}),
    internet: Object.assign({
      response_style_instruction: 'Answer directly using the web sources provided. Cite sources inline as [n]. Plain language, no jargon.',
      web_search_depth: 'basic',
      web_sources_fetched_count: 5,
      max_chars_per_web_source_excerpt: 1200,
      max_response_output_tokens: 1200,
      max_response_wait_timeout_seconds: 120
    }, (rawS.prompt_modes_configuration && rawS.prompt_modes_configuration.internet) || {}),
    research: Object.assign({
      response_style_instruction: 'Write a research report: a one-paragraph answer first, then short sections with headings covering the evidence, the trade-offs and a clear recommendation. Cite sources inline as [n] and end with a numbered source list. Plain language, no jargon.',
      web_search_depth: 'advanced',
      web_sources_fetched_count: 8,
      max_chars_per_web_source_excerpt: 1200,
      max_response_output_tokens: 2400,
      max_response_wait_timeout_seconds: 180
    }, (rawS.prompt_modes_configuration && rawS.prompt_modes_configuration.research) || {}),
    deep: Object.assign({
      response_style_instruction: 'Write an annotated research paper: an abstract that states the answer, then numbered sections in which every claim carries its source [n] and a short note on why it matters or how strong the evidence is, a section on where the sources disagree, and a conclusion with practical next steps. More insight, no jargon: explain anything technical in everyday words. End with a numbered source list.',
      web_search_depth: 'advanced',
      web_sources_fetched_count: 12,
      max_chars_per_web_source_excerpt: 1200,
      max_response_output_tokens: 4000,
      max_response_wait_timeout_seconds: 240
    }, (rawS.prompt_modes_configuration && rawS.prompt_modes_configuration.deep) || {})
  },
  model_execution_and_stream_limits: Object.assign({
    default_model_temperature: 0.4,
    max_internal_thinking_tokens_per_model: 4000,
    max_followup_reply_output_tokens: 1400,
    max_stream_silence_stall_timeout_seconds: 45,
    non_streaming_fallback_timeout_seconds: 150,
    failed_request_max_retry_attempts: 2,
    retry_wait_delay_seconds: 1.5,
    web_search_request_timeout_seconds: 40
  }, rawS.model_execution_and_stream_limits || {}),
  in_app_browser_and_storage_limits: Object.assign({
    browser_fallback_search_depth: 'basic',
    browser_fallback_search_max_results: 10,
    browser_fallback_search_timeout_seconds: 30,
    max_attached_files_per_prompt: 12,
    max_saved_history_sessions: 200,
    max_saved_smartgen_items: 100
  }, rawS.in_app_browser_and_storage_limits || {}),
  discover_market_image_generation: Object.assign({
    image_provider_priority_order: ['Cloudflare', 'NVIDIA', 'fal'],
    cloudflare_flux_model_id: '@cf/black-forest-labs/flux-2-klein-4b',
    nvidia_flux_model_id: 'black-forest-labs/flux.1-dev',
    fal_image_model_id: 'xai/grok-imagine-image/v2.0/text-to-image',
    default_images_per_prompt_count: 4,
    default_image_aspect_ratio: '9:16',
    fal_image_resolution_tier: '2k',
    fal_image_quality_tier: 'medium',
    max_image_generation_wait_timeout_seconds: 600
  }, rawS.discover_market_image_generation || {}),
  live_wallpaper_themes_and_store: Object.assign({
    theme_catalog_worker_url: 'https://collider-themes.ebridavid.workers.dev/',
    theme_catalog_auto_refresh_seconds: 600,
    premium_theme_pack_display_price: '$4.99',
    music_tracks_per_theme_pack_count: 5,
    bypass_purchase_paywall_for_testing: false
  }, rawS.live_wallpaper_themes_and_store || {})
};

let hostPort = String(C.host || 6420);
let rows = (C.providers || []).map(r => ({
  provider_name: r.provider_name || r.name || 'NVIDIA',
  api_endpoint_url: r.api_endpoint_url || r.endpoint || 'https://integrate.api.nvidia.com/v1/chat/completions',
  api_key: r.api_key || r.key || '',
  extra_model_ids: r.extra_model_ids !== undefined ? r.extra_model_ids : (r.models || '')
}));

document.getElementById('where').textContent = WHERE;
document.getElementById('port-badge').textContent = hostPort;

// Sidebar Section Navigation & Search Filter
let activeSection = 'all';
const navButtons = Array.from(document.querySelectorAll('#side-nav .nav-item'));
const sections = Array.from(document.querySelectorAll('.pref-section'));

navButtons.forEach(btn => {
  btn.onclick = () => {
    activeSection = btn.dataset.sec;
    navButtons.forEach(b => b.classList.toggle('active', b === btn));
    document.getElementById('pane-title').textContent = btn.querySelector('span').textContent;
    sections.forEach(sec => {
      sec.classList.toggle('hidden', activeSection !== 'all' && sec.id !== activeSection);
    });
  };
});

document.getElementById('global-filter').oninput = e => {
  const q = e.target.value.trim().toLowerCase();
  document.querySelectorAll('.pref-row, .item-row').forEach(r => {
    if (!q) { r.style.display = ''; return; }
    r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
};

// ============================================================================
// UNIVERSAL EDITABLE SELECTION BOX HELPER
// Gives every field a clean <select> list + inline Edit / Update / + Add / × Remove
// ============================================================================
function getOptionsList(listKey, defaultOpts) {
  if (!Array.isArray(S.custom_option_lists[listKey]) || !S.custom_option_lists[listKey].length) {
    S.custom_option_lists[listKey] = defaultOpts.map(o => ({ val: String(o.val), label: String(o.label || o.val) }));
  }
  return S.custom_option_lists[listKey];
}

function makeEditableSelectRow({ listKey, label, tip, value, defaultOpts, isNumber, onChange }) {
  const row = document.createElement('div');
  row.className = 'pref-row';

  const left = document.createElement('div');
  left.className = 'lbl-wrap';
  const lt = document.createElement('span');
  lt.className = 'lbl-text';
  lt.textContent = label;
  left.appendChild(lt);
  if (tip) {
    const ti = document.createElement('span');
    ti.className = 'tip';
    ti.dataset.tip = tip;
    ti.textContent = 'i';
    left.appendChild(ti);
  }

  const right = document.createElement('div');
  right.className = 'ctrl-bar';

  const sel = document.createElement('select');
  sel.className = 'f';

  const editBtn = document.createElement('button');
  editBtn.type = 'button';
  editBtn.className = 'btn btn-icon';
  editBtn.title = 'Edit, add, or remove options inline';
  editBtn.textContent = '✎';

  const editor = document.createElement('div');
  editor.className = 'inline-editor';

  const editorRow = document.createElement('div');
  editorRow.className = 'inline-editor-row';

  const valInp = document.createElement('input');
  valInp.className = 'f';
  valInp.placeholder = 'Value';

  const lblInp = document.createElement('input');
  lblInp.className = 'f';
  lblInp.placeholder = 'Display label (optional)';

  const updBtn = document.createElement('button');
  updBtn.type = 'button';
  updBtn.className = 'btn btn-primary';
  updBtn.textContent = 'Update Selected';

  const addBtn = document.createElement('button');
  addBtn.type = 'button';
  addBtn.className = 'btn';
  addBtn.textContent = '+ Add Option';

  const rmBtn = document.createElement('button');
  rmBtn.type = 'button';
  rmBtn.className = 'btn btn-danger';
  rmBtn.textContent = 'Remove';

  let curVal = String(value ?? '');

  function renderSelect() {
    const opts = getOptionsList(listKey, defaultOpts);
    if (curVal !== '' && !opts.some(o => String(o.val) === curVal)) {
      opts.unshift({ val: curVal, label: curVal });
    }
    sel.innerHTML = '';
    opts.forEach((o, i) => {
      const opt = document.createElement('option');
      opt.value = String(o.val);
      opt.textContent = o.label || o.val;
      if (String(o.val) === curVal) opt.selected = true;
      sel.appendChild(opt);
    });
    const activeOpt = opts.find(o => String(o.val) === sel.value) || { val: curVal, label: curVal };
    valInp.value = activeOpt.val;
    lblInp.value = activeOpt.label;
  }

  sel.onchange = () => {
    curVal = sel.value;
    const opts = getOptionsList(listKey, defaultOpts);
    const activeOpt = opts.find(o => String(o.val) === curVal);
    if (activeOpt) {
      valInp.value = activeOpt.val;
      lblInp.value = activeOpt.label;
    }
    onChange(isNumber ? (curVal === '' ? '' : Number(curVal)) : curVal);
  };

  editBtn.onclick = () => {
    const open = !editor.classList.contains('open');
    editor.classList.toggle('open', open);
    editBtn.classList.toggle('active', open);
    if (open) valInp.focus();
  };

  updBtn.onclick = () => {
    const nv = valInp.value.trim();
    if (!nv && curVal !== '') return;
    const nl = lblInp.value.trim() || nv;
    const opts = getOptionsList(listKey, defaultOpts);
    const idx = opts.findIndex(o => String(o.val) === sel.value);
    if (idx >= 0) {
      opts[idx] = { val: nv, label: nl };
    } else {
      opts.push({ val: nv, label: nl });
    }
    curVal = nv;
    renderSelect();
    onChange(isNumber ? (nv === '' ? '' : Number(nv)) : nv);
  };

  addBtn.onclick = () => {
    const nv = valInp.value.trim();
    if (!nv) return;
    const nl = lblInp.value.trim() || nv;
    const opts = getOptionsList(listKey, defaultOpts);
    opts.push({ val: nv, label: nl });
    curVal = nv;
    renderSelect();
    onChange(isNumber ? (nv === '' ? '' : Number(nv)) : nv);
  };

  rmBtn.onclick = () => {
    const opts = getOptionsList(listKey, defaultOpts);
    if (opts.length <= 1) return;
    const idx = opts.findIndex(o => String(o.val) === sel.value);
    if (idx >= 0) opts.splice(idx, 1);
    curVal = opts[0].val;
    renderSelect();
    onChange(isNumber ? (curVal === '' ? '' : Number(curVal)) : curVal);
  };

  renderSelect();
  right.appendChild(sel);
  right.appendChild(editBtn);

  editorRow.appendChild(valInp);
  editorRow.appendChild(lblInp);
  editorRow.appendChild(updBtn);
  editorRow.appendChild(addBtn);
  editorRow.appendChild(rmBtn);
  editor.appendChild(editorRow);

  row.appendChild(left);
  row.appendChild(right);
  row.appendChild(editor);
  return row;
}

// Editable Prompt / Instruction Row: Preset <select> + Save/Update/Add/Remove + live <textarea>
function makePromptControl({ listKey, label, tip, value, defaultPresets, onChange }) {
  const row = document.createElement('div');
  row.className = 'pref-row stack';

  const top = document.createElement('div');
  top.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap';

  const left = document.createElement('div');
  left.className = 'lbl-wrap';
  const lt = document.createElement('span');
  lt.className = 'lbl-text';
  lt.textContent = label;
  left.appendChild(lt);
  if (tip) {
    const ti = document.createElement('span');
    ti.className = 'tip';
    ti.dataset.tip = tip;
    ti.textContent = 'i';
    left.appendChild(ti);
  }

  const bar = document.createElement('div');
  bar.style.cssText = 'display:flex;align-items:center;gap:6px;flex:1;max-width:520px;justify-content:flex-end';

  const sel = document.createElement('select');
  sel.className = 'f';

  const nameInp = document.createElement('input');
  nameInp.className = 'f';
  nameInp.style.maxWidth = '150px';
  nameInp.placeholder = 'Preset name';

  const updBtn = document.createElement('button');
  updBtn.type = 'button';
  updBtn.className = 'btn';
  updBtn.textContent = 'Update';
  updBtn.title = 'Save current wording over selected preset';

  const addBtn = document.createElement('button');
  addBtn.type = 'button';
  addBtn.className = 'btn';
  addBtn.textContent = '+ Add';
  addBtn.title = 'Save current wording as a new selectable preset';

  const rmBtn = document.createElement('button');
  rmBtn.type = 'button';
  rmBtn.className = 'btn btn-danger';
  rmBtn.textContent = '×';
  rmBtn.title = 'Remove selected preset from list';

  const ta = document.createElement('textarea');
  ta.className = 'f';
  ta.rows = Math.max(3, Math.min(8, String(value || '').split('\n').length + 1));
  ta.value = value || '';

  function getPresets() {
    if (!Array.isArray(S.custom_option_lists[listKey]) || !S.custom_option_lists[listKey].length) {
      S.custom_option_lists[listKey] = defaultPresets.map(p => ({ label: p.label, val: p.val }));
    }
    return S.custom_option_lists[listKey];
  }

  function renderPresets(selectIdx) {
    const presets = getPresets();
    if (value && !presets.some(p => p.val === value)) {
      presets.unshift({ label: 'Active Custom Prompt', val: value });
    }
    sel.innerHTML = '';
    let matchedIdx = selectIdx !== undefined ? selectIdx : presets.findIndex(p => p.val === ta.value);
    if (matchedIdx < 0) matchedIdx = 0;
    presets.forEach((p, idx) => {
      const o = document.createElement('option');
      o.value = String(idx);
      o.textContent = p.label;
      if (idx === matchedIdx) o.selected = true;
      sel.appendChild(o);
    });
    if (presets[matchedIdx]) nameInp.value = presets[matchedIdx].label;
  }

  sel.onchange = () => {
    const presets = getPresets();
    const chosen = presets[Number(sel.value)];
    if (chosen) {
      ta.value = chosen.val;
      nameInp.value = chosen.label;
      onChange(chosen.val);
    }
  };

  ta.oninput = () => {
    onChange(ta.value);
  };

  updBtn.onclick = () => {
    const presets = getPresets();
    const idx = Number(sel.value) || 0;
    const lbl = nameInp.value.trim() || (presets[idx] ? presets[idx].label : 'Updated Prompt');
    presets[idx] = { label: lbl, val: ta.value };
    renderPresets(idx);
    onChange(ta.value);
  };

  addBtn.onclick = () => {
    const presets = getPresets();
    const lbl = nameInp.value.trim() || `Custom Prompt #${presets.length + 1}`;
    presets.push({ label: lbl, val: ta.value });
    renderPresets(presets.length - 1);
    onChange(ta.value);
  };

  rmBtn.onclick = () => {
    const presets = getPresets();
    if (presets.length <= 1) return;
    const idx = Number(sel.value) || 0;
    presets.splice(idx, 1);
    ta.value = presets[0].val;
    renderPresets(0);
    onChange(ta.value);
  };

  renderPresets();
  bar.appendChild(sel);
  bar.appendChild(nameInp);
  bar.appendChild(updBtn);
  bar.appendChild(addBtn);
  bar.appendChild(rmBtn);

  top.appendChild(left);
  top.appendChild(bar);
  row.appendChild(top);
  row.appendChild(ta);
  return row;
}

// ============================================================================
// 1. GENERAL & HOST
// ============================================================================
function drawHost() {
  const box = document.getElementById('host-box');
  box.innerHTML = '';
  box.appendChild(makeEditableSelectRow({
    listKey: 'host_ports',
    label: 'Session Localhost Port',
    tip: 'Local port number (http://127.0.0.1:<port>/) used when running the local Collider server.',
    value: hostPort,
    isNumber: false,
    defaultOpts: [
      { val: '6420', label: '6420 (Argon Primary)' },
      { val: '8474', label: '8474 (Secondary)' },
      { val: '37418', label: '37418 (Legacy)' }
    ],
    onChange: v => {
      hostPort = String(v);
      document.getElementById('port-badge').textContent = hostPort;
    }
  }));
}

// ============================================================================
// 2. PROVIDERS & KEYS
// ============================================================================
const PROVIDER_PRESETS = [
  { name: 'NVIDIA', endpoint: 'https://integrate.api.nvidia.com/v1/chat/completions', tip: 'NVIDIA Integrate NIM (Ticker, Judges & FLUX.1)' },
  { name: 'OpenCode Zen', endpoint: 'https://opencode.ai/zen/v1/chat/completions', tip: 'OpenCode Zen Gateway (GPT-5.6 Luna, DeepSeek V4, Qwen 3.5)' },
  { name: 'OpenRouter', endpoint: 'https://openrouter.ai/api/v1/chat/completions', tip: 'OpenRouter Gateway (Claude 3.7, Gemini 2.5, GPT-4.1)' },
  { name: 'xAI', endpoint: 'https://api.x.ai/v1/chat/completions', tip: 'xAI Direct (Grok 3 & Grok Mini)' },
  { name: 'OpenAI', endpoint: 'https://api.openai.com/v1/chat/completions', tip: 'OpenAI Direct (GPT-4.1, GPT-4o, o3-mini)' },
  { name: 'Google Gemini', endpoint: 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions', tip: 'Google Gemini Direct' },
  { name: 'Kimi', endpoint: 'https://api.moonshot.cn/v1/chat/completions', tip: 'Moonshot Kimi 128K' },
  { name: 'MiniMax', endpoint: 'https://api.minimax.chat/v1/text/chatcompletion_v2', tip: 'MiniMax M3 Direct' },
  { name: 'Cohere', endpoint: 'https://api.cohere.com/v2/chat', tip: 'Cohere Command-A / R+' },
  { name: 'AI Hub Mix', endpoint: 'https://aihubmix.com/v1/chat/completions', tip: 'AI Hub Mix Aggregator' },
  { name: 'Crazyrouter', endpoint: 'https://cn.crazyrouter.com/v1/chat/completions', tip: 'Crazyrouter Aggregator' },
  { name: 'HuggingFace', endpoint: 'https://router.huggingface.co/v1/chat/completions', tip: 'Hugging Face Router' },
  { name: 'Vercel Gateway', endpoint: 'https://ai-gateway.vercel.sh/v1/chat/completions', tip: 'Vercel AI Gateway' },
  { name: 'Cloudflare', endpoint: 'https://collider-imagine.ebridavid.workers.dev', tip: 'Cloudflare Workers AI FLUX.2 Image Generator' },
  { name: 'fal', endpoint: 'https://queue.fal.run', tip: 'fal.ai 2K Image Queue' },
  { name: 'Tavily', endpoint: 'https://api.tavily.com/search', tip: 'Tavily Web Search API' },
  { name: 'Groq', endpoint: 'https://api.groq.com/openai/v1/audio/transcriptions', tip: 'Groq Whisper Speech-to-Text' },
  { name: 'Phone', endpoint: 'https://collider-phone.ebridavid.workers.dev', tip: 'Permanent Mobile Tunnel' }
];

const catSelect = document.getElementById('cat-select');
function populateKeyCatalogDropdown() {
  catSelect.innerHTML = '';
  KEY_CATALOG.forEach(it => {
    const o = document.createElement('option');
    o.value = it.id;
    const active = rows.some(r => (r.api_key || '').trim() === it.api_key);
    o.textContent = (active ? '✓ ' : '') + it.label;
    o.title = it.consequence || '';
    catSelect.appendChild(o);
  });
  document.getElementById('badge-keys').textContent = String(rows.length);
}

document.getElementById('cat-add-btn').onclick = () => {
  const chosen = KEY_CATALOG.find(k => k.id === catSelect.value);
  if (!chosen) return;
  rows.push({
    provider_name: chosen.provider_name,
    api_endpoint_url: chosen.api_endpoint_url,
    api_key: chosen.api_key,
    extra_model_ids: chosen.extra_model_ids || ''
  });
  drawProviders();
};

document.getElementById('add-blank-prov').onclick = () => {
  rows.push({ provider_name: 'NVIDIA', api_endpoint_url: 'https://integrate.api.nvidia.com/v1/chat/completions', api_key: '', extra_model_ids: '' });
  drawProviders();
};

function drawProviders() {
  populateKeyCatalogDropdown();
  const box = document.getElementById('provider-rows');
  box.innerHTML = '';
  rows.forEach((r, idx) => {
    const row = document.createElement('div');
    row.className = 'item-row';

    const main = document.createElement('div');
    main.className = 'item-main';

    // Provider selector
    const pSel = document.createElement('select');
    pSel.className = 'f';
    pSel.style.maxWidth = '155px';
    let hasP = false;
    PROVIDER_PRESETS.forEach(p => {
      const o = document.createElement('option');
      o.value = p.name;
      o.textContent = p.name;
      o.title = p.tip;
      if (p.name.toLowerCase() === (r.provider_name || '').toLowerCase()) { o.selected = true; hasP = true; }
      pSel.appendChild(o);
    });
    if (!hasP && r.provider_name) {
      const o = document.createElement('option');
      o.value = r.provider_name;
      o.textContent = r.provider_name;
      o.selected = true;
      pSel.appendChild(o);
    }

    // Key selector from catalog
    const kSel = document.createElement('select');
    kSel.className = 'f';
    kSel.style.maxWidth = '240px';
    let keyMatched = false;
    KEY_CATALOG.forEach(k => {
      const o = document.createElement('option');
      o.value = k.api_key;
      o.textContent = k.label;
      o.title = k.consequence || '';
      if (k.api_key === (r.api_key || '').trim()) { o.selected = true; keyMatched = true; }
      kSel.appendChild(o);
    });
    if (!keyMatched) {
      const o = document.createElement('option');
      o.value = r.api_key || '';
      o.textContent = r.api_key ? `Key (${r.api_key.slice(0, 6)}...${r.api_key.slice(-4)})` : '— Select or Paste Key —';
      o.selected = true;
      kSel.insertBefore(o, kSel.firstChild);
    }

    // Endpoint input
    const epInp = document.createElement('input');
    epInp.className = 'f';
    epInp.value = r.api_endpoint_url || '';
    epInp.placeholder = 'Endpoint URL';
    epInp.title = 'API Endpoint URL';
    epInp.oninput = () => { r.api_endpoint_url = epInp.value; };

    // Edit Key / Extra Models toggle
    const editBtn = document.createElement('button');
    editBtn.type = 'button';
    editBtn.className = 'btn btn-icon';
    editBtn.textContent = '✎';
    editBtn.title = 'Edit raw API key string or extra model IDs inline';

    const rmBtn = document.createElement('button');
    rmBtn.type = 'button';
    rmBtn.className = 'btn btn-danger';
    rmBtn.textContent = '×';
    rmBtn.title = 'Remove provider row';
    rmBtn.onclick = () => { rows.splice(idx, 1); drawProviders(); };

    const sub = document.createElement('div');
    sub.className = 'inline-editor';
    const subRow = document.createElement('div');
    subRow.className = 'inline-editor-row';

    const rawKeyInp = document.createElement('input');
    rawKeyInp.className = 'f';
    rawKeyInp.value = r.api_key || '';
    rawKeyInp.placeholder = 'Raw API Key String';
    rawKeyInp.oninput = () => { r.api_key = rawKeyInp.value; };

    const extraInp = document.createElement('input');
    extraInp.className = 'f';
    extraInp.value = r.extra_model_ids || '';
    extraInp.placeholder = 'Extra model IDs (comma-separated)';
    extraInp.oninput = () => { r.extra_model_ids = extraInp.value; };

    subRow.appendChild(rawKeyInp);
    subRow.appendChild(extraInp);
    sub.appendChild(subRow);

    editBtn.onclick = () => {
      const open = !sub.classList.contains('open');
      sub.classList.toggle('open', open);
      editBtn.classList.toggle('active', open);
    };

    pSel.onchange = () => {
      r.provider_name = pSel.value;
      const preset = PROVIDER_PRESETS.find(p => p.name === pSel.value);
      if (preset) r.api_endpoint_url = preset.endpoint;
      const fk = KEY_CATALOG.find(k => k.provider_name.toLowerCase() === pSel.value.toLowerCase());
      if (fk) r.api_key = fk.api_key;
      drawProviders();
    };

    kSel.onchange = () => {
      r.api_key = kSel.value;
      rawKeyInp.value = kSel.value;
      const ci = KEY_CATALOG.find(k => k.api_key === kSel.value);
      if (ci) {
        r.provider_name = ci.provider_name;
        r.api_endpoint_url = ci.api_endpoint_url;
      }
      drawProviders();
    };

    main.appendChild(pSel);
    main.appendChild(kSel);
    main.appendChild(epInp);
    main.appendChild(editBtn);
    main.appendChild(rmBtn);
    row.appendChild(main);
    row.appendChild(sub);
    box.appendChild(row);
  });
}

// ============================================================================
// 3. TICKER MODELS & PER-MODEL INSTRUCTIONS
// ============================================================================
const MODEL_PROMPT_PRESETS = [
  { label: 'Inherit Mode Default (None)', val: '' },
  { label: 'First-Principles Analyst', val: 'Reason from first principles. State the core mechanism directly before elaborating.' },
  { label: 'Concise Executive Synthesizer', val: 'Use crisp, high-signal sentences. Eliminate filler, hedging, and preamble.' },
  { label: 'Code & Systems Architect', val: 'Prioritize concrete architecture, production code patterns, and exact technical trade-offs.' },
  { label: 'Counter-Hypothesis Critic', val: 'Test the premise rigorously and surface non-obvious edge cases or failure modes.' }
];

const quickModelSel = document.getElementById('quick-add-model-sel');
function populateQuickAddModelSelector() {
  const catList = getOptionsList('model_catalog_list', MODEL_CATALOG.map(m => ({ val: m.model_id, label: m.display_name, tip: m.consequence })));
  quickModelSel.innerHTML = '';
  catList.forEach(mc => {
    const o = document.createElement('option');
    o.value = mc.val;
    const inTicker = (S.ticker_response_models || []).some(m => m.model_id === mc.val);
    o.textContent = `${inTicker ? '✓ ' : ''}${mc.label} (${mc.val})`;
    const fullMeta = MODEL_CATALOG.find(x => x.model_id === mc.val);
    if (fullMeta && fullMeta.consequence) o.title = fullMeta.consequence;
    quickModelSel.appendChild(o);
  });
  document.getElementById('badge-models').textContent = String((S.ticker_response_models || []).length);
}

document.getElementById('quick-add-model-btn').onclick = () => {
  const id = quickModelSel.value;
  if (!id) return;
  const mc = MODEL_CATALOG.find(x => x.model_id === id) || { model_id: id, display_name: id.split('/').pop(), ticker_badge: id.slice(0, 4).toUpperCase(), model_creator: 'Custom', api_provider_route: 'NVIDIA', badge_color_hex: '#60A5FA' };
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

document.getElementById('add-custom-model-btn').onclick = () => {
  S.ticker_response_models.push({
    model_id: 'nvidia/nemotron-3-super-120b-a12b',
    display_name: 'New Model',
    ticker_badge: 'NEW',
    model_creator: 'NVIDIA',
    api_provider_route: 'NVIDIA',
    badge_color_hex: '#38BDF8',
    custom_temperature: '',
    custom_system_instruction: ''
  });
  drawTickerModels();
  drawAgents();
};

function drawTickerModels() {
  populateQuickAddModelSelector();

  // Global Base System Prompt
  const gBox = document.getElementById('global-model-prompt-box');
  gBox.innerHTML = '';
  gBox.appendChild(makePromptControl({
    listKey: 'global_system_prompts',
    label: 'Global Base System Prompt (All Ticker Models)',
    tip: 'Optional base system instruction prepended to every Ticker model before its per-model and mode instructions.',
    value: S.global_system_instruction || '',
    defaultPresets: [
      { label: 'None (Use Mode & Per-Model Prompts Only)', val: '' },
      { label: 'Direct & Zero-Filler Standard', val: 'Answer directly with high precision. Never include meta-commentary or filler.' },
      { label: 'First-Principles Technical Standard', val: 'Ground every claim in physical, mathematical, or architectural first principles.' }
    ],
    onChange: v => { S.global_system_instruction = v; }
  }));

  const box = document.getElementById('ticker-models-box');
  box.innerHTML = '';
  const modelOpts = getOptionsList('model_catalog_list', MODEL_CATALOG.map(m => ({ val: m.model_id, label: m.display_name })));

  (S.ticker_response_models || []).forEach((m, idx) => {
    const row = document.createElement('div');
    row.className = 'item-row';

    const main = document.createElement('div');
    main.className = 'item-main';

    // Color swatch
    const colInp = document.createElement('input');
    colInp.type = 'color';
    colInp.className = 'swatch';
    colInp.value = /^#[0-9a-fA-F]{6}$/.test(m.badge_color_hex || '') ? m.badge_color_hex : '#60A5FA';
    colInp.title = 'Badge Color';
    colInp.oninput = () => { m.badge_color_hex = colInp.value; };

    // Model selector (clean name, capability in tooltip)
    const idSel = document.createElement('select');
    idSel.className = 'f';
    idSel.style.minWidth = '175px';
    let matched = false;
    modelOpts.forEach(mc => {
      const o = document.createElement('option');
      o.value = mc.val;
      o.textContent = `${mc.label} (${mc.val})`;
      const fullMeta = MODEL_CATALOG.find(x => x.model_id === mc.val);
      if (fullMeta && fullMeta.consequence) o.title = fullMeta.consequence;
      if (mc.val === m.model_id) { o.selected = true; matched = true; }
      idSel.appendChild(o);
    });
    if (!matched && m.model_id) {
      const o = document.createElement('option');
      o.value = m.model_id;
      o.textContent = `${m.display_name || m.model_id} (${m.model_id})`;
      o.selected = true;
      idSel.insertBefore(o, idSel.firstChild);
    }

    // Display Name
    const lblInp = document.createElement('input');
    lblInp.className = 'f';
    lblInp.style.maxWidth = '145px';
    lblInp.value = m.display_name || '';
    lblInp.placeholder = 'Display Name';
    lblInp.title = 'Display Name in Ticker';
    lblInp.oninput = () => { m.display_name = lblInp.value; };

    // Badge
    const shInp = document.createElement('input');
    shInp.className = 'f';
    shInp.style.maxWidth = '64px';
    shInp.value = m.ticker_badge || '';
    shInp.placeholder = 'Badge';
    shInp.title = 'Short Badge';
    shInp.oninput = () => { m.ticker_badge = shInp.value; };

    // Provider Route
    const viaSel = document.createElement('select');
    viaSel.className = 'f';
    viaSel.style.maxWidth = '125px';
    viaSel.title = 'API Provider Route';
    const routeNames = [...new Set(['NVIDIA', 'OpenCode Zen', 'OpenRouter', 'xAI', 'OpenAI', 'Google Gemini', 'Kimi', 'MiniMax', 'Cohere', ...rows.map(r => r.provider_name)])];
    routeNames.forEach(rn => {
      if (!rn) return;
      const o = document.createElement('option');
      o.value = rn;
      o.textContent = rn;
      if (rn.toLowerCase() === (m.api_provider_route || 'NVIDIA').toLowerCase()) o.selected = true;
      viaSel.appendChild(o);
    });
    viaSel.onchange = () => { m.api_provider_route = viaSel.value; };

    // Temperature
    const tmpSel = document.createElement('select');
    tmpSel.className = 'f';
    tmpSel.style.maxWidth = '95px';
    tmpSel.title = 'Sampling Temperature';
    [
      { val: '', label: 'Default' },
      { val: '0', label: 'Temp 0.0' },
      { val: '0.2', label: 'Temp 0.2' },
      { val: '0.4', label: 'Temp 0.4' },
      { val: '0.7', label: 'Temp 0.7' },
      { val: '1.0', label: 'Temp 1.0' }
    ].forEach(to => {
      const o = document.createElement('option');
      o.value = to.val;
      o.textContent = to.label;
      if (String(m.custom_temperature ?? '') === to.val) o.selected = true;
      tmpSel.appendChild(o);
    });
    tmpSel.onchange = () => { m.custom_temperature = tmpSel.value === '' ? '' : Number(tmpSel.value); };

    // Inline Editor Toggle (Model ID write-in + Per-Model System Instruction)
    const promptBtn = document.createElement('button');
    promptBtn.type = 'button';
    promptBtn.className = 'btn btn-icon' + (m.custom_system_instruction ? ' active' : '');
    promptBtn.textContent = '✎ Prompt';
    promptBtn.title = 'Customize Model ID, options list, or per-model system instruction';

    const rmBtn = document.createElement('button');
    rmBtn.type = 'button';
    rmBtn.className = 'btn btn-danger';
    rmBtn.textContent = '×';
    rmBtn.title = 'Remove model from Ticker';
    rmBtn.onclick = () => {
      S.ticker_response_models.splice(idx, 1);
      drawTickerModels();
      drawAgents();
    };

    const drawer = document.createElement('div');
    drawer.className = 'inline-editor' + (m.custom_system_instruction ? ' open' : '');

    // Row 1 inside drawer: Custom Model ID write-in & catalog list management
    const idEditRow = document.createElement('div');
    idEditRow.className = 'inline-editor-row';
    const rawIdInp = document.createElement('input');
    rawIdInp.className = 'f';
    rawIdInp.value = m.model_id || '';
    rawIdInp.placeholder = 'Exact API Model ID (e.g. nvidia/nemotron-3-super-120b-a12b)';
    rawIdInp.oninput = () => { m.model_id = rawIdInp.value.trim(); };

    const rawTempInp = document.createElement('input');
    rawTempInp.className = 'f';
    rawTempInp.style.maxWidth = '110px';
    rawTempInp.value = m.custom_temperature ?? '';
    rawTempInp.placeholder = 'Custom Temp';
    rawTempInp.oninput = () => { m.custom_temperature = rawTempInp.value === '' ? '' : Number(rawTempInp.value); };

    const saveCatBtn = document.createElement('button');
    saveCatBtn.type = 'button';
    saveCatBtn.className = 'btn';
    saveCatBtn.textContent = '+ Save ID to List';
    saveCatBtn.onclick = () => {
      const nid = rawIdInp.value.trim();
      if (!nid) return;
      const nlbl = lblInp.value.trim() || nid;
      const list = getOptionsList('model_catalog_list', MODEL_CATALOG.map(x => ({ val: x.model_id, label: x.display_name })));
      const ex = list.findIndex(x => x.val === nid);
      if (ex >= 0) list[ex].label = nlbl;
      else list.push({ val: nid, label: nlbl });
      m.model_id = nid;
      drawTickerModels();
    };

    idEditRow.appendChild(rawIdInp);
    idEditRow.appendChild(rawTempInp);
    idEditRow.appendChild(saveCatBtn);
    drawer.appendChild(idEditRow);

    // Row 2 inside drawer: Per-Model System Prompt Preset Selector + Textarea
    const sysRow = document.createElement('div');
    sysRow.className = 'inline-editor-row';
    const sysSel = document.createElement('select');
    sysSel.className = 'f';
    const sysPresets = getOptionsList('per_model_prompts', MODEL_PROMPT_PRESETS);
    sysPresets.forEach((p, pi) => {
      const o = document.createElement('option');
      o.value = String(pi);
      o.textContent = `Prompt Preset: ${p.label}`;
      if (p.val === (m.custom_system_instruction || '')) o.selected = true;
      sysSel.appendChild(o);
    });

    const sysInp = document.createElement('input');
    sysInp.className = 'f';
    sysInp.value = m.custom_system_instruction || '';
    sysInp.placeholder = `Custom system instruction for ${m.display_name || m.model_id} (optional)`;
    sysInp.oninput = () => {
      m.custom_system_instruction = sysInp.value;
      promptBtn.classList.toggle('active', Boolean(m.custom_system_instruction));
    };

    const addSysPresetBtn = document.createElement('button');
    addSysPresetBtn.type = 'button';
    addSysPresetBtn.className = 'btn';
    addSysPresetBtn.textContent = '+ Save Prompt';
    addSysPresetBtn.onclick = () => {
      const v = sysInp.value.trim();
      if (!v) return;
      sysPresets.push({ label: v.slice(0, 32), val: v });
      drawTickerModels();
    };

    sysSel.onchange = () => {
      const chosen = sysPresets[Number(sysSel.value)];
      if (chosen) {
        sysInp.value = chosen.val;
        m.custom_system_instruction = chosen.val;
        promptBtn.classList.toggle('active', Boolean(m.custom_system_instruction));
      }
    };

    sysRow.appendChild(sysSel);
    sysRow.appendChild(sysInp);
    sysRow.appendChild(addSysPresetBtn);
    drawer.appendChild(sysRow);

    promptBtn.onclick = () => {
      const open = !drawer.classList.contains('open');
      drawer.classList.toggle('open', open);
      promptBtn.classList.toggle('active', open || Boolean(m.custom_system_instruction));
    };

    idSel.onchange = () => {
      m.model_id = idSel.value;
      rawIdInp.value = idSel.value;
      const mc = MODEL_CATALOG.find(x => x.model_id === idSel.value);
      if (mc) {
        m.display_name = mc.display_name;
        m.ticker_badge = mc.ticker_badge;
        m.model_creator = mc.model_creator;
        m.api_provider_route = mc.api_provider_route;
        m.badge_color_hex = mc.badge_color_hex;
      }
      drawTickerModels();
      drawAgents();
    };

    main.appendChild(colInp);
    main.appendChild(idSel);
    main.appendChild(lblInp);
    main.appendChild(shInp);
    main.appendChild(viaSel);
    main.appendChild(tmpSel);
    main.appendChild(promptBtn);
    main.appendChild(rmBtn);

    row.appendChild(main);
    row.appendChild(drawer);
    box.appendChild(row);
  });
}

// ============================================================================
// 4. CONSENSUS & SMART GEN AGENTS (MODELS, LIMITS & ALL 6 INSTRUCTIONS)
// ============================================================================
function allSelectableJudgeModels() {
  const map = new Map();
  MODEL_CATALOG.forEach(m => map.set(m.model_id, `${m.display_name} (${m.model_id})`));
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

  // 1. Primary Judge Model
  box.appendChild(makeEditableSelectRow({
    listKey: 'judge_models',
    label: 'Primary Judge Model',
    tip: 'Primary AI model that evaluates Ticker responses for Consensus and Smart Gen.',
    value: csa.primary_judge_model_id,
    isNumber: false,
    defaultOpts: judgeOptions,
    onChange: v => { csa.primary_judge_model_id = v; }
  }));

  // 2. Fallback Judge Chain
  const chainRow = document.createElement('div');
  chainRow.className = 'pref-row';
  const cLeft = document.createElement('div');
  cLeft.className = 'lbl-wrap';
  cLeft.innerHTML = `<span class="lbl-text">Fallback Judge Chain</span><span class="tip" data-tip="Ordered backup models tried if Primary Judge times out or returns invalid JSON.">i</span>`;
  const cRight = document.createElement('div');
  cRight.style.cssText = 'display:flex;flex-direction:column;gap:6px';

  const chips = document.createElement('div');
  chips.className = 'chip-list';
  (csa.fallback_judge_model_ids || []).forEach((mid, idx) => {
    const ch = document.createElement('span');
    ch.className = 'chip';
    const mc = MODEL_CATALOG.find(x => x.model_id === mid);
    ch.innerHTML = `<span>${idx + 1}. ${mc ? mc.display_name : mid}</span>`;
    if (idx > 0) {
      const up = document.createElement('button');
      up.type = 'button';
      up.textContent = '↑';
      up.onclick = () => {
        const t = csa.fallback_judge_model_ids[idx - 1];
        csa.fallback_judge_model_ids[idx - 1] = csa.fallback_judge_model_ids[idx];
        csa.fallback_judge_model_ids[idx] = t;
        drawAgents();
      };
      ch.appendChild(up);
    }
    const rm = document.createElement('button');
    rm.type = 'button';
    rm.textContent = '×';
    rm.onclick = () => { csa.fallback_judge_model_ids.splice(idx, 1); drawAgents(); };
    ch.appendChild(rm);
    chips.appendChild(ch);
  });

  const addBar = document.createElement('div');
  addBar.className = 'ctrl-bar';
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
  addBtn.textContent = '+ Add Backup';
  addBtn.onclick = () => {
    if (!csa.fallback_judge_model_ids.includes(addSel.value)) {
      csa.fallback_judge_model_ids.push(addSel.value);
      drawAgents();
    }
  };
  addBar.appendChild(addSel);
  addBar.appendChild(addBtn);
  cRight.appendChild(chips);
  cRight.appendChild(addBar);
  chainRow.appendChild(cLeft);
  chainRow.appendChild(cRight);
  box.appendChild(chainRow);

  // 3. Judge Limits
  box.appendChild(makeEditableSelectRow({
    listKey: 'agent_input_chars',
    label: 'Input Chars per Model Response',
    tip: 'Max characters from each Ticker response sent to Judge Agents.',
    value: csa.agent_input_max_chars_per_model_response,
    isNumber: true,
    defaultOpts: [
      { val: 1200, label: '1,200 chars' },
      { val: 2200, label: '2,200 chars' },
      { val: 4000, label: '4,000 chars' },
      { val: 8000, label: '8,000 chars' }
    ],
    onChange: v => { csa.agent_input_max_chars_per_model_response = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'primary_judge_tokens',
    label: 'Primary Judge Max Tokens',
    tip: 'Max output token budget for Primary Judge JSON response.',
    value: csa.primary_judge_max_output_tokens,
    isNumber: true,
    defaultOpts: [
      { val: 1500, label: '1,500 tokens' },
      { val: 2500, label: '2,500 tokens' },
      { val: 4000, label: '4,000 tokens' }
    ],
    onChange: v => { csa.primary_judge_max_output_tokens = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'fallback_judge_tokens',
    label: 'Fallback Judge Max Tokens',
    tip: 'Token budget (including <think>) when failing over to a backup reasoning judge.',
    value: csa.fallback_judge_max_output_and_thinking_tokens,
    isNumber: true,
    defaultOpts: [
      { val: 4000, label: '4,000 tokens' },
      { val: 6000, label: '6,000 tokens' },
      { val: 9000, label: '9,000 tokens' },
      { val: 12000, label: '12,000 tokens' }
    ],
    onChange: v => { csa.fallback_judge_max_output_and_thinking_tokens = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'judge_timeout',
    label: 'Judge Timeout',
    tip: 'Seconds to wait before failing over to the next backup judge.',
    value: csa.judge_model_timeout_seconds,
    isNumber: true,
    defaultOpts: [
      { val: 45, label: '45s' },
      { val: 75, label: '75s' },
      { val: 110, label: '110s' },
      { val: 180, label: '180s' }
    ],
    onChange: v => { csa.judge_model_timeout_seconds = Number(v); }
  }));

  // 4. All 6 Agent Instructions & JSON Format Schemas
  box.appendChild(makePromptControl({
    listKey: 'consensus_summary_prompts',
    label: 'Consensus Summary & Ratio Instruction',
    tip: 'System instruction for Judge Agent #1 (Consensus Agent.md): derives each response\'s minimal actionable sentiment, groups duplicates, and elects the democratic Consensus Summary verbatim.',
    value: csa.consensus_summary_and_ratio_instruction,
    defaultPresets: [
      { label: 'Consensus Agent.md Verbatim Standard', val: DEFAULT_AGENT_PROMPT },
      { label: 'Strict Single-Sentence Sentiment Grouping', val: 'Derive the core actionable sentiment of each response in one plain sentence. Group responses with identical sentiment and return the majority sentiment verbatim as consensus_summary.' }
    ],
    onChange: v => { csa.consensus_summary_and_ratio_instruction = v; }
  }));

  box.appendChild(makePromptControl({
    listKey: 'consensus_format_prompts',
    label: 'Consensus JSON Output Schema (AGENT_FORMAT)',
    tip: 'JSON output format instruction appended to Consensus Judge #1.',
    value: csa.consensus_json_format_instruction || DEFAULT_AGENT_FORMAT,
    defaultPresets: [
      { label: 'Standard Consensus JSON Schema', val: DEFAULT_AGENT_FORMAT }
    ],
    onChange: v => { csa.consensus_json_format_instruction = v; }
  }));

  box.appendChild(makePromptControl({
    listKey: 'logical_chain_prompts',
    label: 'Logical Chain Length Instruction',
    tip: 'System instruction for Judge Agent #2: counts explicit and implicit logical chains in each response.',
    value: csa.logical_chain_length_instruction,
    defaultPresets: [
      { label: 'Consensus Agent.md Logical Chain Standard', val: DEFAULT_CHAIN_PROMPT }
    ],
    onChange: v => { csa.logical_chain_length_instruction = v; }
  }));

  box.appendChild(makePromptControl({
    listKey: 'logical_chain_format_prompts',
    label: 'Logical Chain JSON Schema (CHAIN_FORMAT)',
    tip: 'JSON output format instruction appended to Logical Chain Judge #2.',
    value: csa.logical_chain_json_format_instruction || DEFAULT_CHAIN_FORMAT,
    defaultPresets: [
      { label: 'Standard Logical Chain JSON Schema', val: DEFAULT_CHAIN_FORMAT }
    ],
    onChange: v => { csa.logical_chain_json_format_instruction = v; }
  }));

  box.appendChild(makePromptControl({
    listKey: 'smartgen_extraction_prompts',
    label: 'Smart Gen Extraction Instruction',
    tip: 'System instruction for autonomous Smart Gen card creation and updates from conversations.',
    value: csa.smartgen_task_extraction_instruction,
    defaultPresets: [
      { label: 'PRD Smart Gen Extraction Standard', val: DEFAULT_SMARTGEN_PROMPT }
    ],
    onChange: v => { csa.smartgen_task_extraction_instruction = v; }
  }));

  box.appendChild(makePromptControl({
    listKey: 'smartgen_format_prompts',
    label: 'Smart Gen JSON Schema (SMARTGEN_FORMAT)',
    tip: 'JSON output format instruction appended to the Smart Gen Agent.',
    value: csa.smartgen_json_format_instruction || DEFAULT_SMARTGEN_FORMAT,
    defaultPresets: [
      { label: 'Standard Smart Gen JSON Schema', val: DEFAULT_SMARTGEN_FORMAT }
    ],
    onChange: v => { csa.smartgen_json_format_instruction = v; }
  }));
}

// ============================================================================
// 5. PROMPT MODES & SEARCH
// ============================================================================
let activeModeTab = 'chat';
document.querySelectorAll('#mode-tabs .subtab').forEach(btn => {
  btn.onclick = () => {
    activeModeTab = btn.dataset.mode;
    document.querySelectorAll('#mode-tabs .subtab').forEach(b => b.classList.toggle('active', b === btn));
    drawModes();
  };
});

function drawModes() {
  const box = document.getElementById('modes-box');
  box.innerHTML = '';
  const pmc = S.prompt_modes_configuration;
  const mk = activeModeTab;
  const m = pmc[mk];

  box.appendChild(makePromptControl({
    listKey: `mode_prompt_${mk}`,
    label: `${mk.charAt(0).toUpperCase() + mk.slice(1)} Mode System Instruction`,
    tip: `System instruction sent to all Ticker models when composer is in ${mk.toUpperCase()} mode.`,
    value: m.response_style_instruction,
    defaultPresets: [
      { label: `${mk.charAt(0).toUpperCase() + mk.slice(1)} Standard`, val: m.response_style_instruction },
      { label: 'Ultra-Concise Direct Answer', val: 'Answer in 2–4 direct sentences with zero preamble or filler.' },
      { label: 'Step-by-Step Technical Breakdown', val: 'Provide a direct executive answer first, followed by numbered technical steps and trade-offs.' }
    ],
    onChange: v => { m.response_style_instruction = v; }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: `mode_tokens_${mk}`,
    label: 'Max Output Tokens',
    tip: 'Maximum response length in tokens for this mode.',
    value: m.max_response_output_tokens,
    isNumber: true,
    defaultOpts: [
      { val: 600, label: '600 tokens' },
      { val: 900, label: '900 tokens' },
      { val: 1200, label: '1,200 tokens' },
      { val: 2400, label: '2,400 tokens' },
      { val: 4000, label: '4,000 tokens' },
      { val: 6000, label: '6,000 tokens' }
    ],
    onChange: v => { m.max_response_output_tokens = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: `mode_timeout_${mk}`,
    label: 'Mode Deadline',
    tip: 'Overall timeout in seconds for models in this mode.',
    value: m.max_response_wait_timeout_seconds,
    isNumber: true,
    defaultOpts: [
      { val: 60, label: '60s' },
      { val: 100, label: '100s' },
      { val: 120, label: '120s' },
      { val: 180, label: '180s' },
      { val: 240, label: '240s' },
      { val: 300, label: '300s' }
    ],
    onChange: v => { m.max_response_wait_timeout_seconds = Number(v); }
  }));

  if (mk !== 'chat') {
    box.appendChild(makeEditableSelectRow({
      listKey: `mode_depth_${mk}`,
      label: 'Web Search Depth',
      tip: 'Tavily search depth (basic vs advanced).',
      value: m.web_search_depth,
      isNumber: false,
      defaultOpts: [
        { val: 'basic', label: 'Basic (Fast)' },
        { val: 'advanced', label: 'Advanced (Deep Extraction)' }
      ],
      onChange: v => { m.web_search_depth = v; }
    }));

    box.appendChild(makeEditableSelectRow({
      listKey: `mode_sources_${mk}`,
      label: 'Web Sources Count',
      tip: 'Number of cited web sources fetched per query.',
      value: m.web_sources_fetched_count,
      isNumber: true,
      defaultOpts: [
        { val: 3, label: '3 sources' },
        { val: 5, label: '5 sources' },
        { val: 8, label: '8 sources' },
        { val: 12, label: '12 sources' },
        { val: 15, label: '15 sources' }
      ],
      onChange: v => { m.web_sources_fetched_count = Number(v); }
    }));

    box.appendChild(makeEditableSelectRow({
      listKey: `mode_chars_${mk}`,
      label: 'Max Chars per Source',
      tip: 'Maximum excerpt characters passed per cited source.',
      value: m.max_chars_per_web_source_excerpt,
      isNumber: true,
      defaultOpts: [
        { val: 600, label: '600 chars' },
        { val: 1200, label: '1,200 chars' },
        { val: 2400, label: '2,400 chars' },
        { val: 4000, label: '4,000 chars' }
      ],
      onChange: v => { m.max_chars_per_web_source_excerpt = Number(v); }
    }));
  }
}

// ============================================================================
// 6. EXECUTION & LIMITS
// ============================================================================
function drawLimits() {
  const box = document.getElementById('limits-box');
  box.innerHTML = '';
  const mel = S.model_execution_and_stream_limits;

  box.appendChild(makeEditableSelectRow({
    listKey: 'default_temp',
    label: 'Default Temperature',
    tip: 'Default sampling temperature for models without a custom override.',
    value: mel.default_model_temperature,
    isNumber: true,
    defaultOpts: [
      { val: 0.0, label: '0.0 (Deterministic)' },
      { val: 0.2, label: '0.2 (High Precision)' },
      { val: 0.4, label: '0.4 (Balanced)' },
      { val: 0.7, label: '0.7 (Creative)' },
      { val: 1.0, label: '1.0 (Max Variety)' }
    ],
    onChange: v => { mel.default_model_temperature = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'thinking_tokens',
    label: 'Internal Reasoning (<think>) Budget',
    tip: 'Extra token budget for hidden chain-of-thought before visible output.',
    value: mel.max_internal_thinking_tokens_per_model,
    isNumber: true,
    defaultOpts: [
      { val: 1000, label: '1,000 tokens' },
      { val: 2000, label: '2,000 tokens' },
      { val: 4000, label: '4,000 tokens' },
      { val: 8000, label: '8,000 tokens' }
    ],
    onChange: v => { mel.max_internal_thinking_tokens_per_model = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'reply_tokens',
    label: 'Follow-Up Reply Max Tokens',
    tip: 'Max output tokens for single-model thread replies.',
    value: mel.max_followup_reply_output_tokens,
    isNumber: true,
    defaultOpts: [
      { val: 800, label: '800 tokens' },
      { val: 1400, label: '1,400 tokens' },
      { val: 2400, label: '2,400 tokens' },
      { val: 4000, label: '4,000 tokens' }
    ],
    onChange: v => { mel.max_followup_reply_output_tokens = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'stream_silence',
    label: 'Stream Stall Cutoff',
    tip: 'Seconds of stream silence before falling back to a single request.',
    value: mel.max_stream_silence_stall_timeout_seconds,
    isNumber: true,
    defaultOpts: [
      { val: 20, label: '20s' },
      { val: 30, label: '30s' },
      { val: 45, label: '45s' },
      { val: 60, label: '60s' },
      { val: 90, label: '90s' }
    ],
    onChange: v => { mel.max_stream_silence_stall_timeout_seconds = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'fallback_timeout',
    label: 'Non-Streaming Timeout',
    tip: 'Timeout in seconds for non-streaming fallback completion calls.',
    value: mel.non_streaming_fallback_timeout_seconds,
    isNumber: true,
    defaultOpts: [
      { val: 60, label: '60s' },
      { val: 120, label: '120s' },
      { val: 150, label: '150s' },
      { val: 240, label: '240s' }
    ],
    onChange: v => { mel.non_streaming_fallback_timeout_seconds = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'retry_attempts',
    label: 'Max Retry Attempts',
    tip: 'Attempts across round-robin API keys when a request fails.',
    value: mel.failed_request_max_retry_attempts,
    isNumber: true,
    defaultOpts: [
      { val: 1, label: '1 attempt' },
      { val: 2, label: '2 attempts' },
      { val: 3, label: '3 attempts' },
      { val: 4, label: '4 attempts' }
    ],
    onChange: v => { mel.failed_request_max_retry_attempts = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'retry_delay',
    label: 'Retry Cooldown Delay',
    tip: 'Pause in seconds between failed request retries.',
    value: mel.retry_wait_delay_seconds,
    isNumber: true,
    defaultOpts: [
      { val: 0.5, label: '0.5s' },
      { val: 1.5, label: '1.5s' },
      { val: 3.0, label: '3.0s' },
      { val: 5.0, label: '5.0s' }
    ],
    onChange: v => { mel.retry_wait_delay_seconds = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'search_timeout',
    label: 'Web Search Timeout',
    tip: 'Timeout in seconds for Tavily web search requests.',
    value: mel.web_search_request_timeout_seconds,
    isNumber: true,
    defaultOpts: [
      { val: 15, label: '15s' },
      { val: 30, label: '30s' },
      { val: 40, label: '40s' },
      { val: 60, label: '60s' }
    ],
    onChange: v => { mel.web_search_request_timeout_seconds = Number(v); }
  }));
}

// ============================================================================
// 7. BROWSER & STORAGE
// ============================================================================
function drawBrowserAndStorage() {
  const box = document.getElementById('browser-box');
  box.innerHTML = '';
  const bsl = S.in_app_browser_and_storage_limits;

  box.appendChild(makeEditableSelectRow({
    listKey: 'browser_depth',
    label: 'Browser Search Depth',
    tip: 'Tavily search depth for In-App Browser search queries.',
    value: bsl.browser_fallback_search_depth,
    isNumber: false,
    defaultOpts: [
      { val: 'basic', label: 'Basic' },
      { val: 'advanced', label: 'Advanced' }
    ],
    onChange: v => { bsl.browser_fallback_search_depth = v; }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'browser_results',
    label: 'Browser Results per Page',
    tip: 'Number of search results shown per query in the In-App Browser.',
    value: bsl.browser_fallback_search_max_results,
    isNumber: true,
    defaultOpts: [
      { val: 5, label: '5 results' },
      { val: 10, label: '10 results' },
      { val: 15, label: '15 results' },
      { val: 20, label: '20 results' }
    ],
    onChange: v => { bsl.browser_fallback_search_max_results = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'browser_timeout',
    label: 'Browser Search Timeout',
    tip: 'Timeout in seconds for In-App Browser search.',
    value: bsl.browser_fallback_search_timeout_seconds,
    isNumber: true,
    defaultOpts: [
      { val: 15, label: '15s' },
      { val: 30, label: '30s' },
      { val: 45, label: '45s' }
    ],
    onChange: v => { bsl.browser_fallback_search_timeout_seconds = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'max_attachments',
    label: 'Max Attached Files per Prompt',
    tip: 'Maximum files attached to a single prompt.',
    value: bsl.max_attached_files_per_prompt,
    isNumber: true,
    defaultOpts: [
      { val: 4, label: '4 files' },
      { val: 8, label: '8 files' },
      { val: 12, label: '12 files' },
      { val: 20, label: '20 files' }
    ],
    onChange: v => { bsl.max_attached_files_per_prompt = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'max_history',
    label: 'Saved History Sessions Limit',
    tip: 'Maximum past sessions kept in history.json.',
    value: bsl.max_saved_history_sessions,
    isNumber: true,
    defaultOpts: [
      { val: 50, label: '50 sessions' },
      { val: 100, label: '100 sessions' },
      { val: 200, label: '200 sessions' },
      { val: 500, label: '500 sessions' },
      { val: 1000, label: '1,000 sessions' }
    ],
    onChange: v => { bsl.max_saved_history_sessions = Number(v); }
  }));

  box.appendChild(makeEditableSelectRow({
    listKey: 'max_smartgen',
    label: 'Saved Smart Gen Items Limit',
    tip: 'Maximum Smart Gen items retained in smartgen_cards.json.',
    value: bsl.max_saved_smartgen_items,
    isNumber: true,
    defaultOpts: [
      { val: 50, label: '50 items' },
      { val: 100, label: '100 items' },
      { val: 250, label: '250 items' },
      { val: 500, label: '500 items' }
    ],
    onChange: v => { bsl.max_saved_smartgen_items = Number(v); }
  }));
}

// ============================================================================
// 8. MEDIA & THEMES
// ============================================================================
function drawMarketAndThemes() {
  const mBox = document.getElementById('market-box');
  mBox.innerHTML = '';
  const dm = S.discover_market_image_generation;

  const orderStr = (dm.image_provider_priority_order || ['Cloudflare', 'NVIDIA', 'fal']).join(',');
  mBox.appendChild(makeEditableSelectRow({
    listKey: 'img_priority',
    label: 'Image Provider Priority Order',
    tip: 'Failover order when generating images in Discover Market.',
    value: orderStr,
    isNumber: false,
    defaultOpts: [
      { val: 'Cloudflare,NVIDIA,fal', label: 'Cloudflare → NVIDIA → fal.ai' },
      { val: 'NVIDIA,Cloudflare,fal', label: 'NVIDIA → Cloudflare → fal.ai' },
      { val: 'fal,Cloudflare,NVIDIA', label: 'fal.ai → Cloudflare → NVIDIA' },
      { val: 'Cloudflare,NVIDIA', label: 'Cloudflare → NVIDIA (Free Only)' }
    ],
    onChange: v => { dm.image_provider_priority_order = String(v).split(',').map(s => s.trim()).filter(Boolean); }
  }));

  mBox.appendChild(makeEditableSelectRow({
    listKey: 'cf_flux_model',
    label: 'Cloudflare Image Model',
    tip: 'FLUX model executed on Cloudflare Workers AI.',
    value: dm.cloudflare_flux_model_id,
    isNumber: false,
    defaultOpts: [
      { val: '@cf/black-forest-labs/flux-2-klein-4b', label: 'FLUX.2 Klein 4B' },
      { val: '@cf/black-forest-labs/flux-2-dev', label: 'FLUX.2 Dev' },
      { val: '@cf/black-forest-labs/flux-1-schnell', label: 'FLUX.1 Schnell' }
    ],
    onChange: v => { dm.cloudflare_flux_model_id = v; }
  }));

  mBox.appendChild(makeEditableSelectRow({
    listKey: 'nv_flux_model',
    label: 'NVIDIA Image Model',
    tip: 'FLUX model executed via NVIDIA API keys.',
    value: dm.nvidia_flux_model_id,
    isNumber: false,
    defaultOpts: [
      { val: 'black-forest-labs/flux.1-dev', label: 'FLUX.1 Dev' }
    ],
    onChange: v => { dm.nvidia_flux_model_id = v; }
  }));

  mBox.appendChild(makeEditableSelectRow({
    listKey: 'fal_img_model',
    label: 'fal.ai Image Model',
    tip: 'High-resolution model executed on fal.ai.',
    value: dm.fal_image_model_id,
    isNumber: false,
    defaultOpts: [
      { val: 'xai/grok-imagine-image/v2.0/text-to-image', label: 'Grok Imagine v2.0 (2K)' }
    ],
    onChange: v => { dm.fal_image_model_id = v; }
  }));

  mBox.appendChild(makeEditableSelectRow({
    listKey: 'img_batch_count',
    label: 'Default Images per Prompt',
    tip: 'Batch count generated per image prompt.',
    value: dm.default_images_per_prompt_count,
    isNumber: true,
    defaultOpts: [
      { val: 1, label: '1 image' },
      { val: 2, label: '2 images' },
      { val: 4, label: '4 images' },
      { val: 6, label: '6 images' },
      { val: 8, label: '8 images' }
    ],
    onChange: v => { dm.default_images_per_prompt_count = Number(v); }
  }));

  mBox.appendChild(makeEditableSelectRow({
    listKey: 'img_aspect',
    label: 'Default Aspect Ratio',
    tip: 'Default aspect ratio for generated images.',
    value: dm.default_image_aspect_ratio,
    isNumber: false,
    defaultOpts: [
      { val: '9:16', label: '9:16 (Portrait)' },
      { val: '3:4', label: '3:4' },
      { val: '1:1', label: '1:1 (Square)' },
      { val: '4:3', label: '4:3' },
      { val: '16:9', label: '16:9 (Widescreen)' }
    ],
    onChange: v => { dm.default_image_aspect_ratio = v; }
  }));

  const tBox = document.getElementById('themes-box');
  tBox.innerHTML = '';
  const lts = S.live_wallpaper_themes_and_store;

  tBox.appendChild(makeEditableSelectRow({
    listKey: 'theme_worker_url',
    label: 'Theme Catalog Worker URL',
    tip: 'Cloudflare R2 Worker serving live wallpapers and audio packs.',
    value: lts.theme_catalog_worker_url,
    isNumber: false,
    defaultOpts: [
      { val: 'https://collider-themes.ebridavid.workers.dev/', label: 'collider-themes.ebridavid.workers.dev' }
    ],
    onChange: v => { lts.theme_catalog_worker_url = v; }
  }));

  tBox.appendChild(makeEditableSelectRow({
    listKey: 'theme_refresh_sec',
    label: 'Catalog Auto-Refresh Interval',
    tip: 'Seconds between background theme catalog checks.',
    value: lts.theme_catalog_auto_refresh_seconds,
    isNumber: true,
    defaultOpts: [
      { val: 300, label: '300s (5m)' },
      { val: 600, label: '600s (10m)' },
      { val: 1800, label: '1800s (30m)' },
      { val: 3600, label: '3600s (1h)' }
    ],
    onChange: v => { lts.theme_catalog_auto_refresh_seconds = Number(v); }
  }));

  tBox.appendChild(makeEditableSelectRow({
    listKey: 'theme_pack_price',
    label: 'Theme Pack Display Price',
    tip: 'Display price badge for Premium Theme Packs.',
    value: lts.premium_theme_pack_display_price,
    isNumber: false,
    defaultOpts: [
      { val: '$1.99', label: '$1.99' },
      { val: '$2.99', label: '$2.99' },
      { val: '$4.99', label: '$4.99' },
      { val: '$6.99', label: '$6.99' },
      { val: '$9.99', label: '$9.99' }
    ],
    onChange: v => { lts.premium_theme_pack_display_price = v; }
  }));

  tBox.appendChild(makeEditableSelectRow({
    listKey: 'theme_tracks_count',
    label: 'Tracks per Theme Pack',
    tip: 'Number of ambient audio tracks bundled per wallpaper pack.',
    value: lts.music_tracks_per_theme_pack_count,
    isNumber: true,
    defaultOpts: [
      { val: 1, label: '1 track' },
      { val: 3, label: '3 tracks' },
      { val: 5, label: '5 tracks' },
      { val: 8, label: '8 tracks' },
      { val: 10, label: '10 tracks' }
    ],
    onChange: v => { lts.music_tracks_per_theme_pack_count = Number(v); }
  }));

  tBox.appendChild(makeEditableSelectRow({
    listKey: 'store_bypass',
    label: 'Developer Paywall Bypass',
    tip: 'Unlock all Premium Themes immediately on click without StoreKit checkout.',
    value: String(Boolean(lts.bypass_purchase_paywall_for_testing)),
    isNumber: false,
    defaultOpts: [
      { val: 'false', label: 'Off (Standard Paywall)' },
      { val: 'true', label: 'On (Bypass Enabled)' }
    ],
    onChange: v => { lts.bypass_purchase_paywall_for_testing = (String(v) === 'true'); }
  }));
}

// Initial Render + Live Fetch Sync
function renderAll() {
  drawHost();
  drawProviders();
  drawTickerModels();
  drawAgents();
  drawModes();
  drawLimits();
  drawBrowserAndStorage();
  drawMarketAndThemes();
}
renderAll();

// Sync latest live config from /api/config/data if available
fetch('/api/config/data').then(r => r.ok ? r.json() : null).then(live => {
  if (!live || !live.settings) return;
  if (live.host) hostPort = String(live.host);
  if (Array.isArray(live.providers) && live.providers.length) {
    rows = live.providers.map(r => ({
      provider_name: r.provider_name || r.name || 'NVIDIA',
      api_endpoint_url: r.api_endpoint_url || r.endpoint || '',
      api_key: r.api_key || r.key || '',
      extra_model_ids: r.extra_model_ids !== undefined ? r.extra_model_ids : (r.models || '')
    }));
  }
  Object.keys(live.settings).forEach(k => {
    if (live.settings[k] !== undefined && live.settings[k] !== null) {
      if (typeof live.settings[k] === 'object' && !Array.isArray(live.settings[k]) && typeof S[k] === 'object') {
        Object.assign(S[k], live.settings[k]);
      } else {
        S[k] = live.settings[k];
      }
    }
  });
  renderAll();
}).catch(() => {});

let busy = false;
async function saveConfig(e) {
  if (e) e.preventDefault();
  if (busy) return;
  const payload = {
    host: hostPort,
    providers: rows,
    themes: S.live_wallpaper_themes_and_store.theme_catalog_worker_url,
    bypass: S.live_wallpaper_themes_and_store.bypass_purchase_paywall_for_testing,
    settings: S
  };
  if (window.pywebview && window.pywebview.api) {
    busy = true;
    try {
      await window.pywebview.api.launch(payload);
    } finally {
      busy = false;
    }
    return;
  }
  busy = true;
  const g = document.getElementById('go-btn');
  const sb = document.getElementById('side-save-btn');
  const pill = document.getElementById('save-pill');
  const prevText = g.textContent;
  g.textContent = 'Saving...';
  sb.textContent = 'Saving...';
  try {
    const r = await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (r.ok) {
      g.textContent = '✓ Saved & Applied Live';
      sb.textContent = '✓ Saved';
      pill.textContent = 'Saved to config & live app (' + new Date().toLocaleTimeString() + ')';
      pill.style.color = 'var(--green)';
    } else {
      g.textContent = 'Save Failed';
      sb.textContent = 'Save Failed';
      pill.textContent = 'Error saving config';
      pill.style.color = 'var(--red)';
    }
    setTimeout(() => {
      g.textContent = prevText;
      sb.textContent = 'Save Changes';
    }, 2200);
  } finally {
    busy = false;
  }
}

document.getElementById('f').onsubmit = saveConfig;
document.getElementById('side-save-btn').onclick = saveConfig;
</script>
</body>
</html>
"""


def ask(data_dir, initial):
    """Opens the launch window before the app when running as desktop pywebview."""
    import json
    import collider_config as ccfg
    try:
        import webview
    except ImportError:
        return initial.get("host"), initial.get("providers")

    result = {}

    class Api:
        def launch(self, payload):
            try:
                port = int(str(payload.get("host") or "").strip())
                if not (1024 <= port <= 65535):
                    return {"error": "bad port"}
            except ValueError:
                return {"error": "bad port"}
            result["host"] = port
            result["providers"] = payload.get("providers") or []
            result["settings"] = payload.get("settings") or {}
            win.destroy()
            return {"ok": True}

    html = (
        FORM.replace("WHERE", json.dumps(ccfg.path(data_dir)))
        .replace("INITIAL", json.dumps(initial))
    )
    win = webview.create_window("Collider — Preferences", html=html, js_api=Api(), width=1060, height=780)
    webview.start()
    return result.get("host"), result.get("providers"), result.get("settings")

# Collider — Master Product & Architectural Specification (v5.0 Master Edition)

> **Document Classification**: Authoritative Canonical Master Specification  
> **Status**: Active & Binding  
> **Supersedes**: `docs/COLLIDER_GENERAL_SPEC.md`, `docs/COLLIDER_MASTER_SPEC.md` (v4.0), `docs/COLLIDER_SPEC.md`, and all legacy briefs  
> **Design Authority**: Apple visionOS Spatial Design System Exclusively (Zero Custom Theming)  
> **Target Frameworks**: Universal Mobile, Spatial, & Web (Flutter Native Impeller, Apple visionOS Native Swift, CanvasKit Web Preview)  
> **Repository Locations**:  
> - Root: [`COLLIDER_MASTER_SPEC.md`](file:///c:/Users/D/Documents/collider_flutter/COLLIDER_MASTER_SPEC.md)  
> - Docs: [`docs/COLLIDER_MASTER_SPEC.md`](file:///c:/Users/D/Documents/collider_flutter/docs/COLLIDER_MASTER_SPEC.md)  
> - Companion Figma Mapping: [`docs/FIGMA_MAPPING_SPEC.md`](file:///c:/Users/D/Documents/collider_flutter/docs/FIGMA_MAPPING_SPEC.md)

---

## 1. Executive Summary & Core Philosophy

### 1.1 The Prime Directive: Reducing Cognitive Load
Collider provides a unified, transparent lens into multi-model artificial intelligence without forcing the user to context-switch across fragmented interfaces or grapple with model selection anxiety.
- **Conversation Stream $\equiv$ Response Ticker Stack**: The application does **NOT** contain a separate or duplicate chat screen. The floating model row ticker on Plane 2 **IS** the conversational interface. In its resting collapsed state, it delivers instantaneous, zero-tap comparison across all models. When tapped, each row expands into an inline accordion containing tailed speech bubbles, local model tools, and an isolated follow-up reply box.
- **Proactive Value Delivery**: The system computes and surfaces value before the user asks for it. Consensus synthesis is aggregated and displayed in-line before a manual comparison is requested. Tasks, deadlines, project structures, and code artifacts are autonomously identified and captured from conversation context into the Smart Gen suite.
- **Zero Friction**: No forced onboarding wizards, no interstitial configuration gates. The application opens directly into a living, responsive workspace.
- **Data Discipline & Signal-to-Noise**: Raw technical metrics, tokens-per-second, and verbose provider metadata are pruned unless actionable. Labels are clean, human, and conversational.

### 1.2 The Zero User Data Loss Law (Forever Invariant)
Nothing in the application may ever delete, clear, or discard unsubmitted user input.
- If a user is typing a prompt or message, opening an overlay, summoning a drawer, closing a pane, or switching categories must **NEVER** wipe the active draft.
- Anything created by the user can only be destroyed by an explicit action from the user (e.g., clear button or backspace). Unsubmitted text is cached in memory and restored automatically upon returning to the composer.

### 1.3 Thumb-Zone Ergonomics (Mid-Phone Height Rule)
Users must be able to navigate the application continuously and comfortably with one hand without repositioning their grip:
- All primary triggers, input bars, bottom dock icons, and drawer tab affordances must reside **below the mid-screen horizontal meridian**.
- Reaching above mid-phone height is restricted to passive reading (e.g., scrolling conversation history) or explicit modal dismissal.

### 1.4 The Emotional Core: Unobstructed Living Wallpaper & Negative Space Primacy (Plane 0)
The visual and emotional foundation of Collider is its living wallpaper layer:
- The wallpaper remains visible and continuous across all screen states, modals, and sub-drawers.
- All windows, sheets, ribbons, and modals are rendered as translucent optical frosted glass, allowing background movement and atmosphere to illuminate through.
- Background media consists of organic, breathing, endless atmospheric loops with zero jarring transitions or jerky ping-pong loops.
- **Negative Space Primacy (Forever Law)**: Negative space is the void, NOT space to be filled. The Living Wallpaper is the star of the product and must remain unobstructed across **65%–75%+** of the screen during resting states.
- Resting UI elements must be content-hugging and compact: half-width layout (`maxWidth: 240px–260px` on mobile; max `480px` on spatial/desktop), never full-width.

---

## 2. Canonical User Layout Segment (Authoritative Ground Truth)

The following directives represent the verbatim, authoritative user layout contract:

```markdown
- Consensus preview will be another row, pinned to the top or bottom of rows. it includes the score, then 1 line consensus summary, not truncated. clicking on it reveals the full map the consensus.html
- rows should not be ful width and should be in a window towards the bottom of the screen
- rows are a non-interactive surface (not draggable/repositionable) and carry no card chrome/border — no bordered container, since there is nothing left for a border to signal
- the model row stack is a scrollable ticker: max height 40% of screen height, max width equal to the width of the nav bar
- consensus lives only on this pinned row — it is not duplicated on any nav surface, bottom or side
- both history buttons allow you to clck on a specific conversation to load it, and to immediately send the user there (closing all open temporary panes as well) to its expanded view.
- bottom nav bar holds 3 icons: Compose (doubles as Home), Settings, Apps
- a second, contextual side nav bar reshapes based on the active work surface:
  - Smart Gen → Smart Gen side menu
  - Discover Market → category/nav panel, including search (search always lives on the side nav)
  - Theme Selector → quick switch between Premium Marketplace, Theme Gallery, and Music Collection
  - Web Browser → web settings panel
  - Files → category navigation
  - AI Chat → tabs for Local History, Global History, and Consensus; start-new-conversation; model category selection (swipeable left/right); model selection within category
- apps icon opens an Apps overlay: no visible canvas, blurred/dimmed background, summoned to the center. Displays ICONS (not buttons) for 7 destinations: Smart Gen, Discover Market, Theme Gallery, Premium Theme Marketplace, Files, Music Player, Browser. Clicking any icon opens that durable work surface, floating and centered, background blurred/dimmed. clickaway close + close icon to escape
- any nav interaction — bottom bar or side nav — closes all other open panes, temporary and durable alike, since menu and work surface never coexist
- composer can be summoned by swiping up on nav bar and has an indicator acknowledging its tucked view. an arrow. swiping down tucks it away again
- Expanded Conversation Accordion: Scrollable chat, Local(model) Files, local history icon with a small popup pane that opens up centered to a scrollable list of model-specific conversations with timestamp and a search button on top that searches within the conversation body and the title, click on message to get zoomed in view (also scrollable) with blurred background or dimmed and with action options along the bottom of the message and with no visible wndow and with faded eedges, browser icon for opeing that model's specific browser. one browser instance active at a time, even in background
- chat bubbles use a tailed shape, not a plain rounded rect
- max 9 rows
- settings holds functional options only — no cosmetic or preference toggles
- remember animation requirements
- remember exit requiremens for popup panes
- remember no full screen elements requirement
- remember only necessary sizing for elements (o oversized popup panes or other temporary elements)
- remember the background image is the star but the entire app and every window, submenu, element, font must be from the visionOS package.
```

---

## 3. Spatial Design System (Exclusive visionOS Authority)

### 3.1 The Exclusive visionOS Design Authority (Forever Law)
- **Apple visionOS is the ONLY design system and theme**: All visual components, materials, typography, button states, physics, and animations derive strictly and exclusively from official Apple visionOS component specifications or direct user overrides.
- **Prohibition of Custom Theming & Invented Physics**:
  - ZERO custom theming layers on top of visionOS.
  - ZERO pseudo-game animations, ZERO "celestial drift physics", and ZERO arbitrary non-standard easing curves.
  - All transitions follow genuine Apple visionOS spatial mechanics: spring-damped drawer ascension, optical glass refraction, 1px specular light highlights, and standard visionOS depth layering.
- **Permanent Ban on AIisms & Glitter Icons (Forever Law)**:
  - ZERO tolerance for glitter or sparkle icons (`Icons.auto_awesome*`, `Icons.stars`, magic wands), toy robot heads (`Icons.smart_toy*`), glowing brains (`Icons.psychology*`).
  - Pure deterministic engineering icons only: `Icons.balance_rounded`, `Icons.hub_rounded`, `Icons.inventory_2_rounded`, `Icons.terminal_rounded`, `Icons.tune_rounded`.
  - ZERO tolerance for marketing AI buzzwords ("Magic", "Cosmic", "AI Assistant"). Use pure functional engineering terms: "Artifacts", "Consensus", "Synthesis", "Models", "Sessions".
    - Struck on 2026-10-04 (not David's; added by the agent that wrote this rule on 2026-09-05): the ban on a breathing pulse while a model is answering, and the renaming of "Smart Gen" to "Workspaces". "Smart Gen" is David's own name for the feature and is never renamed.

### 3.2 Optical Glass Architecture (`VisionGlass`)
Every visual surface in Collider exists on a defined spatial depth plane:

| Depth Plane | Z-Elevation | Tint (`Color`) | Blur Sigma | Specular Border | Ambient Shadow |
|---|---|---|---|---|---|
| **Plane 0: Atmosphere** | `0.0` | Live Wallpaper / Canvas | None | None | None |
| **Plane 1: Base / Prompt** | `1.0` | `Color(0x18FFFFFF)` | `16.0` | `0.5px SpecularRim` | `Offset(0, 8), Blur 24, Opacity 0.18` |
| **Plane 2: Resting Windows** | `2.0` | `Color(0x1EFFFFFF)` | `24.0` | `0.5px SpecularRim` | `Offset(0, 12), Blur 32, Opacity 0.22` |
| **Plane 3: Elevated Flyouts** | `3.0` | `Color(0x24FFFFFF)` | `28.0` | `0.6px SpecularRim` | `Offset(0, 16), Blur 40, Opacity 0.28` |
| **Plane 4: Modals & Zoom** | `4.0` | `Color(0x28FFFFFF)` | `32.0` | `0.6px SpecularRim` | `Offset(0, 20), Blur 48, Opacity 0.32` |
| **Plane 5: Work Surfaces** | `5.0` | `Color(0x2CFFFFFF)` | `36.0` | `0.6px SpecularRim` | `Offset(0, 24), Blur 56, Opacity 0.36` |

### 3.3 Typography: Instrument Sans
- All textual elements use **Instrument Sans** (`GoogleFonts.instrumentSans`).
- Monospace typefaces are completely purged from user-facing screens.
- Optical weights range from `FontWeight.w400` (conversation body) to `FontWeight.w600` (model names, titles, headers).

### 3.4 Color Coding Discipline
- **Neutral Core**: Interfaces are composed of shades of optical white, subtle translucency, and pure monochromatic contrast.
- **Provider colour**: a model's card carries its provider's colour across the whole card, so cards are told apart at a glance (see Full-Surface Aesthetics).
  - Struck on 2026-10-03 on David's instruction (not his, no justification): the callout that restricted provider colour to a 3.5px left bar and a dot, with no coloured card backgrounds.

---

## 4. Screen Hierarchy & Interaction Architecture (The 6 Planes)

### 4.1 Spatial Plane Structure

```
┌────────────────────────────────────────────────────────┐
│ Plane 0: Living Wallpaper (Continuous, Unobstructed)   │
│                                                        │
│ [Plane 1: Floating Input Prompt (Tucked by default)]   │
│                                                        │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Plane 2: Floating Glass Rows Container             │ │
│ │ ┌────────────────────────────────────────────────┐ │ │
│ │ │ Pinned Consensus Row (Score + Summary + Map >) │ │ │
│ │ ├────────────────────────────────────────────────┤ │ │
│ │ │ Scrollable Model Accordion Pills (Max 9)       │ │ │
│ │ │  - GPT-5 Nano (Collapsed)                      │ │ │
│ │ │  - Gemini 3.6 Flash Lite (Expanded)            │ │ │
│ │ │    [Local Ribbon: Search, Files, History, etc] │ │ │
│ │ │    [Momentum Scroll Chat Stream]               │ │ │
│ │ │    [Inline Isolated Branch Composer]           │ │ │
│ │ └────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│         [▲ Swipe up for composer pull indicator]       │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Permanent Floating Glass Capsule Nav Bar (3 Icons) │ │
│ │              [Compose/Home]  [Settings]  [Apps]    │ │
│ └────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

### 4.2 Inseparable Ticker Dimensions & Non-Interactive Surface
- **Height Cap**: Strictly $\le 40\%$ of screen height. If responses exceed this height, internal momentum scrolling handles it; the container never expands past 40%.
- **Width Cap**: Strictly equal to the width of the bottom nav bar (`maxWidth: 240px–260px` on mobile; max `480px` on desktop/spatial). Content-hugging, NEVER full-width.
- **Non-Interactive Surface**: Model rows are a non-interactive surface (no dragging, no card reordering, non-repositionable). Drag-and-drop of model cards is permanently removed.
- **Zero Card Borders/Chrome**: Containers carry no outer border; there is nothing left for a border to signal.
- **The Summary Invariant**: *"Expansion is for depth, not completion. If the user must expand to get the answer, the summary failed."* Summaries scale down gracefully via `FittedBox(fit: BoxFit.scaleDown)` without ugly truncation ellipsis.
- **Tailed Speech Bubbles**: Chat bubbles inside expanded accordions use directional tail geometry (`_TailedBubble`), never plain rounded rectangles.
- **Faded Edge Masking**: Scrollable chat streams use vertical alpha gradient masking so message cards smoothly fade into the wallpaper at top and bottom edges.

### 4.3 Wallpaper Display & Full Thumbnail Representation (Forever Laws)
- **Unblurred Wallpaper During Theme Browsing (Forever Law)**:
  - When browsing or previewing wallpapers in the Theme Selector (`WindowlessThemeScroller`), the background living wallpaper must **NEVER** be blurred out by backdrop filters.
  - Backdrop blur is strictly bypassed (`sigmaX: 0, sigmaY: 0`), and the ambient dimming is limited to a subtle tint (`0.12` max) so the live wallpaper is 100% visible, sharp, and crisp.
- **Full Thumbnail & Icon Representation (Forever Law)**:
  - Every single thumbnail and icon in the application must fully represent itself within its viewport without being cropped into unrecognizable strips or blurry visual noise.
  - Wallpaper thumbnails in `WindowlessThemeScroller`, `WallpaperDrawer`, and `ThemeMarketplaceDetailView` are rendered in **portrait squircle cards** (aspect ratio ~`0.56` to `0.58`, matching native phone wallpaper dimensions: `width: 68, height: 116`).
  - All image rendering applies `FilterQuality.medium` and `alignment: Alignment.center` with `fit: BoxFit.cover`, ensuring that 100% of the subject matter is clearly and sharply recognizable.

---

## 5. Consensus Architecture & Isolated Sub-Threads

### 5.1 Consensus Eligibility Invariant
Consensus is strictly computable across responses sharing **identical global prompt stimuli**:
1. **Global Stimulus Requirement**: Only model responses generated from a shared broadcast query sent simultaneously to the active category roster are eligible for consensus synthesis.
2. **Exclusion of Isolated Sub-Threads**:
   - When a user sends an inline follow-up reply to a specific model inside its expanded accordion, that interaction creates an **isolated** sub-thread (`isIsolated: true`).
   - Isolated conversations are **consensus-ineligible**. They do not corrupt, dilute, or recalculate the collective consensus synthesis of the category.
   - The pinned consensus row evaluates and displays the latest shared global broadcast turn.
3. **Headcount Score Ratio**:
   - Consensus convergence is calculated and displayed strictly as an objective headcount ratio (e.g. `✦ 7/7 Consensus`, `8/9 Consensus`).
   - Arbitrary percentages (e.g. "94% Agreement") are permanently forbidden.
4. **Pinned Consensus Row**:
   - Pinned permanently to the top or bottom of the model ticker window.
   - Displays the headcount ratio chip, a 1-line untruncated synthesis summary, and an active generation pulse.
   - Tapping it immediately opens the **3D Celestial Consensus Constellation Map** (`assets/html/consensus.html`).

### 5.2 3D Celestial Constellation Renderer
- Opens a full-height spatial window with deep obsidian space background.
- **Central Cluster**: Consensus-agreeing models cluster in a central constellation linked with translucent force-directed vector filaments.
- **Dissenting Stars**: Dissenting models render as 3D celestial nodes positioned radially by degree of divergence:
  - Vertical axis: Alignment with core consensus essence.
  - Horizontal axis: Mutual affinity and divergence between dissenting nodes.
- **Interactive Inspection**: Tapping any star node displays its one-line dissent rationale and full response card.

---

## 6. Dual Navigation System: Bottom Dock & Contextual Side Nav

### 6.1 Permanent Floating Bottom Dock (3 Icons)
The bottom dock floats permanently above the bottom bezel in an optical frosted glass capsule:
1. **Compose / Home** (`Icons.mode_comment_outlined` / `Icons.home_rounded`): Double function: resets open temporary panes and returns to the resting ticker; swiping up summons the global broadcast composer.
2. **Settings** (`Icons.tune_rounded`): Opens the functional settings panel (system preferences, keys, model routing).
3. **Apps** (`Icons.apps_rounded`): Summons the centered 7-destination Apps Selection Platter.
- **Swipe-Summoned Composer**: Swiping up on the pull-handle indicator capsule (`▲`) or tapping it summons the floating visionOS composer with multi-model target chips. Swiping down (`▼`) tucks it away.

### 6.2 Contextual Side Nav Bar (6 Work Surfaces)
The side nav adapts dynamically based on the active work surface:

| Active Surface | Side Nav Role | Contextual Affordances & Controls |
|---|---|---|
| **1. AI Chat** | Conversations & Models Panel | Tabs for `Local History`, `Global History`, and `Consensus History`; `+ New Chat` button; Model Category selector (swipeable left/right); Model selector chips within category. |
| **2. Smart Gen** | Workspace Control Panel | Direct switches for `Cards`, `Boards`, `Canvas`, and `Genie`; View filter pills (`Active`, `Urgent`, `All`); Quick "+ New Card" shortcut. |
| **3. Discover Market** | Market Category & Search Panel | Persistent Top Search Bar; Category navigation (`Prompts`, `Visuals`, `Video`, `Audio`, `Gallery`); Filter by popular/trending. |
| **4. Theme Selector** | Theme & Audio Switcher Panel | Quick-switch tabs between `Premium Marketplace`, `Theme Gallery`, and `Music Collection`; Soundscape toggle. |
| **5. Web Browser** | Browser Settings & Tabs Panel | Search engine selector (`DuckDuckGo`, `Google`, `Brave`); Cookie sync toggle; In-memory cache clear; Dedicated tab switcher. |
| **6. Files** | File System Categories Panel | Category tree (`All Files`, `Artifacts`, `Attachments`, `Model Outputs`, `System`); Storage usage stats; Batch export. |

### 6.3 Adequate Warning & Consent Modal (Switching Work Surfaces)
To honor the Zero User Data Loss Law:
- When a user attempts to switch between durable work surfaces while active drafts, incomplete forms, or streaming models exist, an **Adequate Warning & User Consent Dialog** (`_showSwitchConsentDialog`) is summoned.
- **Actions**:
  - `Stay`: Aborts surface switch, keeping the current work surface active.
  - `Switch`: Confirms switch, safely preserving all active drafts and component states in memory so nothing is lost upon return.

### 6.4 Nav Mutual Exclusivity Law
Any navigation interaction—on either the bottom bar or side nav—immediately closes all other open temporary panes and flyouts. Menus and temporary work surfaces never coexist simultaneously.

---

## 7. Exhaustive Smart Gen Autonomous Suite

### 7.1 Architecture: The 4 Pillars
Smart Gen is structured into four distinct, interconnected pillars:
1. **Smart Cards**: Individual context-bearing objects.
2. **Smart Boards**: Scoped work surfaces and background boards.
3. **Smart Canvas**: The interactive spatial playground bridging cards and boards.
4. **Smart Genie**: The autonomous Pro/Elite AI agent for generation, bulk editing, and refactoring.

### 7.2 Physical Object Realism (The Functional Meaning Law)
Every card, canvas, and board resembles its real-world physical counterpart:
- A **notebook** looks and turns pages like a real physical notebook.
- A **portfolio** looks like a genuine leather/paper portfolio.
- A **desk** resembles a real wood work surface.
- The functional meaning of the word is always the most real and impactful rendition. Words are chosen, not assigned, and their physical reality reduces user cognitive dissonance.

### 7.3 Smart Cards (Standard & Extensible Types)
- **Default Types**:
  1. `Artifacts`: Code snippets, documents, design systems, diagrams.
  2. `Tasks`: Actionable items with priority (`P0`–`P3`), assignee, and due date.
  3. `Reminders`: Time-sensitive alerts with automatic Google Calendar synchronization.
  4. `Projects`: Multi-turn initiatives grouping related tasks and artifacts.
  5. `Journal Entry`: Timestamped personal reflections.
  6. `Note`: Lightweight scratchpad memos.
  7. `List`: Ordered checklists with completion toggles.
  8. `Feature`: Engineering product specifications.
  9. `Job`: Career management items (company, role, dates, achievements).
  10. `Poster`: Visual showcase cards with full-bleed imagery.
  11. `Segment`: Category division markers.
  12. `+ Add New Card Type`: Extensible custom types.
- **Full-Surface Aesthetics**: Color tints apply to the full card surface as a soft optical gradient, not a mere left stripe.
- **3D Card Flip for Hidden Fields**: Cards with private notes feature a flip icon. Clicking it rotates the card 180° via 3D transform to reveal private fields on the back.
- **Urgent Digital Countdown Timer**: Urgent cards with deadlines feature a digital clock frame (`HH:MM:SS`) with red glowing tabular digits and overdue alert toasts.

### 7.4 Smart Canvas (The Spatial Playground)
Canvases hold cards and smaller grouping layers, sitting on top of boards:
- **Default Types**:
  `Glass`, `Mirror`, `Swimlane Vertical`, `Swimlane Horizontal`, `Name Photo Description`, `Portfolio`, `Notebook`, `Collection`, `Folder`, `Gallery`, `Diary`, `Journal`, `Kanban Widget`, `Table`, `Calendar Widget`, `Diagrams/Charts`, `+ Add New Canvas Type`.
- Up to 10 customizable canvases can be loaded simultaneously with swipeable pagination or direct numbered icon selection.

### 7.5 Smart Boards (Scope & Work Area)
Background boards holding cards and canvases:
- **Default Types**:
  `Kanban Board with Swimlanes`, `Calendar`, `Whiteboard Empty`, `Whiteboard with Swimlanes`, `Long Wood Bench`, `Workbench`, `Desk`, `Table`, `Wood Round Table`, `Wood Nightstand`, `Wood Long Table`, `Wood Coffee Table`, `+ Add New Board Type`.

### 7.6 The In-Line Editing Invariant (Zero Configuration Menus)
- **Forever Law**: All editable properties, attributes, dropdowns, and custom fields must be editable **in-line on the component itself**.
- ZERO separate configuration menus, settings panels, or complex sub-dialogs.
- Type, column, and status dropdowns provide an "+ Add new..." option at the bottom with an inline text input and auto-suggestions from previous history.

### 7.7 Smart Genie (Autonomous Pro/Elite Agent)
- The autonomous assistant responsible for Smart Gen entities, accessible in Pro and Elite tiers.
- Can be summoned or minimized in any card, board, or canvas view.
- Performs mass field edits, updates individual cards, reconfigures card type inheritance hierarchies, and refactors existing instances across boards.
- Elite tier enables custom coding agent attachments to Smart Genie for fully autonomous programmatic workflows.

---

## 8. Theme Marketplace & 5-Track Soundscape Engine (Figma Node `417-15864`)

### 8.1 Theme Marketplace Detail View
- **Source**: [Vision OS Design System — Node 417-15864](https://www.figma.com/design/YEuK4CL2uyECUhvGEcgCNS/Vision-OS-Design-System--Community---Copy-?node-id=417-15864&t=HGxWD7LNjZa9NQpD-4)
- **Metadata Mapping**:
  - Album Title $\to$ **Theme Name** (e.g. *Aurora Drift 4K*, *Ember Fall 4K*, *Star Bridge*).
  - Artist Name $\to$ **Creator / Soundscape Author** (e.g. *Polaris Optical Labs • Dynamic Atmosphere*).
  - Album Cover Artwork $\to$ **4K Live Wallpaper Artwork** displayed in a phone-proportioned squircle preview card (`76x128`) with specular highlights.
  - Tier Badge $\to$ `✦ Elite 4K Live` or `Free Spatial Canvas`.

### 8.2 The 5-Track Soundscape Package Requirement
- **Forever Law**: Every live wallpaper is packaged with a **curated set of exactly 5 ambient music tracks** composed to match that specific visual aesthetic.
- **Playlist Structure**:
  1. Column 1: Track Number (`01`–`05`).
  2. Column 2: Play/Pause button with animated real-time audio waveform bars.
  3. Column 3: Track Title & Mood Descriptor chip (e.g., *Solar Wind Ionization* / *Atmospheric Glow*).
  4. Column 4: Track Duration (`mm:ss`).
- **Actions**: `Apply Theme` (instant update) and `Preview` (temporary atmospheric preview).
- **Return Gesture**: Swiping down vertically on the sheet triggers `onSwipeDownReturn()`, returning to the regular theme selector ([Figma Node 69-1926](https://www.figma.com/design/jqsG6Hqkm7yws2iz607kim/Vision-Pro--Spatial-UI-Kit--Community-?node-id=69-1926)).

---

## 9. Centered Apps Selection Platter (Figma Node `2-6774`)

- **Source**: [Vision OS Design System — Node 2-6774](https://www.figma.com/design/YEuK4CL2uyECUhvGEcgCNS/Vision-OS-Design-System--Community---Copy-?node-id=2-6774&m=dev&t=e7CAGVGRU9jrcDVy-1)
- **Spatial Positioning**: Centered in neutral middle space over an optical backdrop blur scrim (`sigmaX: 30, sigmaY: 30`).
- **Frameless Glass Platter**: Bounded width (`maxWidth: 290px`) containing 7 labeled app destinations with clean text identifiers:
  1. `Smart Gen` (`Icons.inventory_2_rounded`)
  2. `Discover` (`Icons.explore_rounded`)
  3. `Themes` (`Icons.palette_rounded`)
  4. `Marketplace` (`Icons.shopping_bag_rounded`)
  5. `Files` (`Icons.folder_open_rounded`)
  6. `Audio` (`Icons.graphic_eq_rounded`)
  7. `Browser` (`Icons.language_rounded`)
- **Two-Escape Law**: Scrim clickaway (Escape 1) or circular `✕` button (Escape 2).

---

## 10. Message Click-to-Zoom Overlay (`MessageZoomOverlay`)

Tapping any message bubble in an expanded accordion summons the frameless zoom reader:
- **Frameless Presentation**: Background dimmed with heavy optical blur (`sigmaX: 24, sigmaY: 24`).
- **Faded Gradient Edges**: Top and bottom edges are smoothly faded into transparency via `ShaderMask` with a vertical `LinearGradient`.
- **Bottom Action Capsule**: Floating frosted glass capsule with actions:
  - `Copy`: Copies text to clipboard with haptic confirmation.
  - Struck on 2026-10-04 on David's instruction: `Branch`. He never asked for it (his line says only "action options along the bottom of the message"); it is developer vocabulary and it was wired to nothing.
  - `Save`: Auto-extracts and saves to Smart Gen Artifacts.
  - `Share`: Invokes native system share sheet.
  - `Close`: Dismisses the zoom overlay.

---

## 11. Curated Coverage Across ALL Five Modalities

Collider provides exhaustive, high-agency curation across 5 independent modalities (4 Pro + 4 Elite models per modality):

### 11.1 General Chat Modality
- **Pro Roster**: Gemini 3.6 Flash Lite, Claude 3.7 Haiku, GPT-5 Nano, Grok 3 Mini.
- **Elite Roster**: Gemini 3.6 Pro, Claude 3.7 Sonnet, GPT-5 Omni, DeepSeek R1.

### 11.2 Image Studio Modality
- **Pro Roster**: Flux 1.1 Schnell, Midjourney v6 Fast, SDXL Turbo, DALL-E 3 Standard.
- **Elite Roster**: Flux 1.1 Pro Ultra, Midjourney v6.1 Ultra, Imagen 3 HD, Recraft v3 Vector.
- **Pill Presentation**: Generative image thumbnails display directly in collapsed model pills for zero-tap visual comparison.

### 11.3 Video Lab Modality
- **Pro Roster**: Kling 1.5 Standard, Runway Gen-3 Alpha Turbo, Luma Dream Machine Fast, Pika 2.0 Standard.
- **Elite Roster**: Kling 1.5 Pro, Runway Gen-3 Alpha HD, Sora 1.0 Cinema, Minimax Hailuo 01 Director.

### 11.4 Audio & Music Modality
- **Pro Roster**: Suno v3.5 Fast, Udio 130 Standard, ElevenLabs Flash TTS, Cartesia Sonic.
- **Elite Roster**: Suno v4 Ultra, Udio v1.5 High-Fi, ElevenLabs Conversational Voice v2, Kyutai Moshi Native.
- **Pill Presentation**: Audio waveforms render directly in collapsed pills with inline play/pause.

### 11.5 Coding & Autonomous Agents Modality
- **Pro Roster**: Claude 3.7 Sonnet Code, DeepSeek Coder V2.5, Qwen 2.5 Coder 32B, GPT-5 Code Mini.
- **Elite Roster**: Devin Autonomous Agent, Claude 3.7 Sonnet Multi-File, Codex Ultra, DeepSeek R1 Architect.

---

## 12. Complete Catalog of Implementations

The following catalog documents the complete, verified codebase implemented in `collider_flutter`:

### 12.1 Core System & Spatial Glass Tokens
- [`lib/core/theme/vision_glass.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/core/theme/vision_glass.dart): Multi-plane optical glassmorphic container supporting specular rims, dynamic refraction, depth layering (Planes 0–5), and squircle corners.
- [`lib/core/theme/specular_border.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/core/theme/specular_border.dart): 1px specular light highlight simulation with top-left directional illumination and bottom occlusion shading.
- [`lib/core/theme/vision_pressable.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/core/theme/vision_pressable.dart): VisionOS tactile pressable surface with scale feedback (0.97) and haptic response.

### 12.2 Navigation Architecture
- [`lib/features/nav/permanent_nav_bar.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/nav/permanent_nav_bar.dart): 3-icon permanent floating bottom dock (`Compose/Home`, `Settings`, `Apps`) with swipe-summon pull indicator (`▲`).
- [`lib/features/nav/contextual_side_nav.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/nav/contextual_side_nav.dart): Contextual side navigation panel dynamically adapting across all 6 work surfaces (AI Chat, Smart Gen, Discover Market, Theme Selector, Web Browser, Files).
- [`lib/main.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/main.dart): Master coordinator managing:
  - Consensus calculation excluding isolated sub-threads (`isIsolated == true`).
  - Adequate warning & user consent modal dialog (`_showSwitchConsentDialog`) with in-memory draft preservation.
  - Zero backdrop blur during theme browsing (`_activeDrawer == 'themes'`).
  - Mobile responsive layouts with tucked side nav triggers.

### 12.3 Conversational Ticker Stack & Consensus
- [`lib/features/ticker/widgets/consensus_row.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/ticker/widgets/consensus_row.dart): Pinned consensus row displaying headcount score ratio (e.g. `7/7`), 1-line untruncated synthesis summary, and 3D Celestial Map trigger.
- [`lib/features/ticker/widgets/model_pill.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/ticker/widgets/model_pill.dart): Model pills tinted in their provider's colour, untruncated summaries, inline accordion chat with tailed speech bubbles (`_TailedBubble`), local tools ribbon, and isolated follow-up reply box.
- [`lib/features/ticker/widgets/message_zoom_overlay.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/ticker/widgets/message_zoom_overlay.dart): Frameless zoom reader with vertical linear gradient edge fading and contextual actions (`Copy`, `Save`, `Share`, `Close`).
- [`lib/features/ticker/widgets/local_history_pane.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/ticker/widgets/local_history_pane.dart): Centered model-specific conversation history popup with search across titles and message bodies.

### 12.4 Themes, Wallpapers & 5-Track Soundscapes
- [`lib/features/wallpaper/widgets/windowless_theme_scroller.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/wallpaper/widgets/windowless_theme_scroller.dart): In-view windowless wallpaper carousel with portrait squircle cards (`68x116`), `FilterQuality.medium`, tier switcher (`Free` vs `✦ 4K Live`), and direct link to 5-track view.
- [`lib/features/theme/theme_marketplace_detail_view.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/theme/theme_marketplace_detail_view.dart): Figma Node `417-15864` implementation replacing album metadata with Theme Name and Creator, displaying 5 curated ambient tracks with animated waveforms, and swipe-down return gesture.
- [`lib/features/drawers/wallpaper_drawer.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/drawers/wallpaper_drawer.dart): Full wallpaper gallery grid with `childAspectRatio: 0.56` portrait squircle cards.
- [`lib/models/theme_def.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/models/theme_def.dart): Data models for `WallpaperTheme`, `AmbientTrack`, and complete `WallpaperCatalog`.

### 12.5 Apps Selection Platter & Work Surfaces
- [`lib/features/apps/apps_popup_pane.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/apps/apps_popup_pane.dart): Figma Node `2-6774` centered platter with 7 labeled icons (`Smart Gen`, `Discover`, `Themes`, `Marketplace`, `Files`, `Audio`, `Browser`) and Two-Escape dismissals.
- [`lib/features/smartgen/screens/smartgen_screen.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/smartgen/screens/smartgen_screen.dart): Smart Gen suite implementing Cards, Boards, Canvas, and Genie tabs with in-line editing.
- [`lib/features/market/screens/market_screen.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/market/screens/market_screen.dart): Discover Market surface with prompt feed, Grok Imagine studio, Video lab, and gallery.
- [`lib/features/browser/screens/in_app_browser_sheet.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/browser/screens/in_app_browser_sheet.dart): Single-instance dedicated model browser with tab management.
- [`lib/features/files/screens/files_screen.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/files/screens/files_screen.dart): Spatial file manager with categorized assets and exports.

### 12.6 Verification & Automated Tests
- [`test/widget_test.dart`](file:///c:/Users/D/Documents/collider_flutter/test/widget_test.dart): Comprehensive 4-suite automated test covering:
  1. VisionOS architecture, consensus row headcount, permanent nav bar, and history navigation.
  2. Mobile responsive layout, tucked side nav, and session triggers.
  3. Theme marketplace 5-track template (Node 417-15864) and swipe-down return.
  4. Contextual side nav adaptation across 6 surfaces and adequate warning consent modal.
- Live server: Running continuously on assigned port `http://localhost:28470/`.

---

## 13. Verification Invariants & QA Gates

1. **User-Perspective Reality Over Clerical Checks**:
   - Typechecks and compiler exit codes are internal clerical checkpoints with zero customer value on their own.
   - All user workflows must be physically running and visually confirmed in the live browser preview.
2. **Visual Polish Standard**:
   - 100% compliance with high-agency frontend benchmarks (Linear/Raycast/visionOS). No muddy blurs, no broken Android padding, no generic AI tells.
3. **Session Attribution**:
   - Live mobile/web preview runs continuously on assigned session ports (`http://localhost:28470/`).
4. **Independent QA / Inspector Subagent Gate**:
   - Prior to declaring any milestone complete, an independent QA/Inspector subagent must physically verify the running application and confirm zero functional or visual defects.

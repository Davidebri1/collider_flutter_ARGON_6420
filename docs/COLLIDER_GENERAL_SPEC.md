# Collider — Universal Product & Architectural Specification (v4.3 General Edition)

> **Classification**: Platform & Framework-Agnostic Master Specification  
> **Status**: Authoritative & Active  
> **Design Authority**: Apple visionOS Spatial Design System Exclusively (Zero Custom Theming)  
> **Target Platforms**: Universal Mobile, Spatial, & Web (Flutter Impeller, Native Swift/visionOS, React Native, Canvas/WebGL)  

> **v4.3 Changelog**: 
> - **Consensus Eligibility & Isolated Conversation Handling**: Codified the foundational law that consensus is strictly computable across responses sharing identical global prompt stimuli. Defined that inline follow-up branches are **consensus-ineligible** for global consensus; the pinned consensus row evaluates the latest shared global broadcast turn.
> - **Complete Contextual Side Nav Guidelines**: Fully specified all contextual control options across all 6 work surfaces (AI Chat, Smart Gen, Discover Market, Theme Selector, Web Browser, Files).
> - **Exhaustive Smart Gen Suite Integration**: Fully captured `Smart Gen Summary.md`, `smart gen ui.md`, and `smart gen and testing suite ideas.txt` into the core specification. Integrated the 4 pillars (Smart Cards, Smart Boards, Smart Canvas, Smart Genie), real-world physical object metaphors, the In-Line Editing Invariant (zero separate configuration menus), and Pro/Elite Smart Genie agentic capabilities.
> - **visionOS Exclusive Design Authority**: Formalized that Apple visionOS is the **ONLY** theme. All physics, animations, design tokens, materials, and colors derive strictly and exclusively from the visionOS spatial kit or direct user overrides. Custom themes, invented animation styles, and ungrounded "celestial drift" physics are permanently prohibited.
> - **Inseparable Ticker Dimensions (Height & Width Caps) & Removal of Drag-and-Drop**: 
>   - **Height Cap**: Strictly $\le 40\%$ of screen height (internal momentum scroll only; ticker container never grows past 40%).
>   - **Width Cap**: Strictly equal to the width of the bottom nav bar (`maxWidth: 240px–260px` on mobile; max `480px` on desktop/spatial). Half-width, content-hugging, NEVER full-width.
>   - **Non-Interactive Surface**: Model rows are a non-interactive surface (no dragging, no reordering, non-repositionable). Long-press activation glow and drag-and-drop mechanics are permanently deleted.
>   - **Zero Card Borders/Chrome**: Containers carry no outer borders; there is nothing left for a border to signal.
>   - **The Summary Invariant**: *"Expansion is for depth, not completion. If the user must expand to get the answer, the summary failed."*
> - **Curated Coverage Across ALL Five Modalities**: Every model category (General Chat, Image Studio, Video Lab, Audio & Music, Coding & Agents) is given exhaustive, high-agency curation (4 Pro + 4 Elite) with explicit call shapes, real API endpoints, and sub-modality coverage (e.g. Audio covering Music, Raw Byte Stream TTS, and Conversational Voice).
> - **Zero User Data Loss Law**: User drafts can only be destroyed by the user. Opening or closing any drawer, popup pane, or switching surfaces must preserve active prompt drafts in memory.
> - **Thumb-Zone Ergonomics**: All actionable buttons, primary triggers, and tabs must reside below mid-phone height to prevent one-handed reach strain.
> - **Windowless Theme Gallery & 5-Track Soundscape Engine**: In-view windowless carousel with real-time live background updates on scroll, `Preview` vs `Set` actions, swipe-up tier elevation to 4K Live wallpapers, and 5 curated ambient tracks per theme (Figma Node `417-15864`).
> - **Generative Media Collapsed Pill Rule**: Media pills (Image, Video, Audio) display thumbnails/waveforms directly in collapsed state for zero-tap comparison.

---

## 1. Product Vision & Core Philosophy

### 1.1 The Prime Directive: Reducing Cognitive Load
Collider provides a unified, transparent lens into multi-model artificial intelligence without forcing the user to context-switch across fragmented interfaces or grapple with model selection anxiety.
- **Conversation Stream $\equiv$ Response Ticker Stack**: The application does NOT contain a separate or duplicate chat screen. The floating model row ticker on Plane 2 IS the conversational interface. In its resting collapsed state, it delivers instantaneous, zero-tap comparison across all models. When clicked, each row expands into an inline accordion containing tailed speech bubbles, local model tools, and an isolated reply box.
- **Proactive Value Delivery**: The system computes and surfaces value before the user asks for it. Consensus synthesis is aggregated and displayed in-line before a manual comparison is requested. Tasks, deadlines, project structures, and code artifacts are autonomously identified and captured from conversation context.
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

### 1.4 The Emotional Core: Unobstructed Living Wallpaper (Plane 0)
The visual and emotional foundation of Collider is its living wallpaper layer:
- The wallpaper remains visible and continuous across all screen states, modals, and sub-drawers.
- All windows, sheets, ribbons, and modals are rendered as translucent optical frosted glass, allowing background movement and atmosphere to illuminate through.
- Background media consists of organic, breathing, endless atmospheric loops with zero jarring transitions or jerky ping-pong loops.
- Negative space is the product void: 65%–75%+ of the screen must remain unobstructed during resting states. Resting UI elements must be content-hugging and compact (`maxWidth: 240px–260px` on mobile; max `480px` on spatial/desktop).

---

## 2. Verbatim Canonical User Layout Segment

The following directives represent the authoritative user layout contract:

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
- **Apple visionOS is the ONLY design system and theme**: All visual components, materials, typography, button states, physics, and animations must derive strictly and exclusively from official Apple visionOS component kits or direct user overrides.
- **Prohibition of Custom Theming & Invented Physics**:
  - No custom theming layers on top of visionOS.
  - No pseudo-game animations, no "celestial drift physics", no arbitrary non-standard easing curves.
  - All transitions must follow genuine Apple visionOS spatial mechanics: spring-damped drawer ascension, optical glass refraction, 1px specular light highlights, and standard visionOS depth layering.
- **Permanent Ban on AIisms**:
  - ZERO glitter/sparkle icons (`Icons.auto_awesome*`, magic wands), toy robot heads, or glowing brains.
  - Pure deterministic engineering icons only (`Icons.balance_rounded`, `Icons.hub_rounded`, `Icons.inventory_2_rounded`, `Icons.terminal_rounded`, `Icons.tune_rounded`).
  - ZERO AI marketing buzzwords ("Magic", "Cosmic"). Pure functional engineering terms only: *Artifacts*, *Consensus*, *Synthesis*, *Models*.
    - Struck on 2026-10-04 (not David's; added by the agent that wrote this rule on 2026-09-05): the ban on a breathing pulse while a model is answering, and the renaming of "Smart Gen" to "Workspaces". "Smart Gen" is David's own name for the feature and is never renamed.

### 3.2 Optical Multi-Plane Z-Depth Hierarchy

Every element resides on an explicit optical depth plane:

| Depth Plane | Relative Z | Optical Tint | Blur Radius | Border Highlight | Ambient Shadow | Purpose |
|---|---|---|---|---|---|---|
| **Plane 0: Atmosphere** | `0` | Dynamic Living Canvas | None | None | None | Continuous living wallpaper |
| **Plane 1: Base / Prompt** | `1` | Translucent White `10%` | `16px` | `0.5px` Specular Top | `8px` blur, `18%` opacity | Unsummoned resting query indicator |
| **Plane 2: Resting Windows** | `2` | Translucent White `12%` | `24px` | None (chromeless) | `12px` blur, `22%` opacity | Floating model rows ticker container |
| **Plane 3: Elevated Flyouts** | `3` | Translucent White `14%` | `28px` | `0.6px` Specular Top | `16px` blur, `28%` opacity | History flyouts, summoned composer |
| **Plane 4: Modals & Zoom** | `4` | Translucent White `16%` | `32px` | `0.6px` Specular Top | `20px` blur, `32%` opacity | Centered Apps popup, Message Zoom |
| **Plane 5: Work Surfaces** | `5` | Translucent White `18%` | `36px` | `0.6px` Specular Top | `24px` blur, `36%` opacity | 3D Consensus, Smart Gen, Theme Market |

### 3.3 Specular Rim Lighting & Bevels
Glass panels feature a 0.5px to 0.6px simulated directional light rim:
- **Top / Top-Left Edge**: Soft specular white highlight simulating ambient overhead luminance.
- **Bottom / Right Edge**: Subtle occlusion shadow grounding the panel against Plane 0.
- **Corner Curvature**: Continuous curvature squircles (radii between 16px and 28px).
- **Compound Panes**: Where two panes share an edge, outer corners round while the shared seam stays flat.

### 3.4 Typography Standard
- **Typeface Family**: Proportional modern geometric sans-serif (*Instrument Sans* / *SF Pro Display*). Monospace is permanently excluded from UI labels.
- **Strictly Untruncated 1-Line Summaries**: Consensus row and model pill summaries must never display ellipsis (`...`). Complete thoughts must fit naturally or scale down gracefully with `BoxFit.scaleDown`.

### 3.5 Provider Color Discipline
- Glass surfaces remain neutral, monochromatic, and optically translucent by default.
- Provider identity is carried by an emissive specular **hue** on the left edge highlight (not a flat colored slab).
- A non-hue-dependent secondary cue (model name text or logo icon) must always accompany the color to support color-vision deficiency.
- Heavy neon borders or opaque colored card bodies are prohibited.

---

## 4. Screen Architecture & Core Layout

### 4.1 Home Screen Layout (Conversation Stream $\equiv$ Response Ticker Stack)

```
┌────────────────────────────────────────────────────────┐
│ Plane 0: Living Wallpaper (Continuous, Unobstructed)   │
│                                                        │
│ [Floating Input Prompt / Active Query Indicator]       │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Plane 2: Model Row Ticker                          │ │
│ │          Height: ≤ 40% of screen height            │ │
│ │          Width:  = bottom nav bar width (half-width)│
│ │          Chrome: NONE (no card borders/chrome)     │ │
│ │ ┌────────────────────────────────────────────────┐ │ │
│ │ │ Pinned Consensus Row (Score + Summary + Map >) │ │ │
│ │ ├────────────────────────────────────────────────┤ │ │
│ │ │ Scrollable Model Rows (Max 9, no card chrome)  │ │ │
│ │ │  - Model A (Collapsed Row: Text or Thumbnail)  │ │ │
│ │ │  - Model B (Expanded Accordion, pushes down)   │ │ │
│ │ │    [Local Tools Ribbon: Search, Files, History]│ │ │
│ │ │    [Momentum Scroll Chat Stream — tailed bubbles]│ │
│ │ │    [Inline Isolated Branch Composer]           │ │ │
│ │ └────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│         [▲ Swipe up for composer pull indicator]       │
│ ┌──────────────┐                          ┌──────────┐│
│ │ Contextual   │                          │ Bottom   ││
│ │ Side Nav     │                          │ Nav: 3   ││
│ │ (per surface)│                          │ icons    ││
│ └──────────────┘                          └──────────┘│
└────────────────────────────────────────────────────────┘
```

#### A. Inseparable Ticker Geometry (Height & Width Caps)
The model row ticker's dimensions are governed by two strict, inseparable geometric laws:
1. **Height Cap**: **Max height: 40% of screen height.**
   - The outer ticker frame NEVER expands beyond 40% of the viewport.
   - When accordions expand or additional model rows stream in, internal momentum scrolling accommodates the height without pushing siblings off-screen or expanding the outer footprint.
2. **Width Cap**: **Max width: equal to the bottom nav bar's width (half-width).**
   - **NOT full width**. Resting containers must be compact and content-hugging (`maxWidth: 240px–260px` on mobile; max `480px–500px` on tablet/spatial).
   - This preserves 65%–75%+ of the screen as unobstructed living wallpaper void.
3. **Non-Interactive Surface**:
   - Model rows are a non-interactive surface (not draggable, not repositionable).
   - **Permanent Deletion of Drag-and-Drop**: Model card drag-and-drop and the 1.5s long-press glow are permanently deleted. There is zero reordering since the order encodes deterministic provider categorization and the summary is complete.
4. **Zero Card Chrome / Borders**:
   - No outer bordered container; there is nothing left for a border to signal once positioning is non-manipulable.

#### B. The Summary Invariant (Forever Law)
- **"Expansion is for depth, not completion. If the user must expand to get the answer, the summary failed."**
- Every collapsed row must deliver a self-contained, actionable, complete answer in its 1-line untruncated preview. Expansion is strictly for follow-up questions, file inspection, or browsing history.

#### C. Generative Media Collapsed Pill Rule (Zero-Tap Comparison)
- For Image, Video, and Audio/Music categories, collapsed pills must render **inline visual thumbnails and audio waveforms** directly inside the collapsed row.
- **Zero Interaction to Compare**: The user does NOT tap or expand to compare media. The thumbnails *are* the comparison.
- **Expanded Media State**: Full-resolution playback, prompt parameters, and multiple generations as a horizontal scrollable strip.

#### D. Pinned Consensus Row
- Pinned permanently to the top or bottom of the row ticker. Lives only here — never duplicated on any nav bar.
- **Score Chip**: Objective democratic headcount ratio (e.g. `✦ 7/7 Consensus`, `8/9 Consensus`). Arbitrary percentages are forbidden.
- **Essence Summary**: Strictly 1-line untruncated synthesis capturing the core mutual agreement.
- **Full Map Trigger**: Clicking the row opens the 3D celestial constellation map work surface.

#### E. Model Accordion Rows
- **Collapsed State (52px height)**:
  - Provider hue accent on left edge + model name text.
  - Relative timestamp.
  - Strictly untruncated 1-line answer (or generative media thumbnail).
- **Expanded State** (pushes subsequent rows down within the ticker's internal 40%-height scrollable bounds; does not expand outer ticker footprint):
  - **Local Tools Ribbon**: Search toggle, local model files picker, local history flyout, copy answer button, dedicated model browser instance, collapse button.
  - **Momentum-Scrolling Chat Stream**: Max 240px internal height, vertical momentum scrolling, frosted message bubbles with a tailed shape (`_TailedBubble`), not a plain rounded rectangle.
  - **Inline Isolated Branch Composer**: Dedicated text input for follow-up prompts sent exclusively to this single model.

#### F. Ticker Boundary & Error States
- **Empty State**: Single clean glass guidance pill (*"Select models to begin"*). Bottom dock remains accessible; zero layout shift.
- **Subtle Error States**: Subtle inline status indicator with brief 1-line error message; inline Retry/Dismiss action without mutating card geometry or pushing siblings off-screen.

---

### 4.2 Bottom Nav Bar
Permanently floating above the bottom bezel in an optical frosted glass capsule. 3 icons:
1. **Compose** (doubles as Home): Restores pristine home window, collapses open accordions, dismisses temporary flyouts, and opens broadcast composer.
2. **Settings**: Opens functional configuration drawer.
3. **Apps**: Summons the centered Apps Popup Pane.

*Any interaction with this bar closes all other open panes — temporary and durable alike.*

---

### 4.3 Contextual Side Nav Bar: Exhaustive Control Guidelines
A second, contextual nav bar positioned on the side that reshapes based on whichever work surface is currently active. Every work surface provides tailored, high-utility controls:

| Active Work Surface | Contextual Side Nav Panel Role | Contextual Options Available |
|---|---|---|
| **AI Chat (The Conversation Ticker)** | **Session & Modality Hub** | • **3 Navigation Tabs**: `Local History` (conversations with focused model), `Global History` (all past broadcast sessions), `Consensus` (consensus archive & logs).<br>• **Action Trigger**: `+ New Conversation` (clears active ticker context, restores pristine state).<br>• **Category Swiper**: Horizontal swipeable pill strip to switch between `General`, `Image`, `Video`, `Audio`, and `Coding`.<br>• **Model Filter Chips**: Toggle checkboxes to include/exclude specific active models from the broadcast cluster. |
| **Smart Gen** | **Kanban & Component Hub** | • **4 Mode Selectors**: `Smart Cards`, `Smart Boards`, `Smart Canvas`, `Smart Genie`.<br>• **Board View Switcher**: Quick-switch between Kanban, Calendar, Notebook, Photo Album, Storyboard, Vision Board, Swimlanes, Portfolio Desk, US Map, World Map.<br>• **Component Tray**: Filter cards and canvases by type, attribute, or function.<br>• **Bulk Selection**: Multi-select trigger for grouping and batch actions. |
| **Discover Market** | **Ecosystem Navigation & Search** | • **Category Panels**: Prompts, Fine-Tunes, Agent Workflows, Datasets, Templates.<br>• **Persistent Search Bar**: Search input that lives permanently on the side nav for real-time item discovery.<br>• **Filter Toggles**: Sort by popularity, new releases, free vs premium. |
| **Theme Selector & Gallery** | **Atmosphere & Music Switcher** | • **Section Quick-Switch**: Toggle between `Theme Gallery` (free spatial carousel), `Premium Marketplace` (4K Live wallpapers), and `Music Collection`.<br>• **Tier Filter**: Free Spatial Canvas vs ✦ Elite 4K Live.<br>• **Soundscape Playlist Trigger**: Direct link to 5-track ambient playlist detail view. |
| **Web Browser** | **Web Controls & Tab Manager** | • **Browser Settings Panel**: Search engine selection, Ad/Tracker blocking toggle, Reader Mode trigger, SSL indicator.<br>• **Active Tabs List**: Vertical stack of active browser tabs with instant close `✕`.<br>• **Session Utilities**: Clear cache, copy URL, export reading list. |
| **Files (Spatial Library)** | **Media & Asset Categories** | • **Category Tree**: Documents, Code Blocks, Generated Images, Audio Tracks, Video Renders, Smart Gen Artifacts.<br>• **Sort & Filter**: By date modified, originating model, project association, or file size. |

*Any interaction with the contextual side nav closes all other open panes, since menu and work surface never coexist.*

---

### 4.4 Centered Apps Popup Pane
- **Summon Position**: Centered in the middle neutral area of the screen on Plane 4.
- **Framing**: Frameless frosted glass capsule menu over a dimmed/blurred backdrop scrim. Strictly zero outer rectangular window canvas.
- **Presentation**: Icons only (not buttons) with clean text identifiers in *Instrument Sans*:
  1. `Smart Gen` (`Icons.inventory_2_rounded`)
  2. `Discover` (`Icons.explore_rounded`)
  3. `Themes` (`Icons.palette_rounded`)
  4. `Marketplace` (`Icons.shopping_bag_rounded`)
  5. `Files` (`Icons.folder_open_rounded`)
  6. `Audio` (`Icons.graphic_eq_rounded`)
  7. `Browser` (`Icons.language_rounded`)
- Clicking any icon opens that durable work surface, floating and centered, with background blurred/dimmed.
- **Two-Escape Law**: Scrim tap (Escape 1) or circular `✕` button (Escape 2).

### 4.5 Swipe-Summoned Global Broadcast Composer
- **Summon Gesture**: Swiping up on the bottom nav bar / pull indicator capsule.
- **State Acknowledgment**: Features a downward arrow pull indicator (`▼`) confirming the summoned state; swiping down tucks it back away (`▲`).
- **Model Selector Carousel**: Horizontal chips carousel allowing users to toggle which of the active models receive the broadcast prompt.
- **Broadcast Input**: Glass text input with instant broadcast dispatch. Automatically tucks away upon send to reveal streaming model cards.

### 4.6 Floating User Prompt Lifecycle & Message Click-to-Zoom
- **Floating User Prompt**: User's last submitted prompt floats collapsed above the wallpaper with no outer frame. Tapping zooms it into the blurred foreground; tapping outside dismisses back to collapsed.
- **Message Click-to-Zoom Overlay**:
  - Tapping any chat message or user prompt opens a frameless zoom presentation over a dimmed background (`sigma: 32`).
  - Top and bottom edges smoothly fade into transparency using vertical gradient alpha masking.
  - Floating bottom action capsule: `Copy`, `Save to Smart Gen`, `Share`, `Close`.

### 4.7 Dedicated In-App Browser System
- Every model has access to an isolated browser instance via its local tools ribbon.
- **System Invariant**: Only **one active browser instance** exists in the application at any given time (even across background models) to conserve memory and maintain deterministic session states.

### 4.8 The Two-Escape Law & Settings Scope
- **Temporary Flyouts**: Must provide two frictionless exit paths: (1) outside scrim tap and (2) circular `✕` close button.
- **Durable Work Surfaces**: Require an explicit exit action (`✕` button, "Done" pill, or any bottom/side nav interaction).
- **Settings Scope**: Restricted to functional options only (API keys, storage, account level, device sync). Vanity cosmetic toggles are permanently excluded.

---

## 5. Windowless Theme Gallery & 5-Track Soundscape Architecture

### 5.1 Windowless Theme Carousel & Live Preview
- **In-View Summoning**: Clicking Theme Gallery opens the carousel right in view without navigating to a new screen.
- **Live Background Switching on Scroll**: As the user scrolls horizontally through wallpaper thumbnails, each new image changes the background *live* with immediate visual feedback.
- **Inline Action Affordances**:
  - `Preview`: Temporarily tests the atmospheric wallpaper while keeping current preferences intact.
  - `Set`: Commits and permanently saves the selection to persistent storage.
  - `Revert`: Instantly restores the previous wallpaper.

### 5.2 Swipe-Up Tier Elevation to 4K Live Wallpapers
- Swiping up vertically on the regular theme carousel elevates the interface to the upper tier where **4K Live Wallpapers** reside.
- Displays high-resolution live thumbnails with clean entitlement indicators (`✦ Elite 4K Live`) without breaking the windowless immersion.
- Clicking any locked 4K Live theme opens the Theme Marketplace Detail View with upgrade affordances.

### 5.3 Curated 5-Track Ambient Soundscape Engine (Figma Node `417-15864`)
The Theme Marketplace detail view adopts the Apple visionOS music playlist architecture:
- **Metadata Replacement**:
  - Album Title $\to$ **Theme Name** (e.g. *Aurora Drift 4K*, *Ember Fall 4K*).
  - Artist Name $\to$ **Creator & Soundscape Author** (e.g. *Polaris Optical Labs • Dynamic Atmosphere*).
  - Album Art $\to$ **4K Live Wallpaper Hero Artwork** in a 104x104 squircle frame with 1px specular lighting.
  - Tier Badge $\to$ `✦ Elite 4K Live` or `Free Spatial Canvas`.
- **The 5-Track Atmospheric Rule**:
  - Every Live Wallpaper Theme is packaged with a **curated bundle of exactly 5 ambient audio tracks**.
  - Tracks render in visionOS playlist row format:
    1. **Track Index**: Numbered `01` through `05`.
    2. **Interactive Playback**: Tap to toggle play/pause with real-time 3-bar animated waveform visualizer.
    3. **Track Title & Mood**: Title with atmospheric mood descriptor chip (e.g. *Solar Wind Ionization* / *Atmospheric Glow*).
    4. **Duration**: Minute and second duration tag (`mm:ss`).
- **Swipe-Down Return Gesture (Figma Node `69-1926`)**:
  - Swiping down vertically on the detail view immediately returns to the regular horizontal theme carousel (`WindowlessThemeScroller`).
  - Top pill button `↓ Selector` and circular `✕` button provide two additional escape paths.

---

## 6. Consensus Engine & 3D Celestial Constellation Architecture

### 6.1 Consensus Eligibility & Isolated Conversation Handling
The foundational purpose of distinguishing between global broadcast responses and isolated conversation branches is **consensus integrity**:

1. **The Shared Context Invariant**:
   - Consensus can **ONLY** be computed across responses that share the identical prompt stimulus.
   - You cannot derive a democratic consensus between models responding to completely different questions.

2. **Consensus Eligibility Classification**:
   - **Consensus ELIGIBLE (Global Broadcast)**:
     - All responses generated by models that received the shared global broadcast prompt from the primary composer or prompt sheet.
     - These responses enter the collective consensus synthesis pool.
   - **Consensus INELIGIBLE (Isolated Branches)**:
     - When a user expands a specific model's pill (e.g. Model B) and sends a targeted follow-up prompt via its inline composer, Model B branches off into an **isolated conversation**.
     - Because Models A, C, D never received that follow-up prompt, Model B's new response is **strictly ineligible for the global consensus**.

3. **System Behavior During Isolated Branches**:
   - **Visual Distinction**: The branched model's pill displays a **subtle, pristine warm highlight** (gold-tinted specular rim) indicating that it is operating in an isolated branch and is detached from the active global consensus group.
   - **Pinned Consensus Row Continuity**: The pinned consensus row on Plane 2 continues to evaluate and display the synthesis of the **latest shared global message turn**. It is never corrupted, overwritten, or confused by isolated branches.
   - **Historical Vote Retention**: In the global consensus history and 3D map, Model B's original response to the shared global broadcast is preserved as its representative position in that global turn.
   - **Re-Joining the Global Consensus**: When the user subsequently issues a new global prompt from the main composer, all active models receive it simultaneously. This clears the isolated branch state, synchronizes all models to a new shared turn, and restores full consensus eligibility across the entire active cluster.

### 6.2 Consensus Calculation Pipeline
1. **Essence Extraction**: The engine reduces raw model responses into standalone, factual/thematic assertions (not descriptions of the response, and omitting model names).
2. **Democratic Headcount Law**: Agreement is calculated strictly as an objective democratic headcount ratio of identical essences (e.g. `9/9`, `7/8`). Arbitrary percentages are forbidden. The arbiter has zero vote except in the event of an exact tie.
3. **Verbatim Summary Reduction**: The winning essence is copied verbatim as the 1-line consensus summary. Dissenting opinions are also preserved verbatim.
4. **Logical Chain Counting via 5 Whys**: Counts explicit connectives (*because, so, therefore, thus, hence*) and implied logic in raw responses to determine celestial star node mass and luminance.

### 6.3 3D Celestial Constellation Renderer
- Opens a dedicated full-height spatial work surface with obsidian space background.
- **Agreement Center**: Central cluster representing consenting models linked with dynamic force-directed vector beams.
- **Dissenting Stars**: Dissenting models render as distinct celestial nodes positioned radially by degree of divergence:
  - *Radial distance*: Level of disagreement with core consensus.
  - *Angular clustering*: Affinity and agreement between dissenting peers.
- **Node Inspection**: Tapping any star node highlights its vector lines and opens a floating detail card showing its rationale and dissenting output.

---

## 7. Smart Gen Autonomous Intelligence Suite (Trello-Grade Kanban Architecture)

The Smart Gen Suite encapsulates an industrial-grade, visual Kanban manager ported from [`Smart Gen Summary.md`](file:///c:/Users/D/Documents/02_Specifications/SmartGen/Smart%20Gen%20Summary.md), [`smart gen ui.md`](file:///c:/Users/D/Documents/02_Specifications/SmartGen/smart%20gen%20ui.md), and [`smart gen and testing suite ideas.txt`](file:///c:/Users/D/Documents/02_Specifications/SmartGen/smart%20gen%20and%20testing%20suite%20ideas.txt).

### 7.1 The Four Core Pillars
Smart Gen is structured across four distinct architectural tiers:
1. **Smart Cards**: Base atomic items that sit on canvases or boards and draw context from them.
2. **Smart Canvas**: Intermediate grouping layers that hold cards and sit on top of boards (e.g. realistic work desk, bench, notebook).
3. **Smart Boards**: The macro background work area holding both cards and canvases, defining the overall project scope.
4. **Smart Genie**: The Pro/Elite AI agent assistant that manages, generates, edits, and refactors Smart Gen entities.

### 7.2 The Real-World Physical Object Metaphor
Every card, canvas, and board adopts the physical perspective and appearance of the real-world object it represents:
- **Literal Meaning**: A notebook looks like a physical bound notebook; a portfolio looks like an accordion physical portfolio; a desk canvas looks like a physical oak workbench.
- Words carry their singular, concrete meaning. The user immediately understands the functional affordance because the visual representation matches reality.

### 7.3 The In-Line Editing Invariant (Forever Law)
- **Zero Separate Configuration Menus**: All properties, attributes, statuses, tags, due dates, and colors must be **in-line editable directly on the component itself**.
- There are no separate settings modals or detached configuration windows.
- If a property exists on a card, canvas, or board, you tap and configure it right at its physical location. Status can be swapped from a dropdown to a toggle, input field, color tag, or custom field directly in-place.
- Inheritance is automatically implied across all related child components.

### 7.4 Smart Cards (Atomic Items)
Smart cards represent discrete actionable units. Default base types:
- `Artifacts`: Code deliverables, architecture blueprints, legal drafts.
- `Tasks`: Action items with P0–P3 priorities and assignee tags.
- `Reminders`: Deadlines synchronized to device calendars.
- `Projects`: High-level initiatives containing nested tasks.
- `Journal Entry`: Dated reflective entries.
- `Note`: Freeform rich text with markdown support.
- `List`: Checklist with checkbox state toggles.
- `Feature`: Product capability specification.
- `Job`: Career/recruitment card with company, position, and milestones.
- `Poster`: Visual graphic banner or mood board element.
- `Segment`: Sliced workflow component.
- `+ Add New Card Type`: User-defined custom card type.

#### Card Mechanics
- **3D Card Flip for Hidden Fields**: Cards with private notes or hidden attributes feature a 3D 180° rotation revealing private data on the reverse side.
- **Digital Clock Countdown Frame**: Urgent cards with due dates display a glowing red digital clock frame (`HH:MM:SS`) with automatic `OVERDUE` alert states.
- **All Elements Hideable**: Any attribute on a card can be hidden, graying it out and moving it to the back.

### 7.5 Smart Canvas (Grouping Layers)
Canvases hold cards and represent distinct grouping surfaces sitting on top of the master board:
- Default types: *Glass, Mirror, Vertical Swimlane, Horizontal Swimlane, Portfolio, Notebook (paginated pages with `---` page breaks), Collection, Folder, Gallery, Diary, Journal, Kanban Board Widget, Table, Calendar Widget, Charts/Diagrams* + *Add New Canvas Type*.
- **Multi-Canvas Management**: Up to 10 canvases can be loaded simultaneously. Users can swipe between them or jump directly using labeled custom pills (e.g. "Job Hunt", "Q4 Architecture").

### 7.6 Smart Boards (The Scope of Work)
The background work surface that hosts cards and canvases:
- Default types: *Kanban Board with Swimlanes, Monthly Calendar, Empty Whiteboard, Whiteboard with Swimlanes, Long Wood Bench, Workbench, Executive Desk, Round Table, Nightstand, Coffee Table* + *Add New Board Type*.

### 7.7 Smart Genie (The Pro/Elite AI Agent Assistant)
The intelligent co-pilot for the Smart Gen suite:
- **In-View Floating Assistant**: Operates like Canva/Figma AI assistant. Can be toggled on across Cards, Boards, and Canvas views as an in-view minimizable floating chat assistant.
- **Capabilities**:
  - Generates custom boards, canvases, and cards from conversational intent with zero friction.
  - Applies mass field edits across multiple selected cards.
  - Reconfigures card types (e.g. converting tasks to milestones) and refactors all historical instances.
  - Continuously extracts projects, tasks, and reminders from the main AI chat stream.
- **Tier Gates**:
  - *Free Tier*: Cards, Boards, and Canvas manual creation and editing.
  - *Pro Tier*: Smart Genie AI generation, mass edits, and automated calendar extraction.
  - *Elite Tier*: Custom agent attachment (users can attach specialized subagents to Smart Genie to execute autonomous scripts, code refactoring, or external API tasks).

---

## 8. Curated Multi-Model Modality Architecture

Every model category in Collider receives exhaustive, high-agency curation. Slots are filled only by models that earn their place through distinct capabilities, real API endpoints, and complete modality coverage. Placeholder slot-filling and dead endpoints are permanently banned.

### 8.1 Category 1: General Chat & Reasoning
*Focus: Conversational reasoning, deep synthesis, low latency, and zero-hallucination research.*

| Tier | Model | Provider / Slug | Why It Earns the Slot |
|---|---|---|---|
| **Pro** | **Gemini 2.5 Flash** | `google/gemini-2.5-flash` | Ultra-fast multimodal workhorse; near-zero latency for instant consensus generation. |
| **Pro** | **Claude 3.5 Haiku** | `anthropic/claude-3-5-haiku` | Rapid instruction following, crisp formatting, and efficient conversational synthesis. |
| **Pro** | **GPT-4o Mini** | `openai/gpt-4o-mini` | Reliable cost-efficient reasoning baseline with broad knowledge retrieval. |
| **Pro** | **DeepSeek V3** | `deepseek/deepseek-chat` | Uncensored open-weights reasoning with exceptional factual density at low cost. |
| **Elite** | **Gemini 2.5 Pro** | `google/gemini-2.5-pro` | Flagship 2M-token context window; deep research and multi-document synthesis. |
| **Elite** | **Claude 3.7 Sonnet (Thinking)** | `anthropic/claude-3-7-sonnet:thinking` | Industry standard in traceable chain-of-thought analysis and nuanced logical depth. |
| **Elite** | **o3 Mini High** | `openai/o3-mini-high` | Deterministic mathematical and logical problem solving with high reasoning effort. |
| **Elite** | **DeepSeek R1** | `deepseek/deepseek-r1` | Open reasoning model with unconstrained long-form analytical deductions. |

---

### 8.2 Category 2: Image Studio
*Focus: Photorealism, artistic styling, prompt typography, and zero-tap thumbnail comparison.*

| Tier | Model | Provider / Slug | Why It Earns the Slot |
|---|---|---|---|
| **Pro** | **FLUX.1 Schnell** | `black-forest-labs/flux-schnell` | Sub-second generative speed for real-time comparison preview thumbnails. |
| **Pro** | **SDXL Turbo** | `stabilityai/sdxl-turbo` | Single-step visual feedback for rapid iterative prompt refinement. |
| **Pro** | **Ideogram V2 Turbo** | `ideogram/ideogram-v2-turbo` | Low-cost accurate in-image typography and poster layouts. |
| **Pro** | **Recraft V3 Vector** | `recraft/recraft-v3-vector` | Clean vector graphic and icon generation matching visionOS design primitives. |
| **Elite** | **FLUX.1.1 Pro** | `black-forest-labs/flux-1.1-pro` | Flagship photographic skin texture, dynamic lighting, and cinematic optics. |
| **Elite** | **Midjourney V6.1** | `midjourney/v6.1` | Gold standard artistic aesthetic, atmospheric composition, and spatial depth. |
| **Elite** | **Imagen 3** | `google/imagen-3` | Supreme photorealism, natural language adherence, and low artifact rates. |
| **Elite** | **Ideogram V2 Flagship** | `ideogram/ideogram-v2` | Complex typographic compositions, signage, and high-fidelity text rendering. |

---

### 8.3 Category 3: Video Lab
*Focus: Cinematic camera motion, physical momentum, character consistency, and 60 FPS motion.*

| Tier | Model | Provider / Slug | Why It Earns the Slot |
|---|---|---|---|
| **Pro** | **Kling 1.5 Standard** | `kuaishou/kling-v1.5-standard` | Rapid short-clip video generation with strong physical momentum. |
| **Pro** | **Luma Dream Machine Fast** | `luma/dream-machine-fast` | Fast camera trajectory rendering and prompt-reactive spatial staging. |
| **Pro** | **Hailuo 01 Mini** | `minimax/video-01-mini` | Expressive human movement, emotional dynamics, and fast turnaround. |
| **Pro** | **Pika 2.0** | `pika/pika-2.0` | Creative visual effects, seamless loops, and stylistic motion. |
| **Elite** | **Runway Gen-3 Alpha** | `runway/gen-3-alpha` | Industry benchmark in cinematic lighting, complex camera controls, and temporal fidelity. |
| **Elite** | **Kling 1.5 Pro** | `kuaishou/kling-v1.5-pro` | 1080p full HD cinematic realism with high physical consistency. |
| **Elite** | **Hailuo 01 Flagship** | `minimax/video-01` | Photorealistic human action, intricate clothing dynamics, and cinematic depth. |
| **Elite** | **Sora Turbo** | `openai/sora-turbo` | Complex world simulation, multi-angle temporal persistence, and cinematic optics. |

---

### 8.4 Category 4: Audio & Music
*Focus: Coverage of the entire modality across Music generation, Raw Byte Stream TTS, and Conversational Voice.*

| Tier | Model | Provider / Slug | Call Shape | Why It Earns the Slot |
|---|---|---|---|---|
| **Pro** | **Lyria 3 Clip** | `google/lyria-3-clip-preview` | `chat/completions` + `audio` | Rapid ambient music clip entry point (\$0.04/30s clip). |
| **Pro** | **GPT-4o Mini TTS** | `openai/gpt-4o-mini-tts-2025-12-15` | `audio/speech` (raw byte stream) | Cheapest high-quality narration (\$0.60/M); reliable workhorse. |
| **Pro** | **Kokoro 82M** | `hexgrad/kokoro-82m` | `audio/speech` (raw byte stream) | 8 languages, 54 voices, \$0.62/M. Multilingual breadth at near-zero cost. |
| **Pro** | **GPT Audio Mini** | `openai/gpt-audio-mini` | `chat/completions` + `audio` | Conversational voice output with emotional inflection. |
| **Elite** | **Lyria 3 Pro** | `google/lyria-3-pro-preview` | `chat/completions` + `audio` | Full-length ambient soundtracks with structured composition. |
| **Elite** | **Gemini 3.1 Flash TTS** | `google/gemini-3.1-flash-tts-preview` | `audio/speech` (raw byte stream) | 70+ languages, 200+ inline emotion tags (`[whispers]`, `[laughs]`). |
| **Elite** | **Voxtral Mini TTS** | `mistralai/voxtral-mini-tts-2603` | `audio/speech` (raw byte stream) | Zero-shot voice cloning capability justifying elite status. |
| **Elite** | **GPT Audio** | `openai/gpt-audio` | `chat/completions` + `audio` | Flagship conversational audio with natural human cadence. |

---

### 8.5 Category 5: Coding & Software Agents
*Focus: Multi-file repository reasoning, automated bug fixing, architectural planning, and clean syntax.*

| Tier | Model | Provider / Slug | Why It Earns the Slot |
|---|---|---|---|
| **Pro** | **Claude 3.5 Haiku Code** | `anthropic/claude-3-5-haiku` | Rapid syntax completion, linter resolution, and unit test generation. |
| **Pro** | **DeepSeek V3 Code** | `deepseek/deepseek-chat` | Exceptional algorithmic accuracy across 80+ programming languages. |
| **Pro** | **Qwen 2.5 Coder 32B** | `qwen/qwen-2.5-coder-32b-instruct` | Compact coding champion for local script writing and refactoring. |
| **Pro** | **Codestral 2501** | `mistralai/codestral-2501` | Low-latency 256k context window for swift code fill-in-the-middle. |
| **Elite** | **Claude 3.7 Sonnet (Code Thinking)** | `anthropic/claude-3-7-sonnet:thinking` | World benchmark for complex multi-file architectural refactoring and logic proofs. |
| **Elite** | **o3 Mini High Code** | `openai/o3-mini-high` | Flawless competitive programming, algorithmic edge cases, and proofs. |
| **Elite** | **DeepSeek R1 Code** | `deepseek/deepseek-r1` | Autonomous debugging, self-correction traces, and execution synthesis. |
| **Elite** | **Qwen 2.5 Coder 72B** | `qwen/qwen-2.5-coder-72b-instruct` | Full repository synthesis, schema generation, and agentic orchestration. |

---

## 9. Universal Verification & Quality Gates

1. **User-Perspective Reality Over Clerical Checks**:
   - Internal compiler exit codes, typecheck passes, and test runner outputs have zero intrinsic customer value.
   - Deliverables are validated only when physically running, fully interactive, and visually confirmed under real user workflows.
2. **Visual Polish Standards**:
   - 100% adherence to Apple visionOS design specifications (0.5px specular rim highlights, optical squircle radii, single-pass optical glassmorphism, zero unstyled scrollbars).
3. **Dedicated Session Isolation**:
   - Every active preview iteration runs on its assigned dedicated session port with direct accessible preview links.

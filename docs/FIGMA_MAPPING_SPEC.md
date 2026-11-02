# Collider — Canonical Figma Architecture & Mapping Specification

> **Status**: Active & Authoritative  
> **Source Artifacts**: User Figma Teams Folder & VisionOS Community Component Kits  
> **Design Framework**: Apple visionOS Spatial Design System & High-Agency Glassmorphism  
> **Repository Path**: `docs/FIGMA_MAPPING_SPEC.md`

---

## 1. Master Team Folder & Ecosystem Reference

- **Figma Teams Folder**:  
  [Figma Teams Folder: Collider Spatial Workspace](https://www.figma.com/files/team/1640942759764734319/folder/606153351?fuid=1640942758085627402)
  - Contains project assets, custom icons, screen templates, and spatial canvas experiments.

---

## 2. Canonical Component Node Mappings

### 2.1 Theme Marketplace Template: 5-Track Soundscape View
- **Figma Source**:  
  [Vision OS Design System — Community: Node 417-15864](https://www.figma.com/design/YEuK4CL2uyECUhvGEcgCNS/Vision-OS-Design-System--Community---Copy-?node-id=417-15864&t=HGxWD7LNjZa9NQpD-4)
- **Component Role**: Theme Marketplace Detail View
- **Implementation File**: [`lib/features/theme/theme_marketplace_detail_view.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/theme/theme_marketplace_detail_view.dart)
- **Mapping Directives**:
  1. **Metadata Replacement**:
     - Album Title $\to$ **Theme Name** (e.g. *Aurora Drift 4K*, *Ember Fall 4K*, *Star Bridge*).
     - Artist Name $\to$ **Creator / Soundscape Author** (e.g. *Polaris Optical Labs • Dynamic Atmosphere*).
     - Album Cover Artwork $\to$ **4K Live Wallpaper Artwork** framed in a 104x104 squircle with a 1px specular light highlight and 28px glass backdrop.
     - Tier Badge $\to$ `✦ Elite 4K Live` or `Free Spatial Canvas`.
  2. **5-Track Ambient Soundscape Requirement**:
     - Every live wallpaper is packaged with a **curated set of exactly 5 ambient music tracks**.
     - Displayed in the visionOS music playlist row format:
       - Column 1: Track Number (`01`, `02`, `03`, `04`, `05`).
       - Column 2: Interactive Play/Pause button with animated real-time waveform bars.
       - Column 3: Track Title & Mood Descriptor chip (e.g. *Solar Wind Ionization* / *Atmospheric Glow*).
       - Column 4: Duration (`mm:ss`).
  3. **Actions**:
     - Primary: `Apply Theme` (instantly updates `_currentTheme`).
     - Secondary: `Preview` (live temporary atmospheric preview).
  4. **Swipe-Down Return Gesture**:
     - Swiping down vertically on the sheet triggers `onSwipeDownReturn()`, returning to the regular theme selector ([Node 69-1926](https://www.figma.com/design/jqsG6Hqkm7yws2iz607kim/Vision-Pro--Spatial-UI-Kit--Community-?node-id=69-1926)).
     - Top pill button `Selector` and circular `✕` close button provide two additional escape paths (Two-Escape Law).

---

### 2.2 Regular Theme Selector (Swipe-Down Return Target)
- **Figma Source**:  
  [Vision Pro Spatial UI Kit — Community: Node 69-1926](https://www.figma.com/design/jqsG6Hqkm7yws2iz607kim/Vision-Pro--Spatial-UI-Kit--Community-?node-id=69-1926&t=1oosbBuC4gLvobPS-4)
- **Component Role**: Horizontal Wallpaper Carousel & Live Preview Selector
- **Implementation File**: [`lib/features/wallpaper/widgets/windowless_theme_scroller.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/wallpaper/widgets/windowless_theme_scroller.dart)
- **Mapping Directives**:
  - Horizontal carousel of squircle wallpaper cards (`120px` width) with bottom title scrim.
  - Tier switcher pill (`Free` vs `✦ 4K Live`).
  - Dedicated `5 Curated Tracks >` button that immediately opens the detailed view (Node `417-15864`).
  - In-line action buttons: `Revert` and `Set Wallpaper`.

---

### 2.3 Centered Apps Selection Platter
- **Figma Source**:  
  [Vision OS Design System — Community: Node 2-6774](https://www.figma.com/design/YEuK4CL2uyECUhvGEcgCNS/Vision-OS-Design-System--Community---Copy-?node-id=2-6774&m=dev&t=e7CAGVGRU9jrcDVy-1)
- **Component Role**: Centered 7-Destination Apps Menu
- **Implementation File**: [`lib/features/apps/apps_popup_pane.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/apps/apps_popup_pane.dart)
- **Mapping Directives**:
  - Frameless frosted glass platter summoned to the center neutral area on Plane 4.
  - Bounded width (`maxWidth: 290px`) over a dimmed/blurred backdrop scrim.
  - Icons only (not full buttons) with clean text identifiers in *Instrument Sans*:
    1. `Smart Gen` (`Icons.inventory_2_rounded`)
    2. `Discover` (`Icons.explore_rounded`)
    3. `Themes` (`Icons.palette_rounded`)
    4. `Marketplace` (`Icons.shopping_bag_rounded`)
    5. `Files` (`Icons.folder_open_rounded`)
    6. `Audio` (`Icons.graphic_eq_rounded`)
    7. `Browser` (`Icons.language_rounded`)
  - Two-Escape Law: Scrim tap (Escape 1) or circular `✕` button (Escape 2).
  - Permanent ban on glitter/sparkle icons and marketing AI buzzwords.

---

### 2.4 Model Responses & Increasing Elevation (Conversation Stream)
- **Figma Source**:  
  [WeChat Vision OS — Community: Node 0-639](https://www.figma.com/design/OkuRCwJ6Hgz664K8YSe1zr/wechat-vision-os--Community-?node-id=0-639&t=L3jwyLijibMGTspH-4)  
  [Vision OS Design System — Community: Node 417-6826](https://www.figma.com/design/YEuK4CL2uyECUhvGEcgCNS/Vision-OS-Design-System--Community---Copy-?node-id=417-6826&t=HGxWD7LNjZa9NQpD-4)
- **Component Role**: Multi-Model Response Ticker Stack (The Conversation Stream)
- **Implementation Files**:  
  - [`lib/features/ticker/widgets/model_pill.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/ticker/widgets/model_pill.dart)  
  - [`lib/features/ticker/widgets/consensus_row.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/ticker/widgets/consensus_row.dart)  
  - [`lib/main.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/main.dart)
- **Mapping Directives**:
  - **Conversation Stream $\equiv$ Response Tickers Stack**: Confirmed authoritative design principle. No separate chat screen exists.
  - **Non-Interactive Surface**: Ticker container is non-repositionable and carries zero card chrome/border.
  - **Bounded Dimensions**: Max height 40% of screen height; max width equal to the nav bar's width.
  - **Untruncated 1-Line Summaries**: Removed all `...` ellipsis. Summaries scale down gracefully via `FittedBox(fit: BoxFit.scaleDown)` while preserving natural character densities.
  - **Increasing Elevation**: Message cards subtly increase elevation and specular luminance as they stack vertically.
  - **Tailed Speech Bubbles**: Chat bubbles in expanded accordions use directional tail geometry (`_TailedBubble`), not plain rounded rectangles.
  - **Faded Edge Masking**: Scrollable view uses vertical alpha gradient masking so cards fade smoothly into the wallpaper at the edges.

---

### 2.5 Message Bar & Broadcast Composer
- **Figma Source**:  
  [Apple VisionOS Apps Basic Design System: Node 1-240](https://www.figma.com/design/TReeWMHkw4GE5uKPhzvgMu/Apple-VisionOS-Apps---Basic-design-system--Community-?node-id=1-240&m=dev)  
  [Daily UI Chat Box Vision OS: Node 0-1](https://www.figma.com/design/uFFIq8Q3lGnIvKQ8DNHwj0/Daily-UI--02-10--%7C-Chat-box-%7C-Vision-OS--Community-?node-id=0-1&t=ccz1iFUrm40LoSqv-1)
- **Component Role**: Swipe-Summoned Broadcast Composer
- **Implementation File**: [`lib/features/prompt/floating_prompt.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/prompt/floating_prompt.dart)
- **Mapping Directives**:
  - Resting indicator with pull affordance (`▲`).
  - Swiping up on the nav bar summons the composer; swiping down tucks it away (`▼`).
  - Horizontal carousel of active model chips allowing multi-model query selection.
  - Translucent glass input field with integrated voice/attachment triggers.

---

### 2.6 Dedicated In-App Browser
- **Figma Source**:  
  [Apple VisionOS Apps Basic Design System: Node 1-71](https://www.figma.com/design/TReeWMHkw4GE5uKPhzvgMu/Apple-VisionOS-Apps---Basic-design-system--Community-?node-id=1-71&m=dev)
- **Component Role**: Single-Instance Model Browser
- **Implementation File**: [`lib/features/browser/screens/in_app_browser_sheet.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/browser/screens/in_app_browser_sheet.dart)
- **Mapping Directives**:
  - Only ONE browser instance active across the entire system at any given moment.
  - Multi-tab management, address bar, SSL indicator, and instant close.

---

### 2.7 Files & Content Library
- **Figma Source**:  
  [Vision Pro Spatial UI Kit: Node 71-7502](https://www.figma.com/design/jqsG6Hqkm7yws2iz607kim/Vision-Pro--Spatial-UI-Kit--Community-?node-id=71-7502&t=1oosbBuC4gLvobPS-4)
- **Component Role**: Spatial Files Drawer
- **Implementation File**: [`lib/features/files/screens/files_screen.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/files/screens/files_screen.dart)

---

### 2.8 Smart Gen Kanban & Interactive Boards
- **Figma Sources**:  
  [Nimo Spatial OS Design System: Node 2012-201531](https://www.figma.com/design/gQWsPhZJQjqFPgaJQDds9p/Nimo-Spatial-OS-Design-System--Community-?node-id=2012-201531&t=ylAJcEw0hRiv2lFS-4)  
  [Vision Pro UI Kit Work in Progress: Node 30-75](https://www.figma.com/design/BLoCtbUcCpX32i0Fh7Y0ld/Vision-Pro-UI-Kit--Work-in-Progress--1.0.4--Community-?node-id=30-75&t=mmEzEDXaPKMV6Kat-4)  
  [Spatial UI UX: Node 59-170](https://www.figma.com/design/IZidmdk7e3KXXGqdbtUGWF/Spatial-UI-UX--Community-?node-id=59-170&t=7JL2JHQwBuoD9mWc-4)
- **Component Role**: Smart Gen Autonomous Suite (Projects, Tasks, Reminders, Artifacts)
- **Implementation File**: [`lib/features/smartgen/screens/smartgen_screen.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/features/smartgen/screens/smartgen_screen.dart)

---

### 2.9 Frosted Micro UI Kit & Light Emittance Icons
- **Figma Source**:  
  [Frosted Micro UI Kit — Minimal Glass Components: Node 1-69](https://www.figma.com/design/hPpbxx4ICpK2a3WPJ9jZjt/Frosted-Micro-UI-Kit-%E2%80%94-Minimal-Glass-Components--Community-?node-id=1-69&t=apzuVIhyDrV2FESY-1)
- **Component Role**: Specular Rim Lighting & Micro Glass Tokens
- **Implementation File**: [`lib/core/theme/vision_glass.dart`](file:///c:/Users/D/Documents/collider_flutter/lib/core/theme/vision_glass.dart)

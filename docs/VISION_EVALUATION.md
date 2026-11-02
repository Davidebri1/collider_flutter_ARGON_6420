# Collider Vision — screen evaluation and implementation

Kit: `lib/core/vision/` (`vision_tokens.dart`, `vision_kit.dart`, `work_surface.dart`). Screenshots: `_ds_work/before/` and `_ds_work/after/` (402×874).

| Screen | Reference node | Before | After |
|---|---|---|---|
| Response stack | 417:6826, 0:639 | Pills with left bars; consensus summary shrunk to unreadable size | Comment-card layout: avatar, name, time, thesis, tool circles; elevation rises up the stack; summary wraps |
| Composer | 1:240 | Tap-to-edit capsule opening a second modal | Message capsule: models circle, inline field, send circle |
| Dock | 0:639 | Custom capsule | Kit ornament, 44px circles |
| Rail | 71:7502, 97:34752 | Drawn over every modal | Kit ornament rail; hidden while a focused overlay is open |
| Contextual panel | 97:34752 | Dense form of mixed controls | Menu panel: sidebar rows, recessed segmented, chips, search, fading list |
| Apps | 2:6774 | Icons on a platter over a black-out | Icons float on the dimmed environment, offset rows, no platter |
| Settings | 417:8552, 130:75006 | Toggle list; Upgrade/Skills/Files had no entry | Account window: close top-left, grouped toggles, rows to Tiers, Skills, Files |
| Unsaved-changes | 130:75006 | Side-by-side buttons | Alert: icon, title, message, stacked actions |
| History, model history | 417:8104 | Generic dark box | Notes list window: large title, search capsule, fading cells |
| Models & Ladder | 417:6219 | Rows with left bars, Switch, extra Done | Library list: chips, search, avatar rows, kit toggles |
| Theme gallery | 69:1926 | Card over the stack, colliding with rail and ticker | Windowless: segmented, title, widening thumbnail strip, capsules; stack hidden |
| Music | 417:1777 | Plain list with dead play icons | Cover-flow with transport ornament |
| Message zoom | 417:1777 | Floating text, black-out | Focus card + action ornament |
| Smart Gen | 2012:201531, 30:75, 59:170 | Single column labelled Kanban; footer text | Work surface: priority lanes, in-place title edit, segmented ornament |
| Discover | 417:6219, 203:5891 | Card list; placeholder gallery icons | Hero with Use Prompt, shelf, gallery tiles, segmented ornament |
| Files | 71:7502 | Switch list with two chip rows and footer | Tile grid with select circles, model chips / sidebar, type ornament |
| Browser | 1:71 | Neon cyan borders, in-window toolbar | Address-bar ornament above the page window |
| Consensus | — | Dark window with header/footer text | Work window, close circle, title |
| Tiers, Skills | 417:8552 | Footer text, Done buttons | Account-style windows |
| Premium Theme Market, Theme detail | 1:3, 149:1202, 417:15864 | — | Unchanged |

Global: overlays use one kit scrim (black 35% + 20 blur) instead of stacked 48–78% black-outs; nested blurs inside windows removed; footers, redundant Done buttons and descriptive subtitles removed.

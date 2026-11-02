# Made by Claude (2026-10-23). Round 24: whatever a person types stays as they left it, everywhere.
# David, 23 Oct: "make sure the fix for draft deletion is handled everywhere in app. smart gen, edit fields, anywhere
# users act, leave it as they left it." Every text box now keeps its words in Drafts (lib/core/drafts.dart) instead of
# inside itself, so closing or covering its view never loses them. A SmartGen card being edited is saved as it is typed.
# And the resting workspace (ticker and composer) is no longer taken off the screen when a window opens over it: it is
# hidden and paused, then shown again as it was ("just hide the element and pause/stop the processing ... then resume").
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
LIB = ROOT / "lib"

# file, variable, draft id ('{model}' is the conversation's model)
BOXES = [
    ("features/browser/screens/in_app_browser_sheet.dart", "_addr", "browser.address"),
    ("features/composer/tucked_global_composer.dart", "_promptCtrl", "composer.tucked"),
    ("features/drawers/history_drawer.dart", "_searchCtrl", "history.search"),
    ("features/drawers/history_pane.dart", "_search", "history.pane.search"),
    ("features/drawers/history_pane.dart", "_ctrl", "history.pane.reply"),
    ("features/drawers/wallpaper_drawer.dart", "_searchCtrl", "wallpaper.search"),
    ("features/files/screens/files_screen.dart", "_search", "files.search"),
    ("features/nav/contextual_side_nav.dart", "_chatSearchCtrl", "sidenav.search"),
    ("features/smartgen/screens/smartgen_screen.dart", "_searchCtrl", "smartgen.search"),
    ("features/smartgen/screens/smartgen_screen.dart", "_newCtrl", "smartgen.new"),
    ("features/theme/premium_theme_market_view.dart", "_c", "premium.search"),
    ("features/ticker/widgets/conversation_view.dart", "_search", "conversation.search:{model}"),
    ("features/ticker/widgets/local_history_pane.dart", "_searchCtrl", "localhistory.search"),
]

for rel, var, key in BOXES:
    p = LIB / rel
    s = p.read_text(encoding="utf-8")
    pat = re.compile(r"(\s*)(final|late final) (TextEditingController |)" + re.escape(var) + r" = TextEditingController\(\);")
    m = pat.search(s)
    if not m:
        sys.exit(f"{rel}: no declaration of {var}")
    if "{model}" in key:
        decl = f"{m.group(1)}late final TextEditingController {var} = Drafts.text('{key.replace('{model}', '${widget.item.modelDef.id}')}');"
    else:
        decl = f"{m.group(1)}final TextEditingController {var} = Drafts.text('{key}');"
    s = s[:m.start()] + decl + s[m.end():]
    # the box no longer owns its words, so it must not discard them when it goes
    s = re.sub(r"\n\s*" + re.escape(var) + r"\.dispose\(\);", "", s)
    if "core/drafts.dart" not in s:
        depth = rel.count("/")
        imp = "import '" + "../" * depth + "core/drafts.dart';\n"
        i = s.index("\nimport ") + 1 if not s.startswith("import ") else 0
        s = s[:i] + imp + s[i:]
    p.write_text(s, encoding="utf-8")
    print("kept:", rel, var)

# SmartGen: the card being edited is saved as it is typed
p = LIB / "features/smartgen/screens/smartgen_screen.dart"
s = p.read_text(encoding="utf-8")
old = "              onChanged: (v) => c.title = v,"
assert s.count(old) == 1
s = s.replace(old, "              onChanged: (v) => widget.store.update(c, title: v), // kept as typed (Claude, 2026-10-23)")
p.write_text(s, encoding="utf-8")
print("smartgen card saved as typed")

# The resting workspace: hidden and paused under a window, never removed
p = LIB / "main.dart"
s = p.read_text(encoding="utf-8")
old = """          if (!_browserOpen && !(isMobile && _isMobileSideNavOpen) && !const {'premium', 'themes', 'apps', 'settings', 'smartgen', 'market', 'files', 'consensus'}.contains(_activeDrawer))
          Positioned.fill("""
new = """          // The resting workspace stays where it is under any window: hidden and paused (no drawing, no animation), then
          // shown again exactly as it was. It used to be taken off the screen, and everything typed in it went too.
          // (Claude, 2026-10-23)
          Positioned.fill("""
assert s.count(old) == 1, "plane 1 condition"
s = s.replace(old, new)
# wrap the plane's child: find the SafeArea that follows and wrap it with Visibility + TickerMode
old2 = """            bottom: 78,
            child: SafeArea("""
new2 = """            bottom: 78,
            child: Builder(builder: (context) {
              final resting = !_browserOpen && !(isMobile && _isMobileSideNavOpen) &&
                  !const {'premium', 'themes', 'apps', 'settings', 'smartgen', 'market', 'files', 'consensus'}.contains(_activeDrawer);
              return Visibility(
                visible: resting,
                maintainState: true,
                child: TickerMode(
                  enabled: resting,
                  child: SafeArea("""
assert s.count(old2) == 1, "plane 1 child"
s = s.replace(old2, new2)
old3 = """                        onTuck: () => setState(() => _isComposerSummoned = false),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // ================= PLANE 2: APPS POPUP PANE ================="""
new3 = """                        onTuck: () => setState(() => _isComposerSummoned = false),
                      ),
                    ),
                  ],
                ),
              ),
            ),
                ),
              );
            }),
          ),

          // ================= PLANE 2: APPS POPUP PANE ================="""
assert s.count(old3) == 1, "plane 1 end"
s = s.replace(old3, new3)
p.write_text(s, encoding="utf-8")
print("main.dart: resting workspace hidden and paused, not removed")

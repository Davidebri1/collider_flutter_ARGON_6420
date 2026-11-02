# Made by Claude (2026-10-21). Round 8: a phone's shape and layouts that fit it.
# David, 21 Oct: "Yeah we need proper mobile aspect ratio. And responsive design to match".
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for: {old[:80]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


# ---- Collider.exe: the window is a phone, iPhone 16 Pro's 402 x 874 points, scaled down whole on a short screen ----
edit("tools/collider_app.py", [
    ("""        width, height = min(440, int(area_w / scale)), min(940, int(area_h / scale))
""",
     """        # A phone's shape, never cut to fit: iPhone 16 Pro's screen (402 x 874 points) under the window's title bar,
        # made smaller as a whole when the screen is shorter (Claude, 2026-10-21).
        bar = 32
        inner = min(874, int(area_h / scale) - bar - 24)
        width, height = round(inner * 402 / 874), inner + bar
"""),
])

# ---- Files on a phone: the buttons in one row, the name large under them, then search (as iPhone's Files) ----
edit("lib/features/files/screens/files_screen.dart", [
    ("""          ? Column(mainAxisSize: MainAxisSize.min, children: [
              Row(children: [nav, SizedBox(width: 15 * _u), Expanded(child: name), SizedBox(width: 15 * _u), actions]),
              SizedBox(height: 20 * _u),
              search,
            ])""",
     """          ? Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
              Row(children: [nav, const Spacer(), actions]),
              if (title.isNotEmpty) ...[
                SizedBox(height: 10 * _u),
                Text(title, maxLines: 1, overflow: TextOverflow.ellipsis, style: _N.text(22, FontWeight.w700, _N.title)),
              ],
              SizedBox(height: 14 * _u),
              search,
            ])"""),
])

# ---- History on a phone: the width of the other panes, not the screen's ----
edit("lib/features/drawers/history_pane.dart", [
    ("""    final listW = wide ? 300.0 : (size.width - 32).clamp(260.0, 380.0);""",
     """    final listW = wide ? 300.0 : VOverlay.toolWidth(context);"""),
])

# ---- Browser on a phone: Safari's layout ----
B = ROOT / "lib/features/browser/screens/in_app_browser_sheet.dart"
s = B.read_text(encoding="utf-8")
a = s.index("    return Stack(\n      children: [\n        Dialog(")
z = s.index("  /// Shares the page's address")
s = s[:a] + (ROOT / "dev/draft/browser_build_tail.dart").read_text(encoding="utf-8") + s[z:]
if "import 'dart:math' as math;" not in s:
    sys.exit("browser: dart:math not imported")
B.write_text(s, encoding="utf-8")
print("edited in_app_browser_sheet.dart")

# ---- Documents on a phone: the tools in one row that scrolls sideways, as on iPhone's Pages ----
edit("dev/editor/src/style.css", [
    (""".name:focus { outline: none; background: rgba(255,255,255,.08); }""",
     """.name:focus { outline: none; background: rgba(255,255,255,.08); }
@media (max-width: 600px) {
  .bar { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; padding-right: 44px; -webkit-overflow-scrolling: touch; }
  .bar::-webkit-scrollbar { display: none; }
  .bar > * { flex-shrink: 0; }
  .name { flex: 0 0 150px; min-width: 150px; }
}"""),
])

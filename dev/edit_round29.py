# Made by Claude (2026-10-23). Round 29: the detail view keeps to the work column (the ticker's width and place) and its
# actions sit right under the content, as the composer sits under the ticker. David: "the action context should be
# right underneath the content ... stop treating the screen like an open playground. see the zones before acting."
import re

p = "lib/core/vision/detail_view.dart"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


rep("""  /// How wide the content may be.
  final double maxWidth;
""", """  /// Pictures: the media column, as wide as the pictures' ticker.
  final bool media;

  /// The work column: as wide as the ticker window it opens from (phone 300, wider screens 480; pictures 360 and 780).
  static double zoneWidth(BuildContext context, {bool media = false}) {
    final phone = MediaQuery.sizeOf(context).width < 768;
    return phone ? (media ? 360 : 300) : (media ? 780 : 480);
  }

  /// The tallest the content may be: the work column above the dock, less the actions under it.
  static double zoneHeight(BuildContext context) {
    final m = MediaQuery.of(context);
    return m.size.height - m.padding.top - m.padding.bottom - 16 - 92 - 74;
  }
""")
rep("""    this.maxWidth = 560,""", """    this.media = false,""")

a = s.index("          SafeArea(\n            child: Padding(\n              // the actions end just above the dock")
b = s.index("        ]);\n      },\n    );\n  }\n}")
s = s[:a] + """          // The content and its actions are one group in the work column, standing where the ticker and the composer
          // stand: the actions right under what they act on (Claude, 2026-10-23; they were pinned to the screen's foot,
          // far from short content, and the content took the screen's width).
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(0, VSpace.md, 0, 92),
              child: Align(
                alignment: Alignment.bottomCenter,
                child: SizedBox(
                  width: DetailView.zoneWidth(context, media: widget.media),
                  child: Opacity(
                    opacity: v,
                    child: Transform.translate(
                      offset: Offset(0, 14 * (1 - v)),
                      child: Column(mainAxisSize: MainAxisSize.min, children: [
                        Flexible(child: Transform.scale(scale: 0.94 + 0.06 * v, child: widget.child)),
                        const SizedBox(height: VSpace.sm),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [for (final a in all) _ActionButton(a)],
                        ),
                      ]),
                    ),
                  ),
                ),
              ),
            ),
          ),
""" + s[b:]
rep("""        child: SizedBox(
          width: 60,""", """        child: SizedBox(
          width: 50, // six fit the phone's column""")
open(p, "w", encoding="utf-8").write(s)

# callers: no widths of their own
for f, pats in {
    "lib/main.dart": ["                maxWidth: 560,\n"],
    "lib/features/ticker/widgets/message_zoom_overlay.dart": ["      maxWidth: 520,\n"],
    "lib/features/media/picture_viewer.dart": ["      maxWidth: 900,\n"],
}.items():
    t = open(f, encoding="utf-8").read()
    for x in pats:
        assert t.count(x) == 1, (f, x)
        t = t.replace(x, "      media: true,\n" if "picture" in f else "")
    open(f, "w", encoding="utf-8").write(t)

# message: no height cap of its own beyond the column
f = "lib/features/ticker/widgets/message_zoom_overlay.dart"
t = open(f, encoding="utf-8").read()
t = t.replace("        constraints: BoxConstraints(maxHeight: size.height * 0.62),", "        constraints: BoxConstraints(maxHeight: DetailView.zoneHeight(context)),")
t = t.replace("    final size = MediaQuery.of(context).size;\n", "")
open(f, "w", encoding="utf-8").write(t)

# conversation: the column's height
f = "lib/main.dart"
t = open(f, encoding="utf-8").read()
x = "                  constraints: BoxConstraints(maxHeight: MediaQuery.sizeOf(context).height * 0.66),"
assert t.count(x) == 1
t = t.replace(x, "                  constraints: BoxConstraints(maxHeight: DetailView.zoneHeight(context)),")
open(f, "w", encoding="utf-8").write(t)

# picture: the pages as tall as the picture at the column's width, so the actions sit under it
f = "lib/features/media/picture_viewer.dart"
t = open(f, encoding="utf-8").read()
x = "      child: PageView.builder("
assert t.count(x) == 1
t = t.replace(x, """      child: SizedBox(
        height: math.min(DetailView.zoneWidth(context, media: true) / p.aspect, DetailView.zoneHeight(context)),
        child: PageView.builder(""")
x = """              : _picture(widget.pictures[i]),
        ),
      ),
    );"""
assert t.count(x) == 1
t = t.replace(x, """              : _picture(widget.pictures[i]),
        ),
      ),
      ),
    );""")
t = t.replace("import 'package:material_ui/material_ui.dart';\n", "import 'dart:math' as math;\n\nimport 'package:material_ui/material_ui.dart';\n", 1)
open(f, "w", encoding="utf-8").write(t)

# files: a held text file keeps to the column's height
f = "lib/features/files/screens/files_screen.dart"
t = open(f, encoding="utf-8").read()
x = "              constraints: BoxConstraints(maxHeight: size.height * 0.6),"
assert t.count(x) == 1
t = t.replace(x, "              constraints: BoxConstraints(maxHeight: DetailView.zoneHeight(ctx)),")
open(f, "w", encoding="utf-8").write(t)
print("round 29 applied")

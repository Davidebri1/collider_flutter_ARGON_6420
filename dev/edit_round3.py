# Made by Claude (2026-10-20). One-time edits, David's answers of 20 Oct:
#  - video skips back to 10 s ("video skips should be 10 seconds")
#  - the browser starts on Google ("browser start page is supposed to be google")
#  - every control has at least Apple's minimum touch target, 44 x 44 points ("make sure everything is at the minimum
#    required size"); a control drawn smaller keeps its look and gets the room around it
import os, re
root = os.path.join(os.path.dirname(__file__), "..")


def edit(rel, pairs):
    p = os.path.join(root, rel)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        if s.count(a) != 1:
            raise SystemExit(f"{rel}: expected one of {a!r}, found {s.count(a)}")
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s)


edit("lib/core/media/video_window.dart", [
    ("_Skip15(forward: false, onTap: () => _skip(-15)),", "_Plain(icon: Icons.replay_10_rounded, onTap: () => _skip(-10)),"),
    ("_Skip15(forward: true, onTap: () => _skip(15)),", "_Plain(icon: Icons.forward_10_rounded, onTap: () => _skip(10)),"),
])
p = os.path.join(root, "lib/core/media/video_window.dart")
s = open(p, encoding="utf-8").read()
cut = s.index("\n/// The reference's 15-second skips")
open(p, "w", encoding="utf-8", newline="").write(s[:cut] + "\n")

edit("lib/features/browser/screens/in_app_browser_sheet.dart", [
    ("  static const _homePage = 'https://html.duckduckgo.com/html/';\n  static const _search = 'https://html.duckduckgo.com/html/?q=';",
     "  static const _homePage = 'https://www.google.com/';\n  static const _search = 'https://www.google.com/search?q=';"),
])
edit("lib/main.dart", [
    ("BrowserTab(id: 'user_default', title: 'Search', url: 'https://html.duckduckgo.com/html/', isUserControlling: true),",
     "BrowserTab(id: 'user_default', title: 'Search', url: 'https://www.google.com/', isUserControlling: true),"),
])

# Touch targets: every VPress control is at least 44 x 44; what is drawn smaller sits centred in that room.
edit("lib/core/vision/vision_kit.dart", [
    ("          child: CustomPaint(foregroundPainter: _GlowPainter(_at, _glow), child: widget.child),\n        ),\n      ),\n    );",
     "          child: CustomPaint(foregroundPainter: _GlowPainter(_at, _glow), child: widget.child),\n        ),\n      ),\n    );\n"
     "    // Apple's minimum touch target, 44 x 44 points: a smaller control keeps its look and gets the room around it.\n"
     "    w = ConstrainedBox(\n"
     "      constraints: const BoxConstraints(minWidth: 44, minHeight: 44),\n"
     "      child: Center(widthFactor: 1, heightFactor: 1, child: w),\n"
     "    );"),
])
print("ok")

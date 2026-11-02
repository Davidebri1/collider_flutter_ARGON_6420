# Made by Claude (2026-10-23). Round 25: glass shows what is behind it.
# David, 23 Oct: "isnt glass material supposed to be transparent? i dont notice any transparency."
# Cause: a 50-point blur smears the room behind into one even grey, and a white layer of up to 30% on top finishes it
# off, so every pane read as a grey card. Apple's glass blurs the room but keeps its light and colour (vibrancy: the
# blurred room's colours are strengthened, not washed out). Now: a 28-point blur, the room's colours lifted (saturation
# 1.6) inside the blur, and the white layer lighter (10% panes, 18% bars, menus and alerts, 14% windows).
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for {old[:70]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("lib/core/vision/vision_tokens.dart", [
    ("static const Color glassElevated = Color(0x4DF2F5F9); // bars and ornaments: a cool white 30%",
     "static const Color glassElevated = Color(0x2EF2F5F9); // bars and ornaments: a cool white 18% (was 30%; Claude, 2026-10-23)"),
    ("static const Color glassModal = Color(0x4DF2F5F9); // alerts and menus: a cool white 30%",
     "static const Color glassModal = Color(0x2EF2F5F9); // alerts and menus: a cool white 18% (was 30%; Claude, 2026-10-23)"),
    ("static const Color glassWork = Color(0x38F2F5F9); // windows: a cool white 22%, the content layer",
     "static const Color glassWork = Color(0x24F2F5F9); // windows: a cool white 14%, the content layer (was 22%; Claude, 2026-10-23)"),
])
edit("lib/core/vision/vision_kit.dart", [
    ("""  // Background blur 100 in the nodes is a 50 px blur.
  double get blur => 50;""",
     """  // The room behind, blurred but still there (Claude, 2026-10-23; was 50, which left a flat grey).
  double get blur => 28;"""),
    ("""          filter: ImageFilter.blur(sigmaX: material.blur, sigmaY: material.blur),
          child: CustomPaint(
            foregroundPainter: VGlassStroke(radius: radius, pane: material.pane),""",
     """          // vibrancy: the blurred room's own colours, lifted, as Apple's glass keeps them
          filter: ImageFilter.compose(outer: const ColorFilter.matrix(_vibrancy), inner: ImageFilter.blur(sigmaX: material.blur, sigmaY: material.blur)),
          child: CustomPaint(
            foregroundPainter: VGlassStroke(radius: radius, pane: material.pane),"""),
    ("""/// One-pass glass surface: blur + material fill + hairline + specular rim.""",
     """/// Saturation 1.6 (Claude, 2026-10-23): the colour of what is behind the glass comes through it.
const List<double> _vibrancy = <double>[
  1.4724, -0.4288, -0.0436, 0, 0,
  -0.1276, 1.1712, -0.0436, 0, 0,
  -0.1276, -0.4288, 1.5564, 0, 0,
  0, 0, 0, 1, 0,
];

/// One-pass glass surface: blur + material fill + hairline + specular rim."""),
])

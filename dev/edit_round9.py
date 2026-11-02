# Made by Claude (2026-10-21). Round 9: what did not fit the smallest phone (iPhone SE, 375 x 667).
#  - Files: six buttons and their gaps were wider than the window; Close was cut at the right edge. On a phone the
#    gaps go (each button already has its 44-point target around it, which spaces them).
#  - Smart Gen: the bar above the window held the name, four modes and Close; on a phone it ran past its right edge,
#    cutting Close and hiding the name. The side rail beside the window holds the same four modes on a phone, so the
#    bar there holds the name and Close.
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new, n in pairs:
        if s.count(old) != n:
            sys.exit(f"{rel}: expected {n} match(es) for: {old[:80]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


FS = "lib/features/files/screens/files_screen.dart"
p = ROOT / FS
s = p.read_text(encoding="utf-8")
a = s.index("  Widget _titleBar(bool compact) {")
z = s.index("    final search = VRecessed(", a)
part = s[a:z]
n = part.count("const SizedBox(width: 6),")
if n != 4:
    sys.exit(f"files title bar: expected 4 gaps, found {n}")
part = part.replace("const SizedBox(width: 6),", "SizedBox(width: compact ? 0 : 6),")
p.write_text(s[:a] + part + s[z:], encoding="utf-8")
print("edited", FS)

edit("lib/features/smartgen/screens/smartgen_screen.dart", [
    ("                _navbar(),\n", "                _navbar(isMobile),\n", 1),
    ("  Widget _navbar() => VGlass(", "  Widget _navbar(bool isMobile) => VGlass(", 1),
    ("""            for (final (id, label) in const [
              ('boards', 'Boards'),""",
     """            // On a phone the side rail holds these four (Claude, 2026-10-21).
            if (!isMobile)
            for (final (id, label) in const [
              ('boards', 'Boards'),""", 1),
])

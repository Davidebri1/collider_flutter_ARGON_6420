# Made by Claude (2026-10-23). Round 31: text at 11 points, Apple's minimum, everywhere but headers. David: "the minimum
# font size is 11 ... i understand hierarchies for headers. but outside of that, you have no reason to go above."
# Headers keep their sizes (VType headline 17 and up, and any size 15 and over that is a title). Body, callout,
# footnote and caption, and every fixed size from 9 to 14, become 11.
import glob, re

changed = {}


def save(p, s, n):
    if n:
        open(p, "w", encoding="utf-8").write(s)
        changed[p] = changed.get(p, 0) + n


# the type scale: body (15) and callout/footnote (13) to 11
p = "lib/core/vision/vision_tokens.dart"
s = open(p, encoding="utf-8").read()
n = 0
for a, b in [("  static const double sm = 13;", "  static const double sm = 11; // 13 until 2026-10-23 (Claude): 11 is the size outside headers"),
             ("  static const double md = 15;", "  static const double md = 11; // 15 until 2026-10-23 (Claude): 11 is the size outside headers")]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
    n += 1
save(p, s, n)

# the ticker's line: 11 on a 15-point line; two lines of it are 30 points
p = "lib/core/vision/vision_kit.dart"
s = open(p, encoding="utf-8").read()
a = "  static TextStyle get rowStyle => VType.callout(weight: FontWeight.w500).copyWith(fontSize: 12, height: 17 / 12);"
assert s.count(a) == 1
s = s.replace(a, "  static TextStyle get rowStyle => VType.callout(weight: FontWeight.w500).copyWith(fontSize: 11, height: 15 / 11);")
save(p, s, 1)
for p in ["lib/features/ticker/widgets/model_pill.dart", "lib/features/ticker/widgets/consensus_row.dart"]:
    s = open(p, encoding="utf-8").read()
    k = s.count("height: 34,") + s.count(": 34,\n")
    s = s.replace("? null : 34,", "? null : 30,").replace("              height: 34,", "              height: 30,")
    s = s.replace("margin: const EdgeInsets.symmetric(vertical: 4), // two of them fill the summary's two lines",
                  "margin: const EdgeInsets.symmetric(vertical: 3), // two of them fill the summary's two lines")
    s = s.replace("height: 17 / 12,", "height: 15 / 11,")
    save(p, s, k)

# every fixed size from 9 to 14 (not 11) to 11
num = re.compile(r"(fontSize:\s*)(\d+(?:\.\d+)?)(?![\d.])")
ntext = re.compile(r"(_N\.text\()(\d+(?:\.\d+)?)(,)")
for p in glob.glob("lib/**/*.dart", recursive=True):
    p = p.replace("\\", "/")
    s = open(p, encoding="utf-8").read()
    k = 0

    def f(m):
        global k
        v = float(m.group(2))
        if 9 <= v <= 14 and v != 11:
            return m.group(1) + "11" + (m.group(3) if m.lastindex >= 3 else "")
        return m.group(0)

    s2, k1 = num.subn(lambda m: f(m), s)
    s2 = num.sub(lambda m: f(m), s)
    k1 = sum(1 for m in num.finditer(s) if 9 <= float(m.group(2)) <= 14 and float(m.group(2)) != 11)
    s3 = ntext.sub(lambda m: f(m), s2)
    k2 = sum(1 for m in ntext.finditer(s2) if 9 <= float(m.group(2)) <= 14 and float(m.group(2)) != 11)
    save(p, s3, k1 + k2)

# the zoomed message is body text, not a title
p = "lib/features/ticker/widgets/message_zoom_overlay.dart"
s = open(p, encoding="utf-8").read()
if "fontSize: 15, height: 1.5" in s:
    s = s.replace("fontSize: 15, height: 1.5", "fontSize: 11, height: 1.5")
    save(p, s, 1)
for p, n in sorted(changed.items()):
    print(n, p)
print("total", sum(changed.values()))

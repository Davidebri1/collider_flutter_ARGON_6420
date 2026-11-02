# Made by Claude (2026-10-23). Round 27b: the consensus row's summary gets two lines, shown whole, the score leading it.
p = "lib/features/ticker/widgets/consensus_row.dart"
s = open(p, encoding="utf-8").read()
a = s.index("            // The score leads the line it belongs to")
b = s.index("            if (isGenerating)")
new = """            // The score leads the words it belongs to; it does not take a line of its own. Two lines are kept for them
            // from the start and the summary shows whole (Claude, 2026-10-23; was one line, shrunk to fit).
            SizedBox(
              height: 34,
              child: AnimatedSwitcher(
                duration: VMotion.base,
                layoutBuilder: (cur, prev) => Stack(alignment: Alignment.topLeft, children: [...prev, if (cur != null) cur]),
                child: SizedBox(
                  key: ValueKey('$score|$summary'),
                  width: double.infinity,
                  child: Text.rich(
                    TextSpan(children: [
                      TextSpan(
                        text: agree == null ? '\\u2013/\\u2013' : score,
                        style: VType.caption(color: ink, weight: FontWeight.w700).copyWith(
                          fontSize: 12,
                          height: 17 / 12,
                          shadows: agree == null
                              ? null
                              : [Shadow(color: ink.withValues(alpha: 0.9), blurRadius: 10), Shadow(color: ink.withValues(alpha: 0.5), blurRadius: 3)],
                        ),
                      ),
                      if (summary.isNotEmpty) TextSpan(text: '   $summary', style: VOneLine.rowStyle),
                    ]),
                    maxLines: 2,
                    overflow: TextOverflow.fade,
                  ),
                ),
              ),
            ),
"""
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("round 27b applied")

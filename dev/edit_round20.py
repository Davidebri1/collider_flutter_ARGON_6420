# Made by Claude (2026-10-21). Round 20: a summary's conversation opens attached under it, in a window that keeps its
# size. David, 21 Oct: going from the ticker summary to the expanded view "is not only not an expanded window (where the
# expanded pane attaches to the original message), but it resizes the pane ... we lost the summaries in the process."
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
p = ROOT / "lib" / "main.dart"
s = p.read_text(encoding="utf-8")

start = s.index("    // Expanded: that model's conversation, closeable.")
end = s.index("    if (ThemeBlurCache.instance.activeAssetPath != _currentTheme.assetPath) {", start)
conv = s[start:end]
s = s[:start] + s[end:]
anchor = "    // Collapsed: the consensus row pinned on top, then one row per model."
assert s.count(anchor) == 1
conv = conv.replace("    // Expanded: that model's conversation, closeable.\n",
                    "    // Expanded: that model's conversation, closeable, opened under its own summary (see the rows below).\n"
                    "    final convHeight = (MediaQuery.sizeOf(context).height * 0.36).clamp(240.0, 420.0);\n")
conv = conv.replace("            key: ValueKey('conv-${openItem.modelDef.id}'),\n            item: openItem,\n",
                    "            key: ValueKey('conv-${openItem.modelDef.id}'),\n            item: openItem,\n            attached: true,\n")
s = s.replace(anchor, conv + anchor)


def one(old, new):
    global s
    if s.count(old) != 1:
        sys.exit(f"expected one match for {old[:70]!r} (found {s.count(old)})")
    s = s.replace(old, new)


# the window keeps one size: the same width collapsed and opened
one("""                              ? (media ? 360.0 : (openItem != null ? 300.0 : 260.0)) // the pictures' toolbar fits whole (Claude, 2026-10-21)
                              : (openItem != null || media ? 780.0 : 480.0),""",
    """                              ? (media ? 360.0 : 300.0) // one width, opened or not; the pictures' toolbar fits whole (Claude, 2026-10-21)
                              : (media ? 780.0 : 480.0),""")
one("""                              : openItem == null
                              ? rows
                              : (isMobile
                                  ? conversation
                                  : Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [SizedBox(width: 260, child: rows), const SizedBox(width: 13), Expanded(child: conversation)],
                                    )),""",
    """                              : rows,""")
one("""                      constraints: BoxConstraints(maxWidth: isMobile ? 260.0 : 480.0),""",
    """                      constraints: BoxConstraints(maxWidth: isMobile ? 300.0 : 480.0),""")
# the side rail no longer has to step aside: the window does not widen
one("""    final railVisible = _railVisible && !(isMobile && openItem != null);""",
    """    final railVisible = _railVisible;""")
p.write_text(s, encoding="utf-8")
print("edited main.dart")

c = ROOT / "lib" / "features" / "ticker" / "widgets" / "conversation_view.dart"
t = c.read_text(encoding="utf-8")


def cone(old, new):
    global t
    if t.count(old) != 1:
        sys.exit(f"conversation_view: expected one match for {old[:70]!r} (found {t.count(old)})")
    t = t.replace(old, new)


cone("""  final VoidCallback? onOpenLocalHistory;

  const ConversationView({""", """  final VoidCallback? onOpenLocalHistory;
  /// Opened under its own summary, which already shows the model's name and closes it on a tap (Claude, 2026-10-21).
  final bool attached;

  const ConversationView({""")
cone("""    this.onOpenLocalHistory,
  });""", """    this.onOpenLocalHistory,
    this.attached = false,
  });""")
cone("""              Expanded(
                child: Text(item.modelDef.label, maxLines: 1, softWrap: false, overflow: TextOverflow.fade, style: VType.headline().copyWith(fontSize: 15, height: 20 / 15)),
              ),
              Builder(builder: (c) => VCircleButton(icon: Icons.more_horiz_rounded, size: 30, tooltip: 'More', onTap: () => _menu(c))),
              const SizedBox(width: 6),
              VCircleButton(icon: Icons.close_rounded, size: 30, tooltip: 'Close', onTap: widget.onClose),""",
     """              Expanded(
                child: widget.attached
                    ? const SizedBox.shrink()
                    : Text(item.modelDef.label, maxLines: 1, softWrap: false, overflow: TextOverflow.fade, style: VType.headline().copyWith(fontSize: 15, height: 20 / 15)),
              ),
              Builder(builder: (c) => VCircleButton(icon: Icons.more_horiz_rounded, size: 30, tooltip: 'More', onTap: () => _menu(c))),
              if (!widget.attached) ...[
                const SizedBox(width: 6),
                VCircleButton(icon: Icons.close_rounded, size: 30, tooltip: 'Close', onTap: widget.onClose),
              ],""")
c.write_text(t, encoding="utf-8")
print("edited conversation_view.dart")

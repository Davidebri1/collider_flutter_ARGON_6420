# Made by Claude (2026-10-23). Round 30: the ticker side by side (David's IDE layout, the Whimsical board): the model
# rows stay as the left column, the opened conversation is a closeable pane beside them, in one window. The selected
# row shows its summary in full. On a phone the window takes the side navigation's room while a conversation is open.
p = "lib/main.dart"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)


# the conversation detail view gives way to the pane
a = s.index("          // ================= AN OPENED CONVERSATION (Claude, 2026-10-23) =================")
b = s.index("          // ================= PLANE 3: LOCAL MODEL HISTORY PANE =================")
s = s[:a] + s[b:]

rep("""            item: openItem,
            attached: true,""", """            item: openItem,
            fill: true, // the pane's full height, the entry box at its foot""")

rep("""                        isExpanded: activePills[i].modelDef.id == openId,""",
    """                        isExpanded: activePills[i].modelDef.id == openId,
                        compact: openItem != null,""")

rep("""    final railVisible = _railVisible && openItem == null;""",
    """    // side by side: the rows as the left column and the conversation as a closeable pane beside them
    final sideBySide = openItem != null && !media;
    // On a phone the window takes the side navigation's room while a conversation is open.
    final railVisible = _railVisible && !(isMobile && sideBySide);
    final screenW = MediaQuery.sizeOf(context).width;""")

rep("""                  padding: EdgeInsets.only(left: isMobile && !media ? 76 : 0),
                  child: Column(""", """                  padding: EdgeInsets.zero,
                  child: Column(""")

rep("""                    Center(
                      child: Container(
                        constraints: BoxConstraints(
                          maxWidth: isMobile
                              ? (media ? 360.0 : 300.0) // one width, opened or not; the pictures' toolbar fits whole (Claude, 2026-10-21)
                              : (media ? 780.0 : 480.0),
                          // rows: never more than 40% of the screen; a conversation: "halfway up is sufficient"
                          maxHeight: MediaQuery.of(context).size.height * (media && _mediaExpanded ? 0.50 : 0.40),
                        ),
                        margin: EdgeInsets.symmetric(horizontal: isMobile ? 12 : 24),""",
    """                    Padding(
                      // beside the side navigation on a phone, never under it
                      padding: EdgeInsets.only(left: isMobile && !media && !sideBySide ? 76 : 0),
                      child: Center(
                      child: Container(
                        constraints: BoxConstraints(
                          maxWidth: sideBySide
                              ? (isMobile ? screenW - 20 : (screenW - 220).clamp(480.0, 872.0))
                              : isMobile
                                  ? (media ? 360.0 : 300.0) // the pictures' toolbar fits whole (Claude, 2026-10-21)
                                  : (media ? 780.0 : 480.0),
                          // rows: never more than 40% of the screen; a conversation: "halfway up is sufficient"
                          maxHeight: MediaQuery.of(context).size.height * (sideBySide || (media && _mediaExpanded) ? 0.50 : 0.40),
                        ),
                        height: sideBySide ? MediaQuery.of(context).size.height * 0.50 : null,
                        margin: EdgeInsets.symmetric(horizontal: sideBySide ? 0 : (isMobile ? 12 : 24)),""")

rep("""                                  refresh: _mediaRefresh,
                                )
                              : rows,
                        ),
                      ),
                    ),""", """                                  refresh: _mediaRefresh,
                                )
                              : sideBySide
                                  ? Row(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                                      SizedBox(width: isMobile ? 136 : 300, child: Align(alignment: Alignment.topCenter, child: rows)),
                                      const SizedBox(width: VSpace.xs),
                                      Expanded(
                                        child: Container(
                                          padding: const EdgeInsets.fromLTRB(10, 8, 8, 8),
                                          decoration: BoxDecoration(color: VColors.fillRow, borderRadius: BorderRadius.circular(VRadius.card - VSpace.xs)),
                                          child: conversation,
                                        ),
                                      ),
                                    ])
                                  : rows,
                        ),
                      ),
                    ),
                    ),""")

rep("""                    ConstrainedBox(
                      // as wide as the ticker and the dock, so it stands beside the side navigation, not over it
                      constraints: BoxConstraints(maxWidth: isMobile ? 300.0 : 480.0),""",
    """                    Padding(
                      // in the ticker's column, beside the side navigation; it stays put when a conversation opens
                      padding: EdgeInsets.only(left: isMobile && !media ? 76 : 0),
                      child: ConstrainedBox(
                      constraints: BoxConstraints(maxWidth: isMobile ? 300.0 : 480.0),""")
rep("""                        onTuck: () => setState(() => _isComposerSummoned = false),
                      ),
                    ),""", """                        onTuck: () => setState(() => _isComposerSummoned = false),
                      ),
                    ),
                    ),""")
open(p, "w", encoding="utf-8").write(s)

# ConversationView: fill the pane, entry box at the foot
p = "lib/features/ticker/widgets/conversation_view.dart"
s = open(p, encoding="utf-8").read()
rep("""  final bool attached;

  const ConversationView({""", """  final bool attached;

  /// Fills the height it is given (the side-by-side pane): the messages take the room, the entry box sits at the foot.
  final bool fill;

  const ConversationView({""")
rep("""    this.attached = false,
  });""", """    this.attached = false,
    this.fill = false,
  });""")
rep("""    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // 0:639 header""", """    return Column(
      mainAxisSize: widget.fill ? MainAxisSize.max : MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // 0:639 header""")
rep("""        Flexible(
          child: EdgeFade(
            fadeHeight: 16,""", """        Flexible(
          fit: widget.fill ? FlexFit.tight : FlexFit.loose,
          child: EdgeFade(
            fadeHeight: 16,""")
open(p, "w", encoding="utf-8").write(s)

# ModelPill: compact in the left column; the selected row shows its summary in full
p = "lib/features/ticker/widgets/model_pill.dart"
s = open(p, encoding="utf-8").read()
rep("""  /// 0 = resting (bottom of the stack) to 1 = highest row.
  final double elevation;
""", """  /// 0 = resting (bottom of the stack) to 1 = highest row.
  final double elevation;

  /// In the narrow left column beside an open conversation.
  final bool compact;
""")
rep("""    this.elevation = 0,
  });""", """    this.elevation = 0,
    this.compact = false,
  });""")
rep("""                  if (waiting) _Pulse(color: c) else Text(item.relativeTime, style: meta),""",
    """                  if (waiting) _Pulse(color: c) else if (!widget.compact) Text(item.relativeTime, style: meta),""")
rep("""            SizedBox(
              height: 34,
              child: AnimatedSwitcher(""", """            // The open model's summary in full, the row growing in place like an accordion (David, 23 Oct).
            AnimatedSize(
              duration: VMotion.base,
              curve: Curves.easeOutCubic,
              alignment: Alignment.topCenter,
              child: SizedBox(
              height: widget.isExpanded && item.summary.isNotEmpty ? null : 34,
              child: AnimatedSwitcher(""")
rep("""                        child: Text(item.summary, maxLines: 2, overflow: TextOverflow.fade, style: VOneLine.rowStyle),
                      ),
              ),
            ),""", """                        child: Text(item.summary,
                            maxLines: widget.isExpanded ? null : 2, overflow: widget.isExpanded ? null : TextOverflow.fade, style: VOneLine.rowStyle),
                      ),
              ),
            ),
            ),""")
open(p, "w", encoding="utf-8").write(s)
print("round 30 applied")

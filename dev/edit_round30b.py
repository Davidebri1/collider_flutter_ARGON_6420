# Made by Claude (2026-10-23). Round 30b: the conversation pane's menu carries Send and Open, as every opened thing does.
def edit(p, pairs):
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:60])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)


edit("lib/features/ticker/widgets/conversation_view.dart", [
    ("""  final VoidCallback? onOpenLocalHistory;
""", """  final VoidCallback? onOpenLocalHistory;
  final VoidCallback? onSend; // the conversation through the share sheet
  final VoidCallback? onOpen; // the conversation as a document
"""),
    ("""    this.onOpenLocalHistory,
""", """    this.onOpenLocalHistory,
    this.onSend,
    this.onOpen,
"""),
    ("""      if (widget.onOpenBrowser != null) VMenuItem(Icons.language_rounded, 'Browser', widget.onOpenBrowser!),
""", """      if (widget.onOpenBrowser != null) VMenuItem(Icons.language_rounded, 'Browser', widget.onOpenBrowser!),
      if (widget.onSend != null) VMenuItem(Icons.ios_share_rounded, 'Send', widget.onSend!, apart: true),
      if (widget.onOpen != null) VMenuItem(Icons.open_in_new_rounded, 'Open', widget.onOpen!),
"""),
])
edit("lib/main.dart", [
    ("""            onOpenLocalHistory: () => setState(() => _localHistoryModel = openItem.modelDef),
          );""", """            onOpenLocalHistory: () => setState(() => _localHistoryModel = openItem.modelDef),
            onSend: () => _sendText(_conversationText(openItem)),
            onOpen: () => _openTextAsDocument(openItem.modelDef.label, _conversationText(openItem), openItem.modelDef.label),
          );"""),
])
print("round 30b applied")

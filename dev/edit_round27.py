# Made by Claude (2026-10-23). Round 27: a summary opens its conversation in the detail view (the ticker never changes
# size); summaries get two lines, shown whole; message and conversation Open as a document; the side rail steps aside
# while a conversation is open.
p = "lib/main.dart"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


rep("""                      // The opened conversation grows out of its own summary, the other summaries staying where they
                      // are (Claude, 2026-10-21; David: the swap "to slightly larger ticker ... we lost the summaries").
                      AnimatedSize(
                        duration: const Duration(milliseconds: 320),
                        curve: Curves.easeOutCubic,
                        alignment: Alignment.topCenter,
                        child: activePills[i].modelDef.id == openId
                            ? Padding(
                                padding: const EdgeInsets.only(top: 8),
                                child: SizedBox(height: convHeight, child: conversation),
                              )
                            : const SizedBox(width: double.infinity),
                      ),
""", """                      // The conversation opens in the detail view over the room; the ticker keeps its size and place
                      // (Claude, 2026-10-23; it used to grow out of the summary).
""")

rep("""    // what is left of the window (half the screen) under the consensus row and the summary, so the entry box shows whole
    final convHeight = (MediaQuery.sizeOf(context).height * 0.5 - 150).clamp(220.0, 420.0);
""", "")

rep("""    final railVisible = _railVisible;""", """    final railVisible = _railVisible && openItem == null;""")

rep("""(openItem != null || (media && _mediaExpanded) ? 0.50 : 0.40)""", """(media && _mediaExpanded ? 0.50 : 0.40)""")

# two lines a summary (David, 23 Oct: "it can be 2 lines. the important thing is that it shows in full")
rep("""  int get _lineChars => VOneLine.charsFor((MediaQuery.of(context).size.width < 768 ? 260.0 : 480.0) - 42);""",
    """  int get _lineChars => VOneLine.charsFor((MediaQuery.of(context).size.width < 768 ? 260.0 : 480.0) - 42) * 2;""")

# the opened conversation, in the detail view; placed under the local history pane and the zoomed message
rep("""          // ================= PLANE 3: LOCAL MODEL HISTORY PANE =================""",
    """          // ================= AN OPENED CONVERSATION (Claude, 2026-10-23) =================
          // The app's detail view: the model, its summary in full, the conversation and its entry box; Send, Open, Close.
          if (openItem != null && _activeDrawer == null)
            Positioned.fill(
              child: DetailView(
                onClose: () => setState(() => _expandedModelIds.clear()),
                onSend: () => _sendText(_conversationText(openItem)),
                onOpen: () => _openTextAsDocument(openItem.modelDef.label, _conversationText(openItem), openItem.modelDef.label),
                maxWidth: 560,
                child: ConstrainedBox(
                  constraints: BoxConstraints(maxHeight: MediaQuery.sizeOf(context).height * 0.66),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(openItem.modelDef.label,
                          maxLines: 1,
                          softWrap: false,
                          overflow: TextOverflow.fade,
                          style: VType.headline().copyWith(fontSize: 15, height: 20 / 15, shadows: const [Shadow(color: Color(0x99000000), blurRadius: 12)])),
                      if (openItem.summary.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(openItem.summary,
                            style: VType.callout(color: VColors.textSecondary).copyWith(height: 1.4, shadows: const [Shadow(color: Color(0x99000000), blurRadius: 12)])),
                      ],
                      const SizedBox(height: 10),
                      Flexible(child: conversation),
                    ],
                  ),
                ),
              ),
            ),

          // ================= PLANE 3: LOCAL MODEL HISTORY PANE =================""")

rep("""                providerColor: _zoomedModelDef!.providerColor,
                onClose: () => setState(() => _zoomedMessage = null),
              ),""", """                providerColor: _zoomedModelDef!.providerColor,
                onClose: () => setState(() => _zoomedMessage = null),
                onOpen: () => _openTextAsDocument(_zoomedModelDef!.label, _zoomedMessage!.text, _zoomedModelDef!.label),
              ),""")

# helpers
rep("""  final GlobalKey _openKey = GlobalKey();
""", """  final GlobalKey _openKey = GlobalKey();

  /// A conversation as text: who said each part, then what was said.
  String _conversationText(TickerItem it) => [
        for (final m in it.conversation) '${m.sender == 'user' ? 'You' : it.modelDef.label}:\\n${m.text}',
      ].join('\\n\\n');

  /// The device's share sheet; where there is none, the text is copied.
  Future<void> _sendText(String text) async {
    if (!await shareText(text)) await Clipboard.setData(ClipboardData(text: text));
  }

  /// Opens text in Documents: it is kept in Files > Generated first, so the document is a file like any other
  /// (Claude, 2026-10-23).
  Future<void> _openTextAsDocument(String title, String text, String model) async {
    final words = text.replaceAll(RegExp(r'[#*_`>\\[\\]\\n]'), ' ').trim().split(RegExp(r'\\s+')).take(6).join(' ');
    final name = await ColliderApi.instance.saveGenerated('$title - $words.md', text, model: model);
    if (name == null || !mounted) return;
    final all = await ColliderApi.instance.files(forceRefresh: true);
    final f = (all['generated'] ?? const <ColliderFile>[]).where((f) => f.name == name).firstOrNull;
    if (f == null || !mounted) return;
    setState(() {
      _zoomedMessage = null;
      _expandedModelIds.clear();
    });
    _openDocument(f.url, f.name);
  }
""")

if "import 'core/platform/open_url.dart';" not in s:
    rep("import 'core/drafts.dart';\n", "import 'core/drafts.dart';\nimport 'core/platform/open_url.dart';\n")
open(p, "w", encoding="utf-8").write(s)
print("round 27 applied")

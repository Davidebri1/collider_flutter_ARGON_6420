import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';
import 'package:file_picker/file_picker.dart';
import '../../../models/ticker_item.dart';
import '../../../core/vision/vision_kit.dart';
import '../../../core/api/collider_api.dart';
import '../../../core/drafts.dart';
import '../../../core/platform/open_url.dart';

/// One model's conversation, opened. Made by Claude on 2026-10-04.
/// David's reference map, row 15 (wechat vision os 0:639): "Collapsed is left column, Expanded is middle area;
/// expanded is closeable". This is the middle area of that frame: the name and a round button at the top,
/// the messages as bubbles with their time under the text, the entry box at the foot.
/// What a message can do is in its press menu, and what the conversation can do is in the header's menu.
class ConversationView extends StatefulWidget {
  final TickerItem item;
  final VoidCallback onClose;
  final void Function(String replyText, List<String> files)? onSendReply;
  final VoidCallback? onOpenBrowser;
  final void Function(TickerMessage message)? onTapMessage;
  final VoidCallback? onOpenLocalHistory;
  final VoidCallback? onSend; // the conversation through the share sheet
  final VoidCallback? onOpen; // the conversation as a document
  /// Opened under its own summary, which already shows the model's name and closes it on a tap (Claude, 2026-10-21).
  final bool attached;

  /// Fills the height it is given (the side-by-side pane): the messages take the room, the entry box sits at the foot.
  final bool fill;

  const ConversationView({
    super.key,
    required this.item,
    required this.onClose,
    this.onSendReply,
    this.onOpenBrowser,
    this.onTapMessage,
    this.onOpenLocalHistory,
    this.onSend,
    this.onOpen,
    this.attached = false,
    this.fill = false,
  });

  @override
  State<ConversationView> createState() => _ConversationViewState();
}

class _ConversationViewState extends State<ConversationView> {
  // the reply being written is kept per model in Drafts: closing this view or opening another keeps it (Claude, 2026-10-21)
  late final TextEditingController _reply = Drafts.text('reply:${widget.item.modelDef.id}');
  late final TextEditingController _search = Drafts.text('conversation.search:${widget.item.modelDef.id}');
  bool _searching = false;
  String _filter = '';
  late final List<String> _files = Drafts.files('reply:${widget.item.modelDef.id}');
  final ScrollController _scroll = ScrollController();

  @override
  void initState() {
    super.initState();
    if (widget.item.conversation.length > 2) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scroll.hasClients) _scroll.jumpTo(_scroll.position.maxScrollExtent);
      });
    }
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  /// While an answer drafts, the newest words stay in view (unless the reader has scrolled up to read).
  @override
  void didUpdateWidget(ConversationView old) {
    super.didUpdateWidget(old);
    final a = old.item.conversation, b = widget.item.conversation;
    final grew = b.length != a.length || (b.isNotEmpty && a.isNotEmpty && b.last.text.length != a.last.text.length) || widget.item.isStreaming != old.item.isStreaming;
    if (!grew || !_scroll.hasClients) return;
    final p = _scroll.position;
    if (p.maxScrollExtent - p.pixels > 120 && b.length == a.length) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) _scroll.jumpTo(_scroll.position.maxScrollExtent);
    });
  }

  void _toast(String text) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      duration: const Duration(seconds: 1),
      behavior: SnackBarBehavior.floating,
      backgroundColor: VColors.glassDark,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(VRadius.full)),
      margin: EdgeInsets.fromLTRB(MediaQuery.sizeOf(context).width * 0.24, 0, MediaQuery.sizeOf(context).width * 0.24, 100),
      elevation: 0,
      content: Text(text, textAlign: TextAlign.center, style: VType.callout()),
    ));
  }

  void _submit() {
    final text = _reply.text.trim();
    if (text.isEmpty && _files.isEmpty) return;
    widget.onSendReply?.call(text, List.of(_files));
    Drafts.sent('reply:${widget.item.modelDef.id}');
    setState(() {});
  }

  Future<void> _attach() async {
    try {
      final res = await FilePicker.platform.pickFiles(allowMultiple: true, withData: true);
      if (res == null) return;
      for (final f in res.files) {
        if (f.bytes == null) continue;
        final saved = await ColliderApi.instance.uploadFile(f.name, f.bytes!);
        if (saved != null && mounted) setState(() => _files.add(saved));
        Drafts.touch();
      }
    } catch (_) {}
  }

  Future<void> _save(TickerMessage m) async {
    final words = m.text.replaceAll(RegExp(r'[#*_`>\[\]\n]'), ' ').trim().split(RegExp(r'\s+')).take(6).join(' ');
    final name = await ColliderApi.instance.saveGenerated('${widget.item.modelDef.label} - $words.md', m.text, model: widget.item.modelDef.label);
    if (mounted) _toast(name == null ? 'Not saved' : 'Saved to Files');
  }

  /// A message's press menu.
  void _messageMenu(Offset at, TickerMessage m) {
    showVMenu(context, at, [
      VMenuItem(Icons.copy_rounded, 'Copy', () {
        Clipboard.setData(ClipboardData(text: m.text));
        _toast('Copied');
      }),
      VMenuItem(Icons.bookmark_border_rounded, 'Save', () => _save(m)),
      if (canShareText) VMenuItem(Icons.ios_share_rounded, 'Share', () => shareText(m.text)),
    ]);
  }

  /// What can be done with this conversation.
  void _menu(BuildContext anchor) {
    final box = anchor.findRenderObject() as RenderBox;
    // Under its button, its right edge on the button's right edge: it stays inside the window.
    final at = box.localToGlobal(Offset(box.size.width, box.size.height));
    showVMenu(context, at, align: VMenuAlign.end, [
      VMenuItem(Icons.search_rounded, 'Search', () => setState(() {
            _searching = !_searching;
            if (!_searching) _filter = '';
          }), checked: _searching),
      VMenuItem(Icons.attach_file_rounded, 'Attach', _attach),
      if (widget.onOpenLocalHistory != null) VMenuItem(Icons.history_rounded, 'History', widget.onOpenLocalHistory!),
      if (widget.onOpenBrowser != null) VMenuItem(Icons.language_rounded, 'Browser', widget.onOpenBrowser!),
      if (widget.onSend != null) VMenuItem(Icons.ios_share_rounded, 'Send', widget.onSend!, apart: true),
      if (widget.onOpen != null) VMenuItem(Icons.open_in_new_rounded, 'Open', widget.onOpen!),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    final shown = [
      for (final m in item.conversation)
        if (_filter.isEmpty || m.text.toLowerCase().contains(_filter)) m,
    ];
    // The model is writing and nothing of its answer has arrived yet: its bubble shows that it is drafting.
    final drafting = item.isStreaming && (item.conversation.isEmpty || item.conversation.last.sender == 'user');
    return Column(
      mainAxisSize: widget.fill ? MainAxisSize.max : MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Header: Auto-Named Conversation Title + Model subtitle, and action buttons at the right.
        if (!widget.attached)
          Padding(
            padding: const EdgeInsets.fromLTRB(8, 2, 0, 8),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        item.displayTitle,
                        maxLines: 1,
                        softWrap: false,
                        overflow: TextOverflow.fade,
                        style: VType.headline().copyWith(fontSize: 13.5, height: 18 / 13.5),
                      ),
                      Text(
                        item.modelDef.label,
                        maxLines: 1,
                        softWrap: false,
                        overflow: TextOverflow.fade,
                        style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w500).copyWith(fontSize: 10.5),
                      ),
                    ],
                  ),
                ),
                Builder(builder: (c) => VCircleButton(icon: Icons.more_horiz_rounded, size: 30, tooltip: 'More', onTap: () => _menu(c))),
                const SizedBox(width: 6),
                VCircleButton(icon: Icons.close_rounded, size: 30, tooltip: 'Close', onTap: widget.onClose),
              ],
            ),
          ),
        if (_searching) ...[
          VSearchField(controller: _search, hint: 'Search', height: 32, onChanged: (v) => setState(() => _filter = v.toLowerCase())),
          const SizedBox(height: VSpace.xs),
        ],
        Flexible(
          fit: widget.fill ? FlexFit.tight : FlexFit.loose,
          child: EdgeFade(
            fadeHeight: 16,
            focus: FadeFocus.bottom, // the newest message is at the bottom; older ones recede upwards
            child: ListView.builder(
              controller: _scroll,
              shrinkWrap: true,
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.symmetric(vertical: 6),
              itemCount: shown.length + (drafting ? 1 : 0),
              itemBuilder: (_, i) {
                if (i == shown.length) {
                  return const Align(alignment: Alignment.centerLeft, child: _Bubble(isUser: false, child: _Drafting()));
                }
                final m = shown[i];
                final isUser = m.sender == 'user';
                final t = m.timestamp;
                final time = '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: GestureDetector(
                    onLongPressStart: (d) => _messageMenu(d.globalPosition, m),
                    onSecondaryTapDown: (d) => _messageMenu(d.globalPosition, m),
                    child: VPress(
                      onTap: () => widget.onTapMessage?.call(m),
                      child: _Bubble(
                        isUser: isUser,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            isUser
                                ? Text(m.text, style: VType.callout(weight: FontWeight.w400).copyWith(height: 1.4))
                                : MdText(m.text),
                            const SizedBox(height: 3),
                            Text(time, style: VType.caption(color: VColors.textTertiary).copyWith(fontSize: 11, height: 12 / 10)),
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ),
        if (_files.isNotEmpty) ...[
          const SizedBox(height: VSpace.xs),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              for (final f in _files) VChip(label: f.length > 22 ? '${f.substring(0, 21)}…' : f, selected: true, onTap: () {
                setState(() => _files.remove(f));
                Drafts.touch();
              }),
            ],
          ),
        ],
        const SizedBox(height: VSpace.xs),
        // 0:639 entry box: recessed, the words to type, send at the right.
        VRecessed(
          radius: 20,
          padding: EdgeInsets.fromLTRB(widget.attached ? 4 : 14, 0, 4, 0),
          child: SizedBox(
            height: 40,
            child: Row(
              children: [
                if (widget.attached) ...[
                  Builder(builder: (c) => VCircleButton(icon: Icons.more_horiz_rounded, size: 32, tooltip: 'More', onTap: () => _menu(c))),
                  const SizedBox(width: 6),
                ],
                Expanded(
                  child: TextField(
                    controller: _reply,
                    cursorColor: VColors.textPrimary,
                    style: VType.callout(weight: FontWeight.w400),
                    decoration: InputDecoration(
                      hintText: 'Enter message',
                      hintStyle: VType.callout(color: VColors.textTertiary, weight: FontWeight.w400),
                      border: InputBorder.none,
                      isDense: true,
                      contentPadding: EdgeInsets.zero,
                    ),
                    onSubmitted: (_) => _submit(),
                  ),
                ),
                VCircleButton(icon: Icons.arrow_upward_rounded, size: 32, selected: true, tooltip: 'Send', onTap: _submit),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

/// Three dots that brighten in turn while the model drafts, as in Messages (Claude, 2026-10-19).
class _Drafting extends StatefulWidget {
  const _Drafting();
  @override
  State<_Drafting> createState() => _DraftingState();
}

class _DraftingState extends State<_Drafting> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => SizedBox(
        height: 18,
        child: AnimatedBuilder(
          animation: _c,
          builder: (_, __) => Row(mainAxisSize: MainAxisSize.min, children: [
            for (var i = 0; i < 3; i++)
              Container(
                width: 7,
                height: 7,
                margin: EdgeInsets.only(right: i < 2 ? 5 : 0),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.3 + 0.6 * (1 - ((_c.value * 3 - i) % 3).clamp(0.0, 1.0))),
                ),
              ),
          ]),
        ),
      );
}

/// Speech bubble, WeChat visionOS 0:639: one small corner on the speaker's side.
class _Bubble extends StatelessWidget {
  final bool isUser;
  final Widget child;
  const _Bubble({required this.isUser, required this.child});

  @override
  Widget build(BuildContext context) {
    const r = Radius.circular(14);
    const tail = Radius.circular(3);
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 5),
      constraints: const BoxConstraints(maxWidth: 270),
      padding: const EdgeInsets.fromLTRB(13, 9, 13, 8),
      decoration: BoxDecoration(
        color: isUser ? VColors.fillActive : const Color(0x4D808080),
        borderRadius: isUser
            ? const BorderRadius.only(topLeft: r, topRight: tail, bottomLeft: r, bottomRight: r)
            : const BorderRadius.only(topLeft: tail, topRight: r, bottomLeft: r, bottomRight: r),
      ),
      child: child,
    );
  }
}

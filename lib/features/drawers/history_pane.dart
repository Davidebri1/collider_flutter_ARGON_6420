import '../../core/drafts.dart';
import 'package:material_ui/material_ui.dart';

import '../../core/api/collider_api.dart';
import '../../core/vision/vision_kit.dart';
import '../../models/model_def.dart';
import '../../models/ticker_item.dart';
import 'history_drawer.dart' show VHistoryRowsGrouped;

/// History Pane — Centered, Ergonomic Scannable Explorer per VisionOS HIG & PRD R15/R21/R37/R46:
/// - Vertically and horizontally centered (Alignment.center, never pinned to the top).
/// - Height (~320px) calibrated to show 5–6 auto-named conversation titles at once before scrolling.
/// - ~33% screen width list pane with side-by-side 1-on-1 Model Conversation Thread popout.
/// - Model selector dropdown in the list header (R15) + top-anchored live search bar (R46/R21).
/// - Dims room background without blur (R37), while focusing the search or reply input triggers Plane 0 DOF blur (R65).
class HistoryPane extends StatefulWidget {
  final List<ConversationHistorySession> sessions;
  final JobState? Function(String id) job;
  final ValueChanged<ConversationHistorySession> onLoad;
  final VoidCallback onClose;
  final VoidCallback? onUpdated;

  const HistoryPane({
    super.key,
    required this.sessions,
    required this.job,
    required this.onLoad,
    required this.onClose,
    this.onUpdated,
  });

  @override
  State<HistoryPane> createState() => _HistoryPaneState();
}

class _HistoryPaneState extends State<HistoryPane> {
  final TextEditingController _search = Drafts.text('history.pane.search');
  String _q = '';
  String? _modelFilter; // null = All Models, or specific modelId (PRD R15)
  ConversationHistorySession? _open;
  bool _previewInitDone = false;

  static const _filterModels = <String>[
    'pro/claude-3-7-sonnet',
    'free/gpt-5-nano',
    'free/gemini-3-6-flash-lite',
    'free/mistral-small',
    'free/qwen-3-6-27b',
    'free/minimax-m3',
  ];

  void _cycleModelFilter() {
    setState(() {
      if (_modelFilter == null) {
        _modelFilter = _filterModels.first;
      } else {
        final idx = _filterModels.indexOf(_modelFilter!);
        if (idx == -1 || idx + 1 >= _filterModels.length) {
          _modelFilter = null;
        } else {
          _modelFilter = _filterModels[idx + 1];
        }
      }
    });
  }

  void _syncPreviewParam(List<ConversationHistorySession> sessions) {
    if (_previewInitDone || sessions.isEmpty) return;
    final p = Uri.base.queryParameters['preview'];
    if (p != null) {
      _previewInitDone = true;
      final idx = int.tryParse(p) ?? 0;
      _open = sessions[idx.clamp(0, sessions.length - 1)];
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    // ~33% screen width for list pane, side-by-side popout for 1-on-1 model conversation
    final listW = (size.width * 0.33).clamp(132.0, 195.0);
    final previewW = (size.width - listW - 26).clamp(216.0, 420.0);
    // Ergonomic height: header + model filter + search + 5–6 conversation titles before scrolling
    final h = (size.height * 0.39).clamp(296.0, 336.0);

    final q = _q.toLowerCase();
    final sessions = widget.sessions.where((s) {
      if (_modelFilter != null && s.modelIds.isNotEmpty && !s.modelIds.contains(_modelFilter)) {
        return false;
      }
      if (q.isEmpty) return true;
      final autoTitle = autoNameConversationTitle(s.title, s.summary).toLowerCase();
      return autoTitle.contains(q) ||
          s.title.toLowerCase().contains(q) ||
          s.summary.toLowerCase().contains(q) ||
          s.messages.any((m) => m.text.toLowerCase().contains(q));
    }).toList();

    _syncPreviewParam(sessions);
    final open = _open;
    final filterLabel = _modelFilter == null ? 'All Models' : (ModelRoster.byId(_modelFilter!)?.label ?? _modelFilter!);

    final list = SizedBox(
      width: listW,
      height: h,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(10, 8, 6, 4),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    'History',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: VType.headline().copyWith(fontSize: 13),
                  ),
                ),
                VCircleButton(icon: Icons.close_rounded, size: 24, tooltip: 'Close', onTap: widget.onClose),
              ],
            ),
          ),
          // PRD R15: Local model history accessed via model selector dropdown within the History pane
          Padding(
            padding: const EdgeInsets.fromLTRB(6, 0, 6, 4),
            child: VPress(
              onTap: _cycleModelFilter,
              tooltip: 'Filter by model',
              child: Container(
                height: 24,
                padding: const EdgeInsets.symmetric(horizontal: 8),
                decoration: BoxDecoration(
                  color: const Color(0x1FFFFFFF),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: VColors.borderLight, width: 0.5),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        filterLabel,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: VType.caption(color: VColors.textPrimary, weight: FontWeight.w600).copyWith(fontSize: 10.5),
                      ),
                    ),
                    const Icon(Icons.unfold_more_rounded, size: 13, color: VColors.textSecondary),
                  ],
                ),
              ),
            ),
          ),
          // PRD R46: Dedicated search bar anchored at top of History pane
          Padding(
            padding: const EdgeInsets.fromLTRB(6, 0, 6, 4),
            child: VSearchField(
              controller: _search,
              hint: 'Search',
              height: 28,
              onChanged: (v) => setState(() => _q = v.trim()),
            ),
          ),
          // PRD R21: Live as you type; no empty box when nothing matches
          Expanded(
            child: sessions.isEmpty
                ? const SizedBox.shrink()
                : VHistoryRowsGrouped(
                    sessions: sessions,
                    selectedId: open?.id,
                    onSelect: (s) => setState(() => _open = identical(_open, s) ? null : s),
                  ),
          ),
        ],
      ),
    );

    final Widget pane = Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        list,
        AnimatedSize(
          duration: VMotion.base,
          curve: Curves.easeOutCubic,
          alignment: Alignment.centerLeft,
          child: open == null
              ? const SizedBox(height: 0)
              : Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(width: 0.5, height: h, color: VColors.borderLight),
                    SizedBox(
                      width: previewW,
                      height: h,
                      child: _Preview(
                        key: ValueKey('${open.id}_${_modelFilter ?? "all"}'),
                        session: open,
                        job: widget.job(open.id),
                        preferredModelId: _modelFilter,
                        onLoad: (targetModelId) => widget.onLoad(
                          ConversationHistorySession(
                            id: open.id,
                            title: autoNameConversationTitle(open.title, open.summary),
                            targetModelId: targetModelId,
                            relativeTime: open.relativeTime,
                            timestamp: open.timestamp,
                            summary: open.summary,
                            modelIds: open.modelIds,
                            messages: open.messages,
                          ),
                        ),
                        onUpdated: widget.onUpdated,
                      ),
                    ),
                  ],
                ),
        ),
      ],
    );

    return Stack(
      fit: StackFit.expand,
      children: [
        // PRD R37: History dims without blur as an exploration pause
        VScrim(onTap: widget.onClose, blur: false),
        Align(
          alignment: Alignment.center,
          child: GestureDetector(
            onTap: () {},
            child: VGlass(material: VMaterial.modal, radius: VRadius.lg + 4, child: pane),
          ),
        ),
      ],
    );
  }
}

/// 1-on-1 Model Conversation Thread Popout inside History:
/// - Headed by Auto-Named Conversation Title + active Model badge + 'Open Thread' button.
/// - Displays the single selected model's 1-on-1 conversation (user prompt + model response + follow-up turns).
/// - Includes in-pane follow-up reply input at the bottom.
class _Preview extends StatefulWidget {
  final ConversationHistorySession session;
  final JobState? job;
  final String? preferredModelId;
  final ValueChanged<String?> onLoad;
  final VoidCallback? onUpdated;

  const _Preview({
    super.key,
    required this.session,
    required this.job,
    required this.onLoad,
    this.preferredModelId,
    this.onUpdated,
  });

  @override
  State<_Preview> createState() => _PreviewState();
}

class _Turn {
  final String question;
  final Map<String, String?> answers = {};
  _Turn(this.question);
}

class _PreviewState extends State<_Preview> {
  final TextEditingController _ctrl = Drafts.text('history.pane.reply');
  final List<_Turn> _turns = [];

  String _resolveModelId(JobState? job) {
    if (widget.preferredModelId != null && (job == null || job.results.containsKey(widget.preferredModelId))) {
      return widget.preferredModelId!;
    }
    if (widget.session.targetModelId != null) return widget.session.targetModelId!;
    if (job != null) {
      for (final e in job.results.entries) {
        if (e.value.status == 'done' && e.value.text.isNotEmpty) return e.key;
      }
      if (job.results.isNotEmpty) return job.results.keys.first;
    }
    if (widget.session.modelIds.isNotEmpty) return widget.session.modelIds.first;
    return 'pro/claude-3-7-sonnet';
  }

  void _send(String targetMid) {
    final text = _ctrl.text.trim();
    final job = widget.job;
    if (text.isEmpty || job == null) return;
    _ctrl.clear();
    final turn = _Turn(text);
    turn.answers[targetMid] = null;
    setState(() => _turns.add(turn));
    final mode = AskMode.values.firstWhere((m) => m.wire == job.mode, orElse: () => AskMode.chat);
    final res = job.results[targetMid];
    final baseHistory = (res != null && res.messages.isNotEmpty)
        ? [for (final m in res.messages) {'role': m['role'] ?? 'user', 'content': m['content'] ?? ''}]
        : <Map<String, String>>[
            {'role': 'user', 'content': job.prompt},
            if (res != null && res.text.isNotEmpty) {'role': 'assistant', 'content': res.text},
          ];
    final messages = <Map<String, String>>[
      ...baseHistory,
      for (final t in _turns.where((t) => t != turn)) ...[
        {'role': 'user', 'content': t.question},
        if (t.answers[targetMid] != null) {'role': 'assistant', 'content': t.answers[targetMid]!},
      ],
      {'role': 'user', 'content': text},
    ];
    ColliderApi.instance.replyStream(model: targetMid, messages: messages, mode: mode, jobId: job.id).listen((d) {
      if (mounted && d.text.isNotEmpty) setState(() => turn.answers[targetMid] = d.text);
      if (d.done) {
        ColliderApi.instance.cachedHistory = null;
        widget.onUpdated?.call();
      }
    }, onError: (Object _) {
      if (mounted) setState(() => turn.answers.remove(targetMid));
    }, cancelOnError: true);
  }

  Widget _answer(String mid, String? text) {
    final def = ModelRoster.byId(mid);
    final c = def?.providerColor ?? VColors.textSecondary;
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8, right: 14),
        padding: const EdgeInsets.fromLTRB(11, 7, 11, 9),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color.alphaBlend(c.withValues(alpha: 0.18), VColors.fillRow),
              Color.alphaBlend(c.withValues(alpha: 0.06), VColors.fillRow),
            ],
          ),
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(4),
            topRight: Radius.circular(14),
            bottomLeft: Radius.circular(14),
            bottomRight: Radius.circular(14),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(def?.label ?? mid, style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w600).copyWith(fontSize: 10)),
            const SizedBox(height: 3),
            text == null
                ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 1.5, color: VColors.textSecondary))
                : MdText(text, style: VType.callout(weight: FontWeight.w400).copyWith(fontSize: 11, height: 1.38)),
          ],
        ),
      ),
    );
  }

  Widget _question(String q) => Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(bottom: 8, left: 20),
          padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
          decoration: const BoxDecoration(
            color: VColors.fillActive,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(14),
              topRight: Radius.circular(4),
              bottomLeft: Radius.circular(14),
              bottomRight: Radius.circular(14),
            ),
          ),
          child: Text(q, style: VType.callout(weight: FontWeight.w500).copyWith(fontSize: 11)),
        ),
      );

  @override
  Widget build(BuildContext context) {
    final job = widget.job;
    final s = widget.session;
    final targetMid = _resolveModelId(job);
    final targetDef = ModelRoster.byId(targetMid);
    final autoTitle = autoNameConversationTitle(job?.prompt ?? s.title, s.summary);

    final res = job?.results[targetMid];
    final List<Map<String, String>> threadMsgs = [];
    if (res != null && res.messages.isNotEmpty) {
      for (final m in res.messages) {
        threadMsgs.add({'role': '${m['role'] ?? 'user'}', 'content': '${m['content'] ?? ''}'});
      }
    } else if (res != null && res.text.isNotEmpty) {
      threadMsgs.add({'role': 'user', 'content': job!.prompt});
      threadMsgs.add({'role': 'assistant', 'content': res.text});
    } else {
      for (final m in s.messages) {
        threadMsgs.add({'role': m.sender == 'user' ? 'user' : 'assistant', 'content': m.text});
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(10, 8, 8, 6),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      autoTitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: VType.callout(weight: FontWeight.w600).copyWith(fontSize: 11.5),
                    ),
                    Text(
                      targetDef?.label ?? targetMid,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w500).copyWith(fontSize: 9.5),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 6),
              VPress(
                onTap: () => widget.onLoad(targetMid),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(color: VColors.accentBlue, borderRadius: BorderRadius.circular(VRadius.full)),
                  child: Text(
                    'Open Thread',
                    style: VType.caption(color: Colors.white, weight: FontWeight.w600).copyWith(fontSize: 10.5),
                  ),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: VFadeScroll(
            padding: const EdgeInsets.fromLTRB(10, 2, 10, 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final m in threadMsgs)
                  m['role'] == 'user'
                      ? _question(m['content'] ?? '')
                      : _answer(targetMid, m['content'] ?? ''),
                for (final t in _turns) ...[
                  _question(t.question),
                  if (t.answers.containsKey(targetMid)) _answer(targetMid, t.answers[targetMid]),
                ],
              ],
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(8, 0, 8, 8),
          child: VRecessed(
            radius: 16,
            padding: const EdgeInsets.fromLTRB(12, 0, 4, 0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 7),
                    child: TextField(
                      controller: _ctrl,
                      minLines: 1,
                      maxLines: 3,
                      cursorColor: VColors.textPrimary,
                      textInputAction: TextInputAction.send,
                      style: VType.callout(weight: FontWeight.w500).copyWith(fontSize: 11, height: 16 / 12),
                      decoration: InputDecoration(
                        hintText: 'Reply to ${targetDef?.label ?? "model"}…',
                        hintStyle: VType.callout(color: const Color(0x99FFFFFF), weight: FontWeight.w400).copyWith(fontSize: 10.5, height: 16 / 12),
                        border: InputBorder.none,
                        isDense: true,
                        contentPadding: EdgeInsets.zero,
                      ),
                      onSubmitted: (_) => _send(targetMid),
                    ),
                  ),
                ),
                const SizedBox(width: 4),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 3.5),
                  child: VPress(
                    onTap: () => _send(targetMid),
                    child: Container(
                      width: 24,
                      height: 24,
                      decoration: const BoxDecoration(shape: BoxShape.circle, color: VColors.fillActive),
                      child: const Icon(Icons.arrow_upward_rounded, size: 14, color: Colors.white),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

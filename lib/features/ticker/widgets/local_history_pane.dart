import '../../../core/drafts.dart';
import 'package:material_ui/material_ui.dart';
import '../../../models/ticker_item.dart';
import '../../../models/model_def.dart';
import '../../../core/vision/vision_kit.dart';
import '../../drawers/history_drawer.dart';

/// REQ-14 Model Local History — the same notes-list window as the global
/// history, headed by the model's avatar. Search covers titles and message bodies.
class LocalHistoryPane extends StatefulWidget {
  final ModelDef modelDef;
  final List<ConversationHistorySession> sessions;
  final Function(ConversationHistorySession) onSelectSession;
  final VoidCallback onClose;

  const LocalHistoryPane({
    super.key,
    required this.modelDef,
    required this.sessions,
    required this.onSelectSession,
    required this.onClose,
  });

  @override
  State<LocalHistoryPane> createState() => _LocalHistoryPaneState();
}

class _LocalHistoryPaneState extends State<LocalHistoryPane> with SingleTickerProviderStateMixin {
  final TextEditingController _searchCtrl = Drafts.text('localhistory.search');
  String _query = '';
  late final AnimationController _ctrl = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 240),
    reverseDuration: const Duration(milliseconds: 190),
  )..forward();
  late final Animation<double> _curve = CurvedAnimation(
    parent: _ctrl,
    curve: Curves.easeOutCubic,
  );
  bool _closing = false;

  Future<void> _handleClose([VoidCallback? then]) async {
    if (_closing) return;
    _closing = true;
    try {
      await _ctrl.reverse();
    } catch (_) {}
    if (!mounted) return;
    widget.onClose();
    then?.call();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final q = _query.toLowerCase();
    final sessions = widget.sessions.where((s) {
      if (q.isEmpty) return true;
      return s.title.toLowerCase().contains(q) || s.messages.any((m) => m.text.toLowerCase().contains(q));
    }).toList();

    return Stack(
      fit: StackFit.expand,
      children: [
        FadeTransition(opacity: _curve, child: VScrim(onTap: () => _handleClose())),
        Align(
          alignment: Alignment.topCenter,
          child: AnimatedBuilder(
            animation: _curve,
            builder: (_, child) => Opacity(
              opacity: _curve.value.clamp(0.0, 1.0),
              child: Transform.translate(
                offset: Offset(0, -12 * (1 - _curve.value)),
                child: Transform.scale(scale: 0.96 + 0.04 * _curve.value, child: child),
              ),
            ),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(VSpace.md, 56, VSpace.md, 0),
              child: VWindow(
                title: widget.modelDef.label,
                maxWidth: VOverlay.menuWidth(context),
                maxHeight: VOverlay.menuMaxHeight(context),
                actions: [VCircleButton(icon: Icons.close_rounded, tooltip: 'Close', onTap: () => _handleClose())],
                child: HistorySessionList(
                  sessions: sessions,
                  searchController: _searchCtrl,
                  onQuery: (v) => setState(() => _query = v.trim()),
                  onSelect: (s) => _handleClose(() => widget.onSelectSession(s)),
                  emptyText: _query.isEmpty ? 'No recorded conversations for this model' : 'No matching conversations found',
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

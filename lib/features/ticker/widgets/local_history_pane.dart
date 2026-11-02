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

class _LocalHistoryPaneState extends State<LocalHistoryPane> {
  final TextEditingController _searchCtrl = Drafts.text('localhistory.search');
  String _query = '';

  @override
  void dispose() {
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
        VScrim(onTap: widget.onClose),
        Align(
          alignment: Alignment.topCenter,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(VSpace.md, 56, VSpace.md, 0),
            child: VWindow(
              title: widget.modelDef.label,
              maxWidth: VOverlay.menuWidth(context),
              maxHeight: VOverlay.menuMaxHeight(context),
              actions: [VCircleButton(icon: Icons.close_rounded, tooltip: 'Close', onTap: widget.onClose)],
              child: HistorySessionList(
                sessions: sessions,
                searchController: _searchCtrl,
                onQuery: (v) => setState(() => _query = v.trim()),
                onSelect: widget.onSelectSession,
                emptyText: _query.isEmpty ? 'No recorded conversations for this model' : 'No matching conversations found',
              ),
            ),
          ),
        ),
      ],
    );
  }
}

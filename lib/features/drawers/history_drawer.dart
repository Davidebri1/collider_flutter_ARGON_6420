import '../../core/drafts.dart';
import 'package:material_ui/material_ui.dart';
import '../../../models/ticker_item.dart';
import '../../../core/vision/vision_kit.dart';

/// REQ-13 Global History Drawer — notes-list window (Vision OS Design System
/// 417:8104 "All iCloud"): large title, recessed search capsule, rows with
/// auto-named conversation title, one-line summary and relative time; edges fade into the glass.
class HistoryDrawer extends StatefulWidget {
  final List<ConversationHistorySession> sessions;
  final Function(ConversationHistorySession session) onSelectSession;
  final VoidCallback onClose;

  const HistoryDrawer({
    super.key,
    required this.sessions,
    required this.onSelectSession,
    required this.onClose,
  });

  @override
  State<HistoryDrawer> createState() => _HistoryDrawerState();
}

class _HistoryDrawerState extends State<HistoryDrawer> {
  final TextEditingController _searchCtrl = Drafts.text('history.search');
  String _query = '';

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final q = _query.toLowerCase();
    final sessions = widget.sessions
        .where((s) =>
            q.isEmpty ||
            autoNameConversationTitle(s.title, s.summary).toLowerCase().contains(q) ||
            s.title.toLowerCase().contains(q) ||
            s.summary.toLowerCase().contains(q))
        .toList();

    return Stack(
      fit: StackFit.expand,
      children: [
        VScrim(onTap: widget.onClose, blur: false),
        Align(
          alignment: Alignment.center,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: VSpace.md),
            child: VWindow(
              title: 'History',
              maxWidth: VOverlay.menuWidth(context),
              maxHeight: (MediaQuery.sizeOf(context).height * 0.39).clamp(296.0, 336.0),
              actions: [VCircleButton(icon: Icons.close_rounded, tooltip: 'Close', onTap: widget.onClose)],
              child: HistorySessionList(
                sessions: sessions,
                searchController: _searchCtrl,
                onQuery: (v) => setState(() => _query = v.trim()),
                onSelect: widget.onSelectSession,
                emptyText: '',
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// Shared session list (global + local history): each conversation's auto-named title on one line and when it was.
class HistorySessionList extends StatelessWidget {
  final List<ConversationHistorySession> sessions;
  final TextEditingController searchController;
  final ValueChanged<String> onQuery;
  final ValueChanged<ConversationHistorySession> onSelect;
  final String emptyText;
  final String searchHint;

  const HistorySessionList({
    super.key,
    required this.sessions,
    required this.searchController,
    required this.onQuery,
    required this.onSelect,
    required this.emptyText,
    this.searchHint = 'Search',
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        VSearchField(controller: searchController, hint: searchHint, onChanged: onQuery),
        const SizedBox(height: VSpace.xs),
        Flexible(
          // PRD R21: Nothing listed is shown as nothing: no empty box when nothing matches.
          child: sessions.isEmpty ? const SizedBox.shrink() : HistoryRows(sessions: sessions, onSelect: onSelect),
        ),
      ],
    );
  }
}

/// Conversations under the day they belong to, as every chat app lists them: an auto-named title on one line, and when.
class HistoryRows extends StatelessWidget {
  final List<ConversationHistorySession> sessions;
  final ValueChanged<ConversationHistorySession> onSelect;
  const HistoryRows({super.key, required this.sessions, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final sorted = [...sessions]..sort((a, b) => b.timestamp.compareTo(a.timestamp));
    final rows = <Widget>[];
    String? group;
    for (final s in sorted) {
      final t = s.timestamp;
      final days = today.difference(DateTime(t.year, t.month, t.day)).inDays;
      final g = days <= 0 ? 'Today' : (days == 1 ? 'Yesterday' : (days <= 7 ? 'Previous 7 Days' : 'Older'));
      if (g != group) {
        group = g;
        rows.add(Padding(
          padding: EdgeInsets.fromLTRB(6, rows.isEmpty ? 2 : 10, 6, 2),
          child: Text(g, style: VType.caption(color: VColors.textTertiary, weight: FontWeight.w600)),
        ));
      }
      final displayTitle = autoNameConversationTitle(s.title, s.summary);
      rows.add(VHistoryRow(title: displayTitle, onTap: () => onSelect(s)));
    }
    return EdgeFade(
      fadeHeight: 10,
      child: ListView(shrinkWrap: true, physics: const BouncingScrollPhysics(), padding: EdgeInsets.zero, children: rows),
    );
  }
}

/// The History pane's list (history_pane.dart): conversations under their day, an auto-named title each, the one being
/// previewed lit. Scrolls within the pane.
class VHistoryRowsGrouped extends StatelessWidget {
  final List<ConversationHistorySession> sessions;
  final String? selectedId;
  final ValueChanged<ConversationHistorySession> onSelect;
  const VHistoryRowsGrouped({super.key, required this.sessions, required this.onSelect, this.selectedId});

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final sorted = [...sessions]..sort((a, b) => b.timestamp.compareTo(a.timestamp));
    final rows = <Widget>[];
    String? group;
    for (final s in sorted) {
      final t = s.timestamp;
      final days = today.difference(DateTime(t.year, t.month, t.day)).inDays;
      final g = days <= 0 ? 'Today' : (days == 1 ? 'Yesterday' : (days <= 7 ? 'Previous 7 Days' : 'Older'));
      if (g != group) {
        group = g;
        rows.add(Padding(
          padding: EdgeInsets.fromLTRB(8, rows.isEmpty ? 2 : 8, 8, 2),
          child: Text(g, style: VType.caption(color: VColors.textTertiary, weight: FontWeight.w600).copyWith(fontSize: 9.5)),
        ));
      }
      final on = s.id == selectedId;
      final displayTitle = autoNameConversationTitle(s.title, s.summary);
      rows.add(AnimatedContainer(
        duration: VMotion.fast,
        margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
        decoration: BoxDecoration(color: on ? VColors.fillActive : Colors.transparent, borderRadius: BorderRadius.circular(10)),
        child: VHistoryRow(title: displayTitle, onTap: () => onSelect(s)),
      ));
    }
    return VFadeScroll(padding: const EdgeInsets.fromLTRB(2, 0, 2, 6), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: rows));
  }
}

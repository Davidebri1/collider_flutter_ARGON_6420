import 'package:material_ui/material_ui.dart';
import '../../core/vision/vision_kit.dart';
import 'contextual_side_nav.dart';

/// One affordance on the side nav. [key] is what the surface acts on.
class SideRailEntry {
  final String key;
  final IconData icon;
  final String label;
  const SideRailEntry(this.key, this.icon, this.label);
}

/// Master Spec §6.2 & PRD R15 / R21:
/// - The side nav reshapes to the active work surface.
/// - Search lives on the side nav for every view using a side nav bar and is contextually scoped to that view.
/// - On the ticker (chat): New Chat, Search, History.
List<SideRailEntry> sideRailEntries(ActiveWorkSurface s) => switch (s) {
      ActiveWorkSurface.chat => const [
          SideRailEntry('new', Icons.add_rounded, 'New Chat'),
          SideRailEntry('search', Icons.search_rounded, 'Search'),
          SideRailEntry('history', Icons.history_rounded, 'History'),
        ],
      ActiveWorkSurface.smartgen => const [
          SideRailEntry('search', Icons.search_rounded, 'Search'),
          SideRailEntry('cards', Icons.style_rounded, 'Cards'),
          SideRailEntry('boards', Icons.dashboard_rounded, 'Boards'),
          SideRailEntry('canvas', Icons.crop_free_rounded, 'Canvas'),
          SideRailEntry('genie', Icons.assistant_rounded, 'Genie'),
          SideRailEntry('new', Icons.add_rounded, 'New Card'),
        ],
      ActiveWorkSurface.market => const [
          SideRailEntry('search', Icons.search_rounded, 'Search'),
          SideRailEntry('discover', Icons.explore_outlined, 'Discover'),
          SideRailEntry('gallery', Icons.collections_outlined, 'My Gallery'),
        ],
      ActiveWorkSurface.themes => const [
          SideRailEntry('search', Icons.search_rounded, 'Search'),
          SideRailEntry('premium', Icons.workspace_premium_rounded, 'Premium Theme Market'),
          SideRailEntry('gallery', Icons.collections_rounded, 'Theme Gallery'),
        ],
      ActiveWorkSurface.browser => const [
          SideRailEntry('search', Icons.search_rounded, 'Search'),
          SideRailEntry('tabs', Icons.tab_rounded, 'Tabs'),
          SideRailEntry('engine', Icons.travel_explore_rounded, 'Search Engine'),
        ],
      ActiveWorkSurface.files => const [
          SideRailEntry('search', Icons.search_rounded, 'Search'),
          SideRailEntry('all', Icons.folder_open_rounded, 'All Files'),
          SideRailEntry('artifacts', Icons.description_outlined, 'Artifacts'),
          SideRailEntry('attachments', Icons.attach_file_rounded, 'Attachments'),
          SideRailEntry('outputs', Icons.output_rounded, 'Model Outputs'),
          SideRailEntry('system', Icons.settings_suggest_outlined, 'System'),
        ],
    };

/// Vertical tab-bar ornament on the left edge, as in every visionOS app.
class SideNavRail extends StatelessWidget {
  final ActiveWorkSurface surface;
  final String? activeKey;
  final ValueChanged<String> onSelect;
  final bool compact;

  const SideNavRail({
    super.key,
    required this.surface,
    required this.activeKey,
    required this.onSelect,
    this.compact = true,
  });

  @override
  Widget build(BuildContext context) {
    final entries = sideRailEntries(surface);
    return AnimatedSwitcher(
      duration: VMotion.base,
      child: VOrnamentRail(
        key: ValueKey(surface),
        size: compact ? 36 : 40,
        items: [for (final e in entries) VRailItem(e.icon, e.label)],
        active: entries.indexWhere((e) => e.key == activeKey),
        onSelect: (i) => onSelect(entries[i].key),
      ),
    );
  }
}

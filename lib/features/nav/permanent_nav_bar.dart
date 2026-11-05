import 'package:material_ui/material_ui.dart';
import '../../core/vision/vision_kit.dart';

/// REQ-12 Permanent 3-Icon Bottom Dock — styled to match the Side Nav Rail's
/// elevated glass capsule, circular button geometry, spacing, and emissive polish.
/// Uses full-colored solid Material icons in sensible order: Chat / Home, Apps, Settings (Gear).
class PermanentNavBar extends StatelessWidget {
  final bool isComposerSummoned;
  final VoidCallback onToggleComposer;
  final VoidCallback onHome;
  final VoidCallback onApps;
  final VoidCallback onSettings;
  final String? activeDrawer;

  const PermanentNavBar({
    super.key,
    required this.isComposerSummoned,
    required this.onToggleComposer,
    required this.onHome,
    required this.onApps,
    required this.onSettings,
    this.activeDrawer,
  });

  Widget _item({
    required IconData icon,
    required String label,
    required Color color,
    required bool selected,
    required VoidCallback onTap,
    required bool compact,
  }) {
    final btnSize = compact ? 38.0 : 42.0;
    return Semantics(
      button: true,
      label: label,
      child: VPress(
        onTap: onTap,
        tooltip: label,
        child: AnimatedContainer(
          duration: VMotion.fast,
          width: btnSize,
          height: btnSize,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withValues(alpha: selected ? 0.30 : 0.16),
            border: Border.all(
              color: color.withValues(alpha: selected ? 0.72 : 0.38),
              width: selected ? 0.95 : 0.65,
            ),
            boxShadow: selected ? VShadow.emissive(color, intensity: 0.75) : null,
          ),
          child: Icon(
            icon,
            size: compact ? 19 : 21,
            color: selected ? Colors.white : color,
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 768;
    return GestureDetector(
      onVerticalDragEnd: (details) {
        final velocity = details.primaryVelocity;
        if (velocity == null) return;
        if (velocity < -200 && !isComposerSummoned) {
          onToggleComposer();
        } else if (velocity > 200 && isComposerSummoned) {
          onToggleComposer();
        }
      },
      child: VGlass(
        material: VMaterial.elevated,
        radius: VRadius.full,
        padding: EdgeInsets.symmetric(
          horizontal: compact ? 10 : 12,
          vertical: compact ? 6 : 7,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _item(
              icon: Icons.chat_bubble_rounded,
              label: 'Chat',
              color: VHue.blue,
              selected: (activeDrawer == null && !isComposerSummoned) || isComposerSummoned,
              onTap: onHome,
              compact: compact,
            ),
            SizedBox(width: compact ? 10 : 12),
            _item(
              icon: Icons.grid_view_rounded,
              label: 'Apps',
              color: VHue.orange,
              selected: activeDrawer == 'apps',
              onTap: onApps,
              compact: compact,
            ),
            SizedBox(width: compact ? 10 : 12),
            _item(
              icon: Icons.settings_rounded,
              label: 'Settings',
              color: VHue.green,
              selected: activeDrawer == 'settings',
              onTap: onSettings,
              compact: compact,
            ),
          ],
        ),
      ),
    );
  }
}

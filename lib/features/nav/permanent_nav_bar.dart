import 'package:material_ui/material_ui.dart';
import '../../core/vision/vision_kit.dart';

/// REQ-12 Permanent 3-Icon Bottom Dock — a compact glass capsule ornament
/// (WeChat visionOS 0:639). Swipe up summons the composer, swipe down tucks it.
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

  // Icons stand on the bar itself, white 60%; the current one is white 96% on a light circle.
  Widget _item(IconData icon, String tooltip, bool selected, VoidCallback onTap) => Semantics(
        button: true,
        label: tooltip,
        child: VPress(
          onTap: onTap,
          tooltip: tooltip,
          child: AnimatedContainer(
            duration: VMotion.fast,
            width: 44,
            height: 44,
            decoration: BoxDecoration(shape: BoxShape.circle, color: selected ? const Color(0x29FFFFFF) : Colors.transparent),
            alignment: Alignment.center,
            // each in its own colour (Claude, 2026-10-20), full when it is the current one
            child: Icon(icon, size: 22, color: (vHueFor(icon) ?? Colors.white).withValues(alpha: selected ? 1.0 : 0.78)),
          ),
        ),
      );

  @override
  Widget build(BuildContext context) {
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
      // WeChat visionOS "Tab Bar" at 0.765: 260 x 58 capsule, #2F2F2F 37%, shadow 0/37/36 black 49%.
      child: DecoratedBox(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(VRadius.full),
          boxShadow: const [BoxShadow(color: Color(0x7D000000), blurRadius: 36, offset: Offset(0, 37), spreadRadius: -14)],
        ),
        child: VGlass(
          material: VMaterial.elevated,
          fill: const Color(0x5E2F2F2F),
          radius: VRadius.full,
          shadow: false,
          child: SizedBox(
            width: 260,
            height: 58,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _item(Icons.edit_note_rounded, 'Compose / Home', activeDrawer == null || isComposerSummoned, onHome),
                _item(Icons.tune_rounded, 'Settings', activeDrawer == 'settings', onSettings),
                _item(Icons.apps_rounded, 'Apps', activeDrawer == 'apps', onApps),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

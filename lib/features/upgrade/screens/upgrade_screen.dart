import 'package:material_ui/material_ui.dart';
import '../../../core/vision/vision_kit.dart';

/// Tiers & Entitlements — account-style window (Vision OS Design System
/// 417:8552): close circle, centred title, one grouped card per tier.
class UpgradeScreen extends StatelessWidget {
  final VoidCallback onClose;

  const UpgradeScreen({super.key, required this.onClose});

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        VScrim(onTap: onClose),
        SafeArea(
          child: Align(
            alignment: Alignment.topCenter,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(VSpace.md, 40, VSpace.md, 0),
              child: VWindow(
                title: 'Tiers & Entitlements',
                centerTitle: true,
                maxWidth: VOverlay.menuWidth(context),
                maxHeight: VOverlay.menuMaxHeight(context),
                leading: VCircleButton(icon: Icons.close_rounded, tooltip: 'Close', onTap: onClose),
                child: VFadeScroll(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _tier('Free Tier', '\$0', 'Current Plan', false, const [
                        '5 Free models (GPT-5 Nano, Gemini Flash Lite, etc.)',
                        '50 Daily queries',
                        'Standard single-stream consensus',
                        'Curated Live Wallpaper themes',
                      ]),
                      const SizedBox(height: VSpace.sm),
                      _tier('Pro Tier', '\$19 / mo', 'Upgrade to Pro', true, const [
                        'Unlock all Pro Writing & General models',
                        'Parallel multi-model streaming up to 6 models',
                        'Interactive 3D Consensus View',
                        'SmartGen Boards, Canvas & Genie synthesis',
                        '2,000 monthly credits',
                      ]),
                      const SizedBox(height: VSpace.sm),
                      _tier('Elite Tier', '\$49 / mo', 'Upgrade to Elite', false, const [
                        'All Pro capabilities + 9-model comparison grid',
                        'Full 120 FPS high-fidelity spatial glass effects',
                        'Unlimited Smart Gen household projects',
                        '10,000 monthly credits',
                        'Instant priority model responses',
                      ]),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _tier(String name, String price, String cta, bool featured, List<String> features) {
    return Container(
      padding: const EdgeInsets.all(VSpace.md),
      decoration: BoxDecoration(
        color: featured ? VColors.overlayLight : VColors.fillCell,
        borderRadius: BorderRadius.circular(VRadius.lg),
        border: Border.all(color: featured ? VColors.borderHeavy : Colors.transparent, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Expanded(child: Text(name, style: VType.headline())),
            Text(price, style: VType.headline()),
          ]),
          const SizedBox(height: VSpace.xs),
          for (final f in features)
            Padding(
              padding: const EdgeInsets.only(bottom: VSpace.xxs),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Padding(
                  padding: EdgeInsets.only(top: 2),
                  child: Icon(Icons.check_rounded, size: 15, color: VColors.textSecondary),
                ),
                const SizedBox(width: VSpace.xs),
                Expanded(child: Text(f, style: VType.footnote())),
              ]),
            ),
          const SizedBox(height: VSpace.sm),
          VButton(
            label: cta,
            dense: true,
            expand: true,
            variant: featured ? VButtonVariant.primary : VButtonVariant.secondary,
            onTap: () {},
          ),
        ],
      ),
    );
  }
}

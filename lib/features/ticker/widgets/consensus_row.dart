import 'package:material_ui/material_ui.dart';
import '../../../core/vision/vision_kit.dart';
import 'model_pill.dart';

/// The consensus, first line of the ticker. Rewritten by Claude (2026-10-23): a line in the window's list like the model
/// rows, no box of its own, no words that were not asked for. The score leads its words, coloured red to green by how
/// many agree; two lines are kept for the words; tapping opens the consensus map.
class ConsensusRow extends StatelessWidget {
  final String agreementRatio;
  final String summary;
  final bool isGenerating;
  final VoidCallback? onGenerateConsensus;
  final VoidCallback? onTap;

  const ConsensusRow({
    super.key,
    required this.agreementRatio,
    required this.summary,
    this.onGenerateConsensus,
    this.onTap,
    this.isGenerating = false,
  });

  @override
  Widget build(BuildContext context) {
    final score = agreementRatio.replaceAll('Consensus', '').trim();
    final m = RegExp(r'^(\d+)\s*/\s*(\d+)$').firstMatch(score);
    final double? agree = m == null || int.parse(m.group(2)!) == 0 ? null : int.parse(m.group(1)!) / int.parse(m.group(2)!);
    final Color ink = agree == null ? VColors.textTertiary : HSVColor.fromAHSV(1, 120 * agree.clamp(0.0, 1.0), 0.6, 1).toColor();
    return VPress(
      onTap: onTap ?? onGenerateConsensus,
      child: Container(
        color: const Color(0x00000000),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: SizedBox(
          height: 30,
          width: double.infinity,
          child: Text.rich(
            TextSpan(children: [
              TextSpan(
                text: agree == null ? '–/–' : score,
                style: VType.caption(color: ink, weight: FontWeight.w700).copyWith(fontSize: 11, height: 15 / 11),
              ),
              if (summary.isNotEmpty) TextSpan(text: '   $summary', style: VOneLine.rowStyle.copyWith(color: VColors.textPrimary)),
            ]),
            maxLines: 2,
            overflow: TextOverflow.fade,
          ),
        ),
      ),
    );
  }
}

/// The hairline under the consensus: one line of light across the column, fading out at both ends.
class TickerDivider extends StatelessWidget {
  const TickerDivider({super.key});
  @override
  Widget build(BuildContext context) => Container(
        height: 1,
        margin: const EdgeInsets.symmetric(horizontal: ModelPill.radius / 2, vertical: 4),
        decoration: const BoxDecoration(
          gradient: LinearGradient(colors: [Color(0x00FFFFFF), Color(0x24FFFFFF), Color(0x24FFFFFF), Color(0x00FFFFFF)], stops: [0, 0.2, 0.8, 1]),
        ),
      );
}

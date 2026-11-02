import 'package:material_ui/material_ui.dart';
import '../../../models/ticker_item.dart';
import '../../../core/vision/vision_kit.dart';

/// One model's row in the ticker. Rewritten by Claude (2026-10-23) after David: "rectangles in rectangles spaced apart,
/// looks like cardboard cut outs" and "something very off" about the colour.
/// A row is a line in a list on the window's glass, not a card of its own: no box, border, glow or tint. The open row is
/// lit by one capsule of light whose corners follow the window's (concentric). A selected model's name is bright; a
/// model that is not selected is dim and shows its name only.
class ModelPill extends StatefulWidget {
  final TickerItem item;

  /// This model's conversation is the one open beside the column.
  final bool isExpanded;
  final VoidCallback onToggleExpand;
  final double elevation; // kept for callers; rows no longer differ by height
  final bool compact;

  /// Selected: questions go to this model.
  final bool isActive;

  const ModelPill({
    super.key,
    required this.item,
    required this.isExpanded,
    required this.onToggleExpand,
    this.elevation = 0,
    this.compact = false,
    this.isActive = true,
  });

  /// The lit row's corners: the window's corner less the window's inner margin, so the two curves run together.
  static const double radius = VRadius.card - VSpace.xs;

  @override
  State<ModelPill> createState() => _ModelPillState();
}

class _ModelPillState extends State<ModelPill> {
  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    final active = widget.isActive;
    final waiting = active && item.isStreaming;
    final name = VType.caption(color: active ? VColors.textPrimary : VColors.textTertiary, weight: FontWeight.w600)
        .copyWith(fontSize: 11, height: 14 / 11);
    final time = VType.caption(color: VColors.textTertiary, weight: FontWeight.w500).copyWith(fontSize: 11, height: 14 / 11);
    final hasSummary = active && (item.summary.isNotEmpty || waiting);

    return VPress(
      onTap: widget.onToggleExpand,
      child: AnimatedContainer(
        duration: VMotion.base,
        curve: Curves.easeOutCubic,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: widget.isExpanded ? const Color(0x24FFFFFF) : const Color(0x00FFFFFF),
          borderRadius: BorderRadius.circular(ModelPill.radius),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(children: [
              Expanded(child: Text(item.modelDef.label, maxLines: 1, softWrap: false, overflow: TextOverflow.fade, style: name)),
              if (active && !waiting && !widget.compact && item.relativeTime.isNotEmpty) Text(item.relativeTime, style: time),
            ]),
            if (hasSummary) ...[
              const SizedBox(height: 2),
              // Two lines kept for the summary; the open row shows it whole.
              AnimatedSize(
                duration: VMotion.base,
                curve: Curves.easeOutCubic,
                alignment: Alignment.topCenter,
                child: SizedBox(
                  height: widget.isExpanded && item.summary.isNotEmpty ? null : 30,
                  width: double.infinity,
                  child: waiting && item.summary.isEmpty
                      ? const _SkeletonLines()
                      : Text(item.summary,
                          maxLines: widget.isExpanded ? null : 2,
                          overflow: widget.isExpanded ? null : TextOverflow.fade,
                          style: VOneLine.rowStyle.copyWith(color: VColors.textSecondary)),
                ),
              ),
            ],
            if (active && item.mediaUrls != null && item.mediaUrls!.isNotEmpty) ...[
              const SizedBox(height: VSpace.xs),
              SizedBox(
                height: 58,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: item.mediaUrls!.length,
                  separatorBuilder: (_, __) => const SizedBox(width: VSpace.xs),
                  itemBuilder: (_, i) => ClipRRect(
                    borderRadius: BorderRadius.circular(VRadius.sm),
                    child: Image.network(item.mediaUrls![i], width: 58, height: 58, fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => const SizedBox(width: 58, height: 58)),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Two soft lines, breathing, until the summary arrives.
class _SkeletonLines extends StatefulWidget {
  const _SkeletonLines();
  @override
  State<_SkeletonLines> createState() => _SkeletonLinesState();
}

class _SkeletonLinesState extends State<_SkeletonLines> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1600))..repeat(reverse: true);

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Widget line(double w) => FractionallySizedBox(
          widthFactor: w,
          alignment: Alignment.centerLeft,
          child: Container(
            height: 7,
            margin: const EdgeInsets.symmetric(vertical: 4),
            decoration: BoxDecoration(color: const Color(0x2EFFFFFF), borderRadius: BorderRadius.circular(4)),
          ),
        );
    return FadeTransition(
      opacity: Tween(begin: 0.45, end: 1.0).animate(CurvedAnimation(parent: _c, curve: Curves.easeInOut)),
      child: Column(mainAxisSize: MainAxisSize.min, children: [line(0.86), line(0.58)]),
    );
  }
}

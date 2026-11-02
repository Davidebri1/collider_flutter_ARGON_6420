import 'package:material_ui/material_ui.dart';

/// Where a list keeps its focus, so its fades tell which way the content runs.
/// top: the list starts at the top and runs away downwards (history, files); the far end dissolves over a long run.
/// bottom: the newest is at the bottom and older content recedes upwards (a conversation).
/// center: both ends recede alike.
enum FadeFocus { top, center, bottom }

/// Content dissolving into the room at the edges of a scroll view. Rewritten by Claude (2026-10-20).
///
/// David, 20 Oct: "your edge fades have corners, and are uniformly square. very fake looking and too edge bound ...
/// the idea isnt to fade the list equally. you fade above and below and keep the middle. or otherwise: fade bottom
/// option graduating up to the focus top. and vice versa. always tell a realistic physical story."
/// Apple (Scroll views): edge effects mark where content continues; "Scroll edge effects aren't decorative."
///
/// So an edge fades only where there is more content past it, and the fade grows as the content goes out of view
/// (at rest the first row is crisp). The ramp is eased, not linear, so there is no visible band and no corner where
/// it starts; its length follows the size of the view instead of a few pixels at the rim, and the end away from the
/// focus recedes over a longer run than the end at the focus. It is only a mask: no tint, no box, no blur.
class EdgeFade extends StatefulWidget {
  final Widget child;

  /// The shortest ramp, in logical pixels; the ramp grows with the view.
  final double fadeHeight;
  final bool fadeTop;
  final bool fadeBottom;
  final FadeFocus focus;
  final Axis axis;

  const EdgeFade({
    super.key,
    required this.child,
    this.fadeHeight = 18.0,
    this.fadeTop = true,
    this.fadeBottom = true,
    this.focus = FadeFocus.center,
    this.axis = Axis.vertical,
  });

  @override
  State<EdgeFade> createState() => _EdgeFadeState();
}

class _EdgeFadeState extends State<EdgeFade> {
  // How much content lies beyond each end, in pixels; null until the scroll view has reported.
  final ValueNotifier<(double, double)?> _beyond = ValueNotifier(null);

  bool _onMetrics(ScrollMetrics m) {
    if (m.axis != widget.axis) return false;
    final next = (m.extentBefore, m.extentAfter);
    final now = _beyond.value;
    if (now == null || (now.$1 - next.$1).abs() > 0.5 || (now.$2 - next.$2).abs() > 0.5) _beyond.value = next;
    return false;
  }

  @override
  void dispose() {
    _beyond.dispose();
    super.dispose();
  }

  /// A smooth ramp from the edge to fully shown, sampled so the gradient has no visible start line.
  static const _ease = [0.0, 0.06, 0.2, 0.42, 0.66, 0.86, 1.0];

  @override
  Widget build(BuildContext context) {
    if (!widget.fadeTop && !widget.fadeBottom) return widget.child;
    final listened = NotificationListener<ScrollMetricsNotification>(
      onNotification: (n) => n.depth == 0 ? _onMetrics(n.metrics) : false,
      child: NotificationListener<ScrollNotification>(
        onNotification: (n) => n.depth == 0 ? _onMetrics(n.metrics) : false,
        child: widget.child,
      ),
    );
    return ValueListenableBuilder<(double, double)?>(
      valueListenable: _beyond,
      child: listened,
      builder: (context, beyond, child) {
        return ShaderMask(
          blendMode: BlendMode.dstIn,
          shaderCallback: (rect) {
            final vertical = widget.axis == Axis.vertical;
            final size = vertical ? rect.height : rect.width;
            if (size <= 0) return const LinearGradient(colors: [Colors.white, Colors.white]).createShader(rect);
            // ramp lengths: about an eighth of the view, the end away from the focus about a third
            final base = (size * 0.12).clamp(widget.fadeHeight, 72.0);
            final long = (size * 0.32).clamp(base, 220.0);
            final lead = widget.focus == FadeFocus.bottom ? long : base; // top end
            final tail = widget.focus == FadeFocus.top ? long : base; // bottom end
            // strength: 0 when nothing lies beyond that end, full once a ramp's worth has gone past it
            final before = beyond?.$1 ?? 0, after = beyond?.$2 ?? 0;
            final sTop = widget.fadeTop ? (before / base).clamp(0.0, 1.0) : 0.0;
            final sBottom = widget.fadeBottom ? (after / base).clamp(0.0, 1.0) : 0.0;
            final a = (lead / size).clamp(0.0, 0.45), b = (tail / size).clamp(0.0, 0.45);
            final stops = <double>[], colors = <Color>[];
            for (var i = 0; i < _ease.length; i++) {
              stops.add(a * i / (_ease.length - 1));
              colors.add(Colors.white.withValues(alpha: 1 - sTop * (1 - _ease[i])));
            }
            for (var i = _ease.length - 1; i >= 0; i--) {
              stops.add(1 - b * i / (_ease.length - 1));
              colors.add(Colors.white.withValues(alpha: 1 - sBottom * (1 - _ease[i])));
            }
            return LinearGradient(
              begin: vertical ? Alignment.topCenter : Alignment.centerLeft,
              end: vertical ? Alignment.bottomCenter : Alignment.centerRight,
              colors: colors,
              stops: stops,
            ).createShader(rect);
          },
          child: child,
        );
      },
    );
  }
}

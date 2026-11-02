import 'dart:math' as math;
import 'dart:ui';
import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';
import '../theme/edge_fade.dart';
import 'vision_tokens.dart';
import 'hues.dart';

export 'package:cupertino_ui/cupertino_ui.dart'
    show
        CupertinoIcons,
        CupertinoSwitch,
        CupertinoSlidingSegmentedControl,
        CupertinoSearchTextField,
        CupertinoScrollbar,
        CupertinoActivityIndicator,
        CupertinoButton,
        CupertinoColors;
export 'vision_tokens.dart';
export 'hues.dart';
export '../theme/edge_fade.dart';
export 'md_text.dart';
export 'detail_view.dart';

/// Glass material levels, mapped to the Collider depth planes.
enum VMaterial { prompt, resting, elevated, modal, work }

extension VMaterialX on VMaterial {
  Color get fill => switch (this) {
        VMaterial.prompt => VColors.glassPrompt,
        VMaterial.resting => VColors.glassResting,
        VMaterial.elevated => VColors.glassElevated,
        VMaterial.modal => VColors.glassModal,
        VMaterial.work => VColors.glassWork,
      };
  double get blur => 28;

  /// Pane glass carries a top highlight; kit glass carries the kit hairline.
  bool get pane => this == VMaterial.prompt || this == VMaterial.resting;
  Color get rim => switch (this) {
        VMaterial.prompt || VMaterial.resting => const Color(0x2EFFFFFF),
        VMaterial.elevated => const Color(0x3DFFFFFF),
        VMaterial.modal => const Color(0x47FFFFFF),
        VMaterial.work => const Color(0x52FFFFFF),
      };
  List<BoxShadow> get shadow => pane ? VShadow.pane : VShadow.ornament;
}

/// Saturation 1.6: the colour of what is behind the glass comes through it.
const List<double> _vibrancy = <double>[
  1.4724, -0.4288, -0.0436, 0, 0,
  -0.1276, 1.1712, -0.0436, 0, 0,
  -0.1276, -0.4288, 1.5564, 0, 0,
  0, 0, 0, 1, 0,
];

/// One-pass glass surface: blur + material fill + hairline + specular rim.
/// Never nest a VGlass inside another VGlass; use plain fills inside.
class VGlass extends StatelessWidget {
  final Widget child;
  final VMaterial material;
  final double radius;
  final EdgeInsetsGeometry padding;
  final Color? fill;
  final bool shadow;

  const VGlass({
    super.key,
    required this.child,
    this.material = VMaterial.resting,
    this.radius = VRadius.card,
    this.padding = EdgeInsets.zero,
    this.fill,
    this.shadow = true,
  });

  @override
  Widget build(BuildContext context) {
    final r = BorderRadius.circular(radius);
    return DecoratedBox(
      decoration: BoxDecoration(borderRadius: r, boxShadow: shadow ? material.shadow : null),
      child: ClipRRect(
        borderRadius: r,
        child: BackdropFilter(
          filter: ImageFilter.compose(
            outer: const ColorFilter.matrix(_vibrancy),
            inner: ImageFilter.blur(sigmaX: material.blur, sigmaY: material.blur),
          ),
          child: CustomPaint(
            foregroundPainter: VGlassStroke(radius: radius, pane: material.pane),
            child: Container(
              padding: padding,
              decoration: BoxDecoration(color: fill ?? material.fill, borderRadius: r),
              child: child,
            ),
          ),
        ),
      ),
    );
  }
}

/// The hairline of a glass surface.
class VGlassStroke extends CustomPainter {
  final double radius;
  final bool pane;
  const VGlassStroke({required this.radius, this.pane = false});

  @override
  void paint(Canvas canvas, Size size) {
    final w = pane ? 1.0 : 1.4;
    final rect = Offset.zero & size;
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = w
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: pane
            ? const [Color(0x99FFFFFF), Color(0x00FFFFFF), Color(0x00FFFFFF), Color(0x1AFFFFFF)]
            : const [Color(0x66FFFFFF), Color(0x00FFFFFF), Color(0x00FFFFFF), Color(0x1AFFFFFF)],
        stops: pane ? const [0, 0.18, 0.8, 1] : const [0, 0.41, 0.57, 1],
      ).createShader(rect);
    final r = (radius - w / 2).clamp(0.0, size.shortestSide / 2);
    canvas.drawRRect(RRect.fromRectAndRadius(rect.deflate(w / 2), Radius.circular(r)), paint);
  }

  @override
  bool shouldRepaint(covariant VGlassStroke old) => old.radius != radius || old.pane != pane;
}

/// Recessed capsule (prompt capsule, Safari address bar).
class VRecessed extends StatelessWidget {
  final Widget child;
  final double radius;
  final EdgeInsetsGeometry padding;
  final double? height;
  const VRecessed({super.key, required this.child, this.radius = VRadius.full, this.padding = EdgeInsets.zero, this.height});

  @override
  Widget build(BuildContext context) {
    final r = BorderRadius.circular(radius);
    return CustomPaint(
      foregroundPainter: _RecessedEdge(radius),
      child: Container(
        height: height,
        padding: padding,
        decoration: BoxDecoration(
          borderRadius: r,
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0x73000000), Color(0x4D000000), Color(0x4D000000)],
            stops: [0, 0.35, 1],
          ),
        ),
        child: child,
      ),
    );
  }
}

class _RecessedEdge extends CustomPainter {
  final double radius;
  const _RecessedEdge(this.radius);

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1
      ..shader = const LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [Color(0x00FFFFFF), Color(0x00FFFFFF), Color(0x80FFFFFF)],
        stops: [0, 0.6, 1],
      ).createShader(rect);
    final r = (radius - 0.5).clamp(0.0, size.shortestSide / 2);
    canvas.drawRRect(RRect.fromRectAndRadius(rect.deflate(0.5), Radius.circular(r)), paint);
  }

  @override
  bool shouldRepaint(covariant _RecessedEdge old) => old.radius != radius;
}

/// Click-away layer behind an overlay.
class VScrim extends StatelessWidget {
  final VoidCallback? onTap;
  final bool blur;
  final bool soft;

  const VScrim({super.key, this.onTap, this.blur = true, this.soft = false});

  @override
  Widget build(BuildContext context) {
    final dim = Container(color: soft ? const Color(0x14000000) : VOverlay.scrim);
    if (!blur || soft) {
      return GestureDetector(
        onTap: onTap,
        behavior: HitTestBehavior.opaque,
        child: dim,
      );
    }
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: ClipRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: VBlur.medium, sigmaY: VBlur.medium),
          child: dim,
        ),
      ),
    );
  }
}

/// Press physics from the kit: scale 0.97, look glow on hover/press.
class VPress extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final String? tooltip;
  final double minHitSize;
  const VPress({
    super.key,
    required this.child,
    this.onTap,
    this.tooltip,
    this.minHitSize = 0,
  });

  @override
  State<VPress> createState() => _VPressState();
}

class _GlowPainter extends CustomPainter {
  final ValueNotifier<Offset?> at;
  final Animation<double> amount;
  _GlowPainter(this.at, this.amount) : super(repaint: Listenable.merge([at, amount]));

  @override
  void paint(Canvas canvas, Size size) {
    final a = amount.value;
    if (a <= 0.001 || size.isEmpty) return;
    final c = at.value ?? size.center(Offset.zero);
    final r = (size.longestSide * 0.7).clamp(22.0, 180.0);
    final radius = Radius.circular((size.shortestSide / 2).clamp(0.0, 22.0));
    canvas.save();
    canvas.clipRRect(RRect.fromRectAndRadius(Offset.zero & size, radius));
    canvas.drawCircle(
      c,
      r,
      Paint()
        ..blendMode = BlendMode.plus
        ..shader = RadialGradient(
          colors: [
            Colors.white.withValues(alpha: 0.2 * a),
            Colors.white.withValues(alpha: 0.07 * a),
            Colors.white.withValues(alpha: 0),
          ],
          stops: const [0, 0.45, 1],
        ).createShader(Rect.fromCircle(center: c, radius: r)),
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(_GlowPainter old) => false;
}

class _VPressState extends State<VPress> with SingleTickerProviderStateMixin {
  bool _down = false;
  bool _over = false;
  final ValueNotifier<Offset?> _at = ValueNotifier(null);
  late final AnimationController _glow = AnimationController(vsync: this, duration: const Duration(milliseconds: 220));

  void _light() => _glow.animateTo(
        _down ? 1.0 : (_over ? 0.6 : 0.0),
        duration: Duration(milliseconds: _down ? 90 : 320),
        curve: _down ? Curves.easeOut : Curves.easeOutCubic,
      );

  @override
  void dispose() {
    _glow.dispose();
    _at.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final enabled = widget.onTap != null;
    Widget inner = AnimatedScale(
      scale: _down ? VMotion.pressedScale : 1,
      duration: _down ? VMotion.fast : const Duration(milliseconds: 340),
      curve: _down ? Curves.easeOutCubic : Curves.easeOutBack,
      child: CustomPaint(foregroundPainter: _GlowPainter(_at, _glow), child: widget.child),
    );
    if (widget.minHitSize > 0) {
      inner = ConstrainedBox(
        constraints: BoxConstraints(minWidth: widget.minHitSize, minHeight: widget.minHitSize),
        child: Center(widthFactor: 1, heightFactor: 1, child: inner),
      );
    }
    Widget w = MouseRegion(
      cursor: enabled ? SystemMouseCursors.click : SystemMouseCursors.basic,
      onEnter: enabled
          ? (e) {
              _over = true;
              _at.value = e.localPosition;
              _light();
            }
          : null,
      onHover: enabled ? (e) => _at.value = e.localPosition : null,
      onExit: enabled
          ? (_) {
              _over = false;
              _light();
            }
          : null,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: widget.onTap,
        onTapDown: enabled
            ? (d) {
                _at.value = d.localPosition;
                setState(() => _down = true);
                _light();
                HapticFeedback.selectionClick();
              }
            : null,
        onTapUp: enabled
            ? (_) {
                setState(() => _down = false);
                _light();
              }
            : null,
        onTapCancel: enabled
            ? () {
                setState(() => _down = false);
                _light();
              }
            : null,
        child: inner,
      ),
    );
    if (widget.tooltip != null && widget.tooltip!.isNotEmpty) {
      w = Tooltip(
        message: widget.tooltip!,
        excludeFromSemantics: true,
        waitDuration: const Duration(milliseconds: 550),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: const Color(0xEB141620),
          borderRadius: BorderRadius.circular(VRadius.full),
          border: Border.all(color: const Color(0x38FFFFFF), width: 0.6),
          boxShadow: VShadow.subtle,
        ),
        textStyle: VType.caption(color: VColors.textPrimary, weight: FontWeight.w500),
        child: w,
      );
    }
    return w;
  }
}

/// Circular glass icon button (close, back, more, rail and dock items).
class VCircleButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onTap;
  final double size;
  final bool selected;
  final bool floating; // own blur when floating directly over the wallpaper
  final String? tooltip;
  final Color? iconColor;

  const VCircleButton({
    super.key,
    required this.icon,
    this.onTap,
    this.size = 36,
    this.selected = false,
    this.floating = false,
    this.tooltip,
    this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    final core = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: selected ? VColors.fillActive : (floating ? VColors.glassElevated : VColors.fillCell),
        border: Border.all(color: selected ? const Color(0x4DFFFFFF) : const Color(0x22FFFFFF), width: 0.6),
      ),
      alignment: Alignment.center,
      child: Icon(
        icon,
        size: size * 0.46,
        color: iconColor ?? vHueFor(icon) ?? (selected ? VColors.textPrimary : VColors.textSecondary),
      ),
    );
    final body = floating
        ? ClipOval(
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: VBlur.medium, sigmaY: VBlur.medium),
              child: core,
            ),
          )
        : core;
    return Semantics(
      button: true,
      label: tooltip,
      child: VPress(onTap: onTap, tooltip: tooltip, child: body),
    );
  }
}

enum VButtonVariant { primary, secondary, ghost, destructive }

/// Kit Button: height 48 (36 dense), capsule, label 15/500.
class VButton extends StatelessWidget {
  final String label;
  final IconData? icon;
  final VoidCallback? onTap;
  final VButtonVariant variant;
  final bool dense;
  final bool expand;

  const VButton({
    super.key,
    required this.label,
    this.icon,
    this.onTap,
    this.variant = VButtonVariant.secondary,
    this.dense = false,
    this.expand = false,
  });

  @override
  Widget build(BuildContext context) {
    final (Color bg, Color fg, Color border) = switch (variant) {
      VButtonVariant.primary => (VColors.accentBlue, Colors.white, Colors.transparent),
      VButtonVariant.destructive => (VColors.accentRed, Colors.white, Colors.transparent),
      VButtonVariant.secondary => (VColors.overlayLight, VColors.textPrimary, VColors.borderLight),
      VButtonVariant.ghost => (Colors.transparent, VColors.textPrimary, Colors.transparent),
    };
    final h = dense ? 36.0 : 48.0;
    return VPress(
      onTap: onTap,
      child: Container(
        height: h,
        width: expand ? double.infinity : null,
        padding: EdgeInsets.symmetric(horizontal: dense ? VSpace.md : VSpace.lg),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(VRadius.full),
          border: Border.all(color: border, width: 0.5),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (icon != null) ...[
              Icon(icon, size: dense ? 15 : 17, color: fg),
              const SizedBox(width: VSpace.xs - 2),
            ],
            Flexible(
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: VType.callout(color: fg, weight: FontWeight.w600).copyWith(fontSize: dense ? VType.sm : VType.md),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Floating capsule ornament (dock, toolbars, transport, URL bar).
class VOrnament extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final Axis axis;
  const VOrnament({super.key, required this.child, this.padding = const EdgeInsets.all(6), this.axis = Axis.horizontal});

  @override
  Widget build(BuildContext context) {
    return VGlass(
      material: VMaterial.elevated,
      radius: VRadius.full,
      padding: padding,
      child: child,
    );
  }
}

class VRailItem {
  final IconData icon;
  final String label;
  const VRailItem(this.icon, this.label);
}

/// Side navigation rail: visionOS glass capsule floating beside the main spatial window.
class VOrnamentRail extends StatelessWidget {
  final List<VRailItem> items;
  final int active;
  final ValueChanged<int> onSelect;
  final double size;
  final Set<int> dim;
  const VOrnamentRail({
    super.key,
    required this.items,
    required this.active,
    required this.onSelect,
    this.size = 36,
    this.dim = const {},
  });

  @override
  Widget build(BuildContext context) {
    // visionOS tab bar (Claude, 2026-10-23): a glass capsule beside the window; each place its glyph on a disc, its name
    // under it, the chosen one lit. 11 points, one word to a line.
    return DecoratedBox(
      decoration: BoxDecoration(borderRadius: BorderRadius.circular(VRadius.full), boxShadow: VShadow.ornament),
      child: VGlass(
        material: VMaterial.elevated,
        radius: VRadius.full,
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 10),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            for (int i = 0; i < items.length; i++) ...[
              if (i > 0) const SizedBox(height: 10),
              Semantics(
                button: true,
                label: items[i].label,
                child: VPress(
                  onTap: dim.contains(i) ? null : () => onSelect(i),
                  child: SizedBox(
                    width: 56,
                    child: Column(mainAxisSize: MainAxisSize.min, children: [
                      AnimatedContainer(
                        duration: VMotion.fast,
                        width: 44,
                        height: 44,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(shape: BoxShape.circle, color: i == active ? VColors.fillActive : VColors.fillCell),
                        child: Icon(items[i].icon, size: 20, color: dim.contains(i) ? const Color(0x59FFFFFF) : VColors.textPrimary),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        items[i].label.replaceAll(' ', '\n'),
                        textAlign: TextAlign.center,
                        softWrap: false,
                        overflow: TextOverflow.visible,
                        style: VType.caption(
                          color: dim.contains(i) ? const Color(0x59FFFFFF) : (i == active ? VColors.textPrimary : VColors.textSecondary),
                          weight: FontWeight.w500,
                        ).copyWith(fontSize: 11, height: 13 / 11),
                      ),
                    ]),
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

/// One conversation in a history list: its title on one line and when it was.
class VHistoryRow extends StatelessWidget {
  final String title;
  final String? time;
  final VoidCallback? onTap;
  const VHistoryRow({super.key, required this.title, this.time, this.onTap});

  @override
  Widget build(BuildContext context) {
    return VPress(
      onTap: onTap,
      child: Container(
        color: Colors.transparent,
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
        child: Row(
          children: [
            Expanded(
              child: Text(
                title,
                maxLines: 1,
                softWrap: false,
                overflow: TextOverflow.fade,
                style: VType.callout(weight: FontWeight.w500),
              ),
            ),
            if (time != null) ...[
              const SizedBox(width: 10),
              Text(time!, style: VType.caption(color: VColors.textTertiary)),
            ],
          ],
        ),
      ),
    );
  }
}

/// Segmented capsule (CupertinoSlidingSegmentedControl / spatial segmented track).
class VSegmented extends StatelessWidget {
  final List<String> labels;
  final int active;
  final ValueChanged<int> onSelect;
  final bool ornament; // true: floating glass capsule; false: recessed in-window track
  const VSegmented({
    super.key,
    required this.labels,
    required this.active,
    required this.onSelect,
    this.ornament = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!ornament && labels.length >= 2 && labels.length <= 5) {
      final safeActive = active.clamp(0, labels.length - 1);
      return SizedBox(
        width: double.infinity,
        child: CupertinoSlidingSegmentedControl<int>(
          groupValue: safeActive,
          backgroundColor: VColors.fillRecessed,
          thumbColor: const Color(0x47FFFFFF),
          padding: const EdgeInsets.all(3),
          onValueChanged: (v) {
            if (v != null) onSelect(v);
          },
          children: {
            for (int i = 0; i < labels.length; i++)
              i: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                child: Text(
                  labels[i],
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: VType.callout(
                    color: i == safeActive ? VColors.textPrimary : VColors.textSecondary,
                    weight: i == safeActive ? FontWeight.w600 : FontWeight.w500,
                  ).copyWith(fontSize: 12),
                ),
              ),
          },
        ),
      );
    }

    final row = SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      physics: const BouncingScrollPhysics(),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          for (int i = 0; i < labels.length; i++)
            VPress(
              onTap: () => onSelect(i),
              child: AnimatedContainer(
                duration: VMotion.fast,
                height: 32,
                padding: const EdgeInsets.symmetric(horizontal: VSpace.sm),
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: i == active ? VColors.fillActive : Colors.transparent,
                  borderRadius: BorderRadius.circular(VRadius.full),
                ),
                child: Text(
                  labels[i],
                  style: VType.callout(
                    color: i == active ? VColors.textPrimary : VColors.textSecondary,
                    weight: i == active ? FontWeight.w600 : FontWeight.w500,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
    if (ornament) return VOrnament(padding: const EdgeInsets.all(VSpace.xxs), child: row);
    return Container(
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(color: VColors.fillRecessed, borderRadius: BorderRadius.circular(VRadius.full)),
      child: row,
    );
  }
}

/// Filter chip (capsule).
class VChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback? onTap;
  final Color? dot;
  const VChip({super.key, required this.label, this.selected = false, this.onTap, this.dot});

  @override
  Widget build(BuildContext context) {
    return VPress(
      onTap: onTap,
      child: AnimatedContainer(
        duration: VMotion.fast,
        height: 30,
        padding: const EdgeInsets.symmetric(horizontal: VSpace.sm),
        decoration: BoxDecoration(
          color: selected ? VColors.fillActive : VColors.fillCell,
          borderRadius: BorderRadius.circular(VRadius.full),
          border: Border.all(color: selected ? VColors.borderHeavy : VColors.borderLight, width: 0.5),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (dot != null) ...[
              Container(width: 7, height: 7, decoration: BoxDecoration(shape: BoxShape.circle, color: dot)),
              const SizedBox(width: 6),
            ],
            Text(
              label,
              style: VType.callout(
                color: selected ? VColors.textPrimary : VColors.textSecondary,
                weight: selected ? FontWeight.w600 : FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Recessed capsule search field using CupertinoSearchTextField styling.
class VSearchField extends StatelessWidget {
  final TextEditingController? controller;
  final String hint;
  final ValueChanged<String>? onChanged;
  final double height;
  const VSearchField({super.key, this.controller, required this.hint, this.onChanged, this.height = 36});

  @override
  Widget build(BuildContext context) {
    return VRecessed(
      height: height,
      padding: const EdgeInsets.symmetric(horizontal: VSpace.xs),
      child: Center(
        child: CupertinoSearchTextField(
          controller: controller,
          onChanged: onChanged,
          placeholder: hint,
          backgroundColor: Colors.transparent,
          itemColor: VColors.textTertiary,
          itemSize: 16,
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
          style: VType.callout(weight: FontWeight.w400),
          placeholderStyle: VType.callout(color: VColors.textTertiary, weight: FontWeight.w400),
        ),
      ),
    );
  }
}

/// Grouped list container (account/settings rows).
class VListGroup extends StatelessWidget {
  final List<Widget> children;
  const VListGroup({super.key, required this.children});

  @override
  Widget build(BuildContext context) {
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(color: VColors.fillCell, borderRadius: BorderRadius.circular(VRadius.md)),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (int i = 0; i < children.length; i++) ...[
            if (i > 0) const Divider(height: 0.5, thickness: 0.5, indent: VSpace.md, color: VColors.borderLight),
            children[i],
          ],
        ],
      ),
    );
  }
}

/// List row: leading, title, subtitle, trailing / chevron.
class VListRow extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final String? trailingText;
  final bool chevron;
  final bool selected;
  final VoidCallback? onTap;
  final int subtitleLines;
  final int titleLines;

  const VListRow({
    this.titleLines = 1,
    super.key,
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.trailingText,
    this.chevron = false,
    this.selected = false,
    this.onTap,
    this.subtitleLines = 1,
  });

  @override
  Widget build(BuildContext context) {
    final body = Container(
      constraints: const BoxConstraints(minHeight: 48),
      padding: const EdgeInsets.symmetric(horizontal: VSpace.md, vertical: 10),
      decoration: BoxDecoration(
        color: selected ? VColors.overlayLight : Colors.transparent,
        borderRadius: BorderRadius.circular(selected ? VRadius.md : 0),
      ),
      child: Row(
        children: [
          if (leading != null) ...[leading!, const SizedBox(width: VSpace.sm)],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  title,
                  maxLines: titleLines,
                  overflow: TextOverflow.ellipsis,
                  style: VType.body(weight: FontWeight.w500).copyWith(height: VType.normal),
                ),
                if (subtitle != null && subtitle!.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(subtitle!, maxLines: subtitleLines, overflow: TextOverflow.ellipsis, style: VType.footnote()),
                ],
              ],
            ),
          ),
          if (trailingText != null) ...[
            const SizedBox(width: VSpace.xs),
            Text(trailingText!, style: VType.footnote(color: VColors.textTertiary)),
          ],
          if (trailing != null) ...[const SizedBox(width: VSpace.xs), trailing!],
          if (chevron) ...[
            const SizedBox(width: VSpace.xxs),
            const Icon(CupertinoIcons.chevron_right, size: 16, color: VColors.textTertiary),
          ],
        ],
      ),
    );
    return onTap == null ? body : VPress(onTap: onTap, child: body);
  }
}

/// Sidebar menu item: icon in a circle + label; selected = lighter capsule.
class VSidebarItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback? onTap;
  final Widget? trailing;
  const VSidebarItem({super.key, required this.icon, required this.label, this.selected = false, this.onTap, this.trailing});

  @override
  Widget build(BuildContext context) {
    return VPress(
      onTap: onTap,
      child: AnimatedContainer(
        duration: VMotion.fast,
        height: 44,
        padding: const EdgeInsets.symmetric(horizontal: VSpace.xs),
        decoration: BoxDecoration(
          color: selected ? VColors.overlayLight : Colors.transparent,
          borderRadius: BorderRadius.circular(VRadius.full),
        ),
        child: Row(
          children: [
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(shape: BoxShape.circle, color: selected ? VColors.fillActive : VColors.fillCell),
              child: Icon(icon, size: 15, color: selected ? VColors.textPrimary : VColors.textSecondary),
            ),
            const SizedBox(width: VSpace.sm),
            Expanded(
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: VType.callout(
                  color: selected ? VColors.textPrimary : VColors.textSecondary,
                  weight: selected ? FontWeight.w600 : FontWeight.w500,
                ),
              ),
            ),
            if (trailing != null) trailing!,
          ],
        ),
      ),
    );
  }
}

/// Circle avatar with initials in the model's provider colour.
class VAvatar extends StatelessWidget {
  final String label;
  final Color color;
  final double size;
  const VAvatar({super.key, required this.label, required this.color, this.size = 32});

  @override
  Widget build(BuildContext context) {
    final initials = label.trim().isEmpty
        ? '?'
        : label.trim().split(RegExp(r'\s+')).take(2).map((w) => w.characters.first.toUpperCase()).join();
    final onColor = (color.a >= 0.5 && color.computeLuminance() > 0.45) ? const Color(0xFF14141E) : Colors.white;
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(shape: BoxShape.circle, color: color),
      alignment: Alignment.center,
      child: Text(initials, style: VType.caption(color: onColor, weight: FontWeight.w700).copyWith(fontSize: size * 0.36)),
    );
  }
}

/// Media tile: rounded image, title and subtitle beneath (album grid).
class VTile extends StatelessWidget {
  final Widget media;
  final String title;
  final String? subtitle;
  final VoidCallback? onTap;
  final double aspect;
  final bool selected;
  const VTile({super.key, required this.media, required this.title, this.subtitle, this.onTap, this.aspect = 1, this.selected = false});

  @override
  Widget build(BuildContext context) {
    return VPress(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(6),
        decoration: BoxDecoration(
          color: selected ? VColors.overlayLight : Colors.transparent,
          borderRadius: BorderRadius.circular(VRadius.md + 4),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            AspectRatio(
              aspectRatio: aspect,
              child: ClipRRect(borderRadius: BorderRadius.circular(VRadius.md), child: media),
            ),
            const SizedBox(height: 6),
            Text(title, maxLines: 1, overflow: TextOverflow.ellipsis, style: VType.callout(weight: FontWeight.w600)),
            if (subtitle != null) Text(subtitle!, maxLines: 1, overflow: TextOverflow.ellipsis, style: VType.caption()),
          ],
        ),
      ),
    );
  }
}

/// Kit toggle using CupertinoSwitch styled for spatial glass.
class VToggle extends StatelessWidget {
  final bool value;
  final ValueChanged<bool>? onChanged;
  const VToggle({super.key, required this.value, this.onChanged});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 44,
      height: 26,
      child: FittedBox(
        fit: BoxFit.contain,
        child: CupertinoSwitch(
          value: value,
          activeTrackColor: VColors.accentBlue,
          inactiveTrackColor: VColors.overlayDark,
          onChanged: onChanged,
        ),
      ),
    );
  }
}

/// A bounded glass window with a visionOS header: leading circle, title, trailing circles.
class VWindow extends StatelessWidget {
  final String? title;
  final bool largeTitle;
  final Widget? leading;
  final List<Widget> actions;
  final Widget child;
  final double maxWidth;
  final double? maxHeight;
  final EdgeInsetsGeometry contentPadding;
  final VMaterial material;
  final bool centerTitle;

  const VWindow({
    super.key,
    this.title,
    this.largeTitle = false,
    this.leading,
    this.actions = const [],
    required this.child,
    this.maxWidth = 420,
    this.maxHeight,
    this.contentPadding = const EdgeInsets.fromLTRB(VSpace.md, 0, VSpace.md, VSpace.md),
    this.material = VMaterial.modal,
    this.centerTitle = false,
  });

  @override
  Widget build(BuildContext context) {
    final header = (title != null || leading != null || actions.isNotEmpty)
        ? Padding(
            padding: const EdgeInsets.fromLTRB(VSpace.sm, VSpace.sm, VSpace.sm, VSpace.xs),
            child: SizedBox(
              height: 40,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  if (title != null)
                    Positioned.fill(
                      left: centerTitle ? 48 : (leading != null ? 48 : VSpace.xxs),
                      right: centerTitle ? 48 : (actions.length * 42.0),
                      child: Align(
                        alignment: centerTitle ? Alignment.center : Alignment.centerLeft,
                        child: Text(
                          title!,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: largeTitle ? VType.title() : VType.headline(),
                        ),
                      ),
                    ),
                  if (leading != null) Align(alignment: Alignment.centerLeft, child: leading!),
                  if (actions.isNotEmpty)
                    Align(
                      alignment: Alignment.centerRight,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          for (int i = 0; i < actions.length; i++) ...[
                            if (i > 0) const SizedBox(width: 6),
                            actions[i],
                          ],
                        ],
                      ),
                    ),
                ],
              ),
            ),
          )
        : const SizedBox(height: VSpace.md);

    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: maxWidth, maxHeight: maxHeight ?? double.infinity),
      child: VGlass(
        material: material,
        radius: VRadius.xl,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            header,
            Flexible(child: Padding(padding: contentPadding, child: child)),
          ],
        ),
      ),
    );
  }
}

/// Alert (Prime Video visionOS): icon, title, message, stacked actions.
class VAlertAction {
  final String label;
  final VoidCallback onTap;
  final bool destructive;
  final bool emphasized;
  const VAlertAction(this.label, this.onTap, {this.destructive = false, this.emphasized = false});
}

class VAlert extends StatelessWidget {
  final Widget? icon;
  final String title;
  final String? message;
  final List<VAlertAction> actions;
  const VAlert({super.key, this.icon, required this.title, this.message, required this.actions});

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 320),
      child: VGlass(
        material: VMaterial.modal,
        radius: 32,
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (icon != null) ...[Center(child: SizedBox(width: 52, height: 52, child: icon!)), const SizedBox(height: 8)],
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(title, textAlign: TextAlign.center, style: VType.title2(color: const Color(0xF5FFFFFF)).copyWith(fontSize: 19, height: 24 / 19)),
                  if (message != null) ...[
                    const SizedBox(height: 2),
                    Text(message!, textAlign: TextAlign.center, style: VType.body(color: VColors.textSecondary).copyWith(height: 20 / 15)),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 8),
            Container(height: 1, color: const Color(0x1FFFFFFF)),
            const SizedBox(height: 12),
            for (int i = 0; i < actions.length; i++) ...[
              if (i > 0) const SizedBox(height: 8),
              VPress(
                onTap: actions[i].onTap,
                child: Container(
                  height: 44,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: actions[i].emphasized ? VColors.fillCell : Colors.transparent,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    actions[i].label,
                    style: VType.headline(color: actions[i].destructive ? VColors.accentRed : const Color(0xF5FFFFFF)).copyWith(height: 20 / 17),
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

/// Section title (window content headings).
class VSectionTitle extends StatelessWidget {
  final String text;
  final Widget? trailing;
  final bool large;
  const VSectionTitle(this.text, {super.key, this.trailing, this.large = false});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: Text(text, maxLines: 1, overflow: TextOverflow.ellipsis, style: large ? VType.title() : VType.title2())),
        if (trailing != null) trailing!,
      ],
    );
  }
}

/// Scroll view whose content dissolves at its edges.
class VFadeScroll extends StatelessWidget {
  final Widget child;
  final double fade;
  final EdgeInsetsGeometry padding;
  final Axis axis;
  final FadeFocus focus;
  const VFadeScroll({
    super.key,
    required this.child,
    this.fade = 14,
    this.padding = EdgeInsets.zero,
    this.axis = Axis.vertical,
    this.focus = FadeFocus.top,
  });

  @override
  Widget build(BuildContext context) {
    final scroll = SingleChildScrollView(
      scrollDirection: axis,
      physics: const BouncingScrollPhysics(),
      padding: padding,
      child: child,
    );
    return EdgeFade(fadeHeight: fade, axis: axis, focus: focus, child: scroll);
  }
}

/// Summary text helper for 2-line ticker summaries.
class VOneLine extends StatelessWidget {
  final String text;
  final TextStyle? style;
  const VOneLine({super.key, required this.text, this.style});

  static TextStyle get rowStyle => VType.callout(weight: FontWeight.w500).copyWith(fontSize: 11, height: 15 / 11);

  /// How many characters [maxLines] of [width] hold in the row style.
  static int charsFor(double width, {int maxLines = 2}) {
    const sample = 'Seal leaks and lower the thermostat. Water boils at 100 C at sea level. Yes, with a cold-climate model.';
    final p = TextPainter(text: TextSpan(text: sample, style: rowStyle), maxLines: 1, textDirection: TextDirection.ltr)..layout();
    final per = p.width / sample.length;
    p.dispose();
    return ((width / per) * (maxLines * 0.925)).floor().clamp(90, 135);
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Text(
        text,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        style: style ?? rowStyle,
      ),
    );
  }
}

/// One line of a press menu.
class VMenuItem {
  final IconData? icon;
  final String label;
  final VoidCallback onTap;
  final bool checked;
  final bool apart;
  const VMenuItem(this.icon, this.label, this.onTap, {this.checked = false, this.apart = false});
}

enum VMenuAlign { start, center, end }

class _VMenuLayout extends SingleChildLayoutDelegate {
  final Offset at;
  final VMenuAlign align;
  _VMenuLayout(this.at, this.align);

  @override
  BoxConstraints getConstraintsForChild(BoxConstraints constraints) =>
      BoxConstraints(maxWidth: math.max(0, constraints.maxWidth - 16), maxHeight: math.max(0, constraints.maxHeight - 16));

  @override
  Offset getPositionForChild(Size size, Size child) {
    final x = switch (align) {
      VMenuAlign.start => at.dx,
      VMenuAlign.center => at.dx - child.width / 2,
      VMenuAlign.end => at.dx - child.width,
    };
    final left = x.clamp(8.0, math.max(8.0, size.width - child.width - 8));
    final below = at.dy + 8 + child.height <= size.height - 8;
    final top = below ? at.dy + 8 : (at.dy - child.height - 8).clamp(8.0, math.max(8.0, size.height - child.height - 8));
    return Offset(left.toDouble(), top.toDouble());
  }

  @override
  bool shouldRelayout(covariant _VMenuLayout old) => old.at != at || old.align != align;
}

/// A press menu: a small glass list that opens where it was asked for and closes on a choice or a tap elsewhere.
Future<void> showVMenu(BuildContext context, Offset at, List<VMenuItem> items, {VMenuAlign align = VMenuAlign.center}) {
  final ticks = items.any((it) => it.checked);
  return showGeneralDialog<void>(
    context: context,
    barrierDismissible: true,
    barrierLabel: 'Close',
    barrierColor: Colors.transparent,
    transitionDuration: VMotion.fast,
    pageBuilder: (ctx, _, __) => CustomSingleChildLayout(
      delegate: _VMenuLayout(at, align),
      child: Material(
        type: MaterialType.transparency,
        child: VGlass(
          material: VMaterial.modal,
          radius: 16,
          padding: const EdgeInsets.all(6),
          child: IntrinsicWidth(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final it in items) ...[
                  if (it.apart) const SizedBox(height: 8),
                  VPress(
                    onTap: () {
                      Navigator.of(ctx).pop();
                      it.onTap();
                    },
                    child: Container(
                      height: 36,
                      padding: const EdgeInsets.symmetric(horizontal: 10),
                      decoration: BoxDecoration(
                        color: it.checked ? const Color(0x1FFFFFFF) : Colors.transparent,
                        borderRadius: BorderRadius.circular(11),
                      ),
                      child: Row(
                        children: [
                          if (it.icon != null) ...[
                            Icon(it.icon, size: 16, color: vHueFor(it.icon!) ?? VColors.textSecondary),
                            const SizedBox(width: 10),
                          ],
                          Text(it.label, maxLines: 1, softWrap: false, style: VType.callout(weight: FontWeight.w500)),
                          if (ticks) ...[
                            const Spacer(),
                            SizedBox(
                              width: 26,
                              child: it.checked
                                  ? const Align(
                                      alignment: Alignment.centerRight,
                                      child: Icon(CupertinoIcons.checkmark_alt, size: 16, color: VColors.textPrimary),
                                    )
                                  : null,
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    ),
    transitionBuilder: (ctx, a, _, child) => FadeTransition(
      opacity: a,
      child: ScaleTransition(
        scale: Tween(begin: 0.96, end: 1.0).animate(CurvedAnimation(parent: a, curve: Curves.easeOutCubic)),
        child: child,
      ),
    ),
  );
}

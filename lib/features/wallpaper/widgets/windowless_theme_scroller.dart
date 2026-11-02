import 'dart:math' as math;
import 'dart:ui' show ImageFilter;
import 'package:material_ui/material_ui.dart';
import '../../../models/theme_def.dart';
import '../../../core/audio/music_player.dart';
import '../../../core/media/theme_blur_cache.dart';
import '../../../core/vision/vision_kit.dart';
import '../../theme/theme_living_media.dart';
import '../../theme/theme_pack_store.dart';

/// Theme Gallery — Pure Spatial Artwork per VisionOS HIG & PRD R29/R42:
/// - The central artwork is 100% PRISTINE, with ZERO overlaid controls, icons, play buttons, or scrubbers.
/// - Sized in true 9:16 vertical mobile portrait aspect ratio.
/// - Browsing/scrolling themes updates ONLY the preview card; the room's living background wallpaper
///   does NOT swap until the user explicitly commits it via 'Set Wallpaper' or tapping the preview (PRD R29).
/// - Floating VisionOS Top Ornament houses navigation & action, cleanly detached above the art.
class WindowlessThemeScroller extends StatefulWidget {
  final WallpaperTheme currentTheme;
  final ValueChanged<WallpaperTheme> onLivePreview;
  final ValueChanged<WallpaperTheme> onConfirmTheme;
  final VoidCallback onCancel;
  final VoidCallback onUpgradeTier;

  const WindowlessThemeScroller({
    super.key,
    required this.currentTheme,
    required this.onLivePreview,
    required this.onConfirmTheme,
    required this.onCancel,
    required this.onUpgradeTier,
  });

  @override
  State<WindowlessThemeScroller> createState() => _WindowlessThemeScrollerState();
}

class _WindowlessThemeScrollerState extends State<WindowlessThemeScroller> {
  late WallpaperTheme _previewed;
  final ScrollController _strip = ScrollController();

  /// How far the gallery has been pulled up toward the live wallpapers: 0 at rest, 1 in focus.
  double _pull = 0;

  static const _thumbH = 56.0;
  static const _thumbW = _thumbH * 9.0 / 16.0; // 9:16 portrait thumbnail
  static const _gap = 6.0;

  /// The free themes, then the live wallpapers that have been bought
  List<WallpaperTheme> get _themes => [
        ...WallpaperCatalog.freeThemes,
        for (final t in WallpaperCatalog.premiumThemes)
          if (ThemePackStore.instance.isUnlocked(t.id)) t,
      ];

  @override
  void initState() {
    super.initState();
    _previewed = widget.currentTheme;
    ThemeBlurCache.instance.prewarmThemes(_themes);
    ThemePackStore.instance.init().then((_) {
      if (mounted) {
        ThemeBlurCache.instance.prewarmThemes(_themes);
        setState(() {});
      }
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final i = _themes.indexWhere((t) => t.id == _previewed.id);
      if (i > 0 && _strip.hasClients) _strip.jumpTo(i * (_thumbW + _gap));
    });
  }

  @override
  void dispose() {
    _strip.dispose();
    super.dispose();
  }

  void _select(WallpaperTheme t) {
    if (t.id == _previewed.id) return;
    ThemeBlurCache.instance.setActiveTheme(t);
    setState(() => _previewed = t);
    // PRD R29: Theme Gallery does NOT swap the background while browsing.
    // Changing theme changes the preview card only; background changes on explicit commit.
    final i = _themes.indexWhere((x) => x.id == t.id);
    if (_strip.hasClients) _strip.animateTo(i * (_thumbW + _gap), duration: VMotion.base, curve: Curves.easeOutCubic);
  }

  void _step(int by) {
    final i = _themes.indexWhere((t) => t.id == _previewed.id);
    _select(_themes[(i + by).clamp(0, _themes.length - 1)]);
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);

    // True 9:16 Vertical Mobile Portrait Aspect Ratio
    final pictureH = (size.height * 0.44).clamp(280.0, 420.0);
    final pictureW = pictureH * (9.0 / 16.0);
    final k = pictureW / 400.0;
    final stripW = math.min(size.width - 32, 340.0);

    return GestureDetector(
      behavior: HitTestBehavior.translucent,
      onVerticalDragUpdate: (d) => setState(() => _pull = (_pull - d.delta.dy / 150).clamp(0.0, 1.0)),
      onVerticalDragEnd: (d) {
        final go = (d.primaryVelocity ?? 0) < -300 || _pull > 0.55;
        setState(() => _pull = 0);
        if (go) widget.onUpgradeTier();
      },
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // The live wallpapers seen above the gallery, fading upward
            SizedBox(width: math.max(pictureW, 260.0), child: _LivePeek(pull: _pull, onTap: widget.onUpgradeTier)),
            const SizedBox(height: 10),

            // Floating Top Ornament for Navigation & Action (VisionOS Spatial HIG)
            // Cleanly separated ABOVE the artwork; zero occlusion on the wallpaper itself.
            VOrnament(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  VCircleButton(
                    icon: Icons.close_rounded,
                    size: 32,
                    tooltip: 'Close',
                    onTap: widget.onCancel,
                  ),
                  const SizedBox(width: 14),
                  Text(
                    _previewed.name,
                    style: VType.title2().copyWith(fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(width: 14),
                  VPress(
                    onTap: () => widget.onConfirmTheme(_previewed),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: VColors.accentBlue,
                        borderRadius: BorderRadius.circular(VRadius.full),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.check_rounded, size: 14, color: Colors.white),
                          const SizedBox(width: 5),
                          Text('Set Wallpaper', style: VType.caption(color: Colors.white, weight: FontWeight.w600)),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Central Pure Artwork Container: 100% PRISTINE, ZERO OVERLAID ICONS OR CONTROLS
            SizedBox(
              width: pictureW,
              height: pictureH,
              child: _picture(k),
            ),

            const SizedBox(height: 14),

            // Thumbnails strip with soft edge fades
            SizedBox(width: stripW, height: _thumbH, child: _thumbnails(stripW)),
          ],
        ),
      ),
    );
  }

  /// The picture itself: 100% pure artwork, backed by its ambient optical glow.
  /// Strictly ZERO overlaid controls, play buttons, progress bars, or icons.
  Widget _picture(double k) {
    final radius = math.max(25 * k, 16.0);
    final image = ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 260),
        switchInCurve: Curves.easeOutCubic,
        switchOutCurve: Curves.easeInCubic,
        transitionBuilder: (child, anim) {
          final curved = CurvedAnimation(parent: anim, curve: Curves.easeOutCubic);
          return FadeTransition(opacity: curved, child: child);
        },
        child: SizedBox.expand(
          key: ValueKey(_previewed.assetPath),
          child: ThemePosterImage(theme: _previewed, filterQuality: FilterQuality.high),
        ),
      ),
    );

    return GestureDetector(
      onTap: () => widget.onConfirmTheme(_previewed),
      onHorizontalDragEnd: (d) {
        final v = d.primaryVelocity ?? 0;
        if (v < -150) _step(1);
        if (v > 150) _step(-1);
      },
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Ambient optical glow behind the pure art
          Positioned(
            left: -24 * k,
            right: -24 * k,
            top: -24 * k,
            bottom: -24 * k,
            child: IgnorePointer(
              child: Opacity(
                opacity: 0.85,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(radius + 16),
                  child: CachedThemeSurface(
                    assetPath: _previewed.assetPath,
                    preset: ThemeBlurPreset.galleryGlow,
                  ),
                ),
              ),
            ),
          ),

          // 100% Pure Artwork — Zero Icons, Zero Scrubbers, Zero Play Controls
          Positioned.fill(child: image),
        ],
      ),
    );
  }

  /// Clean thumbnail strip with silver selected indicator (PRD R29).
  Widget _thumbnails(double stripW) {
    final themes = _themes;
    return ShaderMask(
      blendMode: BlendMode.dstIn,
      shaderCallback: (r) => const LinearGradient(
        colors: [Color(0x00FFFFFF), Colors.white, Colors.white, Color(0x00FFFFFF)],
        stops: [0, 0.15, 0.85, 1.0],
      ).createShader(r),
      child: ListView.separated(
        controller: _strip,
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        padding: EdgeInsets.symmetric(horizontal: (stripW - _thumbW) / 2),
        itemCount: themes.length,
        separatorBuilder: (_, __) => const SizedBox(width: _gap),
        itemBuilder: (_, i) {
          final t = themes[i];
          final sel = t.id == _previewed.id;
          return VPress(
            onTap: () => _select(t),
            tooltip: t.name,
            child: AnimatedContainer(
              duration: VMotion.base,
              curve: Curves.easeOutCubic,
              width: sel ? _thumbW + 6 : _thumbW,
              height: _thumbH,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                // PRD R29: Selected state stays silver
                border: Border.all(
                  color: sel ? const Color(0xFFC0C0C0) : Colors.white.withValues(alpha: 0.12),
                  width: sel ? 1.8 : 0.8,
                ),
                boxShadow: sel ? const [BoxShadow(color: Color(0x66FFFFFF), blurRadius: 10)] : null,
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(7),
                child: Image.asset(t.assetPath, height: _thumbH, fit: BoxFit.cover, filterQuality: FilterQuality.medium),
              ),
            ),
          );
        },
      ),
    );
  }
}

/// The live wallpapers as they appear from the gallery below them.
class _LivePeek extends StatefulWidget {
  final double pull;
  final VoidCallback onTap;
  const _LivePeek({required this.pull, required this.onTap});

  @override
  State<_LivePeek> createState() => _LivePeekState();
}

class _LivePeekState extends State<_LivePeek> with SingleTickerProviderStateMixin {
  late final AnimationController _drift = AnimationController(
    vsync: this,
    duration: Duration(seconds: 12 * WallpaperCatalog.premiumThemes.length.clamp(2, 60)),
  )..repeat();

  @override
  void dispose() {
    _drift.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final live = WallpaperCatalog.premiumThemes;
    if (live.isEmpty) return const SizedBox.shrink();
    const w = 54.0, gap = 8.0, full = 96.0, rest = 48.0;
    final span = live.length * (w + gap);
    final p = widget.pull;
    final soft = 1.7 * (1 - p);

    Widget cards(double offset, double width) {
      final first = (offset / (w + gap)).floor();
      final n = (width / (w + gap)).ceil() + 2;
      return Stack(
        clipBehavior: Clip.none,
        children: [
          for (var k = first; k < first + n; k++)
            Positioned(
              left: k * (w + gap) - offset,
              bottom: 0,
              width: w,
              height: full,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(7),
                child: Image.asset(live[k % live.length].assetPath, width: w, height: full, fit: BoxFit.cover, filterQuality: FilterQuality.medium),
              ),
            ),
        ],
      );
    }

    return GestureDetector(
      onTap: widget.onTap,
      child: SizedBox(
        height: rest + (full - rest) * p,
        child: ShaderMask(
          blendMode: BlendMode.dstIn,
          shaderCallback: (r) => LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color.fromRGBO(255, 255, 255, p), Colors.white],
            stops: const [0, 0.8],
          ).createShader(r),
          child: EdgeFadeHorizontal(
            fade: 28,
            child: ClipRect(
              child: RepaintBoundary(
                child: ImageFiltered(
                  enabled: soft > 0.05,
                  imageFilter: ImageFilter.blur(sigmaX: soft, sigmaY: soft, tileMode: TileMode.decal),
                  child: LayoutBuilder(
                    builder: (_, box) => AnimatedBuilder(
                      animation: _drift,
                      builder: (_, __) => cards(_drift.value * span, box.maxWidth),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Horizontal edge fade for thumbnail strips.
class EdgeFadeHorizontal extends StatelessWidget {
  final Widget child;
  final double fade;
  const EdgeFadeHorizontal({super.key, required this.child, this.fade = 16});

  @override
  Widget build(BuildContext context) {
    return ShaderMask(
      blendMode: BlendMode.dstIn,
      shaderCallback: (r) {
        final f = (fade / (r.width <= 0 ? 1 : r.width)).clamp(0.0, 0.3);
        return LinearGradient(
          colors: const [Color(0x00FFFFFF), Colors.white, Colors.white, Color(0x00FFFFFF)],
          stops: [0, f, 1 - f, 1],
        ).createShader(r);
      },
      child: child,
    );
  }
}

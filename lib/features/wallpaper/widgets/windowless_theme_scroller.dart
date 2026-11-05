import 'dart:math' as math;
import 'package:material_ui/material_ui.dart';
import '../../../models/theme_def.dart';
import '../../../core/media/theme_blur_cache.dart';
import '../../../core/vision/vision_kit.dart';
import '../../theme/theme_living_media.dart';
import '../../theme/theme_pack_store.dart';

/// Theme Gallery — Pure Spatial 9:16 Portrait Card + Centered Thumbnail Strip:
/// - Single razor-sharp 9:16 portrait preview card (no double-container blurry halo border).
/// - No useless top edition strip (_LivePeek removed) and no goofy top ornament bar.
/// - Clean cinematic title & Set Wallpaper action bar directly beneath the 9:16 card.
/// - Dead-center horizontal thumbnail strip sized cleanly to the card width.
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

  static const double _thumbH = 56.0;
  static const double _thumbW = _thumbH * 9.0 / 16.0; // 31.5px 9:16 portrait thumbnail
  static const double _gap = 8.0;

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
    final i = _themes.indexWhere((x) => x.id == t.id);
    if (i >= 0 && _strip.hasClients && _strip.position.maxScrollExtent > 0) {
      final target = (i * (_thumbW + _gap)).clamp(0.0, _strip.position.maxScrollExtent);
      _strip.animateTo(target, duration: VMotion.base, curve: Curves.easeOutCubic);
    }
  }

  void _step(int by) {
    final i = _themes.indexWhere((t) => t.id == _previewed.id);
    _select(_themes[(i + by).clamp(0, _themes.length - 1)]);
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    final isMobile = size.width < 768;

    // True 9:16 Vertical Mobile Portrait Aspect Ratio
    final pictureH = (size.height * (isMobile ? 0.50 : 0.54)).clamp(300.0, 460.0);
    final pictureW = pictureH * (9.0 / 16.0);

    return GestureDetector(
      behavior: HitTestBehavior.translucent,
      onTap: widget.onCancel,
      onVerticalDragEnd: (d) {
        if ((d.primaryVelocity ?? 0) < -300) widget.onUpgradeTier();
      },
      child: Center(
        child: GestureDetector(
          onTap: () {}, // Consume taps inside the gallery column so background tap-away doesn't fire
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 1. Single razor-sharp 9:16 portrait preview card — NO blurry outer halo box
              SizedBox(
                width: pictureW,
                height: pictureH,
                child: _picture(),
              ),
              const SizedBox(height: 16),

              // 2. Clean cinematic title + Set Wallpaper capsule directly under the 9:16 card
              SizedBox(
                width: math.max(pictureW, 256.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Expanded(
                      child: Text(
                        _previewed.name,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: VType.title2(color: Colors.white).copyWith(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          letterSpacing: -0.3,
                          shadows: const [
                            Shadow(color: Color(0xCC000000), blurRadius: 12, offset: Offset(0, 2)),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    VPress(
                      onTap: () => widget.onConfirmTheme(_previewed),
                      tooltip: 'Set Wallpaper',
                      child: Container(
                        height: 34,
                        padding: const EdgeInsets.symmetric(horizontal: 14),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(VRadius.full),
                          boxShadow: const [
                            BoxShadow(color: Color(0x66000000), blurRadius: 14, offset: Offset(0, 4)),
                          ],
                        ),
                        alignment: Alignment.center,
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.check_rounded, size: 15, color: Colors.black),
                            const SizedBox(width: 5),
                            Text(
                              'Set Wallpaper',
                              style: VType.caption(color: Colors.black, weight: FontWeight.w700).copyWith(fontSize: 12.5),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // 3. Dead-center thumbnail strip constrained cleanly to the gallery column
              SizedBox(
                width: math.max(pictureW, 256.0),
                height: _thumbH,
                child: _thumbnails(math.max(pictureW, 256.0)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _picture() {
    const radius = 22.0;
    return GestureDetector(
      onTap: () => widget.onConfirmTheme(_previewed),
      onHorizontalDragEnd: (d) {
        final v = d.primaryVelocity ?? 0;
        if (v < -150) _step(1);
        if (v > 150) _step(-1);
      },
      child: DecoratedBox(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(radius),
          boxShadow: const [
            BoxShadow(color: Color(0xCC000000), blurRadius: 42, spreadRadius: -6, offset: Offset(0, 22)),
            BoxShadow(color: Color(0x80000000), blurRadius: 18, offset: Offset(0, 6)),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(radius),
          child: Stack(
            fit: StackFit.expand,
            children: [
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 260),
                switchInCurve: Curves.easeOutCubic,
                switchOutCurve: Curves.easeInCubic,
                transitionBuilder: (child, anim) => FadeTransition(
                  opacity: CurvedAnimation(parent: anim, curve: Curves.easeOutCubic),
                  child: child,
                ),
                child: SizedBox.expand(
                  key: ValueKey(_previewed.assetPath),
                  child: ThemePosterImage(theme: _previewed, filterQuality: FilterQuality.high),
                ),
              ),
              // Subtle top-to-bottom cinematic vignette for depth
              const IgnorePointer(
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [Color(0x22000000), Color(0x00000000), Color(0x00000000), Color(0x33000000)],
                      stops: [0.0, 0.22, 0.75, 1.0],
                    ),
                  ),
                ),
              ),
              // Subtle top-left close button inside the card corner
              Positioned(
                left: 12,
                top: 12,
                child: VCircleButton(
                  icon: Icons.close_rounded,
                  size: 32,
                  floating: true,
                  tooltip: 'Close',
                  onTap: widget.onCancel,
                ),
              ),
              // Crisp 1px specular glass rim on the card edge
              Positioned.fill(
                child: IgnorePointer(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(radius),
                      border: Border.all(color: Colors.white.withValues(alpha: 0.24), width: 1.0),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Dead-center thumbnail strip: when the thumbnails fit within [maxW], they sit centered in a Row;
  /// when more themes are unlocked than fit, they scroll horizontally inside a centered viewport.
  Widget _thumbnails(double maxW) {
    final themes = _themes;
    if (themes.isEmpty) return const SizedBox.shrink();

    Widget buildThumb(WallpaperTheme t) {
      final sel = t.id == _previewed.id;
      return VPress(
        onTap: () => _select(t),
        tooltip: t.name,
        child: AnimatedContainer(
          duration: VMotion.base,
          curve: Curves.easeOutCubic,
          width: sel ? _thumbW + 8 : _thumbW,
          height: _thumbH,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: sel ? Colors.white : Colors.white.withValues(alpha: 0.20),
              width: sel ? 1.8 : 0.8,
            ),
            boxShadow: sel
                ? const [BoxShadow(color: Color(0x55FFFFFF), blurRadius: 10)]
                : const [BoxShadow(color: Color(0x66000000), blurRadius: 8, offset: Offset(0, 3))],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(6.5),
            child: Image.asset(
              t.assetPath,
              height: _thumbH,
              fit: BoxFit.cover,
              filterQuality: FilterQuality.medium,
            ),
          ),
        ),
      );
    }

    final totalW = themes.length * _thumbW + 8 + math.max(0, themes.length - 1) * _gap;
    if (totalW <= maxW) {
      return Center(
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            for (int i = 0; i < themes.length; i++) ...[
              if (i > 0) const SizedBox(width: _gap),
              buildThumb(themes[i]),
            ],
          ],
        ),
      );
    }

    return ShaderMask(
      blendMode: BlendMode.dstIn,
      shaderCallback: (r) => const LinearGradient(
        colors: [Color(0x00FFFFFF), Colors.white, Colors.white, Color(0x00FFFFFF)],
        stops: [0.0, 0.08, 0.92, 1.0],
      ).createShader(r),
      child: Center(
        child: ListView.separated(
          controller: _strip,
          scrollDirection: Axis.horizontal,
          shrinkWrap: true,
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 12),
          itemCount: themes.length,
          separatorBuilder: (_, __) => const SizedBox(width: _gap),
          itemBuilder: (_, i) => buildThumb(themes[i]),
        ),
      ),
    );
  }
}

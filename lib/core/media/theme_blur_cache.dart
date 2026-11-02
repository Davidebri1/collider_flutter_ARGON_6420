import 'dart:async';
import 'dart:ui' as ui;

import 'package:flutter/foundation.dart';
import 'package:material_ui/material_ui.dart';

import '../../models/theme_def.dart';
import '../vision/vision_tokens.dart';
import 'theme_media_bundle.dart';

enum ThemeBlurPreset {
  poster,
  scrim,
  galleryRoom,
  galleryGlow,
  ambient,
}

Widget themeBlurLook(ThemeBlurPreset preset, Widget sharp) {
  Widget blur(double s, Widget c, {TileMode mode = TileMode.clamp}) =>
      ImageFiltered(imageFilter: ui.ImageFilter.blur(sigmaX: s, sigmaY: s, tileMode: mode), child: c);
  switch (preset) {
    case ThemeBlurPreset.poster:
      return sharp;
    case ThemeBlurPreset.scrim:
      return Stack(fit: StackFit.expand, children: [blur(VBlur.medium, sharp), ColoredBox(color: VOverlay.scrim)]);
    case ThemeBlurPreset.galleryRoom:
      return Stack(fit: StackFit.expand, children: [blur(16, sharp), const ColoredBox(color: Color(0x38000000))]);
    case ThemeBlurPreset.galleryGlow:
      return blur(36, sharp, mode: TileMode.decal);
    case ThemeBlurPreset.ambient:
      const matrix = <double>[
        0.36, 0, 0, 0, -25.5,
        0, 0.36, 0, 0, -25.5,
        0, 0, 0.36, 0, -25.5,
        0, 0, 0, 0.7, 0,
      ];
      return Stack(fit: StackFit.expand, children: [
        const ColoredBox(color: Colors.black),
        blur(20, ColorFiltered(colorFilter: const ColorFilter.matrix(matrix), child: sharp)),
        const ColoredBox(color: Color(0x59000000)),
        const DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Color(0xF2000000), Color(0x00000000), Color(0x00000000), Color(0xF2000000)],
              stops: [0.0, 0.3, 0.7, 1.0],
            ),
          ),
        ),
      ]);
  }
}

class ThemeBlurCache extends ChangeNotifier {
  ThemeBlurCache._();
  static final ThemeBlurCache instance = ThemeBlurCache._();

  final Map<String, ui.Image> _posters = {};
  final Map<String, Future<ui.Image?>> _posterPending = {};

  String _activeAssetPath = WallpaperCatalog.defaultTheme.assetPath;
  String get activeAssetPath => _activeAssetPath;

  void setActiveTheme(WallpaperTheme theme) {
    if (theme.assetPath.isEmpty) return;
    _activeAssetPath = theme.assetPath;
    unawaited(ensurePoster(theme.assetPath));
  }

  ui.Image? posterOf(String assetPath) => _posters[assetPath];

  Future<void> prewarmThemes(Iterable<WallpaperTheme> themes) async {
    for (final t in themes) {
      if (t.assetPath.isEmpty) continue;
      unawaited(ensurePoster(t.assetPath));
    }
  }

  Future<void> ensureAllPresets(String assetPath) => ensurePoster(assetPath);

  // Keep up to 36 decoded posters in LRU cache so multi-column grids and carousels never evict visible cards.
  static const _keepPosters = 36;

  void _keep() {
    while (_posters.length > _keepPosters) {
      final old = _posters.keys.firstWhere((k) => k != _activeAssetPath, orElse: () => '');
      if (old.isEmpty) break;
      _posters.remove(old);
    }
  }

  Future<ui.Image?> ensurePoster(String assetPath) {
    if (assetPath.isEmpty) return SynchronousFuture(null);
    final hit = _posters.remove(assetPath);
    if (hit != null) {
      _posters[assetPath] = hit;
      return SynchronousFuture(hit);
    }
    final inflight = _posterPending[assetPath];
    if (inflight != null) return inflight;

    final fut = _decodePoster(assetPath);
    _posterPending[assetPath] = fut;
    fut.whenComplete(() => _posterPending.remove(assetPath));
    return fut;
  }

  Future<ui.Image?> _decodePoster(String assetPath) async {
    try {
      final data = await ThemeMediaAssetBundle.instance.load(assetPath);
      if (data.lengthInBytes == 0) return null;
      final bytes = data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
      final codec = await ui.instantiateImageCodec(bytes);
      final frame = await codec.getNextFrame();
      final img = frame.image;
      _posters[assetPath] = img;
      _keep();
      notifyListeners();
      return img;
    } catch (e) {
      debugPrint('ThemeBlurCache poster decode failed ($assetPath): $e');
      return null;
    }
  }
}

class CachedThemeSurface extends StatefulWidget {
  final String assetPath;
  final ThemeBlurPreset preset;
  final BoxFit fit;
  final Widget? placeholder;

  const CachedThemeSurface({
    super.key,
    required this.assetPath,
    required this.preset,
    this.fit = BoxFit.cover,
    this.placeholder,
  });

  @override
  State<CachedThemeSurface> createState() => _CachedThemeSurfaceState();
}

class _CachedThemeSurfaceState extends State<CachedThemeSurface> {
  ui.Image? _img;

  @override
  void initState() {
    super.initState();
    _syncOrLoad();
  }

  @override
  void didUpdateWidget(covariant CachedThemeSurface old) {
    super.didUpdateWidget(old);
    if (old.assetPath != widget.assetPath) _syncOrLoad();
  }

  void _syncOrLoad() {
    final cache = ThemeBlurCache.instance;
    _img = cache.posterOf(widget.assetPath);
    if (_img != null) return;
    final path = widget.assetPath;
    cache.ensurePoster(path).then((res) {
      if (mounted && res != null && widget.assetPath == path) setState(() => _img = res);
    });
  }

  @override
  Widget build(BuildContext context) {
    final img = _img;
    if (img == null) return widget.placeholder ?? const ColoredBox(color: Color(0xFF0B0D13));
    return RepaintBoundary(
      child: ClipRect(
        child: themeBlurLook(
          widget.preset,
          RawImage(image: img, fit: widget.fit, width: double.infinity, height: double.infinity, filterQuality: FilterQuality.medium),
        ),
      ),
    );
  }
}

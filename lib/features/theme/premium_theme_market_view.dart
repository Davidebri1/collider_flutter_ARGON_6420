import '../../core/drafts.dart';
import 'dart:async';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';

import '../../core/audio/music_player.dart';
import '../../core/media/live_frames.dart';
import '../../core/media/theme_blur_cache.dart';
import '../../core/media/theme_cloud.dart';
import '../../core/vision/vision_kit.dart';
import '../../models/theme_def.dart';
import 'theme_living_media.dart';
import 'theme_pack_store.dart';

/// Premium Theme Market.
/// - CoverFlow cards render in true 9:16 vertical portrait aspect ratio.
/// - Completely pristine live wallpaper artwork: zero overlaid icons, play buttons, or scrubbers.
/// - Browsing/dragging in the marketplace updates only the preview card and ambient audio preview;
///   the room's living background wallpaper is NOT mutated until the user commits it (PRD R29/R32).
/// - Instant 1-tap "Set Wallpaper" action: no price barrier or fake checkout gating in test mode.
class PremiumThemeMarketView extends StatefulWidget {
  final WallpaperTheme currentTheme;
  final ValueChanged<WallpaperTheme> onApplyTheme;
  final ValueChanged<WallpaperTheme> onPreviewTheme;
  final VoidCallback onClose;

  const PremiumThemeMarketView({
    super.key,
    required this.currentTheme,
    required this.onApplyTheme,
    required this.onPreviewTheme,
    required this.onClose,
  });

  @override
  State<PremiumThemeMarketView> createState() => _PremiumThemeMarketViewState();
}

class _PremiumThemeMarketViewState extends State<PremiumThemeMarketView> with SingleTickerProviderStateMixin {
  // App.tsx state
  String _query = '';
  List<WallpaperTheme> _shown = const [];
  int _index = 0; // unbounded: the row goes round, so the theme is _shown[_index mod length]

  // CoverFlow.tsx state
  bool _dragging = false;
  double _dragStart = 0, _dragOffset = 0, _velocity = 0;
  int _lastDragTime = 0;
  late final AnimationController _move = AnimationController(vsync: this, duration: const Duration(milliseconds: 400));
  double _from = 0, _to = 0;
  final FocusNode _keys = FocusNode();
  final Map<int, LiveFrames> _live = {};
  int _track = 0; // the preview track in focus

  static const _ease = Cubic(0.23, 1, 0.32, 1);

  WallpaperTheme? get _selected => _shown.isEmpty ? null : _at(_index);
  WallpaperTheme _at(int i) => _shown[((i % _shown.length) + _shown.length) % _shown.length];
  double get _pos => _from + (_to - _from) * _ease.transform(_move.value);

  @override
  void initState() {
    super.initState();
    PremiumAmbient.playing.value = true;
    ThemeCloud.instance.addListener(_reload);
    ThemeCloud.instance.init();
    ThemePackStore.instance.addListener(_storeChanged);
    ThemePackStore.instance.init();
    _move.addListener(() => setState(() {}));
    _reload();
    _keys.requestFocus();
  }

  @override
  void dispose() {
    ThemeCloud.instance.removeListener(_reload);
    ThemePackStore.instance.removeListener(_storeChanged);
    _search?.cancel();
    _move.dispose();
    _keys.dispose();
    for (final f in _live.values) {
      f.dispose();
    }
    super.dispose();
  }

  void _storeChanged() {
    if (mounted) setState(() {});
  }

  // ---------------------------------------------------------------- App.tsx: loading and search

  Widget _empty() {
    if (!ThemeCloud.instance.failed) {
      return const Center(
        child: SizedBox(width: 32, height: 32, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF9CA3AF))),
      );
    }
    return Center(
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        Text('The wallpapers could not be loaded.', textAlign: TextAlign.center, style: VType.callout(color: VColors.textSecondary)),
        const SizedBox(height: 14),
        VPress(
          onTap: () => ThemeCloud.instance.reload(),
          child: Container(
            height: 36,
            padding: const EdgeInsets.symmetric(horizontal: 18),
            decoration: BoxDecoration(color: const Color(0x33FFFFFF), borderRadius: BorderRadius.circular(999)),
            child: Center(child: Text('Try again', style: VType.callout(color: Colors.white, weight: FontWeight.w600))),
          ),
        ),
      ]),
    );
  }

  void _reload() {
    final all = WallpaperCatalog.premiumThemes;
    ThemePackStore.instance.loadPrices(all);
    final q = _query.trim().toLowerCase();
    var found = q.isEmpty ? all : all.where((t) => t.name.toLowerCase().contains(q) || t.id.contains(q)).toList();
    if (found.isEmpty) found = all;
    final keep = _selected?.id;
    setState(() {
      _shown = found;
      final i = keep == null ? -1 : found.indexWhere((t) => t.id == keep);
      _index = i >= 0 ? i : found.length ~/ 2;
      _from = _to = _index.toDouble();
      _dropFrames();
    });
    if (_selected != null) WidgetsBinding.instance.addPostFrameCallback((_) { if (mounted && _selected != null) widget.onPreviewTheme(_selected!); });
  }

  Timer? _search;

  void _onSearch(String v) {
    _search?.cancel();
    if (v.trim().isEmpty) return;
    _search = Timer(const Duration(milliseconds: 500), () {
      _query = v;
      _reload();
    });
  }

  void _clearSearch() {
    _search?.cancel();
    _query = '';
    _reload();
  }

  // ---------------------------------------------------------------- CoverFlow.tsx: moving

  void _select(int i) {
    if (_shown.isEmpty || (i == _index && !_dragging)) return;
    _from = _pos + (_dragging ? -_dragOffset / 100 : 0);
    _to = i.toDouble();
    final moved = i != _index;
    _index = i;
    _move.forward(from: 0);
    if (!moved) return;
    _track = 0;
    _dropFrames();
    final t = _selected!;
    ThemeBlurCache.instance.setActiveTheme(t);
    ThemeBlurCache.instance.prewarmThemes([_at(i - 2), _at(i - 1), t, _at(i + 1), _at(i + 2)]);
    widget.onPreviewTheme(t);
    if (PremiumAmbient.playing.value) _playSong(t);
  }

  void _dragStartAt(double x) {
    _dragging = true;
    _dragStart = x;
    _dragOffset = 0;
    _velocity = 0;
    _lastDragTime = DateTime.now().millisecondsSinceEpoch;
  }

  void _dragMoveTo(double x) {
    if (!_dragging) return;
    final now = DateTime.now().millisecondsSinceEpoch;
    final dt = math.max(now - _lastDragTime, 1);
    final offset = x - _dragStart;
    setState(() {
      _velocity = (offset - _dragOffset) / dt;
      _dragOffset = offset;
    });
    _lastDragTime = now;
  }

  void _dragEnd() {
    if (!_dragging) return;
    const threshold = 50.0, velocityThreshold = 0.5, highVelocityThreshold = 2.0;
    var target = _index;
    final distance = _dragOffset.abs(), speed = _velocity.abs();
    if (distance > threshold || speed > velocityThreshold) {
      var jump = 1;
      if (speed > highVelocityThreshold) jump = math.min(2, (speed / 1.5).ceil());
      if (distance > threshold * 2) jump = math.max(jump, (distance / (threshold * 1.5)).floor());
      if (_dragOffset < 0 || _velocity < -velocityThreshold) {
        target = _index + jump;
      } else if (_dragOffset > 0 || _velocity > velocityThreshold) {
        target = _index - jump;
      }
    }
    _select(target);
    _dragging = false;
    setState(() {
      _dragOffset = 0;
      _velocity = 0;
    });
  }

  KeyEventResult _onKey(FocusNode _, KeyEvent e) {
    if (e is! KeyDownEvent) return KeyEventResult.ignored;
    if (e.logicalKey == LogicalKeyboardKey.arrowLeft) {
      _select(_index - 1);
    } else if (e.logicalKey == LogicalKeyboardKey.arrowRight) {
      _select(_index + 1);
    } else if (e.logicalKey == LogicalKeyboardKey.escape) {
      widget.onClose();
    } else {
      return KeyEventResult.ignored;
    }
    return KeyEventResult.handled;
  }

  // ---------------------------------------------------------------- Player.tsx

  void _playSong(WallpaperTheme t) {
    final p = MusicPlayer.instance;
    if (t.tracks.isEmpty) {
      if (p.playing) p.toggle();
      return;
    }
    final i = _track.clamp(0, t.tracks.length - 1);
    if (p.queueId == t.id && p.index == i && p.playing) return;
    p.play(i, list: MusicPlayer.forTheme(t), id: t.id);
  }

  void _focusTrack(WallpaperTheme t, int i) {
    setState(() => _track = i);
    PremiumAmbient.playing.value = true;
    _playSong(t);
  }

  // ---------------------------------------------------------------- live covers

  ValueNotifier<ui.Image?>? _framesFor(int i, WallpaperTheme t) {
    if ((i - _index).abs() > 0 || t.videoPath == null) return null;
    return (_live[i] ??= LiveFrames(themeMediaUrl(t.videoPath!), fps: 20)).frame;
  }

  void _dropFrames() {
    final gone = _live.keys.where((k) => (k - _index).abs() > 0).toList();
    for (final k in gone) {
      _live.remove(k)?.dispose();
    }
  }

  // ---------------------------------------------------------------- layout (App.tsx)

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    final isMobile = size.width < 768;
    final t = _selected;
    return Focus(
      focusNode: _keys,
      onKeyEvent: _onKey,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // Tapping the room closes the market.
          Positioned.fill(child: GestureDetector(behavior: HitTestBehavior.opaque, onTap: widget.onClose)),
          // The source's floor: faint perspective lighting along lower half
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            height: size.height / 2,
            child: IgnorePointer(
              child: Transform(
                alignment: Alignment.bottomCenter,
                transform: Matrix4.identity()
                  ..setEntry(3, 2, 0.001)
                  ..rotateX(60 * math.pi / 180),
                child: const DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(begin: Alignment.bottomCenter, end: Alignment.topCenter, colors: [Color(0x05FFFFFF), Color(0x00FFFFFF)]),
                  ),
                ),
              ),
            ),
          ),
          SafeArea(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                  child: Center(child: _SearchBar(onSearch: _onSearch, onClear: _clearSearch)),
                ),
                Expanded(
                  child: _shown.isEmpty
                      ? _empty()
                      : LayoutBuilder(
                          builder: (context, box) {
                            final availH = box.maxHeight;
                            final compactH = availH < 780;
                            final coverH = (availH * 0.44).clamp(240.0, 360.0);
                            final gapTitle = (availH * 0.025).clamp(10.0, 24.0);
                            final gapTracks = (availH * 0.02).clamp(10.0, 18.0);
                            return SingleChildScrollView(
                              physics: const BouncingScrollPhysics(),
                              padding: EdgeInsets.fromLTRB(isMobile ? 16 : 32, 0, isMobile ? 16 : 32, 20),
                              child: Column(
                                children: [
                                  _coverFlow(isMobile, size.width, coverH: coverH, compactH: compactH),
                                  if (t != null) ...[
                                    SizedBox(height: gapTitle),
                                    Text(t.name,
                                        textAlign: TextAlign.center,
                                        style: VType.title2(color: Colors.white).copyWith(
                                          fontWeight: FontWeight.w300,
                                          shadows: const [Shadow(color: Color(0x80000000), blurRadius: 8, offset: Offset(0, 2))],
                                        )),
                                    if (t.tracks.isNotEmpty) ...[SizedBox(height: gapTracks), _tracks(t, compactH: compactH)],
                                  ],
                                ],
                              ),
                            );
                          },
                        ),
                ),
                // Prominent "Set Wallpaper" action button
                if (t != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 76),
                    child: Center(child: _apply(t)),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------- CoverFlow.tsx: drawing

  Widget _coverFlow(bool isMobile, double width, {double coverH = 340, bool compactH = false}) {
    // True 9:16 Vertical Portrait Cards
    final cardH = isMobile ? 220.0 : (compactH ? 250.0 : 280.0);
    final cardW = cardH * (9.0 / 16.0);
    final spacing = isMobile ? 95.0 : 125.0;
    final drag = _dragging ? _dragOffset / 100 : 0.0;
    final pos = _pos - drag;
    final reach = math.min(math.min(4, (width / spacing / 2).ceil() + 1), (_shown.length - 1) ~/ 2);
    final order = [for (int k = -reach; k <= reach; k++) _index + k]..sort((a, b) => (b - pos).abs().compareTo((a - pos).abs()));
    return SizedBox(
      height: coverH,
      width: double.infinity,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onHorizontalDragStart: (d) => _dragStartAt(d.globalPosition.dx),
        onHorizontalDragUpdate: (d) => _dragMoveTo(d.globalPosition.dx),
        onHorizontalDragEnd: (_) => _dragEnd(),
        onHorizontalDragCancel: _dragEnd,
        child: Stack(
          clipBehavior: Clip.none,
          alignment: Alignment.center,
          children: [
            for (final i in order) _cover(i, i - pos, cardW, cardH, spacing),
          ],
        ),
      ),
    );
  }

  Widget _cover(int i, double offset, double cardW, double cardH, double spacing) {
    final t = _at(i);
    final center = offset.abs() < 0.1;
    final d = offset.abs();
    final m = Matrix4.identity()..setEntry(3, 2, 1 / 1500);
    if (center) {
      m
        ..translate(0.0, 0.0, -280.0)
        ..scale(1.25, 1.25, 1.25);
    } else {
      final k = math.max(0.78, 1.10 - d * 0.04);
      m
        ..translate(offset * spacing, 0.0, 80.0 * d)
        ..rotateY((offset < 0 ? 55 : -55) * math.pi / 180)
        ..scale(k, k, 1.0);
    }
    const opacity = 1.0;
    final isCurrent = i == _index;
    final frames = _framesFor(i, t);
    Widget picture() => frames == null
        ? _Poster(theme: t)
        : ValueListenableBuilder<ui.Image?>(
            valueListenable: frames,
            builder: (_, img, __) => img == null ? _Poster(theme: t) : RawImage(image: img, fit: BoxFit.cover, filterQuality: FilterQuality.high),
          );
    return Transform(
      alignment: Alignment.center,
      transform: m,
      child: Opacity(
        opacity: opacity,
        child: GestureDetector(
          onTap: () => _select(i),
          child: SizedBox(
            width: cardW,
            height: cardH,
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                // 100% Pristine 9:16 Artwork Container: ZERO OVERLAID ICONS OR PLAY BUTTONS
                Positioned.fill(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: const [
                        BoxShadow(color: Color(0xE6000000), blurRadius: 40, spreadRadius: -8, offset: Offset(0, 20)),
                        BoxShadow(color: Color(0x99000000), blurRadius: 24, offset: Offset(0, 6)),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Stack(fit: StackFit.expand, children: [
                        picture(),
                        // Subtle specular sheen across the face
                        const DecoratedBox(
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: [Color(0x1AFFFFFF), Color(0x08FFFFFF), Color(0x00FFFFFF), Color(0x05000000), Color(0x14000000)],
                              stops: [0, 0.25, 0.5, 0.75, 1],
                            ),
                          ),
                        ),
                      ]),
                    ),
                  ),
                ),
                Positioned.fill(
                  child: IgnorePointer(
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.white.withValues(alpha: isCurrent ? 0.35 : 0.12), width: isCurrent ? 1.5 : 1),
                      ),
                    ),
                  ),
                ),
                // Floor reflection under the 9:16 card
                Positioned(
                  top: cardH,
                  left: 0,
                  width: cardW,
                  height: cardH,
                  child: IgnorePointer(
                    child: Opacity(
                      opacity: isCurrent ? 0.85 : 0.65,
                      child: Transform(
                        alignment: Alignment.center,
                        transform: Matrix4.diagonal3Values(1, -1, 1),
                        child: ShaderMask(
                          blendMode: BlendMode.dstIn,
                          shaderCallback: (r) => const LinearGradient(
                            begin: Alignment.bottomCenter,
                            end: Alignment.topCenter,
                            colors: [Color(0xBFFFFFFF), Color(0x66FFFFFF), Color(0x26FFFFFF), Color(0x00FFFFFF)],
                            stops: [0, 0.2, 0.4, 0.6],
                          ).createShader(r),
                          child: ColorFiltered(
                            colorFilter: const ColorFilter.matrix(<double>[
                              0.78, 0, 0, 0, -38.25,
                              0, 0.78, 0, 0, -38.25,
                              0, 0, 0.78, 0, -38.25,
                              0, 0, 0, 1, 0,
                            ]),
                            child: ClipRRect(borderRadius: BorderRadius.circular(12), child: picture()),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                // Floor highlight
                Positioned(
                  top: cardH + 6,
                  left: 0,
                  width: cardW,
                  height: 12,
                  child: IgnorePointer(
                    child: Opacity(
                      opacity: isCurrent ? 0.6 : 0.35,
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(8),
                          gradient: const LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [Color(0x0FFFFFFF), Color(0x1FFFFFFF), Color(0x00FFFFFF)],
                            stops: [0, 0.4, 1],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                if (isCurrent) ...[
                  Positioned(
                    top: 0,
                    left: cardW / 4,
                    right: cardW / 4,
                    height: 4,
                    child: IgnorePointer(
                      child: ImageFiltered(
                        imageFilter: ui.ImageFilter.blur(sigmaX: 4, sigmaY: 4),
                        child: DecoratedBox(
                          decoration: BoxDecoration(color: const Color(0x33FFFFFF), borderRadius: BorderRadius.circular(999)),
                        ),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// The pack's preview tracks. The one playing (or chosen) sits in focus; changing pack fades one set into the next.
  Widget _tracks(WallpaperTheme t, {bool compactH = false}) {
    final p = MusicPlayer.instance;
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 450),
      switchInCurve: Curves.easeOutCubic,
      switchOutCurve: Curves.easeInCubic,
      child: AnimatedBuilder(
        key: ValueKey(t.id),
        animation: p,
        builder: (_, __) {
          final mine = p.queueId == t.id && p.index != null;
          return _TrackWheel(
            tracks: t.tracks,
            selected: (mine ? p.index! : _track).clamp(0, t.tracks.length - 1),
            onSelect: (i) => _focusTrack(t, i),
            compactH: compactH,
          );
        },
      ),
    );
  }

  /// Direct 1-tap "Set Wallpaper" action without fake paywalls or bypass gates.
  Widget _apply(WallpaperTheme t) {
    return VPress(
      onTap: () => widget.onApplyTheme(t),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 10),
        decoration: BoxDecoration(
          color: VColors.accentBlue,
          borderRadius: BorderRadius.circular(VRadius.full),
          boxShadow: const [
            BoxShadow(color: Color(0x4D0A84FF), blurRadius: 16, offset: Offset(0, 4)),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.check_rounded, size: 16, color: Colors.white),
            const SizedBox(width: 8),
            Text('Set Wallpaper', style: VType.callout(color: Colors.white, weight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

/// Five rows on a wheel that goes round, so every track of the pack is always in view. The row in focus is sharp and
/// full size at the centre; each step away is smaller, fainter and more blurred, and the top and bottom edges dissolve.
/// A tap or a vertical drag brings a row to the centre.
class _TrackWheel extends StatefulWidget {
  final List<AmbientTrack> tracks;
  final int selected;
  final ValueChanged<int> onSelect;
  final bool compactH;
  const _TrackWheel({required this.tracks, required this.selected, required this.onSelect, this.compactH = false});

  @override
  State<_TrackWheel> createState() => _TrackWheelState();
}

class _TrackWheelState extends State<_TrackWheel> with SingleTickerProviderStateMixin {
  double get _rowH => widget.compactH ? 28.0 : 36.0;
  int get _rows => widget.compactH ? 3 : 5;
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 560));
  double _from = 0, _to = 0, _drag = 0;
  bool _dragging = false;

  int get _n => widget.tracks.length;
  double get _pos => _dragging ? _to - _drag / _rowH : _from + (_to - _from) * Curves.easeOutCubic.transform(_c.value);
  int _wrap(int i) => ((i % _n) + _n) % _n;

  @override
  void initState() {
    super.initState();
    _from = _to = widget.selected.toDouble();
    _c.addListener(() => setState(() {}));
  }

  @override
  void didUpdateWidget(_TrackWheel old) {
    super.didUpdateWidget(old);
    final at = _to.round();
    if (_wrap(at) != widget.selected && !_dragging) {
      final k = ((at - widget.selected) / _n).round();
      _glide(widget.selected + k * _n);
    }
  }

  @override
  void dispose() {
    super.dispose();
  }

  void _glide(int i) {
    _from = _pos;
    _to = i.toDouble();
    _c.forward(from: 0);
  }

  void _choose(int i) {
    _glide(i);
    if (_wrap(i) != widget.selected) widget.onSelect(_wrap(i));
  }

  @override
  Widget build(BuildContext context) {
    final pos = _pos;
    final base = VType.callout(color: Colors.white, weight: FontWeight.w400).copyWith(fontSize: widget.compactH ? 15 : 17, height: 1.2);
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onVerticalDragStart: (_) => setState(() {
        _to = pos;
        _drag = 0;
        _dragging = true;
      }),
      onVerticalDragUpdate: (d) => setState(() => _drag += d.delta.dy),
      onVerticalDragEnd: (d) {
        final velocity = d.primaryVelocity ?? 0;
        final delta = -(_drag / _rowH) - (velocity / 800);
        _dragging = false;
        _glide((pos + delta).round());
        widget.onSelect(_wrap((pos + delta).round()));
      },
      child: SizedBox(
        height: _rows * _rowH,
        child: ShaderMask(
          blendMode: BlendMode.dstIn,
          shaderCallback: (r) => const LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0x00FFFFFF), Colors.white, Colors.white, Color(0x00FFFFFF)],
            stops: [0, 0.25, 0.75, 1],
          ).createShader(r),
          child: Stack(
            children: [
              for (int k = -(_rows ~/ 2) - 1; k <= (_rows ~/ 2) + 1; k++) _row(k, pos, base),
            ],
          ),
        ),
      ),
    );
  }

  Widget _row(int k, double pos, TextStyle base) {
    final centerRow = pos.round();
    final rowIdx = centerRow + k;
    final offset = rowIdx - pos;
    final d = offset.abs();
    final track = widget.tracks[_wrap(rowIdx)];
    Widget text = Text(
      track.title,
      textAlign: TextAlign.center,
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      style: base.copyWith(
        fontWeight: d < 0.3 ? FontWeight.w500 : FontWeight.w300,
        color: Colors.white,
        shadows: const [Shadow(color: Color(0x80000000), blurRadius: 8, offset: Offset(0, 2))],
      ),
    );
    if (d > 0.04) {
      final sigma = 1.6 * d;
      text = ImageFiltered(imageFilter: ui.ImageFilter.blur(sigmaX: sigma, sigmaY: sigma, tileMode: TileMode.decal), child: text);
    }
    return Positioned(
      left: 0,
      right: 0,
      top: (_rows - 1) / 2 * _rowH + offset * _rowH,
      height: _rowH,
      child: GestureDetector(
        onTap: () => _choose((pos + offset).round()),
        child: Center(
          child: Opacity(
            opacity: (1 - 0.34 * d).clamp(0.15, 1.0),
            child: Transform.scale(scale: 1 - 0.1 * d, child: Padding(padding: const EdgeInsets.symmetric(horizontal: 8), child: text)),
          ),
        ),
      ),
    );
  }
}

/// A theme's poster from the bucket or pre-decoded cache.
class _Poster extends StatelessWidget {
  final WallpaperTheme theme;
  const _Poster({required this.theme});

  @override
  Widget build(BuildContext context) {
    const empty = DecoratedBox(
      decoration: BoxDecoration(gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFF030712), Colors.black])),
    );
    if (theme.assetPath.isEmpty) return empty;
    return ListenableBuilder(
      listenable: ThemeBlurCache.instance,
      builder: (context, _) {
        final cached = ThemeBlurCache.instance.posterOf(theme.assetPath);
        if (cached != null) {
          return RawImage(
            image: cached,
            fit: BoxFit.cover,
            filterQuality: FilterQuality.medium,
          );
        }
        ThemeBlurCache.instance.ensurePoster(theme.assetPath);
        return Image.asset(
          theme.assetPath,
          fit: BoxFit.cover,
          filterQuality: FilterQuality.medium,
          gaplessPlayback: true,
          frameBuilder: (_, child, frame, sync) => frame == null && !sync ? empty : child,
          errorBuilder: (_, __, ___) => empty,
        );
      },
    );
  }
}

class _SearchBar extends StatefulWidget {
  final ValueChanged<String> onSearch;
  final VoidCallback onClear;
  const _SearchBar({required this.onSearch, required this.onClear});

  @override
  State<_SearchBar> createState() => _SearchBarState();
}

class _SearchBarState extends State<_SearchBar> {
  final TextEditingController _c = Drafts.text('premium.search');

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 448),
      child: Container(
        height: 46,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: const Color(0xFF374151)),
          gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0x66000000), Color(0x05FFFFFF)]),
          boxShadow: const [BoxShadow(color: Color(0x0DFFFFFF), blurRadius: 2, offset: Offset(0, 1))],
        ),
        child: Row(
          children: [
            const SizedBox(width: 12),
            const Icon(Icons.search_rounded, size: 16, color: Color(0xFF9CA3AF)),
            const SizedBox(width: 12),
            Expanded(
              child: TextField(
                controller: _c,
                cursorColor: Colors.white70,
                style: VType.callout(color: Colors.white, weight: FontWeight.w300).copyWith(fontSize: 11),
                decoration: InputDecoration(
                  hintText: 'Search...',
                  hintStyle: VType.callout(color: const Color(0xFF6B7280), weight: FontWeight.w300).copyWith(fontSize: 11),
                  border: InputBorder.none,
                  isDense: true,
                  contentPadding: EdgeInsets.zero,
                ),
                onChanged: (v) {
                  setState(() {});
                  widget.onSearch(v);
                },
                onSubmitted: (v) => widget.onSearch(v),
              ),
            ),
            if (_c.text.isNotEmpty)
              VPress(
                onTap: () {
                  _c.clear();
                  setState(() {});
                  widget.onClear();
                },
                child: const Padding(padding: EdgeInsets.symmetric(horizontal: 12), child: Icon(Icons.close_rounded, size: 16, color: Color(0xFF9CA3AF))),
              )
            else
              const SizedBox(width: 12),
          ],
        ),
      ),
    );
  }
}

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

/// Premium Theme Market — 3D CoverFlow showcase with spatial reflections, track preview wheel, and store unlock.
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
  String _query = '';
  String _activeTag = 'All Themes';
  final Set<int> _disabledTracks = {};
  List<WallpaperTheme> _shown = const [];
  int _index = 0;

  static const _categoryTags = [
    'All Themes',
    'Spatial Rooms',
    'Nature & Sea',
    'Sci-Fi & Cosmos',
    'Architecture',
  ];

  static bool _matchesTag(WallpaperTheme t, String tag) {
    if (tag == 'All Themes') return true;
    final n = t.name.toLowerCase();
    return switch (tag) {
      'Nature & Sea' => n.contains('sea') || n.contains('ocean') || n.contains('forest') || n.contains('rain') || n.contains('mountain') || n.contains('beach') || n.contains('aurora') || n.contains('water'),
      'Sci-Fi & Cosmos' => n.contains('nebula') || n.contains('space') || n.contains('cyber') || n.contains('galaxy') || n.contains('star') || n.contains('neon') || n.contains('orbit') || n.contains('moon'),
      'Architecture' => n.contains('villa') || n.contains('loft') || n.contains('tokyo') || n.contains('city') || n.contains('sanctuary') || n.contains('temple') || n.contains('studio') || n.contains('hall'),
      _ => true, // Spatial Rooms matches curated spatial scenes
    };
  }

  bool _dragging = false;
  double _dragStart = 0, _dragOffset = 0, _velocity = 0;
  int _lastDragTime = 0;
  late final AnimationController _move = AnimationController(vsync: this, duration: const Duration(milliseconds: 400));
  double _from = 0, _to = 0;
  final FocusNode _keys = FocusNode();
  final Map<int, LiveFrames> _live = {};
  int _track = 0;
  bool _buying = false;

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

  Widget _empty() {
    if (!ThemeCloud.instance.failed) {
      return const Center(
        child: CupertinoActivityIndicator(radius: 14, color: Color(0xFF9CA3AF)),
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
    // Deduplicate by title so consecutive identical theme names never clutter the CoverFlow carousel
    final rawAll = WallpaperCatalog.premiumThemes;
    final seenNames = <String>{};
    final all = <WallpaperTheme>[
      for (final t in rawAll)
        if (seenNames.add(t.name.toLowerCase().trim())) t,
    ];
    ThemePackStore.instance.loadPrices(all);
    final q = _query.trim().toLowerCase();
    var found = all.where((t) {
      final matchesQ = q.isEmpty || t.name.toLowerCase().contains(q) || t.id.contains(q);
      return matchesQ && _matchesTag(t, _activeTag);
    }).toList();
    if (found.isEmpty) found = all;
    final keep = _selected?.id;
    setState(() {
      _shown = found;
      final i = keep == null ? -1 : found.indexWhere((t) => t.id == keep);
      _index = i >= 0 ? i : found.length ~/ 2;
      _from = _to = _index.toDouble();
      _dropFrames();
    });
    final s = _selected;
    if (s != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => widget.onPreviewTheme(s));
    }
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

  void _select(int i) {
    if (_shown.isEmpty || (i == _index && !_dragging)) return;
    final n = _shown.length;
    var startPos = _pos + (_dragging ? -_dragOffset / 114.0 : 0.0);
    if (n > 1) {
      startPos += n * ((i.toDouble() - startPos) / n).roundToDouble();
    }
    _from = startPos;
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

  ValueNotifier<ui.Image?>? _framesFor(int i, WallpaperTheme t) {
    if (i != _index || t.videoPath == null) return null;
    return (_live[i] ??= LiveFrames(themeMediaUrl(t.videoPath!), width: 720, fps: 24)).frame;
  }

  void _dropFrames() {
    final gone = _live.keys.where((k) => k != _index).toList();
    for (final k in gone) {
      _live.remove(k)?.dispose();
    }
  }

  Widget _buildCategoryPills({required bool isMobile}) {
    final list = ListView.separated(
      scrollDirection: Axis.horizontal,
      shrinkWrap: true,
      physics: const BouncingScrollPhysics(),
      padding: EdgeInsets.symmetric(horizontal: isMobile ? 6 : 0),
      itemCount: _categoryTags.length,
      separatorBuilder: (_, __) => const SizedBox(width: 8),
      itemBuilder: (_, idx) {
        final tag = _categoryTags[idx];
        final sel = tag == _activeTag;
        return VPress(
          onTap: () {
            setState(() => _activeTag = tag);
            _reload();
          },
          child: AnimatedContainer(
            duration: VMotion.fast,
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: sel ? VColors.accentBlue.withValues(alpha: 0.38) : VColors.glassElevated,
              borderRadius: BorderRadius.circular(VRadius.full),
              border: Border.all(
                color: sel ? VColors.accentBlue.withValues(alpha: 0.85) : VColors.borderLight,
                width: sel ? 1.0 : 0.6,
              ),
              boxShadow: sel ? VShadow.emissive(VColors.accentBlue, intensity: 0.65, radius: 14) : null,
            ),
            child: Text(
              tag,
              style: VType.caption(
                color: sel ? Colors.white : VColors.textSecondary,
                weight: sel ? FontWeight.w700 : FontWeight.w500,
              ),
            ),
          ),
        );
      },
    );
    return SizedBox(
      height: 34,
      child: isMobile ? EdgeFade(axis: Axis.horizontal, fadeHeight: 20, child: list) : list,
    );
  }

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
          Positioned.fill(child: GestureDetector(behavior: HitTestBehavior.opaque, onTap: widget.onClose)),
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
                    gradient: LinearGradient(
                      begin: Alignment.bottomCenter,
                      end: Alignment.topCenter,
                      colors: [Color(0x05FFFFFF), Color(0x00FFFFFF)],
                    ),
                  ),
                ),
              ),
            ),
          ),
          SafeArea(
            child: Column(
              children: [
                if (isMobile) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(24, 8, 16, 6),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 236),
                          child: _SearchBar(onSearch: _onSearch, onClear: _clearSearch),
                        ),
                        const SizedBox(width: 8),
                        VCircleButton(
                          icon: Icons.close_rounded,
                          size: 32,
                          tooltip: 'Close',
                          floating: true,
                          onTap: widget.onClose,
                        ),
                      ],
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    child: _buildCategoryPills(isMobile: true),
                  ),
                ] else
                  Padding(
                    padding: const EdgeInsets.fromLTRB(24, 14, 24, 6),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Flexible(child: _buildCategoryPills(isMobile: false)),
                        const SizedBox(width: 16),
                        SizedBox(
                          width: (size.width * 0.28).clamp(240.0, 360.0),
                          child: _SearchBar(onSearch: _onSearch, onClear: _clearSearch),
                        ),
                        const SizedBox(width: 12),
                        VCircleButton(
                          icon: Icons.close_rounded,
                          size: 34,
                          tooltip: 'Close',
                          floating: true,
                          onTap: widget.onClose,
                        ),
                      ],
                    ),
                  ),
                Expanded(
                  child: _shown.isEmpty
                      ? _empty()
                      : LayoutBuilder(
                          builder: (context, box) {
                            final availH = box.maxHeight;
                            final compactH = availH < 680;
                            final coverH = (availH - 180.0).clamp(184.0, isMobile ? 248.0 : 316.0);
                            return Center(
                              child: SingleChildScrollView(
                                physics: const BouncingScrollPhysics(),
                                padding: EdgeInsets.fromLTRB(isMobile ? 44 : 32, 4, isMobile ? 12 : 32, 72),
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    _coverFlow(isMobile, size.width - (isMobile ? 56 : 0), coverH: coverH, compactH: compactH),
                                    if (t != null) ...[
                                      const SizedBox(height: 8),
                                      Text(
                                        t.name,
                                        textAlign: TextAlign.center,
                                        style: VType.title2(color: Colors.white).copyWith(
                                          fontWeight: FontWeight.w600,
                                          shadows: const [Shadow(color: Color(0x99000000), blurRadius: 8, offset: Offset(0, 2))],
                                        ),
                                      ),
                                      if (t.tracks.isNotEmpty) ...[
                                        const SizedBox(height: 4),
                                        _tracks(t, compactH: true),
                                      ],
                                      const SizedBox(height: 12),
                                      Center(child: _apply(t)),
                                    ],
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _coverFlow(bool isMobile, double width, {double coverH = 340, bool compactH = false}) {
    final cardW = isMobile ? 136.0 : (compactH ? 156.0 : 172.0);
    final cardH = isMobile ? 214.0 : (compactH ? 242.0 : 268.0);
    final spacing = isMobile ? 114.0 : 152.0;
    final drag = _dragging ? _dragOffset / spacing : 0.0;
    final pos = _pos - drag;
    final centerSlot = pos.round();
    final reach = math.min(6, math.max(1, (_shown.length - 1) ~/ 2));
    final order = [
      for (int k = -reach; k <= reach; k++)
        if (((centerSlot + k) - pos).abs() <= 6.0) centerSlot + k
    ]..sort((a, b) {
        final da = (a - pos).abs();
        final db = (b - pos).abs();
        final cmp = db.compareTo(da);
        return cmp != 0 ? cmp : a.compareTo(b);
      });
    return SizedBox(
      height: coverH,
      width: double.infinity,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onHorizontalDragStart: (d) => _dragStartAt(d.globalPosition.dx),
        onHorizontalDragUpdate: (d) => _dragMoveTo(d.globalPosition.dx),
        onHorizontalDragEnd: (_) => _dragEnd(),
        onHorizontalDragCancel: _dragEnd,
        child: Transform(
          alignment: Alignment.center,
          transform: Matrix4.identity()..setEntry(3, 2, -1 / 1500),
          child: Stack(
            clipBehavior: Clip.none,
            alignment: Alignment.center,
            children: [
              for (final i in order) _cover(i, i - pos, cardW, cardH, spacing),
            ],
          ),
        ),
      ),
    );
  }

  double _conveyorOpacity(double a) {
    if (a <= 3.0) return 1.0;
    if (a <= 4.0) return 0.95;
    if (a <= 5.0) return 0.85;
    return math.max(0.0, 0.85 * (1.0 - (a - 5.0)));
  }

  Widget _cover(int i, double offset, double cardW, double cardH, double spacing) {
    final t = _at(i);
    final a = offset.abs();
    final sign = offset < 0 ? -1.0 : 1.0;
    final sideScale = math.max(0.78, 1.04 - a * 0.05);
    final s = a < 1.0 ? 1.18 + (sideScale - 1.18) * a : sideScale;
    final tx = offset * spacing;
    final tz = -140.0 * math.min(a, 1.0) - 45.0 * math.max(0.0, a - 1.0);
    final ryDeg = -sign * 52.0 * math.min(a, 1.0);
    final m = Matrix4.identity()
      ..translate(tx, 0.0, tz)
      ..rotateY(ryDeg * math.pi / 180.0)
      ..scale(s, s, 1.0);
    final opacity = _conveyorOpacity(a);
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
                Positioned.fill(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: const [
                        BoxShadow(color: Color(0xE6000000), blurRadius: 50, spreadRadius: -12, offset: Offset(0, 25)),
                        BoxShadow(color: Color(0x99000000), blurRadius: 32, offset: Offset(0, 8)),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: Stack(fit: StackFit.expand, children: [
                        picture(),
                        const DecoratedBox(
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: [Color(0x1FFFFFFF), Color(0x0AFFFFFF), Color(0x00FFFFFF), Color(0x05000000), Color(0x28000000)],
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
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.white.withValues(alpha: isCurrent ? 0.45 : 0.16), width: isCurrent ? 1.1 : 0.7),
                      ),
                    ),
                  ),
                ),
                Positioned(
                  top: cardH,
                  left: 0,
                  width: cardW,
                  height: cardH * 0.45,
                  child: IgnorePointer(
                    child: Opacity(
                      opacity: isCurrent ? 0.65 : 0.45,
                      child: Transform(
                        alignment: Alignment.center,
                        transform: Matrix4.diagonal3Values(1, -1, 1),
                        child: ShaderMask(
                          blendMode: BlendMode.dstIn,
                          shaderCallback: (r) => const LinearGradient(
                            begin: Alignment.bottomCenter,
                            end: Alignment.topCenter,
                            colors: [Color(0xBFFFFFFF), Color(0x55FFFFFF), Color(0x00FFFFFF)],
                            stops: [0, 0.35, 0.85],
                          ).createShader(r),
                          child: ClipRRect(borderRadius: BorderRadius.circular(16), child: picture()),
                        ),
                      ),
                    ),
                  ),
                ),
                Positioned(
                  top: cardH + 4,
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
              ],
            ),
          ),
        ),
      ),
    );
  }

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
            disabledTracks: _disabledTracks,
            onToggleTrackEnabled: (i) => setState(() {
              if (_disabledTracks.contains(i)) {
                _disabledTracks.remove(i);
              } else if (_disabledTracks.length < t.tracks.length - 1) {
                _disabledTracks.add(i);
              }
            }),
            onSelect: (i) => _focusTrack(t, i),
            compactH: compactH,
          );
        },
      ),
    );
  }

  Widget _apply(WallpaperTheme t) {
    final store = ThemePackStore.instance;
    final price = store.priceFor(t);
    final isLocked = price != null && !store.isUnlocked(t.id);

    if (isLocked) {
      final isCurrentlyPreviewed = widget.currentTheme.id == t.id;
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Direct Set Wallpaper bypass button: sets the wallpaper immediately without unlocking account status
          VPress(
            onTap: () {
              widget.onPreviewTheme(t);
              widget.onApplyTheme(t);
            },
            child: AnimatedContainer(
              duration: VMotion.fast,
              height: 38,
              constraints: const BoxConstraints(minWidth: 132),
              padding: const EdgeInsets.symmetric(horizontal: 18),
              decoration: BoxDecoration(
                color: VColors.accentBlue,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: const Color(0x66FFFFFF), width: 0.8),
                boxShadow: const [
                  BoxShadow(color: Color(0x4D0A84FF), blurRadius: 16, offset: Offset(0, 4)),
                ],
              ),
              child: Center(
                widthFactor: 1,
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.check_rounded, size: 16, color: Colors.white),
                    const SizedBox(width: 6),
                    Text('Set Wallpaper', style: VType.callout(color: Colors.white, weight: FontWeight.w600)),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          // Production IAP Paywall Button
          VPress(
            onTap: () async {
              if (_buying) return;
              setState(() => _buying = true);
              final outcome = await store.buy(t);
              if (!mounted) return;
              setState(() => _buying = false);
              await PurchaseNotice.show(context, outcome, bypassed: store.bypass);
              if (outcome == PurchaseOutcome.purchased && mounted) widget.onApplyTheme(t);
            },
            child: AnimatedContainer(
              duration: VMotion.fast,
              height: 38,
              constraints: const BoxConstraints(minWidth: 112),
              padding: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: VColors.glassElevated,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: const Color(0x4DFFFFFF), width: 0.8),
              ),
              child: Center(
                widthFactor: 1,
                child: _buying
                    ? const CupertinoActivityIndicator(color: Colors.white, radius: 8)
                    : Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.lock_outline_rounded, size: 15, color: Colors.white),
                          const SizedBox(width: 6),
                          Text('Unlock $price', style: VType.callout(color: Colors.white, weight: FontWeight.w600)),
                        ],
                      ),
              ),
            ),
          ),
        ],
      );
    }
    return VPress(
      onTap: () => widget.onApplyTheme(t),
      child: Container(
        height: 38,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        decoration: BoxDecoration(
          color: VColors.accentBlue,
          borderRadius: BorderRadius.circular(999),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.check_rounded, size: 18, color: Colors.white),
            const SizedBox(width: 6),
            Text('Apply Theme', style: VType.callout(color: Colors.white, weight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

class _TrackWheel extends StatefulWidget {
  final List<AmbientTrack> tracks;
  final int selected;
  final Set<int> disabledTracks;
  final ValueChanged<int> onToggleTrackEnabled;
  final ValueChanged<int> onSelect;
  final bool compactH;
  const _TrackWheel({
    required this.tracks,
    required this.selected,
    required this.disabledTracks,
    required this.onToggleTrackEnabled,
    required this.onSelect,
    this.compactH = false,
  });

  @override
  State<_TrackWheel> createState() => _TrackWheelState();
}

class _TrackWheelState extends State<_TrackWheel> with SingleTickerProviderStateMixin {
  double get _rowH => widget.compactH ? 28.0 : 34.0;
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
    _c.dispose();
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
    final base = VType.callout(color: Colors.white, weight: FontWeight.w500).copyWith(fontSize: widget.compactH ? 14 : 16, height: 1.2);
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onVerticalDragStart: (_) => setState(() {
        _to = pos;
        _drag = 0;
        _dragging = true;
        _c.stop();
      }),
      onVerticalDragUpdate: (d) => setState(() => _drag += d.delta.dy),
      onVerticalDragEnd: (d) {
        final flung = pos - (d.primaryVelocity ?? 0) / 1800;
        setState(() => _dragging = false);
        _from = _to = pos;
        _choose(flung.round());
      },
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 340),
        child: SizedBox(
          height: _rowH * _rows,
          child: ShaderMask(
            blendMode: BlendMode.dstIn,
            shaderCallback: (r) => const LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Color(0x00FFFFFF), Color(0xFFFFFFFF), Color(0xFFFFFFFF), Color(0x00FFFFFF)],
              stops: [0, 0.3, 0.7, 1],
            ).createShader(r),
            child: Stack(
              clipBehavior: Clip.hardEdge,
              children: [
                for (int i = 0; i < _n; i++) _row(i, _offset(i, pos), pos, base),
              ],
            ),
          ),
        ),
      ),
    );
  }

  double _offset(int i, double pos) {
    final half = _n / 2;
    return ((i - pos + half) % _n + _n) % _n - half;
  }

  Widget _row(int i, double offset, double pos, TextStyle base) {
    final d = offset.abs().clamp(0.0, 2.5);
    final focus = (1 - d).clamp(0.0, 1.0);
    final enabled = !widget.disabledTracks.contains(i);
    final isCenter = d < 0.35;
    Widget rowContent = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        GestureDetector(
          onTap: () => widget.onToggleTrackEnabled(i),
          child: Padding(
            padding: const EdgeInsets.only(right: 6),
            child: Icon(
              enabled ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
              size: 14,
              color: enabled ? (isCenter ? VColors.accentBlue : VColors.textSecondary) : VColors.textTertiary,
            ),
          ),
        ),
        Flexible(
          child: Text(
            widget.tracks[i].title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
            style: base.copyWith(
              color: enabled ? Colors.white : VColors.textTertiary,
              decoration: enabled ? null : TextDecoration.lineThrough,
              fontWeight: FontWeight.lerp(FontWeight.w400, FontWeight.w600, focus),
              shadows: const [Shadow(color: Color(0x80000000), blurRadius: 8, offset: Offset(0, 2))],
            ),
          ),
        ),
        if (isCenter) ...[
          const SizedBox(width: 6),
          const Icon(Icons.graphic_eq_rounded, size: 14, color: VColors.accentBlue),
        ],
      ],
    );
    if (d > 0.04) {
      final sigma = 1.6 * d;
      rowContent = ImageFiltered(imageFilter: ui.ImageFilter.blur(sigmaX: sigma, sigmaY: sigma, tileMode: TileMode.decal), child: rowContent);
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
            child: Transform.scale(scale: 1 - 0.1 * d, child: Padding(padding: const EdgeInsets.symmetric(horizontal: 8), child: rowContent)),
          ),
        ),
      ),
    );
  }
}

class _Poster extends StatelessWidget {
  final WallpaperTheme theme;
  const _Poster({required this.theme});

  @override
  Widget build(BuildContext context) {
    const empty = DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFF030712), Colors.black]),
      ),
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
      constraints: const BoxConstraints(maxWidth: 420),
      child: VSearchField(
        controller: _c,
        hint: 'Search premium themes...',
        onChanged: (v) {
          setState(() {});
          if (v.trim().isEmpty) {
            widget.onClear();
          } else {
            widget.onSearch(v);
          }
        },
      ),
    );
  }
}

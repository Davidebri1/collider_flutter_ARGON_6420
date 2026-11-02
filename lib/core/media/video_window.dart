import 'dart:async';

import 'package:material_ui/material_ui.dart';
import 'package:video_player/video_player.dart';

import '../vision/vision_kit.dart';

/// Collider's own video player. Made by Claude (2026-10-18) from David's Figma reference row 19 (417:8630,
/// visionOS video player), revised the same day on his notes:
///  - proportions are the reference's: the window takes about 60% of the space it sits in (the reference: 590 of
///    960 across), the control bar about 57% of the window's width, and the bar rides over the window's lower edge
///    as a visionOS ornament does;
///  - nothing is laid over the picture: close, back and forward, play/pause, the position line, volume and more all
///    sit in the one bar under it ("the obvious thing is to include all those buttons in the ... progress bar");
///  - volume is a button; its slider shows only while it is being changed, then folds away;
///  - "more" holds the [actions] as icons.
/// The window rises into place when summoned; the bar fades after a few seconds of stillness and returns on a touch
/// or a move.
class VideoWindow extends StatefulWidget {
  final String url;
  final String? poster;
  final VoidCallback onClose;
  final List<Widget> actions;
  final bool active;

  const VideoWindow({super.key, required this.url, this.poster, required this.onClose, this.actions = const [], this.active = true});

  @override
  State<VideoWindow> createState() => _VideoWindowState();
}

class _VideoWindowState extends State<VideoWindow> with SingleTickerProviderStateMixin {
  static const _share = 0.6; // of the space the window sits in (reference: 590 / 960)
  static const _barShare = 0.57; // of the window's width (reference: 335 / 590)
  static const _barH = 40.0;

  VideoPlayerController? _c;
  double _volume = 0; // starts silent, as a looping wallpaper should
  bool _more = false;
  bool _chrome = true;
  bool _volumeOpen = false;
  Timer? _volumeFold;
  DateTime _lastTouch = DateTime.now();
  late final AnimationController _in = AnimationController(vsync: this, duration: const Duration(milliseconds: 520))..forward();

  @override
  void initState() {
    super.initState();
    if (widget.active) _start();
  }

  @override
  void didUpdateWidget(VideoWindow old) {
    super.didUpdateWidget(old);
    if (widget.active && _c == null) _start();
    final c = _c;
    if (c == null || !c.value.isInitialized) return;
    if (!widget.active && c.value.isPlaying) c.pause();
    if (widget.active && !old.active) c.play();
  }

  void _start() {
    final c = _c = VideoPlayerController.networkUrl(Uri.parse(widget.url));
    c.addListener(_tick);
    c.initialize().then((_) async {
      await c.setLooping(true);
      await c.setVolume(_volume);
      if (widget.active) await c.play();
    });
  }

  void _tick() {
    if (!mounted) return;
    final still = DateTime.now().difference(_lastTouch).inMilliseconds > 3200;
    final playing = _c?.value.isPlaying ?? false;
    setState(() => _chrome = !(still && playing && !_more && !_volumeOpen));
  }

  void _touch() {
    _lastTouch = DateTime.now();
    if (!_chrome) setState(() => _chrome = true);
  }

  @override
  void dispose() {
    _volumeFold?.cancel();
    _c?.removeListener(_tick);
    _c?.dispose();
    _in.dispose();
    super.dispose();
  }

  void _skip(int s) {
    final c = _c;
    if (c == null || !c.value.isInitialized) return;
    final d = c.value.duration;
    var p = c.value.position + Duration(seconds: s);
    if (p < Duration.zero) p = Duration.zero;
    if (p > d) p = d;
    c.seekTo(p);
    _touch();
  }

  void _seek(double dx, double w) {
    final c = _c;
    if (c == null || w <= 0 || !c.value.isInitialized) return;
    c.seekTo(c.value.duration * (dx / w).clamp(0.0, 1.0));
    _touch();
  }

  /// The slider shows while the volume is being changed and folds away 1.6 s after the last change.
  void _setVolume(double x) {
    setState(() {
      _volume = x;
      _volumeOpen = true;
    });
    _c?.setVolume(x);
    _touch();
    _volumeFold?.cancel();
    _volumeFold = Timer(const Duration(milliseconds: 1600), () => mounted ? setState(() => _volumeOpen = false) : null);
  }

  @override
  Widget build(BuildContext context) {
    final c = _c;
    final v = c?.value;
    final ready = v != null && v.isInitialized;
    final ar = ready && v.aspectRatio > 0 ? v.aspectRatio : 16 / 9;
    final d = ready ? v.duration.inMilliseconds : 0;
    final f = d == 0 ? 0.0 : (v!.position.inMilliseconds / d).clamp(0.0, 1.0);
    final rise = CurvedAnimation(parent: _in, curve: const Cubic(0.2, 0.9, 0.25, 1));
    return MouseRegion(
      onHover: (_) => _touch(),
      child: AnimatedBuilder(
        animation: rise,
        builder: (_, child) => Opacity(
          opacity: rise.value.clamp(0.0, 1.0),
          child: Transform.translate(
            offset: Offset(0, 28 * (1 - rise.value)),
            child: Transform.scale(scale: 0.94 + 0.06 * rise.value, child: child),
          ),
        ),
        child: LayoutBuilder(builder: (context, box) {
          // the reference's share of the width, never so small the bar's seven controls do not fit
          var picW = (box.maxWidth * _share).clamp(300.0, box.maxWidth);
          var picH = picW / ar;
          final maxH = box.maxHeight * 0.7;
          if (picH > maxH) {
            picH = maxH;
            picW = picH * ar;
          }
          final barW = (picW * _barShare).clamp(320.0, box.maxWidth);
          return Center(
            child: GestureDetector(
              onTap: _touch, // a tap on the player stays in it; a tap around it closes the overlay
              child: SizedBox(
                width: picW > barW ? picW : barW,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // the window: the picture only
                    Container(
                      width: picW,
                      height: picH,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(VRadius.lg),
                        boxShadow: const [BoxShadow(color: Color(0x73000000), blurRadius: 40, offset: Offset(0, 18))],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(VRadius.lg),
                        child: ready
                            ? FittedBox(fit: BoxFit.cover, child: SizedBox(width: v.size.width, height: v.size.height, child: VideoPlayer(c!)))
                            : (widget.poster != null && widget.poster!.isNotEmpty
                                ? Image.asset(widget.poster!, fit: BoxFit.cover, errorBuilder: (_, __, ___) => const ColoredBox(color: Colors.black))
                                : const ColoredBox(color: Colors.black)),
                      ),
                    ),
                    // the ornament rides over the window's lower edge
                    Transform.translate(
                      offset: const Offset(0, -_barH * 0.28),
                      child: AnimatedOpacity(
                        opacity: _chrome ? 1 : 0,
                        duration: const Duration(milliseconds: 420),
                        curve: Curves.easeOut,
                        child: IgnorePointer(
                          ignoring: !_chrome,
                          child: SizedBox(
                            width: barW,
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                VGlass(
                                  material: VMaterial.elevated,
                                  radius: VRadius.full,
                                  padding: const EdgeInsets.symmetric(horizontal: 6),
                                  child: SizedBox(
                                    height: _barH,
                                    child: Row(
                                      children: [
                                        _Plain(icon: Icons.close_rounded, onTap: widget.onClose),
                                        _Plain(icon: Icons.replay_10_rounded, onTap: () => _skip(-10)),
                                        _Plain(
                                          icon: ready && v.isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                                          size: 22,
                                          onTap: () {
                                            if (!ready) return;
                                            v.isPlaying ? c!.pause() : c!.play();
                                            _touch();
                                          },
                                        ),
                                        _Plain(icon: Icons.forward_10_rounded, onTap: () => _skip(10)),
                                        const SizedBox(width: 4),
                                        Expanded(
                                          child: LayoutBuilder(
                                            builder: (_, b) => GestureDetector(
                                              behavior: HitTestBehavior.opaque,
                                              onTapDown: (e) => _seek(e.localPosition.dx, b.maxWidth),
                                              onHorizontalDragUpdate: (e) => _seek(e.localPosition.dx, b.maxWidth),
                                              child: SizedBox(height: _barH, child: Center(child: _Line(value: f))),
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 4),
                                        _Plain(
                                          icon: _volume > 0 ? Icons.volume_up_rounded : Icons.volume_off_rounded,
                                          onTap: () => _setVolume(_volume > 0 ? 0 : 0.8),
                                        ),
                                        _Plain(
                                          icon: Icons.more_horiz_rounded,
                                          onTap: () {
                                            setState(() => _more = !_more);
                                            _touch();
                                          },
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                                // under the bar, only while in use: the volume slider, or the more actions
                                AnimatedSize(
                                  duration: VMotion.base,
                                  curve: Curves.easeOutCubic,
                                  alignment: Alignment.topCenter,
                                  child: _volumeOpen || (_more && widget.actions.isNotEmpty)
                                      ? Padding(
                                          padding: const EdgeInsets.only(top: 8),
                                          child: Align(
                                            alignment: Alignment.centerRight,
                                            child: VGlass(
                                              material: VMaterial.elevated,
                                              radius: VRadius.full,
                                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                              child: _volumeOpen
                                                  ? SizedBox(
                                                      width: 140,
                                                      height: 28,
                                                      child: LayoutBuilder(
                                                        builder: (_, b) => GestureDetector(
                                                          behavior: HitTestBehavior.opaque,
                                                          onTapDown: (e) => _setVolume((e.localPosition.dx / b.maxWidth).clamp(0.0, 1.0)),
                                                          onHorizontalDragUpdate: (e) => _setVolume((e.localPosition.dx / b.maxWidth).clamp(0.0, 1.0)),
                                                          child: Center(child: _Line(value: _volume)),
                                                        ),
                                                      ),
                                                    )
                                                  : Row(mainAxisSize: MainAxisSize.min, children: widget.actions),
                                            ),
                                          ),
                                        )
                                      : const SizedBox(width: double.infinity),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
}

class _Line extends StatelessWidget {
  final double value;
  const _Line({required this.value});

  @override
  Widget build(BuildContext context) => ClipRRect(
        borderRadius: BorderRadius.circular(VRadius.full),
        child: SizedBox(
          height: 4,
          width: double.infinity,
          child: Stack(children: [
            const Positioned.fill(child: ColoredBox(color: Color(0x40FFFFFF))),
            FractionallySizedBox(widthFactor: value, heightFactor: 1, alignment: Alignment.centerLeft, child: const ColoredBox(color: Color(0xE6FFFFFF))),
          ]),
        ),
      );
}

/// A control in the bar: a glyph with a 34 x 32 target.
class _Plain extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final double size;
  const _Plain({required this.icon, required this.onTap, this.size = 18});

  @override
  Widget build(BuildContext context) => VPress(
        onTap: onTap,
        child: SizedBox(width: 34, height: 32, child: Icon(icon, size: size, color: const Color(0xE6FFFFFF))),
      );
}


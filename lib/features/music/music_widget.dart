// The music bar. Made by Claude. Redrawn on 2026-10-04 from the frame David mapped to "Music widget":
// Vision OS Design System 417:1777, "Media Controls and Play Bar".
//   bar: a glass capsule; back, play/pause, forward as plain glyphs (white 85%), no circles
//   chip: #000000 25%, radius 10; square cover with radius 5; title 500 12/14 white; second line 500 10/12 #C9C9C9;
//         how far the track has played is a line along the chip's lower edge
//   then the list glyph and the speaker glyph (tap: mute)
// It floats over the app while a song is loaded.
// Floating, it can be dragged anywhere and stays where it is put.
// The list glyph drops a menu down: the songs, Music Player (the music in Files), and Close. A long press or a right click on the bar opens it too.
import 'package:material_ui/material_ui.dart';
import '../../core/audio/music_player.dart';
import '../../core/vision/vision_kit.dart';

class MusicBar extends StatelessWidget {
  final MusicTrack track;
  final bool playing;
  final double progress; // 0 to 1
  final String? time; // shown under the title once the track's length is known
  final VoidCallback onPrevious;
  final VoidCallback onPlayPause;
  final VoidCallback onNext;
  /// What the list glyph drops down; also the bar's press menu.
  final List<VMenuItem> Function()? menu;
  final ValueChanged<double>? onSeek; // touch along the chip to move through the track

  const MusicBar({
    super.key,
    required this.track,
    required this.playing,
    required this.onPrevious,
    required this.onPlayPause,
    required this.onNext,
    this.progress = 0,
    this.time,
    this.menu,
    this.onSeek,
  });

  static const _glyph = Color(0xD9FFFFFF); // white 85%
  static const _chipWidth = 132.0;

  Widget _button(IconData icon, double size, String tip, VoidCallback onTap) => VPress(
        onTap: onTap,
        tooltip: tip,
        child: SizedBox(width: 30, height: 40, child: Icon(icon, size: size, color: _glyph)),
      );

  @override
  Widget build(BuildContext context) {
    final p = MusicPlayer.instance;
    Widget chip = ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: _chipWidth,
        height: 36,
        color: const Color(0x40000000),
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.all(4),
              child: Row(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    // A song from Files has no theme picture: the music colour with a note (Claude, 2026-10-20).
                    child: track.art.isEmpty
                        ? Container(
                            width: 28,
                            height: 28,
                            decoration: const BoxDecoration(gradient: LinearGradient(colors: [Color(0xFFFF7A95), Color(0xFFD0105C)])),
                            child: const Icon(Icons.music_note_rounded, size: 16, color: Colors.white),
                          )
                        : Image.asset(track.art, width: 28, height: 28, fit: BoxFit.cover),
                  ),
                  const SizedBox(width: 7),
                  Expanded(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(track.title,
                            maxLines: 1,
                            softWrap: false,
                            overflow: TextOverflow.fade,
                            style: VType.caption(color: Colors.white, weight: FontWeight.w500).copyWith(fontSize: 11, height: 14 / 12)),
                        if (time != null)
                          Text(time!,
                              maxLines: 1,
                              style: VType.caption(color: const Color(0xFFC9C9C9), weight: FontWeight.w500).copyWith(fontSize: 11, height: 12 / 10)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            Positioned(left: 0, bottom: 0, child: Container(width: _chipWidth * progress, height: 2, color: Colors.white)),
          ],
        ),
      ),
    );
    if (onSeek != null) {
      chip = GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTapDown: (d) => onSeek!(d.localPosition.dx / _chipWidth),
        onHorizontalDragUpdate: (d) => onSeek!(d.localPosition.dx / _chipWidth),
        child: chip,
      );
    }

    final bar = VGlass(
      material: VMaterial.elevated,
      radius: VRadius.full,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _button(Icons.fast_rewind_rounded, 22, 'Previous', onPrevious),
          _button(playing ? Icons.pause_rounded : Icons.play_arrow_rounded, 26, playing ? 'Pause' : 'Play', onPlayPause),
          _button(Icons.fast_forward_rounded, 22, 'Next', onNext),
          const SizedBox(width: 6),
          chip,
          const SizedBox(width: 4),
          if (menu != null)
            Builder(
              builder: (c) => _button(Icons.format_list_bulleted_rounded, 19, 'Tracks', () {
                final box = c.findRenderObject() as RenderBox;
                showVMenu(c, box.localToGlobal(Offset(box.size.width, box.size.height)), menu!(), align: VMenuAlign.end);
              }),
            ),
          AnimatedBuilder(
            animation: p,
            builder: (_, __) => _button(p.muted ? Icons.volume_off_rounded : Icons.volume_up_rounded, 20, p.muted ? 'Sound On' : 'Mute', p.toggleMute),
          ),
        ],
      ),
    );
    if (menu == null) return bar;
    return GestureDetector(
      onLongPressStart: (d) => showVMenu(context, d.globalPosition, menu!()),
      onSecondaryTapDown: (d) => showVMenu(context, d.globalPosition, menu!()),
      child: bar,
    );
  }
}

/// The bar floating over the app while a track is loaded.
class MusicWidget extends StatelessWidget {
  /// Opens the music in Files.
  final VoidCallback onOpenLibrary;
  const MusicWidget({super.key, required this.onOpenLibrary});

  @override
  Widget build(BuildContext context) {
    final p = MusicPlayer.instance;
    return AnimatedBuilder(
      animation: p,
      builder: (_, __) {
        final t = p.current;
        return AnimatedSwitcher(
          duration: VMotion.base,
          transitionBuilder: (c, a) => ScaleTransition(scale: Tween(begin: 0.9, end: 1.0).animate(a), child: FadeTransition(opacity: a, child: c)),
          child: t == null
              ? const SizedBox.shrink(key: ValueKey('none'))
              : MusicBar(
                  key: const ValueKey('player'),
                  track: t,
                  playing: p.playing,
                  progress: p.progress,
                  time: p.duration > 0 ? '${musicTime(p.position)} / ${musicTime(p.duration)}' : null,
                  onPrevious: p.previous,
                  onPlayPause: p.toggle,
                  onNext: p.next,
                  menu: () => [
                    for (int i = 0; i < p.queue.length; i++) VMenuItem(null, p.queue[i].title, () => p.play(i), checked: i == p.index),
                    VMenuItem(null, 'Music Player', onOpenLibrary, apart: true),
                    VMenuItem(null, 'Close', p.close),
                  ],
                ),
        );
      },
    );
  }
}

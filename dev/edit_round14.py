# Made by Claude (2026-10-21). Round 14: Premium Theme Market as David set it out on 21 Oct:
#  "dim ... when browsing through locked live wallpapers. Unlocked live wallpapers are fully lit. Thumbnails during
#   browsing are always fully lit and play the preview video in full. Background video is just like the source(unless
#   unlocked, then it's full resolution and no dim)." "lose the music player icons: play, skip track (left and right).
#   And any other leftovers from the music source. Make sure the dim is the same as the source. That was nearly black."
# The source (SimpleBackgroundVideo.tsx) blurs the video 20px at brightness 0.5, contrast 1.2, opacity 0.7, under 20%
# black; and the YouTube frame it plays is 16:9 letterboxed inside a 200vw x 200vh box, so on a phone most of what
# shows is the black of the bars: nearly black. The same darkness is drawn here directly: brightness 0.3 (so 0.36 with
# the contrast), opacity 0.7, under 35% black, with the edges falling away to black (the bars).
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new, n in pairs:
        if s.count(old) != n:
            sys.exit(f"{rel}: expected {n} match(es) for: {old[:80]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


def cut(rel, start, end):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    a = s.index(start)
    z = s.index(end, a)
    p.write_text(s[:a] + s[z:], encoding="utf-8")
    print("cut", rel, start[:40])


PM = "lib/features/theme/premium_theme_market_view.dart"
edit(PM, [
    ("""                                    SizedBox(height: gapPlayer),
                                    _player(t, compactH: compactH),
""", "", 1),
    ("""    if ((i - _index).abs() > 1 || t.videoPath == null) return null;""",
     """    if ((i - _index).abs() > 4 || t.videoPath == null) return null; // every cover on screen plays (David, 21 Oct)""", 1),
    ("""    final gone = _live.keys.where((k) => (k - _index).abs() > 1).toList();""",
     """    final gone = _live.keys.where((k) => (k - _index).abs() > 4).toList();""", 1),
    ("""    final opacity = d <= 2 ? 1.0 : d <= 3 ? 0.95 : d <= 4 ? 0.9 : math.max(0.8, 0.9 - (d - 4) * 0.05);""",
     """    const opacity = 1.0; // covers are always fully lit (David, 21 Oct)""", 1),
    ("""                  const Positioned(top: 12, right: 12, child: _Pulse()),
""", "", 1),
    ("""            builder: (_, img, __) => img == null ? _Poster(theme: t) : RawImage(image: img, fit: BoxFit.cover, filterQuality: FilterQuality.medium),""",
     """            builder: (_, img, __) => img == null ? _Poster(theme: t) : RawImage(image: img, fit: BoxFit.cover, filterQuality: FilterQuality.high),""", 1),
])
cut(PM, "  // ---------------------------------------------------------------- Player.tsx: drawing", "  /// The pack's preview tracks.")
cut(PM, "class _Pulse extends StatefulWidget {", "class _SearchBar extends StatefulWidget {")
p = ROOT / PM
s = p.read_text(encoding="utf-8")
a = s.index("  void _togglePlay() {")
z = s.index("\n  }\n", a) + len("\n  }\n")
s = s[:a] + s[z:]
p.write_text(s, encoding="utf-8")
print("cut _togglePlay")

edit("lib/core/media/theme_blur_cache.dart", [
    ("""            0.6, 0, 0, 0, -25.5,
            0, 0.6, 0, 0, -25.5,
            0, 0, 0.6, 0, -25.5,""", """            0.36, 0, 0, 0, -25.5,
            0, 0.36, 0, 0, -25.5,
            0, 0, 0.36, 0, -25.5,""", 1),
    ("""        0.6, 0, 0, 0, -25.5,
        0, 0.6, 0, 0, -25.5,
        0, 0, 0.6, 0, -25.5,""", """        0.36, 0, 0, 0, -25.5,
        0, 0.36, 0, 0, -25.5,
        0, 0, 0.36, 0, -25.5,""", 1),
    ("""          canvas.drawRect(dstRect, Paint()..color = const Color(0x33000000));""",
     """          canvas.drawRect(dstRect, Paint()..color = const Color(0x59000000));
          canvas.drawRect(dstRect, Paint()..shader = _edges(dstRect));""", 1),
    ("""      canvas.drawRect(dst, Paint()..color = const Color(0x33000000));""",
     """      canvas.drawRect(dst, Paint()..color = const Color(0x59000000));
      canvas.drawRect(dst, Paint()..shader = _edges(dst));""", 1),
])
p = ROOT / "lib/core/media/theme_blur_cache.dart"
s = p.read_text(encoding="utf-8")
s = s.rstrip() + '''

/// The source's letterbox: the picture falls away to black toward the top and bottom edges (Claude, 2026-10-21).
Shader _edges(Rect r) => const LinearGradient(
      begin: Alignment.topCenter,
      end: Alignment.bottomCenter,
      colors: [Color(0xF2000000), Color(0x00000000), Color(0x00000000), Color(0xF2000000)],
      stops: [0.0, 0.3, 0.7, 1.0],
    ).createShader(r);
'''
p.write_text(s, encoding="utf-8")
print("added _edges")

edit("lib/main.dart", [
    ("""import 'features/theme/theme_living_media.dart';
""", """import 'features/theme/theme_living_media.dart';
import 'features/theme/theme_pack_store.dart';
""", 1),
    ("""              builderAmbient: _activeDrawer == 'premium',""",
     """              // Locked: the source's near-black dim. Unlocked (or free): the wallpaper itself, full and lit (David, 21 Oct).
              builderAmbient: _activeDrawer == 'premium' && _locked(_currentTheme),""", 1),
    ("""  Widget _buildSideNav({required bool isMobile}) {""",
     """  bool _locked(WallpaperTheme t) => ThemePackStore.instance.priceFor(t) != null && !ThemePackStore.instance.isUnlocked(t.id);

  Widget _buildSideNav({required bool isMobile}) {""", 1),
])

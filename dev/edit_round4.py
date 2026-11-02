# Made by Claude (2026-10-21). Round 4: editor toolbar at the 44-point minimum; songs in Files.
# David, 20 Oct: "only generated music. and only in the music player menu. not the music widget."
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for: {old[:70]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("dev/editor/src/style.css", [
    (".btn { width: 32px; height: 32px; border-radius: 10px;",
     ".btn { width: 44px; height: 44px; border-radius: 12px;"),
    (".btn:hover { background: rgba(255,255,255,.10); }",
     "@media (hover: hover) { .btn:hover { background: rgba(255,255,255,.10); } }\n"
     ".btn:active { background: rgba(255,255,255,.16); }"),
    (".ico { font-family: 'Symbols'; font-size: 20px;",
     ".ico { font-family: 'Symbols'; font-size: 22px;"),
    ("select.pick { height: 32px;", "select.pick { height: 44px;"),
    (".name { flex: 1 1 160px; min-width: 120px; height: 32px;",
     ".name { flex: 1 1 160px; min-width: 120px; height: 44px;"),
])

FS = "lib/features/files/screens/files_screen.dart"
edit(FS, [
    ("import '../../../core/audio/music_player.dart';\n",
     "import '../../../core/audio/generated_songs.dart';\nimport '../../../core/audio/music_player.dart';\n"),
    ("""    // An uploaded, generated or downloaded song plays in the music bar, with the songs listed beside it.
    if (f != null && !f.asset && f.kind == 'audio') {
      final songs = _shown().where((x) => x.kind == 'audio' && !x.asset).toList();
      final at = songs.indexOf(f);
      MusicPlayer.instance.play(at < 0 ? 0 : at,
          list: [for (final s in (at < 0 ? [f] : songs)) MusicTrack(s.name.replaceFirst(RegExp(r'\\.[^.]+$'), ''), '', _api.fileUrl(s))],
          id: 'files-${_view.source}');
      return;
    }
""",
     """    // A song a model made plays here, in Files > Music, in its own row; never in the music bar (David, 20 Oct).
    // Songs uploaded or downloaded do not play in the app; they open to their cover. (Claude, 2026-10-21)
    if (f != null && !f.asset && f.kind == 'audio' && f.source == 'generated') {
      if (_view.kind != 'music') {
        setState(() {
          _history.removeRange(_at + 1, _history.length);
          _history.add(_View(_view.source, kind: 'music', model: _view.model));
          _at++;
        });
      }
      GeneratedSongs.instance.toggle(_api.fileUrl(f));
      return;
    }
"""),
    ("""  Widget _preview(ColliderFile f) {
""",
     """  Widget _preview(ColliderFile f) {
    if (f.kind == 'audio') return Center(child: _Thumb(file: f, api: _api, width: 180));
"""),
    ("""            _Thumb(file: file, api: api, width: 88),
            const SizedBox(height: 10),""",
     """            file.kind == 'audio' && file.source == 'generated'
                ? _SongState(url: api.fileUrl(file), child: _Thumb(file: file, api: api, width: 88))
                : _Thumb(file: file, api: api, width: 88),
            const SizedBox(height: 10),"""),
    ("""        child: Row(children: [
          _Thumb(file: file, api: api, width: 44),""",
     """        child: Row(children: [
          file.kind == 'audio' && file.source == 'generated'
              ? _SongState(url: api.fileUrl(file), child: _Thumb(file: file, api: api, width: 44))
              : _Thumb(file: file, api: api, width: 44),"""),
])

p = ROOT / FS
p.write_text(p.read_text(encoding="utf-8") + '''
/// A generated song's cover with its state on it: a pause glyph while it plays and the line of how far it has got.
/// Made by Claude (2026-10-21).
class _SongState extends StatelessWidget {
  final String url;
  final Widget child;
  const _SongState({required this.url, required this.child});

  @override
  Widget build(BuildContext context) {
    final s = GeneratedSongs.instance;
    return AnimatedBuilder(
      animation: s,
      builder: (_, __) {
        final on = s.isPlaying(url);
        final started = s.url == url && s.position > 0;
        return Stack(alignment: Alignment.center, children: [
          child,
          AnimatedOpacity(
            opacity: on ? 1 : 0,
            duration: const Duration(milliseconds: 220),
            child: Container(
              width: 30,
              height: 30,
              decoration: const BoxDecoration(color: Color(0x66000000), shape: BoxShape.circle),
              child: const Icon(Icons.pause_rounded, size: 20, color: Colors.white),
            ),
          ),
          if (started)
            Positioned(
              left: 6,
              right: 6,
              bottom: 6,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(2),
                child: LinearProgressIndicator(
                  value: s.progressOf(url),
                  minHeight: 3,
                  backgroundColor: const Color(0x40FFFFFF),
                  valueColor: const AlwaysStoppedAnimation(Colors.white),
                ),
              ),
            ),
        ]);
      },
    );
  }
}
''', encoding="utf-8")
print("appended _SongState")

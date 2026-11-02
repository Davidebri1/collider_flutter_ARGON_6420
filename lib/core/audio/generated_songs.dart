// Made by Claude (2026-10-20). Songs made by the models play here, in the Music Player (Files > Music), each in its
// own row; the music bar is only for the songs that come with the live wallpapers.
// David, 20 Oct: "only generated music. and only in the music player menu. not the music widget. the music widget is
// only for the curated songs with the live wallpaper." Songs uploaded or downloaded do not play in the app.
import 'package:flutter/foundation.dart';
import 'audio_engine_stub.dart' if (dart.library.js_interop) 'audio_engine_web.dart';
import 'music_player.dart';

class GeneratedSongs extends ChangeNotifier {
  GeneratedSongs._() {
    _engine.onEnded = () {
      playing = false;
      position = 0;
      notifyListeners();
    };
    _engine.onTime = (p, d) {
      position = p;
      duration = d;
      notifyListeners();
    };
  }
  static final GeneratedSongs instance = GeneratedSongs._();
  final AudioEngine _engine = AudioEngine();

  String url = '';
  bool playing = false;
  double position = 0;
  double duration = 0;

  bool isPlaying(String u) => playing && url == u;
  double progressOf(String u) => url == u && duration > 0 ? (position / duration).clamp(0.0, 1.0) : 0;

  /// Plays [u], or pauses it when it is the one playing. One sound at a time: the music bar pauses.
  void toggle(String u) {
    if (url == u && playing) {
      _engine.pause();
      playing = false;
    } else {
      final bar = MusicPlayer.instance;
      if (bar.playing) bar.toggle();
      if (url != u) {
        position = 0;
        duration = 0;
      }
      url = u;
      _engine.play(u);
      playing = true;
    }
    notifyListeners();
  }

  void stop() {
    _engine.stop();
    playing = false;
    notifyListeners();
  }
}

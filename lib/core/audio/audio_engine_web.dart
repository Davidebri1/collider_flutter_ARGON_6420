// Web audio engine. Made by Claude.
import 'dart:js_interop';
import 'package:web/web.dart' as web;

class AudioEngine {
  web.HTMLAudioElement? _el;
  String _src = '';
  bool _muted = false;
  void Function()? onEnded;

  /// Called when the browser refuses to start sound.
  void Function()? onBlocked;

  /// Called as the track advances: seconds played, seconds in total (0 until known).
  void Function(double position, double duration)? onTime;

  void _tick(web.Event _) {
    final e = _el;
    if (e == null) return;
    final d = e.duration;
    onTime?.call(e.currentTime.toDouble(), d.isFinite ? d.toDouble() : 0);
  }

  void play(String url) {
    if (_el == null) {
      _el = web.HTMLAudioElement();
      _el!.addEventListener('ended', ((web.Event _) { onEnded?.call(); }).toJS);
      _el!.addEventListener('timeupdate', _tick.toJS);
      _el!.addEventListener('loadedmetadata', _tick.toJS);
      _el!.muted = _muted;
    }
    if (_src != url) {
      _src = url;
      _el!.src = url;
    }
    _el!.play().toDart.catchError((Object e) {
      if ('$e'.contains('NotAllowed')) onBlocked?.call();
      return null;
    });
  }

  void pause() => _el?.pause();

  void setMuted(bool m) {
    _muted = m;
    _el?.muted = m;
  }

  void seek(double seconds) {
    if (_el != null) _el!.currentTime = seconds;
  }

  void stop() {
    _el?.pause();
    _el = null;
    _src = '';
  }
}

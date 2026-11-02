import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';

class LiveFrames {
  factory LiveFrames(String url, {int width = 480, int fps = 20, bool wantAmbient = false}) {
    final existing = _pool.remove(url);
    if (existing != null) {
      _pool[url] = existing;
      existing._refs++;
      if (wantAmbient) existing._ambientRefs++;
      existing.play();
      return existing;
    }
    final created = LiveFrames._internal(url, width: width, fps: fps, wantAmbient: wantAmbient);
    _pool[url] = created;
    return created;
  }

  LiveFrames._internal(this.url, {this.width = 480, int fps = 20, bool wantAmbient = false})
      : _ambientRefs = wantAmbient ? 1 : 0;

  static final Map<String, LiveFrames> _pool = {};

  final String url;
  final int width;
  int _refs = 1;
  int _ambientRefs;

  final ValueNotifier<ui.Image?> frame = ValueNotifier(null);
  final ValueNotifier<ui.Image?> ambientFrame = ValueNotifier(null);

  void play() {}
  void pause() {}

  void release({bool wantAmbient = false}) {
    if (wantAmbient && _ambientRefs > 0) _ambientRefs--;
    if (_refs > 0) _refs--;
    if (_refs <= 0) pause();
  }

  void dispose() => release();
}

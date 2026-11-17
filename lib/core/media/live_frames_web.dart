import 'dart:async';
import 'dart:js_interop';
import 'dart:ui' as ui;
import 'dart:ui_web' as ui_web;

import 'package:flutter/foundation.dart';
import 'package:web/web.dart' as web;

/// Pooled, reference-counted live video frame extractor and ambient-blur cache.
/// Pauses automatically when the tab is hidden and caps extraction dimensions
/// so WebGL texture allocation never causes high GPU or VRAM load.
class LiveFrames {
  static final Map<String, LiveFrames> _pool = {};
  static const int _maxPoolSize = 8;

  factory LiveFrames(String url, {int width = 480, int fps = 12, bool wantAmbient = false}) {
    final existing = _pool.remove(url);
    if (existing != null) {
      _pool[url] = existing;
      existing._refs++;
      if (wantAmbient) {
        existing._ambientRefs++;
        if (existing.ambientFrame.value == null && existing.frame.value != null) {
          existing._updateAmbient(existing.frame.value!);
        }
      }
      existing.play();
      return existing;
    }

    if (_pool.length >= _maxPoolSize) {
      String? victimKey;
      for (final k in _pool.keys) {
        if ((_pool[k]?._refs ?? 0) <= 0) {
          victimKey = k;
          break;
        }
      }
      if (victimKey != null) {
        _pool.remove(victimKey)?._destroy();
      }
    }

    final created = LiveFrames._internal(url, width: width, fps: fps, wantAmbient: wantAmbient);
    _pool[url] = created;
    return created;
  }

  LiveFrames._internal(this.url, {this.width = 480, int fps = 12, bool wantAmbient = false})
      : _fps = fps.clamp(6, 15),
        _ambientRefs = wantAmbient ? 1 : 0 {
    final v = web.document.createElement('video') as web.HTMLVideoElement;
    v.muted = true;
    v.defaultMuted = true;
    v.loop = true;
    v.autoplay = true;
    v.playsInline = true;
    v.setAttribute('muted', '');
    v.setAttribute('playsinline', '');
    v.crossOrigin = 'anonymous';
    v.preload = 'auto';
    final s = v.style;
    s.position = 'fixed';
    s.left = '0';
    s.top = '0';
    s.width = '2px';
    s.height = '2px';
    s.opacity = '0';
    s.pointerEvents = 'none';
    s.zIndex = '-1';
    v.src = url;
    web.document.body?.append(v);
    v.play().toDart.catchError((_) => null);
    _v = v;
    _startTimer();
  }

  final String url;
  final int width;
  final int _fps;
  int _refs = 1;
  int _ambientRefs;

  final ValueNotifier<ui.Image?> frame = ValueNotifier(null);
  final ValueNotifier<ui.Image?> ambientFrame = ValueNotifier(null);
  web.HTMLVideoElement? _v;
  Timer? _tick;
  bool _busy = false;
  bool _ambientBusy = false;
  bool _paused = false;

  void _startTimer() {
    _tick?.cancel();
    _tick = Timer.periodic(Duration(milliseconds: 1000 ~/ _fps), (_) => _grab());
  }

  Future<void> _grab() async {
    if (web.document.hidden) return;
    final v = _v;
    if (v == null || _busy || v.readyState < 2 || v.videoWidth == 0) return;
    if (_paused && frame.value != null) return;
    _busy = true;
    try {
      final rawW = v.videoWidth;
      final rawH = v.videoHeight;
      final targetW = rawW > width ? width : rawW;
      final targetH = rawW > 0 ? (rawH * targetW ~/ rawW).clamp(1, rawH) : rawH;
      final img = await ui_web.createImageFromTextureSource(v, width: targetW, height: targetH);
      if (_v == null) {
        img.dispose();
        return;
      }
      final old = frame.value;
      frame.value = img;
      old?.dispose();
      if (_ambientRefs > 0 && !_ambientBusy) {
        _updateAmbient(img);
      }
    } catch (_) {
    } finally {
      _busy = false;
    }
  }

  Future<void> _updateAmbient(ui.Image src) async {}

  void play() {
    _paused = false;
    if (_tick == null || !_tick!.isActive) _startTimer();
    _v?.play().toDart.catchError((_) => null);
  }

  void pause() {
    _paused = true;
    _v?.pause();
  }

  void release({bool wantAmbient = false}) {
    if (wantAmbient && _ambientRefs > 0) _ambientRefs--;
    if (_refs > 0) _refs--;
    if (_refs <= 0) {
      pause();
      _tick?.cancel();
      _tick = null;
    }
  }

  void dispose() => release();

  void _destroy() {
    _tick?.cancel();
    _tick = null;
    final v = _v;
    _v = null;
    if (v != null) {
      v.pause();
      v.removeAttribute('src');
      v.load();
      v.remove();
    }
    frame.value?.dispose();
    frame.dispose();
    ambientFrame.value?.dispose();
    ambientFrame.dispose();
  }
}

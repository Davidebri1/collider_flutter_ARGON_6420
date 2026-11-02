// Made by Claude (2026-10-20). Voice chat (web): the microphone is heard until the speaker stops talking, the
// recording becomes text on the app's server (Groq Whisper, set in the configuration), and answers are read aloud
// with the computer's own voices.
import 'dart:async';
import 'dart:js_interop';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:web/web.dart' as web;

import '../api/collider_api.dart';

class Voice {
  Voice._();
  static final Voice instance = Voice._();

  /// How loud the microphone is right now, 0 to 1, while listening.
  final ValueNotifier<double> level = ValueNotifier(0);
  bool get supported => true;

  web.MediaStream? _stream;
  web.MediaRecorder? _rec;
  web.AudioContext? _ctx;
  Timer? _tick;
  bool _cancelled = false;
  int _speech = 0; // bumps when speaking is stopped, so queued sentences are dropped

  /// Listens until the speaker has been quiet for [silence]; the words said, or null when nothing was said.
  Future<String?> listen({
    Duration silence = const Duration(milliseconds: 1400),
    Duration longest = const Duration(seconds: 90),
    Duration wait = const Duration(seconds: 20),
  }) async {
    cancelListening();
    stopSpeaking();
    _cancelled = false;
    try {
      _stream = await web.window.navigator.mediaDevices.getUserMedia(web.MediaStreamConstraints(audio: true.toJS)).toDart;
    } catch (_) {
      return null;
    }
    final stream = _stream!;
    const kinds = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
    final mime = kinds.firstWhere((m) => web.MediaRecorder.isTypeSupported(m), orElse: () => '');
    final rec = mime.isEmpty ? web.MediaRecorder(stream) : web.MediaRecorder(stream, web.MediaRecorderOptions(mimeType: mime));
    _rec = rec;
    final chunks = <JSAny>[];
    final stopped = Completer<void>();
    rec.ondataavailable = ((web.BlobEvent e) {
      if (e.data.size > 0) chunks.add(e.data);
    }).toJS;
    rec.onstop = ((web.Event _) {
      if (!stopped.isCompleted) stopped.complete();
    }).toJS;
    rec.start(250);

    // Loudness, to know when speech starts and when it has ended. The room's own noise is learnt first.
    final ctx = web.AudioContext();
    _ctx = ctx;
    final an = ctx.createAnalyser()..fftSize = 1024;
    ctx.createMediaStreamSource(stream).connect(an);
    final samples = Float32List(1024).toJS;
    final start = DateTime.now();
    var lastVoice = start;
    var heard = false;
    var floor = 0.0;
    var frames = 0;
    _tick = Timer.periodic(const Duration(milliseconds: 50), (_) {
      an.getFloatTimeDomainData(samples);
      final s = samples.toDart;
      var sum = 0.0;
      for (final v in s) {
        sum += v * v;
      }
      final rms = math.sqrt(sum / s.length);
      level.value = (rms * 10).clamp(0.0, 1.0);
      final now = DateTime.now();
      if (frames++ < 6) {
        floor = math.max(floor, rms);
        return;
      }
      if (rms > math.max(0.015, floor * 3)) {
        heard = true;
        lastVoice = now;
      }
      final done = (heard && now.difference(lastVoice) > silence) ||
          now.difference(start) > longest ||
          (!heard && now.difference(start) > wait);
      if (done) finishListening();
    });

    await stopped.future;
    _release();
    if (_cancelled || !heard || chunks.isEmpty) return null;
    final type = rec.mimeType.isEmpty ? 'audio/webm' : rec.mimeType;
    final blob = web.Blob(chunks.toJS, web.BlobPropertyBag(type: type));
    final bytes = (await blob.arrayBuffer().toDart).toDart.asUint8List();
    final text = await ColliderApi.instance.transcribe(bytes, type);
    return (text == null || text.isEmpty) ? null : text;
  }

  /// Stops listening now and keeps what was said.
  void finishListening() {
    final r = _rec;
    if (r != null && r.state == 'recording') r.stop();
  }

  /// Stops listening and drops what was said.
  void cancelListening() {
    _cancelled = true;
    finishListening();
    _release();
  }

  void _release() {
    _tick?.cancel();
    _tick = null;
    final s = _stream;
    if (s != null) {
      for (final t in s.getTracks().toDart) {
        t.stop();
      }
    }
    _stream = null;
    _ctx?.close();
    _ctx = null;
    _rec = null;
    level.value = 0;
  }

  /// Reads [text] aloud, a sentence at a time; returns when it has been read or reading was stopped.
  Future<void> speak(String text) async {
    stopSpeaking();
    final run = _speech;
    final synth = web.window.speechSynthesis;
    var voices = synth.getVoices().toDart;
    for (var i = 0; voices.isEmpty && i < 6; i++) {
      await Future<void>.delayed(const Duration(milliseconds: 150));
      voices = synth.getVoices().toDart;
    }
    // The most natural English voice on the computer.
    int score(web.SpeechSynthesisVoice v) =>
        (v.lang.toLowerCase().startsWith('en') ? 4 : 0) + (v.name.contains('Natural') ? 2 : 0) + (v.localService ? 1 : 0);
    final voice = voices.isEmpty ? null : (voices.toList()..sort((a, b) => score(b) - score(a))).first;
    for (final sentence in _sentences(_plain(text))) {
      if (run != _speech) return;
      final u = web.SpeechSynthesisUtterance(sentence);
      if (voice != null) u.voice = voice;
      final done = Completer<void>();
      void end(web.Event _) {
        if (!done.isCompleted) done.complete();
      }
      u.onend = end.toJS;
      u.onerror = end.toJS;
      synth.speak(u);
      await done.future;
    }
  }

  void stopSpeaking() {
    _speech++;
    web.window.speechSynthesis.cancel();
  }

  /// What is read: the words only, without markdown, links or citation marks.
  static String _plain(String s) => s
      .replaceAll(RegExp(r'```[\s\S]*?```'), ' ')
      .replaceAllMapped(RegExp(r'\[([^\]]+)\]\([^)]+\)'), (m) => m[1]!)
      .replaceAll(RegExp(r'\[\d+(?:,\s*\d+)*\]'), '')
      .replaceAll(RegExp(r'[*_`#>|]'), '')
      .replaceAll(RegExp(r'https?://\S+'), '')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

  static Iterable<String> _sentences(String s) sync* {
    final parts = RegExp(r'[^.!?]+[.!?]*\s*').allMatches(s).map((m) => m[0]!.trim()).where((p) => p.isNotEmpty);
    var buf = '';
    for (final p in parts) {
      if (buf.isNotEmpty && buf.length + p.length > 220) {
        yield buf;
        buf = '';
      }
      buf = buf.isEmpty ? p : '$buf $p';
    }
    if (buf.isNotEmpty) yield buf;
  }
}

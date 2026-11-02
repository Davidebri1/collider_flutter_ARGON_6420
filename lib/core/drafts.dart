// Made by Claude (2026-10-21). Unsent messages belong to the person writing them.
// David, 21 Oct: "if i draft a message and click on 'models' ... the drafted message, which is often hours of work for
// me, is inexplicably and illogically wiped ... no one should ever have power over the user's personal belongings."
// Cause: each box kept its words inside itself, and the screen removes a box from view when another surface opens
// (main.dart hides the ticker and composer while Models, a drawer or an app is open). Flutter discards a removed
// widget's state, so the words went with it. Here the words live apart from any box, for as long as the app runs, and
// are kept on the device too, so a reload or a closed tab does not lose them either. Only sending empties a draft.
import 'dart:async';
import 'dart:convert';

import 'package:flutter/widgets.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Drafts {
  Drafts._();
  static const _key = 'drafts_v1';
  static final Map<String, TextEditingController> _boxes = {};
  static final Map<String, List<String>> _files = {};
  static Map<String, dynamic> _saved = {};
  static bool _loaded = false;
  static Timer? _write;

  /// Reads the kept drafts once, at start (main.dart awaits it before the first screen).
  static Future<void> load() async {
    if (_loaded) return;
    _loaded = true;
    try {
      final p = await SharedPreferences.getInstance();
      _saved = jsonDecode(p.getString(_key) ?? '{}') as Map<String, dynamic>;
    } catch (_) {
      _saved = {};
    }
  }

  /// The words of draft [id] ('composer', 'discover', 'reply:<model>'): the same controller every time the box shows.
  static TextEditingController text(String id) => _boxes.putIfAbsent(id, () {
        final s = _saved[id];
        final c = TextEditingController(text: s is Map ? '${s['text'] ?? ''}' : '');
        c.addListener(_keep);
        return c;
      });

  /// The files attached to draft [id], kept the same way.
  static List<String> files(String id) => _files.putIfAbsent(id, () {
        final s = _saved[id];
        return s is Map && s['files'] is List ? [for (final f in s['files'] as List) '$f'] : <String>[];
      });

  /// After the files of a draft change.
  static void touch() => _keep();

  /// Sending is the one thing that empties a draft.
  static void sent(String id) {
    _boxes[id]?.clear();
    _files[id]?.clear();
    _keep();
  }

  static void _keep() {
    _write?.cancel();
    _write = Timer(const Duration(milliseconds: 400), () async {
      final out = <String, dynamic>{};
      for (final id in {..._boxes.keys, ..._files.keys}) {
        final t = _boxes[id]?.text ?? '';
        final f = _files[id] ?? const <String>[];
        if (t.isNotEmpty || f.isNotEmpty) out[id] = {'text': t, 'files': f};
      }
      _saved = out;
      try {
        (await SharedPreferences.getInstance()).setString(_key, jsonEncode(out));
      } catch (_) {}
    });
  }
}

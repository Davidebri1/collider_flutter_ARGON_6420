// Smart Gen's cards, kept on this device and synced with Collider's consensus synthesis sessions.
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/api/collider_api.dart';

class SgCard {
  final String id;
  String title;
  String subtitle;
  String score;
  bool done;
  SgCard({
    required this.id,
    required this.title,
    this.subtitle = '',
    this.score = '',
    this.done = false,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        if (subtitle.isNotEmpty) 'subtitle': subtitle,
        if (score.isNotEmpty) 'score': score,
        if (done) 'done': true,
      };
  factory SgCard.fromJson(Map<String, dynamic> j) => SgCard(
        id: j['id'] as String,
        title: (j['title'] as String?) ?? '',
        subtitle: (j['subtitle'] as String?) ?? '',
        score: (j['score'] as String?) ?? '',
        done: j['done'] == true,
      );
}

class SmartGenStore extends ChangeNotifier {
  SmartGenStore._();
  static final SmartGenStore instance = SmartGenStore._();

  static const _key = 'smartgen_board_v2';
  static const _dismissedKey = 'smartgen_dismissed_v2';
  final Map<String, List<SgCard>> _lists = {};
  final Set<String> _dismissedIds = {};
  bool _loaded = false;

  static bool _isTrivialCard(String title) {
    final t = title.trim().toLowerCase();
    return t.isEmpty ||
        t == 'four' ||
        t == '4' ||
        t.startsWith('i am glm') ||
        t.startsWith('nemotron 3 super by') ||
        t.startsWith('i am nemotron') ||
        t == 'who are you' ||
        t == 'what is 2+2';
  }

  List<SgCard> list(String name) => _lists.putIfAbsent(name, () => []);

  Future<void> load() async {
    if (_loaded) {
      unawaited(syncAutonomousCards());
      return;
    }
    _loaded = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_key);
      if (raw != null) {
        final j = jsonDecode(raw) as Map<String, dynamic>;
        for (final e in j.entries) {
          _lists[e.key] = [
            for (final c in (e.value as List))
              if (!_isTrivialCard('${(c as Map)['title'] ?? ''}'))
                SgCard.fromJson(c.cast<String, dynamic>()),
          ];
        }
      }
      final dis = prefs.getStringList(_dismissedKey);
      if (dis != null) _dismissedIds.addAll(dis);
    } catch (e) {
      debugPrint('SmartGenStore: $e');
    }
    notifyListeners();
    await syncAutonomousCards();
  }

  /// Syncs autonomous cards extracted from real Collider conversation history (/api/smartgen).
  Future<void> syncAutonomousCards() async {
    try {
      final remote = await ColliderApi.instance.smartgenCards();
      if (remote.isEmpty) return;
      final existingIds = <String>{
        ..._dismissedIds,
        for (final l in _lists.values)
          for (final c in l) c.id,
      };
      final existingTitles = <String>{
        for (final l in _lists.values)
          for (final c in l) c.title.toLowerCase().trim(),
      };
      var added = false;
      for (final item in remote) {
        final id = '${item['id'] ?? ''}'.trim();
        final listName = '${item['list'] ?? 'Medium'}'.trim();
        final title = '${item['title'] ?? ''}'.trim();
        final content = '${item['content'] ?? ''}'.trim();
        final score = '${item['score'] ?? ''}'.trim();
        if (id.isEmpty || title.isEmpty || _isTrivialCard(title)) continue;
        if (existingIds.contains(id)) {
          // Update existing card if title was upgraded on server
          for (final l in _lists.values) {
            for (final c in l) {
              if (c.id == id && (c.title != title || c.subtitle != content || c.score != score)) {
                c.title = title;
                c.subtitle = content;
                c.score = score;
                added = true;
              }
            }
          }
          continue;
        }
        if (existingTitles.contains(title.toLowerCase())) continue;
        list(listName).add(SgCard(
          id: id,
          title: title,
          subtitle: content,
          score: score,
          done: item['done'] == true,
        ));
        existingIds.add(id);
        existingTitles.add(title.toLowerCase());
        added = true;
      }
      if (added) await _save();
    } catch (_) {}
  }

  Future<void> _save() async {
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_key, jsonEncode({for (final e in _lists.entries) e.key: [for (final c in e.value) c.toJson()]}));
      await prefs.setStringList(_dismissedKey, _dismissedIds.toList());
    } catch (_) {}
  }

  SgCard add(String listName, String title) {
    final c = SgCard(id: DateTime.now().microsecondsSinceEpoch.toRadixString(36), title: title.trim());
    list(listName).add(c);
    _save();
    return c;
  }

  void update(SgCard c, {String? title, bool? done}) {
    if (title != null) c.title = title;
    if (done != null) c.done = done;
    _save();
  }

  void remove(SgCard c) {
    _dismissedIds.add(c.id);
    for (final l in _lists.values) {
      l.remove(c);
    }
    _save();
  }

  void move(SgCard c, String listName, int? index) {
    String? from;
    int fromIndex = -1;
    for (final e in _lists.entries) {
      final i = e.value.indexOf(c);
      if (i >= 0) {
        from = e.key;
        fromIndex = i;
        e.value.removeAt(i);
        break;
      }
    }
    final to = list(listName);
    var at = index ?? to.length;
    if (from == listName && fromIndex >= 0 && fromIndex < at) at -= 1;
    to.insert(at.clamp(0, to.length), c);
    _save();
  }
}

void unawaited(Future<void> f) {}

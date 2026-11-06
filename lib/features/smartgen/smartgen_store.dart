// Smart Gen's cards, typed fields, spatial canvas coordinates, and event-driven automation hooks.
// Combines Collider's autonomous consensus synthesis (/api/smartgen) with the Smart Gen Clone
// typed fields (fields.ts), automation hooks (hooks.ts), board/hold kinds, and 2D CanvasPlane.
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/api/collider_api.dart';

enum SgFieldKind {
  text,
  textarea,
  number,
  date,
  select,
  checkbox,
  url,
  person,
}

class SgFieldDef {
  final String key;
  final String name;
  final SgFieldKind kind;
  final List<String> options;
  const SgFieldDef({
    required this.key,
    required this.name,
    required this.kind,
    this.options = const [],
  });
}

const List<SgFieldDef> kDefaultSgFields = [
  SgFieldDef(key: 'status', name: 'Status', kind: SgFieldKind.select, options: ['open', 'doing', 'done']),
  SgFieldDef(key: 'due', name: 'Due', kind: SgFieldKind.date),
  SgFieldDef(key: 'owner', name: 'Person', kind: SgFieldKind.person),
  SgFieldDef(key: 'estimate', name: 'Estimate', kind: SgFieldKind.number),
  SgFieldDef(key: 'link', name: 'URL', kind: SgFieldKind.url),
  SgFieldDef(key: 'done', name: 'Done', kind: SgFieldKind.checkbox),
];

const List<String> kBoardKinds = [
  'notebook',
  'portfolio',
  'corkboard',
  'clipboard',
  'ledger',
  'desk',
  'binder',
  'slate',
];

const List<String> kHoldKinds = [
  'tray',
  'shelf',
  'table',
  'wall',
  'spread',
  'rack',
];

class SgHook {
  final String id;
  final String name;
  final String trigger; // fieldChange | listEnter | listLeave | cardCreate
  final String? fieldKey;
  final dynamic equalsValue;
  final String? listName;
  final String action; // setField | moveToList | addLabel
  final String? targetFieldKey;
  final dynamic targetValue;
  final String? targetListName;
  final String? labelName;
  bool enabled;

  SgHook({
    required this.id,
    required this.name,
    required this.trigger,
    this.fieldKey,
    this.equalsValue,
    this.listName,
    required this.action,
    this.targetFieldKey,
    this.targetValue,
    this.targetListName,
    this.labelName,
    this.enabled = true,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'trigger': trigger,
        if (fieldKey != null) 'fieldKey': fieldKey,
        if (equalsValue != null) 'equalsValue': equalsValue,
        if (listName != null) 'listName': listName,
        'action': action,
        if (targetFieldKey != null) 'targetFieldKey': targetFieldKey,
        if (targetValue != null) 'targetValue': targetValue,
        if (targetListName != null) 'targetListName': targetListName,
        if (labelName != null) 'labelName': labelName,
        'enabled': enabled,
      };

  factory SgHook.fromJson(Map<String, dynamic> j) => SgHook(
        id: '${j['id'] ?? ''}',
        name: '${j['name'] ?? 'Hook'}',
        trigger: '${j['trigger'] ?? 'fieldChange'}',
        fieldKey: j['fieldKey'] as String?,
        equalsValue: j['equalsValue'],
        listName: j['listName'] as String?,
        action: '${j['action'] ?? 'setField'}',
        targetFieldKey: j['targetFieldKey'] as String?,
        targetValue: j['targetValue'],
        targetListName: j['targetListName'] as String?,
        labelName: j['labelName'] as String?,
        enabled: j['enabled'] != false,
      );
}

class SgCard {
  final String id;
  String title;
  String subtitle;
  String score;
  bool done;
  String cardType; // task | project | reminder | memory | artifact
  Map<String, dynamic> fields;
  List<String> labels;
  double? x;
  double? y;

  SgCard({
    required this.id,
    required this.title,
    this.subtitle = '',
    this.score = '',
    this.done = false,
    this.cardType = 'task',
    Map<String, dynamic>? fields,
    List<String>? labels,
    this.x,
    this.y,
  })  : fields = fields ??
            {
              'status': done ? 'done' : 'open',
              'due': '',
              'owner': '',
              'estimate': '',
              'link': '',
              'done': done,
            },
        labels = labels ?? [];

  String get status => '${fields['status'] ?? (done ? 'done' : 'open')}';
  String get due => '${fields['due'] ?? ''}';
  String get owner => '${fields['owner'] ?? ''}';
  String get estimate => '${fields['estimate'] ?? ''}';
  String get link => '${fields['link'] ?? ''}';

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        if (subtitle.isNotEmpty) 'subtitle': subtitle,
        if (score.isNotEmpty) 'score': score,
        if (done) 'done': true,
        'cardType': cardType,
        'fields': fields,
        if (labels.isNotEmpty) 'labels': labels,
        if (x != null) 'x': x,
        if (y != null) 'y': y,
      };

  factory SgCard.fromJson(Map<String, dynamic> j) {
    final isDone = j['done'] == true || (j['fields'] is Map && j['fields']['done'] == true);
    final rawFields = j['fields'] is Map ? Map<String, dynamic>.from(j['fields'] as Map) : <String, dynamic>{};
    rawFields.putIfAbsent('status', () => isDone ? 'done' : 'open');
    rawFields.putIfAbsent('due', () => '${j['due'] ?? ''}');
    rawFields.putIfAbsent('owner', () => '');
    rawFields.putIfAbsent('estimate', () => '');
    rawFields.putIfAbsent('link', () => '');
    rawFields['done'] = isDone;
    return SgCard(
      id: j['id'] as String,
      title: (j['title'] as String?) ?? '',
      subtitle: (j['subtitle'] as String?) ?? '',
      score: (j['score'] as String?) ?? '',
      done: isDone,
      cardType: (j['cardType'] as String?) ?? 'task',
      fields: rawFields,
      labels: [for (final l in (j['labels'] as List? ?? const [])) '$l'],
      x: (j['x'] as num?)?.toDouble(),
      y: (j['y'] as num?)?.toDouble(),
    );
  }
}

class SmartGenStore extends ChangeNotifier {
  SmartGenStore._();
  static final SmartGenStore instance = SmartGenStore._();

  static const _key = 'smartgen_board_v2';
  static const _metaKey = 'smartgen_meta_v2';
  static const _dismissedKey = 'smartgen_dismissed_v2';
  final Map<String, List<SgCard>> _lists = {};
  final Set<String> _dismissedIds = {};
  final Map<int, String> _boardKinds = {
    0: 'notebook',
    1: 'portfolio',
    2: 'clipboard',
    3: 'corkboard',
    4: 'ledger',
  };
  String _holdKind = 'spread';
  bool _paperStackStyle = true;
  late List<SgHook> _hooks = _defaultHooks();
  bool _loaded = false;

  static List<SgHook> _defaultHooks() => [
        SgHook(
          id: 'hook_done_status',
          name: 'When Done is checked → Set Status = done',
          trigger: 'fieldChange',
          fieldKey: 'done',
          equalsValue: true,
          action: 'setField',
          targetFieldKey: 'status',
          targetValue: 'done',
        ),
        SgHook(
          id: 'hook_undone_status',
          name: 'When Done is unchecked → Set Status = open',
          trigger: 'fieldChange',
          fieldKey: 'done',
          equalsValue: false,
          action: 'setField',
          targetFieldKey: 'status',
          targetValue: 'open',
        ),
        SgHook(
          id: 'hook_high_list_doing',
          name: 'When moved to High → Set Status = doing & Label Urgent',
          trigger: 'listEnter',
          listName: 'High',
          action: 'setField',
          targetFieldKey: 'status',
          targetValue: 'doing',
          labelName: 'Urgent',
        ),
      ];

  String boardKindForTab(int tab) => _boardKinds[tab] ?? 'notebook';
  void setBoardKindForTab(int tab, String kind) {
    _boardKinds[tab] = kind;
    _save();
  }

  String get holdKind => _holdKind;
  void setHoldKind(String kind) {
    _holdKind = kind;
    _save();
  }

  bool get paperStackStyle => _paperStackStyle;
  void setPaperStackStyle(bool v) {
    _paperStackStyle = v;
    _save();
  }

  List<SgHook> get hooks => _hooks;
  void toggleHook(SgHook h) {
    h.enabled = !h.enabled;
    _save();
  }

  void addHook(SgHook h) {
    _hooks.add(h);
    _save();
  }

  static bool _isTrivialCard(String title) {
    final t = title.trim().toLowerCase();
    return t.isEmpty ||
        t == 'four' ||
        t == '4' ||
        t == 'ok then' ||
        t.startsWith('ok then') ||
        t.startsWith('i am glm') ||
        t.startsWith('nemotron 3 super by') ||
        t.startsWith('i am nemotron') ||
        t == 'who are you' ||
        t == 'what is 2+2';
  }

  List<SgCard> list(String name) => _lists.putIfAbsent(name, () => []);

  String? listOfCard(SgCard card) {
    for (final e in _lists.entries) {
      if (e.value.contains(card)) return e.key;
    }
    return null;
  }

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
      final rawMeta = prefs.getString(_metaKey);
      if (rawMeta != null) {
        final m = jsonDecode(rawMeta) as Map<String, dynamic>;
        if (m['holdKind'] is String) _holdKind = m['holdKind'] as String;
        if (m['paperStackStyle'] is bool) _paperStackStyle = m['paperStackStyle'] as bool;
        if (m['boardKinds'] is Map) {
          for (final e in (m['boardKinds'] as Map).entries) {
            final k = int.tryParse('${e.key}');
            if (k != null) _boardKinds[k] = '${e.value}';
          }
        }
        if (m['hooks'] is List) {
          _hooks = [
            for (final h in (m['hooks'] as List))
              if (h is Map) SgHook.fromJson(Map<String, dynamic>.from(h)),
          ];
        }
      }
      final dis = prefs.getStringList(_dismissedKey);
      if (dis != null) _dismissedIds.addAll(dis);
    } catch (e) {
      debugPrint('SmartGenStore: $e');
    }
    _ensureDefaultCoordinates();
    notifyListeners();
    await syncAutonomousCards();
  }

  void _ensureDefaultCoordinates() {
    var globalIdx = 0;
    final used = <String>{};
    for (final e in _lists.entries) {
      for (var i = 0; i < e.value.length; i++) {
        final c = e.value[i];
        final defX = 18.0 + (globalIdx % 3) * 242.0;
        final defY = 18.0 + (globalIdx ~/ 3) * 162.0;
        c.x ??= defX;
        c.y ??= defY;
        final posKey = '${c.x!.round()},${c.y!.round()}';
        if (!used.add(posKey)) {
          c.x = defX;
          c.y = defY;
          used.add('${c.x!.round()},${c.y!.round()}');
        }
        globalIdx++;
      }
    }
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
        final due = '${item['due'] ?? ''}'.trim();
        final cType = '${item['type'] ?? 'task'}'.trim();
        if (id.isEmpty || title.isEmpty || _isTrivialCard(title)) continue;
        if (existingIds.contains(id)) {
          for (final l in _lists.values) {
            for (final c in l) {
              if (c.id == id && (c.title != title || c.subtitle != content || c.score != score)) {
                c.title = title;
                c.subtitle = content;
                c.score = score;
                if (due.isNotEmpty) c.fields['due'] = due;
                added = true;
              }
            }
          }
          continue;
        }
        if (existingTitles.contains(title.toLowerCase())) continue;
        final isDone = item['done'] == true;
        final rawEst = score.contains('/') ? score.split('/').first.trim() : '';
        final cleanEst = RegExp(r'^\d+$').hasMatch(rawEst) ? rawEst : '';
        final card = SgCard(
          id: id,
          title: title,
          subtitle: content,
          score: score,
          done: isDone,
          cardType: cType,
          fields: {
            'status': isDone ? 'done' : (listName == 'High' ? 'doing' : 'open'),
            'due': due,
            'owner': '@consensus',
            'estimate': cleanEst,
            'link': '',
            'done': isDone,
          },
          labels: [
            if (listName == 'High') 'Consensus',
            if (cType.isNotEmpty) cType[0].toUpperCase() + cType.substring(1),
          ],
        );
        list(listName).add(card);
        existingIds.add(id);
        existingTitles.add(title.toLowerCase());
        added = true;
      }
      if (added) {
        _ensureDefaultCoordinates();
        await _save();
      }
    } catch (_) {}
  }

  void _runHooks(
    SgCard card, {
    required String trigger,
    String? fieldKey,
    String? listName,
    int depth = 0,
  }) {
    if (depth >= 3) return;
    for (final h in _hooks) {
      if (!h.enabled || h.trigger != trigger) continue;
      if (h.fieldKey != null && h.fieldKey != fieldKey) continue;
      if (h.equalsValue != null && card.fields[h.fieldKey] != h.equalsValue) continue;
      if (h.listName != null && h.listName != listName) continue;

      if (h.action == 'setField' && h.targetFieldKey != null) {
        card.fields[h.targetFieldKey!] = h.targetValue;
        if (h.targetFieldKey == 'done') {
          card.done = h.targetValue == true;
        } else if (h.targetFieldKey == 'status') {
          card.done = h.targetValue == 'done';
          card.fields['done'] = card.done;
        }
      }
      if (h.labelName != null && h.labelName!.isNotEmpty && !card.labels.contains(h.labelName)) {
        card.labels.add(h.labelName!);
      }
      if (h.action == 'moveToList' && h.targetListName != null) {
        move(card, h.targetListName!, null, runTrigger: false);
      }
    }
  }

  Future<void> _save() async {
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
        _key,
        jsonEncode({
          for (final e in _lists.entries) e.key: [for (final c in e.value) c.toJson()],
        }),
      );
      await prefs.setString(
        _metaKey,
        jsonEncode({
          'holdKind': _holdKind,
          'paperStackStyle': _paperStackStyle,
          'boardKinds': {for (final e in _boardKinds.entries) '${e.key}': e.value},
          'hooks': [for (final h in _hooks) h.toJson()],
        }),
      );
      await prefs.setStringList(_dismissedKey, _dismissedIds.toList());
    } catch (_) {}
  }

  SgCard add(String listName, String title, {String subtitle = '', Map<String, dynamic>? fields}) {
    final target = list(listName);
    final idx = target.length;
    final c = SgCard(
      id: DateTime.now().microsecondsSinceEpoch.toRadixString(36),
      title: title.trim(),
      subtitle: subtitle.trim(),
      fields: fields,
      x: 24.0 + (idx % 3) * 244.0,
      y: 24.0 + (idx ~/ 3) * 148.0,
    );
    target.add(c);
    _runHooks(c, trigger: 'cardCreate', listName: listName);
    _save();
    return c;
  }

  void update(
    SgCard c, {
    String? title,
    String? subtitle,
    bool? done,
    String? cardType,
    List<String>? labels,
  }) {
    if (title != null) c.title = title;
    if (subtitle != null) c.subtitle = subtitle;
    if (cardType != null) c.cardType = cardType;
    if (labels != null) c.labels = labels;
    if (done != null) {
      c.done = done;
      c.fields['done'] = done;
      _runHooks(c, trigger: 'fieldChange', fieldKey: 'done');
    }
    _save();
  }

  void setField(SgCard c, String key, dynamic value) {
    c.fields[key] = value;
    if (key == 'done') {
      c.done = value == true;
    } else if (key == 'status') {
      c.done = value == 'done';
      c.fields['done'] = c.done;
    }
    _runHooks(c, trigger: 'fieldChange', fieldKey: key);
    _save();
  }

  void setPosition(SgCard c, double x, double y, {bool persist = true}) {
    c.x = x.clamp(8.0, 1600.0);
    c.y = y.clamp(8.0, 1200.0);
    if (persist) {
      _save();
    } else {
      notifyListeners();
    }
  }

  void autoArrangeCanvas(List<String> lists) {
    var idx = 0;
    for (final l in lists) {
      for (final c in list(l)) {
        c.x = 20.0 + (idx % 3) * 244.0;
        c.y = 20.0 + (idx ~/ 3) * 148.0;
        idx++;
      }
    }
    _save();
  }

  void remove(SgCard c) {
    _dismissedIds.add(c.id);
    for (final l in _lists.values) {
      l.remove(c);
    }
    _save();
  }

  void move(SgCard c, String listName, int? index, {bool runTrigger = true}) {
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
    if (runTrigger && from != listName) {
      if (from != null) _runHooks(c, trigger: 'listLeave', listName: from);
      _runHooks(c, trigger: 'listEnter', listName: listName);
    }
    _save();
  }
}

void unawaited(Future<void> f) {}

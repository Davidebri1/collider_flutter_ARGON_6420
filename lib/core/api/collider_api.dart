// Collider API client. Made by Claude.
// Talks only to the local Collider server (tools/collider_server.py), which holds the keys.
import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform, TargetPlatform;
import 'package:material_ui/material_ui.dart';
import '../../models/model_def.dart';
import 'sse.dart';

/// Server values read as text whatever type they came in as, so one odd field never stops a whole answer.
String _s(Object? v) => v == null ? '' : '$v';

List<Map<String, String>> _msgs(Object? raw) => [
      for (final m in (raw is List ? raw : const []))
        if (m is Map) {'role': _s(m['role'] ?? 'user'), 'content': _s(m['content'])}
    ];

/// A reply as it is being written (Claude, 2026-10-19).
class ReplyDraft {
  final bool done;
  final String text;
  final String line;
  final List<Map<String, String>> messages;
  const ReplyDraft(this.done, this.text, this.line, this.messages);
}

enum AskMode { chat, internet, research, deep }

extension AskModeX on AskMode {
  String get wire => switch (this) {
        AskMode.chat => 'chat',
        AskMode.internet => 'internet',
        AskMode.research => 'research',
        AskMode.deep => 'deep',
      };
  String get label => switch (this) {
        AskMode.chat => 'Chat',
        AskMode.internet => 'Internet',
        AskMode.research => 'Research',
        AskMode.deep => 'Deep Research',
      };
  String get outcome => switch (this) {
        AskMode.chat => 'A direct answer',
        AskMode.internet => 'An answer from live web sources',
        AskMode.research => 'A research report with sources',
        AskMode.deep => 'An annotated research paper',
      };
  IconData get icon => switch (this) {
        AskMode.chat => Icons.chat_bubble_outline_rounded,
        AskMode.internet => Icons.public_rounded,
        AskMode.research => Icons.article_outlined,
        AskMode.deep => Icons.auto_stories_outlined,
      };
}

class ModelResult {
  final String status; // pending | done | error
  final String text;
  final String essence;
  final String? error;
  final String line; // the complete answer on one line that fits the ticker row
  final List<Map<String, String>> messages; // full multi-turn thread [{role, content}, ...]
  const ModelResult(this.status, this.text, this.essence, this.error, [this.line = '', this.messages = const []]);
  factory ModelResult.fromJson(Map<String, dynamic> j) => ModelResult(
        j['status'] == null ? 'pending' : _s(j['status']),
        _s(j['text']),
        _s(j['essence']),
        j['error'] == null ? null : _s(j['error']),
        _s(j['line']),
        _msgs(j['messages']),
      );
}

class ConsensusResult {
  final String status; // pending | done | unavailable
  final String summary;
  final String score;
  final List<String> dissent;
  final String need;
  final List<List<String>> groups;
  final Map<String, int> chains;
  final String tieBasis;
  final String line; // the winning group's line, word for word
  const ConsensusResult(this.status, this.summary, this.score, this.dissent, this.need,
      [this.groups = const [], this.chains = const {}, this.tieBasis = '', this.line = '']);
  factory ConsensusResult.fromJson(Map<String, dynamic>? j) {
    final dissent = j?['dissent'], groups = j?['groups'], chains = j?['chains'];
    return ConsensusResult(
      j?['status'] == null ? 'pending' : _s(j!['status']),
      _s(j?['summary']),
      _s(j?['score']),
      [for (final e in (dissent is List ? dissent : const [])) _s(e)],
      _s(j?['need']),
      [for (final g in (groups is List ? groups : const [])) if (g is List) [for (final m in g) _s(m)]],
      {
        for (final e in (chains is Map ? chains : const {}).entries)
          _s(e.key): e.value is num ? (e.value as num).toInt() : int.tryParse(_s(e.value)) ?? 0
      },
      _s(j?['tie_basis']),
      _s(j?['line']),
    );
  }
}

class JobState {
  final String id;
  final String prompt;
  final String mode;
  final String stage;
  final bool done;
  final Map<String, ModelResult> results;
  final ConsensusResult consensus;
  final List<Map<String, dynamic>> sources;
  final DateTime created;
  const JobState(this.id, this.prompt, this.mode, this.stage, this.done, this.results, this.consensus, this.sources, this.created);
  factory JobState.fromJson(Map<String, dynamic> j) {
    final results = j['results'], cons = j['consensus'], sources = j['sources'], created = j['created'];
    return JobState(
      _s(j['id']),
      _s(j['prompt']),
      j['mode'] == null ? 'chat' : _s(j['mode']),
      _s(j['stage']),
      (j['status'] ?? 'done') == 'done',
      {
        for (final e in (results is Map ? results : const {}).entries)
          if (e.value is Map) _s(e.key): ModelResult.fromJson(Map<String, dynamic>.from(e.value as Map))
      },
      ConsensusResult.fromJson(cons is Map ? Map<String, dynamic>.from(cons) : null),
      [for (final e in (sources is List ? sources : const [])) if (e is Map) Map<String, dynamic>.from(e)],
      DateTime.fromMillisecondsSinceEpoch(((created is num ? created : 0) * 1000).toInt()),
    );
  }
}

/// One making: pictures from words, a video from words, or a video from a picture.
class Creation {
  final String id;
  final String kind; // image | video | motion
  final String text;
  final String status; // making | done | failed
  final List<Map<String, dynamic>> media;
  final String? from; // for a video made from a picture: the making that holds the picture
  final String model; // "Provider:model" asked for, '' for the configuration's order
  final String label; // the model that made it, by name
  final List<String> references; // pictures it was made from, as "source/name" in Files
  final String aspect;
  final int count;
  const Creation(this.id, this.kind, this.text, this.status, this.media,
      [this.from, this.model = '', this.label = '', this.references = const [], this.aspect = '', this.count = 0]);
  factory Creation.fromJson(Map<String, dynamic> j) => Creation(
        '${j['id']}',
        '${j['kind'] ?? 'image'}',
        '${j['text'] ?? ''}',
        '${j['status'] ?? 'making'}',
        [for (final m in (j['media'] as List? ?? const [])) Map<String, dynamic>.from(m as Map)],
        j['from'] == null ? null : '${j['from']}',
        '${j['model'] ?? ''}',
        '${j['label'] ?? ''}',
        [for (final r in (j['references'] as List? ?? const [])) '$r'],
        '${j['aspect'] ?? ''}',
        (j['count'] as num?)?.toInt() ?? 0,
      );
  bool get making => status == 'making';
  bool get isVideo => kind != 'image';
}

/// One entry in Files. Sources: uploaded, generated, purchased, downloaded.
class ColliderFile {
  final String name;
  final String source;
  final int size; // bytes; 0 when unknown (bundled purchases)
  final DateTime modified;
  final String kind; // image | audio | video | pdf | text | file
  final String url; // server path, or a bundled asset path when [asset] is true
  final bool asset;
  final String model; // in Generated: the model (or Documents) that made it; '' when not known
  const ColliderFile(this.name, this.source, this.size, this.modified, this.kind, this.url, {this.asset = false, this.model = ''});
  factory ColliderFile.fromJson(Map<String, dynamic> j) => ColliderFile(
        j['name'] as String,
        j['source'] as String,
        (j['size'] as num?)?.toInt() ?? 0,
        DateTime.fromMillisecondsSinceEpoch((((j['modified'] as num?) ?? 0) * 1000).toInt()),
        j['kind'] as String? ?? 'file',
        j['url'] as String,
        model: '${j['model'] ?? ''}',
      );
}

class ColliderApi {
  ColliderApi._();
  static final ColliderApi instance = ColliderApi._();

  /// Where Collider's server is. On the web: the address the page came from. On a phone, tablet or desktop run from
  /// Flutter's runner: --dart-define=COLLIDER_SERVER=<address>, else the server on this computer at host 47801
  /// (seen as 10.0.2.2 from inside Android's emulator). (Claude, 2026-10-23)
  static final String base = () {
    const named = String.fromEnvironment('COLLIDER_SERVER');
    if (named.isNotEmpty) return named;
    if (kIsWeb) return Uri.base.origin;
    return defaultTargetPlatform == TargetPlatform.android ? 'http://10.0.2.2:47801' : 'http://127.0.0.1:47801';
  }();
  final Dio _dio = Dio(BaseOptions(connectTimeout: const Duration(seconds: 8), receiveTimeout: const Duration(seconds: 180)));

  String get _base => base;
  bool online = false;
  bool webSearch = false;
  int nvidiaKeys = 0;

  /// In-memory caches so opening Files or History panes never triggers a blank flash or redundant fetch.
  Map<String, List<ColliderFile>>? cachedFiles;
  List<JobState>? cachedHistory;
  final Map<String, String> _fileTextCache = {};
  final Set<String> _linesResolvedCache = {};

  static Color _hex(String h) => Color(int.parse('FF${h.replaceAll('#', '')}', radix: 16));

  /// Loads the live roster from the server into [ModelRoster]. Returns true when connected.
  Future<bool> loadRoster() async {
    try {
      final r = await _dio.get('$_base/api/models');
      final list = (r.data['models'] as List).cast<Map>();
      webSearch = r.data['search'] == true;
      nvidiaKeys = (r.data['keys'] as num?)?.toInt() ?? 0;
      // The picture models (Claude, 2026-10-21): the Image category, from the providers that have keys.
      var pictures = const <Map>[];
      try {
        pictures = ((await _dio.get('$_base/api/imagine')).data['models'] as List? ?? const []).cast<Map>();
      } catch (_) {}
      ModelRoster.setLive([
        for (final m in pictures)
          ModelDef(
            id: '${m['id']}',
            label: '${m['label']}',
            short: '${m['label']}'.split(' ').map((w) => w.isEmpty ? '' : w[0]).join(),
            desc: '${m['provider']}',
            tier: ModelTier.free,
            categories: const [ModelCategory.image],
            providerColor: const Color(0xFF8E8E93),
            isMedia: true,
          ),
        for (final m in list)
          ModelDef(
            id: m['id'] as String,
            label: m['label'] as String,
            short: m['short'] as String,
            desc: m['provider'] as String,
            tier: ModelTier.free,
            categories: const [ModelCategory.general],
            providerColor: _hex(m['color'] as String),
          ),
      ]);
      online = true;
    } catch (_) {
      online = false;
    }
    return online;
  }

  /// Files the server holds: uploaded, generated, downloaded (purchases are bundled with the app).
  Future<Map<String, List<ColliderFile>>> files({bool forceRefresh = false}) async {
    if (!forceRefresh && cachedFiles != null) return cachedFiles!;
    try {
      final r = await _dio.get('$_base/api/files');
      cachedFiles = {
        for (final e in (r.data as Map).entries)
          '${e.key}': [for (final f in e.value as List) ColliderFile.fromJson(Map<String, dynamic>.from(f as Map))],
      };
      return cachedFiles!;
    } catch (_) {
      return cachedFiles ?? const {};
    }
  }

  /// The preview picture of a file in Files (the server makes and keeps it).
  String thumbUrl(ColliderFile f) =>
      '$_base/api/files/thumb?source=${Uri.encodeQueryComponent(f.source)}&name=${Uri.encodeQueryComponent(f.name)}&v=${f.modified.millisecondsSinceEpoch}';

  /// Full address of a file for viewing.
  /// Discover Market (Claude, 2026-10-20): what has been made through fal, newest first.
  Future<List<Creation>> creations() async {
    try {
      final r = await _dio.get('$_base/api/imagine');
      return [for (final j in (r.data['items'] as List? ?? const [])) Creation.fromJson(Map<String, dynamic>.from(j as Map))];
    } catch (_) {
      return const [];
    }
  }

  /// Makes pictures (kind image) or a video (video) from words, or a video from a made picture (motion, from its id).
  Future<void> make(String text, String kind,
      {String? from, String? replace, String? model, List<String>? references, String? aspect, int? count}) async {
    try {
      await _dio.post('$_base/api/imagine', data: {
        'text': text,
        'kind': kind,
        if (from != null) 'from': from,
        if (replace != null) 'replace': replace,
        if (model != null) 'model': model,
        if (references != null && references.isNotEmpty) 'references': references,
        if (aspect != null) 'aspect': aspect,
        if (count != null) 'count': count,
      });
      cachedFiles = null;
    } catch (_) {}
  }

  /// Windows' own app picker for [f], on the computer that serves the app (Claude, 2026-10-21).
  Future<void> openWith(ColliderFile f) async {
    try {
      await _dio.post('$_base/api/files/openwith', data: {'source': f.source, 'name': f.name});
    } catch (_) {}
  }

  /// The file's bytes, for handing it to the phone's share sheet.
  Future<List<int>?> fileBytes(ColliderFile f) async {
    try {
      final r = await _dio.get<List<int>>(fileUrl(f), options: Options(responseType: ResponseType.bytes));
      return r.data;
    } catch (_) {
      return null;
    }
  }

  /// The phone link and its QR picture (data URL); empty away from the computer that serves the app.
  Future<(String, String)> phone() async {
    try {
      final r = await _dio.get('$_base/api/phone');
      return ('${r.data['link'] ?? ''}', '${r.data['qr'] ?? ''}');
    } catch (_) {
      return ('', '');
    }
  }

  String fileUrl(ColliderFile f) => f.asset ? '$_base/assets/${f.url}' : '$_base${f.url}';

  Future<String> fileText(ColliderFile f) async {
    final u = fileUrl(f);
    if (_fileTextCache.containsKey(u)) return _fileTextCache[u]!;
    final r = await _dio.get<String>(u, options: Options(responseType: ResponseType.plain));
    final txt = r.data ?? '';
    _fileTextCache[u] = txt;
    return txt;
  }

  /// Stores an upload in Files and returns the name it was saved under.
  Future<String?> uploadFile(String name, List<int> bytes) async {
    try {
      final r = await _dio.post('$_base/api/files/upload', data: {'name': name, 'b64': base64Encode(bytes)});
      cachedFiles = null;
      return r.data['name'] as String?;
    } catch (_) {
      return null;
    }
  }

  /// Voice chat (Claude, 2026-10-20): recorded speech in, its words out.
  Future<String?> transcribe(List<int> bytes, String mime) async {
    try {
      final r = await _dio.post('$_base/api/transcribe', data: {'b64': base64Encode(bytes), 'mime': mime});
      final t = r.data['text'];
      return t is String ? t.trim() : null;
    } catch (_) {
      return null;
    }
  }

  /// Saves model output as a file in Files > Generated.
  Future<String?> saveGenerated(String name, String text, {String model = ''}) async {
    try {
      final r = await _dio.post('$_base/api/files/generated', data: {'name': name, 'text': text, 'model': model});
      cachedFiles = null;
      return r.data['name'] as String?;
    } catch (_) {
      return null;
    }
  }

  /// Saves whatever is at [url] in Files > Downloaded.
  Future<String?> download(String url) async {
    try {
      final r = await _dio.post('$_base/api/files/download', data: {'url': url});
      cachedFiles = null;
      return r.data['name'] as String?;
    } catch (_) {
      return null;
    }
  }

  Future<String> ask({
    required String prompt,
    required List<String> models,
    required AskMode mode,
    required bool autosave,
    required bool incognito,
    List<String> attachments = const [],
    int line = 28,
    String? sessionId,
  }) async {
    final r = await _dio.post('$_base/api/ask', data: {
      'line': line,
      'prompt': prompt,
      'attachments': attachments,
      'models': models,
      'mode': mode.wire,
      'autosave': autosave,
      'incognito': incognito,
      if (sessionId != null && sessionId.isNotEmpty) 'session_id': sessionId,
    });
    return r.data['id'] as String;
  }

  /// A job as it happens, answers drafting word by word: the server's event stream, or polling where there is none.
  Stream<JobState> watch(String id) async* {
    try {
      await for (final data in sseEvents('$_base/api/stream/$id')) {
        final s = JobState.fromJson(Map<String, dynamic>.from(jsonDecode(data) as Map));
        yield s;
        if (s.done) return;
      }
    } catch (_) {}
    while (true) {
      final r = await _dio.get('$_base/api/job/$id');
      final s = JobState.fromJson(Map<String, dynamic>.from(r.data as Map));
      yield s;
      if (s.done) return;
      await Future.delayed(const Duration(milliseconds: 250));
    }
  }

  /// A reply as the model writes it; the last one has done set. Throws when the model gives no answer.
  Stream<ReplyDraft> replyStream({
    required String model,
    required List<Map<String, String>> messages,
    required AskMode mode,
    List<String> attachments = const [],
    int line = 28,
    String? jobId,
  }) async* {
    final r = await _dio.post('$_base/api/reply/start', data: {
      'model': model,
      'messages': messages,
      'mode': mode.wire,
      'attachments': attachments,
      'line': line,
      if (jobId != null && jobId.isNotEmpty) 'job_id': jobId,
    });
    final id = _s(r.data['id']);
    ReplyDraft read(Map j) {
      if (j['status'] == 'error') throw StateError(_s(j['error']));
      return ReplyDraft(j['status'] == 'done', _s(j['text']), _s(j['line']), _msgs(j['messages']));
    }

    try {
      await for (final data in sseEvents('$_base/api/stream/r/$id')) {
        final d = read(jsonDecode(data) as Map);
        yield d;
        if (d.done) return;
      }
    } on StateError catch (e) {
      if (e.message != 'stream closed' && e.message != 'not found') rethrow;
    } on UnsupportedError catch (_) {}
    while (true) {
      final d = read((await _dio.get('$_base/api/reply/$id')).data as Map);
      yield d;
      if (d.done) return;
      await Future.delayed(const Duration(milliseconds: 250));
    }
  }

  Future<({String text, String line, List<Map<String, String>> messages})> reply({
    required String model,
    required List<Map<String, String>> messages,
    required AskMode mode,
    List<String> attachments = const [],
    int line = 28,
    String? jobId,
  }) async {
    final r = await _dio.post('$_base/api/reply', data: {
      'model': model,
      'messages': messages,
      'mode': mode.wire,
      'attachments': attachments,
      'line': line,
      if (jobId != null && jobId.isNotEmpty) 'job_id': jobId,
    });
    final rawMsgs = r.data['messages'] as List?;
    final parsedMsgs = rawMsgs != null
        ? [
            for (final m in rawMsgs)
              if (m is Map)
                {
                  'role': '${m['role'] ?? 'user'}',
                  'content': '${m['content'] ?? ''}',
                }
          ]
        : const <Map<String, String>>[];
    return (
      text: r.data['text'] as String? ?? '',
      line: r.data['line'] as String? ?? '',
      messages: parsedMsgs,
    );
  }

  /// One-line forms for a saved conversation that has none, or has them for a wider row.
  Future<JobState?> lines(String id, int line) async {
    final key = '$id:$line';
    if (_linesResolvedCache.contains(key)) return null;
    try {
      final r = await _dio.post('$_base/api/lines', data: {'id': id, 'line': line});
      final m = Map<String, dynamic>.from(r.data as Map);
      if (m['error'] != null) return null;
      _linesResolvedCache.add(key);
      return JobState.fromJson({...m, 'status': 'done'});
    } catch (_) {
      return null;
    }
  }

  Future<List<JobState>> history({bool forceRefresh = false}) async {
    if (!forceRefresh && cachedHistory != null) return cachedHistory!;
    try {
      final r = await _dio.get('$_base/api/history');
      cachedHistory = [
        for (final s in (r.data['sessions'] as List)) JobState.fromJson({...Map<String, dynamic>.from(s as Map), 'status': 'done'}),
      ];
      return cachedHistory!;
    } catch (_) {
      return cachedHistory ?? const [];
    }
  }

  Future<List<Map<String, dynamic>>> smartgenCards() async {
    try {
      final r = await _dio.get('$_base/api/smartgen');
      final list = (r.data['cards'] as List?) ?? const [];
      return [for (final c in list) Map<String, dynamic>.from(c as Map)];
    } catch (_) {
      return const [];
    }
  }
}

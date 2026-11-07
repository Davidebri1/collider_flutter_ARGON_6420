import 'dart:io' show File, Platform;

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

/// A live-model reply from the Genie's provider chain.
class GenieAiReply {
  final String text;
  final String provider;
  final String model;

  const GenieAiReply({
    required this.text,
    required this.provider,
    required this.model,
  });

  /// Compact form for the header chip, e.g. "glm-5.3".
  String get chip {
    final short = model.split('/').last;
    return '$provider $short';
  }
}

/// Live-AI chain for Smart Genie.
///
/// Priority order (first healthy responder wins):
///   1. MiniMax M3 — Command Code (MiniMaxAI/MiniMax-M3) then OpenCode Go
///      (minimax-m3). Strict: when a router has no MiniMax M3, the chain
///      moves on rather than substituting another model.
///   2. NVIDIA NIM (one key, sequential fallback):
///      z-ai/glm-5.3 → z-ai/glm-5.3-flash → moonshotai/kimi-k3
///      → nvidia/nemotron-3-ultra-550b-a55b → nvidia/nemotron-nano-3-30b-a3b
///
/// Key resolution (in order):
///   1. --dart-define: SMART_GENIE_COMMAND_CODE_KEY / SMART_GENIE_OPENCODE_KEY
///      / SMART_GENIE_NVIDIA_KEY
///   2. The machine's keys files (never bundled into the binary):
///      - 00_Config_and_Secrets\keys.json   (structured, NVIDIA NIM entry)
///      - Documents\API KEYS.txt            (user_… / oc_sk_… / nvapi-… tokens)
///      Override the location with SMART_GENIE_KEYS_FILE.
///
/// Honesty rule: this client only reports LIVE when a provider actually
/// answered. Any error falls through the chain and the caller falls back
/// to the local interpreter.
class GenieAiClient {
  static const _cmdKeyDefine =
      String.fromEnvironment('SMART_GENIE_COMMAND_CODE_KEY');
  static const _ocKeyDefine = String.fromEnvironment('SMART_GENIE_OPENCODE_KEY');
  static const _nvKeyDefine = String.fromEnvironment('SMART_GENIE_NVIDIA_KEY');
  static const _keysFileDefine = String.fromEnvironment('SMART_GENIE_KEYS_FILE');

  static const _cmdBaseUrl = 'https://api.commandcode.ai/provider/v1';
  static const _ocBaseUrl = 'https://opencode.ai/zen/v1';
  static const _nvBaseUrl = 'https://integrate.api.nvidia.com/v1';

  /// NVIDIA fallback chain — all served by the same nvapi key.
  /// Verified live 2026-10-09: glm-5.3 / glm-5.3-flash / kimi-k3 answer;
  /// nemotron-3-ultra-550b intermittently 503s; the nano id is listed but
  /// 404s on chat, so nemotron-3.5-lightning closes the chain as the
  /// working Nemotron floor.
  static const nvidiaChain = [
    'z-ai/glm-5.3',
    'z-ai/glm-5.3-flash',
    'moonshotai/kimi-k3',
    'nvidia/nemotron-3-ultra-550b-a55b',
    'nvidia/nemotron-nano-3-30b-a3b',
    'nvidia/nemotron-3.5-lightning-30b-a3b',
  ];

  static const _systemPrompt = 'You are Smart Genie, the in-app assistant for '
      "Collider's Smart Gen workspace (kanban boards, smart cards, canvases, "
      'typed fields, and hooks). Be concise, concrete, and honest. You can '
      'suggest edits to cards/boards but never claim to have applied them — '
      'the local interpreter handles that.';

  final Dio _dio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 12),
      receiveTimeout: const Duration(seconds: 60),
    ),
  );

  bool _keysLoaded = false;
  String? _cmdKey;
  String? _ocKey;
  String? _nvKey;
  final Map<String, String?> _discoveredModel = {};

  /// True when widget tests run this code — never hit the network from tests.
  bool get _inTest =>
      !kIsWeb && Platform.environment.containsKey('FLUTTER_TEST');

  bool get hasAnyKey {
    _loadKeys();
    return _cmdKey != null || _ocKey != null || _nvKey != null;
  }

  void _loadKeys() {
    if (_keysLoaded) return;
    _keysLoaded = true;

    _cmdKey = _nonEmpty(_cmdKeyDefine);
    _ocKey = _nonEmpty(_ocKeyDefine);
    _nvKey = _nonEmpty(_nvKeyDefine);

    final blob = _readKeysBlob();
    if (blob == null) return;

    _cmdKey ??= _firstMatch(blob, RegExp(r'user_[A-Za-z0-9]{20,}'));
    _ocKey ??= _firstMatch(blob, RegExp(r'oc_sk_[A-Za-z0-9_]+'));
    _nvKey ??= _firstMatch(blob, RegExp(r'nvapi-[A-Za-z0-9_\-]+'));
    _ocKey ??= _firstMatch(blob, RegExp(r'"provider"\s*:\s*"OpenCode Zen"'
        r'[\s\S]{0,200}?"key"\s*:\s*"([^"]+)"'));
  }

  String? _readKeysBlob() {
    if (kIsWeb || _inTest) return null;
    try {
      final paths = <String>[
        if (_keysFileDefine.isNotEmpty) _keysFileDefine,
        r'C:\Users\D\Documents\00_Config_and_Secrets\keys.json',
        r'C:\Users\D\Documents\API KEYS.txt',
        r'C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt',
      ];
      final sb = StringBuffer();
      for (final p in paths) {
        final f = File(p);
        if (f.existsSync()) {
          try {
            sb.writeln(f.readAsStringSync());
          } catch (_) {}
        }
      }
      return sb.isEmpty ? null : sb.toString();
    } catch (_) {
      return null;
    }
  }

  String? _nonEmpty(String s) => s.trim().isEmpty ? null : s.trim();

  String? _firstMatch(String blob, RegExp re) {
    final m = re.firstMatch(blob);
    if (m == null) return null;
    final v = m.groupCount > 0 ? m.group(1) : m.group(0);
    return _nonEmpty(v ?? '');
  }

  /// Ask the provider for a usable model id (cached for the session).
  /// With [strict], a provider is skipped entirely when none of [prefer]
  /// matches — no generic first-model fallback.
  Future<String?> _discoverModel(String base, String key, List<String> prefer,
      {String? fixed, bool strict = false}) async {
    if (fixed != null) return fixed;
    final cacheKey = '$base|$prefer|$strict';
    if (_discoveredModel.containsKey(cacheKey)) {
      return _discoveredModel[cacheKey];
    }
    String? picked;
    try {
      final r = await _dio.get(
        '$base/models',
        options: Options(headers: _authHeaders(key)),
      );
      final data = r.data;
      final ids = <String>[];
      final raw = data is Map ? (data['data'] ?? data['models']) : null;
      if (raw is List) {
        for (final m in raw) {
          final id = m is Map ? m['id'] ?? m['name'] : m;
          if (id is String && id.isNotEmpty) ids.add(id);
        }
      }
      String? pick;
      for (final want in prefer) {
        final hits =
            ids.where((id) => id.toLowerCase().contains(want.toLowerCase()));
        if (hits.isNotEmpty) {
          pick = hits.first;
          break;
        }
      }
      pick ??= strict ? null : (ids.isNotEmpty ? ids.first : null);
      picked = pick;
    } catch (_) {
      picked = null;
    }
    _discoveredModel[cacheKey] = picked;
    return picked;
  }

  Map<String, String> _authHeaders(String key) => {
        'Authorization': 'Bearer $key',
        'x-api-key': key,
        'Content-Type': 'application/json',
      };

  /// Try the chain in order. Returns the first live reply, or null when
  /// every provider is unavailable (caller falls back to local mode).
  ///
  /// [history] is the conversation so far as {'role','content'} maps.
  Future<GenieAiReply?> chat(
    String userText, {
    List<Map<String, String>> history = const [],
  }) async {
    _loadKeys();
    if (_inTest) return null;

    final messages = [
      {'role': 'system', 'content': _systemPrompt},
      ...history,
      {'role': 'user', 'content': userText},
    ];

    final candidates = <_Candidate>[
      if (_cmdKey != null)
        _Candidate('Command Code', _cmdBaseUrl, _cmdKey!, const [
          'minimax-m3',
          'minimax',
        ], strict: true),
      if (_ocKey != null)
        _Candidate('OpenCode', _ocBaseUrl, _ocKey!, const [
          'minimax-m3',
          'minimax',
        ], strict: true),
      if (_nvKey != null)
        ...nvidiaChain.map(
          (m) => _Candidate('NVIDIA', _nvBaseUrl, _nvKey!, const [],
              fixedModel: m),
        ),
    ];

    for (final c in candidates) {
      final model = await _discoverModel(c.base, c.key, c.prefer,
          fixed: c.fixedModel, strict: c.strict);
      if (model == null) continue;
      final text = await _postChat(c.base, c.key, model, messages);
      if (text != null && text.trim().isNotEmpty) {
        return GenieAiReply(text: text.trim(), provider: c.name, model: model);
      }
    }
    return null;
  }

  Future<String?> _postChat(
    String base,
    String key,
    String model,
    List<Map<String, String>> messages,
  ) async {
    try {
      final r = await _dio.post(
        '$base/chat/completions',
        options: Options(headers: _authHeaders(key)),
        data: {
          'model': model,
          'messages': messages,
          'temperature': 0.4,
          'max_tokens': 2048,
          'stream': false,
        },
      );
      final data = r.data;
      if (data is! Map) return null;
      final choices = data['choices'];
      if (choices is! List || choices.isEmpty) return null;
      final first = choices.first;
      if (first is! Map) return null;
      final message = first['message'];
      var content = message is Map ? message['content'] : null;
      if (content is List) {
        // Anthropic-style content parts: [{type:'text', text:…}, …]
        final sb = StringBuffer();
        for (final part in content) {
          if (part is Map && part['text'] is String) {
            sb.write(part['text']);
          }
        }
        content = sb.toString();
      }
      if (content is String && content.trim().isNotEmpty) return content;
      final text = first['text'];
      if (text is String && text.trim().isNotEmpty) return text;
      return null;
    } catch (_) {
      return null;
    }
  }
}

class _Candidate {
  final String name;
  final String base;
  final String key;
  final List<String> prefer;
  final String? fixedModel;
  final bool strict;

  const _Candidate(this.name, this.base, this.key, this.prefer,
      {this.fixedModel, this.strict = false});
}

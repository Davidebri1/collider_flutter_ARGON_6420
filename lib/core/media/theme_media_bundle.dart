import 'dart:async';
import 'dart:typed_data';
import 'dart:ui' show ImmutableBuffer;

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Asset bundle that resolves absolute http(s) keys and caches resolved [ByteData] in memory.
/// Eliminates redundant network fetches when covers, reflections, and galleries reference the same theme asset.
class ThemeMediaAssetBundle extends AssetBundle {
  ThemeMediaAssetBundle(this._fallback);

  static final ThemeMediaAssetBundle instance = ThemeMediaAssetBundle(rootBundle);

  final AssetBundle _fallback;
  final Dio _dio = Dio(BaseOptions(
    responseType: ResponseType.bytes,
    connectTimeout: const Duration(seconds: 15),
    receiveTimeout: const Duration(seconds: 30),
  ));

  // Resolved ByteData cache + in-flight requests so all 46+ themes stay cached in memory.
  final Map<String, ByteData> _resolved = {};
  final Map<String, Future<ByteData>> _inflight = {};
  static const int _maxCached = 256;

  static bool isNetworkKey(String key) => key.startsWith('https://') || key.startsWith('http://');

  /// Synchronous lookup if already loaded.
  ByteData? getSynchronously(String key) => _resolved[key];

  @override
  Future<ByteData> load(String key) {
    final hit = _resolved[key];
    if (hit != null) return SynchronousFuture<ByteData>(hit);
    final pending = _inflight[key];
    if (pending != null) return pending;

    final Future<ByteData> f = isNetworkKey(key) ? _fetch(key) : _fallback.load(key);
    _inflight[key] = f;
    f.then((data) {
      _inflight.remove(key);
      if (data.lengthInBytes > 0) {
        if (_resolved.length >= _maxCached) {
          _resolved.remove(_resolved.keys.first);
        }
        _resolved[key] = data;
      }
    }).catchError((Object _) {
      _inflight.remove(key);
    });
    return f;
  }

  Future<ByteData> _fetch(String url) async {
    final res = await _dio.get<List<int>>(url);
    final data = res.data;
    if (res.statusCode != 200 || data == null || data.isEmpty) {
      throw StateError('ThemeMediaAssetBundle: ${res.statusCode} for $url');
    }
    final bytes = data is Uint8List ? data : Uint8List.fromList(data);
    return ByteData.sublistView(bytes);
  }

  @override
  Future<ImmutableBuffer> loadBuffer(String key) async {
    if (!isNetworkKey(key) && !_resolved.containsKey(key)) return _fallback.loadBuffer(key);
    final d = await load(key);
    return ImmutableBuffer.fromUint8List(d.buffer.asUint8List(d.offsetInBytes, d.lengthInBytes));
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) =>
      isNetworkKey(key) ? super.loadString(key, cache: cache) : _fallback.loadString(key, cache: cache);

  @override
  Future<T> loadStructuredData<T>(String key, Future<T> Function(String value) parser) =>
      _fallback.loadStructuredData<T>(key, parser);

  @override
  Future<T> loadStructuredBinaryData<T>(String key, FutureOr<T> Function(ByteData data) parser) =>
      _fallback.loadStructuredBinaryData<T>(key, parser);

  @override
  void evict(String key) {
    _resolved.remove(key);
    _inflight.remove(key);
    _fallback.evict(key);
  }

  @override
  void clear() {
    _resolved.clear();
    _inflight.clear();
    _fallback.clear();
  }
}

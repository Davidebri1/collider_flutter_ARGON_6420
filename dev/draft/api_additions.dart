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
  Future<void> make(String text, String kind, {String? from}) async {
    try {
      await _dio.post('$_base/api/imagine', data: {'text': text, 'kind': kind, if (from != null) 'from': from});
      cachedFiles = null;
    } catch (_) {}
  }

/// One making: pictures from words, a video from words, or a video from a picture.
class Creation {
  final String id;
  final String kind; // image | video | motion
  final String text;
  final String status; // making | done | failed
  final List<Map<String, dynamic>> media;
  final String? from; // for a video made from a picture: the making that holds the picture
  const Creation(this.id, this.kind, this.text, this.status, this.media, [this.from]);
  factory Creation.fromJson(Map<String, dynamic> j) => Creation(
        '${j['id']}',
        '${j['kind'] ?? 'image'}',
        '${j['text'] ?? ''}',
        '${j['status'] ?? 'making'}',
        [for (final m in (j['media'] as List? ?? const [])) Map<String, dynamic>.from(m as Map)],
        j['from'] == null ? null : '${j['from']}',
      );
  bool get making => status == 'making';
  bool get isVideo => kind != 'image';
}

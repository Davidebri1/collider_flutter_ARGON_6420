import 'model_def.dart';

/// Generates a concise, scannable Auto-Named Conversation Title (3-6 words)
/// from a user prompt and optional model summary. Used as the header in
/// History line items, History preview headers, and Conversation Expanded Views.
String autoNameConversationTitle(String prompt, [String summary = '']) {
  final raw = prompt.trim();
  if (raw.isEmpty) return 'New Conversation';
  final lower = raw.toLowerCase().replaceAll(RegExp(r'[^a-z0-9\s]'), '').trim();
  if (const {'hello', 'hi', 'hey', 'hola', 'greetings', 'yo', 'sup', 'test'}.contains(lower)) {
    final s = summary.replaceAll(RegExp(r'[#*_`>\[\]\n]'), ' ').trim();
    if (s.toLowerCase().contains('assist') || s.toLowerCase().contains('help')) {
      return 'Greeting & Capabilities Overview';
    }
    return 'Welcome & Assistant Introduction';
  }
  var cleaned = raw
      .replaceAll(RegExp(r'[\r\n]+'), ' ')
      .replaceFirst(
        RegExp(
          r'^(please\s+|can\s+you\s+|could\s+you\s+|would\s+you\s+|help\s+me\s+|explain\s+|tell\s+me\s+about\s+|what\s+is\s+|what\s+are\s+|how\s+do\s+i\s+|how\s+to\s+|write\s+a\s+|create\s+a\s+)',
          caseSensitive: false,
        ),
        '',
      )
      .replaceAll(RegExp(r'[?.!,;:]+$'), '')
      .trim();
  if (cleaned.isEmpty) cleaned = raw;
  final words = cleaned.split(RegExp(r'\s+'));
  final selected = words.length > 6 ? words.sublist(0, 6) : words;
  const smallWords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'vs'};
  final titled = <String>[];
  for (var i = 0; i < selected.length; i++) {
    final w = selected[i];
    if (w.isEmpty) continue;
    final lw = w.toLowerCase();
    if (i > 0 && smallWords.contains(lw)) {
      titled.add(lw);
    } else if (w.length > 1 && w == w.toUpperCase()) {
      titled.add(w);
    } else {
      titled.add(w[0].toUpperCase() + w.substring(1));
    }
  }
  final out = titled.join(' ');
  return out.length > 44 ? '${out.substring(0, 42).trim()}…' : out;
}

class TickerMessage {
  final String id;
  final String sender; // 'user' or 'model'
  final String text;
  final DateTime timestamp;
  final List<String>? fileAttachments;

  const TickerMessage({
    required this.id,
    required this.sender,
    required this.text,
    required this.timestamp,
    this.fileAttachments,
  });
}

class TickerItem {
  final ModelDef modelDef;
  final String relativeTime;
  final String summary;
  final String conversationTitle;
  final List<TickerMessage> conversation;
  final bool isIsolated;
  final List<String>? mediaUrls;
  final bool isStreaming;

  const TickerItem({
    required this.modelDef,
    required this.relativeTime,
    required this.summary,
    required this.conversation,
    this.conversationTitle = '',
    this.isIsolated = false,
    this.mediaUrls,
    this.isStreaming = false,
  });

  String get displayTitle {
    if (conversationTitle.trim().isNotEmpty) return conversationTitle;
    final firstUser = conversation.where((m) => m.sender == 'user').firstOrNull;
    if (firstUser != null && firstUser.text.trim().isNotEmpty) {
      return autoNameConversationTitle(firstUser.text, summary);
    }
    return autoNameConversationTitle(summary);
  }

  TickerItem copyWith({
    ModelDef? modelDef,
    String? relativeTime,
    String? summary,
    String? conversationTitle,
    List<TickerMessage>? conversation,
    bool? isIsolated,
    List<String>? mediaUrls,
    bool? isStreaming,
  }) {
    return TickerItem(
      modelDef: modelDef ?? this.modelDef,
      relativeTime: relativeTime ?? this.relativeTime,
      summary: summary ?? this.summary,
      conversationTitle: conversationTitle ?? this.conversationTitle,
      conversation: conversation ?? this.conversation,
      isIsolated: isIsolated ?? this.isIsolated,
      mediaUrls: mediaUrls ?? this.mediaUrls,
      isStreaming: isStreaming ?? this.isStreaming,
    );
  }
}

class ConversationHistorySession {
  final String id;
  final String title;
  final String? targetModelId; // If specific to a single model
  final String relativeTime;
  final DateTime timestamp;
  final String summary;
  final List<String> modelIds;
  final List<TickerMessage> messages;

  const ConversationHistorySession({
    required this.id,
    required this.title,
    this.targetModelId,
    required this.relativeTime,
    required this.timestamp,
    required this.summary,
    this.modelIds = const [],
    required this.messages,
  });
}

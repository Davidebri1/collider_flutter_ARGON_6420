// Light Markdown renderer for model answers. Made by Claude.
// Headings, bold, bullets and numbered lists, rendered as calm text (no raw symbols).
import 'package:material_ui/material_ui.dart';
import 'vision_tokens.dart';

class MdText extends StatelessWidget {
  final String text;
  final TextStyle? style;

  /// When given, a citation like [3] or [2, 5] becomes a small mark that opens that source (Claude, 2026-10-20).
  final void Function(int n)? onCite;
  const MdText(this.text, {super.key, this.style, this.onCite});

  static final _bold = RegExp(r'\*\*(.+?)\*\*|__(.+?)__|(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])');
  static final _cite = RegExp(r'\[(\d+(?:\s*[,–-]\s*\d+)*)\]');

  List<InlineSpan> _inline(String s, TextStyle base) {
    if (onCite == null) return _styled(s, base);
    final spans = <InlineSpan>[];
    var i = 0;
    for (final m in _cite.allMatches(s)) {
      if (m.start > i) spans.addAll(_styled(s.substring(i, m.start), base));
      for (final n in RegExp(r'\d+').allMatches(m.group(1)!)) {
        final k = int.parse(n.group(0)!);
        spans.add(WidgetSpan(
          alignment: PlaceholderAlignment.middle,
          child: GestureDetector(
            onTap: () => onCite!(k),
            child: MouseRegion(
              cursor: SystemMouseCursors.click,
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 1.5),
                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                decoration: BoxDecoration(color: const Color(0x33FFFFFF), borderRadius: BorderRadius.circular(VRadius.full)),
                child: Text('$k', style: base.copyWith(fontSize: (base.fontSize ?? 13) * 0.72, height: 1.2, fontWeight: FontWeight.w600)),
              ),
            ),
          ),
        ));
      }
      i = m.end;
    }
    if (i < s.length) spans.addAll(_styled(s.substring(i), base));
    return spans;
  }

  List<InlineSpan> _styled(String s, TextStyle base) {
    final spans = <InlineSpan>[];
    var i = 0;
    for (final m in _bold.allMatches(s)) {
      if (m.start > i) spans.add(TextSpan(text: s.substring(i, m.start)));
      if (m.group(3) != null) {
        spans.add(TextSpan(text: m.group(3), style: base.copyWith(fontStyle: FontStyle.italic)));
      } else {
        spans.add(TextSpan(text: m.group(1) ?? m.group(2), style: base.copyWith(fontWeight: FontWeight.w700)));
      }
      i = m.end;
    }
    if (i < s.length) spans.add(TextSpan(text: s.substring(i)));
    return spans;
  }

  @override
  Widget build(BuildContext context) {
    final base = style ?? VType.callout(weight: FontWeight.w400).copyWith(height: 1.45);
    final lines = text.replaceAll('\r', '').split('\n');
    final children = <Widget>[];
    for (var raw in lines) {
      final line = raw.trimRight();
      if (line.trim().isEmpty) {
        children.add(const SizedBox(height: 6));
        continue;
      }
      if (RegExp(r'^\s*(---+|\*\*\*+)\s*$').hasMatch(line)) continue;
      final h = RegExp(r'^(#{1,6})\s+(.*)$').firstMatch(line);
      if (h != null) {
        final level = h.group(1)!.length;
        children.add(Padding(
          padding: const EdgeInsets.only(top: 6, bottom: 2),
          child: Text.rich(TextSpan(children: _inline(h.group(2)!.replaceAll('*', ''), base)),
              style: base.copyWith(fontWeight: FontWeight.w700, fontSize: (base.fontSize ?? 13) + (level <= 2 ? 3 : 1))),
        ));
        continue;
      }
      final b = RegExp(r'^(\s*)[-*•]\s+(.*)$').firstMatch(line);
      final n = RegExp(r'^(\s*)(\d+)[.)]\s+(.*)$').firstMatch(line);
      if (b != null || n != null) {
        final indent = ((b ?? n)!.group(1)!.length / 2).clamp(0, 3) * 12.0;
        final marker = b != null ? '•' : '${n!.group(2)}.';
        final body = b != null ? b.group(2)! : n!.group(3)!;
        children.add(Padding(
          padding: EdgeInsets.only(left: indent, top: 1, bottom: 1),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            SizedBox(width: 18, child: Text(marker, style: base.copyWith(color: VColors.textSecondary))),
            Expanded(child: Text.rich(TextSpan(children: _inline(body, base)), style: base)),
          ]),
        ));
        continue;
      }
      if (line.startsWith('|')) {
        // Tables become readable rows.
        if (RegExp(r'^\|[\s:|-]+\|$').hasMatch(line)) continue;
        final cells = line.split('|').map((c) => c.trim()).where((c) => c.isNotEmpty).join('  ·  ');
        children.add(Text.rich(TextSpan(children: _inline(cells, base)), style: base));
        continue;
      }
      children.add(Text.rich(TextSpan(children: _inline(line, base)), style: base));
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: children);
  }
}

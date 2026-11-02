// The media chat's generations: what the picture models made from what was asked, newest first. Made by Claude
// (2026-10-21). David, 21 Oct: model categories need "their config surfaces ... options and toolbars and settings and
// source and reference and queues and generations pane(perhaps collapsible expandable)/Files preview window".
//  - toolbar: the shape (9:16, 1:1, 16:9) and how many pictures a request makes;
//  - the queue: a request being made shows its tiles breathing until the pictures arrive; one that failed retries on a tap;
//  - the pane: the latest request; expanded, every request, scrolling;
//  - a picture opens large (PictureViewer): keep it, share it, or remix it (it becomes the next request's reference);
//  - everything made is also in Files > Generated, under the model that made it.
import 'dart:async';

import 'package:material_ui/material_ui.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../core/api/collider_api.dart';
import '../../core/vision/vision_kit.dart';
import 'picture_viewer.dart';

const kAspects = ['9:16', '1:1', '16:9'];
const kCounts = [1, 2, 4];

double aspectOf(String a) {
  final p = a.split(':');
  return p.length == 2 ? (double.tryParse(p[0]) ?? 9) / (double.tryParse(p[1]) ?? 16) : 9 / 16;
}

class GenerationsPane extends StatefulWidget {
  final String aspect;
  final int count;
  final ValueChanged<String> onAspect;
  final ValueChanged<int> onCount;
  final bool expanded;
  final VoidCallback onToggleExpanded;
  final ValueChanged<String> onRemix; // the picture's place in Files ("generated/<name>")
  final int refresh; // changes when a request was just sent
  const GenerationsPane({
    super.key,
    required this.aspect,
    required this.count,
    required this.onAspect,
    required this.onCount,
    required this.expanded,
    required this.onToggleExpanded,
    required this.onRemix,
    required this.refresh,
  });

  @override
  State<GenerationsPane> createState() => _GenerationsPaneState();
}

class _GenerationsPaneState extends State<GenerationsPane> {
  static const _savedKey = 'market_saved_v1'; // the same keeping as Discover's My Gallery
  List<Creation> _made = const [];
  Timer? _poll;
  final Set<String> _saved = {};

  @override
  void initState() {
    super.initState();
    _refresh();
    SharedPreferences.getInstance().then((p) {
      if (mounted) setState(() => _saved.addAll(p.getStringList(_savedKey) ?? const []));
    });
  }

  @override
  void didUpdateWidget(GenerationsPane old) {
    super.didUpdateWidget(old);
    if (old.refresh != widget.refresh) _refresh();
  }

  @override
  void dispose() {
    _poll?.cancel();
    super.dispose();
  }

  Future<void> _refresh() async {
    final list = await ColliderApi.instance.creations();
    if (!mounted) return;
    setState(() => _made = [for (final c in list) if (c.kind == 'image') c]);
    _poll?.cancel();
    if (_made.any((c) => c.making)) _poll = Timer(const Duration(seconds: 2), _refresh);
  }

  Future<void> _save(ViewedPicture p) async {
    setState(() => _saved.contains(p.id) ? _saved.remove(p.id) : _saved.add(p.id));
    (await SharedPreferences.getInstance()).setStringList(_savedKey, _saved.toList()..sort());
  }

  void _open(Creation c, int i) {
    final api = ColliderApi.instance;
    final pics = [
      for (final m in c.media)
        ViewedPicture(
          id: 'c:${m['name']}',
          url: api.fileUrl(ColliderFile('${m['name']}', 'generated', 0, DateTime.now(), 'image', '${m['url']}')),
          aspect: (m['width'] is num && m['height'] is num && (m['height'] as num) > 0) ? (m['width'] as num) / (m['height'] as num) : aspectOf(widget.aspect),
          fileRef: 'generated/${m['name']}',
        ),
    ];
    showGeneralDialog(
      context: context,
      barrierColor: Colors.transparent,
      pageBuilder: (ctx, _, __) => PictureViewer(
        pictures: pics,
        start: i,
        saved: _saved,
        onSave: _save,
        onRemix: (p) {
          Navigator.of(ctx).pop();
          widget.onRemix(p.fileRef!);
        },
        onClose: () => Navigator.of(ctx).pop(),
      ),
    );
  }

  Widget _toolbar() {
    Widget chip(String label, bool on, VoidCallback onTap) => Padding(
          padding: const EdgeInsets.only(right: 4),
          child: VChip(label: label, selected: on, onTap: onTap),
        );
    return SizedBox(
      height: 44,
      // the chips slide sideways when the pane is narrow (a phone); the expand button always keeps its place
      child: Row(children: [
        Expanded(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            physics: const BouncingScrollPhysics(),
            child: Row(children: [
              for (final a in kAspects) chip(a, widget.aspect == a, () => widget.onAspect(a)),
              const SizedBox(width: 12),
              for (final n in kCounts) chip('$n', widget.count == n, () => widget.onCount(n)),
            ]),
          ),
        ),
        const SizedBox(width: 4),
        VCircleButton(
          icon: widget.expanded ? Icons.unfold_less_rounded : Icons.unfold_more_rounded,
          size: 44,
          onTap: widget.onToggleExpanded,
        ),
      ]),
    );
  }

  /// One request: its words, then its pictures. Kept small, they sit in one row across the pane; expanded, two to a row,
  /// as Grok's results (Claude, 2026-10-21).
  Widget _group(Creation c, double width) {
    final api = ColliderApi.instance;
    final n = c.media.isNotEmpty ? c.media.length : (c.count > 0 ? c.count : widget.count);
    final a = aspectOf(c.aspect.isEmpty ? widget.aspect : c.aspect);
    final cols = widget.expanded ? (n == 1 ? 1 : 2) : n;
    var tileW = (width - 4 * (cols - 1)) / cols;
    var tileH = tileW / a;
    final most = widget.expanded ? 420.0 : 160.0;
    if (tileH > most) {
      tileH = most;
      tileW = most * a;
    }
    Widget tile(int i) {
      Widget body;
      if (c.status == 'failed') {
        body = const ColoredBox(color: Color(0x22FFFFFF), child: Center(child: Icon(Icons.refresh_rounded, color: Colors.white70)));
      } else if (c.making || i >= c.media.length) {
        body = const BreathingTile();
      } else {
        final m = c.media[i];
        final f = ColliderFile('${m['name']}', 'generated', 0, DateTime.now(), 'image', '${m['url']}');
        body = Image.network(api.fileUrl(f), fit: BoxFit.cover, filterQuality: FilterQuality.high, gaplessPlayback: true,
            errorBuilder: (_, __, ___) => const ColoredBox(color: Color(0xFF111318)));
      }
      return VPress(
        onTap: () {
          if (c.status == 'failed') {
            ColliderApi.instance
                .make(c.text, c.kind, replace: c.id, model: c.model.isEmpty ? null : c.model, references: c.references,
                    aspect: c.aspect.isEmpty ? null : c.aspect, count: c.count > 0 ? c.count : null)
                .then((_) => _refresh());
          } else if (i < c.media.length) {
            _open(c, i);
          }
        },
        child: ClipRRect(borderRadius: BorderRadius.circular(8), child: SizedBox(height: tileH, width: tileW, child: body)),
      );
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: VSpace.sm),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(
          c.label.isEmpty ? c.text : '${c.text}  ·  ${c.label}',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w500),
        ),
        const SizedBox(height: 6),
        Wrap(spacing: 4, runSpacing: 4, children: [for (int i = 0; i < n; i++) tile(i)]),
      ]),
    );
  }

  @override
  Widget build(BuildContext context) {
    final groups = widget.expanded ? _made : _made.take(1).toList();
    return Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      _toolbar(),
      if (groups.isNotEmpty) ...[
        const SizedBox(height: 6),
        Flexible(
          child: EdgeFade(
            focus: FadeFocus.top,
            child: LayoutBuilder(
              builder: (_, box) => ListView(
                shrinkWrap: true,
                physics: const BouncingScrollPhysics(),
                padding: EdgeInsets.zero,
                children: [for (final c in groups) _group(c, box.maxWidth)],
              ),
            ),
          ),
        ),
      ],
    ]);
  }
}

/// While something is being made: the tile's light rises and falls slowly, as a held breath, nothing flashing.
class BreathingTile extends StatefulWidget {
  const BreathingTile({super.key});
  @override
  State<BreathingTile> createState() => _BreathingTileState();
}

class _BreathingTileState extends State<BreathingTile> with SingleTickerProviderStateMixin {
  late final AnimationController _a = AnimationController(vsync: this, duration: const Duration(milliseconds: 2600))..repeat(reverse: true);
  @override
  void dispose() {
    _a.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _a,
        builder: (_, __) {
          final t = Curves.easeInOut.transform(_a.value);
          return DecoratedBox(
            decoration: BoxDecoration(
              gradient: RadialGradient(
                center: const Alignment(0, -0.2),
                radius: 0.9,
                colors: [Colors.white.withValues(alpha: 0.10 + 0.08 * t), Colors.white.withValues(alpha: 0.03)],
              ),
            ),
          );
        },
      );
}

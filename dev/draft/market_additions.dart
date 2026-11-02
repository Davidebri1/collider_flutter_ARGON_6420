// ======================================================================================================
// Making pictures and videos in Discover Market, as in Grok's Imagine (Claude, 2026-10-20).
// David: "discover market should be wired to Fal ... whatever functionality imagine market has, discover market has."
// The bar at the foot of the pane: picture or video, the words, and the button that makes them. What is made appears
// at the head of the feed while it is being made, then as itself; a picture opens large and can be set in motion.
// No words of Grok's are used, and none on the bar at all.
// ======================================================================================================

/// The bar that makes: a picture or a video, then the words.
class _MakeBar extends StatefulWidget {
  final Future<void> Function(String text, bool video) onMake;
  const _MakeBar({required this.onMake});
  @override
  State<_MakeBar> createState() => _MakeBarState();
}

class _MakeBarState extends State<_MakeBar> {
  final _text = TextEditingController();
  bool _video = false;
  bool _sending = false;

  Future<void> _go() async {
    final t = _text.text.trim();
    if (t.isEmpty || _sending) return;
    setState(() => _sending = true);
    try {
      await widget.onMake(t, _video);
      _text.clear();
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return VGlass(
      material: VMaterial.elevated,
      radius: 28,
      padding: const EdgeInsets.fromLTRB(6, 4, 6, 4),
      child: Row(children: [
        VCircleButton(icon: Icons.image_rounded, size: 34, selected: !_video, onTap: () => setState(() => _video = false)),
        VCircleButton(icon: Icons.movie_rounded, size: 34, selected: _video, onTap: () => setState(() => _video = true)),
        const SizedBox(width: 6),
        Expanded(
          child: VRecessed(
            radius: 18,
            padding: const EdgeInsets.symmetric(horizontal: 14),
            child: TextField(
              controller: _text,
              minLines: 1,
              maxLines: 4,
              cursorColor: VColors.textPrimary,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _go(),
              style: VType.callout(weight: FontWeight.w500),
              decoration: const InputDecoration(border: InputBorder.none, isDense: true, contentPadding: EdgeInsets.symmetric(vertical: 13)),
            ),
          ),
        ),
        const SizedBox(width: 6),
        VCircleButton(
          icon: _sending ? Icons.more_horiz_rounded : Icons.arrow_upward_rounded,
          size: 34,
          selected: true,
          onTap: _sending ? null : _go,
        ),
      ]),
    );
  }
}

/// A making in the feed: a soft light breathing while it is made, then the picture or the video's first frame.
class _CreationTile extends StatelessWidget {
  final Creation c;
  final Map<String, dynamic>? m;
  const _CreationTile(this.c, this.m);

  @override
  Widget build(BuildContext context) {
    if (c.making || m == null) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(4),
        child: c.status == 'failed'
            ? const ColoredBox(color: Color(0x22FFFFFF), child: Center(child: Icon(Icons.refresh_rounded, color: Colors.white70)))
            : const _Breathing(),
      );
    }
    final api = ColliderApi.instance;
    final file = ColliderFile('${m!['name']}', 'generated', 0, DateTime.now(), m!['kind'] == 'video' ? 'video' : 'image', '${m!['url']}');
    return ClipRRect(
      borderRadius: BorderRadius.circular(4),
      child: Stack(fit: StackFit.expand, children: [
        Image.network(m!['kind'] == 'video' ? api.thumbUrl(file) : api.fileUrl(file), fit: BoxFit.cover, filterQuality: FilterQuality.high,
            errorBuilder: (_, __, ___) => const ColoredBox(color: Color(0xFF111318))),
        if (m!['kind'] == 'video')
          Positioned(
            right: 8,
            bottom: 8,
            child: Container(
              width: 26,
              height: 26,
              decoration: const BoxDecoration(shape: BoxShape.circle, color: Color(0x66000000)),
              child: const Icon(Icons.play_arrow_rounded, size: 16, color: Colors.white),
            ),
          ),
      ]),
    );
  }
}

/// While something is being made: the tile's light rises and falls slowly, as a held breath, nothing flashing.
class _Breathing extends StatefulWidget {
  const _Breathing();
  @override
  State<_Breathing> createState() => _BreathingState();
}

class _BreathingState extends State<_Breathing> with SingleTickerProviderStateMixin {
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

/// A picture opened large: set it in motion, keep it in My Gallery, or copy where it is.
class _PictureWindow extends StatelessWidget {
  final Creation c;
  final Map<String, dynamic> m;
  final bool saved;
  final VoidCallback onClose;
  final VoidCallback onMotion;
  final VoidCallback onSave;
  const _PictureWindow({required this.c, required this.m, required this.saved, required this.onClose, required this.onMotion, required this.onSave});

  @override
  Widget build(BuildContext context) {
    final api = ColliderApi.instance;
    final file = ColliderFile('${m['name']}', 'generated', 0, DateTime.now(), 'image', '${m['url']}');
    return Stack(children: [
      GestureDetector(behavior: HitTestBehavior.opaque, onTap: onClose, child: const ColoredBox(color: Color(0xCC06080E), child: SizedBox.expand())),
      Center(
        child: LayoutBuilder(builder: (context, box) {
          return Column(mainAxisSize: MainAxisSize.min, children: [
            ConstrainedBox(
              constraints: BoxConstraints(maxWidth: box.maxWidth * 0.86, maxHeight: box.maxHeight * 0.78),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(VRadius.xl),
                child: Image.network(api.fileUrl(file), fit: BoxFit.contain, filterQuality: FilterQuality.high),
              ),
            ),
            const SizedBox(height: VSpace.sm),
            VGlass(
              material: VMaterial.elevated,
              radius: VRadius.full,
              padding: const EdgeInsets.symmetric(horizontal: 6),
              child: Row(mainAxisSize: MainAxisSize.min, children: [
                VCircleButton(icon: Icons.close_rounded, size: 34, onTap: onClose),
                VCircleButton(icon: Icons.movie_rounded, size: 34, onTap: onMotion),
                VCircleButton(icon: saved ? Icons.favorite_rounded : Icons.favorite_border_rounded, size: 34, onTap: onSave),
                VCircleButton(
                  icon: Icons.ios_share_rounded,
                  size: 34,
                  onTap: () => Clipboard.setData(ClipboardData(text: api.fileUrl(file))),
                ),
              ]),
            ),
          ]);
        }),
      ),
    ]);
  }
}

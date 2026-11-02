// A picture opened large. Made by Claude (2026-10-21), on the layout of Grok Imagine's picture view (Mobbin, Grok iOS):
// the picture at its own shape, rounded; actions under it; a sideways swipe to the next.
// David, 21 Oct: Discover "needs to extract the cinematic effect. Through dimming the background", and Remix hands the
// picture to the media chat as its reference ("Grok merely transfers you to the chat window when you hit remix").
// Claude, 2026-10-23: the app's one detail view (DetailView): Remix, Keep and Save, then Send, Open and Close, each with
// its name under it, no tray. Pinch or double-tap to look closer (Flutter's InteractiveViewer); a zoomed picture pans
// instead of turning the page.
import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';

import '../../core/platform/open_url.dart';
import '../../core/vision/vision_kit.dart';

class ViewedPicture {
  final String id; // what My Gallery keeps it by
  final String url; // full size
  final double aspect; // width / height, as far as it is known
  final String? fileRef; // "source/name" in Files, when it is there
  final Widget Function(BoxFit fit)? builder; // a picture the app draws itself (a wallpaper's poster)
  const ViewedPicture({required this.id, required this.url, this.aspect = 9 / 16, this.fileRef, this.builder});
}

class PictureViewer extends StatefulWidget {
  final List<ViewedPicture> pictures;
  final int start;
  final Set<String> saved;
  final ValueChanged<ViewedPicture>? onSave;
  final ValueChanged<ViewedPicture>? onRemix;
  final ValueChanged<ViewedPicture>? onFiles;
  final VoidCallback onClose;
  const PictureViewer({
    super.key,
    required this.pictures,
    required this.start,
    this.saved = const {},
    this.onSave,
    this.onRemix,
    required this.onClose,
    this.onFiles,
  });

  @override
  State<PictureViewer> createState() => _PictureViewerState();
}

class _PictureViewerState extends State<PictureViewer> {
  late final PageController _pages = PageController(initialPage: widget.start);
  late int _i = widget.start;
  final TransformationController _zoom = TransformationController();
  bool _zoomed = false;
  TapDownDetails? _tap;

  @override
  void initState() {
    super.initState();
    _zoom.addListener(() {
      final z = _zoom.value.getMaxScaleOnAxis() > 1.01;
      if (z != _zoomed) setState(() => _zoomed = z);
    });
  }

  @override
  void dispose() {
    _pages.dispose();
    _zoom.dispose();
    super.dispose();
  }

  Future<void> _send(ViewedPicture p) async {
    if (canShareText && await shareText(p.url)) return;
    await Clipboard.setData(ClipboardData(text: p.url));
  }

  void _toggleZoom() {
    if (_zoomed) {
      _zoom.value = Matrix4.identity();
      return;
    }
    final at = _tap?.localPosition ?? Offset.zero;
    _zoom.value = Matrix4.identity()
      ..translateByDouble(-at.dx * 1.5, -at.dy * 1.5, 0, 1)
      ..scaleByDouble(2.5, 2.5, 1, 1);
  }

  Widget _picture(ViewedPicture p) {
    final img = p.builder != null
        ? p.builder!(BoxFit.contain)
        : Image.network(p.url, fit: BoxFit.contain, filterQuality: FilterQuality.high, gaplessPlayback: true,
            loadingBuilder: (_, child, progress) => progress == null ? child : const ColoredBox(color: Color(0xFF0B0B0D)),
            errorBuilder: (_, __, ___) => const ColoredBox(color: Color(0xFF0B0B0D)));
    return DetailRaised(child: AspectRatio(aspectRatio: p.aspect, child: img));
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.pictures[_i];
    final kept = widget.saved.contains(p.id);
    return DetailView(
      onClose: widget.onClose,
      onSend: () => _send(p),
      onOpen: () => openUrl(p.url),
      media: true,
      actions: [
        if (widget.onRemix != null) DetailAction(Icons.auto_fix_high_rounded, 'Remix', () => widget.onRemix!(p)),
        if (widget.onSave != null)
          DetailAction(kept ? Icons.favorite_rounded : Icons.favorite_border_rounded, 'Keep', () {
            widget.onSave!(p);
            setState(() {});
          }, tint: kept ? const Color(0xFFE5484D) : null),
        if (widget.onFiles != null) DetailAction(Icons.download_rounded, 'Save', () => widget.onFiles!(p)),
      ],
      child: SizedBox(
        height: math.min(DetailView.zoneWidth(context, media: true) / p.aspect, DetailView.zoneHeight(context)),
        child: PageView.builder(
        controller: _pages,
        physics: _zoomed ? const NeverScrollableScrollPhysics() : const PageScrollPhysics(),
        itemCount: widget.pictures.length,
        onPageChanged: (i) => setState(() {
          _i = i;
          _zoom.value = Matrix4.identity();
        }),
        itemBuilder: (_, i) => Center(
          child: i == _i
              ? GestureDetector(
                  onDoubleTapDown: (d) => _tap = d,
                  onDoubleTap: _toggleZoom,
                  child: InteractiveViewer(
                    transformationController: _zoom,
                    minScale: 1,
                    maxScale: 5,
                    clipBehavior: Clip.none,
                    child: _picture(widget.pictures[i]),
                  ),
                )
              : _picture(widget.pictures[i]),
        ),
      ),
      ),
    );
  }
}

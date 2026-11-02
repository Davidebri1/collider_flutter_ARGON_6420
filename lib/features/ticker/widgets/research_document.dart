import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';

import '../../../core/api/collider_api.dart';
import '../../../core/platform/open_url.dart';
import '../../../core/vision/vision_kit.dart';
import '../../../models/ticker_item.dart';

/// An answer that drew on the web, opened as a document. Made by Claude (2026-10-20) after Claude's own research
/// artifact: the report in a window that rises into place, each citation a small mark that opens its source, the
/// sources listed under the report by the numbers the report cites, and Copy, Save and Share under the window.
/// Research and Deep Research reports are also kept in Files > Generated when they finish.
class ResearchDocument extends StatelessWidget {
  final TickerMessage message;
  final String modelName;
  final List<Map<String, dynamic>> sources;
  final void Function(int index) onOpenSource; // 0-based
  final VoidCallback onClose;

  const ResearchDocument({
    super.key,
    required this.message,
    required this.modelName,
    required this.sources,
    required this.onOpenSource,
    required this.onClose,
  });

  static String _host(String url) => Uri.tryParse(url)?.host.replaceFirst('www.', '') ?? url;

  void _toast(BuildContext context, String text) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      duration: const Duration(seconds: 1),
      behavior: SnackBarBehavior.floating,
      backgroundColor: VColors.glassDark,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(VRadius.full)),
      margin: EdgeInsets.fromLTRB(MediaQuery.sizeOf(context).width * 0.3, 0, MediaQuery.sizeOf(context).width * 0.3, 100),
      elevation: 0,
      content: Text(text, textAlign: TextAlign.center, style: VType.callout()),
    ));
  }

  String get _document {
    final listed = [for (var i = 0; i < sources.length; i++) '${i + 1}. ${sources[i]['title'] ?? ''} ${sources[i]['url'] ?? ''}'];
    return listed.isEmpty ? message.text : '${message.text.trim()}\n\nSources\n${listed.join('\n')}';
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    // A reading window: most of a phone, about 60% of a wider screen, never wider than a comfortable line of text.
    final width = (size.width < 600 ? size.width - 32 : (size.width * 0.6).clamp(0.0, 720.0)).toDouble();
    final body = VType.body().copyWith(fontSize: 11, height: 1.55);
    final meta = VType.caption(color: VColors.textSecondary);
    void cite(int n) {
      if (n >= 1 && n <= sources.length) onOpenSource(n - 1);
    }

    return Stack(
      fit: StackFit.expand,
      children: [
        VScrim(onTap: onClose),
        SafeArea(
          child: Center(
            child: TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: 1),
              duration: const Duration(milliseconds: 460),
              curve: const Cubic(0.2, 0.9, 0.25, 1),
              builder: (_, t, child) => Opacity(
                opacity: t,
                child: Transform.translate(offset: Offset(0, 24 * (1 - t)), child: Transform.scale(scale: 0.96 + 0.04 * t, child: child)),
              ),
              child: Padding(
                padding: const EdgeInsets.only(bottom: 92, top: VSpace.lg),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Flexible(
                      child: SizedBox(
                        width: width,
                        child: VGlass(
                          radius: VRadius.xl,
                          padding: const EdgeInsets.fromLTRB(VSpace.lg, VSpace.md, VSpace.sm, VSpace.sm),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Row(children: [
                                Expanded(child: Text(modelName, maxLines: 1, overflow: TextOverflow.fade, softWrap: false, style: meta)),
                                VCircleButton(icon: Icons.close_rounded, size: 30, tooltip: 'Close', onTap: onClose),
                              ]),
                              Flexible(
                                child: VFadeScroll(
                                  fade: 22,
                                  padding: const EdgeInsets.fromLTRB(0, VSpace.xs, VSpace.sm, VSpace.md),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      MdText(message.text, style: body, onCite: cite),
                                      if (sources.isNotEmpty) ...[
                                        const SizedBox(height: VSpace.lg),
                                        Text('Sources', style: body.copyWith(fontWeight: FontWeight.w700, fontSize: 16)),
                                        const SizedBox(height: VSpace.xs),
                                        for (var i = 0; i < sources.length; i++)
                                          VPress(
                                            onTap: () => onOpenSource(i),
                                            child: Padding(
                                              padding: const EdgeInsets.symmetric(vertical: 5),
                                              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                                SizedBox(width: 26, child: Text('${i + 1}', style: meta)),
                                                Expanded(
                                                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                                    Text('${sources[i]['title'] ?? ''}', style: body.copyWith(fontSize: 11, height: 1.35)),
                                                    Text(_host('${sources[i]['url'] ?? ''}'), style: meta),
                                                  ]),
                                                ),
                                              ]),
                                            ),
                                          ),
                                      ],
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: VSpace.xs),
                    VOrnament(
                      padding: const EdgeInsets.all(4),
                      child: Row(mainAxisSize: MainAxisSize.min, children: [
                        VCircleButton(
                          icon: Icons.copy_rounded,
                          tooltip: 'Copy',
                          onTap: () {
                            Clipboard.setData(ClipboardData(text: _document));
                            _toast(context, 'Copied');
                          },
                        ),
                        const SizedBox(width: 4),
                        VCircleButton(
                          icon: Icons.bookmark_border_rounded,
                          tooltip: 'Save',
                          onTap: () async {
                            final words = message.text.replaceAll(RegExp(r'[#*_`>\[\]\n]'), ' ').trim().split(RegExp(r'\s+')).take(6).join(' ');
                            final name = await ColliderApi.instance.saveGenerated('$modelName - $words.md', _document, model: modelName);
                            if (context.mounted) _toast(context, name == null ? 'Not saved' : 'Saved to Files');
                          },
                        ),
                        if (canShareText) ...[
                          const SizedBox(width: 4),
                          VCircleButton(icon: Icons.ios_share_rounded, tooltip: 'Share', onTap: () => shareText(_document)),
                        ],
                      ]),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

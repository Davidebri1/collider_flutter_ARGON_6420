import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';
import '../../../models/ticker_item.dart';
import '../../../core/vision/vision_kit.dart';
import '../../../core/api/collider_api.dart';
import '../../../core/platform/open_url.dart';

class MessageZoomOverlay extends StatelessWidget {
  final TickerMessage message;
  final String modelName;
  final String? conversationTitle;
  final Color providerColor;
  final VoidCallback onClose;
  final VoidCallback? onOpen;

  const MessageZoomOverlay({
    super.key,
    required this.message,
    required this.modelName,
    this.conversationTitle,
    required this.providerColor,
    required this.onClose,
    this.onOpen,
  });

  void _toast(BuildContext context, String text) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      duration: const Duration(seconds: 1),
      behavior: SnackBarBehavior.floating,
      backgroundColor: VColors.glassDark,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(VRadius.full)),
      margin: EdgeInsets.fromLTRB(MediaQuery.sizeOf(context).width * 0.24, 0, MediaQuery.sizeOf(context).width * 0.24, 100),
      elevation: 0,
      content: Text(text, textAlign: TextAlign.center, style: VType.callout()),
    ));
  }

  void _copy(BuildContext context) {
    Clipboard.setData(ClipboardData(text: message.text));
    _toast(context, 'Copied');
  }

  Future<void> _save(BuildContext context) async {
    final words = message.text.replaceAll(RegExp(r'[#*_`>\[\]\n]'), ' ').trim().split(RegExp(r'\s+')).take(6).join(' ');
    final name = await ColliderApi.instance.saveGenerated('$modelName - $words.md', message.text, model: modelName);
    if (context.mounted) _toast(context, name == null ? 'Not saved' : 'Saved to Files');
  }

  Future<void> _send(BuildContext context) async {
    if (!await shareText(message.text) && context.mounted) _copy(context);
  }

  @override
  Widget build(BuildContext context) {
    return DetailView(
      onClose: onClose,
      onSend: () => _send(context),
      onOpen: onOpen,
      actions: [
        DetailAction(Icons.copy_rounded, 'Copy', () => _copy(context)),
        DetailAction(Icons.bookmark_border_rounded, 'Save', () => _save(context)),
      ],
      child: ConstrainedBox(
        constraints: BoxConstraints(maxHeight: DetailView.zoneHeight(context)),
        child: VFadeScroll(
          fade: 30,
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 26),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      autoNameConversationTitle(conversationTitle ?? message.text),
                      style: VType.headline().copyWith(fontSize: 14, color: Colors.white),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      modelName,
                      style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w500),
                    ),
                  ],
                ),
              ),
              MdText(
                message.text,
                style: VType.body().copyWith(fontSize: 11, height: 1.5, shadows: const [Shadow(color: Color(0x99000000), blurRadius: 14)]),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

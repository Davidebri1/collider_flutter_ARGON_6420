// Documents — Novel rich-text & Word/PDF/Markdown editor inside a spatial glass window.
import 'package:material_ui/material_ui.dart';
import '../../core/vision/vision_kit.dart';
import 'html_page.dart';

class DocumentsScreen extends StatelessWidget {
  final VoidCallback onClose;
  final String? fileUrl;
  final String? fileName;

  const DocumentsScreen({super.key, required this.onClose, this.fileUrl, this.fileName});

  String get _src {
    const page = 'assets/assets/html/claude_documents.html';
    if (fileUrl == null) return page;
    return '$page?file=${Uri.encodeQueryComponent(fileUrl!)}&name=${Uri.encodeQueryComponent(fileName ?? '')}';
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, box) {
      final compact = box.maxWidth < 768;
      final w = compact ? box.maxWidth - 20 : (box.maxWidth - 80).clamp(420.0, 1100.0);
      final h = box.maxHeight - (compact ? 20 : 44);
      return Center(
        child: TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: 1),
          duration: const Duration(milliseconds: 260),
          curve: Curves.easeOutCubic,
          builder: (_, t, child) => Opacity(opacity: t, child: Transform.scale(scale: 0.96 + 0.04 * t, child: child)),
          child: SizedBox(
            width: w,
            height: h,
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                Positioned.fill(
                  child: VGlass(
                    material: VMaterial.work,
                    radius: 24,
                    child: ClipRRect(borderRadius: BorderRadius.circular(24), child: HtmlPage(src: _src)),
                  ),
                ),
                Positioned(
                  top: -12,
                  right: -12,
                  child: VCircleButton(icon: Icons.close_rounded, size: 32, tooltip: 'Close Documents', floating: true, onTap: onClose),
                ),
              ],
            ),
          ),
        ),
      );
    });
  }
}

// Browser page surface (non-web placeholder). Made by Claude.
import 'package:flutter/widgets.dart';

class WebFrame extends StatelessWidget {
  final String url;
  final int reload;
  final double zoom;
  final void Function(String url, String title)? onNavigated;
  final void Function(String name)? onDownloaded;
  const WebFrame({super.key, required this.url, this.reload = 0, this.zoom = 1, this.onNavigated, this.onDownloaded});
  @override
  Widget build(BuildContext context) => Center(child: Text(url));
}

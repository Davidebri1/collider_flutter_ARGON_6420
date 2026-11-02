// Made by Claude (2026-10-20). A page of the app's own HTML shown in a pane (web).
// The page comes from the app itself, so it may use the app's server (to open and save files) and the clipboard.
import 'dart:ui_web' as ui_web;
import 'package:flutter/widgets.dart';
import 'package:web/web.dart' as web;

int _pages = 0;

class HtmlPage extends StatefulWidget {
  final String src;
  const HtmlPage({super.key, required this.src});

  @override
  State<HtmlPage> createState() => _HtmlPageState();
}

class _HtmlPageState extends State<HtmlPage> {
  late final String _type = 'collider-html-${_pages++}';
  late final web.HTMLIFrameElement _el;

  @override
  void initState() {
    super.initState();
    _el = web.HTMLIFrameElement()
      ..src = widget.src
      ..style.border = '0'
      ..style.width = '100%'
      ..style.height = '100%'
      ..style.background = 'transparent';
    _el.setAttribute('allow', 'clipboard-read; clipboard-write; microphone');
    ui_web.platformViewRegistry.registerViewFactory(_type, (int _) => _el);
  }

  @override
  void didUpdateWidget(covariant HtmlPage old) {
    super.didUpdateWidget(old);
    if (widget.src != old.src) _el.src = widget.src;
  }

  @override
  Widget build(BuildContext context) => HtmlElementView(viewType: _type);
}

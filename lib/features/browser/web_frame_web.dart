// Browser page surface (web). Made by Claude.
// Pages load through the local Collider server so sites that refuse framing still render.
// The page reports where it is, so the address bar, Back and Forward follow links the user taps.
import 'browser_store.dart';
import 'dart:js_interop';
import 'dart:ui_web' as ui_web;
import 'package:flutter/widgets.dart';
import 'package:web/web.dart' as web;

int _frames = 0;

class WebFrame extends StatefulWidget {
  /// The page the app wants shown.
  final String url;

  /// Increase to load the current page again.
  final int reload;

  /// Text size: 1 is the page's own size.
  final double zoom;

  /// The page moved on its own: a link, a form, a redirect.
  final void Function(String url, String title)? onNavigated;

  /// A link turned out to be a file; it was saved to Files > Downloaded under this name.
  final void Function(String name)? onDownloaded;

  const WebFrame({super.key, required this.url, this.reload = 0, this.zoom = 1, this.onNavigated, this.onDownloaded});

  @override
  State<WebFrame> createState() => _WebFrameState();
}

class _WebFrameState extends State<WebFrame> {
  late final String _type = 'collider-frame-${_frames++}';
  late final web.HTMLIFrameElement _el;
  late final JSFunction _listener;
  String _showing = '';

  static String _proxied(String url) => '/api/page?url=${Uri.encodeComponent(url)}';

  @override
  void initState() {
    super.initState();
    _showing = widget.url;
    // A phone-sized window gets the phone page of a site, so the page fits it.
    // Sites are asked for their phone pages on a phone, unless Settings > Request Desktop Website is on.
    web.document.cookie = 'collider_ua=${web.window.innerWidth < 768 && !BrowserStore.instance.desktop ? 'mobile' : 'desktop'}; path=/; SameSite=Lax';
    _el = web.HTMLIFrameElement()
      ..src = _proxied(widget.url)
      ..style.border = '0'
      ..style.width = '100%'
      ..style.height = '100%'
      ..style.background = 'white';
    // A page may run its scripts and forms but may never replace the app around it.
    _el.style.setProperty('zoom', '${widget.zoom}');
    // The page recedes at the window's lower edge, where it runs on, over an eased ramp (Claude, 2026-10-20).
    // The app cannot fade inside a web page with its own masks, so the frame itself carries the mask.
    const mask = 'linear-gradient(to bottom, #000 0, #000 calc(100% - 56px), rgba(0,0,0,.86) calc(100% - 40px), '
        'rgba(0,0,0,.58) calc(100% - 24px), rgba(0,0,0,.24) calc(100% - 10px), transparent 100%)';
    _el.style.setProperty('mask-image', mask);
    _el.style.setProperty('-webkit-mask-image', mask);
    _el.setAttribute('sandbox', 'allow-scripts allow-forms allow-same-origin allow-popups');
    ui_web.platformViewRegistry.registerViewFactory(_type, (int _) => _el);
    _listener = ((web.Event e) {
      final m = e as web.MessageEvent;
      final from = m.source as JSAny?;
      if (from == null || !from.strictEquals(_el.contentWindow as JSAny?).toDart) return;
      final d = m.data.dartify();
      if (d is! Map) return;
      if (d['collider'] == 'nav') {
        final u = '${d['url'] ?? ''}';
        if (u.isEmpty) return;
        _showing = u;
        widget.onNavigated?.call(u, '${d['title'] ?? ''}');
      } else if (d['collider'] == 'download') {
        widget.onDownloaded?.call('${d['name'] ?? ''}');
      }
    }).toJS;
    web.window.addEventListener('message', _listener);
  }

  @override
  void didUpdateWidget(covariant WebFrame old) {
    super.didUpdateWidget(old);
    if (widget.zoom != old.zoom) _el.style.setProperty('zoom', '${widget.zoom}');
    if (widget.reload != old.reload || widget.url != _showing) {
      _showing = widget.url;
      _el.src = _proxied(widget.url);
    }
  }

  @override
  void dispose() {
    web.window.removeEventListener('message', _listener);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => HtmlElementView(viewType: _type);
}

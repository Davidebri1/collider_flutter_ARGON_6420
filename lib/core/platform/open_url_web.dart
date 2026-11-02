// Made by Claude.
import 'dart:js_interop';
import 'dart:typed_data';
import 'dart:js_interop_unsafe';
import 'package:web/web.dart' as web;

void openUrl(String url) => web.window.open(url, '_blank');

/// System share sheet. Returns false when the browser has none, so the caller can copy instead.
Future<bool> shareText(String text) async {
  try {
    await web.window.navigator.share(web.ShareData(text: text)).toDart;
    return true;
  } catch (_) {
    return false;
  }
}

/// The app is running on the computer that serves it (Collider.exe's window, or a browser on that computer).
bool get onThisComputer => const {'127.0.0.1', 'localhost'}.contains(Uri.base.host);

/// The phone's share sheet with the file itself in it, so the apps that take that kind of file are offered
/// (Claude, 2026-10-21). False where the browser cannot share files.
Future<bool> shareFile(List<int> bytes, String name, String mime) async {
  try {
    final file = web.File([Uint8List.fromList(bytes).toJS].toJS, name, web.FilePropertyBag(type: mime));
    final data = web.ShareData(files: [file].toJS);
    if (!web.window.navigator.canShare(data)) return false;
    await web.window.navigator.share(data).toDart;
    return true;
  } catch (_) {
    return false;
  }
}

/// True when this device has a system share sheet.
bool get canShareText => (web.window.navigator as JSObject).has('share');

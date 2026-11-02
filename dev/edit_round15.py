# Made by Claude (2026-10-21). Round 15: files Collider does not open go to the device's own app picker.
# David, 21 Oct: "Uploaded songs, like all uploaded files, should open up the app picker so users get to choose where
# they play the file. An iOS and Android thing. Videos play in this app because we have a full video player, not a full
# music player ... It either opens the document/file, or it opens app picker and outsources the effort. Previews still
# do show in my app though".
# On this computer the picker is Windows' own "Open with" (rundll32 shell32.dll,OpenAs_RunDLL); on a phone it is the
# phone's share sheet with the file in it (the Web Share API, which lists the apps that take that kind of file).
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for: {old[:80]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("tools/collider_server.py", [
    ("""            if p == "/api/files/download":""",
     """            if p == "/api/files/openwith":
                # Windows' own app picker for a file in Files; only from this computer's own window.
                b = self._body()
                path = FILES.path_for(b.get("source", ""), b.get("name", "")) if self._local() else None
                if not path:
                    return self._json({"ok": False}, 404)
                import subprocess
                subprocess.Popen(["rundll32.exe", "shell32.dll,OpenAs_RunDLL", path], stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return self._json({"ok": True})
            if p == "/api/files/download":"""),
])

edit("lib/core/platform/open_url_web.dart", [
    ("""/// True when this device has a system share sheet.""",
     """/// The app is running on the computer that serves it (Collider.exe's window, or a browser on that computer).
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

/// True when this device has a system share sheet."""),
    ("""import 'dart:js_interop';
""", """import 'dart:js_interop';
import 'dart:typed_data';
"""),
])

edit("lib/core/platform/open_url_stub.dart", [
    ("""bool get canShareText => false;""",
     """bool get canShareText => false;

bool get onThisComputer => false;

Future<bool> shareFile(List<int> bytes, String name, String mime) async => false;"""),
])

edit("lib/core/api/collider_api.dart", [
    ("""  String fileUrl(ColliderFile f) =>""",
     """  /// Windows' own app picker for [f], on the computer that serves the app (Claude, 2026-10-21).
  Future<void> openWith(ColliderFile f) async {
    try {
      await _dio.post('$_base/api/files/openwith', data: {'source': f.source, 'name': f.name});
    } catch (_) {}
  }

  /// The file's bytes, for handing it to the phone's share sheet.
  Future<List<int>?> fileBytes(ColliderFile f) async {
    try {
      final r = await _dio.get<List<int>>(fileUrl(f), options: Options(responseType: ResponseType.bytes));
      return r.data;
    } catch (_) {
      return null;
    }
  }

  String fileUrl(ColliderFile f) =>"""),
])

FS = "lib/features/files/screens/files_screen.dart"
edit(FS, [
    ("""    setState(() {
      _history.removeRange(_at + 1, _history.length);
      _history.add(v);
      _at++;
    });
  }
""", """    setState(() {
      _history.removeRange(_at + 1, _history.length);
      _history.add(v);
      _at++;
    });
    // A file Collider does not open itself: its preview here, and the device's app picker for the rest.
    if (f != null && !f.asset && _outside(f)) _appPicker(f);
  }

  /// Collider opens pictures, videos (its player), documents (Documents) and the songs the models made (Files >
  /// Music). Everything else goes to the device's own apps. (Claude, 2026-10-21)
  bool _outside(ColliderFile f) => f.kind != 'image' && f.kind != 'video';

  final Map<String, List<int>> _bytes = {};

  Future<void> _appPicker(ColliderFile f) async {
    if (onThisComputer) {
      await _api.openWith(f);
      return;
    }
    final bytes = _bytes[f.url] ??= (await _api.fileBytes(f)) ?? const [];
    if (bytes.isEmpty) return;
    if (!await shareFile(bytes, f.name, _mime(f.name))) openUrl(_api.fileUrl(f));
  }

  static String _mime(String name) {
    final e = name.contains('.') ? name.split('.').last.toLowerCase() : '';
    return const {
          'mp3': 'audio/mpeg', 'm4a': 'audio/mp4', 'aac': 'audio/aac', 'wav': 'audio/wav', 'flac': 'audio/flac', 'ogg': 'audio/ogg',
          'zip': 'application/zip', 'csv': 'text/csv', 'json': 'application/json', 'stl': 'model/stl', 'obj': 'model/obj',
          'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
          'svg': 'image/svg+xml', 'exe': 'application/vnd.microsoft.portable-executable',
        }[e] ??
        'application/octet-stream';
  }
"""),
    ("""          onTap: () => openUrl(_api.fileUrl(f)),""", """          onTap: () => _appPicker(f),"""),
])

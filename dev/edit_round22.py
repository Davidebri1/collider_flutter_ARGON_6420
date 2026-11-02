# Made by Claude (2026-10-23). Round 22: the app runs from Flutter's own runner on any device, not only as a web page
# served by Collider's server. David, 23 Oct: "i just want a standard flutter runner ... simple load project, run".
# Every call the app makes went to "the address this page came from" (Uri.base.origin), which only exists on the web.
# Now one address serves them all: on the web, the page's own; elsewhere, Collider's server on this computer
# (10.0.2.2 is this computer as seen from inside Android's emulator), or whatever --dart-define=COLLIDER_SERVER names.
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for {old[:70]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("lib/core/api/collider_api.dart", [
    ("import 'package:dio/dio.dart';\n",
     "import 'package:dio/dio.dart';\nimport 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform, TargetPlatform;\n"),
    ("""class ColliderApi {
  ColliderApi._();
  static final ColliderApi instance = ColliderApi._();
""", """class ColliderApi {
  ColliderApi._();
  static final ColliderApi instance = ColliderApi._();

  /// Where Collider's server is. On the web: the address the page came from. On a phone, tablet or desktop run from
  /// Flutter's runner: --dart-define=COLLIDER_SERVER=<address>, else the server on this computer at host 47801
  /// (seen as 10.0.2.2 from inside Android's emulator). (Claude, 2026-10-23)
  static final String base = () {
    const named = String.fromEnvironment('COLLIDER_SERVER');
    if (named.isNotEmpty) return named;
    if (kIsWeb) return Uri.base.origin;
    return defaultTargetPlatform == TargetPlatform.android ? 'http://10.0.2.2:47801' : 'http://127.0.0.1:47801';
  }();
"""),
    ("  String get _base => Uri.base.origin;", "  String get _base => base;"),
])
edit("lib/core/media/theme_cloud.dart", [
    ("'${Uri.base.origin}/api/themes'", "'${ColliderApi.base}/api/themes'"),
])
edit("lib/features/theme/theme_pack_store.dart", [
    ("'${Uri.base.origin}/api/store'", "'${ColliderApi.base}/api/store'"),
])
for rel in ("lib/core/media/theme_cloud.dart", "lib/features/theme/theme_pack_store.dart"):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    if "collider_api.dart" not in s:
        depth = rel.count("/") - 1
        imp = "import '" + "../" * depth + "core/api/collider_api.dart';\n"
        i = s.index("import ")
        s = s[:i] + imp + s[i:]
        p.write_text(s, encoding="utf-8")
        print("import added", rel)

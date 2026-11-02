# Made by Claude (2026-10-23). Round 26: Device Preview 3.0 (pub.dev). 3.0 has no in-app toolbar: its device picker,
# sizes, orientation and screenshot button live in the "device_preview" tab of Flutter DevTools, in debug and profile
# runs only. Release builds (app stores, the hosted page) are untouched.
p = "lib/main.dart"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


# undo the 2.x-style attempt from the first version of this script, if present
if "DevicePreview.appBuilder" in s:
    rep("      locale: DevicePreview.locale(context),\n"
        "      builder: (context, child) => DevicePreview.appBuilder(context,\n"
        "          MaterialUiCompatibilityBridge(child: DefaultAssetBundle(bundle: ThemeMediaAssetBundle.instance, child: child!))),",
        "      builder: (context, child) =>\n          MaterialUiCompatibilityBridge(child: DefaultAssetBundle(bundle: ThemeMediaAssetBundle.instance, child: child!)),")
    rep("  // Device Preview: device frames, sizes and screenshots on the web test page in a wide browser (Claude, 2026-10-23).\n"
        "  final view = WidgetsBinding.instance.platformDispatcher.views.first;\n"
        "  final wide = view.physicalSize.width / view.devicePixelRatio >= 900;\n"
        "  runApp(DevicePreview(enabled: kIsWeb && wide, builder: (context) => const ColliderApp()));\n}",
        "  runApp(const ColliderApp());\n}")
    rep("import 'package:flutter/foundation.dart' show kIsWeb;\n", "")

if "DevicePreview.enable" not in s:
    rep("Future<void> main() async {\n  WidgetsFlutterBinding.ensureInitialized();",
        "Future<void> main() async {\n"
        "  // Device Preview 3.0: devices, sizes, orientation and screenshots from the device_preview tab in DevTools,\n"
        "  // debug and profile runs only (Claude, 2026-10-23).\n"
        "  DevicePreview.enable();\n"
        "  WidgetsFlutterBinding.ensureInitialized();")
open(p, "w", encoding="utf-8").write(s)
print("round 26 applied")

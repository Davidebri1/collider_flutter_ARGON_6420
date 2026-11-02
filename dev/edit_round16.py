# Made by Claude (2026-10-21). Round 16: the browser's bookmarks, history and settings (browser_store.dart).
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


B = "lib/features/browser/screens/in_app_browser_sheet.dart"
edit(B, [
    ("import '../models/browser_tab.dart';\n", "import '../browser_store.dart';\nimport '../models/browser_tab.dart';\n"),
    ("""  final Function(BrowserTab newTab)? onNewUserTab;

  const InAppBrowserSheet({""", """  final Function(BrowserTab newTab)? onNewUserTab;
  final bool incognito; // the app's Incognito: pages are not kept in History

  const InAppBrowserSheet({"""),
    ("""    this.onNewUserTab,
  });""", """    this.onNewUserTab,
    this.incognito = false,
  });"""),
    ("""  bool _sidebar = false;
""", """  bool _sidebar = false;
  String? _side; // the sidebar's open section: bookmarks, history or settings
"""),
    ("""    _activeTabId = widget.initialTabId;
  }""", """    _activeTabId = widget.initialTabId;
    BrowserStore.instance.init().then((_) {
      if (mounted) setState(() {});
    });
  }"""),
    ("""    widget.onTabUpdated?.call(updated);
    setState(() => _overview = false);""", """    widget.onTabUpdated?.call(updated);
    if (!widget.incognito) BrowserStore.instance.visited(updated.url, updated.title);
    setState(() => _overview = false);"""),
    ("""    final sidebar = round(Icons.view_sidebar_outlined, 'Sidebar', () => setState(() => _sidebar = !_sidebar), on: _sidebar);""",
     """    final sidebar = round(Icons.view_sidebar_outlined, 'Sidebar', () => setState(() {
          _sidebar = !_sidebar;
          _side = null;
        }), on: _sidebar);"""),
    ("""        if (_sidebar) Positioned(left: 8, top: 8, width: 200, child: _sidebarPanel()),""",
     """        if (_sidebar) Positioned(left: 8, top: 8, width: 240, child: _sidebarPanel()),"""),
])
p = ROOT / B
s = p.read_text(encoding="utf-8")
a = s.index("  /// The sidebar: the open tabs, then Save")
z = s.index("  Widget _page(BrowserTab tab) {")
s = s[:a] + (ROOT / "dev/draft/browser_sidebar.dart").read_text(encoding="utf-8") + s[z:]
p.write_text(s, encoding="utf-8")
print("sidebar replaced")

edit("lib/features/browser/web_frame_web.dart", [
    ("""    web.document.cookie = 'collider_ua=${web.window.innerWidth < 768 ? 'mobile' : 'desktop'}; path=/; SameSite=Lax';""",
     """    // Sites are asked for their phone pages on a phone, unless Settings > Request Desktop Website is on.
    web.document.cookie = 'collider_ua=${web.window.innerWidth < 768 && !BrowserStore.instance.desktop ? 'mobile' : 'desktop'}; path=/; SameSite=Lax';"""),
])
p = ROOT / "lib/features/browser/web_frame_web.dart"
s = p.read_text(encoding="utf-8")
i = s.index("import ")
s = s[:i] + "import 'browser_store.dart';\n" + s[i:]
p.write_text(s, encoding="utf-8")
print("import added to web_frame_web.dart")

edit("lib/main.dart", [
    ("""        return InAppBrowserSheet(
          initialTabId: tabId,
          tabs: _browserTabs,""", """        return InAppBrowserSheet(
          initialTabId: tabId,
          tabs: _browserTabs,
          incognito: _incognito,"""),
])

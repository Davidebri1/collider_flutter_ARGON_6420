import '../../../core/drafts.dart';
import 'dart:math' as math;
import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';
import '../../../core/platform/open_url.dart';
import '../../../core/api/collider_api.dart';
import '../../../core/vision/vision_kit.dart';
import '../browser_store.dart';
import '../models/browser_tab.dart';
import '../web_frame.dart';

/// In-app browser — visionOS Safari glass bar + page window with top-bar Close action.
class InAppBrowserSheet extends StatefulWidget {
  final String initialTabId;
  final List<BrowserTab> tabs;
  final Function(BrowserTab updatedTab)? onTabUpdated;
  final Function(BrowserTab newTab)? onNewUserTab;
  final bool incognito;

  const InAppBrowserSheet({
    super.key,
    required this.initialTabId,
    required this.tabs,
    this.onTabUpdated,
    this.onNewUserTab,
    this.incognito = false,
  });

  @override
  State<InAppBrowserSheet> createState() => _InAppBrowserSheetState();
}

class _InAppBrowserSheetState extends State<InAppBrowserSheet> {
  static const _homePage = 'https://www.google.com/';
  static const _search = 'https://www.google.com/search?q=';

  late String _activeTabId;
  bool _overview = false;
  final TextEditingController _addr = Drafts.text('browser.address');
  final Map<String, List<String>> _back = {};
  final Map<String, List<String>> _forward = {};
  int _reload = 0;
  bool _sidebar = false;
  String? _side;
  double _zoom = 1;
  String? _shownUrl;
  String? _savedName;

  late final List<BrowserTab> _tabs = List.of(widget.tabs);

  BrowserTab get _tab => _tabs.firstWhere((t) => t.id == _activeTabId, orElse: () => _tabs.first);

  @override
  void initState() {
    super.initState();
    _activeTabId = widget.initialTabId;
    BrowserStore.instance.init().then((_) {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    super.dispose();
  }

  void _switchTab(String id) => setState(() {
        _activeTabId = id;
        _overview = false;
      });

  void _newTab() {
    final t = BrowserTab(
      id: 'user_${DateTime.now().millisecondsSinceEpoch}',
      title: 'Search',
      url: _homePage,
      isModelAssigned: false,
      isUserControlling: true,
    );
    _tabs.add(t);
    widget.onNewUserTab?.call(t);
    _switchTab(t.id);
  }

  String _host(String url) => url.replaceFirst(RegExp(r'^https?://'), '');

  String _site(String url) {
    final h = Uri.tryParse(url)?.host ?? '';
    return h.isEmpty ? _host(url) : h.replaceFirst(RegExp(r'^www\.'), '');
  }

  void _show(String url, {String? title}) {
    final updated = _tab.copyWith(url: url, title: title ?? _host(url));
    final i = _tabs.indexWhere((t) => t.id == updated.id);
    if (i != -1) _tabs[i] = updated;
    widget.onTabUpdated?.call(updated);
    if (!widget.incognito) BrowserStore.instance.visited(updated.url, updated.title);
    setState(() => _overview = false);
  }

  void _go(String input) {
    final q = input.trim();
    if (q.isEmpty) return;
    final isUrl = !q.contains(' ') && (q.contains('.') || q.startsWith('http'));
    final url = isUrl ? (q.startsWith('http') ? q : 'https://$q') : '$_search${Uri.encodeComponent(q)}';
    if (url == _tab.url) {
      setState(() => _reload++);
      return;
    }
    (_back[_tab.id] ??= []).add(_tab.url);
    _forward[_tab.id]?.clear();
    _show(url, title: isUrl ? null : q);
  }

  void _onNavigated(String url, String title) {
    final tab = _tab;
    if (url != tab.url) {
      (_back[tab.id] ??= []).add(tab.url);
      _forward[tab.id]?.clear();
    } else if (title.isEmpty || title == tab.title) {
      return;
    }
    _show(url, title: title.isEmpty ? null : title);
  }

  void _goBack() {
    final stack = _back[_tab.id];
    if (stack == null || stack.isEmpty) return;
    (_forward[_tab.id] ??= []).add(_tab.url);
    _show(stack.removeLast());
  }

  void _goForward() {
    final stack = _forward[_tab.id];
    if (stack == null || stack.isEmpty) return;
    (_back[_tab.id] ??= []).add(_tab.url);
    _show(stack.removeLast());
  }

  void _flashSaved(String? name) {
    if (name == null || name.isEmpty || !mounted) return;
    setState(() => _savedName = name);
    Future.delayed(const Duration(milliseconds: 1800), () {
      if (mounted) setState(() => _savedName = null);
    });
  }

  Future<void> _save() async => _flashSaved(await ColliderApi.instance.download(_tab.url));

  @override
  Widget build(BuildContext context) {
    final tab = _tab;
    if (_shownUrl != tab.url) {
      _shownUrl = tab.url;
      _addr.text = _site(tab.url);
    }
    final size = MediaQuery.sizeOf(context);
    final h = math.max(size.height - 56 - 84 - 54, 320.0);
    final canBack = (_back[tab.id] ?? const []).isNotEmpty;
    final canForward = (_forward[tab.id] ?? const []).isNotEmpty;

    Widget round(IconData icon, String tip, VoidCallback? onTap, {bool on = false}) => VCircleButton(
          icon: icon,
          size: 30,
          selected: true,
          tooltip: tip,
          iconColor: onTap == null ? VColors.textTertiary : (on ? VColors.accentBlue : null),
          onTap: onTap,
        );

    final phone = size.width < 768;
    final address = VRecessed(
      height: phone ? 36 : 30,
      padding: const EdgeInsets.symmetric(horizontal: 10),
      child: Row(
        children: [
          VPress(
            tooltip: 'Text Size',
            onTap: () => setState(() => _zoom = _zoom >= 1.3 ? 1 : _zoom + 0.15),
            child: Text('Aa', style: VType.caption(color: VColors.textPrimary, weight: FontWeight.w500).copyWith(fontSize: phone ? 14 : 12)),
          ),
          const SizedBox(width: 4),
          const Icon(Icons.lock_rounded, size: 10, color: Color(0x99FFFFFF)),
          const SizedBox(width: 4),
          Expanded(
            child: TextField(
              controller: _addr,
              textAlign: TextAlign.center,
              cursorColor: VColors.textPrimary,
              style: VType.caption(color: VColors.textPrimary, weight: FontWeight.w500).copyWith(fontSize: phone ? 14 : 12),
              keyboardType: TextInputType.url,
              textInputAction: TextInputAction.go,
              decoration: const InputDecoration(border: InputBorder.none, isDense: true, contentPadding: EdgeInsets.zero),
              onTap: () {
                _addr.text = _tab.url;
                _addr.selection = TextSelection(baseOffset: 0, extentOffset: _addr.text.length);
              },
              onSubmitted: _go,
            ),
          ),
          const SizedBox(width: 4),
          VPress(
            tooltip: 'Reload',
            onTap: () => setState(() => _reload++),
            child: Icon(Icons.refresh_rounded, size: phone ? 17 : 15, color: VColors.textPrimary),
          ),
        ],
      ),
    );
    final sidebar = round(Icons.view_sidebar_outlined, 'Sidebar', () => setState(() {
          _sidebar = !_sidebar;
          _side = null;
        }), on: _sidebar);
    final back = round(Icons.chevron_left_rounded, 'Back', canBack ? _goBack : null);
    final forward = round(Icons.chevron_right_rounded, 'Forward', canForward ? _goForward : null);
    final share = round(Icons.ios_share_rounded, 'Share', _share);
    final newTab = round(Icons.add_rounded, 'New Tab', _newTab);
    final tabs = round(Icons.filter_none_rounded, 'Tabs (${_tabs.length})', () => setState(() => _overview = !_overview), on: _overview);
    final closeBtn = round(Icons.close_rounded, 'Close Browser', () => Navigator.of(context).pop());

    Widget capsule(Widget child) => GestureDetector(
          onVerticalDragEnd: (d) {
            if ((d.primaryVelocity ?? 0) > 250) Navigator.of(context).pop();
          },
          child: VGlass(
            material: VMaterial.elevated,
            radius: VRadius.full,
            fill: const Color(0x4D808080),
            padding: const EdgeInsets.all(6),
            child: child,
          ),
        );
    final window = Stack(
      children: [
        Positioned.fill(
          child: VGlass(
            material: VMaterial.work,
            radius: 20,
            padding: const EdgeInsets.all(5),
            child: AnimatedSwitcher(
              duration: VMotion.base,
              child: _overview ? _tabsOverview() : _page(tab),
            ),
          ),
        ),
        if (_sidebar) Positioned(left: 8, top: 8, width: 240, child: _sidebarPanel()),
      ],
    );

    return Stack(
      children: [
        Dialog(
          backgroundColor: Colors.transparent,
          elevation: 0,
          alignment: Alignment.topCenter,
          insetPadding: phone
              ? const EdgeInsets.fromLTRB(VSpace.md, 52, VSpace.md, 92)
              : const EdgeInsets.fromLTRB(VSpace.xl, 44, VSpace.xl, 92),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 920),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: phone
                  ? [
                      capsule(Row(children: [Expanded(child: address), const SizedBox(width: 6), closeBtn])),
                      const SizedBox(height: 10),
                      SizedBox(height: math.max(size.height - 268, 280.0), child: window),
                      const SizedBox(height: 10),
                      capsule(Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [back, forward, share, newTab, tabs, sidebar])),
                    ]
                  : [
                      capsule(Row(children: [
                        sidebar,
                        const SizedBox(width: 4),
                        back,
                        const SizedBox(width: 4),
                        forward,
                        const SizedBox(width: 8),
                        Expanded(child: address),
                        const SizedBox(width: 8),
                        share,
                        const SizedBox(width: 4),
                        newTab,
                        const SizedBox(width: 4),
                        tabs,
                        const SizedBox(width: 4),
                        closeBtn,
                      ])),
                      const SizedBox(height: 12),
                      SizedBox(height: h, child: window),
                    ],
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _share() async {
    if (canShareText && await shareText(_tab.url)) return;
    await Clipboard.setData(ClipboardData(text: _tab.url));
    _flashSaved('Copied');
  }

  Widget _sidebarPanel() {
    final store = BrowserStore.instance;
    Widget row(IconData? icon, String label, VoidCallback onTap, {bool on = false, Widget? trailing}) => VPress(
          onTap: onTap,
          child: Container(
            height: 40,
            padding: const EdgeInsets.symmetric(horizontal: 10),
            decoration: BoxDecoration(color: on ? const Color(0x24FFFFFF) : Colors.transparent, borderRadius: BorderRadius.circular(11)),
            child: Row(
              children: [
                if (icon != null) ...[Icon(icon, size: 17, color: VColors.textSecondary), const SizedBox(width: 10)],
                Expanded(child: Text(label, maxLines: 1, softWrap: false, overflow: TextOverflow.fade, style: VType.callout(weight: FontWeight.w500))),
                if (trailing != null) trailing,
              ],
            ),
          ),
        );
    Widget page(BrowserPage p) => row(null, p.title.isEmpty ? _host(p.url) : p.title, () {
          setState(() => _sidebar = false);
          _go(p.url);
        });
    Widget back(String label) => row(Icons.chevron_left_rounded, label, () => setState(() => _side = null));

    final List<Widget> children;
    switch (_side) {
      case 'bookmarks':
        final here = store.isBookmarked(_tab.url);
        children = [
          back('Bookmarks'),
          row(here ? Icons.bookmark_rounded : Icons.bookmark_add_outlined, _tab.title.isEmpty ? _host(_tab.url) : _tab.title,
              () => setState(() => store.toggleBookmark(_tab.url, _tab.title)),
              on: here),
          const Divider(height: 10, color: Color(0x1FFFFFFF)),
          for (final b in store.bookmarks) page(b),
        ];
      case 'history':
        children = [
          back('History'),
          for (final h in store.history.take(200)) page(h),
          if (store.history.isNotEmpty) ...[
            const Divider(height: 10, color: Color(0x1FFFFFFF)),
            row(Icons.delete_outline_rounded, 'Clear History', () => setState(store.clearHistory)),
          ],
        ];
      case 'settings':
        children = [
          back('Settings'),
          row(Icons.desktop_windows_outlined, 'Request Desktop Website', () {
            setState(() => store.setDesktop(!store.desktop));
            setState(() => _reload++);
          }, trailing: IgnorePointer(child: VToggle(value: store.desktop, onChanged: (_) {}))),
          row(Icons.delete_outline_rounded, 'Clear History', () => setState(store.clearHistory)),
        ];
      default:
        children = [
          for (final t in _tabs)
            row(null, t.title.isEmpty ? _host(t.url) : t.title, () {
              _switchTab(t.id);
              setState(() => _sidebar = false);
            }, on: t.id == _activeTabId),
          const Divider(height: 10, color: Color(0x1FFFFFFF)),
          row(Icons.bookmark_border_rounded, 'Bookmarks', () => setState(() => _side = 'bookmarks')),
          row(Icons.history_rounded, 'History', () => setState(() => _side = 'history')),
          row(Icons.tune_rounded, 'Settings', () => setState(() => _side = 'settings')),
          const Divider(height: 10, color: Color(0x1FFFFFFF)),
          row(_savedName != null ? Icons.check_rounded : Icons.download_rounded, _savedName ?? 'Save', _save),
          row(Icons.close_rounded, 'Close', () => Navigator.of(context).pop()),
        ];
    }
    return DecoratedBox(
      decoration: BoxDecoration(color: const Color(0xFF1C2026), borderRadius: BorderRadius.circular(16)),
      child: VGlass(
        material: VMaterial.modal,
        radius: 16,
        padding: const EdgeInsets.all(6),
        child: ConstrainedBox(
          constraints: BoxConstraints(maxHeight: MediaQuery.sizeOf(context).height * 0.6),
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: Column(mainAxisSize: MainAxisSize.min, children: children),
          ),
        ),
      ),
    );
  }

  Widget _page(BrowserTab tab) {
    return ClipRRect(
      key: ValueKey('page-${tab.id}'),
      borderRadius: BorderRadius.circular(15),
      child: WebFrame(
        key: ValueKey('frame-${tab.id}'),
        url: tab.url,
        reload: _reload,
        zoom: _zoom,
        onNavigated: _onNavigated,
        onDownloaded: _flashSaved,
      ),
    );
  }

  Widget _tabsOverview() {
    return LayoutBuilder(
      key: const ValueKey('tabs'),
      builder: (context, c) {
        final cols = c.maxWidth < 420 ? 2 : 3;
        return Padding(
          padding: const EdgeInsets.all(VSpace.sm),
          child: GridView.builder(
            physics: const BouncingScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: cols, childAspectRatio: 0.9),
            itemCount: _tabs.length,
            itemBuilder: (_, i) {
              final t = _tabs[i];
              return VTile(
                selected: t.id == _activeTabId,
                onTap: () => _switchTab(t.id),
                aspect: 4 / 3,
                title: t.title,
                subtitle: t.isModelAssigned ? (t.modelName ?? 'Model') : _host(t.url),
                media: Container(
                  color: VColors.fillCell,
                  child: Icon(t.isModelAssigned ? Icons.terminal_rounded : Icons.public_rounded, size: 26, color: VColors.textSecondary),
                ),
              );
            },
          ),
        );
      },
    );
  }
}

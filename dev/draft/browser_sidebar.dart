  /// The sidebar, as Safari's: the open tabs; Bookmarks, History and Settings, each opening in place; then Save (the
  /// page, to Files) and Close. (Bookmarks, History and Settings: Claude, 2026-10-21.)
  Widget _sidebarPanel() {
    final store = BrowserStore.instance;
    Widget row(IconData? icon, String label, VoidCallback onTap, {bool on = false, Widget? trailing}) => VPress(
          onTap: onTap,
          child: Container(
            height: 44,
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
              () => setState(() => store.toggleBookmark(_tab.url, _tab.title)), on: here),
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
    // Solid backing: the page under this panel is a web frame, which glass cannot blur.
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


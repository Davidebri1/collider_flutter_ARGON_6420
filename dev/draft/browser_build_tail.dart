    // On a phone (Claude, 2026-10-21; David: "proper mobile aspect ratio. And responsive design to match"): Safari's
    // iPhone layout. The address takes the whole bar so the site's name shows, and the buttons sit in their own bar
    // under the page, spread across it. Wider than a phone, the one bar as before.
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
          const SizedBox(width: 3),
          const Icon(Icons.lock_rounded, size: 10, color: Color(0x99FFFFFF)),
          const SizedBox(width: 3),
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
    final sidebar = round(Icons.view_sidebar_outlined, 'Sidebar', () => setState(() => _sidebar = !_sidebar), on: _sidebar);
    final back = round(Icons.chevron_left_rounded, 'Back', canBack ? _goBack : null);
    final forward = round(Icons.chevron_right_rounded, 'Forward', canForward ? _goForward : null);
    final share = round(Icons.ios_share_rounded, 'Share', _share);
    final newTab = round(Icons.add_rounded, 'New Tab', _newTab);
    final tabs = round(Icons.filter_none_rounded, 'Tabs', () => setState(() => _overview = !_overview), on: _overview);
    Widget capsule(Widget child) => GestureDetector(
          // A downward swipe on a bar closes the browser.
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
        if (_sidebar) Positioned(left: 8, top: 8, width: 200, child: _sidebarPanel()),
      ],
    );

    return Stack(
      children: [
        Dialog(
          backgroundColor: Colors.transparent,
          elevation: 0,
          alignment: Alignment.topCenter,
          insetPadding: phone ? const EdgeInsets.fromLTRB(VSpace.md, 52, VSpace.md, 92) : const EdgeInsets.fromLTRB(VSpace.xl, 56, VSpace.xl, 92),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 900),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: phone
                  ? [
                      capsule(address),
                      const SizedBox(height: 10),
                      // the screen less the insets (52 + 92), the two bars (48 + 56) and the gaps between them (20)
                      SizedBox(height: math.max(size.height - 268, 280.0), child: window),
                      const SizedBox(height: 10),
                      capsule(Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [back, forward, share, newTab, tabs, sidebar])),
                    ]
                  : [
                      capsule(Row(children: [
                        sidebar,
                        const SizedBox(width: 3),
                        back,
                        const SizedBox(width: 3),
                        forward,
                        const SizedBox(width: 6),
                        Expanded(child: address),
                        const SizedBox(width: 6),
                        share,
                        const SizedBox(width: 3),
                        newTab,
                        const SizedBox(width: 3),
                        tabs,
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


# Made by Claude (2026-10-23). Round 32, David's callouts:
#  - side navigation (third callout): each place as visionOS shows it, its glyph on a disc with its name under it; no
#    Models button (models are chosen in the ticker);
#  - the ticker as his diagram: (1) every selected model has a row, lit, whether or not it has spoken; (3) under the
#    arrow, the models not selected, dim; while the arrow is open a tap selects or removes a model;
#  - no cardboard: rows are lines on the window's glass (no boxes); the conversation sits on the same glass beside the
#    column, a hairline between them, no box inside the window;
#  - no "answer" wording in the app.
import re


def edit(p, fn):
    s = open(p, encoding="utf-8").read()
    s2 = fn(s)
    assert s2 != s, p
    open(p, "w", encoding="utf-8").write(s2)


def one(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:80])
    return s.replace(a, b)


# ---------- side navigation ----------
def rail(s):
    a = s.index("  @override\n  Widget build(BuildContext context) {\n    return DecoratedBox(\n      decoration: BoxDecoration(borderRadius: BorderRadius.circular(VRadius.full), boxShadow: VShadow.ornament),")
    b = s.index("/// One conversation in a history list")
    new = '''  @override
  Widget build(BuildContext context) {
    // visionOS tab bar (Claude, 2026-10-23): a glass capsule beside the window; each place its glyph on a disc, its name
    // under it, the chosen one lit. 11 points, one word to a line.
    return DecoratedBox(
      decoration: BoxDecoration(borderRadius: BorderRadius.circular(VRadius.full), boxShadow: VShadow.ornament),
      child: VGlass(
        material: VMaterial.elevated,
        radius: VRadius.full,
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 10),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            for (int i = 0; i < items.length; i++) ...[
              if (i > 0) const SizedBox(height: 10),
              Semantics(
                button: true,
                label: items[i].label,
                child: VPress(
                  onTap: dim.contains(i) ? null : () => onSelect(i),
                  child: SizedBox(
                    width: 56,
                    child: Column(mainAxisSize: MainAxisSize.min, children: [
                      AnimatedContainer(
                        duration: VMotion.fast,
                        width: 44,
                        height: 44,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(shape: BoxShape.circle, color: i == active ? VColors.fillActive : VColors.fillCell),
                        child: Icon(items[i].icon, size: 20, color: dim.contains(i) ? const Color(0x59FFFFFF) : VColors.textPrimary),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        items[i].label.replaceAll(' ', '\\n'),
                        textAlign: TextAlign.center,
                        softWrap: false,
                        overflow: TextOverflow.visible,
                        style: VType.caption(
                          color: dim.contains(i) ? const Color(0x59FFFFFF) : (i == active ? VColors.textPrimary : VColors.textSecondary),
                          weight: FontWeight.w500,
                        ).copyWith(fontSize: 11, height: 13 / 11),
                      ),
                    ]),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

'''
    return s[:a] + new + s[b:]


edit("lib/core/vision/vision_kit.dart", rail)
# 11 points outside headers (David): the row style back to 11 (it had been set to 12 again)
edit("lib/core/vision/vision_kit.dart", lambda s: re.sub(r"static TextStyle get rowStyle => VType\.callout\(weight: FontWeight\.w500\)\.copyWith\(fontSize: 1[0-9](\.\d)?, height: [0-9.]+ / 1[0-9](\.\d)?\);",
                                                          "static TextStyle get rowStyle => VType.callout(weight: FontWeight.w500).copyWith(fontSize: 11, height: 15 / 11);", s))
edit("lib/features/nav/side_nav_rail.dart", lambda s: one(s, "          SideRailEntry('models', Icons.hub_outlined, 'Models'),\n", ""))


# ---------- the ticker ----------
def ticker(s):
    s = one(s, """  bool _isPillActive(TickerItem it) =>
      _selectedModelIds.contains(it.modelDef.id) && it.summary != 'No answer';""",
            """  bool _isPillActive(TickerItem it) => _selectedModelIds.contains(it.modelDef.id);

  /// The arrow under the model rows is open: the models not selected show, and a tap selects or removes a model.
  bool _choosing = false;

  /// Selects a model, or removes it (one stays selected; nine at most).
  void _toggleModel(String id) => setState(() {
        if (_selectedModelIds.contains(id)) {
          if (_selectedModelIds.length > 1) _selectedModelIds.remove(id);
          _expandedModelIds.remove(id);
        } else if (_selectedModelIds.length < 9) {
          _selectedModelIds.add(id);
        }
      });""")
    a = s.index("    final categoryItems = _tickerItems")
    b = s.index("    final media = _activeCategory == ModelCategory.image;")
    s = s[:a] + """    // (1) every selected model has a row, whether or not it has spoken yet; (3) the others wait under the arrow.
    TickerItem rowFor(ModelDef d) =>
        _tickerItems.where((t) => t.modelDef.id == d.id).firstOrNull ?? TickerItem(modelDef: d, relativeTime: '', summary: '', conversation: const []);
    final roster = ModelRoster.forCategory(_activeCategory);
    final activePills = [
      for (final id in _selectedModelIds)
        if (roster.where((m) => m.id == id).firstOrNull case final d?) rowFor(d),
    ];
    final idlePills = [for (final m in roster) if (!_selectedModelIds.contains(m.id)) rowFor(m)];

""" + s[b:]
    a = s.index("    // Collapsed Ticker: Consensus row pinned")
    b = s.index("    if (ThemeBlurCache.instance.activeAssetPath")
    s = s[:a] + """    // The ticker's column: the consensus, a hairline, the selected models; under the arrow, the rest (David's diagram).
    final Widget rows = Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (_tickerItems.isNotEmpty) ...[
          ConsensusRow(
            agreementRatio: _consensusRatio,
            summary: _consensusSummary,
            isGenerating: _isConsensusGenerating,
            onTap: () => setState(() => _activeDrawer = 'consensus'),
          ),
          const TickerDivider(),
        ],
        Flexible(
          child: EdgeFade(
            fadeHeight: 14,
            focus: FadeFocus.top,
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (final p in activePills)
                    ModelPill(
                      key: p.modelDef.id == openId ? _openKey : ValueKey('on-${p.modelDef.id}'),
                      item: p,
                      isActive: true,
                      isExpanded: !_choosing && p.modelDef.id == openId,
                      compact: openItem != null,
                      onToggleExpand: () => _choosing ? _toggleModel(p.modelDef.id) : _onTogglePill(p.modelDef.id),
                    ),
                  if (_choosing)
                    for (final p in idlePills)
                      ModelPill(
                        key: ValueKey('off-${p.modelDef.id}'),
                        item: p,
                        isActive: false,
                        isExpanded: false,
                        compact: openItem != null,
                        onToggleExpand: () => _toggleModel(p.modelDef.id),
                      ),
                ],
              ),
            ),
          ),
        ),
        if (idlePills.isNotEmpty || _choosing)
          VPress(
            onTap: () => setState(() => _choosing = !_choosing),
            child: SizedBox(
              height: 28,
              child: Center(
                child: AnimatedRotation(
                  turns: _choosing ? 0.5 : 0,
                  duration: VMotion.base,
                  curve: Curves.easeOutCubic,
                  child: const Icon(Icons.keyboard_arrow_down_rounded, size: 20, color: VColors.textSecondary),
                ),
              ),
            ),
          ),
      ],
    );

""" + s[b:]
    # side by side on one sheet of glass: a hairline between the column and the conversation, no box inside the window
    s, n = re.subn(r"const SizedBox\(width: VSpace\.xs\),\s*Expanded\(\s*child: Container\(\s*padding: const EdgeInsets\.fromLTRB\(10, 8, 8, 8\),\s*decoration: BoxDecoration\(\s*color: VColors\.fillRow,\s*borderRadius: BorderRadius\.circular\(VRadius\.card - VSpace\.xs\),\s*\),\s*child: conversation,\s*\),\s*\),",
                   """Container(
                                                  width: 1,
                                                  margin: const EdgeInsets.symmetric(horizontal: 6, vertical: 18),
                                                  decoration: const BoxDecoration(
                                                    gradient: LinearGradient(
                                                      begin: Alignment.topCenter,
                                                      end: Alignment.bottomCenter,
                                                      colors: [Color(0x00FFFFFF), Color(0x24FFFFFF), Color(0x24FFFFFF), Color(0x00FFFFFF)],
                                                      stops: [0, 0.15, 0.85, 1],
                                                    ),
                                                  ),
                                                ),
                                                Expanded(child: Padding(padding: const EdgeInsets.fromLTRB(4, 4, 4, 2), child: conversation)),""", s)
    assert n == 1, "side by side"
    # no "answer" wording
    s = s.replace("summary: r.status == 'error' ? 'No answer' : ", "summary: r.status == 'error' ? '' : ")
    s = s.replace("summary: 'No answer from this model.'", "summary: ''")
    s = s.replace("        _consensusSummary = 'No answer';\n", "        _consensusSummary = '';\n")
    s = s.replace("t.copyWith(isStreaming: false, summary: 'No answer')", "t.copyWith(isStreaming: false, summary: '')")
    s = s.replace("answer.isNotEmpty && answer != 'No answer'", "answer.isNotEmpty")
    return s


edit("lib/main.dart", ticker)


def api(s):
    a = s.find("  String get outcome => switch (this) {")
    if a < 0:
        return s + "\n"
    b = s.index("      };\n", a) + len("      };\n")
    return s[:a] + s[b:]


edit("lib/core/api/collider_api.dart", api)
print("round 32 applied")

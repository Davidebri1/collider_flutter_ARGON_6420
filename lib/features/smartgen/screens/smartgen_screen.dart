import '../../../core/drafts.dart';
import 'package:material_ui/material_ui.dart';
import '../../../core/vision/vision_kit.dart';
import '../smartgen_store.dart';

/// Smart Gen — spatial workspace with Kanban Boards, Typed Custom Fields, Automation Hooks,
/// Free-Drag 2D CanvasPlane, and Autonomous Genie synthesis views.
class SmartGenScreen extends StatefulWidget {
  final VoidCallback onClose;
  final String viewMode;
  final ValueChanged<String>? onViewModeChanged;
  final int newCardTrigger;

  const SmartGenScreen({
    super.key,
    required this.onClose,
    this.viewMode = 'boards',
    this.onViewModeChanged,
    this.newCardTrigger = 0,
  });

  @override
  State<SmartGenScreen> createState() => _SmartGenScreenState();
}

class _SmartGenScreenState extends State<SmartGenScreen> {
  final TextEditingController _searchCtrl = Drafts.text('smartgen.search');
  final SmartGenStore _store = SmartGenStore.instance;
  String _q = '';
  int _tab = 0;
  late String _mode = widget.viewMode;

  static const _tabs = ['Tasks & Kanban', 'Projects', 'Reminders', 'Memory Items', 'Artifacts'];

  static const _boards = [
    ['High', 'Medium', 'Low'],
    ['Projects'],
    ['Reminders'],
    ['Memory Items'],
    ['Artifacts'],
  ];

  @override
  void initState() {
    super.initState();
    _store.addListener(_changed);
    _store.load().then((_) {
      if (!mounted) return;
      if (Uri.base.queryParameters['modal'] == 'card') {
        for (final l in _boards[_tab]) {
          final cards = _store.list(l);
          if (cards.isNotEmpty) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) _openCardModal(cards.first);
            });
            break;
          }
        }
      } else if (Uri.base.queryParameters['modal'] == 'hooks') {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted) _openHooksModal();
        });
      }
    });
  }

  @override
  void didUpdateWidget(covariant SmartGenScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.viewMode != oldWidget.viewMode) {
      _mode = widget.viewMode;
    }
    if (widget.newCardTrigger != oldWidget.newCardTrigger) {
      final defaultList = _boards[_tab].first;
      _store.add(defaultList, 'New ${_tabs[_tab].split(' ').first} item');
    }
  }

  void _setMode(String m) {
    setState(() => _mode = m);
    widget.onViewModeChanged?.call(m);
  }

  void _changed() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    _store.removeListener(_changed);
    super.dispose();
  }

  void _openCardModal(SgCard card) {
    showDialog<void>(
      context: context,
      barrierColor: const Color(0x88000000),
      builder: (_) => _CardDetailModal(card: card, store: _store, allLists: const [
        'High',
        'Medium',
        'Low',
        'Projects',
        'Reminders',
        'Memory Items',
        'Artifacts',
      ]),
    );
  }

  void _openHooksModal() {
    showDialog<void>(
      context: context,
      barrierColor: const Color(0x88000000),
      builder: (_) => _HooksModal(store: _store),
    );
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    final isMobile = size.width < 768;
    final w = VOverlay.toolWidth(context);
    return SafeArea(
      bottom: false,
      child: Padding(
        padding: EdgeInsets.fromLTRB(isMobile ? 56 : 0, 32, 0, 0),
        child: Align(
          alignment: Alignment.topCenter,
          child: SizedBox(
            width: w,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _navbar(isMobile),
                const SizedBox(height: VSpace.xs),
                SizedBox(
                  height: VOverlay.toolMaxHeight(context),
                  child: VGlass(
                    material: VMaterial.work,
                    radius: VRadius.xl,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _tabsRow(isMobile),
                        Expanded(
                          child: _buildModeBody(),
                        ),
                        _searchBar(isMobile),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildModeBody() {
    if (_mode == 'cards') {
      return _CardsView(
        key: ValueKey('cards-$_tab'),
        lists: _boards[_tab],
        store: _store,
        query: _q,
        checks: _tab == 2,
        onOpenCard: _openCardModal,
      );
    }
    if (_mode == 'canvas') {
      return _CanvasView(
        key: ValueKey('canvas-$_tab'),
        lists: _boards[_tab],
        store: _store,
        query: _q,
        onOpenCard: _openCardModal,
      );
    }
    if (_mode == 'genie') {
      return _GenieView(
        key: ValueKey('genie-$_tab'),
        store: _store,
        query: _q,
        onOpenCard: _openCardModal,
      );
    }
    return _Board(
      key: ValueKey('board-$_tab'),
      lists: _boards[_tab],
      store: _store,
      query: _q,
      checks: _tab == 2,
      onOpenCard: _openCardModal,
    );
  }

  Widget _navbar(bool isMobile) {
    final activeHooks = _store.hooks.where((h) => h.enabled).length;
    return VGlass(
      material: VMaterial.elevated,
      radius: VRadius.full,
      padding: const EdgeInsets.fromLTRB(16, 5, 5, 5),
      child: Row(
        children: [
          Expanded(
            child: Row(
              children: [
                Text(
                  'Smart Gen',
                  maxLines: 1,
                  softWrap: false,
                  overflow: TextOverflow.fade,
                  style: VType.callout(weight: FontWeight.w600),
                ),
                if (!isMobile) ...[
                  const SizedBox(width: 8),
                  VPress(
                    onTap: () {
                      final cur = _store.boardKindForTab(_tab);
                      final next = kBoardKinds[(kBoardKinds.indexOf(cur) + 1) % kBoardKinds.length];
                      _store.setBoardKindForTab(_tab, next);
                    },
                    tooltip: 'Cycle Board Kind (notebook, portfolio, corkboard, clipboard, ledger, desk, binder, slate)',
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: VColors.fillRow,
                        borderRadius: BorderRadius.circular(VRadius.full),
                        border: Border.all(color: VColors.borderSubtle, width: 0.5),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.dashboard_customize_rounded, size: 12, color: VColors.accentBlue),
                          const SizedBox(width: 4),
                          Text(
                            _store.boardKindForTab(_tab),
                            style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w600).copyWith(fontSize: 10.5),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  VPress(
                    onTap: _openHooksModal,
                    tooltip: 'Automation Hooks (when fieldChange / listEnter → setField / addLabel)',
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: VColors.fillRow,
                        borderRadius: BorderRadius.circular(VRadius.full),
                        border: Border.all(color: VColors.borderSubtle, width: 0.5),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.bolt_rounded, size: 13, color: const Color(0xFFF59E0B)),
                          const SizedBox(width: 3),
                          Text(
                            'Hooks ($activeHooks)',
                            style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w600).copyWith(fontSize: 10.5),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (!isMobile)
            for (final (id, label) in const [
              ('boards', 'Boards'),
              ('cards', 'Cards'),
              ('canvas', 'Canvas'),
              ('genie', 'Genie'),
            ])
              Padding(
                padding: const EdgeInsets.only(right: 4),
                child: VPress(
                  onTap: () => _setMode(id),
                  child: AnimatedContainer(
                    duration: VMotion.fast,
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: _mode == id ? VColors.fillActive : Colors.transparent,
                      borderRadius: BorderRadius.circular(VRadius.full),
                    ),
                    child: Text(
                      label,
                      style: VType.caption(
                        color: _mode == id ? VColors.textPrimary : VColors.textSecondary,
                        weight: _mode == id ? FontWeight.w600 : FontWeight.w500,
                      ),
                    ),
                  ),
                ),
              ),
          const SizedBox(width: 4),
          VCircleButton(
            icon: Icons.close_rounded,
            size: 28,
            tooltip: 'Close',
            onTap: widget.onClose,
          ),
        ],
      ),
    );
  }

  Widget _tabsRow(bool isMobile) => SizedBox(
        height: 44,
        child: Row(
          children: [
            Expanded(
              child: _Fade(
                axis: Axis.horizontal,
                fade: 20,
                padding: const EdgeInsets.symmetric(horizontal: VSpace.md),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    for (int i = 0; i < _tabs.length; i++)
                      VPress(
                        onTap: () => setState(() {
                          _tab = i;
                        }),
                        child: Padding(
                          padding: EdgeInsets.only(right: i == _tabs.length - 1 ? 0 : 18),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              Text(
                                _tabs[i],
                                style: VType.callout(
                                  color: i == _tab ? VColors.textPrimary : VColors.textSecondary,
                                  weight: i == _tab ? FontWeight.w600 : FontWeight.w500,
                                ),
                              ),
                              const SizedBox(height: 6),
                              AnimatedContainer(
                                duration: VMotion.base,
                                width: 16,
                                height: 3,
                                decoration: BoxDecoration(
                                  color: i == _tab ? VColors.accentBlue : Colors.transparent,
                                  borderRadius: BorderRadius.circular(VRadius.full),
                                ),
                              ),
                              const SizedBox(height: 4),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
            if (!isMobile)
              Padding(
                padding: const EdgeInsets.only(right: 12),
                child: VPress(
                  onTap: () => _store.setPaperStackStyle(!_store.paperStackStyle),
                  tooltip: 'Toggle layered Paper Stack card edges',
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _store.paperStackStyle ? VColors.fillActive : VColors.fillRow,
                      borderRadius: BorderRadius.circular(VRadius.full),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.layers_rounded,
                          size: 13,
                          color: _store.paperStackStyle ? VColors.accentBlue : VColors.textTertiary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'Paper Stack',
                          style: VType.caption(
                            color: _store.paperStackStyle ? VColors.textPrimary : VColors.textTertiary,
                            weight: FontWeight.w600,
                          ).copyWith(fontSize: 10),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
      );

  Widget _searchBar(bool isMobile) => Padding(
        padding: const EdgeInsets.fromLTRB(VSpace.sm, VSpace.xs, VSpace.sm, VSpace.sm),
        child: Align(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: isMobile ? double.infinity : 320),
            child: VSearchField(
              controller: _searchCtrl,
              hint: 'Search cards, fields & synthesis...',
              onChanged: (v) => setState(() => _q = v.trim()),
            ),
          ),
        ),
      );
}

const _listFill = Color(0x28000000);
const _cardFill = Color(0xFF1E2329);
const _cardInk = Color(0xFFEAF0F6);
const _faint = Color(0xFF9FADBC);

Color _statusColor(String status) => switch (status) {
      'done' => VColors.accentGreen,
      'doing' => const Color(0xFFF59E0B),
      _ => VColors.accentBlue,
    };

Color _labelColor(String label) => switch (label.toLowerCase()) {
      'urgent' => const Color(0xFFEF4444),
      'consensus' => const Color(0xFF3B82F6),
      'design' => const Color(0xFFA855F7),
      'research' => const Color(0xFF14B8A6),
      _ => const Color(0xFF64748B),
    };

Widget _buildCardMetadataChips(SgCard c, SmartGenStore store, {VoidCallback? onOpenModal}) {
  final status = c.status;
  final due = c.due;
  final owner = c.owner;
  final est = c.estimate;
  return Padding(
    padding: const EdgeInsets.only(top: 6),
    child: Wrap(
      spacing: 5,
      runSpacing: 4,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        // Status pill (clickable to cycle open -> doing -> done)
        VPress(
          onTap: () {
            const opts = ['open', 'doing', 'done'];
            final next = opts[(opts.indexOf(status) + 1) % opts.length];
            store.setField(c, 'status', next);
          },
          tooltip: 'Click to cycle Status (open → doing → done)',
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: _statusColor(status).withValues(alpha: 0.16),
              borderRadius: BorderRadius.circular(5),
              border: Border.all(color: _statusColor(status).withValues(alpha: 0.45), width: 0.5),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 5,
                  height: 5,
                  decoration: BoxDecoration(color: _statusColor(status), shape: BoxShape.circle),
                ),
                const SizedBox(width: 4),
                Text(
                  status.toUpperCase(),
                  style: VType.caption(color: _cardInk, weight: FontWeight.w600).copyWith(fontSize: 9),
                ),
              ],
            ),
          ),
        ),
        for (final lbl in c.labels.take(2))
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: _labelColor(lbl).withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(5),
            ),
            child: Text(
              lbl,
              style: VType.caption(color: _cardInk, weight: FontWeight.w600).copyWith(fontSize: 9),
            ),
          ),
        if (due.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
            decoration: BoxDecoration(
              color: const Color(0x18FFFFFF),
              borderRadius: BorderRadius.circular(5),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.event_rounded, size: 10, color: _faint),
                const SizedBox(width: 3),
                Text(due, style: VType.caption(color: _faint).copyWith(fontSize: 9)),
              ],
            ),
          ),
        if (owner.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
            decoration: BoxDecoration(
              color: const Color(0x14FFFFFF),
              borderRadius: BorderRadius.circular(5),
            ),
            child: Text(owner, style: VType.caption(color: _faint).copyWith(fontSize: 9)),
          ),
        if (est.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
            decoration: BoxDecoration(
              color: const Color(0x14FFFFFF),
              borderRadius: BorderRadius.circular(5),
            ),
            child: Text('${est}pt', style: VType.caption(color: _faint).copyWith(fontSize: 9)),
          ),
        if (onOpenModal != null)
          VPress(
            onTap: onOpenModal,
            tooltip: 'Open Card Fields & Details',
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
              decoration: BoxDecoration(
                color: const Color(0x18FFFFFF),
                borderRadius: BorderRadius.circular(5),
              ),
              child: const Icon(Icons.tune_rounded, size: 11, color: _faint),
            ),
          ),
      ],
    ),
  );
}

class _Board extends StatefulWidget {
  final List<String> lists;
  final SmartGenStore store;
  final String query;
  final bool checks;
  final ValueChanged<SgCard> onOpenCard;
  const _Board({
    super.key,
    required this.lists,
    required this.store,
    required this.query,
    required this.checks,
    required this.onOpenCard,
  });

  @override
  State<_Board> createState() => _BoardState();
}

class _BoardState extends State<_Board> {
  PageController? _pages;
  String? _adding;
  SgCard? _editing;
  DateTime _lastTurn = DateTime(0);
  final TextEditingController _newCtrl = Drafts.text('smartgen.new');
  final _newFocus = FocusNode();

  @override
  void dispose() {
    _pages?.dispose();
    _newFocus.dispose();
    super.dispose();
  }

  void _edge(Offset global, Rect box) {
    final p = _pages;
    if (p == null || !p.hasClients || DateTime.now().difference(_lastTurn).inMilliseconds < 650) return;
    final page = (p.page ?? 0).round();
    if (global.dx > box.right - 28 && page < widget.lists.length - 1) {
      _lastTurn = DateTime.now();
      p.animateToPage(page + 1, duration: VMotion.base, curve: Curves.easeOutCubic);
    } else if (global.dx < box.left + 28 && page > 0) {
      _lastTurn = DateTime.now();
      p.animateToPage(page - 1, duration: VMotion.base, curve: Curves.easeOutCubic);
    }
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, c) {
      final n = widget.lists.length;
      final sideBySide = n == 1 || (c.maxWidth - 24 - (n - 1) * 8) / n >= 180;
      if (sideBySide) {
        return Padding(
          padding: const EdgeInsets.fromLTRB(12, 2, 12, 0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (int i = 0; i < n; i++) ...[if (i > 0) const SizedBox(width: 8), Expanded(child: _list(widget.lists[i], c.maxHeight))],
            ],
          ),
        );
      }
      final frac = ((c.maxWidth - 40) / c.maxWidth).clamp(0.6, 1.0);
      _pages ??= PageController(viewportFraction: frac);
      return PageView.builder(
        controller: _pages,
        padEnds: false,
        itemCount: n,
        itemBuilder: (_, i) => Padding(
          padding: EdgeInsets.fromLTRB(i == 0 ? 12 : 4, 2, i == n - 1 ? 12 : 4, 0),
          child: _list(widget.lists[i], c.maxHeight),
        ),
      );
    });
  }

  Widget _list(String name, double maxH) {
    final all = widget.store.list(name);
    final q = widget.query.toLowerCase();
    final cards = q.isEmpty
        ? all
        : all
            .where((c) =>
                c.title.toLowerCase().contains(q) ||
                c.subtitle.toLowerCase().contains(q) ||
                c.status.toLowerCase().contains(q) ||
                c.labels.any((l) => l.toLowerCase().contains(q)))
            .toList();
    return Align(
      alignment: Alignment.topCenter,
      child: DragTarget<SgCard>(
        onWillAcceptWithDetails: (_) => true,
        onAcceptWithDetails: (d) => widget.store.move(d.data, name, null),
        builder: (context, over, _) => AnimatedContainer(
          duration: VMotion.fast,
          constraints: BoxConstraints(maxHeight: maxH - 10),
          decoration: BoxDecoration(
            color: over.isNotEmpty ? const Color(0x3D000000) : _listFill,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: VColors.borderSubtle, width: 0.5),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 6),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        name,
                        maxLines: 1,
                        softWrap: false,
                        overflow: TextOverflow.fade,
                        style: VType.callout(color: _cardInk, weight: FontWeight.w600),
                      ),
                    ),
                    Text(
                      '${cards.length}',
                      style: VType.caption(color: _faint, weight: FontWeight.w500),
                    ),
                  ],
                ),
              ),
              Flexible(
                child: _Fade(
                  fade: 12,
                  padding: const EdgeInsets.fromLTRB(8, 0, 8, 0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      for (final (i, c) in cards.indexed) KeyedSubtree(key: ValueKey(c.id), child: _slot(name, c, all.indexOf(c), i)),
                      if (_adding == name) KeyedSubtree(key: ValueKey('new-$name'), child: _newCard(name)),
                    ],
                  ),
                ),
              ),
              if (_adding != name)
                VPress(
                  onTap: () => setState(() {
                    _adding = name;
                    _editing = null;
                  }),
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(12, 4, 12, 10),
                    child: Row(children: [
                      const Icon(Icons.add_rounded, size: 16, color: _faint),
                      const SizedBox(width: 6),
                      Text('Add card', style: VType.callout(color: _faint, weight: FontWeight.w500)),
                    ]),
                  ),
                )
              else
                const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }

  Widget _slot(String list, SgCard c, int index, int shown) {
    return DragTarget<SgCard>(
      onWillAcceptWithDetails: (d) => d.data != c,
      onAcceptWithDetails: (d) => widget.store.move(d.data, list, index),
      builder: (context, over, _) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AnimatedContainer(
            duration: VMotion.fast,
            height: over.isNotEmpty ? 36 : 0,
            margin: EdgeInsets.only(bottom: over.isNotEmpty ? 6 : 0),
            decoration: BoxDecoration(color: const Color(0x14FFFFFF), borderRadius: BorderRadius.circular(8)),
          ),
          Padding(padding: const EdgeInsets.only(bottom: 6), child: identical(_editing, c) ? _editor(c) : _draggable(c)),
        ],
      ),
    );
  }

  Widget _draggable(SgCard c) {
    final card = _cardFace(c);
    return LayoutBuilder(builder: (context, box) {
      return LongPressDraggable<SgCard>(
        data: c,
        delay: const Duration(milliseconds: 220),
        onDragUpdate: (d) {
          final board = this.context.findRenderObject() as RenderBox?;
          if (board != null && board.hasSize) _edge(d.globalPosition, board.localToGlobal(Offset.zero) & board.size);
        },
        feedback: Material(
          type: MaterialType.transparency,
          child: Transform.rotate(angle: 0.04, child: SizedBox(width: box.maxWidth, child: card)),
        ),
        childWhenDragging: Opacity(opacity: 0.35, child: card),
        child: VPress(
          onTap: () => widget.onOpenCard(c),
          child: card,
        ),
      );
    });
  }

  Widget _cardFace(SgCard c) {
    final stacked = widget.store.paperStackStyle;
    return Container(
      padding: const EdgeInsets.fromLTRB(10, 8, 10, 9),
      decoration: BoxDecoration(
        color: _cardFill,
        borderRadius: BorderRadius.circular(9),
        border: Border.all(color: const Color(0x22FFFFFF), width: 0.6),
        boxShadow: [
          const BoxShadow(color: Color(0x40000000), blurRadius: 3, offset: Offset(0, 1)),
          if (stacked) ...const [
            BoxShadow(color: Color(0xFF171B20), offset: Offset(0, 3), blurRadius: 0, spreadRadius: -1),
            BoxShadow(color: Color(0x33FFFFFF), offset: Offset(0, 3.5), blurRadius: 0, spreadRadius: -1),
          ],
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              VPress(
                onTap: () => widget.store.update(c, done: !c.done),
                child: Padding(
                  padding: const EdgeInsets.only(top: 1, right: 7),
                  child: Icon(
                    c.done ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
                    size: 15,
                    color: c.done ? VColors.accentGreen : _faint,
                  ),
                ),
              ),
              Expanded(
                child: Text(
                  c.title,
                  style: VType.callout(color: c.done ? _faint : _cardInk, weight: FontWeight.w500).copyWith(
                    fontSize: 11,
                    height: 1.35,
                    decoration: c.done ? TextDecoration.lineThrough : null,
                    decorationColor: _faint,
                  ),
                ),
              ),
              if (c.score.isNotEmpty)
                Container(
                  margin: const EdgeInsets.only(left: 6),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: VColors.accentBlue.withValues(alpha: 0.22),
                    borderRadius: BorderRadius.circular(VRadius.full),
                  ),
                  child: Text(
                    c.score,
                    style: VType.caption(color: Colors.white, weight: FontWeight.w600).copyWith(fontSize: 9.5),
                  ),
                ),
            ],
          ),
          if (c.subtitle.isNotEmpty && c.subtitle.toLowerCase() != c.title.toLowerCase()) ...[
            const SizedBox(height: 5),
            Text(
              c.subtitle,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: VType.caption(color: _faint, weight: FontWeight.w400).copyWith(fontSize: 10.2, height: 1.3),
            ),
          ],
          _buildCardMetadataChips(c, widget.store, onOpenModal: () => widget.onOpenCard(c)),
        ],
      ),
    );
  }

  Widget _editor(SgCard c) => Container(
        padding: const EdgeInsets.fromLTRB(10, 6, 6, 6),
        decoration: BoxDecoration(color: _cardFill, borderRadius: BorderRadius.circular(8), border: Border.all(color: VColors.accentBlue, width: 1.5)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextFormField(
              initialValue: c.title,
              autofocus: true,
              maxLines: null,
              textInputAction: TextInputAction.done,
              cursorColor: _cardInk,
              style: VType.callout(color: _cardInk, weight: FontWeight.w400).copyWith(fontSize: 11, height: 18 / 13.5),
              decoration: const InputDecoration(border: InputBorder.none, isDense: true, contentPadding: EdgeInsets.symmetric(vertical: 2)),
              onChanged: (v) => widget.store.update(c, title: v),
              onFieldSubmitted: (v) {
                widget.store.update(c, title: v.trim().isEmpty ? c.title : v.trim());
                setState(() => _editing = null);
              },
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                _round(Icons.delete_outline_rounded, () {
                  widget.store.remove(c);
                  setState(() => _editing = null);
                }),
                const SizedBox(width: 6),
                _round(Icons.check_rounded, () {
                  widget.store.update(c, title: c.title.trim());
                  setState(() => _editing = null);
                }, filled: true),
              ],
            ),
          ],
        ),
      );

  Widget _newCard(String list) {
    final ctrl = _newCtrl;
    void add() {
      if (ctrl.text.trim().isEmpty) return setState(() => _adding = null);
      widget.store.add(list, ctrl.text);
      ctrl.clear();
      WidgetsBinding.instance.addPostFrameCallback((_) => _newFocus.requestFocus());
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Container(
        padding: const EdgeInsets.fromLTRB(10, 6, 6, 6),
        decoration: BoxDecoration(color: _cardFill, borderRadius: BorderRadius.circular(8), border: Border.all(color: VColors.accentBlue, width: 1.5)),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: ctrl,
                focusNode: _newFocus,
                autofocus: true,
                cursorColor: _cardInk,
                style: VType.callout(color: _cardInk, weight: FontWeight.w400).copyWith(fontSize: 11),
                decoration: const InputDecoration(border: InputBorder.none, isDense: true, contentPadding: EdgeInsets.symmetric(vertical: 4)),
                onSubmitted: (_) => add(),
              ),
            ),
            _round(Icons.close_rounded, () => setState(() => _adding = null)),
            const SizedBox(width: 6),
            _round(Icons.check_rounded, add, filled: true),
          ],
        ),
      ),
    );
  }

  Widget _round(IconData icon, VoidCallback onTap, {bool filled = false}) => VPress(
        onTap: onTap,
        child: Container(
          width: 26,
          height: 26,
          decoration: BoxDecoration(shape: BoxShape.circle, color: filled ? VColors.accentBlue : const Color(0x1FFFFFFF)),
          child: Icon(icon, size: 15, color: Colors.white),
        ),
      );
}

class _Fade extends StatefulWidget {
  final Widget child;
  final double fade;
  final EdgeInsetsGeometry padding;
  final Axis axis;
  const _Fade({required this.child, this.fade = 18, this.padding = EdgeInsets.zero, this.axis = Axis.vertical});

  @override
  State<_Fade> createState() => _FadeState();
}

class _FadeState extends State<_Fade> {
  final _c = ScrollController();
  bool _lead = false, _trail = false;

  void _update() {
    if (!_c.hasClients || !_c.position.hasContentDimensions) return;
    final p = _c.position;
    final lead = p.pixels > 0.5, trail = p.pixels < p.maxScrollExtent - 0.5;
    if (lead != _lead || trail != _trail) {
      setState(() {
        _lead = lead;
        _trail = trail;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _c.addListener(_update);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    WidgetsBinding.instance.addPostFrameCallback((_) => _update());
    final h = widget.axis == Axis.horizontal;
    return ShaderMask(
      blendMode: BlendMode.dstIn,
      shaderCallback: (rect) {
        final len = h ? rect.width : rect.height;
        final f = (widget.fade / (len <= 0 ? 1 : len)).clamp(0.0, 0.3);
        return LinearGradient(
          begin: h ? Alignment.centerLeft : Alignment.topCenter,
          end: h ? Alignment.centerRight : Alignment.bottomCenter,
          colors: [_lead ? const Color(0x00FFFFFF) : Colors.white, Colors.white, Colors.white, _trail ? const Color(0x00FFFFFF) : Colors.white],
          stops: [0, f, 1 - f, 1],
        ).createShader(rect);
      },
      child: SingleChildScrollView(
        controller: _c,
        scrollDirection: widget.axis,
        physics: const BouncingScrollPhysics(),
        padding: widget.padding,
        child: widget.child,
      ),
    );
  }
}

class _CardsView extends StatelessWidget {
  final List<String> lists;
  final SmartGenStore store;
  final String query;
  final bool checks;
  final ValueChanged<SgCard> onOpenCard;
  const _CardsView({
    super.key,
    required this.lists,
    required this.store,
    required this.query,
    required this.checks,
    required this.onOpenCard,
  });

  @override
  Widget build(BuildContext context) {
    final q = query.toLowerCase();
    final items = <(String, SgCard)>[
      for (final l in lists)
        for (final c in store.list(l))
          if (q.isEmpty ||
              c.title.toLowerCase().contains(q) ||
              c.subtitle.toLowerCase().contains(q) ||
              c.status.toLowerCase().contains(q))
            (l, c),
    ];
    return VFadeScroll(
      padding: const EdgeInsets.fromLTRB(14, 4, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (items.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 36),
              child: Text('No cards match this filter.', textAlign: TextAlign.center, style: VType.callout(color: VColors.textTertiary)),
            ),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              for (final (listName, card) in items)
                SizedBox(
                  width: 248,
                  child: VPress(
                    onTap: () => onOpenCard(card),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: _cardFill,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: VColors.borderLight, width: 0.5),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(color: VColors.fillActive, borderRadius: BorderRadius.circular(VRadius.full)),
                                child: Text(listName, style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w600).copyWith(fontSize: 11)),
                              ),
                              if (card.score.isNotEmpty) ...[
                                const SizedBox(width: 6),
                                Text(card.score, style: VType.caption(color: VColors.accentBlue, weight: FontWeight.w600)),
                              ],
                              const Spacer(),
                              VPress(
                                onTap: () => store.update(card, done: !card.done),
                                child: Icon(
                                  card.done ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
                                  size: 16,
                                  color: card.done ? VColors.accentGreen : _faint,
                                ),
                              ),
                              const SizedBox(width: 6),
                              VPress(
                                onTap: () => store.remove(card),
                                child: const Icon(Icons.close_rounded, size: 15, color: _faint),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            card.title,
                            style: VType.callout(color: card.done ? _faint : _cardInk, weight: FontWeight.w500).copyWith(
                              fontSize: 11,
                              height: 1.35,
                              decoration: card.done ? TextDecoration.lineThrough : null,
                            ),
                          ),
                          if (card.subtitle.isNotEmpty) ...[
                            const SizedBox(height: 6),
                            Text(
                              card.subtitle,
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                              style: VType.caption(color: _faint, weight: FontWeight.w400).copyWith(fontSize: 10.2, height: 1.3),
                            ),
                          ],
                          _buildCardMetadataChips(card, store, onOpenModal: () => onOpenCard(card)),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Interactive Free-Drag 2D Spatial Canvas Plane (ported from smart-gen-clone's canvas-plane.tsx).
class _CanvasView extends StatefulWidget {
  final List<String> lists;
  final SmartGenStore store;
  final String query;
  final ValueChanged<SgCard> onOpenCard;
  const _CanvasView({
    super.key,
    required this.lists,
    required this.store,
    required this.query,
    required this.onOpenCard,
  });

  @override
  State<_CanvasView> createState() => _CanvasViewState();
}

class _CanvasViewState extends State<_CanvasView> {
  String? _draggingId;

  @override
  Widget build(BuildContext context) {
    final q = widget.query.toLowerCase();
    final items = <(String, SgCard)>[
      for (final l in widget.lists)
        for (final c in widget.store.list(l))
          if (q.isEmpty || c.title.toLowerCase().contains(q) || c.subtitle.toLowerCase().contains(q)) (l, c),
    ];
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 4, 12, 4),
      child: Container(
        decoration: BoxDecoration(
          color: const Color(0x28000000),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: VColors.borderLight, width: 0.5),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Canvas Plane toolbar: HoldKind selector (tray, shelf, table, wall, spread, rack) + Auto-Arrange
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: VColors.borderSubtle, width: 0.5)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.open_with_rounded, size: 13, color: VColors.accentBlue),
                  const SizedBox(width: 6),
                  Text(
                    '2D Canvas Plane (drag cards freely)',
                    style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w600).copyWith(fontSize: 10.5),
                  ),
                  const Spacer(),
                  for (final hk in kHoldKinds)
                    Padding(
                      padding: const EdgeInsets.only(right: 4),
                      child: VPress(
                        onTap: () => widget.store.setHoldKind(hk),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                          decoration: BoxDecoration(
                            color: widget.store.holdKind == hk ? VColors.fillActive : Colors.transparent,
                            borderRadius: BorderRadius.circular(VRadius.full),
                          ),
                          child: Text(
                            hk,
                            style: VType.caption(
                              color: widget.store.holdKind == hk ? VColors.textPrimary : VColors.textTertiary,
                              weight: widget.store.holdKind == hk ? FontWeight.w600 : FontWeight.w500,
                            ).copyWith(fontSize: 10),
                          ),
                        ),
                      ),
                    ),
                  const SizedBox(width: 4),
                  VPress(
                    onTap: () => widget.store.autoArrangeCanvas(widget.lists),
                    tooltip: 'Auto-arrange cards onto grid',
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: VColors.fillRow,
                        borderRadius: BorderRadius.circular(VRadius.full),
                      ),
                      child: Text('Tidy Grid', style: VType.caption(color: VColors.textPrimary, weight: FontWeight.w600).copyWith(fontSize: 10)),
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(bottom: Radius.circular(14)),
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    CustomPaint(painter: _CanvasGridPainter()),
                    SingleChildScrollView(
                      scrollDirection: Axis.vertical,
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: SizedBox(
                          width: 960,
                          height: 680,
                          child: Stack(
                            clipBehavior: Clip.none,
                            children: [
                              for (final (idx, (listName, card)) in items.indexed)
                                Positioned(
                                  left: card.x ?? (20.0 + (idx % 3) * 244.0),
                                  top: card.y ?? (20.0 + (idx ~/ 3) * 148.0),
                                  child: GestureDetector(
                                    onPanStart: (_) => setState(() => _draggingId = card.id),
                                    onPanUpdate: (d) {
                                      final nx = (card.x ?? (20.0 + (idx % 3) * 244.0)) + d.delta.dx;
                                      final ny = (card.y ?? (20.0 + (idx ~/ 3) * 148.0)) + d.delta.dy;
                                      widget.store.setPosition(card, nx, ny, persist: false);
                                    },
                                    onPanEnd: (_) {
                                      setState(() => _draggingId = null);
                                      widget.store.setPosition(
                                        card,
                                        card.x ?? (20.0 + (idx % 3) * 244.0),
                                        card.y ?? (20.0 + (idx ~/ 3) * 148.0),
                                        persist: true,
                                      );
                                    },
                                    onTap: () => widget.onOpenCard(card),
                                    child: AnimatedScale(
                                      scale: _draggingId == card.id ? 1.03 : 1.0,
                                      duration: VMotion.fast,
                                      child: SizedBox(
                                        width: 228,
                                        child: Container(
                                          padding: const EdgeInsets.all(11),
                                          decoration: BoxDecoration(
                                            color: const Color(0xF022272B),
                                            borderRadius: BorderRadius.circular(12),
                                            border: Border.all(
                                              color: _draggingId == card.id
                                                  ? VColors.accentBlue
                                                  : (idx % 3 == 0 ? VColors.accentBlue.withValues(alpha: 0.45) : VColors.borderLight),
                                              width: _draggingId == card.id ? 1.4 : 0.75,
                                            ),
                                            boxShadow: const [BoxShadow(color: Color(0x55000000), blurRadius: 12, offset: Offset(0, 5))],
                                          ),
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Row(
                                                children: [
                                                  const Icon(Icons.drag_indicator_rounded, size: 13, color: _faint),
                                                  const SizedBox(width: 4),
                                                  Text(
                                                    listName.toUpperCase(),
                                                    style: VType.caption(color: VColors.textTertiary, weight: FontWeight.w600).copyWith(fontSize: 10),
                                                  ),
                                                  const Spacer(),
                                                  if (widget.lists.length > 1)
                                                    VPress(
                                                      onTap: () {
                                                        final nextIdx = (widget.lists.indexOf(listName) + 1) % widget.lists.length;
                                                        widget.store.move(card, widget.lists[nextIdx], null);
                                                      },
                                                      tooltip: 'Cycle list',
                                                      child: const Icon(Icons.swap_horiz_rounded, size: 14, color: _faint),
                                                    ),
                                                ],
                                              ),
                                              const SizedBox(height: 6),
                                              Text(
                                                card.title,
                                                maxLines: 2,
                                                overflow: TextOverflow.ellipsis,
                                                style: VType.callout(color: _cardInk, weight: FontWeight.w500).copyWith(fontSize: 11, height: 1.35),
                                              ),
                                              if (card.subtitle.isNotEmpty) ...[
                                                const SizedBox(height: 4),
                                                Text(
                                                  card.subtitle,
                                                  maxLines: 2,
                                                  overflow: TextOverflow.ellipsis,
                                                  style: VType.caption(color: _faint).copyWith(fontSize: 10),
                                                ),
                                              ],
                                              _buildCardMetadataChips(card, widget.store, onOpenModal: () => widget.onOpenCard(card)),
                                            ],
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CanvasGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()..color = const Color(0x18FFFFFF);
    const step = 24.0;
    for (double x = 16; x < size.width; x += step) {
      for (double y = 16; y < size.height; y += step) {
        canvas.drawCircle(Offset(x, y), 1.0, p);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _GenieView extends StatelessWidget {
  final SmartGenStore store;
  final String query;
  final ValueChanged<SgCard> onOpenCard;
  const _GenieView({super.key, required this.store, required this.query, required this.onOpenCard});

  @override
  Widget build(BuildContext context) {
    const allLists = ['High', 'Medium', 'Low', 'Projects', 'Reminders', 'Memory Items', 'Artifacts'];
    final q = query.toLowerCase();
    final items = <(String, SgCard)>[
      for (final l in allLists)
        for (final c in store.list(l))
          if (q.isEmpty || c.title.toLowerCase().contains(q) || c.subtitle.toLowerCase().contains(q)) (l, c),
    ];
    return VFadeScroll(
      padding: const EdgeInsets.fromLTRB(14, 4, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            margin: const EdgeInsets.only(bottom: 10),
            decoration: BoxDecoration(
              color: VColors.fillRow,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: VColors.borderLight, width: 0.5),
            ),
            child: Row(
              children: [
                const Icon(Icons.auto_awesome_rounded, size: 17, color: VColors.accentBlue),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Autonomous synthesis from your Collider sessions (${items.length} active items)',
                    maxLines: 1,
                    softWrap: false,
                    overflow: TextOverflow.fade,
                    style: VType.callout(weight: FontWeight.w500).copyWith(fontSize: 11),
                  ),
                ),
                const SizedBox(width: 8),
                VPress(
                  onTap: () => store.syncAutonomousCards(),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(color: VColors.fillActive, borderRadius: BorderRadius.circular(VRadius.full)),
                    child: Text('Sync', style: VType.caption(color: Colors.white, weight: FontWeight.w600)),
                  ),
                ),
              ],
            ),
          ),
          for (final (listName, card) in items)
            VPress(
              onTap: () => onOpenCard(card),
              child: Container(
                margin: const EdgeInsets.only(bottom: 6),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
                decoration: BoxDecoration(
                  color: _cardFill,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(color: VColors.fillRow, borderRadius: BorderRadius.circular(VRadius.full)),
                      child: Text(listName, style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w600).copyWith(fontSize: 11)),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            card.title,
                            maxLines: 2,
                            softWrap: true,
                            overflow: TextOverflow.fade,
                            style: VType.callout(color: _cardInk, weight: FontWeight.w500).copyWith(fontSize: 11),
                          ),
                          if (card.subtitle.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 2),
                              child: Text(
                                card.subtitle,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: VType.caption(color: _faint).copyWith(fontSize: 10),
                              ),
                            ),
                        ],
                      ),
                    ),
                    if (listName != 'High')
                      VPress(
                        onTap: () => store.move(card, 'High', 0),
                        tooltip: 'Promote to High',
                        child: const Padding(
                          padding: EdgeInsets.only(left: 8),
                          child: Icon(Icons.arrow_upward_rounded, size: 16, color: VColors.accentBlue),
                        ),
                      ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// Full Card Detail Modal with Typed Custom Fields (ported from smart-gen-clone's card-fields.tsx & field-input.tsx).
class _CardDetailModal extends StatefulWidget {
  final SgCard card;
  final SmartGenStore store;
  final List<String> allLists;
  const _CardDetailModal({required this.card, required this.store, required this.allLists});

  @override
  State<_CardDetailModal> createState() => _CardDetailModalState();
}

class _CardDetailModalState extends State<_CardDetailModal> {
  late final TextEditingController _titleCtrl = TextEditingController(text: widget.card.title);
  late final TextEditingController _descCtrl = TextEditingController(text: widget.card.subtitle);
  late final TextEditingController _dueCtrl = TextEditingController(text: widget.card.due);
  late final TextEditingController _ownerCtrl = TextEditingController(text: widget.card.owner);
  late final TextEditingController _estCtrl = TextEditingController(text: widget.card.estimate);
  late final TextEditingController _linkCtrl = TextEditingController(text: widget.card.link);

  static const _availableLabels = ['Urgent', 'Consensus', 'Design', 'Research', 'Task'];

  @override
  void dispose() {
    _titleCtrl.dispose();
    _descCtrl.dispose();
    _dueCtrl.dispose();
    _ownerCtrl.dispose();
    _estCtrl.dispose();
    _linkCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.card;
    final currentList = widget.store.listOfCard(c) ?? 'High';
    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 28),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520, maxHeight: 620),
        child: VGlass(
          material: VMaterial.elevated,
          radius: VRadius.xl,
          padding: const EdgeInsets.all(18),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 3),
                      decoration: BoxDecoration(color: VColors.fillActive, borderRadius: BorderRadius.circular(VRadius.full)),
                      child: Text(currentList, style: VType.caption(color: Colors.white, weight: FontWeight.w600)),
                    ),
                    const SizedBox(width: 8),
                    Text('Smart Gen Card Fields', style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w600)),
                    const Spacer(),
                    VCircleButton(
                      icon: Icons.delete_outline_rounded,
                      size: 28,
                      tooltip: 'Delete card',
                      onTap: () {
                        widget.store.remove(c);
                        Navigator.of(context).pop();
                      },
                    ),
                    const SizedBox(width: 6),
                    VCircleButton(
                      icon: Icons.close_rounded,
                      size: 28,
                      tooltip: 'Close',
                      onTap: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _titleCtrl,
                  style: VType.callout(color: Colors.white, weight: FontWeight.w600).copyWith(fontSize: 14),
                  decoration: InputDecoration(
                    labelText: 'Title',
                    labelStyle: VType.caption(color: _faint),
                    filled: true,
                    fillColor: _cardFill,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                    isDense: true,
                  ),
                  onChanged: (v) => widget.store.update(c, title: v),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _descCtrl,
                  maxLines: 3,
                  style: VType.caption(color: _cardInk).copyWith(fontSize: 12),
                  decoration: InputDecoration(
                    labelText: 'Description / Synthesis Context',
                    labelStyle: VType.caption(color: _faint),
                    filled: true,
                    fillColor: _cardFill,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                    isDense: true,
                  ),
                  onChanged: (v) => widget.store.update(c, subtitle: v),
                ),
                const SizedBox(height: 12),
                Text('TYPED FIELDS', style: VType.caption(color: VColors.textTertiary, weight: FontWeight.w600).copyWith(fontSize: 10)),
                const SizedBox(height: 6),
                // Status + Done row
                Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                        decoration: BoxDecoration(color: _cardFill, borderRadius: BorderRadius.circular(10)),
                        child: Row(
                          children: [
                            Text('Status:', style: VType.caption(color: _faint, weight: FontWeight.w600)),
                            const SizedBox(width: 8),
                            for (final st in const ['open', 'doing', 'done'])
                              Padding(
                                padding: const EdgeInsets.only(right: 4),
                                child: VPress(
                                  onTap: () {
                                    setState(() {
                                      widget.store.setField(c, 'status', st);
                                    });
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                                    decoration: BoxDecoration(
                                      color: c.status == st ? _statusColor(st).withValues(alpha: 0.28) : Colors.transparent,
                                      borderRadius: BorderRadius.circular(6),
                                      border: Border.all(
                                        color: c.status == st ? _statusColor(st) : VColors.borderSubtle,
                                        width: 0.6,
                                      ),
                                    ),
                                    child: Text(
                                      st,
                                      style: VType.caption(
                                        color: c.status == st ? Colors.white : _faint,
                                        weight: FontWeight.w600,
                                      ).copyWith(fontSize: 10),
                                    ),
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    VPress(
                      onTap: () {
                        setState(() {
                          widget.store.setField(c, 'done', !c.done);
                        });
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
                        decoration: BoxDecoration(color: _cardFill, borderRadius: BorderRadius.circular(10)),
                        child: Row(
                          children: [
                            Icon(
                              c.done ? Icons.check_box_rounded : Icons.check_box_outline_blank_rounded,
                              size: 16,
                              color: c.done ? VColors.accentGreen : _faint,
                            ),
                            const SizedBox(width: 6),
                            Text('Done', style: VType.caption(color: Colors.white, weight: FontWeight.w600)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _fieldBox(
                        label: 'Due (YYYY-MM-DD)',
                        controller: _dueCtrl,
                        icon: Icons.event_rounded,
                        onChanged: (v) => widget.store.setField(c, 'due', v.trim()),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _fieldBox(
                        label: 'Person (@handle)',
                        controller: _ownerCtrl,
                        icon: Icons.person_outline_rounded,
                        onChanged: (v) => widget.store.setField(c, 'owner', v.trim()),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _fieldBox(
                        label: 'Estimate (pts)',
                        controller: _estCtrl,
                        icon: Icons.tag_rounded,
                        onChanged: (v) => widget.store.setField(c, 'estimate', v.trim()),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _fieldBox(
                        label: 'URL (https://...)',
                        controller: _linkCtrl,
                        icon: Icons.link_rounded,
                        onChanged: (v) => widget.store.setField(c, 'link', v.trim()),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text('LABELS', style: VType.caption(color: VColors.textTertiary, weight: FontWeight.w600).copyWith(fontSize: 10)),
                const SizedBox(height: 6),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: [
                    for (final lbl in _availableLabels)
                      VPress(
                        onTap: () {
                          setState(() {
                            final next = List<String>.from(c.labels);
                            if (next.contains(lbl)) {
                              next.remove(lbl);
                            } else {
                              next.add(lbl);
                            }
                            widget.store.update(c, labels: next);
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                          decoration: BoxDecoration(
                            color: c.labels.contains(lbl) ? _labelColor(lbl).withValues(alpha: 0.35) : _cardFill,
                            borderRadius: BorderRadius.circular(VRadius.full),
                            border: Border.all(
                              color: c.labels.contains(lbl) ? _labelColor(lbl) : VColors.borderSubtle,
                              width: 0.7,
                            ),
                          ),
                          child: Text(
                            lbl,
                            style: VType.caption(
                              color: c.labels.contains(lbl) ? Colors.white : _faint,
                              weight: FontWeight.w600,
                            ).copyWith(fontSize: 10.5),
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 12),
                Text('MOVE TO LIST (TRIGGERS LIST HOOKS)', style: VType.caption(color: VColors.textTertiary, weight: FontWeight.w600).copyWith(fontSize: 10)),
                const SizedBox(height: 6),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: [
                    for (final l in widget.allLists)
                      VPress(
                        onTap: () {
                          setState(() {
                            widget.store.move(c, l, null);
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                          decoration: BoxDecoration(
                            color: currentList == l ? VColors.fillActive : _cardFill,
                            borderRadius: BorderRadius.circular(VRadius.full),
                          ),
                          child: Text(
                            l,
                            style: VType.caption(
                              color: currentList == l ? Colors.white : _faint,
                              weight: FontWeight.w600,
                            ).copyWith(fontSize: 10.5),
                          ),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _fieldBox({
    required String label,
    required TextEditingController controller,
    required IconData icon,
    required ValueChanged<String> onChanged,
  }) =>
      TextField(
        controller: controller,
        style: VType.caption(color: Colors.white).copyWith(fontSize: 11.5),
        decoration: InputDecoration(
          prefixIcon: Icon(icon, size: 14, color: _faint),
          prefixIconConstraints: const BoxConstraints(minWidth: 30, minHeight: 28),
          labelText: label,
          labelStyle: VType.caption(color: _faint).copyWith(fontSize: 10),
          filled: true,
          fillColor: _cardFill,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
          isDense: true,
        ),
        onChanged: onChanged,
      );
}

/// Automation Hooks Inspector Modal (ported from smart-gen-clone's hooks.ts).
class _HooksModal extends StatefulWidget {
  final SmartGenStore store;
  const _HooksModal({required this.store});

  @override
  State<_HooksModal> createState() => _HooksModalState();
}

class _HooksModalState extends State<_HooksModal> {
  @override
  Widget build(BuildContext context) {
    final hooks = widget.store.hooks;
    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 28),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480),
        child: VGlass(
          material: VMaterial.elevated,
          radius: VRadius.xl,
          padding: const EdgeInsets.all(18),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  const Icon(Icons.bolt_rounded, size: 18, color: const Color(0xFFF59E0B)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text('Smart Gen Automation Hooks', style: VType.callout(weight: FontWeight.w600)),
                  ),
                  VCircleButton(
                    icon: Icons.close_rounded,
                    size: 28,
                    tooltip: 'Close',
                    onTap: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'Event-driven rules triggered on fieldChange, listEnter, listLeave, or cardCreate.',
                style: VType.caption(color: _faint),
              ),
              const SizedBox(height: 12),
              for (final h in hooks)
                Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  decoration: BoxDecoration(
                    color: _cardFill,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: h.enabled ? VColors.accentBlue.withValues(alpha: 0.4) : VColors.borderSubtle, width: 0.6),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(h.name, style: VType.callout(color: Colors.white, weight: FontWeight.w600).copyWith(fontSize: 11.5)),
                            const SizedBox(height: 2),
                            Text(
                              'when: ${h.trigger} → then: ${h.action}',
                              style: VType.caption(color: _faint).copyWith(fontSize: 10),
                            ),
                          ],
                        ),
                      ),
                      VPress(
                        onTap: () {
                          setState(() {
                            widget.store.toggleHook(h);
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: h.enabled ? VColors.accentGreen.withValues(alpha: 0.22) : VColors.fillRow,
                            borderRadius: BorderRadius.circular(VRadius.full),
                          ),
                          child: Text(
                            h.enabled ? 'Active' : 'Paused',
                            style: VType.caption(color: h.enabled ? VColors.accentGreen : _faint, weight: FontWeight.w600),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

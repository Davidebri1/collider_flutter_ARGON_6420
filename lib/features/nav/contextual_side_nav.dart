import '../../core/drafts.dart';
import 'dart:math' as math;
import 'package:material_ui/material_ui.dart';
import '../../core/vision/vision_kit.dart';
import '../../models/model_def.dart';
import '../../models/ticker_item.dart';
import '../browser/models/browser_tab.dart';
import '../drawers/history_drawer.dart';

enum ActiveWorkSurface {
  chat,
  smartgen,
  market,
  themes,
  browser,
  files,
}

enum SideNavTab { local, global }

/// REQ-21 contextual panel beside the rail — the visionOS menu panel
/// (visionOS Apps 97:34752 "Home / People / Environments"): a glass panel of
/// icon-circle rows, selected row lit as a capsule; content follows the surface.
class ContextualSideNav extends StatefulWidget {
  final ActiveWorkSurface activeSurface;

  // AI Chat props
  final ModelCategory activeCategory;
  final List<String> selectedModelIds;
  final Map<String, List<ConversationHistorySession>> localHistory;
  final List<ConversationHistorySession> globalHistory;
  final String consensusRatio;
  final String consensusSummary;
  final String? expandedModelId;
  final ValueChanged<ModelCategory> onSelectCategory;
  final ValueChanged<String> onToggleModel;
  final ValueChanged<ConversationHistorySession> onSelectSession;
  final VoidCallback onOpenConsensus;
  final VoidCallback onNewConversation;
  final String chatSection; // history | models

  // Smart Gen props
  final String activeSmartGenView;
  final String activeSmartGenBoardType;
  final ValueChanged<String>? onSelectSmartGenView;
  final ValueChanged<String>? onSelectSmartGenBoardType;

  // Market props
  final String activeMarketCategory;
  final ValueChanged<String>? onSelectMarketCategory;

  // Themes props
  final String activeThemeSection;
  final ValueChanged<String>? onSelectThemeSection;

  // Browser props
  final List<BrowserTab>? browserTabs;
  final String? activeBrowserTabId;
  final ValueChanged<String>? onSelectBrowserTab;
  final ValueChanged<String>? onCloseBrowserTab;
  final VoidCallback? onClearBrowserCache;

  // Files props
  final String activeFilesCategory;
  final ValueChanged<String>? onSelectFilesCategory;

  final ValueChanged<ActiveWorkSurface>? onRequestSwitchSurface;
  final VoidCallback onPaneInteraction;
  final VoidCallback? onClose;

  const ContextualSideNav({
    super.key,
    this.activeSurface = ActiveWorkSurface.chat,
    required this.activeCategory,
    required this.selectedModelIds,
    required this.localHistory,
    required this.globalHistory,
    required this.consensusRatio,
    required this.consensusSummary,
    required this.expandedModelId,
    required this.onSelectCategory,
    required this.onToggleModel,
    required this.onSelectSession,
    required this.onOpenConsensus,
    required this.onNewConversation,
    this.chatSection = 'history',
    this.activeSmartGenView = 'cards',
    this.activeSmartGenBoardType = 'kanban',
    this.onSelectSmartGenView,
    this.onSelectSmartGenBoardType,
    this.activeMarketCategory = 'discover',
    this.onSelectMarketCategory,
    this.activeThemeSection = 'gallery',
    this.onSelectThemeSection,
    this.browserTabs,
    this.activeBrowserTabId,
    this.onSelectBrowserTab,
    this.onCloseBrowserTab,
    this.onClearBrowserCache,
    this.activeFilesCategory = 'all',
    this.onSelectFilesCategory,
    this.onRequestSwitchSurface,
    required this.onPaneInteraction,
    this.onClose,
  });

  @override
  State<ContextualSideNav> createState() => _ContextualSideNavState();
}

class _ContextualSideNavState extends State<ContextualSideNav> {
  SideNavTab _chatTab = SideNavTab.global;
  final TextEditingController _chatSearchCtrl = Drafts.text('sidenav.search');
  String _chatQuery = '';

  @override
  void dispose() {
    super.dispose();
  }

  List<ConversationHistorySession> _sessions() {
    final q = _chatQuery.toLowerCase().trim();
    final source = _local ? (widget.localHistory[widget.expandedModelId] ?? const <ConversationHistorySession>[]) : widget.globalHistory;
    if (q.isEmpty) return source;
    return source
        .where((s) =>
            s.title.toLowerCase().contains(q) ||
            s.summary.toLowerCase().contains(q) ||
            s.messages.any((m) => m.text.toLowerCase().contains(q)))
        .toList();
  }

  /// Local is the open card's own history; there is no Local without an open card.
  bool get _local => widget.expandedModelId != null && _chatTab == SideNavTab.local;

  String _cap(String s) => s.isEmpty ? s : s[0].toUpperCase() + s.substring(1);

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final isMobile = size.width < 768;
    final width = isMobile ? math.min(220.0, size.width - 104) : 260.0;
    final maxHeight = math.min(440.0, size.height * 0.52);

    // History / Search is headed by its tabs or contextual title
    final history = widget.activeSurface == ActiveWorkSurface.chat && widget.chatSection != 'models';
    final title = switch (widget.activeSurface) {
      ActiveWorkSurface.chat => widget.chatSection == 'search' ? 'Search' : (history ? 'History' : 'Models'),
      ActiveWorkSurface.smartgen => 'Smart Gen Search',
      ActiveWorkSurface.market => 'Discover Search',
      ActiveWorkSurface.themes => 'Theme Studio',
      ActiveWorkSurface.browser => 'Web Browser',
      ActiveWorkSurface.files => 'Files Search',
    };

    // Only as large as what it holds: the chat lists shrink to their rows.
    final hug = widget.activeSurface == ActiveWorkSurface.chat;
    final body = AnimatedSwitcher(
      duration: VMotion.base,
      child: KeyedSubtree(key: ValueKey('${widget.activeSurface}-${widget.chatSection}-$_local'), child: _content()),
    );
    return ConstrainedBox(
      constraints: BoxConstraints(maxHeight: maxHeight),
      child: SizedBox(
        width: width,
        height: hug ? null : maxHeight,
        child: VGlass(
          material: VMaterial.elevated,
          radius: 20,
          padding: const EdgeInsets.fromLTRB(10, 8, 8, 10),
          child: Column(
            mainAxisSize: hug ? MainAxisSize.min : MainAxisSize.max,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(
                height: 28,
                child: Row(
                  children: [
                    const SizedBox(width: 2),
                    Expanded(
                      child: history && widget.expandedModelId != null
                          ? Align(alignment: Alignment.centerLeft, child: _historyTabs())
                          : Text(title, maxLines: 1, style: VType.callout(weight: FontWeight.w600)),
                    ),
                    if (widget.onClose != null)
                      VCircleButton(icon: Icons.close_rounded, size: 26, tooltip: 'Close', onTap: widget.onClose),
                  ],
                ),
              ),
              const SizedBox(height: 6),
              hug ? Flexible(child: body) : Expanded(child: body),
            ],
          ),
        ),
      ),
    );
  }

  Widget _content() => switch (widget.activeSurface) {
        ActiveWorkSurface.chat => _chat(),
        ActiveWorkSurface.smartgen => _smartGen(),
        ActiveWorkSurface.market => _market(),
        ActiveWorkSurface.themes => _themes(),
        ActiveWorkSurface.browser => _browser(),
        ActiveWorkSurface.files => _files(),
      };

  // ---------------- AI Chat ----------------
  Widget _historyTabs() {
    Widget tab(SideNavTab t, String label) => VPress(
          onTap: () => setState(() => _chatTab = t),
          child: AnimatedContainer(
            duration: VMotion.fast,
            height: 26,
            padding: const EdgeInsets.symmetric(horizontal: 10),
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: _chatTab == t ? const Color(0x29FFFFFF) : Colors.transparent,
              borderRadius: BorderRadius.circular(VRadius.full),
            ),
            child: Text(label, style: VType.callout(weight: FontWeight.w600, color: _chatTab == t ? VColors.textPrimary : VColors.textSecondary)),
          ),
        );
    return Row(mainAxisSize: MainAxisSize.min, children: [tab(SideNavTab.local, 'Local'), tab(SideNavTab.global, 'Global')]);
  }

  Widget _chat() {
    if (widget.chatSection == 'models') return _models();
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        VSearchField(controller: _chatSearchCtrl, hint: 'Search', height: 32, onChanged: (v) => setState(() => _chatQuery = v)),
        const SizedBox(height: 4),
        Flexible(child: _history()),
      ],
    );
  }

  /// The models that can answer, by name. A tick marks the ones a question goes to.
  Widget _models() {
    final cats = [
      for (final c in ModelCategory.values)
        if (ModelRoster.forCategory(c).isNotEmpty) c,
    ];
    final cat = cats.contains(widget.activeCategory) || cats.isEmpty ? widget.activeCategory : cats.first;
    final models = ModelRoster.forCategory(cat);
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // A category appears only when it has a model that works; one category needs no tabs.
        if (cats.length > 1) ...[
          GestureDetector(
            onHorizontalDragEnd: (d) {
              final v = d.primaryVelocity ?? 0;
              if (v.abs() < 120) return;
              final next = (cats.indexOf(cat) + (v < 0 ? 1 : -1)).clamp(0, cats.length - 1);
              widget.onPaneInteraction();
              widget.onSelectCategory(cats[next]);
            },
            child: VSegmented(
              ornament: false,
              labels: [for (final c in cats) _cap(c.name)],
              active: cats.indexOf(cat),
              onSelect: (i) {
                widget.onPaneInteraction();
                widget.onSelectCategory(cats[i]);
              },
            ),
          ),
          const SizedBox(height: VSpace.xs),
        ],
        Flexible(
          child: EdgeFade(
            fadeHeight: 10,
            child: ListView(
              shrinkWrap: true,
              physics: const BouncingScrollPhysics(),
              padding: EdgeInsets.zero,
              children: [
                for (final m in models)
                  VPress(
                    onTap: () {
                      widget.onPaneInteraction();
                      widget.onToggleModel(m.id);
                    },
                    child: Container(
                      color: Colors.transparent,
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              m.label,
                              maxLines: 1,
                              softWrap: false,
                              overflow: TextOverflow.fade,
                              style: VType.callout(
                                weight: FontWeight.w500,
                                color: widget.selectedModelIds.contains(m.id) ? VColors.textPrimary : VColors.textSecondary,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          SizedBox(
                            width: 18,
                            child: widget.selectedModelIds.contains(m.id) ? const Icon(Icons.check_rounded, size: 17, color: VColors.textPrimary) : null,
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _history() {
    final sessions = _sessions();
    if (sessions.isEmpty) {
      // PRD R21: No empty box when nothing matches. A miss shows nothing, not a message.
      return const SizedBox.shrink();
    }
    return HistoryRows(sessions: sessions, onSelect: widget.onSelectSession);
  }

  // ---------------- Smart Gen ----------------
  Widget _smartGen() {
    final q = _chatQuery.toLowerCase().trim();
    const views = [
      ('cards', 'Cards', Icons.style_rounded),
      ('boards', 'Boards', Icons.dashboard_rounded),
      ('canvas', 'Canvas', Icons.crop_free_rounded),
      ('genie', 'Smart Genie', Icons.assistant_rounded),
    ];
    const boards = [
      ('kanban', 'Kanban'),
      ('calendar', 'Calendar'),
      ('notebook', 'Notebook'),
      ('photo', 'Photo Album'),
      ('storyboard', 'Storyboard'),
      ('vision', 'Vision Board'),
      ('swimlane', 'Swimlanes'),
      ('desk', 'Portfolio Desk'),
      ('us_map', 'US Map'),
      ('world_map', 'World Map'),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        VSearchField(controller: _chatSearchCtrl, hint: 'Search Smart Gen…', height: 32, onChanged: (v) => setState(() => _chatQuery = v)),
        const SizedBox(height: 6),
        Expanded(
          child: EdgeFade(
            fadeHeight: 12,
            child: ListView(
              physics: const BouncingScrollPhysics(),
              children: [
                for (final v in views)
                  if (q.isEmpty || v.$2.toLowerCase().contains(q))
                    VSidebarItem(
                      icon: v.$3,
                      label: v.$2,
                      selected: widget.activeSmartGenView == v.$1,
                      onTap: () => widget.onSelectSmartGenView?.call(v.$1),
                    ),
                const Padding(padding: EdgeInsets.symmetric(vertical: VSpace.xs), child: Divider(height: 0.5, color: VColors.borderLight)),
                for (final b in boards)
                  if (q.isEmpty || b.$2.toLowerCase().contains(q))
                    VSidebarItem(
                      icon: Icons.view_kanban_outlined,
                      label: b.$2,
                      selected: widget.activeSmartGenBoardType == b.$1,
                      onTap: () => widget.onSelectSmartGenBoardType?.call(b.$1),
                    ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // ---------------- Market ----------------
  Widget _market() {
    final q = _chatQuery.toLowerCase().trim();
    const views = [('discover', 'Discover', Icons.explore_outlined), ('gallery', 'My Gallery', Icons.collections_outlined)];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        VSearchField(controller: _chatSearchCtrl, hint: 'Search Discover…', height: 32, onChanged: (v) => setState(() => _chatQuery = v)),
        const SizedBox(height: 6),
        Expanded(
          child: ListView(
            physics: const BouncingScrollPhysics(),
            children: [
              for (final v in views)
                if (q.isEmpty || v.$2.toLowerCase().contains(q))
                  VSidebarItem(
                    icon: v.$3,
                    label: v.$2,
                    selected: widget.activeMarketCategory == v.$1,
                    onTap: () => widget.onSelectMarketCategory?.call(v.$1),
                  ),
            ],
          ),
        ),
      ],
    );
  }

  // ---------------- Themes ----------------
  Widget _themes() {
    final q = _chatQuery.toLowerCase().trim();
    const sections = [
      ('gallery', 'Theme Gallery', Icons.collections_rounded),
      ('premium', 'Premium Theme Market', Icons.workspace_premium_rounded),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        VSearchField(controller: _chatSearchCtrl, hint: 'Search Themes…', height: 32, onChanged: (v) => setState(() => _chatQuery = v)),
        const SizedBox(height: 6),
        Expanded(
          child: ListView(
            physics: const BouncingScrollPhysics(),
            children: [
              for (final s in sections)
                if (q.isEmpty || s.$2.toLowerCase().contains(q))
                  VSidebarItem(
                    icon: s.$3,
                    label: s.$2,
                    selected: widget.activeThemeSection == s.$1,
                    onTap: () => widget.onSelectThemeSection?.call(s.$1),
                  ),
            ],
          ),
        ),
      ],
    );
  }

  // ---------------- Browser ----------------
  Widget _browser() {
    final q = _chatQuery.toLowerCase().trim();
    final tabs = (widget.browserTabs ?? const <BrowserTab>[])
        .where((t) => q.isEmpty || t.title.toLowerCase().contains(q) || t.url.toLowerCase().contains(q))
        .toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        VSearchField(controller: _chatSearchCtrl, hint: 'Search Tabs…', height: 32, onChanged: (v) => setState(() => _chatQuery = v)),
        const SizedBox(height: 6),
        Expanded(
          child: tabs.isEmpty
              ? const SizedBox.shrink()
              : ListView(
                  physics: const BouncingScrollPhysics(),
                  children: [
                    for (final t in tabs)
                      VSidebarItem(
                        icon: t.isModelAssigned ? Icons.terminal_rounded : Icons.person_outline_rounded,
                        label: t.title.isEmpty ? t.url : t.title,
                        selected: widget.activeBrowserTabId == t.id,
                        onTap: () => widget.onSelectBrowserTab?.call(t.id),
                        trailing: widget.onCloseBrowserTab == null
                            ? null
                            : VCircleButton(icon: Icons.close_rounded, size: 24, tooltip: 'Close tab', onTap: () => widget.onCloseBrowserTab!(t.id)),
                      ),
                  ],
                ),
        ),
      ],
    );
  }

  // ---------------- Files ----------------
  Widget _files() {
    final q = _chatQuery.toLowerCase().trim();
    const categories = ['All', 'Documents', 'Code', 'Images', 'Audio', 'Video', 'Artifacts'];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        VSearchField(controller: _chatSearchCtrl, hint: 'Search Files…', height: 32, onChanged: (v) => setState(() => _chatQuery = v)),
        const SizedBox(height: 6),
        Expanded(
          child: ListView(
            physics: const BouncingScrollPhysics(),
            children: [
              for (final c in categories)
                if (q.isEmpty || c.toLowerCase().contains(q))
                  VSidebarItem(
                    icon: Icons.folder_rounded,
                    label: c,
                    selected: widget.activeFilesCategory.toLowerCase() == c.toLowerCase(),
                    onTap: () => widget.onSelectFilesCategory?.call(c.toLowerCase()),
                  ),
            ],
          ),
        ),
      ],
    );
  }
}

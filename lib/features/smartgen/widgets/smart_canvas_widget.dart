import 'package:flutter/material.dart';
import 'package:collider_flutter/core/theme/app_fonts.dart';
import '../theme/smartgen_glass.dart';
import '../models/smartgen_models.dart';
import '../state/smartgen_store.dart';
import 'sg_menu.dart';
import 'smart_card_widget.dart';

/// A canvas on a board: a physical container (tray, folder, notebook...)
/// that holds cards. Draggable by its header, resizable from its corner,
/// accepts card drops.
class SmartCanvasWidget extends StatefulWidget {
  final SmartCanvas canvas;
  final ComponentTemplate? template;
  final SmartGenStore store;
  final String searchQuery;
  final Size boardSize;

  const SmartCanvasWidget({
    super.key,
    required this.canvas,
    required this.template,
    required this.store,
    this.searchQuery = '',
    required this.boardSize,
  });

  @override
  State<SmartCanvasWidget> createState() => _SmartCanvasWidgetState();
}

class _SmartCanvasWidgetState extends State<SmartCanvasWidget> {
  SmartCanvas get canvas => widget.canvas;
  SmartGenStore get store => widget.store;
  bool _editingTitle = false;
  late TextEditingController _titleCtrl;

  @override
  void initState() {
    super.initState();
    _titleCtrl = TextEditingController(text: canvas.title);
  }

  @override
  void didUpdateWidget(covariant SmartCanvasWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.canvas.title != canvas.title && !_editingTitle) {
      _titleCtrl.text = canvas.title;
    }
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    super.dispose();
  }

  bool _matchesSearch(SmartCard c) {
    final q = widget.searchQuery.trim().toLowerCase();
    if (q.isEmpty) return true;
    return c.title.toLowerCase().contains(q) ||
        c.values.values
            .any((v) => (v?.toString() ?? '').toLowerCase().contains(q));
  }

  void _showMenu(Offset at) {
    SGMenu.show(
      context,
      at: at,
      items: [
        SGMenuItem(
          icon: Icons.title_rounded,
          label: 'Rename canvas',
          onTap: () => setState(() => _editingTitle = true),
        ),
        SGMenuItem(
          icon: Icons.add_rounded,
          label: 'Add card here',
          onTap: () {
            final templates = store.templatesOf(ComponentKind.card);
            if (templates.isEmpty) return;
            final tpl = templates.firstWhere(
              (t) => t.typeKey == 'note',
              orElse: () => templates.first,
            );
            store.instantiateCard(tpl.id,
                boardId: canvas.boardId,
                canvasId: canvas.id,
                title: 'New ${tpl.name}',
                x: 12,
                y: 12);
          },
        ),
        SGMenuItem(
          icon: Icons.copy_rounded,
          label: 'Duplicate canvas',
          onTap: () => store.duplicateCanvas(canvas.id),
        ),
        SGMenuItem(
          icon: Icons.delete_outline_rounded,
          label: 'Delete canvas',
          destructive: true,
          onTap: () => store.deleteCanvas(canvas.id),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final cards = store.canvasCards(canvas.id).where(_matchesSearch).toList();
    return DragTarget<String>(
      onWillAcceptWithDetails: (details) => details.data.startsWith('card:'),
      onAcceptWithDetails: (details) {
        final data = details.data;
        final cardId = data.substring(5);
        final card = store.card(cardId);
        if (card == null || card.canvasId == canvas.id) return;
        store.moveCard(cardId,
            canvasId: canvas.id,
            x: (card.x - canvas.x).clamp(0.0, canvas.width - 80),
            y: (card.y - canvas.y - 44).clamp(0.0, canvas.height - 60));
      },
      builder: (context, candidate, rejected) {
        final hovering = candidate.isNotEmpty;
        final tk = widget.template?.typeKey ?? '';
        final isNotebook = tk == 'notebook' || tk == 'diary' || tk == 'journal';
        final isPortfolio = tk == 'portfolio' || tk == 'folder';
        final fillGradient = isNotebook
            ? const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xF5FBF6EC), Color(0xF0F3EBD9)],
              )
            : isPortfolio
                ? const LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xEB3B2A1E), Color(0xEB2A1D14)],
                  )
                : LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: hovering
                        ? const [Color(0x4DFFFFFF), Color(0x26FFFFFF)]
                        : const [Color(0x2EFFFFFF), Color(0x14FFFFFF)],
                  );
        return GlassPanel(
          radius: SGGlass.rCard,
          blur: SGGlass.blurCard,
          fill: fillGradient,
          border: isPortfolio
              ? const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0x99C89B6E), Color(0x44C89B6E)],
                )
              : isNotebook
                  ? const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [Color(0x77D8CBB5), Color(0x33D8CBB5)],
                    )
                  : SGGlass.edgeStrokeSoft,
          shadows: SGGlass.cardShadow,
          child: SizedBox(
            width: canvas.width,
            height: canvas.height,
            child: Stack(
              children: [
                if (isNotebook)
                  Positioned.fill(
                    child: IgnorePointer(
                      child: CustomPaint(painter: _NotebookCanvasPainter()),
                    ),
                  ),
                Padding(
                  padding: EdgeInsets.only(left: isNotebook ? 14 : 0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _buildHeader(darkInk: isNotebook),
                      Expanded(
                        child: cards.isEmpty
                            ? Center(
                                child: Text(
                                  hovering ? 'Drop to add' : 'Drag cards here',
                                  style: AppFonts.instrumentSans(
                                      fontSize: 11,
                                      color: isNotebook
                                          ? const Color(0x884A3F35)
                                          : hovering
                                              ? Colors.white70
                                              : Colors.white
                                                  .withValues(alpha: 0.28)),
                                ),
                              )
                            : ListView.separated(
                                padding:
                                    const EdgeInsets.fromLTRB(10, 4, 10, 12),
                                itemCount: cards.length,
                                separatorBuilder: (_, __) =>
                                    const SizedBox(height: 8),
                                itemBuilder: (context, i) {
                                  final card = cards[i];
                                  return SmartCardWidget(
                                    card: card,
                                    template: store.template(card.templateId),
                                    store: store,
                                    kanbanMode: false,
                                    width: double.infinity,
                                    onMove: (delta) => store.moveCard(
                                      card.id,
                                      x: (card.x + delta.dx)
                                          .clamp(0.0, canvas.width - 80),
                                      y: (card.y + delta.dy)
                                          .clamp(0.0, canvas.height - 60),
                                    ),
                                  );
                                },
                              ),
                      ),
                    ],
                  ),
                ),
                // Resize handle (bottom-right corner).
                Positioned(
                  right: 0,
                  bottom: 0,
                  child: GestureDetector(
                    onPanUpdate: (d) => store.resizeCanvas(
                      canvas.id,
                      canvas.width + d.delta.dx,
                      canvas.height + d.delta.dy,
                    ),
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      color: Colors.transparent,
                      child: const Icon(
                        Icons.open_in_full_rounded,
                        size: 13,
                        color: Colors.white38,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildHeader({bool darkInk = false}) {
    final fg = darkInk ? SGGlass.ink : Colors.white;
    final subFg = darkInk ? SGGlass.ink3 : const Color(0x47FFFFFF);
    return GestureDetector(
      // Drag the canvas by its header.
      onPanUpdate: (d) => store.moveCanvas(
        canvas.id,
        (canvas.x + d.delta.dx).clamp(0.0, widget.boardSize.width - 120),
        (canvas.y + d.delta.dy).clamp(0.0, widget.boardSize.height - 80),
      ),
      onLongPressStart: (d) => _showMenu(d.globalPosition),
      behavior: HitTestBehavior.opaque,
      child: Container(
        padding: const EdgeInsets.fromLTRB(12, 10, 6, 8),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
                color: (darkInk ? Colors.black : Colors.white)
                    .withValues(alpha: 0.08),
                width: 0.5),
          ),
        ),
        child: Row(
          children: [
            Icon(Icons.drag_indicator_rounded, size: 13, color: subFg),
            const SizedBox(width: 6),
            Expanded(
              child: _editingTitle
                  ? GlassField(
                      controller: _titleCtrl,
                      autofocus: true,
                      style: AppFonts.instrumentSans(
                          fontSize: 12.5,
                          fontWeight: FontWeight.w600,
                          color: fg,
                          letterSpacing: -0.1),
                      onSubmitted: (_) => _saveTitle(),
                      onTapOutside: (_) => _saveTitle(),
                    )
                  : GestureDetector(
                      onTap: () => setState(() => _editingTitle = true),
                      child: Text(
                        canvas.title,
                        style: AppFonts.instrumentSans(
                            fontSize: 12.5,
                            fontWeight: FontWeight.w600,
                            color: fg,
                            letterSpacing: -0.1),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
            ),
            GestureDetector(
              onTapDown: (d) => _showMenu(d.globalPosition),
              behavior: HitTestBehavior.opaque,
              child: Padding(
                padding: const EdgeInsets.all(5),
                child: Icon(Icons.more_horiz_rounded, size: 14, color: subFg),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _saveTitle() {
    final v = _titleCtrl.text.trim();
    if (v.isNotEmpty) {
      canvas.title = v;
      store.updateCanvas(canvas);
    } else {
      _titleCtrl.text = canvas.title;
    }
    setState(() => _editingTitle = false);
  }
}

class _NotebookCanvasPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final rulePaint = Paint()
      ..color = const Color(0x227A8B9E)
      ..strokeWidth = 0.8;
    for (double y = 48; y < size.height - 14; y += 22) {
      canvas.drawLine(Offset(20, y), Offset(size.width - 12, y), rulePaint);
    }
    final marginPaint = Paint()
      ..color = const Color(0x38D96B6B)
      ..strokeWidth = 1.0;
    canvas.drawLine(
        const Offset(26, 0), Offset(26, size.height), marginPaint);
    final ringPaint = Paint()..color = const Color(0xFF6B655E);
    for (double y = 24; y < size.height - 18; y += 28) {
      canvas.drawRRect(
        RRect.fromRectAndRadius(
            Rect.fromLTWH(4, y, 10, 5), const Radius.circular(2.5)),
        ringPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

import '../../core/drafts.dart';
import 'dart:ui';
import 'package:material_ui/material_ui.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../models/model_def.dart';

class TuckedGlobalComposer extends StatefulWidget {
  final bool isSummoned;
  final List<ModelDef> availableModels;
  final Set<String> selectedModelIds;
  final Function(String modelId) onToggleModelSelection;
  final Function(String prompt) onSendPrompt;
  final VoidCallback onTuck;

  const TuckedGlobalComposer({
    super.key,
    required this.isSummoned,
    required this.availableModels,
    required this.selectedModelIds,
    required this.onToggleModelSelection,
    required this.onSendPrompt,
    required this.onTuck,
  });

  @override
  State<TuckedGlobalComposer> createState() => _TuckedGlobalComposerState();
}

class _TuckedGlobalComposerState extends State<TuckedGlobalComposer> {
  final TextEditingController _promptCtrl = Drafts.text('composer.tucked');

  void _submit() {
    final text = _promptCtrl.text.trim();
    if (text.isEmpty) return;
    widget.onSendPrompt(text);
    _promptCtrl.clear();
    widget.onTuck();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isSummoned) {
      return const SizedBox.shrink();
    }

    return GestureDetector(
      onVerticalDragEnd: (details) {
        if (details.primaryVelocity != null && details.primaryVelocity! > 200) {
          // Swiped down -> tuck away
          widget.onTuck();
        }
      },
      child: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 600),
          margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(22),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
              child: Container(
                padding: const EdgeInsets.fromLTRB(14, 8, 14, 12),
                decoration: BoxDecoration(
                  color: const Color(0x20FFFFFF), // Pure visionOS translucent frosted glass
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(
                    color: Colors.white.withOpacity(0.20),
                    width: 0.5,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.25),
                      blurRadius: 32,
                      offset: const Offset(0, -8),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Pull Handle & Tuck Indicator Arrow (swiping down tucks it away)
                    Center(
                      child: InkWell(
                        onTap: widget.onTuck,
                        borderRadius: BorderRadius.circular(10),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 3),
                          child: Column(
                            children: [
                              Container(
                                width: 36,
                                height: 3.5,
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.35),
                                  borderRadius: BorderRadius.circular(2),
                                ),
                              ),
                              const SizedBox(height: 2),
                              Icon(Icons.keyboard_arrow_down_rounded, size: 16, color: Colors.white.withOpacity(0.6)),
                            ],
                          ),
                        ),
                      ),
                    ),

                    // Model Selection Chips (Global send: deselect models -> send -> only selected receive)
                    Row(
                      children: [
                        Text(
                          "Target Models:",
                          style: GoogleFonts.instrumentSans(
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                            color: Colors.white.withOpacity(0.60),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: SingleChildScrollView(
                            scrollDirection: Axis.horizontal,
                            child: Row(
                              children: widget.availableModels.map((m) {
                                final isSelected = widget.selectedModelIds.contains(m.id);
                                return Padding(
                                  padding: const EdgeInsets.only(right: 6),
                                  child: FilterChip(
                                    selected: isSelected,
                                    label: Text(m.short),
                                    labelStyle: GoogleFonts.instrumentSans(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                      color: isSelected ? Colors.white : Colors.white60,
                                    ),
                                    backgroundColor: const Color(0x10FFFFFF),
                                    selectedColor: const Color(0x28FFFFFF),
                                    checkmarkColor: Colors.white,
                                    padding: EdgeInsets.zero,
                                    visualDensity: VisualDensity.compact,
                                    side: BorderSide(
                                      color: isSelected ? Colors.white.withOpacity(0.35) : Colors.white10,
                                      width: 0.5,
                                    ),
                                    onSelected: (_) => widget.onToggleModelSelection(m.id),
                                  ),
                                );
                              }).toList(),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),

                    // Multiline Input & Send Row
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Expanded(
                          child: Container(
                            constraints: const BoxConstraints(maxHeight: 90),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: const Color(0x18FFFFFF),
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(color: Colors.white.withOpacity(0.12), width: 0.5),
                            ),
                            child: TextField(
                              controller: _promptCtrl,
                              autofocus: true,
                              maxLines: null,
                              keyboardType: TextInputType.multiline,
                              style: GoogleFonts.instrumentSans(fontSize: 11, color: Colors.white),
                              decoration: InputDecoration(
                                hintText: "Send prompt to active models...",
                                hintStyle: GoogleFonts.instrumentSans(fontSize: 11, color: Colors.white38),
                                border: InputBorder.none,
                                isDense: true,
                                contentPadding: const EdgeInsets.symmetric(vertical: 4),
                              ),
                              onSubmitted: (_) => _submit(),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        IconButton(
                          style: IconButton.styleFrom(
                            backgroundColor: const Color(0x24FFFFFF),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                              side: BorderSide(color: Colors.white.withOpacity(0.20), width: 0.5),
                            ),
                          ),
                          icon: const Icon(Icons.send_rounded, size: 17, color: Colors.white),
                          onPressed: _submit,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

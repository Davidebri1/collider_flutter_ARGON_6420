// Collider composer.
import 'package:file_picker/file_picker.dart';
import 'package:material_ui/material_ui.dart';
import '../../core/api/collider_api.dart';
import '../../core/drafts.dart';
import '../../core/vision/vision_kit.dart';
import '../../core/voice/voice.dart';

class FloatingPrompt extends StatefulWidget {
  static final ValueNotifier<String?> attach = ValueNotifier(null);

  final bool summoned;
  final bool busy;
  final AskMode mode;
  final bool incognito;
  final ValueChanged<AskMode> onMode;
  final ValueChanged<bool> onIncognito;
  final void Function(String prompt, List<String> attachments) onSubmitPrompt;
  final VoidCallback onSummon;
  final VoidCallback onTuck;
  final String? continuingTitle;
  final VoidCallback? onNewConversation;

  final String? voice;
  final ValueChanged<bool>? onVoiceChat;
  final VoidCallback? onMic;

  const FloatingPrompt({
    super.key,
    required this.summoned,
    required this.mode,
    required this.incognito,
    required this.onMode,
    required this.onIncognito,
    required this.onSubmitPrompt,
    required this.onSummon,
    required this.onTuck,
    this.busy = false,
    this.continuingTitle,
    this.onNewConversation,
    this.voice,
    this.onVoiceChat,
    this.onMic,
  });

  @override
  State<FloatingPrompt> createState() => _FloatingPromptState();
}

class _FloatingPromptState extends State<FloatingPrompt> {
  final TextEditingController _ctrl = Drafts.text('composer');
  final FocusNode _focus = FocusNode();
  final List<String> _files = Drafts.files('composer');
  bool _options = false;

  @override
  void initState() {
    super.initState();
    FloatingPrompt.attach.addListener(_attached);
  }

  void _attached() {
    final f = FloatingPrompt.attach.value;
    if (f == null) return;
    FloatingPrompt.attach.value = null;
    if (mounted && !_files.contains(f)) setState(() => _files.add(f));
    Drafts.touch();
  }

  @override
  void didUpdateWidget(covariant FloatingPrompt old) {
    super.didUpdateWidget(old);
    if (widget.summoned && !old.summoned) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _focus.requestFocus());
    }
    if (!widget.summoned && old.summoned) _options = false;
  }

  @override
  void dispose() {
    FloatingPrompt.attach.removeListener(_attached);
    _focus.dispose();
    super.dispose();
  }

  void _submit() {
    final text = _ctrl.text.trim();
    if (text.isEmpty || widget.busy) return;
    widget.onSubmitPrompt(text, List.of(_files));
    Drafts.sent('composer');
    setState(() => _options = false);
  }

  Future<void> _attach() async {
    setState(() => _options = false);
    try {
      final r = await FilePicker.platform.pickFiles(allowMultiple: true, withData: true);
      if (r == null) return;
      for (final f in r.files) {
        if (f.bytes == null) continue;
        final saved = await ColliderApi.instance.uploadFile(f.name, f.bytes!);
        if (saved != null && mounted) setState(() => _files.add(saved));
        Drafts.touch();
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onVerticalDragEnd: (d) {
        final v = d.primaryVelocity ?? 0;
        if (v > 200 && widget.summoned) widget.onTuck();
        if (v < -200 && !widget.summoned) widget.onSummon();
      },
      child: AnimatedSize(
        duration: const Duration(milliseconds: 320),
        curve: Curves.easeOutCubic,
        alignment: Alignment.bottomCenter,
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 240),
          switchInCurve: Curves.easeOutCubic,
          transitionBuilder: (child, a) => FadeTransition(
            opacity: a,
            child: SlideTransition(position: Tween(begin: const Offset(0, 0.06), end: Offset.zero).animate(a), child: child),
          ),
          child: widget.summoned ? _open() : _tucked(),
        ),
      ),
    );
  }

  Widget _tucked() {
    return VPress(
      key: const ValueKey('tucked'),
      onTap: widget.onSummon,
      tooltip: 'Compose',
      child: const SizedBox(
        width: 72,
        height: 22,
        child: Icon(
          Icons.keyboard_arrow_up_rounded,
          size: 22,
          color: Color(0xD9FFFFFF),
          shadows: [Shadow(color: Color(0x99000000), blurRadius: 8)],
        ),
      ),
    );
  }

  Widget _open() {
    final cont = widget.continuingTitle?.trim() ?? '';
    final chosen = <Widget>[
      if (cont.isNotEmpty && widget.onNewConversation != null)
        VChip(
          label: 'Continuing: ${cont.length > 22 ? "${cont.substring(0, 21)}…" : cont}  ×',
          selected: true,
          onTap: widget.onNewConversation!,
        ),
      if (widget.mode != AskMode.chat) VChip(label: widget.mode.label, selected: true, onTap: () => widget.onMode(AskMode.chat)),
      if (widget.voice != null) VChip(label: 'Voice Chat', selected: true, onTap: () => widget.onVoiceChat?.call(false)),
      if (widget.incognito) VChip(label: 'Private', selected: true, onTap: () => widget.onIncognito(false)),
      for (final f in _files)
        VChip(
            label: () {
              final n = f.split('/').last;
              return n.length > 22 ? '${n.substring(0, 21)}…' : n;
            }(),
            selected: true,
            onTap: () {
              setState(() => _files.remove(f));
              Drafts.touch();
            }),
    ];
    return VGlass(
      key: const ValueKey('open'),
      material: VMaterial.resting,
      radius: 26,
      padding: const EdgeInsets.fromLTRB(VSpace.xs, 4, VSpace.xs, 8),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Center(
            child: VPress(
              onTap: widget.onTuck,
              child: const Padding(
                padding: EdgeInsets.symmetric(horizontal: 18, vertical: 2),
                child: Icon(Icons.keyboard_arrow_down_rounded, size: 18, color: VColors.textSecondary),
              ),
            ),
          ),
          AnimatedSize(
            duration: VMotion.base,
            curve: Curves.easeOutCubic,
            alignment: Alignment.bottomCenter,
            child: _options ? _optionRows() : const SizedBox(width: double.infinity),
          ),
          if (!_options && chosen.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Wrap(spacing: 6, runSpacing: 6, children: chosen),
            ),
          const SizedBox(height: 2),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              VCircleButton(
                icon: _options ? Icons.close_rounded : Icons.add_rounded,
                size: 34,
                selected: true,
                tooltip: 'Options',
                onTap: () => setState(() => _options = !_options),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: VRecessed(
                  radius: 17,
                  padding: const EdgeInsets.fromLTRB(14, 0, 5, 0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 8.5),
                          child: TextField(
                            controller: _ctrl,
                            focusNode: _focus,
                            minLines: 1,
                            maxLines: 5,
                            cursorColor: VColors.textPrimary,
                            textInputAction: TextInputAction.send,
                            style: VType.callout(weight: FontWeight.w500).copyWith(fontSize: 11, height: 17 / 13),
                            decoration: InputDecoration(
                              hintText: 'Enter message',
                              hintStyle: VType.callout(color: const Color(0x99FFFFFF), weight: FontWeight.w400)
                                  .copyWith(fontSize: 11, height: 17 / 13),
                              border: InputBorder.none,
                              isDense: true,
                              contentPadding: EdgeInsets.zero,
                            ),
                            onSubmitted: (_) => _submit(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: widget.voice != null && widget.onMic != null
                            ? _MicButton(
                                phase: widget.voice!,
                                busy: widget.busy,
                                onTap: () => _ctrl.text.trim().isEmpty ? widget.onMic!() : _submit(),
                              )
                            : _SendButton(busy: widget.busy, onTap: _submit),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _optionRows() {
    final cont = widget.continuingTitle?.trim() ?? '';
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (cont.isNotEmpty && widget.onNewConversation != null)
            _Option(
              icon: Icons.add_comment_outlined,
              label: 'New Conversation',
              onTap: () {
                setState(() => _options = false);
                widget.onNewConversation?.call();
              },
            ),
          _Option(icon: Icons.attach_file_rounded, label: 'Attach', onTap: _attach),
          for (final m in AskMode.values.where((m) => m != AskMode.chat))
            _Option(icon: m.icon, label: m.label, on: widget.mode == m, onTap: () => widget.onMode(widget.mode == m ? AskMode.chat : m)),
          if (widget.onVoiceChat != null && Voice.instance.supported)
            _Option(
              icon: Icons.mic_rounded,
              label: 'Voice Chat',
              on: widget.voice != null,
              onTap: () {
                setState(() => _options = false);
                widget.onVoiceChat!(widget.voice == null);
              },
            ),
          _Option(icon: Icons.visibility_off_outlined, label: 'Private', on: widget.incognito, onTap: () => widget.onIncognito(!widget.incognito)),
        ],
      ),
    );
  }
}

class _Option extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool on;
  final VoidCallback onTap;
  const _Option({required this.icon, required this.label, required this.onTap, this.on = false});

  @override
  Widget build(BuildContext context) {
    return VPress(
      onTap: onTap,
      child: AnimatedContainer(
        duration: VMotion.fast,
        height: 34,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        decoration: BoxDecoration(
          color: on ? const Color(0x24FFFFFF) : Colors.transparent,
          borderRadius: BorderRadius.circular(11),
        ),
        child: Row(
          children: [
            Icon(icon, size: 16, color: vHueFor(icon) ?? (on ? VColors.textPrimary : VColors.textSecondary)),
            const SizedBox(width: 10),
            Expanded(child: Text(label, maxLines: 1, style: VType.callout(weight: FontWeight.w500))),
            if (on) const Icon(Icons.check_rounded, size: 16, color: VColors.textPrimary),
          ],
        ),
      ),
    );
  }
}

class _MicButton extends StatelessWidget {
  final String phase;
  final bool busy;
  final VoidCallback onTap;
  const _MicButton({required this.phase, required this.busy, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final listening = phase == 'listening';
    return VPress(
      onTap: onTap,
      child: ValueListenableBuilder<double>(
        valueListenable: Voice.instance.level,
        builder: (_, level, __) => SizedBox(
          width: 26,
          height: 26,
          child: Stack(alignment: Alignment.center, clipBehavior: Clip.none, children: [
            if (listening)
              AnimatedContainer(
                duration: const Duration(milliseconds: 80),
                width: 26 + 14 * level,
                height: 26 + 14 * level,
                decoration: BoxDecoration(shape: BoxShape.circle, color: VHue.red.withValues(alpha: 0.28)),
              ),
            AnimatedContainer(
              duration: VMotion.base,
              width: 26,
              height: 26,
              decoration: BoxDecoration(color: listening ? VHue.red : VColors.fillActive, shape: BoxShape.circle),
              child: Center(
                child: busy || phase == 'thinking'
                    ? const CupertinoActivityIndicator(radius: 7, color: Colors.white)
                    : Icon(
                        phase == 'speaking' ? Icons.graphic_eq_rounded : Icons.mic_rounded,
                        size: 15,
                        color: phase == 'speaking' ? VHue.red : Colors.white,
                      ),
              ),
            ),
          ]),
        ),
      ),
    );
  }
}

class _SendButton extends StatefulWidget {
  final bool busy;
  final VoidCallback onTap;
  const _SendButton({required this.busy, required this.onTap});
  @override
  State<_SendButton> createState() => _SendButtonState();
}

class _SendButtonState extends State<_SendButton> {
  bool _down = false;
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTapDown: (_) => setState(() => _down = true),
      onTapCancel: () => setState(() => _down = false),
      onTapUp: (_) {
        setState(() => _down = false);
        widget.onTap();
      },
      child: SizedBox(
        width: 28,
        height: 26,
        child: Center(
          child: AnimatedScale(
            scale: _down ? 0.86 : 1.0,
            duration: const Duration(milliseconds: 120),
            curve: Curves.easeOutBack,
            child: AnimatedContainer(
              duration: VMotion.base,
              width: 26,
              height: 26,
              decoration: const BoxDecoration(color: VColors.fillActive, shape: BoxShape.circle),
              child: Center(
                child: AnimatedSwitcher(
                  duration: VMotion.fast,
                  child: widget.busy
                      ? const CupertinoActivityIndicator(key: ValueKey('b'), radius: 7, color: Colors.white)
                      : const Icon(Icons.arrow_upward_rounded, key: ValueKey('s'), size: 15, color: Colors.white),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

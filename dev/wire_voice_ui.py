# Made by Claude (2026-10-20). One-time edit: Voice Chat in the composer and its turn-taking in main.dart.
import os
root = os.path.join(os.path.dirname(__file__), "..")


def edit(rel, pairs):
    p = os.path.join(root, rel)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        if s.count(a) != 1:
            raise SystemExit(f"{rel}: expected one of {a!r}, found {s.count(a)}")
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s)


edit("lib/features/prompt/floating_prompt.dart", [
    ("import '../../core/vision/vision_kit.dart';\n",
     "import '../../core/vision/vision_kit.dart';\nimport '../../core/voice/voice.dart';\n"),
    ("  final String? continuingTitle;\n  final VoidCallback? onNewConversation;\n\n  const FloatingPrompt({",
     "  final String? continuingTitle;\n  final VoidCallback? onNewConversation;\n\n"
     "  /// Voice chat (Claude, 2026-10-20): null when it is off, else 'listening', 'thinking', 'speaking' or '' (waiting).\n"
     "  final String? voice;\n"
     "  final ValueChanged<bool>? onVoiceChat;\n"
     "  final VoidCallback? onMic;\n\n"
     "  const FloatingPrompt({"),
    ("    this.continuingTitle,\n    this.onNewConversation,\n  });",
     "    this.continuingTitle,\n    this.onNewConversation,\n    this.voice,\n    this.onVoiceChat,\n    this.onMic,\n  });"),
    ("      if (widget.incognito) VChip(label: 'Private', selected: true, onTap: () => widget.onIncognito(false)),\n      for (final f in _files)",
     "      if (widget.voice != null) VChip(label: 'Voice Chat', selected: true, onTap: () => widget.onVoiceChat?.call(false)),\n"
     "      if (widget.incognito) VChip(label: 'Private', selected: true, onTap: () => widget.onIncognito(false)),\n      for (final f in _files)"),
    ("                      Padding(padding: const EdgeInsets.symmetric(vertical: 4), child: _SendButton(busy: widget.busy, onTap: _submit)),",
     "                      Padding(\n"
     "                        padding: const EdgeInsets.symmetric(vertical: 4),\n"
     "                        child: widget.voice != null && widget.onMic != null\n"
     "                            ? _MicButton(phase: widget.voice!, busy: widget.busy, onTap: () => _ctrl.text.trim().isEmpty ? widget.onMic!() : _submit())\n"
     "                            : _SendButton(busy: widget.busy, onTap: _submit),\n"
     "                      ),"),
    ("            _Option(icon: m.icon, label: m.label, on: widget.mode == m, onTap: () => widget.onMode(widget.mode == m ? AskMode.chat : m)),\n",
     "            _Option(icon: m.icon, label: m.label, on: widget.mode == m, onTap: () => widget.onMode(widget.mode == m ? AskMode.chat : m)),\n"
     "          if (widget.onVoiceChat != null && Voice.instance.supported)\n"
     "            _Option(\n"
     "              icon: Icons.mic_rounded,\n"
     "              label: 'Voice Chat',\n"
     "              on: widget.voice != null,\n"
     "              onTap: () {\n"
     "                setState(() => _options = false);\n"
     "                widget.onVoiceChat!(widget.voice == null);\n"
     "              },\n"
     "            ),\n"),
    ("            Icon(icon, size: 16, color: on ? VColors.textPrimary : VColors.textSecondary),",
     "            Icon(icon, size: 16, color: vHueFor(icon) ?? (on ? VColors.textPrimary : VColors.textSecondary)),"),
    ("/// Send: clear shape, springs on press, turns into a spinner while models answer.",
     "/// Voice chat's button in place of Send: red and swelling with the voice while listening, a spinner while the\n"
     "/// models answer, sound bars while the answer is read; a tap ends listening, or stops the reading, or listens.\n"
     "class _MicButton extends StatelessWidget {\n"
     "  final String phase;\n"
     "  final bool busy;\n"
     "  final VoidCallback onTap;\n"
     "  const _MicButton({required this.phase, required this.busy, required this.onTap});\n\n"
     "  @override\n"
     "  Widget build(BuildContext context) {\n"
     "    final listening = phase == 'listening';\n"
     "    return VPress(\n"
     "      onTap: onTap,\n"
     "      child: ValueListenableBuilder<double>(\n"
     "        valueListenable: Voice.instance.level,\n"
     "        builder: (_, level, __) => SizedBox(\n"
     "          width: 26,\n"
     "          height: 26,\n"
     "          child: Stack(alignment: Alignment.center, clipBehavior: Clip.none, children: [\n"
     "            if (listening)\n"
     "              AnimatedContainer(\n"
     "                duration: const Duration(milliseconds: 80),\n"
     "                width: 26 + 14 * level,\n"
     "                height: 26 + 14 * level,\n"
     "                decoration: BoxDecoration(shape: BoxShape.circle, color: VHue.red.withValues(alpha: 0.28)),\n"
     "              ),\n"
     "            AnimatedContainer(\n"
     "              duration: VMotion.base,\n"
     "              width: 26,\n"
     "              height: 26,\n"
     "              decoration: BoxDecoration(color: listening ? VHue.red : VColors.fillActive, shape: BoxShape.circle),\n"
     "              child: Center(\n"
     "                child: busy || phase == 'thinking'\n"
     "                    ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))\n"
     "                    : Icon(phase == 'speaking' ? Icons.graphic_eq_rounded : Icons.mic_rounded, size: 15,\n"
     "                        color: phase == 'speaking' ? VHue.red : Colors.white),\n"
     "              ),\n"
     "            ),\n"
     "          ]),\n"
     "        ),\n"
     "      ),\n"
     "    );\n"
     "  }\n"
     "}\n\n"
     "/// Send: clear shape, springs on press, turns into a spinner while models answer."),
])

edit("lib/main.dart", [
    ("import 'features/documents/documents_screen.dart';\n",
     "import 'features/documents/documents_screen.dart';\nimport 'core/voice/voice.dart';\n"),
    ("  String? _docUrl; // the file Documents opens (Claude, 2026-10-20); null for a new document\n",
     "  String? _docUrl; // the file Documents opens (Claude, 2026-10-20); null for a new document\n"
     "  bool _voiceChat = false; // Voice Chat (Claude, 2026-10-20): speak, the models answer, the answer is read aloud\n"
     "  String _voicePhase = ''; // listening, thinking, speaking, or '' waiting for a tap\n"),
    ("      _busy = true;\n      _isComposerSummoned = false;\n",
     "      _busy = true;\n      _isComposerSummoned = _voiceChat; // in Voice Chat the composer stays, its button is the microphone\n"),
    ("  /// The Music Player: the music in Files, played by the music bar.\n",
     "  /// Voice Chat on or off. On, it listens at once.\n"
     "  void _setVoiceChat(bool on) {\n"
     "    setState(() {\n"
     "      _voiceChat = on;\n"
     "      _voicePhase = '';\n"
     "    });\n"
     "    if (on) {\n"
     "      _voiceTurn();\n"
     "    } else {\n"
     "      Voice.instance.cancelListening();\n"
     "      Voice.instance.stopSpeaking();\n"
     "    }\n"
     "  }\n\n"
     "  /// One turn: listen until the speaker stops, ask every model, read the consensus aloud, then listen again.\n"
     "  /// When nothing is said it waits for a tap on the microphone.\n"
     "  Future<void> _voiceTurn() async {\n"
     "    if (!_voiceChat || _voicePhase.isNotEmpty || _busy) return;\n"
     "    setState(() => _voicePhase = 'listening');\n"
     "    final said = await Voice.instance.listen();\n"
     "    if (!mounted || !_voiceChat) return;\n"
     "    if (said == null) {\n"
     "      setState(() => _voicePhase = '');\n"
     "      return;\n"
     "    }\n"
     "    setState(() => _voicePhase = 'thinking');\n"
     "    await _onSendPrompt(said);\n"
     "    if (!mounted || !_voiceChat) return;\n"
     "    final j = _currentJobId == null ? null : _jobsById[_currentJobId];\n"
     "    final answer = (j?.consensus.summary.isNotEmpty ?? false) ? j!.consensus.summary : _consensusSummary;\n"
     "    if (answer.isNotEmpty && answer != 'No answer') {\n"
     "      setState(() => _voicePhase = 'speaking');\n"
     "      await Voice.instance.speak(answer);\n"
     "    }\n"
     "    if (!mounted || !_voiceChat) return;\n"
     "    setState(() => _voicePhase = '');\n"
     "    _voiceTurn();\n"
     "  }\n\n"
     "  void _onMic() {\n"
     "    switch (_voicePhase) {\n"
     "      case 'listening':\n"
     "        Voice.instance.finishListening();\n"
     "      case 'speaking':\n"
     "        Voice.instance.stopSpeaking();\n"
     "      case '':\n"
     "        _voiceTurn();\n"
     "    }\n"
     "  }\n\n"
     "  /// The Music Player: the music in Files, played by the music bar.\n"),
    ("                        onSubmitPrompt: (text, files) => _onSendPrompt(text, files),\n",
     "                        onSubmitPrompt: (text, files) => _onSendPrompt(text, files),\n"
     "                        voice: _voiceChat ? _voicePhase : null,\n"
     "                        onVoiceChat: _setVoiceChat,\n"
     "                        onMic: _onMic,\n"),
])
print("ok")

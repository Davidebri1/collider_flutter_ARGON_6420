# Made by Claude (2026-10-21). Round 21: drafts are never wiped (see lib/core/drafts.dart).
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new, n in pairs:
        if s.count(old) != n:
            sys.exit(f"{rel}: expected {n} match(es) for {old[:70]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("lib/features/prompt/floating_prompt.dart", [
    ("import '../../core/api/collider_api.dart';\n", "import '../../core/api/collider_api.dart';\nimport '../../core/drafts.dart';\n", 1),
    ("  final TextEditingController _ctrl = TextEditingController();\n",
     "  // the words and files being written live in Drafts, not in this box, so nothing that hides the box can lose them\n"
     "  final TextEditingController _ctrl = Drafts.text('composer');\n", 1),
    ("  final List<String> _files = [];\n", "  final List<String> _files = Drafts.files('composer');\n", 1),
    ("    if (mounted && !_files.contains(f)) setState(() => _files.add(f));",
     "    if (mounted && !_files.contains(f)) setState(() => _files.add(f));\n    Drafts.touch();", 1),
    ("    _ctrl.dispose();\n", "", 1),
    ("""    widget.onSubmitPrompt(text, List.of(_files));
    _ctrl.clear();
    setState(() {
      _files.clear();
      _options = false;
    });""", """    widget.onSubmitPrompt(text, List.of(_files));
    Drafts.sent('composer');
    setState(() => _options = false);""", 1),
    ("        if (saved != null && mounted) setState(() => _files.add(saved));",
     "        if (saved != null && mounted) setState(() => _files.add(saved));\n        Drafts.touch();", 1),
    ("onTap: () => setState(() => _files.remove(f))),", "onTap: () {\n              setState(() => _files.remove(f));\n              Drafts.touch();\n            }),", 1),
])

edit("lib/features/ticker/widgets/conversation_view.dart", [
    ("import '../../../core/api/collider_api.dart';\n", "import '../../../core/api/collider_api.dart';\nimport '../../../core/drafts.dart';\n", 1),
    ("  final TextEditingController _reply = TextEditingController();\n",
     "  // the reply being written is kept per model in Drafts: closing this view or opening another keeps it (Claude, 2026-10-21)\n"
     "  late final TextEditingController _reply = Drafts.text('reply:${widget.item.modelDef.id}');\n", 1),
    ("  final List<String> _files = [];\n", "  late final List<String> _files = Drafts.files('reply:${widget.item.modelDef.id}');\n", 1),
    ("    _reply.dispose();\n", "", 1),
    ("""    _reply.clear();
    setState(() => _files.clear());""", """    Drafts.sent('reply:${widget.item.modelDef.id}');
    setState(() {});""", 1),
    ("        if (saved != null && mounted) setState(() => _files.add(saved));",
     "        if (saved != null && mounted) setState(() => _files.add(saved));\n        Drafts.touch();", 1),
    ("onTap: () => setState(() => _files.remove(f))),",
     "onTap: () {\n                setState(() => _files.remove(f));\n                Drafts.touch();\n              }),", 1),
])

edit("lib/features/market/screens/market_screen.dart", [
    ("import '../../../core/api/collider_api.dart';\n", "import '../../../core/api/collider_api.dart';\nimport '../../../core/drafts.dart';\n", 1),
    ("  final _text = TextEditingController();\n", "  final _text = Drafts.text('discover'); // kept when Discover closes (Claude, 2026-10-21)\n", 1),
    ("    _text.dispose();\n", "", 1),
    ("""    if (t.isEmpty) return;
    _text.clear();""", """    if (t.isEmpty) return;
    Drafts.sent('discover');""", 1),
])

edit("lib/main.dart", [
    ("  runApp(const ColliderApp());", "  await Drafts.load(); // unsent messages, as they were left (Claude, 2026-10-21)\n  runApp(const ColliderApp());", 1),
    ("void main() {\n", "Future<void> main() async {\n", 1),
    ("import 'core/media/theme_media_bundle.dart';\n", "import 'core/media/theme_media_bundle.dart';\nimport 'core/drafts.dart';\n", 1),
])
print("ok")

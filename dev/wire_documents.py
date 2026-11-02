# Made by Claude (2026-10-20). One-time edit: wires Documents into main.dart and lets Files open documents in it.
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


edit("lib/main.dart", [
    ("import 'features/files/screens/files_screen.dart';\n",
     "import 'features/files/screens/files_screen.dart';\nimport 'features/documents/documents_screen.dart';\n"),
    ("  String _filesPlace = 'home'; // where Files opens: Home, or Music when the Music Player is asked for\n",
     "  String _filesPlace = 'home'; // where Files opens: Home, or Music when the Music Player is asked for\n"
     "  String? _docUrl; // the file Documents opens (Claude, 2026-10-20); null for a new document\n"
     "  String? _docName;\n"),
    ("  /// The Music Player: the music in Files, played by the music bar.\n",
     "  /// Documents: a new document, or [url] (as the server serves it) opened for editing.\n"
     "  void _openDocument([String? url, String? name]) {\n"
     "    _docUrl = url;\n"
     "    _docName = name;\n"
     "    _requestSwitchSurface('documents');\n"
     "  }\n\n"
     "  /// The Music Player: the music in Files, played by the music bar.\n"),
    ("                onOpenFiles: () => _openDrawer('files'),\n                onOpenMusicPlayer: _openMusic,",
     "                onOpenFiles: () => _openDrawer('files'),\n                onOpenDocuments: () => _openDocument(),\n                onOpenMusicPlayer: _openMusic,"),
    ("          if (_activeDrawer == 'smartgen' || _activeDrawer == 'market' || _activeDrawer == 'files')\n            const Positioned.fill(child: VScrim()),",
     "          if (_activeDrawer == 'smartgen' || _activeDrawer == 'market' || _activeDrawer == 'files' || _activeDrawer == 'documents')\n            const Positioned.fill(child: VScrim()),"),
    ("                initialPlace: _filesPlace,\n                onClose: () => _requestSwitchSurface(null),\n              ),\n            ),\n",
     "                initialPlace: _filesPlace,\n                onClose: () => _requestSwitchSurface(null),\n"
     "                onOpenDocument: (url, name) => _openDocument(url, name),\n              ),\n            ),\n\n"
     "          if (_activeDrawer == 'documents')\n"
     "            Positioned(\n"
     "              left: desktopSurfaceLeft,\n"
     "              right: 0,\n"
     "              top: 0,\n"
     "              bottom: 78,\n"
     "              child: DocumentsScreen(\n"
     "                key: ValueKey('documents-$_docUrl'),\n"
     "                fileUrl: _docUrl,\n"
     "                fileName: _docName,\n"
     "                onClose: () => _requestSwitchSurface(null),\n"
     "              ),\n"
     "            ),\n"),
])

edit("lib/features/files/screens/files_screen.dart", [
    ("  final String initialPlace;\n  const FilesScreen({super.key, required this.onClose, this.initialPlace = 'home'});",
     "  final String initialPlace;\n\n"
     "  /// A Word, PDF, Markdown, web page or text file opens in Documents for editing (Claude, 2026-10-20).\n"
     "  final void Function(String url, String name)? onOpenDocument;\n"
     "  const FilesScreen({super.key, required this.onClose, this.initialPlace = 'home', this.onOpenDocument});"),
    ("      MusicPlayer.instance.play(song.$2, list: MusicPlayer.forTheme(song.$1), id: song.$1.id);\n      return;\n    }\n",
     "      MusicPlayer.instance.play(song.$2, list: MusicPlayer.forTheme(song.$1), id: song.$1.id);\n      return;\n    }\n"
     "    final f = v.file;\n"
     "    if (f != null && !f.asset && widget.onOpenDocument != null &&\n"
     "        RegExp(r'\\.(docx|pdf|md|markdown|html?|txt)$', caseSensitive: false).hasMatch(f.name)) {\n"
     "      widget.onOpenDocument!(f.url, f.name);\n"
     "      return;\n"
     "    }\n"),
])
print("ok")

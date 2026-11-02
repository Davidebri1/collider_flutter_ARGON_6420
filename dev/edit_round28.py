# Made by Claude (2026-10-23). Round 28: a long press on a file in Files opens it in the app's detail view, with the
# file's own actions (Play, Edit) and Send, Open, Close.
p = "lib/features/files/screens/files_screen.dart"
s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


# cells and rows take a long press
rep("""class _FileCell extends StatelessWidget {
  final ColliderFile file;
  final ColliderApi api;
  final VoidCallback onTap;
  const _FileCell({required this.file, required this.api, required this.onTap});""",
    """class _FileCell extends StatelessWidget {
  final ColliderFile file;
  final ColliderApi api;
  final VoidCallback onTap;
  final VoidCallback? onLongPress;
  const _FileCell({required this.file, required this.api, required this.onTap, this.onLongPress});""")
rep("""  @override
  Widget build(BuildContext context) => VPress(
        onTap: onTap,
        tooltip: file.name,
        child: Padding(""", """  @override
  Widget build(BuildContext context) => GestureDetector(
        onLongPress: onLongPress,
        child: VPress(
        onTap: onTap,
        tooltip: file.name,
        child: Padding(""")
rep("""            const SizedBox(height: 10),
            ..._name(),
          ]),
        ),
      );
}""", """            const SizedBox(height: 10),
            ..._name(),
          ]),
        ),
      ),
      );
}""")
rep("""class _FileRow extends StatelessWidget {
  final ColliderFile file;
  final ColliderApi api;
  final VoidCallback onTap;
  const _FileRow({required this.file, required this.api, required this.onTap});""",
    """class _FileRow extends StatelessWidget {
  final ColliderFile file;
  final ColliderApi api;
  final VoidCallback onTap;
  final VoidCallback? onLongPress;
  const _FileRow({required this.file, required this.api, required this.onTap, this.onLongPress});""")
rep("""    final meta = [file.model, _size(file.size), when].where((s) => s.isNotEmpty).join('  ·  ');
    return VPress(
      onTap: onTap,""", """    final meta = [file.model, _size(file.size), when].where((s) => s.isNotEmpty).join('  ·  ');
    return GestureDetector(
      onLongPress: onLongPress,
      child: VPress(
      onTap: onTap,""")
rep("""                Text(meta, style: _N.text(10, FontWeight.w500, _N.hint)),
              ],
            ]),
          ),
        ]),
      ),
    );
  }
}""", """                Text(meta, style: _N.text(10, FontWeight.w500, _N.hint)),
              ],
            ]),
          ),
        ]),
      ),
      ),
    );
  }
}""")
rep("""SizedBox(width: w, child: _FileCell(file: f, api: _api, onTap: () => _open(f)))""",
    """SizedBox(width: w, child: _FileCell(file: f, api: _api, onTap: () => _open(f), onLongPress: f.asset ? null : () => _detail(f)))""")
rep("""                  _FileRow(file: f, api: _api, onTap: () => _open(f)),""",
    """                  _FileRow(file: f, api: _api, onTap: () => _open(f), onLongPress: f.asset ? null : () => _detail(f)),""")

# the detail view
rep("""  // ---------------- an opened file ----------------""", """  // ---------------- a file held: the app's detail view (Claude, 2026-10-23) ----------------
  Future<void> _send(ColliderFile f) async {
    final bytes = _bytes[f.url] ??= (await _api.fileBytes(f)) ?? const [];
    if (bytes.isNotEmpty && await shareFile(bytes, f.name, _mime(f.name))) return;
    if (!await shareText(_api.fileUrl(f))) await Clipboard.setData(ClipboardData(text: _api.fileUrl(f)));
  }

  void _detail(ColliderFile f) {
    final docs = RegExp(r'\\.(docx|pdf|md|markdown|html?|txt)$', caseSensitive: false).hasMatch(f.name);
    showGeneralDialog(
      context: context,
      barrierColor: Colors.transparent,
      barrierDismissible: false,
      transitionDuration: Duration.zero,
      pageBuilder: (ctx, _, __) {
        void close() => Navigator.of(ctx).pop();
        final size = MediaQuery.sizeOf(ctx);
        final Widget content = switch (f.kind) {
          'image' => InteractiveViewer(
              minScale: 1,
              maxScale: 5,
              clipBehavior: Clip.none,
              child: DetailRaised(child: Image.network(_api.fileUrl(f), fit: BoxFit.contain, filterQuality: FilterQuality.high)),
            ),
          'text' => ConstrainedBox(
              constraints: BoxConstraints(maxHeight: size.height * 0.6),
              child: FutureBuilder<String>(
                future: _api.fileText(f),
                builder: (_, snap) => VFadeScroll(
                  fade: 30,
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 26),
                  child: SelectableText(snap.data ?? '',
                      style: VType.body().copyWith(fontSize: 14, height: 1.5, shadows: const [Shadow(color: Color(0x99000000), blurRadius: 14)])),
                ),
              ),
            ),
          _ => Column(mainAxisSize: MainAxisSize.min, children: [
              DetailRaised(radius: 12, child: _Thumb(file: f, api: _api, width: math.min(220.0, size.width * 0.5))),
              const SizedBox(height: 14),
              Text(f.name,
                  textAlign: TextAlign.center,
                  style: VType.callout().copyWith(shadows: const [Shadow(color: Color(0x99000000), blurRadius: 12)])),
            ]),
        };
        return DetailView(
          onClose: close,
          onSend: () => _send(f),
          onOpen: () => _appPicker(f),
          actions: [
            if (f.kind == 'audio' || f.kind == 'video')
              DetailAction(Icons.play_arrow_rounded, 'Play', () {
                close();
                _open(f);
              }),
            if (docs && widget.onOpenDocument != null)
              DetailAction(Icons.edit_rounded, 'Edit', () {
                close();
                widget.onOpenDocument!(f.url, f.name);
              }),
          ],
          child: content,
        );
      },
    );
  }

  // ---------------- an opened file ----------------""")

for imp in ["import 'dart:math' as math;\n", "import 'package:flutter/services.dart';\n"]:
    if imp not in s:
        s = s.replace("import 'package:material_ui/material_ui.dart';\n", "import 'package:material_ui/material_ui.dart';\n" + imp, 1)
open(p, "w", encoding="utf-8").write(s)
print("round 28 applied")

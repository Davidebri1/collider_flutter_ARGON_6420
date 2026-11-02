# Made by Claude (2026-10-20). One-time edit: text-like previews drawn on a smaller page (so the words show at
# thumbnail size), CSV drawn as a table; Files asks the server for every file's own preview.
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


edit("tools/collider_thumbs.py", [
    ("        return _page(markdown.markdown(text, extensions=[\"tables\", \"fenced_code\"]))",
     "        return _page(markdown.markdown(text, extensions=[\"tables\", \"fenced_code\"]), small=True)"),
    ("    if ext in TEXTS:\n",
     "    if ext == \".csv\":\n"
     "        import csv\n"
     "        rows = list(csv.reader(open(path, encoding=\"utf-8\", errors=\"ignore\").read(20000).splitlines()))[:30]\n"
     "        return _page(\"<table>\" + \"\".join(\"<tr>\" + \"\".join(f\"<td>{html.escape(c)}</td>\" for c in r[:10]) + \"</tr>\" for r in rows) + \"</table>\", small=True)\n"
     "    if ext in TEXTS:\n"),
    ("        return _page(f\"<pre>{html.escape(chr(10).join(lines))}</pre>\")",
     "        return _page(f\"<pre>{html.escape(chr(10).join(lines))}</pre>\", small=True)"),
    ("def _page(body):\n    with tempfile.TemporaryDirectory() as tmp:\n        p = os.path.join(tmp, \"page.html\")\n"
     "        open(p, \"w\", encoding=\"utf-8\").write(f\"<!doctype html><meta charset='utf-8'><style>{PAGE_CSS}</style><body>{body}</body>\")\n"
     "        return _edge_shot(p, 816, 1056)",
     "def _page(body, small=False):\n"
     "    \"\"\"A page of [body]. small: a narrower page, so short notes and code read at thumbnail size.\"\"\"\n"
     "    w, h = (520, 693) if small else (816, 1056)\n"
     "    css = PAGE_CSS.replace(\"width:816px;padding:56px 64px\", f\"width:{w}px;padding:{36 if small else 56}px {40 if small else 64}px\")\n"
     "    with tempfile.TemporaryDirectory() as tmp:\n        p = os.path.join(tmp, \"page.html\")\n"
     "        open(p, \"w\", encoding=\"utf-8\").write(f\"<!doctype html><meta charset='utf-8'><style>{css}</style><body>{body}</body>\")\n"
     "        return _edge_shot(p, w, h)"),
])

F = "lib/features/files/screens/files_screen.dart"
edit(F, [
    ("        child: file.kind == 'image'\n            ? (file.asset\n                ? Image.asset(file.url, fit: BoxFit.cover, errorBuilder: (_, __, ___) => tile())\n"
     "                : Image.network(api.fileUrl(file), fit: BoxFit.cover, errorBuilder: (_, __, ___) => tile()))\n            : tile(),",
     "        // The file's own picture (made by the server, collider_thumbs.py): a photo, a video's frame, a PDF's first page,\n"
     "        // a model, a document's page, a program's icon. Until it arrives, or when a file has none, the kind's tile.\n"
     "        child: file.asset\n"
     "            ? (file.kind == 'image' ? Image.asset(file.url, fit: BoxFit.cover, errorBuilder: (_, __, ___) => tile()) : tile())\n"
     "            : Image.network(\n"
     "                api.thumbUrl(file),\n"
     "                fit: file.kind == 'image' || file.kind == 'video' ? BoxFit.cover : BoxFit.contain,\n"
     "                filterQuality: FilterQuality.high,\n"
     "                frameBuilder: (_, child, frame, sync) => frame == null && !sync\n"
     "                    ? tile()\n"
     "                    : (file.kind == 'image' || file.kind == 'video' ? child : ColoredBox(color: const Color(0x14FFFFFF), child: child)),\n"
     "                errorBuilder: (_, __, ___) => tile(),\n"
     "              ),"),
])
edit("lib/core/api/collider_api.dart", [
    ("  /// Full address of a file for viewing.\n",
     "  /// The preview picture of a file in Files (the server makes and keeps it).\n"
     "  String thumbUrl(ColliderFile f) =>\n"
     "      '$_base/api/files/thumb?source=${Uri.encodeQueryComponent(f.source)}&name=${Uri.encodeQueryComponent(f.name)}&v=${f.modified.millisecondsSinceEpoch}';\n\n"
     "  /// Full address of a file for viewing.\n"),
])
print("ok")

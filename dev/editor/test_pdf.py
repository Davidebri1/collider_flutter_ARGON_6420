# Made by Claude (2026-10-20). Checks that the app's PDF writer (Edge) produces a PDF with real text, in a scratch folder.
import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
import collider_files as cf

css = open(os.path.join(os.path.dirname(__file__), "src", "print.css"), encoding="utf-8").read()
html = ("<!doctype html><html><head><meta charset='utf-8'><style>" + css + "</style></head><body>"
        "<h1>Quarterly plan</h1><p><strong>Bold start</strong> then plain text.</p>"
        "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table></body></html>")
with tempfile.TemporaryDirectory() as d:
    f = cf.Files(d)
    name = f.print_pdf("plan.pdf", html)
    p = os.path.join(d, "files", "generated", name or "")
    data = open(p, "rb").read() if name else b""
    print("name", name, "bytes", len(data), "has text font", b"/Font" in data)
    name2 = f.print_pdf("plan.pdf", html, replace=name)
    print("replaced same file", name2 == name, os.listdir(os.path.join(d, "files", "generated")))

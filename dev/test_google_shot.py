# Made by Claude (2026-10-21). The finished Google page, with its script taken out, as the in-app browser would show it.
import os, re, shutil, subprocess, tempfile

here = os.path.dirname(os.path.abspath(__file__))
edge = shutil.which("msedge") or os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe")
for k, size in (("m", "430,932"), ("d", "1280,900")):
    t = open(os.path.join(here, f"google_edge_{k}.html"), encoding="utf-8").read()
    t = re.sub(r"(?is)<script\b.*?</script>", "", t)
    t = re.sub(r"(?is)<noscript\b.*?</noscript>", "", t)
    t = t.replace("<head>", '<head><base href="https://www.google.com/">', 1)
    p = os.path.join(here, f"google_static_{k}.html")
    open(p, "w", encoding="utf-8").write(t)
    out = os.path.join(here, "editor", "test_out", f"google_static_{k}.png")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--user-data-dir=" + os.path.join(tmp, "p"),
                        f"--window-size={size}", "--screenshot=" + out, "file:///" + p.replace("\\", "/")],
                       stdin=subprocess.DEVNULL, capture_output=True, timeout=40)
    print(k, os.path.exists(out), len(t))

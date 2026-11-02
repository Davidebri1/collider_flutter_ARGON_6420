# Made by Claude (2026-10-21). A picture of the launch window as it looks, keys hidden, for checking its design.
import json, os, shutil, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "tools"))
import collider_app as app

init = app.initial()
for r in init["providers"]:
    r["key"] = "•" * 12 if r.get("key") else ""
html = app.FORM.replace("WHERE", json.dumps(app.ccfg.path(app.DATA))).replace("INITIAL", json.dumps(init))
html = html.replace("window.pywebview", "window.__nope")
edge = shutil.which("msedge") or os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe")
out_dir = os.path.join(here, "editor", "test_out")
with tempfile.TemporaryDirectory() as tmp:
    page = os.path.join(tmp, "launch.html")
    open(page, "w", encoding="utf-8").write(html)
    for name, size, scheme in (("launch_light", "560,1400", "light"), ("launch_dark", "560,1400", "dark")):
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={size}",
                        f"--force-prefers-color-scheme={scheme}" if scheme == "dark" else "--no-first-run",
                        "--blink-settings=preferredColorScheme=" + ("0" if scheme == "dark" else "1"),
                        "--user-data-dir=" + os.path.join(tmp, "p" + name), "--screenshot=" + os.path.join(out_dir, name + ".png"),
                        "file:///" + page.replace("\\", "/")], stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
        print(name, os.path.exists(os.path.join(out_dir, name + ".png")))

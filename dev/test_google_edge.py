# Made by Claude (2026-10-21). Google's results page needs script; does Edge (part of Windows) give the finished page?
import os, re, shutil, subprocess, tempfile, time

edge = shutil.which("msedge") or next((p for p in (
    os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
    os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")) if os.path.isfile(p)), None)
url = "https://www.google.com/search?q=jacksonville+weather"
for ua in (None, "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"):
    with tempfile.TemporaryDirectory() as tmp:
        t = time.time()
        args = [edge, "--headless=new", "--disable-gpu", "--no-first-run", "--user-data-dir=" + os.path.join(tmp, "p"),
                "--virtual-time-budget=4000", "--dump-dom", url]
        if ua:
            args.insert(1, "--user-agent=" + ua)
        out = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, timeout=40).stdout.decode("utf-8", "ignore")
        print("phone" if ua else "desk ", f"{time.time() - t:.1f}s bytes={len(out)} h3={len(re.findall('<h3', out))} "
              f"sorry={'/sorry/' in out or 'unusual traffic' in out.lower()} enablejs={'enablejs' in out.lower()}")
        open(os.path.join(os.path.dirname(__file__), "google_edge_" + ("m" if ua else "d") + ".html"), "w", encoding="utf-8").write(out)

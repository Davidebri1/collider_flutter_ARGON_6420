# Made by Claude (2026-10-21). Round 6: Google's results in the in-app browser.
# Google now sends its results page only to a browser that runs its script; fetched plainly it is a page that says
# "Please click here if you are not redirected". Edge (part of Windows) runs the page to the end and the finished page,
# with the script taken out, is what the in-app browser shows. Tested: phone and desktop pages, about 3 seconds.
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for: {old[:80]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("tools/collider_files.py", [
    ("import base64, gzip, json, mimetypes, os, re, time, urllib.request, urllib.error, zlib",
     "import base64, gzip, json, mimetypes, os, re, threading, time, urllib.request, urllib.error, zlib"),
    ('''def is_search_challenge(final_url, html):''',
     '''def needs_script(final_url, html):
    """True for a page that shows nothing until its script runs (Google's results). (Claude, 2026-10-21)"""
    return "google." in urlparse(final_url).netloc and "/httpservice/retry/enablejs" in html


_render_gate = threading.Semaphore(2)


def render_page(url, mobile=False):
    """The page as a browser leaves it once its script has run, by Edge (part of Windows), script taken out.
    None when Edge is not there or gives nothing. (Claude, 2026-10-21)"""
    import shutil, subprocess, tempfile
    edge = shutil.which("msedge") or next((p for p in (
        os.path.expandvars(r"%ProgramFiles(x86)%\\Microsoft\\Edge\\Application\\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\\Microsoft\\Edge\\Application\\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\\Microsoft\\Edge\\Application\\msedge.exe")) if os.path.isfile(p)), None)
    if not edge:
        return None
    with _render_gate, tempfile.TemporaryDirectory() as tmp:
        try:
            out = subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-first-run", "--user-agent=" + (UA_MOBILE if mobile else UA),
                                  "--user-data-dir=" + os.path.join(tmp, "p"), "--virtual-time-budget=4000", "--dump-dom", url],
                                 stdin=subprocess.DEVNULL, capture_output=True, timeout=30).stdout.decode("utf-8", "ignore")
        except Exception:
            return None
    if len(out) < 2000:
        return None
    out = re.sub(r"(?is)<script\\b.*?</script>", "", out)
    return re.sub(r"(?is)<noscript\\b.*?</noscript>", "", out)


def is_search_challenge(final_url, html):'''),
])

edit("tools/collider_server.py", [
    ('''            text = cfiles.decode_html(data, headers)
''',
     '''            text = cfiles.decode_html(data, headers)
            if cfiles.needs_script(final, text):
                text = cfiles.render_page(final, mobile=self._mobile()) or text
'''),
])

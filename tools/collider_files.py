"""Collider Files and in-app browser support. Made by Claude.

Files holds what the user uploaded, what the models generated and what the browser downloaded
(purchased theme packs are bundled with the app and listed by the app itself).
The browser part fetches pages here so that sites which refuse framing still render inside the app.
"""
import base64, gzip, json, mimetypes, os, re, threading, time, urllib.request, urllib.error, zlib
from urllib.parse import urlparse, unquote

SOURCES = ("uploaded", "generated", "downloaded")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")
UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
             "Version/18.0 Mobile/15E148 Safari/604.1")
TEXT_EXT = {".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".html", ".htm", ".py", ".dart", ".js", ".ts",
            ".css", ".sql", ".log", ".ini", ".toml", ".sh", ".bat", ".ps1", ".c", ".cpp", ".h", ".java", ".go", ".rs"}
KINDS = {"image": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"},
         "audio": {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"},
         "video": {".mp4", ".webm", ".mov", ".mkv"},
         "pdf": {".pdf"}}
# Shown inside the browser; everything else that is not a web page is saved as a download.
INLINE_TYPES = ("text/", "image/", "application/pdf", "application/json", "application/xml", "application/xhtml",
                "application/javascript", "audio/", "video/", "font/", "application/rss", "application/atom")


class Files:
    def __init__(self, data_dir):
        self.root = os.path.join(data_dir, "files")
        for s in SOURCES:
            os.makedirs(os.path.join(self.root, s), exist_ok=True)

    @staticmethod
    def safe_name(name):
        name = os.path.basename(str(name).replace("\\", "/")).strip() or "file"
        return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)[:120]

    def unique_path(self, source, name):
        base, ext = os.path.splitext(self.safe_name(name))
        p = os.path.join(self.root, source, base + ext)
        i = 2
        while os.path.exists(p):
            p = os.path.join(self.root, source, f"{base} ({i}){ext}")
            i += 1
        return p

    @staticmethod
    def kind(name):
        ext = os.path.splitext(name)[1].lower()
        for k, exts in KINDS.items():
            if ext in exts:
                return k
        return "text" if ext in TEXT_EXT else "file"

    # Which model made each generated file, kept beside the folders (not in them) so it is never listed.
    def _models_path(self):
        return os.path.join(self.root, ".models.json")

    def _models(self):
        try:
            return json.load(open(self._models_path(), encoding="utf-8"))
        except Exception:
            return {}

    def _remember(self, name, model):
        if not model:
            return
        m = self._models()
        m[name] = model
        tmp = self._models_path() + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=1)
        os.replace(tmp, self._models_path())

    @staticmethod
    def _guess(name, labels):
        """Files saved before the model was recorded carry its name: \"<model> - ...\" or \"... - <model>.md\"."""
        stem = os.path.splitext(name)[0]
        for lab in sorted(labels, key=len, reverse=True):
            if stem.startswith(lab + " - ") or stem.endswith(" - " + lab):
                return lab
        return ""

    def listing(self, labels=()):
        out = {}
        made_by = self._models()
        for s in SOURCES:
            d = os.path.join(self.root, s)
            rows = []
            for n in os.listdir(d):
                p = os.path.join(d, n)
                if os.path.isfile(p) and not n.startswith(".") and n.lower() != "desktop.ini":
                    st = os.stat(p)
                    rows.append({"name": n, "source": s, "size": st.st_size, "modified": st.st_mtime,
                                 "kind": self.kind(n), "url": f"/files/{s}/{urllib.request.quote(n)}",
                                 "model": (made_by.get(n) or self._guess(n, labels)) if s == "generated" else ""})
            out[s] = sorted(rows, key=lambda r: -r["modified"])
        return out

    def path_for(self, source, name):
        if source not in SOURCES:
            return None
        p = os.path.join(self.root, source, self.safe_name(unquote(name)))
        return p if os.path.isfile(p) else None

    def save_upload(self, name, b64):
        p = self.unique_path("uploaded", name)
        with open(p, "wb") as f:
            f.write(base64.b64decode(b64))
        return os.path.basename(p)

    def save_generated(self, name, text, model=""):
        p = self.unique_path("generated", name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        self._remember(os.path.basename(p), model)
        return os.path.basename(p)

    def _target(self, name, replace):
        """Where an edited document is written: over the copy the editor itself saved earlier, else a new file.
        Uploaded and downloaded originals are never written over."""
        if replace:
            p = os.path.join(self.root, "generated", self.safe_name(replace))
            if os.path.isfile(p) and os.path.splitext(p)[1].lower() == os.path.splitext(self.safe_name(name))[1].lower():
                return p
        return self.unique_path("generated", name)

    def save_bytes(self, name, b64, replace="", model=""):
        p = self._target(name, replace)
        with open(p, "wb") as f:
            f.write(base64.b64decode(b64))
        self._remember(os.path.basename(p), model)
        return os.path.basename(p)

    def save_media(self, name, data, model=""):
        """A picture or video made through fal (Discover Market), into Generated. (Claude, 2026-10-20)"""
        p = self.unique_path("generated", name)
        with open(p, "wb") as f:
            f.write(data)
        self._remember(os.path.basename(p), model)
        return os.path.basename(p)

    def print_pdf(self, name, html, replace="", model=""):
        """Writes a document as PDF with Microsoft Edge (part of Windows), which keeps the text real and sharp."""
        import shutil, subprocess, tempfile
        edge = shutil.which("msedge") or shutil.which("chromium") or shutil.which("chromium-browser") or next((p for p in (
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe")) if os.path.isfile(p)), None)
        if not edge:
            return None
        with tempfile.TemporaryDirectory() as tmp:
            src, out = os.path.join(tmp, "page.html"), os.path.join(tmp, "page.pdf")
            with open(src, "w", encoding="utf-8") as f:
                f.write(html)
            subprocess.run([edge, *_SANDBOX, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
                            "--user-data-dir=" + os.path.join(tmp, "profile"), "--print-to-pdf=" + out,
                            "file:///" + src.replace("\\", "/")],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=90, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if not os.path.isfile(out) or os.path.getsize(out) == 0:
                return None
            p = self._target(name, replace)
            shutil.copyfile(out, p)
        self._remember(os.path.basename(p), model)
        return os.path.basename(p)

    def save_download(self, name, data):
        p = self.unique_path("downloaded", name)
        with open(p, "wb") as f:
            f.write(data)
        return os.path.basename(p)

    def attachment_text(self, names, limit=6000):
        """Text of uploaded files, for the models. Files that are not text are named only."""
        parts = []
        for n in names or []:
            p = self.path_for("uploaded", n)
            if not p:
                continue
            if self.kind(n) == "text":
                try:
                    body = open(p, encoding="utf-8", errors="ignore").read(limit)
                    parts.append(f"--- {n} ---\n{body}")
                    continue
                except Exception:
                    pass
            parts.append(f"--- {n} --- (attached; its contents are not text)")
        return ("Attached files:\n\n" + "\n\n".join(parts)) if parts else ""


def fetch(url, method="GET", body=None, content_type=None, timeout=25, mobile=False):
    """Returns (status, final_url, headers, data). HTTP error pages are returned, not raised."""
    headers = {"User-Agent": UA_MOBILE if mobile else UA, "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=body if method != "GET" else None, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        r = e
    data = r.read()
    enc = (r.headers.get("Content-Encoding") or "").lower()
    try:
        if enc == "gzip":
            data = gzip.decompress(data)
        elif enc == "deflate":
            data = zlib.decompress(data, -zlib.MAX_WBITS) if not data.startswith(b"\x78") else zlib.decompress(data)
    except Exception:
        pass
    return getattr(r, "status", None) or r.getcode(), r.geturl(), r.headers, data


SOFT_REDIRECT = re.compile(
    r"""(?:location(?:\.href)?\s*=|location\.(?:replace|assign)\()\s*["'](https?://[^"']+)["']"""
    r"""|http-equiv=["']?refresh["']?[^>]*content=["']\s*\d+\s*;\s*url=([^"'>]+)""", re.I)


def fetch_page(url, method="GET", body=None, content_type=None, mobile=False):
    """fetch(), then follow pages that only exist to send the browser somewhere else."""
    from urllib.parse import urlparse, parse_qs, urljoin
    for _ in range(4):
        q = urlparse(url)
        if q.netloc.endswith("duckduckgo.com") and q.path.startswith("/l/"):
            target = (parse_qs(q.query).get("uddg") or [""])[0]
            if target:
                url, method, body = target, "GET", None
                continue
        code, final, headers, data = fetch(url, method, body, content_type, mobile=mobile)
        if "html" in (headers.get("Content-Type") or "").lower() and len(data) < 6000:
            m = SOFT_REDIRECT.search(data.decode("utf-8", "ignore"))
            if m:
                url, method, body = urljoin(final, (m.group(1) or m.group(2)).strip()), "GET", None
                continue
        return code, final, headers, data
    return fetch(url, mobile=mobile)


def needs_script(final_url, html):
    """True for a page that shows nothing until its script runs (Google's results). (Claude, 2026-10-21)"""
    return "google." in urlparse(final_url).netloc and "/httpservice/retry/enablejs" in html


_render_gate = threading.Semaphore(2)
# Chromium in a Linux container (Collider online) runs without its sandbox (Claude, 2026-10-23).
_SANDBOX = [] if os.name == "nt" else ["--no-sandbox", "--disable-dev-shm-usage"]


def render_page(url, mobile=False):
    """The page as a browser leaves it once its script has run, by Edge (part of Windows), script taken out.
    None when Edge is not there or gives nothing. (Claude, 2026-10-21)"""
    import shutil, subprocess, tempfile
    edge = shutil.which("msedge") or shutil.which("chromium") or shutil.which("chromium-browser") or next((p for p in (
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe")) if os.path.isfile(p)), None)
    if not edge:
        return None
    with _render_gate, tempfile.TemporaryDirectory() as tmp:
        try:
            out = subprocess.run([edge, *_SANDBOX, "--headless=new", "--disable-gpu", "--no-first-run", "--user-agent=" + (UA_MOBILE if mobile else UA),
                                  "--user-data-dir=" + os.path.join(tmp, "p"), "--virtual-time-budget=4000", "--dump-dom", url],
                                 stdin=subprocess.DEVNULL, capture_output=True, timeout=30).stdout.decode("utf-8", "ignore")
        except Exception:
            return None
    if len(out) < 2000:
        return None
    out = re.sub(r"(?is)<script\b.*?</script>", "", out)
    return re.sub(r"(?is)<noscript\b.*?</noscript>", "", out)


def is_search_challenge(final_url, html):
    """True when the search engine sent a puzzle instead of results."""
    return urlparse(final_url).netloc.endswith("duckduckgo.com") and ("anomaly-modal" in html or "bots use DuckDuckGo" in html)


def search_query(final_url, body=None):
    from urllib.parse import parse_qs
    q = parse_qs(urlparse(final_url).query).get("q")
    if not q and body:
        q = parse_qs(body.decode("utf-8", "ignore")).get("q")
    return (q or [""])[0]


def results_page(query, results):
    """A plain results page: the search box, then each result's title, site and excerpt."""
    import html as h

    def excerpt(text):
        # the excerpt as plain words: no markdown marks, one run of text
        return re.sub(r"\s+", " ", re.sub(r"[#*`|>]+|\[|\]\([^)]*\)", " ", text or "")).strip()[:220]

    rows = "".join(
        f'<div class="r"><a href="{h.escape(r["url"], True)}">{h.escape(r.get("title") or r["url"])}</a>'
        f'<div class="u">{h.escape(urlparse(r["url"]).netloc)}</div><p>{h.escape(excerpt(r.get("content")))}</p></div>'
        for r in results if r.get("url"))
    return ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{h.escape(query)}</title><style>'
            'body{margin:0;padding:14px 16px;font:15px/1.45 system-ui,"Segoe UI",sans-serif;color:#222;background:#f7f7f7}'
            'form{display:flex;margin:0 0 14px}input{flex:1;min-width:0;font:inherit;padding:10px 12px;border:1px solid #d0d0d0;border-radius:6px;background:#fff}'
            '.r{background:#fff;border-radius:8px;padding:12px 14px;margin:0 0 10px}.r a{color:#1a3fb0;font-size:17px;text-decoration:none}'
            '.u{color:#20692b;font-size:13px;margin:2px 0 4px;overflow-wrap:anywhere}.r p{margin:0;color:#444}</style></head><body>'
            f'<form action="https://www.bing.com/search" method="get"><input name="q" value="{h.escape(query, True)}"></form>'
            f'{rows}</body></html>')


def download_name(url, headers, data=b""):
    cd = headers.get("Content-Disposition") or ""
    ctype = (headers.get("Content-Type") or "").split(";")[0].strip().lower()
    m = re.search(r"filename\*=(?:UTF-8'')?([^;]+)", cd, re.I) or re.search(r'filename="?([^";]+)"?', cd, re.I)
    if m:
        return unquote(m.group(1)).strip()
    if ctype in ("text/html", "application/xhtml+xml"):
        # a web page is saved under its own title
        import html as _html
        t = re.search(r"<title[^>]*>(.*?)</title>", decode_html(data[:200000], headers), re.I | re.S)
        title = re.sub(r"\s+", " ", _html.unescape(t.group(1))).strip() if t else ""
        return (title or urlparse(url).netloc or "page")[:80] + ".html"
    name = os.path.basename(urlparse(url).path) or urlparse(url).netloc or "download"
    if not os.path.splitext(name)[1]:
        name += mimetypes.guess_extension(ctype) or ""
    return name


def is_download(headers):
    cd = (headers.get("Content-Disposition") or "").lower()
    ctype = (headers.get("Content-Type") or "text/html").lower()
    return "attachment" in cd or not any(ctype.startswith(t) for t in INLINE_TYPES)


def decode_html(data, headers):
    m = re.search(r"charset=([\w\-]+)", headers.get("Content-Type") or "", re.I) or \
        re.search(rb"<meta[^>]+charset=[\"']?([\w\-]+)", data[:4096], re.I)
    cs = (m.group(1).decode() if m and isinstance(m.group(1), bytes) else (m.group(1) if m else "utf-8"))
    try:
        return data.decode(cs, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


# Runs first inside every proxied page: keeps links, forms and script requests inside the app,
# and tells the app which page is showing so the address bar and Back stay right.
PAGE_SCRIPT = r"""<script>(function(){
var REAL=%s,O=location.origin,P=O+'/api/page?url=',F=O+'/api/fetch?url=';
function abs(u){try{return new URL(u,REAL).toString()}catch(e){return u}}
function go(u){location.href=P+encodeURIComponent(abs(u))}
function report(){try{parent.postMessage({collider:'nav',url:REAL,title:document.title||''},'*')}catch(e){}}
report();document.addEventListener('DOMContentLoaded',report);window.addEventListener('load',report);
document.addEventListener('click',function(e){
 if(e.defaultPrevented||e.button)return;
 var a=e.target&&e.target.closest&&e.target.closest('a[href]');if(!a)return;
 var h=a.getAttribute('href');if(!h||/^(javascript|mailto|tel|data|blob):/i.test(h))return;
 if(h.charAt(0)==='#'){e.preventDefault();var t=document.getElementById(h.slice(1))||document.getElementsByName(h.slice(1))[0];if(t)t.scrollIntoView();return}
 var u=abs(h);if(!/^https?:/.test(u))return;
 e.preventDefault();e.stopPropagation();go(u);
},true);
document.addEventListener('submit',function(e){
 var f=e.target,m=(f.getAttribute('method')||'get').toLowerCase(),act=abs(f.getAttribute('action')||REAL);
 e.preventDefault();
 if(m==='get'||/(^|\.)duckduckgo\.com$/.test(new URL(act).hostname)){var u=new URL(act);u.search='';new FormData(f).forEach(function(v,k){if(typeof v==='string')u.searchParams.append(k,v)});go(u.toString())}
 else{var pf=document.createElement('form');pf.method='post';pf.action=P+encodeURIComponent(act);pf.style.display='none';
  new FormData(f).forEach(function(v,k){if(typeof v==='string'){var i=document.createElement('input');i.type='hidden';i.name=k;i.value=v;pf.appendChild(i)}});
  document.documentElement.appendChild(pf);sub.call(pf)}
},true);
window.open=function(u){if(u)go(u);return null};
var sub=HTMLFormElement.prototype.submit;HTMLFormElement.prototype.submit=function(){var e=new Event('submit',{bubbles:true,cancelable:true});if(this.dispatchEvent(e))sub.call(this)};
if(window.navigation)navigation.addEventListener('navigate',function(e){var u=e.destination&&e.destination.url;if(e.cancelable&&u&&/^https?:/.test(u)&&u.indexOf(O)!==0){e.preventDefault();go(u)}});
['pushState','replaceState'].forEach(function(k){var o=history[k];history[k]=function(s,t){try{return o.call(history,s,t)}catch(e){}}});
function via(u){var a=abs(u);return(/^https?:/.test(a)&&a.indexOf(O)!==0)?F+encodeURIComponent(a):u}
var of=window.fetch;if(of){window.fetch=function(i,n){try{if(typeof i==='string')i=via(i);else if(i&&i.url)i=new Request(via(i.url),i)}catch(e){}return of.call(window,i,n)}}
var oo=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u){try{arguments[1]=via(u)}catch(e){}return oo.apply(this,arguments)};
})();</script>"""


def prepare_html(html, final_url):
    html = re.sub(r"<meta[^>]+http-equiv=[\"']?Content-Security-Policy[^>]*>", "", html, flags=re.I)
    html = re.sub(r"<base\b[^>]*>", "", html, flags=re.I)
    # a timed refresh would leave the app's proxy; send it back through
    def refresh(m):
        from urllib.parse import urljoin, quote
        return m.group(1) + "/api/page?url=" + quote(urljoin(final_url, m.group(2).strip()), safe="")
    html = re.sub(r"""(http-equiv=["']?refresh["']?[^>]*content=["']\s*\d+\s*;\s*url=)([^"'>]+)""", refresh, html, flags=re.I)
    # The page scrolls by touch or wheel; a desktop scrollbar with arrows has no place in the window.
    bars = '<style>html{scrollbar-width:none}html::-webkit-scrollbar,body::-webkit-scrollbar{width:0;height:0;display:none}</style>'
    inject = f'<base href="{final_url}">' + bars + (PAGE_SCRIPT % json.dumps(final_url))
    m = re.search(r"<head[^>]*>", html, re.I)
    return html[:m.end()] + inject + html[m.end():] if m else inject + html


def saved_page(name):
    """Shown for a moment after a link turned out to be a file: it is in Files, and the browser goes back."""
    return ("<html><body style=\"margin:0;height:100vh;display:flex;align-items:center;justify-content:center;"
            "font:15px system-ui;color:#464652;background:#E1E8EB\"><div>" + name.replace("<", "&lt;") +
            "</div><script>try{parent.postMessage({collider:'download',name:" + json.dumps(name) +
            "},'*')}catch(e){}setTimeout(function(){history.back()},1100)</script></body></html>")


def error_page(url, why):
    return ("<html><body style='font:15px system-ui;padding:24px;color:#464652;background:#E1E8EB'>"
            f"<div>{url}</div><div style='color:#7F7F7F;margin-top:8px'>{why[:160]}</div>"
            "<script>try{parent.postMessage({collider:'nav',url:" + json.dumps(url) + ",title:''},'*')}catch(e){}</script></body></html>")

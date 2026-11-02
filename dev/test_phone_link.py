# Made by Claude (2026-10-21). The phone link from outside: refused without the key, open with it. Prints no key.
import os, urllib.request, urllib.error, http.cookiejar
link = open(os.path.join(os.path.dirname(__file__), "phone_link.txt")).read().strip()
base = link.split("/?")[0]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def code(opener, url):
    try:
        with opener.open(url, timeout=30) as r:
            return r.status, r.headers.get("Set-Cookie", "")[:20]
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Set-Cookie", "")[:20]


plain = urllib.request.build_opener(NoRedirect)
for path in ("/", "/api/models", "/api/phone", "/main.dart.js", "/?k=wrong"):
    print("no key", path, code(plain, base + path))
jar = http.cookiejar.CookieJar()
keyed = urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(jar))
print("with key", code(keyed, link))
print("then /", code(keyed, base + "/"))
print("then /api/models", code(keyed, base + "/api/models"))
with keyed.open(base + "/api/phone", timeout=30) as r:
    print("phone link through the tunnel:", r.read()[:40])

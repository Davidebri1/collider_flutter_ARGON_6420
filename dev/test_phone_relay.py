# Made by Claude (2026-10-21). The unchanging phone link, from outside: refused without the key, leads in with it.
import http.cookiejar, json, os, time, urllib.error, urllib.request
here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(here, "phone_app", "data", "collider_config.json"), encoding="utf-8"))
row = next(r for r in cfg["providers"] if "collider-phone" in r.get("endpoint", ""))
ep, key = row["endpoint"], row["key"]
UA = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


plain = urllib.request.build_opener(NoRedirect)


def code(op, url):
    try:
        with op.open(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.status, r.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location", "")


print("worker without key", code(plain, ep + "/"), code(plain, ep + "/wrong"))
for _ in range(10):
    st, loc = code(plain, f"{ep}/{key}")
    if st == 302:
        break
    time.sleep(3)
print("worker with key", st, "->", loc.split("/?")[0])
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
with op.open(urllib.request.Request(f"{ep}/{key}", headers=UA), timeout=40) as r:
    body = r.read()
    print("followed to", r.geturl().split("/?")[0], r.status, len(body), b"flutter" in body.lower())
with op.open(urllib.request.Request(r.geturl().split("/?")[0] + "/api/models", headers=UA), timeout=40) as r2:
    print("models through the link:", len(json.load(r2)["models"]))

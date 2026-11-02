# Made by Claude (2026-10-20). One-time edit: the browser starts on DuckDuckGo (David: "DUCKDUCKGO"). Its script page
# answers the app's page loader with a bot puzzle; its HTML page answers with the results, so searches go there.
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


edit("lib/features/browser/screens/in_app_browser_sheet.dart", [
    ("  static const _homePage = 'https://www.bing.com/';\n  static const _search = 'https://www.bing.com/search?q=';",
     "  static const _homePage = 'https://html.duckduckgo.com/html/';\n  static const _search = 'https://html.duckduckgo.com/html/?q=';"),
])
edit("lib/main.dart", [
    ("BrowserTab(id: 'user_default', title: 'Search', url: 'https://www.bing.com/', isUserControlling: true),",
     "BrowserTab(id: 'user_default', title: 'Search', url: 'https://html.duckduckgo.com/html/', isUserControlling: true),"),
])
edit("tools/collider_server.py", [
    ("        url = (parse_qs(urlparse(self.path).query).get(\"url\") or [\"\"])[0]\n        return url if re.match(r\"^https?://\", url) else \"https://\" + url",
     "        url = (parse_qs(urlparse(self.path).query).get(\"url\") or [\"\"])[0]\n        url = url if re.match(r\"^https?://\", url) else \"https://\" + url\n"
     "        # DuckDuckGo's script page meets the loader with a bot puzzle; its HTML page gives the same results.\n"
     "        m = re.match(r\"^https?://(?:www\\.)?duckduckgo\\.com/\\?(.*)$\", url)\n"
     "        return \"https://html.duckduckgo.com/html/?\" + m.group(1) if m else url"),
])
print("ok")

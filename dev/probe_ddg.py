# Made by Claude (2026-10-20). Does DuckDuckGo come through the app's page loader with its results?
import sys, urllib.parse, urllib.request
port = sys.argv[1]
for u in ["https://duckduckgo.com/", "https://duckduckgo.com/?q=visionos+windows", "https://html.duckduckgo.com/html/?q=visionos+windows",
          "https://lite.duckduckgo.com/lite/?q=visionos+windows"]:
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/page?url=" + urllib.parse.quote(u, safe=""), timeout=40)
        t = r.read().decode("utf-8", "ignore")
        print(u, r.status, len(t), "results:", t.count("result__a") + t.count("result-link") + t.count('data-testid="result"'),
              "challenge:", "anomaly" in t.lower() or "captcha" in t.lower())
    except Exception as e:
        print(u, "ERR", e)

# Made by Claude (2026-10-21). Does Google come through the in-app browser's page loader, phone and desktop?
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import collider_files as cfiles

for url in ("https://www.google.com/", "https://www.google.com/search?q=jacksonville+weather"):
    for mobile in (True, False):
        try:
            code, final, headers, data = cfiles.fetch_page(url, "GET", None, None, mobile=mobile)
            text = cfiles.decode_html(data, headers)
            links = len(re.findall(r'<a [^>]*href=', text))
            res = len(re.findall(r'<h3', text))
            print(f"{'phone' if mobile else 'desk '} {code} {final[:70]} bytes={len(data)} links={links} h3={res} "
                  f"captcha={'unusual traffic' in text.lower() or '/sorry/' in final} js_only={'enablejs' in text.lower() or 'please click here if you are not redirected' in text.lower()}")
            open(os.path.join(os.path.dirname(__file__), f"google_{'m' if mobile else 'd'}_{'s' if 'search' in url else 'h'}.html"), "w", encoding="utf-8").write(text)
        except Exception as e:
            print("error", url, mobile, e)

# Made by Claude (2026-10-21). Round 7: a page that leaves by its own script stays in the in-app browser.
# Found in the test: searching from Google's own box sent the frame straight to google.com (script navigation, not a
# link or a submitted form), which refuses to be shown in a frame. Every navigation the page starts now goes through
# the app (the browser's Navigation API), and a form sent by script is treated like one sent by hand.
import pathlib, sys

p = pathlib.Path(__file__).resolve().parent.parent / "tools" / "collider_files.py"
s = p.read_text(encoding="utf-8")
old = "window.open=function(u){if(u)go(u);return null};"
new = (old + "\n"
       "var sub=HTMLFormElement.prototype.submit;HTMLFormElement.prototype.submit=function(){"
       "var e=new Event('submit',{bubbles:true,cancelable:true});if(this.dispatchEvent(e))sub.call(this)};\n"
       "if(window.navigation)navigation.addEventListener('navigate',function(e){var u=e.destination&&e.destination.url;"
       "if(e.cancelable&&u&&/^https?:/.test(u)&&u.indexOf(O)!==0){e.preventDefault();go(u)}});")
if s.count(old) != 1:
    sys.exit("window.open line not found once")
s = s.replace(old, new)
old2 = "document.documentElement.appendChild(pf);HTMLFormElement.prototype.submit.call(pf)}"
if s.count(old2) != 1:
    sys.exit("post form line not found once")
s = s.replace(old2, "document.documentElement.appendChild(pf);sub.call(pf)}")
p.write_text(s, encoding="utf-8")
print("edited tools/collider_files.py")

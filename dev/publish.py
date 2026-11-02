# Made by Claude (2026-10-20). Sends this folder's work to GitHub: refuses if any key would be committed, commits,
# pushes main, and attaches Collider.exe to a release named for the day and time.
# python dev/publish.py "what changed"
import os, re, subprocess, sys, time
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
msg = sys.argv[1] if len(sys.argv) > 1 else "Collider, Claude's build"


def run(*a, check=True):
    r = subprocess.run(a, cwd=W, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    print(" ".join(a[:3]), "->", r.returncode, (r.stdout + r.stderr).strip()[-400:])
    if check and r.returncode:
        sys.exit(r.returncode)
    return r


run("git", "add", "-A")
staged = run("git", "diff", "--cached", "--name-only").stdout.split()
for p in staged:
    path = os.path.join(W, p)
    if os.path.isfile(path) and re.search(r"nvapi-[A-Za-z0-9_\-]{20,}|tvly-[A-Za-z0-9_\-]{20,}|sk-[A-Za-z0-9]{20,}|gsk_[A-Za-z0-9]{20,}",
                                          open(path, encoding="utf-8", errors="ignore").read()):
        run("git", "reset", "-q", check=False)
        sys.exit(f"KEY FOUND in {p}: nothing committed")
msg += ("\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
        "\nClaude-Session: https://claude.ai/code/session_01QzSzX6ygNb8jJBtFJbj9Bv")
if staged:
    run("git", "-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com", "commit", "-q", "-m", msg)
run("git", "push", "origin", "main")
exe = os.path.join(W, "Collider.exe")
if os.path.isfile(exe):
    tag = time.strftime("build-%Y%m%d-%H%M")
    run("gh", "release", "create", tag, exe, "--title", tag, "--notes", msg.split("\n")[0], check=False)
print("PUBLISHED")

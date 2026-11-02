# Made by Claude (2026-10-21). Starts Collider's server (David's own data, host 47801, with the phone link) as its own
# process, outside the tool session that launches it: the earlier starts were ended along with that session, which is
# why the link kept dying.
import os, subprocess, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
py = os.path.join(root, "dev", ".venv-build", "Scripts", "pythonw.exe")
if not os.path.exists(py):
    py = sys.executable
flags = 0x00000008 | 0x00000200 | 0x01000000  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB
log = open(os.path.join(root, "dev", "real_server_log.txt"), "a")
p = subprocess.Popen([py, os.path.join(root, "tools", "collider_app.py"), "--go", "--server-only", "--host", "47801"],
                     cwd=root, stdin=subprocess.DEVNULL, stdout=log, stderr=log, creationflags=flags, close_fds=True)
print("started", p.pid)

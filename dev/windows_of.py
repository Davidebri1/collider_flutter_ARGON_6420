# Made by Claude (2026-10-20). Lists the top-level windows of the Collider processes: title, place, size, shown or not.
import ctypes, ctypes.wintypes as wt, subprocess
u = ctypes.windll.user32
pids = set()
for line in subprocess.run(["tasklist", "/FI", "IMAGENAME eq Collider.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout.splitlines():
    parts = line.split('","')
    if len(parts) > 1:
        pids.add(int(parts[1]))
out = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
def each(h, _):
    pid = wt.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(pid))
    if pid.value in pids:
        n = u.GetWindowTextLengthW(h)
        b = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(h, b, n + 1)
        r = wt.RECT()
        u.GetWindowRect(h, ctypes.byref(r))
        out.append((pid.value, h, b.value, (r.left, r.top, r.right - r.left, r.bottom - r.top), bool(u.IsWindowVisible(h)), bool(u.IsIconic(h))))
    return True
u.EnumWindows(each, 0)
print(pids)
for o in out:
    print(o)

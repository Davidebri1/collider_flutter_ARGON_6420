# Made by Claude (2026-10-23). Runs any `flutter ...` command through Flutter's own tool (flutter.bat needs PowerShell,
# which does not start on this computer), writing its output to dev\flutter_cmd_log.txt.
# Usage: python dev\flutter_cmd.py build apk --debug
import os, subprocess, sys
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUTTER = os.environ.get("FLUTTER_ROOT", r"C:\Users\D\flutter")
dart = os.path.join(FLUTTER, "bin", "cache", "dart-sdk", "bin", "dart.exe")
tool = [dart, "--packages=" + os.path.join(FLUTTER, "packages", "flutter_tools", ".dart_tool", "package_config.json"),
        os.path.join(FLUTTER, "bin", "cache", "flutter_tools.snapshot")]
log = os.path.join(W, "dev", "flutter_cmd_log.txt")
with open(log, "w", encoding="utf-8") as f:
    code = subprocess.run(tool + sys.argv[1:], cwd=W, env={**os.environ, "FLUTTER_ROOT": FLUTTER},
                          stdout=f, stderr=f, stdin=subprocess.DEVNULL).returncode
print("EXIT", code, "log:", log)

# Made by Claude (2026-10-21). Runs one `flutter pub` command through Flutter's own tool and prints its output.
import os, subprocess, sys
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUTTER = os.environ.get("FLUTTER_ROOT", r"C:\Users\D\flutter")
dart = os.path.join(FLUTTER, "bin", "cache", "dart-sdk", "bin", "dart.exe")
tool = [dart, "--packages=" + os.path.join(FLUTTER, "packages", "flutter_tools", ".dart_tool", "package_config.json"),
        os.path.join(FLUTTER, "bin", "cache", "flutter_tools.snapshot")]
r = subprocess.run(tool + ["pub", *sys.argv[1:]], cwd=W, env={**os.environ, "FLUTTER_ROOT": FLUTTER},
                   capture_output=True, text=True, stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace")
print((r.stdout + r.stderr)[-3000:])
print("exit", r.returncode)

# Made by Claude (2026-10-20). The web build of this folder, whatever the folder is called.
# Runs Flutter's own tool directly (flutter.bat needs PowerShell, which stopped starting on this computer on 2026-10-20).
import os, subprocess, sys
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUTTER = os.environ.get("FLUTTER_ROOT", r"C:\Users\D\flutter")
dart = os.path.join(FLUTTER, "bin", "cache", "dart-sdk", "bin", "dart.exe")
tool = [dart, "--packages=" + os.path.join(FLUTTER, "packages", "flutter_tools", ".dart_tool", "package_config.json"),
        os.path.join(FLUTTER, "bin", "cache", "flutter_tools.snapshot")]
env = {**os.environ, "FLUTTER_ROOT": FLUTTER}
log = os.path.join(W, "dev", "build_log.txt")
with open(log, "w", encoding="utf-8") as f:
    # --wasm: browsers that run WebAssembly get the Wasm build, the rest get JavaScript (Claude, 2026-10-23)
    code = subprocess.run(tool + ["build", "web", "--release", "--no-tree-shake-icons"],
                          cwd=W, env=env, stdout=f, stderr=f, stdin=subprocess.DEVNULL).returncode
print("BUILD_EXIT", code, "log:", log)
sys.exit(code)

# Made by Claude (2026-10-21). Moves the app from the design libraries inside Flutter's SDK (to be deprecated in the
# November stable release) to the standalone material_ui and cupertino_ui packages, with Flutter's own migration:
# `flutter pub add material_ui cupertino_ui`, then `dart fix --apply --code=migrate_design_widgets` (Flutter 3.47 notes).
import os, subprocess, sys
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUTTER = os.environ.get("FLUTTER_ROOT", r"C:\Users\D\flutter")
dart = os.path.join(FLUTTER, "bin", "cache", "dart-sdk", "bin", "dart.exe")
tool = [dart, "--packages=" + os.path.join(FLUTTER, "packages", "flutter_tools", ".dart_tool", "package_config.json"),
        os.path.join(FLUTTER, "bin", "cache", "flutter_tools.snapshot")]
env = {**os.environ, "FLUTTER_ROOT": FLUTTER}
log = open(os.path.join(W, "dev", "migrate_log.txt"), "w", encoding="utf-8")
steps = [tool + ["pub", "add", "material_ui", "cupertino_ui"],
         [dart, "fix", "--apply", "--code=migrate_design_widgets"]]
for s in steps:
    log.write("$ " + " ".join(s[-4:]) + "\n")
    log.flush()
    code = subprocess.run(s, cwd=W, env=env, stdout=log, stderr=log, stdin=subprocess.DEVNULL).returncode
    log.write(f"exit {code}\n")
    print(s[-3:], "exit", code)
    if code:
        sys.exit(code)

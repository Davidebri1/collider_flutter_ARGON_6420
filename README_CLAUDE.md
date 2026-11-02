# Collider (Flutter) — Claude's build

Made by Claude for David Ebri.

- Repository (the permanent reference): https://github.com/Davidebri1/collider-flutter-claude
- Folder on David's computer, as of 2026-10-20: `C:\Users\D\Documents\collider_flutter_CLAUDE_20261020`
  (before: `collider_flutter__CLAUDE_live-models-consensus_20260927`, left as it was).
  Nothing in the app, its scripts or its documents names this folder: every path is taken from where the file sits,
  so the folder can be renamed or moved without breaking anything. Only this line needs updating after a rename.

## Run

- `Collider.exe` (built by `dev/build_exe.py`), or `python tools/collider_app.py`.
- A launch window comes up first and shows the whole configuration as a form: the host number at the top, the
  consensus agent and its instructions, every model with its own instruction and temperature, every provider with its
  address, key and models (each showing where the app reads it), the answer instruction for each mode, search, limits,
  tuning, themes and purchases. Launch saves `data/collider_config.json` beside the exe and opens the app.
- `python tools/collider_app.py --go --host 30111 --server-only` runs the server on that host with the saved configuration.

Keys live only in `data/collider_config.json` on the computer running it; `data/` is not in this repository.

## Build and publish (scripts in `dev/`, all paths relative to this folder)

- `python dev/build.py` the web build (runs Flutter's tool directly).
- `python dev/build_exe.py` Collider.exe, one file.
- `python dev/publish.py "message"` checks for keys, commits, pushes to GitHub and attaches Collider.exe to a release.

## Where things are

- `lib/` the Flutter app (web build served by the local server).
- `tools/collider_server.py` the local server: models, consensus, research, files, browser pages, `/api/themes`.
- `tools/collider_config.py` the configuration file; `tools/collider_app.py` the launch window and the app window.
- Live wallpapers: David's Cloudflare R2 bucket `collider-themes`, listed by its Worker; see `themes()` in the server.
- `docs/INTENT.md` David's words; `docs/DEVIATIONS.md` every departure from his frames, with the reason, signed.

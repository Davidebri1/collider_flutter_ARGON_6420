# Crouton Alpha — build, run, host

Project folder: `collider_crouton_alpha`
Branch: `crouton-alpha`
Base: `collider_flutter_ARGON_8474` @ `8c745ac` (`feature/ambient-chat-card`)
Premium Theme Market ported from flash `41923` (`795dcf2`).

## Build and run

Windows PowerShell, from the project folder.

```powershell
flutter pub get
dart analyze lib                 # expect 0 errors
flutter build web --release
```

Then the one command that serves the app **and** its API:

```powershell
python tools/collider_server.py --no-open
```

It binds the `localhost_port` saved in `data/collider_config.json` (37418 here) and serves:

| Route | What |
| --- | --- |
| `/` | `build/web` — the app |
| `/api/themes` | the premium theme catalog (~115 KB of JSON) |
| `/api/models` | the model roster and provider status |
| `/api/history` | job snapshots: per-model essences and consensus results |
| `/api/phone` | the outside link (local requests only) |

Use `collider_server.py` rather than `python -m http.server`: a plain static server
has no API, and the theme catalog, history and models all come from it.

## Hosting

### Live link (Cloudflare, this account)

```
https://collider-crouton-alpha.ebridavid.workers.dev/?k=fF6fWTmdXwsu-iZGuNXTRL2A
```

One Worker serves everything: the Flutter build as static assets, plus the whole API on the
same origin. No tunnel, no second host, no local process needed.

```powershell
npx -y wrangler@4 deploy
```

| Piece | Where |
| --- | --- |
| Worker source | `worker/src/index.js` |
| Theme catalog | `worker/themes.json`, served by `/api/themes` |
| Static app | `build/web` via `[assets]` in `wrangler.toml` |
| State | KV `STATE` (`ef855140e2154c7b91fd21bfc34f78f0`) |
| Provider keys | secret `PROVIDERS_JSON` |
| Access key | secret `APP_KEY` |

Routes ported from `tools/collider_server.py`: `/api/models`, `/api/themes`, `/api/history`,
`/api/store`, `/api/ask`, `/api/stream/<id>`, `/api/job/<id>`, `/api/reply`,
`/api/reply/start`, `/api/stream/r/<id>`, `/api/smartgen`, `/api/page`, `/api/transcribe`.
Every request needs `?k=<key>` or the `ck` cookie, otherwise 403.

### How a job runs on Workers

- The job runs **inside** the SSE request that streams it. Cloudflare cancels `waitUntil()`
  work right after an invocation ends, so a job started there is killed mid-answer.
- The stream is built with `new ReadableStream({ start })`. Passing a bare function leaves
  `start` uncalled, which the runtime reports as "the Worker's code had hung".
- Progress is written to KV on every update. A reconnect re-enters the stream, skips models
  that already have an answer, and skips consensus that already ran.
- A timed-out model call is not retried: one deadline, then the model is marked `error` so the
  rest of the job and the consensus are not held hostage.

### Roster

The roster is built from models this NVIDIA key actually answers. Every id was called and
replied before being listed; `worker/roster_probe.json` is that probe. Ten models qualify
(Bolt, 3.5 Lightning, 3 Ultra, 3.5 Super, 3 Nano, Muse Glimmer 30B, Llama 3.2 90B Vision,
MiniMax M3.1 Flash, Mistral Large 4, Step 5 Preview). The consensus judge is
`nvidia/nemotron-3.5-bolt-e4b`, with Ultra and Mistral Large 4 as fallbacks.

### What the Worker cannot do

- `/api/imagine` returns empty `items` and `models`: the image generator spans Cloudflare
  Workers AI, NVIDIA and fal (`tools/collider_imagine.py`) and was not ported. Discover still
  lists its catalog; generation itself is absent.
- `/api/files*` returns empty lists: a Worker has no disk. Uploads, generated files and the
  Files library need object storage.
- `/api/transcribe` is wired to the speech provider but has not been exercised with real audio.

### Data

- `data/collider_config.json` holds the live provider keys and the port. It is git-ignored and
  never leaves this machine; the Worker gets the same rows through the `PROVIDERS_JSON` secret.
- History and job snapshots live in KV (`history`, `job:<id>`, `reply:<id>`), behind the same
  origin, capped at 200 sessions.

## Notes for a reviewer

- The app is one Flutter codebase with iOS, Android and web targets. Web is what was built and
  verified here; device targets were not exercised in this environment.
- Replies, generation and files need the companion server on the same origin. A static host
  alone shows those surfaces empty.
- `docs/PRD_EVALUATION.md` scores all 98 requirements against what this build actually does.

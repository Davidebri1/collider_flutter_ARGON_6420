# Collider progress. Made by Claude.

Goal: Collider opens with one double-click, answers real questions with your NVIDIA models, writes the summaries and the consensus (consensus agent first, each model as backup), and follows the spec and your laws.

Open it: double-click `Open Collider.bat` in this folder. Screenshots of every item: `Collider Progress.html` in this folder.

## Done

| Item | What it does now |
| --- | --- |
| One-click launch | `Open Collider.bat` starts the local server and opens Collider in its own window |
| Models | 13 NVIDIA models that answered on your account. Keys stay in your keys file; the app only talks to the local server |
| Summaries | Consensus agent (Gemma 4 31B, then Nemotron 3 Super, then GLM 5.3) reduces every answer to its essence, groups them, counts the headcount, and pins the winning essence verbatim. If the agent fails, each model summarises its own answer |
| Research depth | Chat: a direct answer. Internet: answer from live web sources. Research: a report with sources. Deep Research: an annotated paper, no jargon. Web search through your Tavily key |
| Composer | Your last prompt is pinned above the dock, inside the ticker window. Tap it or swipe up on the dock: it opens in place with the depth selection, target models, attach and the send button. Send springs on press and turns into a spinner while models answer |
| Model cards | Each model owns a colour. Cards higher in the stack sit higher. A shimmer shows while a model is answering |
| Side nav | Follows Master Spec §6.2: New Chat, Local History, Global History, Consensus History, Models on AI Chat; each work surface gets its own |
| History | Real. Every answered question is saved (unless Incognito) and can be reopened from the side nav |
| Settings | Only consequential switches: Incognito, Save consensus results, Smart Gen personal context |
| Themes | Theme Gallery holds free themes only. Swipe up (or Live Wallpapers) opens the Premium Theme Market; swipe down returns |
| Music | Plays the bundled tracks. A small player appears and can be dragged anywhere; it stays where you put it |
| App icons | Frosted glass with emitted light; they rise into place when Apps opens |
| Smart Gen | Colour-coded cards by type |
| Browser | Real pages, address bar searches or opens a site, back button; research sources open as tabs |
| Consensus map | Draws the current question's answers |
| Focus windows | Blur the background behind them |

## Not done

| Item | State |
| --- | --- |
| Premium Theme Market performance, live wallpaper sourcing | Not investigated yet |
| Ambient animation on every action | Added to composer, cards, apps, music; not every screen audited |
| Attachments | Picked in the composer, not yet sent to the models |
| Image, video, audio models | Not wired; NVIDIA has no equivalents on this account |

## Known limits

- NVIDIA's free endpoints take from 20 seconds to 3 minutes. A model that does not answer in time shows "No answer from this model."
- Kimi K3 currently returns repeated characters on NVIDIA. It stays in the list, last, and is not selected by default.
- Another agent edited `lib/main.dart` in this folder on 2026-09-27 while I was working. If it keeps editing, my changes can be overwritten.

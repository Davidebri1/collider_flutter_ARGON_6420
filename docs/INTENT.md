# Intent

These are outcomes, not measurements. Numbers are yours to choose and to beat. If a number here ever becomes the target, the intent has been lost.

## The screen

- The wallpaper and the conversation are the product. UI serves them and then gets out of the way.
- Nothing runs edge to edge. Nothing fills space because space is there.
- Demure and minimal on the surface, technically ambitious underneath. Think JARVIS: faded edges, depth, restraint, motion with intent.
- Everything lives in a window. A focused window pushes the world back with depth of field, the way a camera racks focus, not with a flat grey sheet.
- Only permanently necessary elements are permanent: the bottom dock, the contextual side nav on the left edge, and the pinned prompt. Everything else appears at the moment it is needed and leaves after.
- Navigation is exactly what COLLIDER_MASTER_SPEC §6 lists. The side nav carries the active surface's affordances, as the left tab bar does in every visionOS app. Nothing floats outside it: no chips, no stray buttons.
- Only the information relevant to this screen. Absolutely no noise.
- This app is not for developers. No developer vocabulary anywhere a user can read it. (David, 2026-10-04)
- Nothing is added that David did not ask for, and nothing is shown that is not wired to do what it says. (David, 2026-10-04)

## Overlays

- An overlay is a pause menu. Brief, sized to its content, never the whole screen, never full width.
- The content behind it stays visible and recognisable.
- One gesture escapes it. Nothing overlaps or collides with anything else.

## Hierarchy

- Consistent hierarchy, spacing and minimalism across every screen, so a user who learns one screen has learned them all.
- Distinction comes from colour, elevation and position, not from lines and borders.
- Cards higher on the stack sit higher in elevation.

## The ticker row

Added by Claude on 2026-10-04, from David's words.

- Every ticker row, and the consensus preview, is a one-line summary that fits in its box. Not truncated.
- "1st, fulfill the functional requirement: legible summary completely fits and without worry of exceeding."
- "Everything should be placed or sized appropriately. Prioritize." Whatever else is in the row takes its place and size after the summary, never from it.
- The line is the complete answer. If the user must open the row to get the answer, the summary failed.

## Words, icons and size

Added by Claude on 2026-10-04, from David's words.

- Where an icon cannot say what it opens, use words. "This is where you should have used words, because you have unsolvable ambiguity."
- Words are for naming, not for filling. A history list is titles, one line each, as Claude's and every other AI's history looks. No summaries in the rows.
- "Minimal size necessary." A pane is only as large as the function it provides. Demure.

## The consensus score

Added by Claude on 2026-10-04, from David's words (docs\COLLIDER_SPEC.md and his comments).

- The score is a fraction, coloured red to green by how many agree, and it glows. It reads -/- until every model has answered.
- No icon beside it. "Did I ask for scales?"

## Moving between tiers

Added by Claude on 2026-10-04, from David's words.

- What lies beyond the current screen is not announced by a floating button. "Use the standard cinematic fades, edges, blurs, etc. to convey what I spoke."

## What David said on 4 Oct 2026

Added by Claude on 2026-10-04, from David's comments on the progress page. His words are in quotes.

- "Words ONLY when visual design cannot sort ambiguity." In a picker a check mark and a cross are understood by everyone; they get no words.
- "No edge to edge UI elements", "no oversized elements", "no unnecessary words", "no added words", "no clutter", "no added symbols", "no counting".
- Where content reaches an edge it fades. "What happened to common sense tools and technique. Edge fade blurs." Never a hard cutoff.
- Things that belong together do not take separate lines of permanent or semi-permanent space. "If you're strapped for space, why not fill that area before you think of downsizing font."
- "Who told you to blur?" was said of the screen of covers that used to be the Music Player. That screen is gone (see below).
- Consensus is not in the side navigation. His layout line: "consensus lives only on this pinned row - it is not duplicated on any nav surface, bottom or side".
- The reading view is his line and nothing more: "zoomed in view (also scrollable) with blurred background or dimmed and with action options along the bottom of the message and with no visible window and with faded edges".
- Model names are written out. No initials, no badges.
- The dot and bar drawn under windows is not wanted: "this weird ugly horizontal bar at bottom. what is that?"
- The browser's controls belong to the side navigation: "side nav bar is where this belongs".
- The browser does not start on DuckDuckGo. "bizarre. not google not bing, not yahoo. DUCKDUCKGO. Are you kidding me?" and, later, "why are you doubling down on duck duck go? whats wrong with google?"
- The music bar has a mute button, and its close is not placed among the controls.
- A progress page shows each thing once. "Not sure why you keep showing the same things over and over."
- The reference map is his "New Collider - Figma Reference Map" of 4 Oct 2026, copied in docs\FIGMA_REFERENCE_MAP_1004.md.

Added later on 2026-10-04, from the comments he left last:

- Overlays and the room behind them: "read the spec. overlays must blur the background. or tint it if cinematic effect is needed (like premium theme market, locked unlock areas/content, tooltips/tutorials)".
- A quick overlay does not take the whole view. Of Apps: "consider only DOF blurring around the icons here. you dont need to take over full attention, because just one quick second is all it takes to select your icon. so it's taxing to make the eyes adjust back and forth for trivial things. keep the field of view clean."
- The consensus map: "should be in a window like everything else".
- The browser has one bar: "add the address bar down here, or add this up to it".
- Premium Theme Market: "so many words. when all i asked for was song list ... and theme name ... who asked for anything else? whats the play button and arrows for?"
- Music: "delete all the low tide high tide stuff. no tie dye". The Music Player is the music bar and the music in Files, as his earlier notes say: "music player is a widget within the files tab pane. the music player has all your purchased songs listed in the files menu music audio view. generated or uploaded music will also go here."
- Live wallpapers and what is bought: "i believe the live wallpapers are for in app use only. so the theme gallery can be the place for the 'purchased' section. here, you can put music in place of the live wallpapers."
- Files: the side menu does not repeat the tiles. "how about filetype".
- Copying a frame: "i dont want any approximations. i want relationships. the %'s should carry over. unless you think otherwise, then write it on your deviations list and provide justification. do that for each deviation." The list is docs\DEVIATIONS.md.
- Context menus: "havent you heard of context menus? on click, on hover, context popups?" What a message, a conversation or the music bar can do is in a menu that opens on it.

## Motion

- Every action is animated realistically: press, open, close, move, arrive.
- Ambient motion exists but never competes with content.
- Motion tells the user where something came from and where it went.

## No options. No preferences.

Options push homework onto the user. They are noise.

A selection is different. It is pulled by the user, the logic behind it is provided, the choices are mutually exclusive, and it has a lasting consequence. The Theme Gallery is a selection.

A toggle is allowed only when it is consequential: incognito, autosave consensus result, Smart Gen access to personal information.

Test for any control: what use case does it serve, and what outcome does the user expect? If there is no answer, remove it.

## Themes

- Theme Gallery: the free themes, and the live wallpapers that have been bought.
- Premium Theme Market: the live wallpapers. Reached by swiping up from the Theme Gallery into a more cinematic tier. Swipe down returns.


## Requirements without intent

Added by Claude on 2026-10-03, from David's words.

- A requirement is valid when it maps cleanly to a functional requirement: something the user does or gets.
- A technical requirement removed from intent is not valid. These are almost always AI-written, not David's. Do not follow them at the expense of creativity and quality.
- Serve the functional requirements dutifully.
- When a line in a spec seems devoid of intent, or the reason for it is unknown: flag it and tell David. Do not silently follow it, and do not silently drop it.

Flagged so far (not followed; each is David's to confirm or strike):

| Where | The line | Why it is flagged | What the app does instead |
| --- | --- | --- | --- |
| COLLIDER_MASTER_SPEC 3.1, AGENTS.md law 4 | No breathing pulse on a waiting card | No user outcome behind it; removing the dot left a waiting card with no sign of life | Struck on 2026-10-04: David never asked for it; the agent that wrote law 4 on 2026-09-05 added it. The dot is on waiting cards |
| COLLIDER_MASTER_SPEC 3.4, CONVERSATION_TICKER_SPEC | Provider colour only as a 3.5 px bar | Conflicts with David's request for colour-coded cards | Struck from the spec on 2026-10-03 on David's instruction. Cards keep their full provider tint |
| COLLIDER_MASTER_SPEC (summaries) | Shrink text to fit | Makes text unreadable; David's line says "1 line, not truncated" | The line is written to the length the row holds: the app measures the row and sends the length with every question, and the server never keeps a line that is over. Nothing is cut, wrapped, scrolled or shrunk |
| COLLIDER_MASTER_SPEC 9 | A fixed icon and label list for Apps | David's own names differ (Smart Gen, Discover Market, Theme Gallery, Premium Theme Market, Files, Music Player, Browser) | David's names |
| AGENTS.md law 4 | "Smart Gen" banned as a buzzword, to be called "Workspaces" | It is David's own name for the feature; he never told a model to rename it | Struck on 2026-10-04 from AGENTS.md and the specs in this clone. The name stays |
| COLLIDER_MASTER_SPEC 6.3 | Consent modal before switching surfaces | Already removed on 2026-09-27; an interruption with no outcome | Switching just proceeds |
| COLLIDER_MASTER_SPEC 10, the reading view | A `Branch` action beside Copy, Save, Share | Not David's: his line says only "action options along the bottom of the message". Developer vocabulary, in an app that is not for developers, and wired to nothing | Struck on 2026-10-04 on David's instruction. The row holds Copy, Save and Share, each of which does what it says |


## Added on 2026-10-17 (second round), David's words

- Smart Gen: "use mobbin Trello as a source as well. it should be similar to that in use and visuals. perhaps monday as well ... flutter should handle all this functionality natively."
- "make sure everything is responsive."
- Account: "make sure teh account tab isnt oversized or big. there's no profile picture so omit that section. no submenu should be larger than its menu. submenus are sub settings area, for configuring. they are organization and framing. panes/windows/work spaces/value-add or transitional screens are not submenus. they are modules."
- History: "history, is not a submenu. It's a pane. an overlay pane. and it will be a scrollable list of selections. include a preview option where if you click on one, it loads the conversation in an expansion preview pane like Windows 11's preview pane. ideally, you should be able to continue the conversation from that view ... make sure the ... 'Load Conversation' shows up in that pane."
- Premium Theme Market: "youre merely changing the code to point at my live wallpaper(s) instead of a music video file. likewise the album covers and all music related mentions and references ... remove all performance hindering code, streamline this. let it read from my cloudflare account to gather images. but adapt this code as-is to fit my app perfectly. no leftover remnants. read every line of code."
- Launch window: "a type in selector that runs on the app's run ... type in host number to launch on ... no more of this hardcoded bullshit"; "a tool for inserting api keys, throughout the app. i want full visibility into where my app's listeners are picking up their input"; "it should save your last used configurations. like a config file that pops up to show you only the form fields you are interested in"; "At the top ... the host number (but default to a random number each time). and the remaining fields can be the admin-only config files for provider and api key pairs."
- On priorities: a development-stage app is not near shipping; administrative drama (key exposure, environment variables) is not the headline. The value-added function working is.
- Launch window (2026-10-17): "it needs to do the default filling ... 'as if the config file was dislayed as a form, showing only the relevant fields to fill in.' ... it should load last defaults"; "the host number is blank by default, not random".
- Premium Theme Market tracks (2026-10-17): "make sure premium theme market displays the preview tracks below. 5 of them. do this cinematically. use edge blurs and center focus on the selected track. this is a preview pane so people know what theyre getting with their purchase."
- Purchases (2026-10-17): "make sure these items are price-marked and listed for actual in app purchase ... just the front end. obviously give me a debug means to bypass these requirements (A button, or a permanent bypass). include the correct tooltips for failed purchases or completed purchases if not already handled by ios and android payment services. make them natural, and in ios and/or android's language and design."
- Discover Market (2026-10-18): "NO PROMPT anthing in this app. discover market is exactly the same as grok's imagine market. so lets copy that. mobbin will guide you. discover market is an in app module so it will be in a pane just like smart gen and every other durable surface"
- Running and size (2026-10-18): "I cant run this without unzipping? and whats up with the file size? we're hosting almost all our assets, right?"
- Portability (2026-10-18): "are the api keys configurator and host number tools available in a portable way? ... can attach to other, especially newer, collider model revisions ... how can i use the config on every collider flutter app or collidr, especially future buids and agents with folder access"
- Discover Market labels (2026-10-18): "yes change the labels. I'm discover market. so dont copy words."
- Video player (2026-10-18): "my app should also have its own built in video player ... there was a figma reference for it. and it should look just like the figma reference."
- Video player (2026-10-18): "those should be outside of viewing area ... include all those buttons in the already existing, non-intrusive, progress bar ... 'close video' ... and the volume as well. that has a standard where it is only shown when volume is edited"; "the reference example is about 50% width, with 25% on each side ... what a weird translation from 50% to 95%."
- HIG (2026-10-18): "That's the full Vision OS documentation right there. This is the blueprint guideline and library, and system reference, and logical backbone ... read every word ... capture this ... to a design document. make it accessible for all and easy to understand. include all logic and reasoning and philosphy."
- Configuration (2026-10-20): "didnt i ask you to give me this control in the config file? so you dont need or have to touch it? i need the config file updated so it's useable."
- Configuration (2026-10-20): "i told you to include system instructions (like for consensus agent and for each model) in the config file ... include every configuration option that one might need ... i want to be able to configure my app and see my app's configuration before i launch it. so provide me the form that gives me this access."
- Not broken (2026-10-20): "why did you mess with things that werent broken?"
- Quality (2026-10-20): "2k is the standard"; "i dont offer junk when good things are available ... quality is the intrinsic promise."
- Pricing (2026-10-20): the spec's band, $2.99–$7.99 per wallpaper, sold individually; no tiers by resolution.
- Project folder (2026-10-20): "the app name references a date, which is not identifying since it hasnt been renamed. daily renaming would keep it relevant and current. it also needs to be a shorter name and a much smaller project folder. it's like 3GB. So let's copy paste what we need to another newly created project folder, identifiably and descriptively named. and we go from there."
- References (2026-10-20): "eventually we need to change the name of the local app. does that mean your link in your documents will break and we lose the reference? can we see how to handle this?"
- Documents (2026-10-20): "also include a document editor (including word and pdf files) with inline editing and the comprehensive suite of functionality (spell check, formatting, autocorrect, in line editing, images, etc. ). you can get this from the vercel templates. get the best one they have and just implement that. it can be a html render in flutter if thats easier."
- Finds (2026-10-20): "implement your smart gen find and the discover market find where you see fit. smart gen is like trello and discover market is like grok imagine market so i dont see the overlap. but you do your thing. and remember, we can use htmls."
- Voice (2026-10-20): "voice chat feel free to incorporate."
- Icons (2026-10-20): "your icons are no good . the app selector overlay mostly. redo them all in a nice distinct and color-respecting manner. the rest of the icons need to be in color too. visionOS isnt meant to be stale. it's meant to be realistic. take a look at apple guidelines to prepare you."
- Files (2026-10-20): "do we have our in-house video player and browser too? i know ios frowns against the broowser so we will have to see about that. but the video player, music player(widget is already in and i think full music module), and any other file reader. i want icons to show in files (which should be segregated by file type/category, file origin (uploaded vs generated), and for generated we need a per model segregation (and All)."


## 2026-10-21 (David's words, kept by Claude)

- "Yeah we need proper mobile aspect ratio. And responsive design to match"
- "does our browser in collider have tabs, bookmarks, history, settings, all working? This should all be part of the package since they are stock features"
- "Are you happy with the look of your discover market? ... Evaluate side by side. And just double check all your screens vs the references or any known good reference of your choice. There should be a standard you're aiming to match and exceed and I want to see where you target your expectations"
- "Discover market is just images for now. But Unsplash has shown that can be displayed well. Use that as a reference as well."
- "The config file first needs a makeover. This cyber tech look is hard to read and annoying."
- On "detailed thinking off": "Why should anyone turn off thinking? ... The rest of us don't think thinking is a trivial toggle. It's mandatory"
- "Are model categories in? General image video audio? Do they have their config surfaces? Their options and toolbars and settings and source and reference and queues and generations pane(perhaps collapsible expandable)/Files preview window for that media type?"
- "Grok merely transfers you to the chat window when you hit remix on something. It injects that thing as context or source or reference ... from there it's the same chat window and agent and you type in a prompt. We should be the same ... either bring the chat window to discover or have discover spit us to media gen rather than duplicate value"
- "discover market ... needs to match grok imagine market in terms of color sharpness, layout, design, features, but also needs to extract the cinematic effect. Through dimming the background."
- Premium Theme Market: "dim ... when browsing through locked live wallpapers. Unlocked live wallpapers are fully lit. Thumbnails during browsing are always fully lit and play the preview video in full. Background video is just like the source(unless unlocked, then it's full resolution and no dim)." "lose the music player icons: play, skip track (left and right). And any other leftovers from the music source. Make sure the dim is the same as the source. That was nearly black. And super cinematic."
- "Uploaded songs, like all uploaded files, should open up the app picker so users get to choose where they play the file ... Videos play in this app because we have a full video player, not a full music player ... Collider will never be on that list. It either opens the document/file, or it opens app picker and outsources the effort. Previews still do show in my app though"
- Picture providers: "All 3. Especially a and c" (NVIDIA FLUX and Cloudflare Workers AI first; fal kept).
- Phone link: yes to installing Cloudflare's tunnel.

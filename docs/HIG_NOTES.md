Made by Claude (research subagent), 2026-10-20.

# Collider — HIG design-logic notes (visionOS-style glass over a live environment)

Scope: design logic, purpose, techniques, examples and applications only. Hardware, AR frameworks and code APIs are left out unless they explain a design rule.

How the sources were read:
- Every HIG page below was read in full from Apple's JSON (`/tutorials/data/design/human-interface-guidelines/<page>.json`) on 2026-10-20. Quotes are copied from that text.
- There is no stand-alone "Depth" page (the JSON returned 404). Depth guidance is a section of **Spatial layout** and is quoted from there.
- The WWDC26 session 234 and 320 transcripts, and the WWDC25 session 237 transcript, were read in full from their Apple video pages.
- The Sketch file was opened in a real browser and read through Sketch's own Inspect panel (section 5).
- Anything marked **[unverified]** comes from general knowledge or a third-party source, not from Apple's text.

---

## 1. Human Interface Guidelines — page by page

Hub: https://developer.apple.com/design/human-interface-guidelines/ — The hub's stated purpose is "guidance and best practices that can help you design a great experience for any Apple platform." It is organised into Getting started, Foundations, Patterns, Components, Inputs and Technologies.

### 1.1 Designing for visionOS — https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos
- **Intent:** people "enter an infinite 3D space where they can engage with your app or game while staying connected to their surroundings."
- **Rule: use the minimum immersion that suits each moment.** "For each key moment in your app, find the minimum level of immersion that suits it best — don't assume that every moment needs to be fully immersive."
- **Rule: windows are for tasks.** "Use windows for contained, UI-centric experiences."
- **Comfort rules:**
  - "Avoid displaying motion that's overwhelming, jarring, too fast, or missing a stationary frame of reference."
  - Keep content in the field of view.
  - People should be able to work at rest.

### 1.2 Materials — https://developer.apple.com/design/human-interface-guidelines/materials
- **Intent:** materials create "a sense of depth, layering, and hierarchy between foreground and background elements". By letting background colour pass through, they help people "retain a sense of place."
- **Two layers.**
  - Liquid Glass "forms a distinct functional layer for controls and navigation elements … that floats above the content layer."
  - "**Don't use Liquid Glass in the content layer.**" Use standard materials for content-layer elements such as app backgrounds.
  - Exception: a transient control such as a slider takes on glass only while it is being used.
- **Use glass sparingly.** "Limit these effects to the most important functional elements in your app."
- **Regular vs. clear glass.**
  - Regular "blurs and adjusts the luminosity of background content". Use it where there is a lot of text: alerts, sidebars, popovers.
  - Clear is "highly translucent". "Use this variant for components that float above media backgrounds — such as photos and videos — to create a more immersive content experience."
- **Dimming behind clear glass.** "If the underlying content is bright, consider adding a dark dimming layer of 35% opacity." No dim layer is needed if the content is already dark.
- **Thick vs. thin.**
  - "Thicker materials, which are more opaque, can provide better contrast for text."
  - "Thinner materials … help people retain their context."
- **visionOS specifics.**
  - Windows use an adaptive *glass* that lets "light, the current Environment, virtual content, and objects in people's surroundings show through." It brightens or darkens with what is behind it. There is no Dark Mode; "glass automatically adapts to the luminance of the objects and colors behind it."
  - "**Prefer translucency to opaque colors in windows.** Areas of opacity can block people's view, making them feel constricted."
  - Material roles inside a window:
    - *thin* "brings attention to interactive elements like buttons and selected items"
    - *regular* separates sections such as a sidebar
    - *thick* makes a dark element that stays distinct on top of regular
  - Vibrancy gives three text levels: label, secondaryLabel, and tertiaryLabel (inactive only). Vibrancy "enhances the sense of depth by pulling light and color forward."

### 1.3 Color — https://developer.apple.com/design/human-interface-guidelines/color
- **Intent:** colour should "enhance communication, evoke your brand, provide visual continuity, communicate status and feedback."
- **Glass carries no colour of its own.** "Liquid Glass has no inherent color, and instead takes on colors from the content directly behind it."
- **Colour emphasis on glass.** "Apply color sparingly." To emphasise a primary action, "apply color to the background rather than to symbols or text." Avoid tinting the background of several controls.
- **Colourful backgrounds.** If the background is colourful (as a live wallpaper is), "prefer a monochromatic appearance for toolbars and tab bars."
- **Resting state.** Colourful content can pass under controls while scrolling, but the "resting state … maintains clear legibility."
- **visionOS:**
  - "Use color sparingly, especially on glass."
  - "Prefer using color in bold text and large areas."
  - In full immersion, keep brightness balanced: "avoid displaying a bright object on a very dark or black background, especially if the object flashes or moves."

### 1.4 Depth (section of Spatial layout) — https://developer.apple.com/design/human-interface-guidelines/spatial-layout#Depth
- "**Use depth to communicate hierarchy.**" Example: "when a sheet appears over a window, the window recedes along the z-axis, allowing the sheet to come forward and become visually prominent."
- "**In general, avoid adding depth to text.**"
- "**Make sure depth adds value.**" Depth is good for big separations, such as a toolbar standing off a window, but not for small items. Changing depth often is tiring: "People need to refocus their eyes to perceive each difference in depth."

### 1.5 Windows — https://developer.apple.com/design/human-interface-guidelines/windows
- **Intent:** windows "define the visual boundaries of app content." A *primary* window holds the main navigation. An *auxiliary* window is "dedicated to one experience" and has a close button.
- **Keep the glass.** "**Retain the window's glass background.**" Removing it makes UI "less legible"; an opaque one "obscures people's surroundings and can make a window feel constricting and heavy."
- **Size and shape.**
  - "Choose an initial window size that minimizes empty areas within it."
  - Shape follows content: Keynote opens wide, Safari opens tall.
  - "Choose a minimum and maximum size for each window."
- **New windows.** "Choose the right moment to open a new window … opening new windows excessively creates clutter."
- **Custom chrome.** "Avoid creating custom window UI … without perfectly matching the system's look and behavior can make your app feel broken."
- **Glow to show bounds.** A volume's baseplate shows "a gentle glow around its border when people look at it." This is a gaze-revealed edge glow that helps people find bounds and the resize control.

### 1.6 Ornaments — https://developer.apple.com/design/human-interface-guidelines/ornaments
- **Intent:** an ornament presents controls "without crowding or obscuring the window's contents." It floats "slightly in front of it along the z-axis" and moves with the window. It does not scroll with the content.
- **Rules:**
  - "In general, keep an ornament visible." It can hide "when people dive into a window's content — for example, when they watch a video or view a photo."
  - "Aim to keep an ornament's width the same or narrower than the width of the associated window."
  - "Consider using borderless buttons in an ornament." The glass shows them, and the system adds the hover effect.
  - Limit the number of ornaments to protect "visual balance."
- **Example:** Music keeps Now Playing controls in an ornament.

### 1.7 Spatial layout — https://developer.apple.com/design/human-interface-guidelines/spatial-layout
- "**Center important content within the field of view.** … not displaying distracting motion or bright, high-contrast objects in the periphery."
- "**Avoid anchoring content to the wearer's head**": it makes people "feel stuck, confined."
- "**Avoid displaying too many windows.**"
- **Space around interactive items.** Enough space keeps "the hover effect from crowding other content". Apple's reference is button centres ≥ 60 pt apart with ≥ 16 pt between them. "Don't let controls overlap other interactive elements."

### 1.8 Immersive experiences — https://developer.apple.com/design/human-interface-guidelines/immersive-experiences
- **Intent:** to design experiences "that extend beyond windows and volumes, immersing people in your content." Apps move between the Shared Space and a Full Space.
- **Immersion is a range.**
  - Dim or tint passthrough (the live camera view of the room) "to bring attention to your content … without hiding other apps."
  - *Progressive* immersion partly replaces the surroundings with your environment.
  - *Full* immersion is a 360° environment that "transports people to a new place."
- **Best practices:**
  - "Reserve immersion for meaningful moments and content."
  - **Example:** "people can browse their albums in Photos using a familiar app window … but when they want to examine a single photo, they can temporarily transition to a more immersive experience."
  - **Attention cues:** "Cues like dimming, tinting, motion, scale, and Spatial Audio can help draw people's attention … Start with subtle cues that gently guide people's attention, strengthening the cues only when there's a good reason."
  - "Prefer subtle tint colors … Avoid bright or dramatic tints."
- **Transitions:**
  - "Design smooth, predictable transitions when changing immersion."
  - "**Let people choose when to enter or exit a more immersive experience.** … provide a clear action to enter or exit." **Example:** Keynote's prominent Exit button.
  - "**Indicate the purpose of an exit control.**" Does it go back one level, or quit?
- **Creating an environment:**
  - "**Minimize distracting content.** To help immerse people in a primary task like watching a video, avoid displaying a lot of movement or high-contrast details in your environment."
  - To steer attention, use "the highest quality textures and shapes in the important area while using lower quality assets and dimming in less important areas."
  - "**Keep animation subtle.** Small, gentle movements, like clouds drifting or transforming … Always avoid displaying too much movement near the edges of a person's field of view."
  - "Create an expansive environment … A small, restrictive environment can make people feel uncomfortable."
  - **Sound:** "keep the experience fresh … by avoiding too much repetition or looping. If people can play other audio … be sure to lower the volume of the soundscape or stop it completely."
  - "In general, avoid using a flat 360-degree image to create your environment … it can reduce the immersiveness." "Always provide a ground plane."
  - "Minimize asset redundancy."

### 1.9 Motion — https://developer.apple.com/design/human-interface-guidelines/motion
- **Intent:** "Beautiful, fluid motions bring the interface to life, conveying status, providing feedback and instruction."
- **Purpose and control:**
  - "**Add motion purposefully** … Don't add motion for the sake of adding motion."
  - "**Make motion optional.**"
  - "**Let people cancel motion.**"
- **Realism:** "**Strive for realistic feedback motion that follows people's gestures and expectations.**" **Example:** a view revealed by sliding down should not be dismissed by sliding sideways.
- **Brevity:** "**Aim for brevity and precision in feedback animations.**" **Example:** a Photos panorama "quickly and smoothly expands to fill the space in front of them."
- **Frequency:** "In apps, generally avoid adding motion to UI interactions that occur frequently."
- **visionOS:**
  - "avoid displaying motion at the edges of a person's field of view."
  - When a large object moves, "increase the object's translucency … or lower its contrast."
  - "**Consider using fades when you need to relocate an object.**"
  - "Consider giving people a stationary frame of reference."
  - "Avoid showing objects that oscillate in a sustained way … around 0.2 Hz."

### 1.10 Layout — https://developer.apple.com/design/human-interface-guidelines/layout
- **Intent:** the layout gives "the structure for people to understand your content."
- **Rules:**
  - "**Differentiate controls from content.** … Instead of applying a solid or semi-opaque background color beneath controls, use a scroll edge effect to visually elevate controls above content."
  - "For full-screen background content, be sure to extend it underneath sidebars, toolbars, and tab bars to fit the entire screen or window."
  - **Background extension effect:** if a panel would cover the important part of a background image, the image can be mirrored and blurred beneath the panel.
  - "When necessary, scale background artwork … don't change the aspect ratio of the artwork; instead, scale it so that it fills the screen completely." Background art may need to extend past the usual visible area because windows can be very wide or very tall.
  - "Use progressive disclosure."
- **visionOS:**
  - Keep content horizontally centred at large sizes.
  - "**Display supplemental content in an adjacent window, not in an ornament.**"

### 1.11 Typography — https://developer.apple.com/design/human-interface-guidelines/typography
- **visionOS:**
  - "**In general, prefer 2D text.**"
  - "By default, the system displays text in white" on glass for contrast.
  - "If you need to display text that's not on a background, consider making it bold … avoid adding shadows."
  - visionOS uses bolder body and title styles, plus Extra Large Title 1 and 2 "for wide, editorial-style layouts."

### 1.12 Buttons — https://developer.apple.com/design/human-interface-guidelines/buttons
- **Intent:** "A button initiates an instantaneous action."
- **General rules:**
  - "**Always include a press state for a custom button.** Without a press state, a button can feel unresponsive."
  - Keep prominent buttons to "one or two per view."
  - "Use style — not size — to visually distinguish the preferred choice."
- **visionOS:**
  - Four interaction states, from the image captions on the page: **Idle, Hover, Selected, Unavailable**.
  - "In visionOS, buttons don't support custom hover effects."
  - A button on a glass window uses the *thin* material. A button floating in space uses *glass*.
  - "**Avoid creating a custom button that uses a white background fill and black text or icons.** The system reserves this visual style to convey the toggled state."
  - "**In general, prefer circular or capsule-shape buttons.** People's eyes tend to be drawn toward the corners in a shape."
  - Use rounded rectangles in vertical stacks and capsules in horizontal rows.
  - Buttons play sound because visionOS has no haptics.
  - Tooltips appear after a short look.

### 1.13 Eyes — hover and highlight design logic — https://developer.apple.com/design/human-interface-guidelines/eyes
- **Intent:** looking at an element is how people target it. "visionOS highlights it, providing visual feedback that helps them confirm the item is one they want. The visual feedback, or _hover effect_, shows people that they can use an indirect gesture."
- **Rules:**
  - "**Minimize visual distractions.** … revealing content near a button people are looking at can cause them to involuntarily look at the new content."
  - "**In general, give an interactive item a rounded shape.**"
  - For multi-part controls, "provide an overall containing shape that visionOS can highlight."
  - "Consider using subtle visual cues … gentle motion, increased contrast, or variations in color or scale … prefer cues that are noticeable without being flashy or harsh."
  - "Avoid using a repeating pattern or texture that fills the field of view."
- **Custom hover effects:**
  - Use them "to emphasize or enhance a special moment". Too many "can dilute the impact … and even cause visual discomfort."
  - **Delays:**
    - none: subtle effects, such as a slider knob appearing
    - short: for example, tab-bar expansion
    - long: tooltips
  - "**Aim to keep one or more of the element's primary views unchanged in both states**" so people can follow the change.
- **Focus vs. hover:** a keyboard or controller focus effect is a separate system from the hover effect (Focus and selection page).

### 1.14 Related lift/glow logic (tvOS focus) — https://developer.apple.com/design/human-interface-guidelines/images#Parallax-effect
- "As an element comes into focus, the system elevates it to the foreground, gently swaying it while applying illumination that makes the element's surface appear to shine. After a period of inactivity, out-of-focus content dims and the focused element expands."
- "**Keep layering simple and subtle.** Parallax is designed to be almost unnoticeable."
- This is Apple's own description of lift plus glow on focus.

### 1.15 Scroll views — fades at edges (special focus a) — https://developer.apple.com/design/human-interface-guidelines/scroll-views
- **Purpose:** a *scroll edge effect* "provides a visual separation between certain interface elements, such as toolbars, and the scrolling content area behind them." Its styles are automatic, soft and hard.
- "**Only use a scroll edge effect when a scroll view is behind floating interface elements.** Scroll edge effects aren't decorative. They don't block or darken like overlays; they exist to ensure controls stay visually distinct."
- "**Apply one scroll edge effect per view.**" In split views, keep the effects consistent in height.
- "Prefer the automatic scroll edge effect style." It becomes more opaque for bars that are busy or full of text.
- **Signal hidden content.** "displaying partial content at the edge of a view indicates that there's more content in that direction."
- **visionOS Look to Scroll:**
  - "Scrolling starts when people look near the boundary of the scroll view."
  - "prefer making the view the full width or full height of the window … provides clear edges."
  - "If your app uses custom scroll effects or animations, remove them before supporting Look to Scroll."
- **visionOS toolbar** (Toolbars page — https://developer.apple.com/design/human-interface-guidelines/toolbars): "To maintain the legibility of toolbar items as content scrolls behind them, visionOS uses a variable blur in the bar background. The variable blur anchors the bar above the scrolling content while letting the view's glass material remain uniform and undivided."
- **Materials page:** "Scroll edge effects further enhance legibility by blurring and reducing the opacity of background content."
- **Toolbars page:** "Reduce the use of toolbar backgrounds and tinted controls … use a ScrollEdgeEffectStyle when necessary."
- **Summary of how edge fades behave in Apple's logic:**
  - They sit only where content passes under a floating control layer (top bar, bottom toolbar or composer).
  - They are a progressive blur plus an opacity drop, not a dark band. The glass above them stays one continuous surface.
  - They lead focus by keeping the controls readable and the content's resting state clear.
  - Partial content at an open edge invites scrolling.
  - There is one fade per view, never decorative, and never on every edge.

### 1.16 Menus — https://developer.apple.com/design/human-interface-guidelines/menus
- **Intent:** "a space-efficient way to present commands."
- **Rules:**
  - "Prefer listing important or frequently used menu items first."
  - "Be mindful of menu length."
  - "**Use submenus sparingly.**" Limit them to one level and about five items.
- **visionOS:**
  - "**Prefer displaying a menu near the content it controls.**"
  - When a menu overlaps 3D content, use the *subtle* "breakthrough" effect, which "blends the presentation with its surrounding content … while preserving the depth and context of the scene." The *prominent* effect "can disrupt the experience … and potentially cause discomfort."

### 1.17 Lists and tables — https://developer.apple.com/design/human-interface-guidelines/lists-and-tables
- "Prefer displaying text in a list or table."
- "Keep item text succinct."
- "Provide appropriate feedback when people select a list item." A navigating list keeps the selected row highlighted; a list of options highlights a row only briefly.
- No visionOS-specific section.

### 1.18 Modality, Sheets, Popovers, Alerts — the pause-menu logic
- **Modality** (https://developer.apple.com/design/human-interface-guidelines/modality):
  - "Present content modally only when there's a clear benefit."
  - "Aim to keep modal tasks simple, short, and streamlined."
  - "avoid creating a modal experience that feels like an app within your app."
  - "Always give people an obvious way to dismiss a modal view."
  - "Let people dismiss a modal view before presenting another one."
- **Sheets** (https://developer.apple.com/design/human-interface-guidelines/sheets):
  - visionOS: "it floats in front of its parent window, dimming it, and becoming the target of people's interactions."
  - "**Avoid displaying a sheet that emerges from the bottom edge of a window.** … prefer centering it in their field of view."
  - "**Present a sheet in a default size that helps people retain their context.** Avoid displaying a sheet that covers most or all of its window."
  - "Display only one sheet at a time."
  - Pair Done with Cancel or Back, but never show all three.
- **Popovers** (https://developer.apple.com/design/human-interface-guidelines/popovers):
  - "**Avoid making a popover too big.** Make a popover only big enough to display its contents and point to the place it came from."
  - "Show one popover at a time … Never show a cascade."
  - "Always save work when automatically closing a nonmodal popover."
  - When resizing, "animate the change to avoid giving the impression that a new popover replaced the old one."
- **Alerts** (https://developer.apple.com/design/human-interface-guidelines/alerts):
  - "Use alerts sparingly."
  - "Avoid showing an alert when your app starts."
  - In visionOS an alert sits "slightly forward along the z-axis" and stays anchored to its window.

### 1.19 Feedback — https://developer.apple.com/design/human-interface-guidelines/feedback
- **Intent:** feedback "helps people know what's happening." "The most effective feedback tends to match the significance of the information to the way it's delivered."
- **Rules:**
  - "Consider integrating status feedback into your interface."
  - Confirm only significant completions: "they only need to know when it doesn't" succeed.

### 1.20 Playing video — environment vs. media (special focus c) — https://developer.apple.com/design/human-interface-guidelines/playing-video
- **Intent:** "People expect to enjoy rich video experiences."
- **Rules:**
  - "Use the system video player … If your app truly requires a custom video player, reference the behavior and interface of the system video player."
  - "Always display video content at its original aspect ratio."
  - In visionOS, transport controls are an ornament.
- **visionOS comfort:** let people choose when playback starts, use "a small window for playback," and make sure "people can see their surroundings during playback."
- "**Avoid automatically starting a fully immersive video playback experience.**"
- "**Avoid expanding an inline video player to fill a window.** … you want to make sure that window content remains visible around the player so people don't expect a more immersive playback experience."
- **Decorative video:** "Use a RealityKit video player if you need to play video in a view like a splash screen or a transitional view … people generally expect the video to lead into the next experience, so they don't need playback controls." Apple separates decorative/ambient video, which has no controls, from watched media, which has controls.
- **tvOS:** "Defer to content when displaying logos or noninteractive overlays above video … prefer translucent graphics."
- **Going full screen** (https://developer.apple.com/design/human-interface-guidelines/going-full-screen):
  - visionOS has no full-screen mode; people "expand a window … or use the Digital Crown … to transition to a more immersive experience."
  - "Prioritize content by temporarily hiding toolbars and navigation controls … let people restore the hidden elements with a familiar gesture."
  - "Let people choose when to exit full-screen mode."

### 1.21 Images — https://developer.apple.com/design/human-interface-guidelines/images
- "**Prefer the feathered glass background effect to display text over spatial photos.** … adds contrast to make the text readable, and it blurs out detail."
- "**When displaying immersively, prefer minimal UI.**" **Example:** Spatial Gallery shows "a single piece of content with a small caption and a single Back button."
- "Display spatial photos and spatial scenes in standalone views."

### 1.22 Icons and app icons — https://developer.apple.com/design/human-interface-guidelines/app-icons
- A visionOS icon has a background layer plus one or two layers on top. Together they produce "a three-dimensional object that subtly expands when people view it." The system adds the shadows and the embossing.
- "**Let the system handle blurring and other visual effects** … there's no need to include specular highlights, drop shadows between layers, beveled edges, blurs, glows."
- "Prefer clearly defined edges in foreground layers."
- "Vary opacity in foreground layers to increase the sense of depth."
- From the Icons page: "Prefer simple, recognizable symbols."

### 1.23 Accessibility (visual parts only) — https://developer.apple.com/design/human-interface-guidelines/accessibility
- **Contrast:** WCAG AA. Text up to 17 pt needs 4.5:1; 18 pt or bold needs 3:1. In visionOS the default text size is 17 pt and the minimum is 12 pt.
- **Reduce Motion:**
  - "reducing automatic and repetitive animations, including zooming, scaling, and peripheral motion"
  - "Replacing transitions in x-, y-, and z-axes with fades"
  - "Avoiding animating into and out of blurs"
  - "Tightening animation springs"
- "Allow people to opt out of flashing lights in video playback."
- **visionOS:** "Reduce the speed and intensity of animated objects, particularly in someone's peripheral vision. Be gentle with camera and video motion."

### 1.24 Gestures — press and highlight logic — https://developer.apple.com/design/human-interface-guidelines/gestures
- An indirect gesture works like this: people "look at a button to focus it and select it by quickly tapping their finger and thumb together."
- The page's recording shows the button becoming highlighted on look, then activating on tap. The sequence is **look → highlight → press → action**.
- "Support standard gestures everywhere you can."

---

## 2. WWDC26 session 234 — "Design immersive environments for visionOS apps and the spatial web"

Link: https://developer.apple.com/videos/play/wwdc2026/234/

Speaker: Michael Breymann, Human Interface Designer at Apple.

**Opening purpose statement (near-verbatim):**
> "In visionOS, system environments are more than simple backdrops. They are photo-realistic natural landscapes, designed for spatial computing, that transport you to a different time and place. … But unlike flat media or a panoramic image, which does not respond to changes in perspective, this environment offers true depth and parallax, giving someone the same experience they would see in the real world. When you combine this with motion and audio, the scene feels alive, and it immerses the viewer in the space."

**Design concepts and techniques:**

- **Start from intent.** Ask: "Why are we building this particular environment? What are the qualities we want to bring to life? And how is the viewer going to use this space?"
- **Use case shapes the build.**
  - **Media viewing:** "watching media in large format … We wanted the media experience to feel cinematic, so we sculpted the terrains to fit a large screen, and researched the optimal center line for viewing."
  - **Keynote rehearsal:** "sound is intentionally absent, to keep them focused, and the lighting is concentrated on the stage."
  - Other uses: an environment can be "a backdrop for your app's content" or showcase a web experience.
- **Composition.**
  - Pick the primary viewpoint, and think about what is visible behind the viewer.
  - Remove what breaks the scene: roads, people, footprints, a too-busy midground, dominant bushes.
  - Framing a "clear shot into the mid-distance" is ideal. "You can always add detail into the foreground … but it's much harder to remove things that obstruct the view."
- **Layering.** "visualize your environment in terms of layers, building from the background to the foreground. Identify which scene elements will need to have motion, and start thinking about what spatial audio you can attach to them."
- **Iteration finds features.** Building a solar-system model for Jupiter led to the "passage of time" becoming a requirement.
- **Fidelity.**
  - Capture more resolution than needed. Apple's reference target is about 40 px per degree, roughly a 14,400 × 7,200 panorama.
  - Keep sharpness consistent so scale reads correctly.
  - Check the work by A/B comparison, by flopping the image (mirroring it), and by testing extreme gamma and gain.
- **Motion techniques (cheap but alive):**
  - Clouds evolve along UV flow maps (images that steer texture movement), "weighting the flow speed in different parts of the sky" so it feels massive.
  - Cloud shadows are "a scrolling mask that darkens the terrain textures," matched to cloud speed and direction.
  - Dense palm shadows are pre-rendered flip-book textures.
  - Palm fronds sway with "hierarchical vertex animation and layered sine waves. By stacking low frequency and high frequency motion, you can create variety that is never repetitive."
  - Water shifts "hue saturation and brightness modulated over time." Waves are built from layered normal maps and scrolling textures. "The sum of these effects, is greater than its parts."
  - "Counterintuitively, it's often the case that less is more."
- **Sound.** Spatial audio emitters are attached to the source of motion, for example rippling water at the rocks.
- **Closing principles:**
  - "Be intentional with everything you do. You should be able to explain the reasoning behind everything you add or remove."
  - "Create a composition that works. Every scene element should feel like it belongs."
  - "all aspects of the scene should be tied together with sound and motion."
  - "Often the best way to know your designs are working, is to try to break them."

**Applications named:** a cinematic media-viewing backdrop, a focused rehearsal stage, a backdrop for an app's content, website environments, and SharePlay experiences.

Skipped (tooling and hardware): camera rig heights, bracketing, LiDAR and photogrammetry, Macbeth charts, and real-time rendering budgets beyond the design point.

---

## 3. WWDC26 session 320 — the immersive web API

Link: https://developer.apple.com/videos/play/wwdc2026/320/ ("Explore immersive website environments in visionOS"). Context: WWDC25 session 237, https://developer.apple.com/videos/play/wwdc2025/237/

**What it does for the user.** A web page can take the visitor into a 3D environment while the page stays visible: the immersive API "transports the model element beyond the browser bounds while keeping the page visible." Fullscreen, by contrast, "replaces the web page content with the provided element." Both can run at once: "you can have a fullscreen video player while being immersed in a virtual environment" (video docking: the video moves onto a screen inside the environment; when it ends, the site comes back).

| Fullscreen API | Immersive API (session 320) |
|---|---|
| `element.requestFullscreen()` | `model.requestImmersive()`, called from a user action |
| `document.exitFullscreen()` | an exit call exists; exact name **[unverified]** |
| `document.fullscreenEnabled` | `document.immersiveEnabled` (feature detection; the entry button shows only when true) |
| `document.fullscreenElement` | `document.immersiveElement` |
| `fullscreenchange` / `fullscreenerror` | `immersivechange` plus an error event (name **[unverified]**) |
| `:fullscreen` CSS pseudo-class | `:immersive` CSS pseudo-class |

Entering is a promise (show a loading cue, hide it in `finally`); a clear exit button: "It's always good to present a clear exit affordance"; the system can exit at any time, so listen for state changes.

**For Collider (Flutter web in a Windows WebView2 window, and phones):** the API exists only in Safari on visionOS; elsewhere `document.immersiveEnabled` is false, so nothing appears. The standard Fullscreen API works in Chromium; in WebView2 the host app handles the request **[unverified detail]**. What is worth taking is the logic, built as app state in Flutter: one explicit entry action, one state flag driving the layout, a visible exit plus Esc/back, a loading cue, feature detection, and docking media inside the environment rather than replacing it.

---

## 4. Libraries and APIs (pub.dev data, 2026-10-20)

| Need | Package / API | What it does | Licence | Fits Flutter? |
|---|---|---|---|---|
| Looping 2K background video | media_kit — https://pub.dev/packages/media_kit | libmpv player; Android, iOS, Windows, Linux, macOS, web | MIT | Yes; strongest for Windows |
| Background video | video_player — https://pub.dev/packages/video_player | Official player | BSD-3 | No Windows on pub.dev; video_player_win (BSD-3) adds it |
| Matched music loop | just_audio — https://pub.dev/packages/just_audio | Gapless/looping audio | Apache-2.0 / MIT | No Windows listed |
| Edge fade (opacity) | ShaderMask + LinearGradient (dstIn) | Built in | SDK | Yes |
| Edge fade (opacity) | fading_edge_scrollview — https://pub.dev/packages/fading_edge_scrollview | Fades only the edge where more content exists | BSD-3 | Yes |
| Progressive blur at edges | soft_edge_blur — https://pub.dev/packages/soft_edge_blur ; progressive_blur — https://pub.dev/packages/progressive_blur | Variable blur at one or more edges | MIT | Yes |
| Glass | BackdropFilter + ImageFilter.blur ; glass_kit (MIT) ; liquid_glass_renderer (1.0.0-dev, licence **[unverified]**) | Frosted glass | — | Yes / test first |
| Custom shaders | flutter_shaders — https://pub.dev/packages/flutter_shaders | Fragment shader helpers | BSD-3 | Yes |
| Hover / press / glow | MouseRegion, AnimatedScale, BlendMode.plus ; flutter_animate (BSD-3) | Highlight, press, additive glow | — | Yes |
| Summoned overlays | OverlayPortal, showGeneralDialog, ModalBarrier ; animations (BSD-3) ; flutter_portal (MIT) | Pause-menu overlays, anchored popovers | — | Yes |
| Desktop window | window_manager (MIT) ; flutter_acrylic (MIT) ; webview_windows (BSD-3) | Full screen, Mica/Acrylic, WebView2 | — | Desktop |

Apple's own web glass recipe (WWDC25 237): `backdrop-filter: blur(20px)` plus `linear-gradient(to right, rgba(240,240,240,0.8), rgba(240,240,240,0.5) 4px)`; the first 4 px act as "a specular highlight on the edge to give a sense of thickness."

---

## 5. The Sketch link — button hover

Link: https://www.sketch.com/s/eb13bfe1-2ddb-4f87-b92c-740a36abed7a/f/1DEC3682-3B90-4B1C-8C22-78AEA768CDB2 — Apple's visionOS UI Kit, frame "Views/Alerts/x/Buttons/Default Action – Hover", read through Sketch's Inspect panel.
1. **Base plate:** #FFFFFF at 8%, blend Plus Lighter, corner radius 12, padding 20 × 11. Idle uses the identical fill.
2. **"Look Glow" (hover):** solid #FFFFFF, layer opacity 15%, blend Plus Lighter, Gaussian blur radius 16.32, roughly the button's size and offset slightly right; reads as a soft radial bloom.
3. **Selected:** solid white 100%, shadow 0 3 5 black 12% (the state the HIG reserves for toggled).

Design logic: the glow is additive light, not a colour, so it works over any wallpaper. That it follows the gaze is an inference **[unverified]**. Flutter: a blurred white layer with BlendMode.plus at low opacity, clipped to the control, placed under the pointer on desktop and under the finger on a press (applied in VPress, 2026-10-20).

---

## 6. Apply to Collider

1. Keep every window translucent glass over the environment; never an opaque panel. ("Prefer translucency to opaque colors in windows"; "Retain the window's glass background.")
2. Controls on glass; chat content on a quieter material, no glass on message bubbles. ("Don't use Liquid Glass in the content layer.")
3. Clear glass for chrome over the wallpaper; a dark dim only when the wallpaper frame is bright ("consider adding a dark dimming layer of 35% opacity", as intent, not a fixed number).
4. Behind the composer and header: a progressive blur plus an opacity fall-off on the scrolling chat, the glass above uniform. ("uses a variable blur in the bar background … uniform and undivided"; "Instead of applying a solid or semi-opaque background color beneath controls, use a scroll edge effect.")
5. Edge fades only where content continues; not decoration, not on every side. ("Scroll edge effects aren't decorative"; "Apply one scroll edge effect per view.") Applied 2026-10-20 in EdgeFade.
6. A partly visible next item at an open edge instead of a hard cut. ("displaying partial content at the edge of a view indicates that there's more content in that direction.")
7. Pause-menu overlays centred, sized to content, the parent dimming and receding; never full-width, never rising from the bottom on desktop. (Sheets, Spatial layout.)
8. One overlay at a time; no cascades. ("Let people dismiss a modal view before presenting another one"; "Never show a cascade.")
9. Every control: Idle, Hover, Pressed/Selected, Unavailable; hover = Look Glow; press visibly responds; solid white only for toggled. ("Always include a press state for a custom button.")
10. Keep a control's label or glyph steady on hover; animate only the light or lift. ("keep one or more of the element's primary views unchanged in both states.")
11. Rounded or capsule targets; one containing highlight shape for multi-part rows. (Eyes.)
12. Room around targets so the bloom never touches a neighbour (Apple's reference ≥ 60 pt between centres, as intent).
13. Wallpaper motion slow, layered, away from the frame edges; low and high frequencies stacked so loops don't read as loops; no sustained pulsing near 0.2 Hz. (Immersive experiences; WWDC26 234; Motion.)
14. Each paid environment with a calm, low-contrast zone where the chat window sits; detail and motion elsewhere. (Immersive experiences.)
15. Duck or stop the environment's music when any other audio plays (voice chat, video, read-aloud); avoid obvious short loops.
16. Fade, don't fly, when windows relocate or swap; under Reduce Motion use cross-fades and don't animate into or out of blur.
17. White text on glass; bold rather than shadows for text directly on the environment; flat text.
18. Controls monochrome over a colourful wallpaper, accent colour on the primary action's background. (Color.) Note: David asked for coloured icons across the app; recorded as DEVIATIONS D76.
19. The environment extends under all chrome to the window edges, scaled to cover without changing its aspect ratio; the UI windows stay inset.
20. Immersive (chrome hidden, environment forward) only by an explicit action, with an exit control that says where it goes, plus Esc or back.

### Product question — paid live wallpapers vs. an immersive mode with the user's own videos and photos

Apple treats an **environment** (a designed, persistent place behind tasks: calm composition, matched sound, subtle motion) and **media** (content people choose to watch, with controls, that makes the environment's sound duck) as different jobs. Photos goes immersive only "when they want to examine a single photo," with minimal UI and one Back button, then returns.

Proposal: paid environments stay the only ambient background. Personal videos and photos become a viewing moment the person starts: the chat recedes and dims, the media plays large with its controls, the environment's music ducks, an exit returns to the environment; where it fits, the video can dock inside the current environment, which makes the paid environment the theatre. If personal media were allowed as a permanent backdrop, it would replace the paid product directly. In a flat app the depth-and-parallax argument does not apply, so the difference rests on craft (composition, motion, matched sound, legibility behind glass) and on moment-versus-place behaviour.

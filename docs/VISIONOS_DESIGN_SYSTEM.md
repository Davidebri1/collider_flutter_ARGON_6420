# visionOS design system: the rules Collider follows

Read from Apple's Human Interface Guidelines, September 2025 edition, plus the visionOS
developer pages. Every rule below is quoted from Apple. The last section says what Collider
does today and what has to change.

The point of this document is that "visionOS" is not a mood. It is a set of decisions about
materials, colour, depth and space, and they are written down. A design decision that cannot be
traced back to one of these rules is a preference, and preferences are where this app drifts.

---

## 1. The material is the environment

> "In visionOS, windows generally use an unmodifiable system-defined material called *glass* that
> helps people stay grounded by letting light, the current Environment, virtual content, and
> objects in people's surroundings show through. Glass is an adaptive material that limits the
> range of background color information so a window can continue to provide contrast for app
> content while becoming brighter or darker depending on people's physical surroundings and other
> virtual content."
>
> "Note: visionOS doesn't have a distinct Dark Mode setting. Instead, glass automatically adapts
> to the luminance of the objects and colors behind it."
>
> — HIG, Materials

> "Retain the window's glass background. The default glass background helps your content feel
> like part of people's surroundings while adapting dynamically to lighting and using specular
> reflections and shadows to communicate the window's scale and position. Removing the glass
> material tends to cause UI elements and text to become less legible and to no longer appear
> related to each other; using an opaque background obscures people's surroundings and can make a
> window feel constricting and heavy."
>
> — HIG, Windows, visionOS

**What this means for Collider.** The living wallpaper is the environment. The glass is not a
style applied on top of it, it is the environment seen through a filter. A pane that cancels the
wallpaper's colour has stopped being glass and become a grey card.

The reason the app looks drab is mechanical, not aesthetic: the material fill is a flat mid grey
(`#808080` at 30 percent, `VColors.glassElevated`, `glassModal`, `glassWork`). Grey at 30 percent
multiplies the background's colour down and desaturates it. Over the blue and amber cockpit
wallpaper, every pane in the app becomes the same neutral grey, and the colour of the real world
is cancelled in exactly the place the app is asking you to look.

A white wash at the same density does the opposite. It lifts the blacks, keeps the hue, and the
wallpaper's blue stays blue and its amber stays amber. That is the whole difference between a
grey app and a colourful one, and it is one token.

## 2. Glass is the functional layer, not the content

> "Liquid Glass forms a distinct functional layer for controls and navigation elements — like tab
> bars and sidebars — that floats above the content layer, establishing a clear visual hierarchy
> between functional elements and content."
>
> "**Don't use Liquid Glass in the content layer.** Liquid Glass works best when it provides a
> clear distinction between interactive elements and content, and including it in the content layer
> can result in unnecessary complexity and a confusing visual hierarchy. Instead, use standard
> materials for elements in the content layer, such as app backgrounds."
>
> — HIG, Materials

> "Use standard materials and effects — such as blur, vibrancy, and blending modes — to convey a
> sense of structure in the content beneath Liquid Glass."
>
> — HIG, Materials, Standard materials

**What this means for Collider.** The app has one material and uses it for everything: the dock,
the side nav, the ticker window, the Files window, the market, the reading view. Apple splits it
in two.

- **Functional layer, glass:** the dock, the contextual side nav, the pinned prompt, the composer.
  These float above the content and they are controls. They get the glass treatment.
- **Content layer, standard materials:** the ticker window, the Files window, the market, the
  reading view. These are the work. They get regular, thin and thick materials and they let the
  wallpaper through with less distortion, because the content inside them has to stay readable.

The material scale Apple defines for this, and what it is for:

|Material | Apple's use | Collider's use |
|---|---|---|
| ultraThin | full screen views that want a light scheme | the wallpaper layer itself |
| thin | brings attention to interactive elements, buttons and selected items | the selected tab, the active row, the round controls |
| regular | separates sections, a sidebar or grouped table | the ticker window, the Files window |
| thick | a dark element that stays distinct on top of a regular background | the modal menus and the market's overlay |

The current code has no thin, no thick, and no ultraThin. It has one grey at three densities.

## 3. Vibrant colour on top of materials

> "To ensure foreground content remains legible when it displays on top of a material, visionOS
> applies vibrancy to text, symbols, and fills. Vibrancy enhances the sense of depth by pulling
> light and color forward from both virtual and physical surroundings."
>
> "visionOS defines three vibrancy values that help you communicate a hierarchy of text, symbols,
> and fills. Use *label* for standard text. Use *secondaryLabel* for descriptive text like
> footnotes and subtitles. Use *tertiaryLabel* for inactive elements, and only when text doesn't
> need high legibility."
>
> — HIG, Materials, visionOS

> "Help ensure legibility by using vibrant colors on top of materials. When you use system-defined
> vibrant colors, you don't need to worry about colors seeming too dark, bright, saturated, or low
> contrast in different contexts. Regardless of the material you choose, use vibrant colors on top
> of it."
>
> — HIG, Materials

**What this means for Collider.** `textPrimary` at 100 percent, `textSecondary` at 70 and
`textTertiary` at 45 white are the three levels Apple defines, and that part is right. What is
missing is that vibrancy means the colour is pulled from the surroundings, so white on a blue
environment is very slightly blue. A fixed white is the flat version of vibrant, and flat white
on a grey wash is the drab look.

## 4. Where colour belongs

> "By default, Liquid Glass has no inherent color, and instead takes on colors from the content
> directly behind it. You can apply color to some Liquid Glass elements, giving them the appearance
> of colored or stained glass. This is useful for drawing emphasis to a specific control, like a
> primary call to action, and is the approach the system uses for prominent button styling."
>
> "**Apply color sparingly to the Liquid Glass material, and to symbols or text on the material.**
> If you apply color, reserve it for elements that truly benefit from emphasis, such as status
> indicators or primary actions. To emphasize primary actions, apply color to the background
> rather than to symbols or text."
>
> — HIG, Color, Liquid Glass color

> "**Prefer using color in bold text and large areas.** Color in lightweight text or small areas
> can make them harder to see and understand."
>
> — HIG, Color, visionOS

> "Use color sparingly, especially on glass... Prefer using color in places where it can help call
> attention to important information or show the relationship between parts of the interface."
>
> — HIG, Color, visionOS

**What this means for Collider.** Colour is not decoration here, it is a signal, and Apple is
strict about where it may go.

- **Status:** the consensus score, red through green, is a status indicator. It is a bold element
  and it earns its colour.
- **Identity:** the provider tint on each model row says which company answered. That is a
  relationship between parts of the interface, which is exactly what Apple says colour is for.
- **Primary action:** the buy button in the market. Colour goes on the background of the primary
  action, not on its label.

Everything else stays monochrome. That is not drabness, that is the system working. The colour in
this app comes from the environment and from the things it is about.

## 5. Windows and their size

> "Choose an initial window size that minimizes empty areas within it... Too much empty space
> inside a window can make it look unnecessarily large while also obscuring other content in
> people's space."
>
> "Choose an initial shape that suits a window's content."
>
> — HIG, Windows

> "**Avoid displaying too many windows.** Too many windows can obscure people's surroundings,
> making people feel overwhelmed, constricted, and even uncomfortable."
>
> — HIG, Spatial layout

> "**Prefer translucency to opaque colors in windows.** Areas of opacity can block people's view,
> making them feel constricted and reducing their awareness of the virtual and physical objects
> around them."
>
> — HIG, Materials, visionOS

**What this means for Collider.** Every pane is a window over the environment. It is translucent,
it is sized to what it holds, and it never becomes an opaque block.

## 6. Ornaments

> "An ornament floats in a plane that's parallel to its associated window and slightly in front of
> it along the z-axis."
>
> "**Aim to keep an ornament's width the same or narrower than the width of the associated
> window.** If an ornament is wider than its window, it can interfere with a tab bar or other
> vertical content on the window's side."
>
> "**Consider using borderless buttons in an ornament.** By default, an ornament's background is
> glass, so if you place a button directly on the background, it may not need a visible border."
>
> "**If you need to display multiple ornaments, prioritize the overall visual balance of the
> window.**"
>
> — HIG, Ornaments

**What this means for Collider.** The dock and the side nav are ornaments of the ticker window.
They are glass, they float in front, and the dock must not be wider than the window it belongs
to. The ticker window is 244 points wide on a phone and the dock is 260. The ornament is wider
than its window.

## 7. Depth

> "**Use depth to communicate hierarchy.**"
>
> "**In general, avoid adding depth to text.** Text that appears to hover above its background is
> difficult to read."
>
> "**Make sure depth adds value.** ... People need to refocus their eyes to perceive each
> difference in depth, and doing so too often or quickly can be tiring."
>
> — HIG, Spatial layout

> "Include enough space around interactive components to be easy for people to look at... place
> multiple, regular-size buttons so that their centers are at least 60 points apart, leaving 16
> points or more of space between them."
>
> — HIG, Spatial layout

**What this means for Collider.** Depth is a hierarchy tool, used a few times and deliberately.
Every surface floating at a different depth is not depth, it is noise, and it tires the eye.

---

## Where Collider stands against these rules

| Rule | Today | Fix |
|---|---|---|
| Material takes the environment's colour | `glassElevated`, `glassModal`, `glassWork` are all `#808080` at 30 percent. Grey cancels the wallpaper's hue. | White-tinted glass at the same density. The wallpaper's blue stays blue. |
| Glass is the functional layer | Every surface is the same glass, including the content windows. | Dock, side nav, composer keep glass. The ticker, Files, market and reading view move to regular, thin and thick. |
| Material thickness is semantic | No thin, no thick, no ultraThin. One grey at three densities. | Add the three thicknesses with the jobs Apple gives them. |
| Vibrant colour on materials | Flat white at three alphas. | Keep the three levels, tint them with the environment. |
| Colour marks status and primary actions | The consensus score and the provider tints are right. The market's buy button is a plain chip. | Give the primary action the accent, on the background. |
| Windows are translucent and sized to their content | The Files window is an opaque white panel, 480 wide on a 393 phone with a clipped price row. | Glass window, sized to its content, price row on screen. |
| Ornaments are no wider than their window | The dock is 260 on a 244 window. | Dock width follows the window. |

## The words used in this app

"Window", "ornament", "pane", "material", "vibrancy", "tint". These are Apple's words for what
is on screen and they are the words in the code. They are not marketing.

## Sources

- HIG, Materials: https://developer.apple.com/design/human-interface-guidelines/materials
- HIG, Color: https://developer.apple.com/design/human-interface-guidelines/color
- HIG, Windows: https://developer.apple.com/design/human-interface-guidelines/windows
- HIG, Ornaments: https://developer.apple.com/design/human-interface-guidelines/ornaments
- HIG, Spatial layout: https://developer.apple.com/design/human-interface-guidelines/spatial-layout
- HIG, Designing for visionOS: https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos
- visionOS platform: https://developer.apple.com/visionos/

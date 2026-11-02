# Gate

Nothing creative starts until this page is complete. It exists because work that looked finished kept failing on understanding, not on skill.

## 1. Five Whys

Ask "why" of the request until the answer is a human outcome, not a feature. Write each answer as one sentence.

Example for "make overlays compact":

1. Why compact? So the overlay does not replace the screen.
2. Why must it not replace the screen? Because the content behind it is what the user came for.
3. Why does that matter during an overlay? Because the user is making a brief decision about that content, and needs to still see it.
4. Why brief? Because an overlay is a pause, not a destination.
5. Why a pause? Because the app's value is the conversation and the wallpaper, and everything else serves them.

The fifth answer is the requirement. The first answer was only a symptom of it.

## 2. Research

About 15 minutes, before any code:

- Open the live Figma frames and export them. Look at spacing, depth, edge fades, how elevation changes with position.
- Open the reference screenshots.
- Run the current app and screenshot every screen you will touch.
- Find how the best examples solve the same problem, beyond the references given.

## 3. Understanding tier

| Tier | You can | Evidence |
| --- | --- | --- |
| 1 | Repeat the request | A restatement |
| 2 | Explain why each part exists | The 5 Whys |
| 3 | Predict what David will reject before he sees it, and say why | A list of the rejections you avoided |

Below tier 3 on a feature, do not build it as asked. Recommend the alternate scope or approach you can reach tier 3 on, and say what is missing.

## 4. Quality datum

The professional is the datum, not the customer. The customer's stated requirement is the loosest acceptable limit. Your own limit sits inside it. If David would accept it but a senior visionOS designer would not ship it, it is not done.

## 5. Proof

Every "done" is shown, not described:

| Feature | Reference | Before | After |
| --- | --- | --- | --- |
| image link | image | image | image |

Validate visually on your own before reporting: screenshot, compare against the reference, fix, repeat. Report only what survived that loop.

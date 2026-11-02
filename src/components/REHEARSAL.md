# Rehearsal: TrainerHub preview

Date: 2026-11-02. Updated for the user's 16px minimum.

The preview retains the browser geometry from stageshow `kit/window` and the
cropped framing of `examples/static-card`, rendered with native Astro and CSS.
It adds no React runtime or dependencies.

The current version removes the duplicate sidebar, vague category subtitles,
and fixed heights. Chinese labels and captions are at least 16px, category
names are 18px, and the content determines the height. The right edge crops
browser filler while the practice labels and workflow remain whole.

The figure is a labeled illustration. Its categories are not fake buttons;
the page's real links open TrainerHub and its repository. It has no cursor,
playback controls, timeline, or animation loop.

Current readability, interaction, copy, code, and antislop verification results
are recorded in [the UI review](../../docs/UI_REVIEW.md).

The original gold was compared through a static DOM rendering of its JSX and
original CSS at 400px and 358px. The original React runtime was not executed.
Current screenshots were inspected at desktop and phone widths in both themes.
External fonts were unavailable in the sandbox; system font fallback was used.
Physical devices and TrainerHub's external application were not tested.

Temporary captures and harnesses were removed after inspection.

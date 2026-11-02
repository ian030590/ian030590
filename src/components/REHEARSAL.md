# Rehearsal: TrainerHub preview and homepage

Date: 2026-11-02

## Composition

Design read: a clinical occupational therapy portfolio for readers, researchers,
and tool users. Existing blue, white, and slate tokens; ENERGY 1 / RHYTHM 2 /
MOTION 1. The numbered section index repeats the site's research-oriented
structure. Typography and the real portrait introduce the person; the product
preview explains the existing tool.

Gold: stageshow `examples/static-card`. Its supplied JSX was rendered as static
DOM with the original example and kit CSS for comparison at 400px and 358px.
The preview retains native browser geometry, a 24px gutter, a full-size content
pane, and a deliberate right/bottom crop. The satellite was omitted because
the four practice categories are the subject. The gold's React runtime was not
installed or executed.

The browser markup is an Astro adaptation of stageshow `kit/window`, without
adding a React runtime. The preview is a labeled illustration. Its tiles and
navigation are not interactive controls. Platform links outside the figure
open the real TrainerHub site and source repository.

## Checks

- PASS: `npm test`, including 24 Python tests and the five Node test entry points.
- PASS: `npm run check`, with zero errors, warnings, or hints.
- PASS: `npm run build`, including 41 immutable articles, 1,975 internal HTML
  links, 41 catalog links, and 48 sitemap URLs.
- PASS: `npm run audit:seo`, with zero errors. The existing thin-content warning
  applies to the blog loading shell, article loading shell, and 404 page.
- PASS: Chromium 151 browser checks at 320, 360, 390, 640, 760, 768, 900, 1024,
  1280, and 1440px in light and dark themes. No horizontal page overflow; the
  preview's workflow stays inside its crop.
- PASS: all six publication disclosures open and close with Enter/Space;
  chapter anchors resolve; seven internal destinations load; the mobile menu
  opens and Escape closes it and returns focus; theme switching persists.
- PASS: computed visible text contrast meets AA in both themes; reduced motion
  leaves the complete illustration visible; no JavaScript page errors.
- PASS: stageshow `film.mjs --still --gate` at desktop and 390px, including dark
  and reduced-motion captures. The final production mobile capture also passed.
- PASS: stageshow `layout.mjs --width 390 --strict` on the production preview.
- PASS: fresh-eye screenshot review. The initial right-side whitespace finding
  was fixed by sizing the content pane to its visible container and rechecked.

## Design gate

- Hard gate PASS: real portrait and existing academic data; working links and
  controls; responsive layouts, visible keyboard focus, and measured contrast.
- Purpose gate PASS: the sole accent marks actions and selected content; browser
  depth distinguishes the product illustration; numbered labels aid navigation.
  No decorative grid, gradients, generated imagery, or animation loop.
- Liveliness PASS: explicit dials, a typographic hero, a distinct product figure,
  and varied editorial/list/timeline sections using the same clinical palette.
- Craftsmanship PASS: preserved publication details and article sources; native
  disclosures; no invented metrics, testimonials, efficacy claims, or new runtime
  dependencies.

## Limits

Google Fonts is blocked in the sandbox. Visual checks used the system fallback;
the filming harness returned an empty stylesheet for that external request.
The new theme icons use inline SVG and the new illustration uses no icon font.

This is a still, with no timeline, cursor, playback, or loop. A `--states` attempt
reported no geometry violations but inconclusive time coverage due to sampling
gaps. No animation timing is claimed. Physical devices, browsers other than
Chromium, and TrainerHub's external application behavior were not checked.

Screenshots, test harnesses, and temporary reports were removed after review,
as required by the repository's cleanup rules. Nothing was published or deployed.

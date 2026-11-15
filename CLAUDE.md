# belikhun.dev: Project Instructions

The personal site of Belikhun: one long page read by scrolling, in the colours of his avatar.
Stack: Bun, SvelteKit (Svelte 5, static adapter), SCSS, GSAP (ScrollTrigger, SplitText) and Lenis.
It is built to a static `build/` folder and hosted on Harbor.

## Where things live

- `src/lib/content/site.ts`: every word on the page. `media.json` beside it is generated.
- `src/lib/components/`: one component per scene, in page order: Loader, Nav, Hero, About, Timeline,
  Band, Work, Rows, OffHours, Contact. `work/` holds the visual of each selected-work card.
- `static/belikhun.asc`: Belikhun's public PGP key. `KeyRain.svelte` streams its characters down
  the ending's card, and the footer links to the file.
- `static/counters/`: the pp, unstable rate, rank, user card and dan counters copied unchanged from
  github.com/Belikhun/osu-counters (commit 1968383) and shown in off-hours through iframes. Only
  `common/socket.js` is ours: it replaces tosu's socket helper with a made-up play and passes the
  site's colours as the counters' settings. `data/` holds saved copies of the osu! profile and
  mania-tracker answers the user card and dan counter would fetch. Update by copying the files again, never by editing them.
- Off-hours also plays the two videos of youtube.com/@Belikhun (`REELS` in `site.ts`) muted, on a
  loop and without controls, from compressed copies in `static/video/` (720p, 30 fps, no sound: AV1
  first, H.264 as the fallback, a still frame as the poster). They mount only once the section is
  reached and only where motion is allowed. Re-encode from the original exports with ffmpeg:
  `-an -vf scale=-2:720,fps=30`, then `libsvtav1 -preset 5 -crf 38` and `libx264 -preset slow -crf 27`.
- `static/emoji/`: Noto Animated Emoji (Google, CC BY 4.0) as Lottie files, played by `Emoji.svelte`
  with lottie-web's light build. Belikhun asked for no credit line on the page; the credit the licence
  asks for is in `static/emoji/LICENSE.txt`, which ships with the site.
- `src/lib/motion/`: GSAP setup, the media queries the scenes share, smooth scrolling, and the
  `reveal` action that wipes an element in when it scrolls into view. CSS transitions use the
  `--ease-out`, `--ease-snap` and `--fast` tokens from `app.scss`, never one-off curves.
- `src/lib/avatar/rig.ts`: the avatar's Live2D-style rig, a WebGL mesh per layer bent by a few
  parameters. `Avatar.svelte` animates it; the flat picture stays where motion is reduced.
- `src/app.scss`: design tokens (day and night). `src/lib/styles/_shared.scss`: mixins, injected
  into every SCSS block by `vite.config.ts`.
- `docs/assets/`: source pictures. `scripts/assets.py` resizes them into `static/img/`.
- `docs/assets/avatar/`: the avatar's layered PSD, split by See-through
  (`D:\Tools\see-through`), and the original it came from. `scripts/avatar.py` paints the
  original back onto the layers and packs them into `static/img/avatar/atlas.webp`.
- `docs/01-research-brief.md` and `docs/02-storyboard.html`: the research and the storyboard the
  site was built from. Not committed: they hold private notes.

## Rules that apply to every change

These follow harbor and luna-console; read `~/harbor/docs/style.md` on maylocnuoc for the full form.

- **Tabs, LF.** CSS lengths in rem on the scale (quarter steps from 1rem, eighths below, 0.1rem
  hairlines); viewport units and percentages are fine. SCSS only, nested, `//` comments.
- **Braces on every block**, never a one-line `if`; blank lines between logical blocks; multi-line
  ternaries. `camelCase` locals and functions, `ALL_CAPS` exported constants, `PascalCase` exported
  types. Full types, JSDoc on every export, the copyright header on every source file.
- **Comments only where the code does not explain itself**: a hack, a hidden constraint, a reason.
- **Copy is lower case**, except product, client and country names; luna and harbor are written
  lower case too. No em or en dashes. First
  person. Never mention AllSafe. CTMS+ is always "unofficial". Vloom App Platform is its own
  project, never listed under Vloom. On Manulife the role is "core developer".
- **Every scene is complete without motion.** CSS holds the final state; GSAP animates `from` it
  inside `gsap.matchMedia()`. Pinned layouts exist only under the `stage` mixin and
  `DESKTOP_MOTION`, which must stay in step.
- **The avatar appears in the hero only.**
- **The cursors** that assemble the ending (`Contact.svelte`) do a job once and leave; they never
  idle or orbit. The idea is Joel Califa's Swarm, which is unlicensed: never copy its code or
  cursor art, and do not credit it on the page.
- **Work cards**: Harbor shows real captures of harbor.belikhun.dev (hide rows that belong to
  other people's sites before capturing). Themis Web Interface and CTMS+ are minimal redrawn
  mockups: a few pieces that resemble the real interface, in the site's colours, with no real
  people's names; never screenshots and never the whole page. Every card's visual keeps one thing
  moving with the scroll for as long as the card is on screen (the `shown` span passed to `animate`). Vloom, Clover and Vloom Arena use the marks and
  colours of the Vloom media kit (docs.vloom.vn/vi/media-kit), unaltered; never its fonts.
  Manulife is a plain card above "everything else", not a work card. The smart home card is a
  minimal mockup: a few pieces in the app's own style, never the whole interface and never photos.
- **Commits**: one line, a leading emoji, then a plain lower-case sentence saying what changed.
  No body, no co-author or tool attribution, and only when Belikhun asks for one.

## Commands

```
bun run dev        # dev server on :8500
bun run check      # svelte-check
bun run build      # static site → build/
bun run preview    # serve build/ on :8501
bun run assets     # regenerate static/img and media.json from docs/assets (needs Python + Pillow)
bun run avatar     # repack the avatar atlas from the PSD (runs in See-through's Python environment)
```

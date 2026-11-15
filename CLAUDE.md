# belikhun.dev: Project Instructions

The personal site of Belikhun: one long page read by scrolling, in the colours of his avatar.
Stack: Bun, SvelteKit (Svelte 5, static adapter), SCSS, GSAP (ScrollTrigger, SplitText) and Lenis.
It is built to a static `build/` folder and hosted on Harbor.

## Where things live

- `src/lib/content/site.ts`: every word on the page. `media.json` beside it is generated.
- `src/lib/components/`: one component per scene, in page order: Loader, Nav, Hero, About, Timeline,
  Band, Work, Rows, OffHours, Contact. `work/` holds the visual of each selected-work card.
- `src/lib/motion/`: GSAP setup, the media queries the scenes share, smooth scrolling.
- `src/app.scss`: design tokens (day and night). `src/lib/styles/_shared.scss`: mixins, injected
  into every SCSS block by `vite.config.ts`.
- `docs/assets/`: source pictures. `scripts/assets.py` resizes them into `static/img/`.
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
- **Copy is lower case**, except product, client and country names. No em or en dashes. First
  person. Never mention AllSafe. CTMS+ is always "unofficial". Vloom App Platform is its own
  project, never listed under Vloom. On Manulife the role is "core developer".
- **Every scene is complete without motion.** CSS holds the final state; GSAP animates `from` it
  inside `gsap.matchMedia()`. Pinned layouts exist only under the `stage` mixin and
  `DESKTOP_MOTION`, which must stay in step.
- **The avatar appears in the hero only.**
- **The cursor swarm** (Clover card, the ending) is inspired by Joel Califa's Swarm. That site and
  its Chrome extension port are unlicensed: never copy their code or cursor art.
- **Commits**: one line, a leading emoji, then a plain lower-case sentence saying what changed.

## Commands

```
bun run dev        # dev server on :8500
bun run check      # svelte-check
bun run build      # static site → build/
bun run preview    # serve build/ on :8501
bun run assets     # regenerate static/img and media.json from docs/assets (needs Python + Pillow)
```

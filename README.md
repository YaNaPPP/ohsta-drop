# OHSTA — Dress Code Violation Drop

Animated hero for the OHSTA.Studio streetwear drop (Fri 23 Oct 2026, 18:00). Designed in Figma, built as one self-contained page.

**What happens:** CCTV preloader → the guy runs in from behind the camera and tags OHSTA (desktop: CCTV captures) / the tag is sprayed along its strokes (mobile) → INCOMING is stencil-sprayed, the O lands as a blue "pshh" stain that becomes the Reserve button with a live countdown → the camera leans in and two tags point at the jacket and the ripped trousers. After the intro, hold the mouse (or finger) to spray in brand blue: slow = wet and wide, fast = thin, hold still = it pools and drips.

## The page
1. **Hero** — CCTV preloader → the run-in as 11 CCTV captures (hard cuts, camera clock) → INCOMING sprayed, the O lands as the Reserve button, tags lead to the pieces. Hold to spray.
2. **01 The rule** — "Suits were made to make you fit in." fills in on scroll; FIT IN is sprayed out, STAND OUT goes over it.
3. **Caution tapes** — speed follows the scroll.
4. **02 The pieces** — horizontal scroll through the 10 designs of Drop 010; each card sprays out the dress-code rule it breaks.
5. **03 How a suit breaks** — FOUND → RIPPED (the word tears) → REWORN (sprayed back on).
6. **04 The drop** — 300 pieces, one Friday, no restock: the mechanics, a live countdown (always the next Friday 18:00 Berlin) and the reserve form (front-end only, nothing is sent).
7. **Footer** — the wordmark runs.

## Case study
`/case-study` — the reader layer behind the Dribbble shot: three key decisions and the nine-chapter story (`src/case_study.py` builds it).

## Structure
- `index.html` — the built page (hero images and fonts embedded)
- `assets/landing.css`, `assets/landing.js` — everything below the hero
- `assets/img/` — piece photos and detail crops · `assets/vendor/` — GSAP, ScrollTrigger, Lenis
- `assets/film/` — the 11 CCTV captures (frames of the film; `src/film/ohsta-run.mp4` is the source clip)
- `src/` — `template.html` (hero), `landing.html` (page markup), `build.py` (assembles `index.html`, piece data lives here), `pieces.py` (photo crops), asset pipelines

## Rebuild
```
cd src && python3 pieces.py && python3 build.py
```
`build.py` expects the licensed font subsets in `fonts/` at the repo root (`mon-black.woff2`, `nm-book.woff2`, `nm-bold.woff2`); they are not committed.

Deployed on Vercel — every push to `main` goes live.

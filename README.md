# OHSTA — Dress Code Violation Drop

Animated hero for the OHSTA.Studio streetwear drop (Fri 23 Oct 2026, 18:00). Designed in Figma, built as one self-contained page.

**What happens:** CCTV preloader → the guy runs in from behind the camera and tags OHSTA (desktop film) / the tag is sprayed along its strokes (mobile) → INCOMING is stencil-sprayed, the O lands as a blue "pshh" stain that becomes the Reserve button with a live countdown → the camera leans in and a white spray line traces the jacket and the ripped trousers. After the intro, hold the mouse (or finger) to spray in brand blue: slow = wet and wide, fast = thin, hold still = it pools and drips.

## Structure
- `index.html` — the built site (images, fonts and data embedded)
- `ohsta-run.webm` / `ohsta-run.mp4` — the desktop film
- `src/` — source: `template.html` (all code) + `build.py` (embeds the assets into `index.html`), image layers, spray paths, outline extraction scripts

## Rebuild
```
cd src && python3 build.py && cp ohsta-hero.html ../index.html
```
`build.py` expects the licensed font subsets in `fonts/` at the repo root (`mon-black.woff2`, `nm-book.woff2`, `nm-bold.woff2`); they are not committed.

Deployed on Vercel — every push to `main` goes live.

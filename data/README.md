# Content Guide

The content is split by purpose so writing work and UI work do not collide.

Edit these files when updating text:

- `movements.js`: short descriptions for movements shown in the "表現から見る" tab
- `eras.js`: era summaries, world events, and photo-history context
- `photographers.js`: photographer cards, detail text, citations, and external links
- `future/era-1990s.js`, `future/era-2000s.js`, `future/era-2010s.js`: empty era frames for newer periods
- `future/photographers-1990s.js`, `future/photographers-2000s.js`, `future/photographers-2010s.js`: placeholders or newly added photographers for newer periods

Recommended workflow:

1. Ask `Claude Code` to draft or revise text inside the relevant file in `data/`
2. Ask `Codex` to adjust layout, filtering, navigation, or other UI behavior in `scripts/site.js` or `index.html`
3. Keep IDs like `era`, `id`, and movement names stable unless the UI is updated at the same time

Adding a new photographer:

1. Open the matching future file in `data/future/` for new periods, or `photographers.js` for existing periods
2. Copy an existing photographer object near the same era
3. Update `id`, names, years, movements, links, and `context`
4. Make sure `era` matches one of the IDs defined in `eras.js`

Adding a new empty era shell:

1. Open the matching `data/future/era-*.js` file
2. Copy one `createEraStub(...)` block
3. Set `id`, `period`, and `title`
4. Fill text and sources later when the writing is ready

Current split:

- `index.html`: page structure and styles
- `data/content-helpers.js`: helper functions for empty era and photographer stubs
- `data/movements.js`: movement metadata
- `data/eras.js`: era metadata
- `data/photographers.js`: photographer entries
- `data/future/`: decade-by-decade shells and placeholders for 1990s onward
- `scripts/site.js`: rendering, filtering, tabs, random photographer, and detail-panel behavior

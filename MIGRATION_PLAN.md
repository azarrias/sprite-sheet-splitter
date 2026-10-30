# Migration plan

Preserve behavior before improving internals. Keep the Lua application intact
throughout; each phase can be checked against baseline `410088a`.

1. **Inventory and behavior specification**
   - Read every source file, inspect binary/asset formats and the preview.
   - Record defaults, exact rectangle math, field-mutation quirks, animation
     timing, no-export scope, and unsupported/unsafe inputs.
   - Exit criterion: `MIGRATION_ANALYSIS.md` describes the observed workflow.
2. **Isolate a small Python core**
   - Add packaging with Python 3.12+ and explicit runtime/dev dependencies.
   - Implement geometry, live/frozen state, selection, Cancel, zoom, timer.
   - Exit criterion: tests compare with actual original Lua functions, not
     only a rewritten expected-value algorithm.
3. **Reproduce in-memory image processing**
   - Load PNG/TGA with Pillow; preserve native size and alpha over black.
   - Implement source clamp-to-edge, frozen quads/live placements, clipping,
     overlays, frozen preview canvas, and nearest-neighbor zoom.
   - Exit criterion: synthetic images and bundled asset tests exercise bounds,
     alpha, offsets, padding, overlap, and rendering state changes.
4. **Replace only the platform shell**
   - Add maintained Dear ImGui Bundle runner, three docks and original labels.
   - Open native chooser on startup; Cancel exits; retain field quirks.
   - Wire global zoom, all-region double clicks, interval restart, debug overlay.
   - Exit criterion: GUI smoke test and manual workflow; no added export UI.
5. **Cross-check and harden narrowly**
   - Run original Lua geometry, Animation, and slice-state code under Lupa.
   - Compare outputs on fixed, randomized, edge-case and bundled-sheet inputs.
   - Document any unavailable original GPU/native validation honestly.
   - Add Windows/Linux Python-version CI and reject only unsafe inputs.
6. **Hand off execution and acceptance instructions**
   - Update README for Windows-first installation and Linux prerequisites.
   - Record actual results, differences, and platform-specific manual checks.
   - Retain the old sources/assets and licensing as the regression reference.

Deferred deliberately: exporting sprites/GIFs, settings/project persistence,
automatic slicing, alternate layouts/themes, packaging as a standalone EXE,
sequence editing, and UX redesign. None is needed for baseline parity.
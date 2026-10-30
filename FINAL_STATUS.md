# Final migration status

**Overall migration completion: 95%.** The complete documented functional scope is implemented in Python; the remaining 5% is platform acceptance and fidelity verification that requires a real Windows/LÖVE desktop comparison. This is a validation limitation, not a known code blocker. The Linux native desktop workflow and automated compatibility suite pass.

## Features implemented

- Startup PNG/TGA chooser with original case-insensitive final-three-character suffix behavior, retry on unsupported suffix, clean Cancel, and recoverable decode errors. An optional image-path argument is available for repeatable launch and testing.
- Original 1280 × 720, three-dock workflow, edit controls, debug overlay, global zoom, scrolling, and native desktop runner.
- Default slicing values and row-major quad geometry; inclusive multi-hit selection, duplicate IDs, animation interval restart, one-step frame advance, strict `timer > interval`, zoom lower bound, and Cancel/reslice behavior.
- Compatibility quirk where rows/columns ignore edits after Slice while X/Y parameters remain live; frozen source regions and animation canvas dimensions with live placement/display geometry.
- Pillow image decode and in-memory rendering, black-backed canvases, alpha compositing, clamp-to-edge sampling, clipped slices, grid/number overlays, and nearest-neighbor scaling.
- Runtime and test dependencies declared; installable Python package, module entry point, GUI script entry point, README installation/run instructions, and CI test workflow.
- Original Lua implementation and assets retained unchanged as the behavioral reference. No export, project persistence, or settings workflow was added.

## Features validated

- **42 automated tests passed** with the real desktop GUI test enabled in this Linux/OpenGL environment; the default headless-safe run reports 41 passed and the GUI test skipped.
- Differential tests execute the unchanged LuaJIT source for 250 seeded geometry cases, animation timing, state/selection behavior, and original draw-call sampling against Python in-memory pixels.
- The real GUI smoke test exercised Slice, ordered double-click selection, preview texture creation, global wheel zoom, Cancel, and texture cleanup.
- Runtime dependency check (`pip check`), CLI help, source distribution build, and platform-independent wheel build all succeeded. Validation Python: 3.14.4.
- PNG/TGA decoding, path/suffix behavior, corruption handling, alpha, clamp-to-edge crops, frozen/live geometry, safety guards, dialogs, and nearest-neighbor display are covered by tests.

## Remaining gaps

- Complete the documented Windows x64 desktop acceptance checklist in [VALIDATION.md](VALIDATION.md), using both the original LÖVE application and Python app on the same machine. In particular, check native dialogs, DPI scaling, GPU/display behavior, and compatibility quirks.
- No real macOS run has been performed; macOS remains best-effort and unvalidated.
- The original Windows LÖVE process/GPU renderer was not executed in this Linux environment. Differential Lua execution and software rendering validate behavior but do not validate native driver output.

These are validation gaps rather than unimplemented application features. No specific technical blocker is known.

## Known differences from the original

- Dear ImGui Bundle replaces the legacy LÖVE/ImGui native shell. Docking metrics, input event coalescing, click-recognition thresholds, DPI behavior, font glyphs, and theme appearance may differ.
- Pillow/software rendering replaces LÖVE GPU canvas rendering. Exact line/font rasterization, decoder corner cases, sampler behavior, blend rounding, and color management are not claimed pixel-identical. Pillow's small default font substitutes for LÖVE's 8px canvas font.
- Invalid images, unsafe dimensions, and invalid intervals produce recoverable errors instead of preserving original crashes or invalid arithmetic. Empty selections render blank rather than triggering the old empty-animation draw error. Explicit safeguards limit grids and allocations.
- Python's desktop backend does not guarantee identical ordering for multiple repeated-click events coalesced in a single update. Normal selection ordering and inclusive multi-hit semantics are covered.
- Remote `mobdebug` integration was not migrated; standard Python debugging is used instead. The command-line image path is a convenience addition.

## Recommended next steps after migration

1. Run and record every Windows item in [VALIDATION.md](VALIDATION.md), including runtime version, GPU driver, DPI, and any observed differences.
2. If macOS support is a release requirement, perform a native macOS install, chooser, GUI, and scaling pass before advertising it as supported.
3. Keep the Lua differential suite as a regression oracle. Treat exports, persistence, workflow redesign, and other deferred features as separate product decisions, not parity work.

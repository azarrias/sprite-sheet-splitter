# Migration validation

## Executed locally

Validation date: 2026-10-30. Baseline: unchanged original Lua at `410088a`.
Host: Linux/WSLg x86-64, usable native desktop display and OpenGL backend.

| Check | Result |
| --- | --- |
| Python 3.12.16, full suite with real GUI enabled | 42 passed |
| Python 3.14.4, full suite with real GUI enabled | 42 passed |
| Normal suite without GUI opt-in | GUI test intentionally skipped; other tests run |
| Source distribution and pure-Python application wheel build | Successful |
| `pip check` | No broken requirements |
| Module `--help` entry point | Successful |
| Windows x64 / CPython 3.12 runtime dependency wheels | Downloaded successfully; **not executed on Windows** |
| Original source changes | None; baseline Lua/DLLs/assets retained |

Runtime packages used: Dear ImGui Bundle 1.93.0, Pillow 12.3.0, NumPy 2.5.4;
test packages: pytest 9.2.0 and Lupa 2.8 (explicit `lupa.luajit21`).
Lupa's default Lua runtime is not used: modern Lua 5.5 rejects a loop-variable
assignment in the original class helper, whereas LuaJIT matches LÖVE.

## Meaning of “equivalent outputs”

The original has **no saved output files**. Comparisons therefore use its
in-memory geometry, selected IDs, timer/frame state, and canvas draw requests.
Tests do not fabricate an exporter or compare nonexistent saved PNG files.

1. **Geometry:** 250 seeded randomized parameter sets execute the original
   `GenerateQuads`, using a LÖVE `newQuad` stub that records rectangle values.
   Python matches every rectangle and order, including negative offsets,
   negative padding, and zero/negative counts.
2. **Animation:** Original `Animation.lua` executes under LuaJIT on empty,
   single, repeated, and multi-frame sequences. Compare current-frame index
   and timer after strict-boundary, small, and long updates (210 updates for
   each of four cases). One-step advancement and restart semantics are retained.
3. **State/selection:** Execute the original start/slice state classes and
   Deque with inclusive edge clicks, repeated selection, missed clicks,
   live-vector mutation, interval rebuilding, and Cancel. Frame lists and
   active animation state agree. Python UI tests separately verify that
   sliced rows/columns ignore returned edits while X/Y fields still mutate.
4. **Image pixels:** Execute unchanged `SlicerGUI.DrawImageToCanvas`,
   `DrawQuadsToCanvas`, and `DrawAnimationToCanvas` with a software adapter for
   the LÖVE draw API. Compare Python canvas bytes with the original code's
   emitted draw operations on both synthetic semitransparent pixels and the
   bundled 272 × 256 sheet. Cases include defaults, offsets/padding,
   off-sheet rectangles, and overlapping regions. The adapter independently
   samples pixels using NumPy index clamping; it does not call the Python
   implementation's rectangle generator or crop helper.
5. **Decode/display:** PNG/TGA round trips, uppercase endings, spaces/Unicode
   paths, corrupt/unsupported input, opaque black composition, frozen preview
   canvas dimensions, nearest-neighbor scaling, allocation guards.
6. **Native chooser flow:** Mock only native answers, checking startup Cancel,
   unsupported filename retry, decode-error notification, and valid load.
7. **Real GUI:** Launch actual Hello ImGui window/renderer on the desktop;
   synthesize mouse events on the actual Slice widget, double-click two sheet
   frames, confirm preview texture creation, wheel to 3×, click Cancel, check
   retained zoom and cleared preview, and release textures before shutdown.
   This is not a mocked renderer. Test waits for initial hidden docking layout.

## Differences and validation boundaries

- **No original Windows LÖVE process was run in this environment.** Its bundled
  Windows DLLs cannot load in Linux Python and matching Linux bindings are
  absent. Lua comparisons run real original source, not the original engine.
- The software adapter omits font/line rasterization, relies on Pillow for
  alpha blending, and assumes LÖVE's default clamp-to-edge sampling. It cannot
  establish bit-identical GPU pixels, blend rounding, color management, or
  native decoder parity. Those remain manual/engine-specific checks.
- Pillow substitutes its small font for LÖVE's default 8px canvas font.
  Grid lines use Pillow rasterization. Modern ImGui docking/theme/DPI metrics
  and click-recognition thresholds are supplied by the new native backend.
  Backend event coalescing differs from LÖVE's explicit newest-first queue when
  multiple repeated clicks arrive in a single update. Normal user sequences
  and inclusive multi-region hits are covered; exact burst-event ordering is
  not claimed. Dock layout is recreated from the original preview, not the
  broken legacy docking API. Layout persistence is disabled.
- Nonpositive/non-finite intervals, nonpositive Slice dimensions, and very
  large grids/buffers are rejected deliberately. The old zero-interval modulo
  and empty-animation draw errors are not recreated. Errors are recoverable.
  Invalid live preview dimensions render no preview until corrected.
- Exact Windows native dialog handling and graphics/DPI behavior are **not
  validated locally**. CI configuration is supplied, not a claim that remote
  jobs have already passed. macOS remains unvalidated best-effort support.

## Reproduce

Install `.[test]` into a venv as described in README. Run `python -m pytest -q`.
Set `SPRITE_SPLITTER_GUI_TEST=1` to also open the real GUI test window (Linux
example: `SPRITE_SPLITTER_GUI_TEST=1 .venv/bin/python -m pytest -q`). A virtual
X display with Mesa may be used on headless Linux. The CI workflow shows that
configuration. Lua tests skip explicitly if the optional LuaJIT runtime is
missing; install the full test extra to avoid an incomplete comparison.

## Remaining Windows-first acceptance checklist

Run the baseline separately with a compatible Windows x64 LÖVE runtime and
the Python version on the same desktop. Use the bundled sheet and a
semitransparent PNG/TGA with known colored cells.

- [ ] Native chooser: PNG/TGA, uppercase extension, Unicode/space path, Cancel,
      unsupported ending, corrupt input; close/restart to change sheets.
- [ ] Initial 1280 × 720 title/layout/defaults, scrollbars, draggable docks,
      debug overlay; repeat at 100%, 150%, and 200% Windows display scaling.
- [ ] Compare the default grid and nonzero offset/padding; Slice gives the
      same numbered cell contents; unselected sheet areas become black.
- [ ] Double-click [1, 2, 2, 5], compare ordered IDs and preview. Edit interval,
      confirm first-frame restart. Test shared-edge/overlapping hits.
- [ ] Wheel over all three docks/fields: shared zoom minimum 1 and scrolling.
- [ ] Confirm scalar-vs-X/Y sliced edit quirk, frozen sources/live positions,
      Cancel clears selection but preserves parameters/zoom, reslice resets
      interval. Slice in sliced mode and Cancel in edit mode are no-ops.
- [ ] Compare negative offsets/padding and out-of-image clamp behavior against
      actual LÖVE. Record any GPU sampler or blend-rounding differences.
- [ ] Verify intentional safety/error handling, then close cleanly with both
      blank and playing preview; check no saved sprites/settings appear.

Record Windows runtime, graphics driver, DPI, baseline LÖVE version and any
differences before claiming native Windows acceptance or screenshot parity.
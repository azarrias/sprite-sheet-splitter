# Migration assessment

## Source of truth and scope

Inspected all tracked files at baseline `410088a` (tag `v1.0`), including all
Lua source, bundled libraries, binary types, sample image, README, and preview
animation. The application is a **slicing/animation preview utility**, not an
image exporter. No sprite files, GIFs, metadata, project files, output directory,
or output naming conventions exist. Do not infer export from the project name.
The original sources and Windows binaries remain unchanged for reference.

## Current architecture and dependencies

| Component | Purpose |
| --- | --- |
| `src/main.lua` | LÖVE callbacks, defaults, input forwarding, global zoom |
| `src/globals.lua` | Imports, title, fixed 1280 × 720 window, platform checks |
| `src/SlicerGUI.lua` | Native open dialog, ImGui docks, image/canvas rendering, fields |
| `src/AppStateStart.lua` | Live parameter editing and Slice transition |
| `src/AppStateSlice.lua` | Quad generation, double-click selection, animation, Cancel |
| `src/Animation.lua` | Frame timer and draw of current quad |
| `src/StateMachine.lua`, `BaseState.lua` | Two-state dispatch |
| `src/Deque.lua`, `Vector2D.lua` | Selection/event queues and mutable coordinates |
| `src/util.lua` | Row-major quad generation; unused auto-grid/tile-set/text/debug helpers |
| `src/libs/class.lua` | MIT-licensed class helper (Matthias Richter) |
| `src/libs/push.lua` | MIT-licensed resolution helper (Ulysse Ramage), imported but unused |
| LÖVE / LuaJIT | Window, GPU textures, canvases, image decode, event loop |
| `src/imgui.dll` | Bundled x86-64 Windows love-imgui native binding and old docking API |
| `src/nfd.dll` | Bundled x86-64 Windows nativefiledialog binding |
| `mobdebug` | Optional external debugger, only with final argument `-debug` |
| `src/graphics/character.png` | 272 × 256 RGBA sample, not automatically opened |
| `preview.gif` | 480 × 270 workflow illustration, not an application input |

The baseline loads `.dll` on Windows, `.so` on Linux, and rejects other OSes;
only Windows binaries are supplied. Native binding versions and build recipes
are absent. There is no dependency manifest or automated test suite. LICENSE
is GPL-3.0; retain it and the original embedded third-party notices.

## Complete observable workflow

1. Startup opens a native single-file chooser filtered to PNG/TGA. Cancel exits.
   A filename whose final three characters are not `png` or `tga`
   (case-insensitive) reopens the chooser. There is no Open/New action later.
   The suffix check does not require a dot. Loading uses bytes rather than a
   path limited to the engine's virtual filesystem. Corrupt input is unhandled.
2. Window title: **Sprite Sheet Splitter**. Initial/fixed size: 1280 × 720.
   Docks: **Edit**, **Sprite sheet**, **Preview animation**. The old port's dock
   placement API is explicitly described as broken; the GIF is a visual guide,
   not a reliable exact layout specification. Docks permit scrolling/rearranging.
3. Default fields: rows 4, columns 4, pixels per sprite X=16 Y=32, offset X=0
   Y=0, padding X=0 Y=0. Integer fields; rows/columns have +/- buttons.
   Grid updates immediately while editing. Cancel in edit mode does nothing.
4. Slice freezes a row-major list of quads, dims slicing text to 0.7 grey, and
   shows 1-based frame numbers. Slice again does nothing. Animation properties
   appear with Interval=0.5 seconds and `Frame IDs:` initially empty.
5. Double-clicking a region appends its ID; duplicates are allowed. There is
   no removal, reordering, play/pause, export, or sequence limit UI. Selecting
   another frame rebuilds the animation at its first frame with timer zero.
   Changing Interval also rebuilds/restarts it, even with no selected frames.
6. Cancel while sliced clears the selection/preview and returns to editing;
   all slicing parameters, zoom, and the original image persist. A new Slice
   resets the interval to 0.5. Empty selections show no preview.
7. Wheel motion **anywhere**, even over fields/other docks, adds its vertical
   delta to the shared sheet/preview scale, with minimum 1 and no upper bound.
   Native ImGui scrolling also receives that event. Nearest-neighbor display.
   No special keyboard shortcuts; ordinary ImGui text editing is forwarded.
8. A fixed bottom-right debug overlay is enabled by default, showing mouse
   coordinates clamped to [-1,1280] and [-1,720]. LÖVE uses an 8px default font
   for canvas frame numbers; ImGui uses its own default font for controls.

### Important original imperfections

The slicing controls are **not actually disabled** after Slice. Rows/columns
are drawn but their returned new values are ignored. However, the X/Y helper
mutates shared Vector2D objects, so size, offset, and padding **remain editable**.
Quads and the animation canvas dimensions stay frozen, whereas destination
positions, hit boxes, grid, and preview display size use the live values. The
Python version intentionally retains this inconsistency.

Double-clicks are collected before update without checking ImGui mouse capture
or clipping. All rectangles are tested with inclusive left/right/top/bottom;
one boundary click can append several adjacent/overlapping IDs in row-major
order. Negative padding can overlap regions. Multiple click events received
within a single update are processed newest-first (Deque push_front). Triple
and later repeated left clicks also count (`presses > 1`).

## Image processing and animation rules

For zero-based row `r` and column `c`:

- `x = offset_x + c * (width + padding_x)`
- `y = offset_y + r * (height + padding_y)`
- source rectangle `(x, y, width, height)`
- displayed ID `r * columns + c + 1`

Rows are outermost; no inference from image size, trimming, transparent-pixel
filtering, automatic tile sets, color-key conversion, or spacing at outer edges.
Zero/negative row or column counts generate no frames. There is no bounds
validation: off-image texture sampling uses the LÖVE default clamp-to-edge
wrap mode, not Pillow's transparent-black crop padding. Negative offsets and
padding are meaningful and retained. Slice with nonpositive sprite dimensions
cannot create the original animation canvas reliably.

The sheet canvas is exactly the original image size and opaque black. Edit
mode draws the whole image. Slice mode clears to black and draws only frozen
source quads at live grid positions (other sheet pixels disappear). Content
outside the sheet canvas is clipped. Alpha is composited over black; source
pixels are not modified. No saved outputs exist. Grid rectangles begin at
`(x+1,y+1)` with size `(width-1,height-1)`, rough lines, RGBA
`(0.9,0.9,0.9,0.3)`. Slice numbers start at `(x+2,y)`, colored
`(1,0.7,0.7,0.7)` and wrap at the original 1280px print width. The animation
canvas is the sprite size captured at Slice; it draws the selected frozen
quad at (0,0), over black. Both canvases share display zoom.

Animation accumulates `dt` only with more than one selected frame. It advances
**one** frame only when `timer > interval` (not `>=`), retains
`timer % interval`, and wraps to the first frame. Long updates do not skip
multiple frames. A single selected frame stays still. Zero/non-finite interval
can cause invalid modulo behavior in the original; negative intervals are not
validated by Lua.

## Python architecture

- Python 3.12+, small installable package under `python/sprite_sheet_splitter`;
  leave `src` as the original reference, not a second Python source tree.
- `model.py`: dataclasses, row-major geometry, two-state workflow, hit tests,
  exact timer logic. No GUI imports, directly testable.
- `imaging.py`: Pillow PNG/TGA decoding, clamped source extraction, opaque-black
  sheet/animation composition, grid and numbers, nearest-neighbor scaling.
- `app.py`: Dear ImGui Bundle / Hello ImGui native desktop runner, the same
  three docks, native portable-file-dialogs bindings, GPU texture ownership.
  NumPy bridges Pillow RGBA buffers to the binding's GPU-upload API.
- `__main__.py`: console entry point; optional image argument for repeatable
  validation without a chooser. No new export workflow.
- pytest unit/integration tests; optional Lupa runs **unchanged Lua code** as
  an independent geometry/timing/state oracle, with minimal LÖVE stubs.

Dear ImGui Bundle is selected over the older pyimgui stack for current Dear
ImGui, maintained wheels, native cross-platform dialogs, docking, and its own
window/render loop. No custom GLFW/OpenGL binding layer is necessary. Python
never loads the old DLLs. Portable File Dialogs uses native Windows/macOS
dialogs and Zenity/KDialog on Linux. An OpenGL-capable desktop is required.

## Risks, assumptions, and intentional changes

- GPU rasterization, font glyphs, theme metrics, modern docking, DPI handling,
  color management, and PNG/TGA decoder corner cases may differ. Pixel-perfect
  LÖVE canvas screenshots are **not** claimed; preserve practical regions,
  ordering, preview, and controls. Pillow's small default font substitutes for
  the old LÖVE canvas font. Dock persistence is disabled for repeatable startup.
- Native ImGui supplies repeated-click thresholds and event coalescing instead
  of LÖVE's explicit newest-first double-click event deque. Inclusive multi-hit
  behavior is retained; ordering of multiple burst events within one update is
  not guaranteed identical. Normal ordered frame-selection workflows are tested.
- Invalid image decode is reported instead of an unhandled Lua error. Dialog
  retry is iterative instead of recursive. Startup Cancel exits cleanly.
- Nonpositive dimensions at Slice, interval <=0/non-finite, and excessive
  allocations are rejected with an in-window error rather than risking a
  crash/hang. Negative offsets/padding and nonpositive grid counts remain
  supported. Safety limits: 100,000 regions and 64 million pixels per canvas
  or zoomed display buffer. These limits are implementation safeguards, not
  original features. Negative intervals are an explicit incompatibility.
- Empty animation objects from an Interval change render blank, avoiding the
  original nil-quad draw error. Slice parameters otherwise retain their bugs.
- PNG/TGA are the only accepted filename endings. Animated PNG, if decoded,
  uses its first image; no animated-input feature is added. No EXIF transpose,
  resize, or profile conversion is applied.
- Optional command-line image selection is a testing/convenience addition.
  Remote mobdebug is not migrated: standard Python debuggers replace it.
- Windows is the primary target; automated Windows tests are provided, but
  native-dialog/GPU interaction still needs a real Windows desktop acceptance
  pass. macOS is best-effort, not a claimed validated platform.

## Validation status

See `VALIDATION.md` for executed checks, exact scope of Lua comparisons,
limitations, and the remaining Windows/manual acceptance checklist. There are
no baseline exported files to compare: meaningful comparisons are geometry,
selected frame order, animation timing, and in-memory image regions.
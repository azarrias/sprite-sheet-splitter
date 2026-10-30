# Sprite Sheet Splitter

Preview slicing settings for irregular sprite sheets and build animation
sequences by double-clicking frames. This is a Python migration of the original
LÖVE/ImGui utility, **not a redesign**.

**Like the original, this application previews slices; it does not export
sprite images, animations, or metadata, and does not save projects/settings.**

![Original workflow](preview.gif)

## Requirements

- **64-bit Python 3.12 or newer** (tested locally with 3.12 and 3.14).
- Windows 10/11 is the primary target. Linux desktop support is also tested.
	macOS is best-effort, using the same dependencies, not yet validated.
- A working desktop display and OpenGL-capable graphics driver (normally
	OpenGL 3.3+; macOS uses the platform-supported core profile). Headless SSH
	sessions need a display server. No LÖVE installation or old DLLs are needed.
- Runtime packages installed automatically: Dear ImGui Bundle (including
	Hello ImGui and Portable File Dialogs), Pillow, and NumPy.

## Windows: install and run

Open PowerShell in the cloned repository. Install x64 Python 3.12+ from
[python.org](https://www.python.org/downloads/windows/) if needed, then:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m sprite_sheet_splitter
```

Use the corresponding launcher version if a newer Python is installed. No
environment activation or PowerShell execution-policy changes are necessary.
Subsequent runs only need the last command. The installed
`sprite-sheet-splitter` GUI entry point is also available in the environment.

## Linux: install and run

Use a desktop session with Python 3.12+. On Debian/Ubuntu, install the matching
venv package, OpenGL/GLFW system libraries, and **Zenity or KDialog** for the
native file chooser. For example (system installation may require an admin):

```sh
sudo apt-get install python3-venv libgl1 libegl1 libx11-6 libxcursor1 libxi6 libxinerama1 libxrandr2 libxkbcommon0 zenity
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
.venv/bin/python -m sprite_sheet_splitter
```

Check `python3 --version` first. Some distributions require a version-specific
package such as `python3.12-venv`. Zenity/KDialog is only required for the
startup chooser; an explicit image path can bypass it. WSL needs WSLg or
another working display server.

On macOS, use Python 3.12+ and the same venv/pip/module commands as Linux;
do not install Linux system packages. The native chooser uses macOS dialogs.

## How to use

1. Select a **PNG or TGA** in the startup native chooser. Cancel exits. To open
	 another sheet later, close and restart the app.
2. In **Edit**, adjust **Number of rows**, **Number of columns**, **Pixels per
	 sprite** (X/Y), **Offset** (X/Y), and **Padding** (X/Y). The grid updates live.
	 Defaults are 4 rows, 4 columns, 16 × 32 pixels, no offset or padding.
3. Click **Slice**. Only selected regions remain visible on black, numbered
	 from 1, left-to-right then top-to-bottom. Slice again does nothing.
4. **Double-click** frames in the desired order. Repeated frames are allowed.
	 IDs appear under **Animation properties** and the sequence plays in
	 **Preview animation**. The **Interval** is seconds per frame, initially 0.5.
	 Adding a frame or changing the interval restarts the sequence.
5. **Cancel** clears the sequence and returns to editing, retaining the sheet,
	 parameters, and zoom. Cancel during editing does nothing.
6. Use the **mouse wheel anywhere** to zoom the sheet and preview together;
	 minimum zoom is 1×. The same wheel event also reaches ImGui scrolling.
	 Docks are scrollable/rearrangeable. A mouse-position debug overlay is kept.

For compatibility, after Slice the grey row/column controls ignore edits, but
the X/Y fields still mutate live layout/hit boxes while source rectangles stay
frozen. Use Cancel before changing slicing parameters for predictable results.
Boundary/overlapping clicks can select more than one frame, as in the original.

An optional image argument skips the chooser (paths with spaces must be quoted):

```sh
python -m sprite_sheet_splitter "src/graphics/character.png"
```

Use your environment's Python path as shown above if it is not activated.

## Tests and validation

Install the optional test dependencies, then run from the repository root:

```sh
python -m pip install -e ".[test]"
python -m pytest -q
```

The tests execute the unchanged original Lua functions with Lupa's LuaJIT
runtime. They compare geometry, frame order, animation timing, and in-memory
canvas pixels through an explicit software adapter. A real desktop/GPU workflow
test is opt-in (it briefly opens a window and injects clicks):

```powershell
$env:SPRITE_SPLITTER_GUI_TEST = "1"
.\.venv\Scripts\python.exe -m pytest -q
```

```sh
SPRITE_SPLITTER_GUI_TEST=1 .venv/bin/python -m pytest -q
```

The Python CI workflow covers Windows/Linux 3.12–3.14 and Linux GUI rendering.
See [VALIDATION.md](VALIDATION.md) for what was actually executed and the
remaining real-Windows acceptance checks; Windows wheel availability alone
is not a Windows runtime validation.

## Compatibility, safety, and troubleshooting

- Invalid images produce an error and reopen the chooser. PNG/TGA names are
	checked case-insensitively; the original final-three-character check is kept.
- Nonpositive sprite dimensions at Slice, nonpositive/non-finite intervals,
	more than 100,000 regions, or canvas/display buffers above 64 million pixels
	are rejected instead of crashing or hanging. Negative offsets/padding and
	zero/negative row/column counts are retained. Extremely wide/tall textures
	can also exceed your graphics driver's texture-size limit.
- An empty frame sequence shows no preview, including after an interval edit.
- Small font, grid rasterization, modern docking, and DPI/theme metrics differ
	from the old native port. There is no claim of pixel-identical GUI screenshots.
- If a graphical launcher closes without showing an error, launch via
	`python -m sprite_sheet_splitter` in a terminal to see diagnostics.
- On Linux, missing-dialog errors mean Zenity/KDialog needs installing; display
	errors mean the native window backend cannot access your desktop/driver.
- No settings/output files are written; installation/build/test tools may
	create their usual ignored environment, cache, and distribution directories.

## Repository layout and migration documents

- [python/sprite_sheet_splitter](python/sprite_sheet_splitter): new implementation;
	independent model, Pillow imaging, and thin ImGui desktop shell.
- [tests](tests): regression, original-Lua comparison, dialog, and GUI tests.
- [src](src): unchanged original Lua application and bundled Windows bindings.
- [MIGRATION_ANALYSIS.md](MIGRATION_ANALYSIS.md): full behavior inventory,
	architecture/dependencies, image rules, risks, and intentional differences.
- [MIGRATION_PLAN.md](MIGRATION_PLAN.md): small, behavior-first migration phases.
- [VALIDATION.md](VALIDATION.md): comparison results and platform acceptance list.

The old version can still be run separately using a compatible Windows x64
LÖVE runtime with `src` as its working/application directory; its DLL versions
and exact engine compatibility were never specified upstream. Do not copy the
old native modules into Python's environment.

## License

[GPL-3.0](LICENSE), unchanged from the repository. Original vendored Lua helpers
retain their embedded third-party license notices. Installed Python/native
dependencies are distributed under their respective upstream licenses.
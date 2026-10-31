# Sprite Sheet Splitter

Preview slicing settings for irregular sprite sheets and build animation
sequences by double-clicking frames. A Python desktop application built with
Dear ImGui Bundle, Pillow, and NumPy.

**This application previews slices; it does not export
sprite images, animations, or metadata, and does not save projects/settings.**

## Requirements

- **64-bit Python 3.12 or newer** (tested locally with 3.12 and 3.14).
- Windows 10/11 is the primary target. Linux desktop support is also tested.
	macOS is best-effort, using the same dependencies, not yet validated.
- A working desktop display and OpenGL-capable graphics driver (normally
	OpenGL 3.3+; macOS uses the platform-supported core profile). Headless SSH
	sessions need a display server.
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
6. Use the **− / + buttons** next to **Zoom** in **Edit** to zoom the sheet and
	 preview together in steps of 1×; minimum zoom is 1×. The current scale is
	 shown between the buttons. The **mouse wheel only scrolls** ImGui panels,
	 without changing zoom.
	 Docks are scrollable/rearrangeable. A mouse-position debug overlay is kept.

After Slice the grey row/column controls ignore edits, but
the X/Y fields still mutate live layout/hit boxes while source rectangles stay
frozen. Use Cancel before changing slicing parameters for predictable results.
Boundary/overlapping clicks can select more than one frame.

An optional image argument skips the chooser (paths with spaces must be quoted):

```sh
python -m sprite_sheet_splitter "/path/to/your/sprite sheet.png"
```

Use your environment's Python path as shown above if it is not activated.

## Development and tests

Install the optional test dependencies, then run from the repository root:

```sh
python -m pip install -e ".[test]"
python -m pytest -q
```

The Python regression tests cover geometry, frame order, animation timing,
image loading, dialog handling, and in-memory canvas pixels against an
independent sampler. Test images are generated at runtime; no bundled assets
or external language runtimes are required. A real desktop/GPU workflow test
is opt-in (it briefly opens a window and injects clicks):

```powershell
$env:SPRITE_SPLITTER_GUI_TEST = "1"
.\.venv\Scripts\python.exe -m pytest -q
```

```sh
SPRITE_SPLITTER_GUI_TEST=1 .venv/bin/python -m pytest -q
```

The Python CI workflow covers Windows/Linux 3.12–3.14 and Linux GUI rendering.
Local validation includes the full regression suite and the real GUI workflow
on Linux. Interactive Windows acceptance and macOS runtime validation remain
platform-specific checks; CI unit tests do not replace them.

To build a source distribution and wheel:

```sh
python -m pip install build
python -m build
```

## Compatibility, safety, and troubleshooting

- Invalid images produce an error and reopen the chooser. PNG/TGA names are
	checked case-insensitively using the final three characters of the filename.
- Nonpositive sprite dimensions at Slice, nonpositive/non-finite intervals,
	more than 100,000 regions, or canvas/display buffers above 64 million pixels
	are rejected instead of crashing or hanging. Negative offsets/padding and
	zero/negative row/column counts are retained. Extremely wide/tall textures
	can also exceed your graphics driver's texture-size limit.
- An empty frame sequence shows no preview, including after an interval edit.
- Fonts, grid rasterization, docking, and DPI/theme metrics can vary across
	platforms and graphics drivers.
- If a graphical launcher closes without showing an error, launch via
	`python -m sprite_sheet_splitter` in a terminal to see diagnostics.
- On Linux, missing-dialog errors mean Zenity/KDialog needs installing; display
	errors mean the native window backend cannot access your desktop/driver.
- No settings/output files are written; installation/build/test tools may
	create their usual ignored environment, cache, and distribution directories.

## Repository layout

- [src/sprite_sheet_splitter](src/sprite_sheet_splitter): application package;
	independent model, Pillow imaging, and thin ImGui desktop shell.
- [tests](tests): self-contained model, imaging, dialog, and GUI regression tests.
- [pyproject.toml](pyproject.toml): dependencies, packaging, entry point, and test
	configuration.
- [.github/workflows/python-tests.yml](.github/workflows/python-tests.yml):
	Windows/Linux test matrix and Linux GUI workflow.

## License

[GPL-3.0](LICENSE). Installed Python/native dependencies are distributed under
their respective upstream licenses.
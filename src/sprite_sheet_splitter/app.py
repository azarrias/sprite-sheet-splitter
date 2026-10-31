"""Thin Dear ImGui desktop shell for the sprite sheet preview tool."""

from dataclasses import astuple
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image
from imgui_bundle import hello_imgui, imgui, portable_file_dialogs as pfd

from .imaging import display_image, load_image, render_animation, render_sheet, supported_filename
from .model import Session


def choose_image() -> Image.Image | None:
    if sys.platform.startswith("linux") and not any(shutil.which(x) for x in ("zenity", "kdialog")):
        raise RuntimeError("Native dialogs require Zenity or KDialog on Linux. Install one, or pass an image path.")
    while True:
        paths = pfd.open_file("Open image", "", ["Image files", "*.png *.tga *.PNG *.TGA"]).result()
        if not paths:
            return None
        if not supported_filename(paths[0]):
            continue
        try:
            return load_image(paths[0])
        except (OSError, ValueError) as error:
            pfd.message("Sprite Sheet Splitter", str(error), pfd.choice.ok, pfd.icon.error).result()


class Application:
    def __init__(self, image: Image.Image):
        self.image = image
        self.session = Session()
        self.error = ""
        self.sheet_origin: tuple[float, float] | None = None
        self.sheet_texture = None
        self.preview_texture = None
        self.sheet_key = None
        self.preview_key = None

    def attempt(self, action) -> None:
        try:
            action()
            self.error = ""
        except ValueError as error:
            self.error = str(error)

    def new_frame(self) -> None:
        io = imgui.get_io()
        # Leave the mouse wheel exclusively to ImGui's native scrolling.
        # No WantCaptureMouse/hover/clip check; test every region.
        if self.sheet_origin is not None and imgui.get_mouse_clicked_count(0) > 1:
            x = (io.mouse_pos.x - self.sheet_origin[0]) / self.session.scale
            y = (io.mouse_pos.y - self.sheet_origin[1]) / self.session.scale
            self.attempt(lambda: self.session.double_click(x, y))
        self.session.update(io.delta_time)

    def scalar(self, label: str, name: str) -> None:
        p = self.session.parameters
        imgui.align_text_to_frame_padding()
        imgui.text(label)
        imgui.same_line(150)
        imgui.set_next_item_width(142)
        changed, value = imgui.input_int(f"##{name}", getattr(p, name), 1)
        if changed and not self.session.sliced:
            setattr(p, name, value)

    def xy(self, label: str, x_name: str, y_name: str) -> None:
        p = self.session.parameters
        imgui.align_text_to_frame_padding()
        imgui.text(label)
        imgui.same_line(150)
        imgui.text("X")
        imgui.same_line(163)
        imgui.set_next_item_width(50)
        changed, value = imgui.input_int(f"##{x_name}", getattr(p, x_name), 0)
        if changed:
            setattr(p, x_name, value)
        imgui.same_line(230)
        imgui.text("Y")
        imgui.same_line(243)
        imgui.set_next_item_width(50)
        changed, value = imgui.input_int(f"##{y_name}", getattr(p, y_name), 0)
        if changed:
            setattr(p, y_name, value)

    @staticmethod
    def centered(text: str) -> None:
        imgui.set_cursor_pos_x(max(8, (293 - imgui.calc_text_size(text).x) / 2))
        imgui.text(text)

    def draw_edit(self) -> None:
        imgui.text("Zoom")
        imgui.same_line()
        if imgui.button("-##zoom_out", (30, 20)):
            self.session.zoom(-1)
        imgui.same_line()
        imgui.text(f"{self.session.scale:g}x")
        imgui.same_line()
        if imgui.button("+##zoom_in", (30, 20)):
            self.session.zoom(1)
        imgui.spacing()
        color = 0.7 if self.session.sliced else 1.0
        imgui.push_style_color(imgui.Col_.text, (color, color, color, 1))
        self.centered("Slicing parameters")
        self.scalar("Number of rows", "rows")
        self.scalar("Number of columns", "columns")
        # X/Y edits remain live in sliced mode; source rectangles stay frozen.
        self.xy("Pixels per sprite", "width", "height")
        self.xy("Offset", "offset_x", "offset_y")
        self.xy("Padding", "padding_x", "padding_y")
        imgui.dummy((0, 10))
        imgui.set_cursor_pos_x(293 / 2 - 60)
        if imgui.button("Slice", (50, 20)):
            self.attempt(self.session.slice)
        imgui.pop_style_color()
        imgui.same_line(293 / 2 + 10)
        if imgui.button("Cancel", (50, 20)):
            self.session.cancel()
            self.error = ""
        if self.session.sliced:
            imgui.dummy((0, 15))
            self.centered("Animation properties")
            imgui.align_text_to_frame_padding()
            imgui.text("Interval")
            imgui.same_line(150)
            imgui.set_next_item_width(142)
            changed, interval = imgui.input_float("##interval", self.session.interval)
            if changed:
                self.attempt(lambda: self.session.set_interval(interval))
            imgui.text("Frame IDs: " + ", ".join(map(str, self.session.frames)))
        if self.error:
            imgui.spacing()
            imgui.text_wrapped(self.error)

    @staticmethod
    def texture(image: Image.Image):
        return hello_imgui.create_texture_gpu_from_rgba_data(np.asarray(image, dtype=np.uint8))

    def draw_sheet(self) -> None:
        cursor = imgui.get_cursor_screen_pos()
        self.sheet_origin = (cursor.x, cursor.y)
        key = (astuple(self.session.parameters), self.session.sliced, self.session.scale)
        try:
            if key != self.sheet_key:
                sheet = render_sheet(self.image, self.session)
                scaled = display_image(sheet, (sheet.width * self.session.scale, sheet.height * self.session.scale))
                self.sheet_texture = self.texture(scaled)
                self.sheet_key = key
            if self.sheet_texture is not None:
                texture = self.sheet_texture
                imgui.image(imgui.ImTextureRef(texture.texture_id()), (texture.width, texture.height))
        except ValueError as error:
            self.error = str(error)
            imgui.text_wrapped(self.error)

    def draw_preview(self) -> None:
        session = self.session
        frame_id = session.animation.frame_id if session.animation else None
        if not session.sliced or frame_id is None:
            self.preview_texture = None
            self.preview_key = None
            return
        p = session.parameters
        key = (frame_id, tuple(session.quads), p.width, p.height, session.scale)
        try:
            if key != self.preview_key:
                preview = render_animation(self.image, session)
                if preview is None:
                    return
                # Original stretches a frozen canvas to the current live size.
                # Negative/zero sizes may arise from the shared-vector bug.
                if p.width <= 0 or p.height <= 0:
                    return
                scaled = display_image(preview, (p.width * session.scale, p.height * session.scale))
                self.preview_texture = self.texture(scaled)
                self.preview_key = key
            texture = self.preview_texture
            if texture is not None:
                imgui.image(imgui.ImTextureRef(texture.texture_id()), (texture.width, texture.height))
        except ValueError as error:
            self.error = str(error)
            imgui.text_wrapped(self.error)

    def draw_debug(self) -> None:
        imgui.set_next_window_pos((1050, 650))
        imgui.set_next_window_size((220, 60))
        flags = (imgui.WindowFlags_.no_title_bar | imgui.WindowFlags_.no_resize
                 | imgui.WindowFlags_.no_move | imgui.WindowFlags_.no_saved_settings)
        visible, _ = imgui.begin("Fixed Overlay", flags=flags)
        if visible:
            pos = imgui.get_io().mouse_pos
            x, y = min(1280, max(-1, pos.x)), min(720, max(-1, pos.y))
            imgui.text("Debug info:")
            imgui.text(f"Mouse Position: ({x:g}, {y:g})")
        imgui.end()

    def release(self) -> None:
        # TextureGpu must be destroyed before Hello ImGui destroys the backend.
        self.sheet_texture = None
        self.preview_texture = None

    def runner_params(self):
        params = hello_imgui.RunnerParams()
        params.app_window_params.window_title = "Sprite Sheet Splitter"
        params.app_window_params.window_geometry.size = (1280, 720)
        params.app_window_params.resizable = False
        params.app_window_params.restore_previous_geometry = False
        params.ini_disable = True
        params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
        params.imgui_window_params.show_menu_bar = False
        params.imgui_window_params.show_status_bar = False
        params.imgui_window_params.enable_viewports = False
        params.fps_idling.enable_idling = False  # Animations run even with no input.
        params.callbacks.setup_imgui_style = imgui.style_colors_classic
        params.callbacks.post_new_frame = self.new_frame
        params.callbacks.show_gui = self.draw_debug
        params.callbacks.before_exit = self.release
        params.docking_params.docking_splits = [
            hello_imgui.DockingSplit("MainDockSpace", "LeftDock", imgui.Dir.left, 0.25),
            hello_imgui.DockingSplit("LeftDock", "PreviewDock", imgui.Dir.down, 0.5),
        ]
        params.docking_params.dockable_windows = [
            hello_imgui.DockableWindow("Edit", "LeftDock", self.draw_edit, True, False),
            hello_imgui.DockableWindow("Sprite sheet", "MainDockSpace", self.draw_sheet, True, False),
            hello_imgui.DockableWindow("Preview animation", "PreviewDock", self.draw_preview, True, False),
        ]
        return params


def run(path: str | Path | None = None) -> int:
    image = load_image(path) if path is not None else choose_image()
    if image is None:
        return 0
    application = Application(image)
    hello_imgui.run(application.runner_params())
    return 0
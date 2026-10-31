"""Opt-in real desktop test; normal/headless unit tests do not open windows."""

import os

import pytest
from PIL import Image

pytestmark = pytest.mark.skipif(
    os.environ.get("SPRITE_SPLITTER_GUI_TEST") != "1",
    reason="Set SPRITE_SPLITTER_GUI_TEST=1 with a working desktop/OpenGL display",
)


def test_real_gui_clicks_preview_zoom_and_cancel(monkeypatch, tmp_path):
    from imgui_bundle import hello_imgui, imgui
    from sprite_sheet_splitter.app import Application
    from sprite_sheet_splitter.imaging import load_image

    path = tmp_path / "sheet.png"
    Image.new("RGBA", (512, 1024), (200, 100, 50, 255)).save(path)
    application = Application(load_image(path))
    original_draw_sheet = application.draw_sheet
    sheet_scroll = []

    def draw_sheet():
        original_draw_sheet()
        sheet_scroll.append(imgui.get_scroll_y())

    monkeypatch.setattr(application, "draw_sheet", draw_sheet)
    params = application.runner_params()
    original_button = imgui.button
    buttons = {}
    observations = []
    failures = []
    count = 0

    def button(label, *args, **kwargs):
        pressed = original_button(label, *args, **kwargs)
        low, high = imgui.get_item_rect_min(), imgui.get_item_rect_max()
        buttons[label] = ((low.x + high.x) / 2, (low.y + high.y) / 2)
        return pressed

    monkeypatch.setattr(imgui, "button", button)

    def step():
        nonlocal count
        count += 1
        # Hello ImGui performs an initial hidden layout frame. Wait for the
        # dock builder and native focus to settle before using widget positions.
        frame = count - 4
        io = imgui.get_io()

        def mouse(position, down):
            io.add_focus_event(True)
            io.add_mouse_pos_event(*position)
            io.add_mouse_button_event(0, down)

        try:
            if frame == 2:
                mouse(buttons["Slice"], True)
            elif frame == 3:
                mouse(buttons["Slice"], False)
            elif frame == 5:
                assert application.session.sliced
                observations.append("slice")
            elif frame in (6, 8, 11, 13):
                x, y = application.sheet_origin
                mouse((x + (5 if frame < 10 else 21), y + 5), True)
            elif frame in (7, 9, 12, 14):
                io.add_mouse_button_event(0, False)
            elif frame == 15:
                assert application.session.frames == [1, 2]
                assert application.preview_texture is not None
                observations.append("double-clicks and preview")
                io.add_mouse_wheel_event(0, -2)
            elif frame == 17:
                assert application.session.scale == 1
                assert sheet_scroll[-1] > 0
                observations.append("wheel scroll only")
                mouse(buttons["+##zoom_in"], True)
            elif frame in (18, 20, 22):
                io.add_mouse_button_event(0, False)
            elif frame == 19:
                assert application.session.scale == 2
                assert application.sheet_texture.width == application.image.width * 2
                assert application.preview_texture.width == application.session.parameters.width * 2
                mouse(buttons["-##zoom_out"], True)
            elif frame == 21:
                assert application.session.scale == 1
                observations.append("zoom")
                mouse(buttons["Cancel"], True)
            elif frame == 24:
                assert not application.session.sliced
                assert application.session.frames == []
                assert application.preview_texture is None
                assert application.session.scale == 1
                observations.append("cancel")
                params.app_shall_exit = True
        except BaseException as error:
            # Do not let Python exceptions escape through a native frame callback.
            failures.append(error)
            params.app_shall_exit = True
        if frame > 30:
            params.app_shall_exit = True

    params.callbacks.after_swap = step
    hello_imgui.run(params)
    if failures:
        raise failures[0]
    assert observations == ["slice", "double-clicks and preview", "wheel scroll only", "zoom", "cancel"]
    assert application.sheet_texture is None  # Released before backend shutdown.
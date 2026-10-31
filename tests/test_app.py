from types import SimpleNamespace

from PIL import Image

from sprite_sheet_splitter import app


def result(value):
    return SimpleNamespace(result=lambda: value)


def test_native_dialog_cancel_exits_without_creating_runner(monkeypatch):
    monkeypatch.setattr(app.shutil, "which", lambda _: "/fake/dialog")
    monkeypatch.setattr(app.pfd, "open_file", lambda *_: result([]))
    monkeypatch.setattr(app.hello_imgui, "run", lambda *_: (_ for _ in ()).throw(AssertionError("Runner must not start")))
    assert app.run() == 0


def test_native_dialog_retries_suffix_and_decode_error(monkeypatch, tmp_path):
    path = tmp_path / "valid.PNG"
    Image.new("RGBA", (4, 4), "red").save(path)
    corrupt = tmp_path / "corrupt.tga"
    corrupt.write_bytes(b"corrupt image")
    responses = iter([["unsupported.gif"], [str(corrupt)], [str(path)]])
    errors = []
    monkeypatch.setattr(app.shutil, "which", lambda _: "/fake/dialog")
    monkeypatch.setattr(app.pfd, "open_file", lambda *_: result(next(responses)))
    monkeypatch.setattr(app.pfd, "message", lambda *args: errors.append(args) or result(None))
    image = app.choose_image()
    assert image.size == (4, 4)
    assert image.getpixel((0, 0)) == (255, 0, 0, 255)
    assert len(errors) == 1


def test_sliced_scalar_ignored_but_xy_mutates(monkeypatch):
    application = app.Application(Image.new("RGBA", (16, 16)))
    for name in ("align_text_to_frame_padding", "text", "same_line", "set_next_item_width"):
        monkeypatch.setattr(app.imgui, name, lambda *_: None)
    monkeypatch.setattr(app.imgui, "input_int", lambda _label, value, _step: (True, value + 1))
    application.scalar("Number of rows", "rows")
    assert application.session.parameters.rows == 5
    application.session.slice()
    application.scalar("Number of rows", "rows")
    assert application.session.parameters.rows == 5
    application.xy("Pixels per sprite", "width", "height")
    assert application.session.parameters.width == 17
    assert application.session.parameters.height == 33
    assert application.session.animation_size == (16, 32)


def test_mouse_wheel_does_not_zoom_or_consume_imgui_scroll(monkeypatch):
    application = app.Application(Image.new("RGBA", (16, 16)))
    io = SimpleNamespace(mouse_wheel=2.0, mouse_wheel_h=1.0, delta_time=0.1)
    monkeypatch.setattr(app.imgui, "get_io", lambda: io)
    application.new_frame()
    assert application.session.scale == 1
    assert io.mouse_wheel == 2.0
    assert io.mouse_wheel_h == 1.0


def test_zoom_buttons_work_in_editing_and_sliced_modes(monkeypatch):
    application = app.Application(Image.new("RGBA", (16, 16)))
    for name in (
        "text", "same_line", "spacing", "push_style_color", "pop_style_color",
        "dummy", "set_cursor_pos_x", "align_text_to_frame_padding", "set_next_item_width",
    ):
        monkeypatch.setattr(app.imgui, name, lambda *_: None)
    monkeypatch.setattr(application, "centered", lambda *_: None)
    monkeypatch.setattr(application, "scalar", lambda *_: None)
    monkeypatch.setattr(application, "xy", lambda *_: None)
    monkeypatch.setattr(app.imgui, "input_float", lambda _label, value: (False, value))
    pressed = "-##zoom_out"
    monkeypatch.setattr(app.imgui, "button", lambda label, *_: label == pressed)
    application.draw_edit()
    assert application.session.scale == 1
    pressed = "+##zoom_in"
    application.draw_edit()
    assert application.session.scale == 2
    application.session.slice()
    application.draw_edit()
    assert application.session.scale == 3
    pressed = "-##zoom_out"
    application.draw_edit()
    assert application.session.scale == 2
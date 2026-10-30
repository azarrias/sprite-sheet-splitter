from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from sprite_sheet_splitter.imaging import (
    clamped_crop, display_image, load_image, render_animation, render_sheet, supported_filename,
)
from sprite_sheet_splitter.model import Parameters, Region, Session

ROOT = Path(__file__).resolve().parents[1]


def sample_image():
    values = np.arange(6 * 5 * 4, dtype=np.uint8).reshape((5, 6, 4))
    values[:, :, 3] = 128
    return Image.fromarray(values)


@pytest.mark.parametrize("extension", ["png", "PNG", "tga", "TGA"])
def test_formats_alpha_and_unicode_paths(tmp_path, extension):
    image = sample_image()
    path = tmp_path / f"sp ace-é猫.{extension}"
    image.save(path)
    assert load_image(path).tobytes() == image.tobytes()


def test_filename_quirk_and_unsupported_or_corrupt(tmp_path):
    assert supported_filename("not_an_extensionpng")
    assert not supported_filename("test.jpeg")
    path = tmp_path / "broken.png"
    path.write_bytes(b"not an image")
    with pytest.raises(OSError):
        load_image(path)
    with pytest.raises(ValueError):
        load_image(tmp_path / "anything.jpg")


@pytest.mark.parametrize("x,y", [(-20, -20), (-2, -2), (0, 0), (4, 3), (20, 20), (20, -10)])
def test_clamp_to_edge_not_transparent_padding(x, y):
    image = sample_image()
    actual = np.asarray(clamped_crop(image, Region(x, y, 8, 7)))
    source = np.asarray(image)
    expected = source[np.clip(np.arange(y, y + 7), 0, image.height - 1)[:, None], np.clip(np.arange(x, x + 8), 0, image.width - 1)]
    assert np.array_equal(actual, expected)


def test_black_background_only_slices_and_frozen_preview():
    image = Image.new("RGBA", (10, 10), (200, 100, 50, 128))
    s = Session(Parameters(1, 1, 2, 2, 2, 2))
    editing = render_sheet(image, s, overlays=False)
    assert editing.getpixel((0, 0)) == (100, 50, 25, 255)
    s.slice()
    sliced = render_sheet(image, s, overlays=False)
    assert sliced.getpixel((0, 0)) == (0, 0, 0, 255)
    assert sliced.getpixel((2, 2)) == editing.getpixel((2, 2))
    assert render_animation(image, s) is None
    s.set_interval(0.2)  # Original builds an empty animation; display safely blank.
    assert render_animation(image, s) is None
    s.double_click(3, 3)
    s.parameters.width = 5
    s.parameters.offset_x = 4
    assert render_animation(image, s).size == (2, 2)
    shifted = render_sheet(image, s, overlays=False)
    assert shifted.getpixel((2, 2)) == (0, 0, 0, 255)
    assert shifted.getpixel((4, 2)) == (100, 50, 25, 255)


def test_nearest_neighbor_and_display_safety():
    image = sample_image()
    zoomed = display_image(image, (12, 10))
    assert zoomed.getpixel((2, 2)) == image.getpixel((1, 1))
    with pytest.raises(ValueError):
        display_image(image, (1_000_000, 1_000_000))


@pytest.mark.parametrize("asset", [False, True])
@pytest.mark.parametrize("params", [Parameters(), Parameters(2, 3, 4, 3, -2, 1, 1, 2), Parameters(2, 2, 4, 4, 0, 0, -2, -2)])
def test_canvas_pixels_from_actual_lua_draw_calls(lua, asset, params):
    """Execute original renderer; independently sample its emitted draw calls.

    This is not a LÖVE GPU screenshot comparison: line/font rendering are omitted
    and the LÖVE draw API is replaced by a small Pillow/NumPy software adapter.
    """
    image = load_image(ROOT / "src/graphics/character.png") if asset else sample_image()
    g = lua.globals()
    g.reset_session(params.rows, params.columns, params.width, params.height, params.offset_x, params.offset_y, params.padding_x, params.padding_y)
    source = np.asarray(image)
    target = None

    def clear(*_):
        target.paste((0, 0, 0, 255), (0, 0, *target.size))

    def draw(_atlas, *args):
        if len(args) == 2:
            tile, x, y = image, *args
        else:
            q, x, y = args[:3]  # Animation supplies identity transform arguments too.
            ys = np.clip(np.arange(q.y, q.y + q.height), 0, image.height - 1)
            xs = np.clip(np.arange(q.x, q.x + q.width), 0, image.width - 1)
            tile = Image.fromarray(source[ys[:, None], xs])
        # Pillow alpha_composite clips destinations in the same canvas extent.
        target.alpha_composite(tile, (int(x), int(y)))

    graphics = g.love.graphics
    graphics.setCanvas = lambda *args: None
    graphics.setBlendMode = lambda *_: None
    graphics.setColor = lambda *_: None
    graphics.setLineStyle = lambda *_: None
    graphics.rectangle = lambda *_: None
    graphics.printf = lambda *_: None
    graphics.clear, graphics.draw = clear, draw
    lua.execute("""
        canvasBackgroundColor = {0,0,0,1}
        sliceLineColor = {0.9,0.9,0.9,0.3}
        themePrimaryColor = {1,1,1,1}
        numbersColor = {1,0.7,0.7,0.7}
        WINDOW_WIDTH = 1280
        unpack = table.unpack or unpack
    """)
    session = Session(params)
    for sliced in (False, True):
        target = Image.new("RGBA", image.size)
        if sliced:
            lua.execute("appStateMachine.current:ClickSlice(); SlicerGUI.DrawQuadsToCanvas(gui)")
            session.slice()
        else:
            lua.execute("SlicerGUI.DrawImageToCanvas(gui)")
        assert render_sheet(image, session, overlays=False).tobytes() == target.tobytes()
    session.double_click(params.offset_x + 1, params.offset_y + 1)
    lua.execute("""
        appStateMachine.current.animationFrames:push_back(1)
        appStateMachine.current:rebuildAnimation()
    """)
    target = Image.new("RGBA", (params.width, params.height))
    lua.execute("SlicerGUI.DrawAnimationToCanvas(gui)")
    assert render_animation(image, session).tobytes() == target.tobytes()
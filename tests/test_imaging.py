import numpy as np
from PIL import Image
import pytest

from sprite_sheet_splitter.imaging import (
    clamped_crop,
    display_image,
    draw_grid,
    load_image,
    render_animation,
    render_sheet,
    supported_filename,
)
from sprite_sheet_splitter.model import Parameters, Region, Session

def sample_image(size=(6, 5)):
    width, height = size
    values = np.arange(width * height * 4, dtype=np.uint8).reshape((height, width, 4))
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
    s.set_interval(0.2)  # An empty animation must still display safely blank.
    assert render_animation(image, s) is None
    s.double_click(3, 3)
    s.parameters.width = 5
    s.parameters.offset_x = 4
    assert render_animation(image, s).size == (2, 2)
    shifted = render_sheet(image, s, overlays=False)
    assert shifted.getpixel((2, 2)) == (0, 0, 0, 255)
    assert shifted.getpixel((4, 2)) == (100, 50, 25, 255)


def test_grid_outline_matches_sampled_pixel_bounds():
    canvas = Image.new("RGBA", (8, 8), (0, 0, 0, 255))
    original = canvas.getpixel((3, 3))

    draw_grid(canvas, Region(2, 2, 4, 4))

    assert canvas.getpixel((2, 3)) != original
    assert canvas.getpixel((5, 3)) != original
    assert canvas.getpixel((3, 2)) != original
    assert canvas.getpixel((3, 5)) != original
    assert canvas.getpixel((3, 3)) == original
    assert canvas.getpixel((1, 3)) == original
    assert canvas.getpixel((6, 3)) == original


def test_nearest_neighbor_and_display_safety():
    image = sample_image()
    zoomed = display_image(image, (12, 10))
    assert zoomed.getpixel((2, 2)) == image.getpixel((1, 1))
    with pytest.raises(ValueError):
        display_image(image, (1_000_000, 1_000_000))


@pytest.mark.parametrize("size", [(6, 5), (64, 128)])
@pytest.mark.parametrize("params", [Parameters(), Parameters(2, 3, 4, 3, -2, 1, 1, 2), Parameters(2, 2, 4, 4, 0, 0, -2, -2)])
def test_canvas_pixels_against_independent_sampler(size, params):
    """Check alpha, clipping, overlap and edge sampling without GUI rendering."""
    image = sample_image(size)
    source = np.asarray(image)

    def tile(x, y):
        ys = np.clip(np.arange(y, y + params.height), 0, image.height - 1)
        xs = np.clip(np.arange(x, x + params.width), 0, image.width - 1)
        return Image.fromarray(source[ys[:, None], xs])

    session = Session(params)
    editing = Image.new("RGBA", image.size, (0, 0, 0, 255))
    editing.alpha_composite(image)
    assert render_sheet(image, session, overlays=False).tobytes() == editing.tobytes()

    session.slice()
    sliced = Image.new("RGBA", image.size, (0, 0, 0, 255))
    for row in range(params.rows):
        for column in range(params.columns):
            x = params.offset_x + column * (params.width + params.padding_x)
            y = params.offset_y + row * (params.height + params.padding_y)
            sliced.alpha_composite(tile(x, y), (x, y))
    assert render_sheet(image, session, overlays=False).tobytes() == sliced.tobytes()

    session.double_click(params.offset_x + 1, params.offset_y + 1)
    assert session.animation.frame_id == 1
    preview = Image.new("RGBA", (params.width, params.height), (0, 0, 0, 255))
    preview.alpha_composite(tile(params.offset_x, params.offset_y))
    assert render_animation(image, session).tobytes() == preview.tobytes()
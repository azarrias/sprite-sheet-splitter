"""Pillow rendering for black-backed sprite sheets and animation previews."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .model import Region, Session, check_canvas, generate_quads

BLACK = (0, 0, 0, 255)
GRID = (230, 230, 230, 76)
NUMBERS = (255, 178, 178, 178)


def supported_filename(path: str | Path) -> bool:
    # Match the final three characters; a separating dot is not required.
    return str(path)[-3:].lower() in ("png", "tga")


def load_image(path: str | Path) -> Image.Image:
    if not supported_filename(path):
        raise ValueError("Choose a PNG or TGA image.")
    with Image.open(path) as source:
        check_canvas(*source.size)
        return source.convert("RGBA")


def clamped_crop(image: Image.Image, region: Region) -> Image.Image:
    """Clamp-to-edge texture sampling, including completely outside quads.

    Construct at most nine pieces: valid pixels, stretched edge strips, corners.
    Pillow crop alone would incorrectly fill the outside with transparent black.
    """
    check_canvas(region.width, region.height)
    result = Image.new("RGBA", (region.width, region.height))

    def segments(start: int, size: int, extent: int):
        end = start + size
        cuts = sorted({start, end, max(start, min(end, 0)), max(start, min(end, extent))})
        for left, right in zip(cuts, cuts[1:]):
            if left < right:
                yield (
                    left - start,
                    right - left,
                    max(0, min(extent - 1, left)),
                    max(1, min(extent, right)),
                )

    for dx, width, left, right in segments(region.x, region.width, image.width):
        for dy, height, top, bottom in segments(region.y, region.height, image.height):
            piece = image.crop((left, top, right, bottom))
            if piece.size != (width, height):
                piece = piece.resize((width, height), Image.Resampling.NEAREST)
            result.paste(piece, (dx, dy))
    return result


def draw_region(canvas: Image.Image, image: Image.Image, region: Region, x: int, y: int) -> None:
    """Clip before extracting; off-canvas regions must not allocate large tiles."""
    left, top = max(0, x), max(0, y)
    right, bottom = min(canvas.width, x + region.width), min(canvas.height, y + region.height)
    if right > left and bottom > top:
        clipped = Region(region.x + left - x, region.y + top - y, right - left, bottom - top)
        piece = clamped_crop(image, clipped)
        canvas.alpha_composite(piece, (left, top))


def draw_grid(canvas: Image.Image, rect: Region) -> None:
    x1, x2 = sorted((rect.x + 1, rect.x + rect.width))
    y1, y2 = sorted((rect.y + 1, rect.y + rect.height))
    left, right = max(0, x1), min(canvas.width - 1, x2)
    top, bottom = max(0, y1), min(canvas.height - 1, y2)
    if left > right or top > bottom:
        return
    overlay = Image.new("RGBA", (right - left + 1, bottom - top + 1))
    draw = ImageDraw.Draw(overlay)
    for y in (y1, y2):
        if top <= y <= bottom:
            draw.line((0, y - top, right - left, y - top), fill=GRID)
    for x in (x1, x2):
        if left <= x <= right:
            draw.line((x - left, 0, x - left, bottom - top), fill=GRID)
    canvas.alpha_composite(overlay, (left, top))


def draw_number(canvas: Image.Image, text: str, rect: Region, font) -> None:
    x, y = rect.x + 2, rect.y
    bx1, by1, bx2, by2 = font.getbbox(text)
    left, top = max(0, x + bx1), max(0, y + by1)
    right, bottom = min(canvas.width, x + bx2), min(canvas.height, y + by2)
    if right <= left or bottom <= top:
        return
    overlay = Image.new("RGBA", (right - left, bottom - top))
    ImageDraw.Draw(overlay).text((x - left, y - top), text, font=font, fill=NUMBERS)
    canvas.alpha_composite(overlay, (left, top))


def render_sheet(image: Image.Image, session: Session, *, overlays: bool = True) -> Image.Image:
    """Frozen sources, live destination geometry, canvas clipped to sheet size."""
    canvas = Image.new("RGBA", image.size, BLACK)
    live = generate_quads(session.parameters)
    font = ImageFont.load_default(size=8) if overlays and session.sliced else None
    if not session.sliced:
        canvas.alpha_composite(image)
    for index, rect in enumerate(live, 1):
        if session.sliced:
            draw_region(canvas, image, session.quads[index - 1], rect.x, rect.y)
        if overlays:
            # Composite per region, not all lines at once: later sprites can
            # cover earlier outlines/numbers when negative padding overlaps.
            draw_grid(canvas, rect)
            if session.sliced:
                draw_number(canvas, str(index), rect, font)
    return canvas


def render_animation(image: Image.Image, session: Session) -> Image.Image | None:
    if not session.sliced or session.animation is None or session.animation.frame_id is None:
        return None
    assert session.animation_size is not None
    canvas = Image.new("RGBA", session.animation_size, BLACK)
    region = session.quads[session.animation.frame_id - 1]
    draw_region(canvas, image, region, 0, 0)
    return canvas


def display_image(image: Image.Image, size: tuple[float, float]) -> Image.Image:
    """Pre-scale nearest so the runner's GPU sampler cannot blur pixel art."""
    width, height = (max(1, round(value)) for value in size)
    check_canvas(width, height)
    return image.resize((width, height), Image.Resampling.NEAREST)
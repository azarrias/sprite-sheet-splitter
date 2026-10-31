"""GUI-independent sprite geometry, animation timing, and editing session."""

from dataclasses import dataclass, field
import math

MAX_REGIONS = 100_000
MAX_PIXELS = 64_000_000


def check_canvas(width: int, height: int) -> None:
    if width <= 0 or height <= 0:
        raise ValueError("Pixels per sprite must be positive to create a canvas.")
    if width * height > MAX_PIXELS:
        raise ValueError("Canvas exceeds the safety limit of 64 million pixels.")


@dataclass
class Parameters:
    rows: int = 4
    columns: int = 4
    width: int = 16
    height: int = 32
    offset_x: int = 0
    offset_y: int = 0
    padding_x: int = 0
    padding_y: int = 0


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    width: int
    height: int


def generate_quads(params: Parameters) -> list[Region]:
    """Row-major, no image-bounds checks; nonpositive counts yield no quads."""
    count = max(0, params.rows) * max(0, params.columns)
    if count > MAX_REGIONS:
        raise ValueError("Grid exceeds the safety limit of 100,000 regions.")
    if not count:
        return []
    return [
        Region(
            params.offset_x + column * (params.width + params.padding_x),
            params.offset_y + row * (params.height + params.padding_y),
            params.width,
            params.height,
        )
        for row in range(params.rows)
        for column in range(params.columns)
    ]


@dataclass
class Animation:
    frames: list[int]
    interval: float = 0.5
    timer: float = 0.0
    current_frame: int = 1  # Frame positions and IDs are deliberately 1-based.

    def __post_init__(self) -> None:
        if not math.isfinite(self.interval) or self.interval <= 0:
            raise ValueError("Interval must be a finite number greater than zero.")

    @property
    def frame_id(self) -> int | None:
        return self.frames[self.current_frame - 1] if self.frames else None

    def update(self, dt: float) -> None:
        if len(self.frames) > 1:
            self.timer += dt
            if self.timer > self.interval:
                self.timer %= self.interval
                self.current_frame = max(
                    1, (self.current_frame + 1) % (len(self.frames) + 1)
                )


@dataclass
class Session:
    parameters: Parameters = field(default_factory=Parameters)
    sliced: bool = False
    scale: float = 1
    quads: list[Region] = field(default_factory=list)
    frames: list[int] = field(default_factory=list)
    interval: float = 0.5
    animation: Animation | None = None
    animation_size: tuple[int, int] | None = None

    def slice(self) -> None:
        if self.sliced:
            return
        p = self.parameters
        check_canvas(p.width, p.height)
        quads = generate_quads(p)
        self.quads = quads
        self.animation_size = (p.width, p.height)
        self.frames.clear()
        self.interval = 0.5
        self.animation = None
        self.sliced = True

    def cancel(self) -> None:
        if self.sliced:
            self.frames.clear()
            self.animation = None
            self.sliced = False

    def set_interval(self, interval: float) -> None:
        # Construct first so invalid input never poisons the running animation.
        animation = Animation(self.frames.copy(), interval)
        self.interval = interval
        self.animation = animation

    def hit_test(self, x: float, y: float) -> list[int]:
        """Image-space coordinates, inclusive edges and all matches, not first."""
        if not self.sliced:
            return []
        return [
            index
            for index, rect in enumerate(generate_quads(self.parameters), 1)
            if rect.x <= x <= rect.x + rect.width
            and rect.y <= y <= rect.y + rect.height
        ]

    def double_click(self, x: float, y: float) -> list[int]:
        hits = self.hit_test(x, y)
        for frame_id in hits:
            self.frames.append(frame_id)
            self.animation = Animation(self.frames.copy(), self.interval)
        return hits

    def zoom(self, delta: float) -> None:
        """Adjust the shared sheet/preview scale, with a minimum of 1x."""
        self.scale = max(1, self.scale + delta)

    def update(self, dt: float) -> None:
        if self.animation is not None:
            self.animation.update(dt)
import math
import random

import pytest

from sprite_sheet_splitter.model import Animation, Parameters, Session, generate_quads


def test_defaults_and_workflow():
    s = Session()
    assert s.parameters == Parameters(4, 4, 16, 32, 0, 0, 0, 0)
    s.cancel()
    assert not s.sliced
    s.slice()
    assert len(s.quads) == 16
    assert s.animation_size == (16, 32)
    assert s.double_click(1, 1) == [1]
    assert s.double_click(1, 1) == [1]
    assert s.double_click(17, 1) == [2]
    assert s.frames == [1, 1, 2]
    s.update(0.6)
    assert s.animation.current_frame == 2
    s.set_interval(0.1)
    assert s.animation.current_frame == 1
    assert s.animation.timer == 0
    s.slice()  # No-op after Slice.
    assert s.interval == 0.1
    s.zoom(4)
    s.cancel()
    assert s.frames == [] and s.animation is None
    assert s.scale == 5
    s.slice()
    assert s.interval == 0.5


def test_live_vectors_frozen_sources_and_shared_edges():
    s = Session(Parameters(2, 2, 4, 4))
    s.slice()
    assert s.double_click(4, 4) == [1, 2, 3, 4]
    frozen = s.quads.copy()
    s.parameters.offset_x = -2
    s.parameters.padding_x = -2
    s.parameters.width = 8
    assert s.double_click(4, 1) == [1, 2]
    assert s.quads == frozen
    assert s.animation_size == (4, 4)


def test_timer_strict_threshold_one_step_and_single_frame():
    a = Animation([1, 2, 3])
    a.update(0.5)
    assert a.current_frame == 1
    a.update(0.01)
    assert a.current_frame == 2
    a.update(20)
    assert a.current_frame == 3
    a.update(0.5)
    assert a.current_frame == 1
    single = Animation([7])
    single.update(100)
    assert single.frame_id == 7 and single.timer == 0


@pytest.mark.parametrize("interval", [0, -0.5, math.nan, math.inf, -math.inf])
def test_unsafe_interval_is_rejected_atomically(interval):
    s = Session()
    s.slice()
    s.double_click(1, 1)
    animation = s.animation
    with pytest.raises(ValueError):
        s.set_interval(interval)
    assert s.interval == 0.5 and s.animation is animation


@pytest.mark.parametrize("rows,columns", [(0, 2), (-2, 3), (2, 0), (1_000_000_000, 0)])
def test_nonpositive_counts_produce_no_regions(rows, columns):
    s = Session(Parameters(rows=rows, columns=columns))
    s.slice()
    assert not s.quads
    assert not s.double_click(1, 1)


def test_safety_limits_and_zoom():
    for p in (Parameters(width=0), Parameters(height=-1), Parameters(rows=1000, columns=1000), Parameters(width=10000, height=10000)):
        s = Session(p)
        with pytest.raises(ValueError):
            s.slice()
        assert not s.sliced
    s = Session()
    s.zoom(-100)
    assert s.scale == 1
    s.zoom(0.5)
    assert s.scale == 1.5


def test_generate_quads_row_major_geometry_randomized():
    rng = random.Random(410088)
    for _ in range(250):
        p = Parameters(
            rng.randint(-2, 8), rng.randint(-2, 8),
            rng.randint(1, 32), rng.randint(1, 32),
            rng.randint(-40, 40), rng.randint(-40, 40),
            rng.randint(-20, 20), rng.randint(-20, 20),
        )
        expected = []
        y = p.offset_y
        for _row in range(p.rows):
            x = p.offset_x
            for _column in range(p.columns):
                expected.append((x, y, p.width, p.height))
                x += p.width + p.padding_x
            y += p.height + p.padding_y
        actual = [(q.x, q.y, q.width, q.height) for q in generate_quads(p)]
        assert actual == expected


@pytest.mark.parametrize("frames,interval", [([], 0.5), ([4], 0.1), ([1, 2, 1, 3], 0.5), ([2, 9], 0.07)])
def test_animation_empty_single_and_repeated_sequences(frames, interval):
    animation = Animation(frames, interval)
    animation.update(0)
    assert animation.current_frame == 1
    assert animation.frame_id == (frames[0] if frames else None)
    for step in range(1, 121):
        # A long update advances exactly once, including across sequence wraps.
        animation.update(interval * 2.5)
        if len(frames) > 1:
            assert animation.current_frame == step % len(frames) + 1
            assert animation.frame_id == frames[step % len(frames)]
            assert 0 <= animation.timer < interval
        else:
            assert animation.current_frame == 1
            assert animation.frame_id == (frames[0] if frames else None)
            assert animation.timer == 0


def test_slice_state_selection_trace_and_live_geometry():
    s = Session(Parameters(2, 2, 4, 4))
    s.slice()
    # All four inclusive boundary hits, repeated frames, outside clicks.
    expected = []
    for x, y, hits in [
        (4, 4, [1, 2, 3, 4]),
        (1, 1, [1]),
        (-1, 1, []),
        (5, 5, [4]),
        (4, 4, [1, 2, 3, 4]),
    ]:
        assert s.double_click(x, y) == hits
        expected.extend(hits)
        s.update(0.1)
        assert s.frames == expected
        assert s.animation.current_frame == 1
    frozen = s.quads.copy()
    s.parameters.width, s.parameters.offset_x, s.parameters.padding_x = 8, -2, -2
    assert s.double_click(4, 1) == [1, 2]
    s.set_interval(0.2)
    assert s.frames == expected + [1, 2]
    assert s.quads == frozen
    assert s.animation_size == (4, 4)
    assert s.animation.current_frame == 1
    assert s.animation.timer == 0
    s.cancel()
    assert not s.sliced
    assert s.frames == [] and s.animation is None
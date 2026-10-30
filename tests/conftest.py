from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def lua():
    """Run unchanged original source; stub only the unavailable LÖVE services."""
    # LÖVE uses LuaJIT/5.1. Lupa's default can be Lua 5.5, which rejects
    # assignments to generic-for loop variables in the original class helper.
    lupa = pytest.importorskip("lupa.luajit21", reason="Install .[test] for Lua parity checks")
    runtime = lupa.LuaRuntime(unpack_returned_tuples=True)
    runtime.globals().source_dir = (ROOT / "src").as_posix()
    runtime.execute("""
        package.path = source_dir .. '/?.lua;' .. package.path
        Class = require 'libs.class'
        require 'Vector2D'
        require 'Deque'
        require 'BaseState'
        require 'Animation'
        require 'StateMachine'
        require 'AppStateStart'
        require 'AppStateSlice'
        require 'SlicerGUI'
        require 'util'
        love = {
            graphics = {
                newQuad = function(x, y, w, h, aw, ah)
                    return {x=x, y=y, width=w, height=h}
                end,
                newCanvas = function(w, h) return {width=w, height=h} end
            },
            mouse = { doubleClicks = Deque() }
        }
        atlas = {
            getDimensions = function() return 272, 256 end,
            getWidth = function() return 272 end,
            getHeight = function() return 256 end
        }
        function reset_session(rows, columns, w, h, ox, oy, px, py)
            nrOfRows, nrOfColumns = rows, columns
            spriteSize, offset, padding = Vector2D(w,h), Vector2D(ox,oy), Vector2D(px,py)
            spriteSheetScale = 1
            gui = {
                image = atlas,
                spriteSheetPos = Vector2D(0,0),
                update = function() end
            }
            appStateMachine = StateMachine {
                start = function() return AppStateStart() end,
                slice = function() return AppStateSlice() end
            }
            appStateMachine:change('start')
        end
    """)
    return runtime
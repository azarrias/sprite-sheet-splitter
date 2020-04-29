-- libraries
Class = require 'libs.class'
push = require 'libs.push'
imgui = require 'imgui'
nfd = require 'nfd'

-- general purpose / utility
require 'StateMachine'
require 'BaseState'
require 'Animation'
require 'AppStateSlice'
require 'AppStateStart'
require 'Deque'
require 'SlicerGUI'
require 'util'
require 'Vector2D'

--[[
    constants
  ]]
GAME_TITLE = 'Sprite Sheet Splitter'

-- OS checks in order to make necessary adjustments to support multiplatform
MOBILE_OS = (love._version_major > 0 or love._version_minor >= 9) and (love.system.getOS() == 'Android' or love.system.getOS() == 'OS X')
WEB_OS = (love._version_major > 0 or love._version_minor >= 9) and love.system.getOS() == 'Web'
  
-- pixels resolution
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

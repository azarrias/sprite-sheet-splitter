require 'globals'

local FONT_SIZE = 16

function love.load()
  if arg[#arg] == "-debug" then 
    require("mobdebug").start() 
  end

  -- use nearest-neighbor (point) filtering on upscaling and downscaling to prevent blurring of text and 
  -- graphics instead of the bilinear filter that is applied by default 
  love.graphics.setDefaultFilter('nearest', 'nearest')
  
  -- Set up window
  push:setupScreen(VIRTUAL_WIDTH, VIRTUAL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, {
    vsync = true,
    fullscreen = MOBILE_OS,
    resizable = not MOBILE_OS
  })
  love.window.setTitle(GAME_TITLE)
  
  font = love.graphics.newFont(FONT_SIZE)
  love.graphics.setFont(font)
  os_str = love.system.getOS()
  vmajor, vminor, vrevision, vcodename = love.getVersion()
  v_str = string.format("Love version: %d.%d.%d - %s", vmajor, vminor, vrevision, vcodename)
  bd_str = love.filesystem.getSourceBaseDirectory()
  wd_str = love.filesystem.getWorkingDirectory()
  
  love.keyboard.keysPressed = {}
end

function love.update(dt)
  -- exit if esc is pressed
  if love.keyboard.keysPressed['escape'] then
    love.event.quit()
  end
  
  love.keyboard.keysPressed = {}
end

function love.resize(w, h)
  push:resize(w, h)
end
  
-- Callback that processes key strokes just once
-- Does not account for keys being held down
function love.keypressed(key)
  love.keyboard.keysPressed[key] = true
end

function love.draw()
  push:start()
  love.graphics.print(GAME_TITLE, 0, 0)
  love.graphics.print("O.S.: " .. os_str, 0, 16)
  love.graphics.print(v_str, 0, 32)
  love.graphics.print("Source base path: " .. bd_str, 0, 48)
  love.graphics.print("Working path: " .. wd_str, 0, 64)
  push:finish()
end
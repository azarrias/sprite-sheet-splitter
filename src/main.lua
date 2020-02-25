require 'globals'

--
-- LOVE callbacks
--
function love.load(arg)
  love.window.setMode(WINDOW_WIDTH, WINDOW_HEIGHT)
  love.window.setTitle(GAME_TITLE)
  love.graphics.setDefaultFilter('nearest', 'nearest')
  test = love.graphics.newImage('graphics/character.png') 
  canvas = love.graphics.newCanvas(test:getWidth(), test:getHeight())
end

function love.update(dt)
  imgui.NewFrame()
end

function love.draw()
  love.graphics.setCanvas(canvas)
  love.graphics.setBlendMode('alpha', 'alphamultiply')
  love.graphics.draw(test, 0, 0)  
  love.graphics.setCanvas()
  
  imgui.SetNextWindowPos(0, 0)
  imgui.SetNextWindowSize(love.graphics.getWidth(), love.graphics.getHeight())
  
  if imgui.Begin("DockArea", nil, { "NoResize", "NoMove", "NoBrinToFrontOnFocus" }) then
    imgui.BeginDockspace()
    
    imgui.SetNextDock("Right")
    imgui.SetNextDockSplitRatio(0.7, 0.7)
    imgui.BeginDock("Edit")
    imgui.Text("Testing...")
    imgui.EndDock()
    
    --[[
    Broken docks on master: BeginDock doesn't return a boolean
    https://github.com/slages/love-imgui/issues/28
    
    if imgui.BeginDock("Edit") then
       ...  
    end
    ]]
    imgui.SetNextDock("Left")
    imgui.BeginDock("Sprite sheet")
    imgui.Image(canvas, test:getWidth() * 2, test:getHeight() * 2)
    imgui.EndDock()
   
    imgui.EndDockspace()
  end
  
  imgui.End()
  
  love.graphics.clear(1, 1, 1)
  --love.graphics.draw(test, 0, 0)
  imgui.Render();
end

function love.quit()
  imgui.ShutDown();
end

--
-- User inputs
--
function love.textinput(t)
    imgui.TextInput(t)
    if not imgui.GetWantCaptureKeyboard() then
        -- Pass event to the game
    end
end

function love.keypressed(key)
    imgui.KeyPressed(key)
    if not imgui.GetWantCaptureKeyboard() then
        -- Pass event to the game
    end
end

function love.keyreleased(key)
    imgui.KeyReleased(key)
    if not imgui.GetWantCaptureKeyboard() then
        -- Pass event to the game
    end
end

function love.mousemoved(x, y)
    imgui.MouseMoved(x, y)
    if not imgui.GetWantCaptureMouse() then
        -- Pass event to the game
    end
end

function love.mousepressed(x, y, button)
    imgui.MousePressed(button)
    if not imgui.GetWantCaptureMouse() then
        -- Pass event to the game
    end
end

function love.mousereleased(x, y, button)
    imgui.MouseReleased(button)
    if not imgui.GetWantCaptureMouse() then
        -- Pass event to the game
    end
end

function love.wheelmoved(x, y)
    imgui.WheelMoved(y)
    if not imgui.GetWantCaptureMouse() then
        -- Pass event to the game
    end
end
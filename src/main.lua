require 'globals'

-- application global parameters
debugMode = true
spriteSheetScale = 1
nrOfRows = 4
nrOfColumns = 4
spriteSize = Vector2D(16, 32)
offset = Vector2D(0, 0)
padding = Vector2D(0, 0)
sliceLineColor = { 0.9, 0.9, 0.9, 0.3 }
canvasBackgroundColor = { 0, 0, 0, 1 }
themePrimaryColor = { 1, 1, 1, 1 }
backgroundTint = { 1, 1, 1, 1 }

function love.load(arg)
  if debugMode and arg[#arg] == "-debug" then 
    require("mobdebug").start() 
  end
  
  love.window.setMode(WINDOW_WIDTH, WINDOW_HEIGHT)
  love.window.setTitle(GAME_TITLE)
  love.graphics.setDefaultFilter('nearest', 'nearest')
  gui = SlicerGUI()
  
  appStateMachine = StateMachine {
    ['start'] = function() return AppStateStart() end,
    ['slice'] = function() return AppStateSlice() end
  }
  appStateMachine:change('start')
  
  love.mouse.doubleClicks = Deque()
end

function love.update(dt)
  appStateMachine:update(dt)
  love.mouse.doubleClicks:clear()
end

function love.draw()
  appStateMachine:render()
end

function love.quit()
  imgui.ShutDown()
end

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

function love.mousepressed(x, y, button, istouch, presses)
    if button == 1 and presses > 1 then
      love.mouse.doubleClicks:push_front(Vector2D(x, y))
    end
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
    spriteSheetScale = math.max(spriteSheetScale + y, 1)
    imgui.WheelMoved(y)
    if not imgui.GetWantCaptureMouse() then
        -- Pass event to the game
    end
end
require 'globals'

local spriteSheetScale = 1
local nrOfRows = 4
local nrOfColumns = 4
local spriteSize = Vector2D(16, 32)
local offset = Vector2D(0, 0)
local padding = Vector2D(0, 0)

function love.load(arg)
  if arg[#arg] == "-debug" then 
    require("mobdebug").start() 
  end
  
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
  love.graphics.clear(0, 0, 0)
  love.graphics.draw(test, 0, 0)
  
  love.graphics.setColor(0.9, 0.9, 0.9, 0.3)
  love.graphics.setLineStyle('rough')
  for y = 1, nrOfRows do
    for x = 1, nrOfColumns do
      love.graphics.rectangle('line', 
        (x - 1) * (spriteSize.x + padding.x) + offset.x + 1, 
        (y - 1) * (spriteSize.y + padding.y) + offset.y + 1, 
        spriteSize.x - 1, 
        spriteSize.y - 1)
    end
  end
  love.graphics.setColor(1, 1, 1)
  
  love.graphics.setCanvas()
  
  imgui.SetNextWindowPos(0, 0)
  imgui.SetNextWindowSize(love.graphics.getWidth(), love.graphics.getHeight())
  
  if imgui.Begin("DockArea", nil, { "ImGuiWindowFlags_NoTitleBar", "NoResize", "NoMove", "NoBringToFrontOnFocus" }) then
    imgui.BeginDockspace()
    
    imgui.SetNextDock("Right")
    imgui.SetNextDockSplitRatio(0.7, 0.7)
    imgui.BeginDock("Edit")
    imgui.Text("Slicing parameters")
    
    nrOfRows = RenderIntParameter("Number of rows", "##nrOfRows", nrOfRows)
    nrOfColumns = RenderIntParameter("Number of columns", "##nrOfColumns", nrOfColumns)
    spriteSize = RenderXYParameter("Pixels per sprite", "##spriteSize", spriteSize)
    offset = RenderXYParameter("Offset", "##offset", offset)
    padding = RenderXYParameter("Padding", "##padding", padding)

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
    imgui.Image(canvas, test:getWidth() * spriteSheetScale, test:getHeight() * spriteSheetScale)
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

function RenderIntParameter(label, id, value)
  imgui.AlignTextToFramePadding()
  imgui.Text(label)
  imgui.SameLine(150)
  imgui.PushItemWidth(142)
  value = imgui.InputInt(id, value, 1)
  imgui.PopItemWidth()
  
  return value
end

function RenderXYParameter(label, id, value)
  imgui.AlignTextToFramePadding()
  imgui.Text(label)
  imgui.SameLine(150)
  imgui.Text("X")
  imgui.SameLine(163)
  imgui.PushItemWidth(50)
  value.x = imgui.InputInt(id .. "X", value.x, 0)
  imgui.SameLine(230)
  imgui.Text("Y")
  imgui.SameLine(243)
  value.y = imgui.InputInt(id .. "Y", value.y, 0)
  imgui.PopItemWidth()
  
  return value
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
    spriteSheetScale = math.max(spriteSheetScale + y, 1)
    imgui.WheelMoved(y)
    if not imgui.GetWantCaptureMouse() then
        -- Pass event to the game
    end
end
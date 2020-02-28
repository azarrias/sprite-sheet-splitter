SlicerGUI = Class{}

function SlicerGUI:init(def)
  self.image = love.graphics.newImage('graphics/character.png') 
  self.canvas = love.graphics.newCanvas(self.image:getWidth(), self.image:getHeight())
end

function SlicerGUI:update(dt)
  imgui.NewFrame()
end

function SlicerGUI:DrawImageToCanvas()
  love.graphics.setCanvas(self.canvas)
  love.graphics.setBlendMode('alpha', 'alphamultiply')
  love.graphics.clear(canvasBackgroundColor)
  love.graphics.draw(self.image, 0, 0)
  
  love.graphics.setColor(sliceLineColor)
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
  love.graphics.setColor(themePrimaryColor)
  
  love.graphics.setCanvas()
end

function SlicerGUI:DrawQuadsToCanvas(texture, quads, x, y)
  
end

function SlicerGUI:DrawDockspace()
  if imgui.Begin("DockArea", nil, { "ImGuiWindowFlags_NoTitleBar", "NoResize", "NoMove", "NoBringToFrontOnFocus" }) then
    imgui.BeginDockspace()
    
    self:DrawEditDock()
    self:DrawSpritesheetDock()
  end

  imgui.End()
  
  if debugMode then
    self:RenderFixedOverlay(Vector2D(WINDOW_WIDTH - 230, WINDOW_HEIGHT - 70))
  end
end

function SlicerGUI:DrawEditDock()
  imgui.SetNextDock("Right")
  imgui.SetNextDockSplitRatio(0.7, 0.7)
  imgui.BeginDock("Edit")
  local x, y = imgui.CalcTextSize("Slicing parameters")
  imgui.Indent(293 / 2 - x / 2)
  imgui.Text("Slicing parameters")
  imgui.Unindent(293 / 2 - x / 2)
  
  nrOfRows = self:RenderIntParameter("Number of rows", "##nrOfRows", nrOfRows)
  nrOfColumns = self:RenderIntParameter("Number of columns", "##nrOfColumns", nrOfColumns)
  spriteSize = self:RenderXYParameter("Pixels per sprite", "##spriteSize", spriteSize)
  offset = self:RenderXYParameter("Offset", "##offset", offset)
  padding = self:RenderXYParameter("Padding", "##padding", padding)
  
  imgui.Dummy(0, 10)
  local buttonSize = Vector2D(50, 20)
  imgui.Indent(293 / 2 - buttonSize.x / 2)
  if imgui.Button("Slice", buttonSize.x, buttonSize.y) then
    imgui.Text("Test button")
  end

  imgui.EndDock()
end

function SlicerGUI:DrawSpritesheetDock()
  --[[
  Broken docks on master: BeginDock doesn't return a boolean
  https://github.com/slages/love-imgui/issues/28
  
  if imgui.BeginDock("Edit") then
     ...  
  end
  ]]
  imgui.SetNextDock("Left")
  imgui.BeginDock("Sprite sheet")
  spritePos = Vector2D(0, 0)
  spritePos.x, spritePos.y = imgui.GetCursorScreenPos()
  imgui.Image(self.canvas, self.image:getWidth() * spriteSheetScale, self.image:getHeight() * spriteSheetScale)
  imgui.EndDock()
 
  imgui.EndDockspace()
end

function SlicerGUI:RenderIntParameter(label, id, value)
  imgui.AlignTextToFramePadding()
  imgui.Text(label)
  imgui.SameLine(150)
  imgui.PushItemWidth(142)
  value = imgui.InputInt(id, value, 1)
  imgui.PopItemWidth()
  
  return value
end

function SlicerGUI:RenderXYParameter(label, id, value)
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

function SlicerGUI:RenderFixedOverlay(pos)
  imgui.SetNextWindowPos(pos.x, pos.y)
  imgui.SetNextWindowSize(220, 60)
  if imgui.Begin("Fixed Overlay", nil, { "ImGuiWindowFlags_NoTitleBar", "ImGuiWindowFlags_NoResize", "ImGuiWindowFlags_NoMove", "ImGuiWindowFlags_NoSavedSettings" }) then
    imgui.Text("Debug info:");
    local x, y = imgui.GetMousePos()
    x = math.min(math.max(-1, x), WINDOW_WIDTH)
    y = math.min(math.max(-1, y), WINDOW_HEIGHT)
    imgui.Text("Mouse Position: (" .. tostring(x) .. ", " .. tostring(y) .. ")")
  end
  imgui.End();
end

function SlicerGUI:render()
  self:DrawImageToCanvas()
  
  imgui.SetNextWindowPos(0, 0)
  imgui.SetNextWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
  
  self:DrawDockspace()
  
  love.graphics.clear(backgroundTint)
  imgui.Render()
end
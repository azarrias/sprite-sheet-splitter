SlicerGUI = Class{}

function SlicerGUI:init(def)
  self.editMode = true
  self.editDockColor = { 1, 1, 1, 1 }
  self.image = self:OpenImage()
  --self.image = love.graphics.newImage('graphics/character.png') 
  if self.image then
    self.canvas = love.graphics.newCanvas(self.image:getWidth(), self.image:getHeight())
  end
  self.animationCanvas = nil
  self.quads = nil
  self.spriteSheetPos = Vector2D(0, 0)
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

function SlicerGUI:DrawQuadsToCanvas()
  love.graphics.setCanvas(self.canvas)
  love.graphics.setBlendMode('alpha', 'alphamultiply')
  love.graphics.clear(canvasBackgroundColor)
  love.graphics.setLineStyle('rough')
  for y = 1, nrOfRows do
    for x = 1, nrOfColumns do
      -- draw quads
      love.graphics.setColor(themePrimaryColor)
      love.graphics.draw(self.image, 
        self.quads[(y - 1) * nrOfColumns + x],
        (x - 1) * (spriteSize.x + padding.x) + offset.x,
        (y - 1) * (spriteSize.y + padding.y) + offset.y)
      
      -- draw lines
      love.graphics.setColor(sliceLineColor)
      love.graphics.rectangle('line', 
        (x - 1) * (spriteSize.x + padding.x) + offset.x + 1, 
        (y - 1) * (spriteSize.y + padding.y) + offset.y + 1, 
        spriteSize.x - 1, 
        spriteSize.y - 1)
      
      -- draw numbers
      love.graphics.setColor(numbersColor)
      love.graphics.printf((y - 1) * nrOfColumns + x, 
        (x - 1) * (spriteSize.x + padding.x) + offset.x + 2,
        (y - 1) * (spriteSize.y + padding.y) + offset.y,
        WINDOW_WIDTH,
        'left')
    end
  end
  love.graphics.setColor(themePrimaryColor)
  
  love.graphics.setCanvas()  
end

function SlicerGUI:DrawAnimationToCanvas()
  love.graphics.setCanvas(self.animationCanvas)
  love.graphics.setBlendMode('alpha', 'alphamultiply')
  love.graphics.clear(canvasBackgroundColor)
  appStateMachine.current.animation:draw(
    self.image,
    0,
    0
  )

  love.graphics.setColor(themePrimaryColor)
  
  love.graphics.setCanvas()
end

function SlicerGUI:DrawWindow()
  imgui.SetNextWindowPos(0, 0)
  imgui.SetNextWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
  
  self:DrawDockspace()
  
  love.graphics.clear(backgroundTint)
  imgui.Render()
end

function SlicerGUI:DrawDockspace()
  if imgui.Begin("DockArea", nil, { "ImGuiWindowFlags_NoTitleBar", "NoResize", "NoMove", "NoBringToFrontOnFocus" }) then
    imgui.BeginDockspace()
    
    -- SetNextDock is broken on the library port
    -- but this layout is ok
    imgui.SetNextDock("Right")
    imgui.SetNextDockSplitRatio(0.25, 0.25)
    self:DrawSpritesheetDock()
    imgui.SetNextDock("Left")
    self:DrawEditDock()
    imgui.SetNextDock("None")
    self:DrawAnimationDock()
    
    imgui.EndDockspace()
  end

  imgui.End()
  
  if debugMode then
    self:RenderFixedOverlay(Vector2D(WINDOW_WIDTH - 230, WINDOW_HEIGHT - 70))
  end
end

function SlicerGUI:DrawEditDock()
  imgui.BeginDock("Edit")
  local x, y = imgui.CalcTextSize("Slicing parameters")
  imgui.PushStyleColor(ImGuiCol_Text, unpack(self.editDockColor))
  imgui.Indent(293 / 2 - x / 2)
  imgui.Text("Slicing parameters")
  imgui.Unindent(293 / 2 - x / 2)
  
  if self.editMode then
    nrOfRows = self:RenderIntParameter("Number of rows", "##nrOfRows", nrOfRows)
    nrOfColumns = self:RenderIntParameter("Number of columns", "##nrOfColumns", nrOfColumns)
    spriteSize = self:RenderXYParameter("Pixels per sprite", "##spriteSize", spriteSize)
    offset = self:RenderXYParameter("Offset", "##offset", offset)
    padding = self:RenderXYParameter("Padding", "##padding", padding)
  else
    self:RenderIntParameter("Number of rows", "##nrOfRows", nrOfRows)
    self:RenderIntParameter("Number of columns", "##nrOfColumns", nrOfColumns)
    self:RenderXYParameter("Pixels per sprite", "##spriteSize", spriteSize)
    self:RenderXYParameter("Offset", "##offset", offset)
    self:RenderXYParameter("Padding", "##padding", padding)
  end
  
  imgui.Dummy(0, 10)
  local buttonSize = Vector2D(50, 20)
  imgui.Indent(293 / 2 - buttonSize.x - 10)
  if imgui.Button("Slice", buttonSize.x, buttonSize.y) then
    appStateMachine.current:ClickSlice()
  end
  imgui.Unindent(293 / 2 - buttonSize.x - 10)
  
  imgui.PopStyleColor()
  
  imgui.SameLine(293 / 2 + 10)
  if imgui.Button("Cancel", buttonSize.x, buttonSize.y) then
    appStateMachine.current:ClickCancel()
  end
  
  if not self.editMode then
    imgui.Dummy(0, 15)
    local x, y = imgui.CalcTextSize("Animation properties")
    imgui.Indent(293 / 2 - x / 2)
    imgui.Text("Animation properties")
    imgui.Unindent(293 / 2 - x / 2)
    
    local status
    appStateMachine.current.animationInterval, status = self:RenderFloatParameter(
      "Interval", "##animationInterval", appStateMachine.current.animationInterval)
    
    if status then
      appStateMachine.current:rebuildAnimation()
    end
    
    local frameIds = "Frame IDs: "
    if not appStateMachine.current.animationFrames:isEmpty() then
      for k, frame in appStateMachine.current.animationFrames:iterator() do
        frameIds = frameIds .. frame .. ", " 
      end
      imgui.Text(frameIds:sub(1, -3))
    else
      imgui.Text(frameIds)
    end    
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
  imgui.BeginDock("Sprite sheet")
  self.spriteSheetPos.x, self.spriteSheetPos.y = imgui.GetCursorScreenPos()
  imgui.Image(self.canvas, self.image:getWidth() * spriteSheetScale, self.image:getHeight() * spriteSheetScale)
  imgui.EndDock()
end

function SlicerGUI:DrawAnimationDock()
  imgui.BeginDock("Preview animation")
  if appStateMachine.current.animation then
    imgui.Image(self.animationCanvas, spriteSize.x * spriteSheetScale, spriteSize.y * spriteSheetScale)
  end
  imgui.EndDock()
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

function SlicerGUI:RenderFloatParameter(label, id, value)
  local status
  imgui.AlignTextToFramePadding()
  imgui.Text(label)
  imgui.SameLine(150)
  imgui.PushItemWidth(142)
  value, status = imgui.InputFloat(id, value)
  imgui.PopItemWidth()
  
  return value, status
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

function SlicerGUI:OpenImage()
  -- Use nativefiledialog library to open image file (only LOVE2D supported formats)
  local filePath = nfd.open("png,tga")
  -- Quit if user pressed Cancel on the file dialog
  if not filePath then
    love.event.quit()
  -- Reopen file dialog if the file extension is not supported
  elseif filePath:sub(-3):lower() ~= "png" and filePath:sub(-3):lower() ~= "tga" then
    return self:OpenImage()
  else
    local file = io.open(filePath, "rb")
    local fileString = file:read("*a")
    local fileData = love.filesystem.newFileData(fileString, filePath:gsub(".-([^\\/]-[^%.]+)$", ""))
    return love.graphics.newImage(fileData)
  end
end
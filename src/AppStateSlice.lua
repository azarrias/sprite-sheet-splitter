AppStateSlice = Class{__includes = BaseState}

function AppStateSlice:enter()
  gui.editMode = false
  gui.quads = GenerateQuads(gui.image, nrOfRows, nrOfColumns, spriteSize, offset, padding)
  gui.animationCanvas = love.graphics.newCanvas(spriteSize.x, spriteSize.y)
  self.animationFrames = Deque()
  self.animationInterval = 0.5
  self.animation = nil
end

function AppStateSlice:update(dt)
  -- check for double clicks within the sliced quads coordinates
  if not love.mouse.doubleClicks:isEmpty() then
    for k, dc in love.mouse.doubleClicks:iterator() do
      for y = 1, nrOfRows do
        for x = 1, nrOfColumns do
          local left = gui.spriteSheetPos.x + ((x - 1) * (spriteSize.x + padding.x) + offset.x) * spriteSheetScale
          local right = left + spriteSize.x * spriteSheetScale
          local top = gui.spriteSheetPos.y + ((y - 1) * (spriteSize.y + padding.y) + offset.y) * spriteSheetScale
          local bottom = top + spriteSize.y * spriteSheetScale
          
          if dc.x >= left and dc.x <= right and dc.y >= top and dc.y <= bottom then
            local id = (y - 1) * nrOfColumns + x
            self.animationFrames:push_back(id)
            
            self:rebuildAnimation()
          end
        end
      end
    end
  end
  
  gui:update(dt)
  if self.animation then
    self.animation:update(dt)
  end
end

function AppStateSlice:render()
  gui:DrawQuadsToCanvas()
  if self.animation then
    gui:DrawAnimationToCanvas()
  end
  gui:DrawWindow()
end

function AppStateSlice:ClickSlice()
  -- do nothing
end

function AppStateSlice:ClickCancel()
  gui.editDockColor = { 1, 1, 1, 1 }
  self.animationFrames:clear()
  self.animation = nil
  appStateMachine:change('start')
end

function AppStateSlice:rebuildAnimation()
  local quads = {}
  for k, frame in self.animationFrames:iterator() do
    table.insert(quads, gui.quads[frame])
  end
  
  self.animation = Animation {
    frames = quads,
    interval = self.animationInterval
  }
end

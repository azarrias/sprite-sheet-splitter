AppStateSlice = Class{__includes = BaseState}

function AppStateSlice:enter()
  gui.editMode = false
  gui.quads = GenerateQuads(gui.image, nrOfRows, nrOfColumns, spriteSize, padding, offset)
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
            gui.animationFrames:push_back(id)
          end
        end
      end
    end
  end
  
  gui:update(dt)
end

function AppStateSlice:render()
  gui:DrawQuadsToCanvas()
  gui:DrawWindow()
end

function AppStateSlice:ClickSlice()
  -- do nothing
end

function AppStateSlice:ClickCancel()
  gui.editDockColor = { 1, 1, 1, 1 }
  appStateMachine:change('start')
end
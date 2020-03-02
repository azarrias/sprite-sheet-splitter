AppStateSlice = Class{__includes = BaseState}

function AppStateSlice:enter()
  gui.editMode = false
  gui.quads = GenerateQuads(gui.image, nrOfRows, nrOfColumns, spriteSize, padding, offset)
end

function AppStateSlice:update(dt)
  if not love.mouse.doubleClicks:isEmpty() then
    for k, dc in love.mouse.doubleClicks:iterator() do
      print(dc)
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
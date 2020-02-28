AppStateSlice = Class{__includes = BaseState}

function AppStateSlice:update(dt)
  gui:update(dt)
end

function AppStateSlice:enter()
  gui.editMode = false
  gui.quads = GenerateQuads(gui.image, nrOfRows, nrOfColumns, spriteSize, padding, offset)
end

function AppStateSlice:render()
  gui:DrawQuadsToCanvas()
  gui:DrawWindow()
end

function AppStateSlice:ClickSlice()
  -- do nothing
end

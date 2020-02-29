AppStateStart = Class{__includes = BaseState}

function AppStateStart:enter()
  gui.editMode = true
end

function AppStateStart:update(dt)
  gui:update(dt)
end

function AppStateStart:render()
  gui:DrawImageToCanvas()
  gui:DrawWindow()
end

function AppStateStart:ClickSlice()
  gui.editDockColor = { 0.7, 0.7, 0.7, 1 }
  appStateMachine:change('slice')
end

function AppStateStart:ClickCancel()
  -- do nothing
end
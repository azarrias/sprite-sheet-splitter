AppStateStart = Class{__includes = BaseState}

function AppStateStart:update(dt)
  gui:update(dt)
end

function AppStateStart:render()
  gui:DrawImageToCanvas()
  gui:DrawWindow()
end

function AppStateStart:ClickSlice()
  appStateMachine:change('slice')
end
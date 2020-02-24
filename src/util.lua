--[[
    Given an "atlas" (a texture with multiple sprites), as well as a
    width and a height for the tiles therein, split the texture into
    all of the quads by simply dividing it evenly.
]]
function GenerateQuads(atlas, tilewidth, tileheight)
  local sheetWidth = atlas:getWidth() / tilewidth
  local sheetHeight = atlas:getHeight() / tileheight
  
  local spritesheet = {}
  
  for y = 0, sheetHeight - 1 do
    for x = 0, sheetWidth - 1 do
      table.insert(spritesheet, love.graphics.newQuad(x * tilewidth, y * tileheight,
          tilewidth, tileheight, atlas:getDimensions()))
    end
  end
  
  return spritesheet
end

--[[
    Divides quads we've generated via slicing our tile sheet into separate tile sets.
]]
function GenerateTileSets(quads, setsX, setsY, sizeX, sizeY)
    local tilesets = {}
    local tableCounter = 0
    local sheetWidth = setsX * sizeX
    local sheetHeight = setsY * sizeY

    -- for each tile set on the X and Y
    for tilesetY = 1, setsY do
        for tilesetX = 1, setsX do
            
            -- tileset table
            table.insert(tilesets, {})
            tableCounter = tableCounter + 1

            for y = sizeY * (tilesetY - 1) + 1, sizeY * (tilesetY - 1) + sizeY do
                for x = sizeX * (tilesetX - 1) + 1, sizeX * (tilesetX - 1) + sizeX do
                    table.insert(tilesets[tableCounter], quads[sheetWidth * (y - 1) + x])
                end
            end
        end
    end

    return tilesets
end

--[[
    Recursive table printing function.
    https://coronalabs.com/blog/2014/09/02/tutorial-printing-table-contents/
]]
function print_r (t)
    local print_r_cache={}
    local function sub_print_r(t,indent)
        if (print_r_cache[tostring(t)]) then
            print(indent.."*"..tostring(t))
        else
            print_r_cache[tostring(t)]=true
            if (type(t)=="table") then
                for pos,val in pairs(t) do
                    if (type(val)=="table") then
                        print(indent.."["..pos.."] => "..tostring(t).." {")
                        sub_print_r(val,indent..string.rep(" ",string.len(pos)+8))
                        print(indent..string.rep(" ",string.len(pos)+6).."}")
                    elseif (type(val)=="string") then
                        print(indent.."["..pos..'] => "'..val..'"')
                    else
                        print(indent.."["..pos.."] => "..tostring(val))
                    end
                end
            else
                print(indent..tostring(t))
            end
        end
    end
    if (type(t)=="table") then
        print(tostring(t).." {")
        sub_print_r(t,"  ")
        print("}")
    else
        sub_print_r(t,"  ")
    end
    print()
end

--[[
    Given a table of formatted text tables, render them vertically and horizontally centered
    The keys in the formatted text tables are:
    font - DEFAULT: love.graphics.getFont()
    textColor - DEFAULT: {1, 1, 1, 1}
    shadow - DEFAULT: false
    string
  ]]
function RenderCenteredText(formattedText)
  local accumulated_height = 0
  
  -- calculate the accumulated height and populate the formatted text table with defaults if needed
  for k, line in pairs(formattedText) do
    line.font = line.font ~= nil and line.font or love.graphics.getFont()
    line.shadow = line.shadow ~= nil and line.shadow or false
    line.accumulated_height = accumulated_height
    accumulated_height = accumulated_height + line.font:getHeight()
    line.textColor = line.textColor or { 1, 1, 1, 1 }
  end
  
  local padding = math.floor((VIRTUAL_HEIGHT - accumulated_height) / 2)
  
  for k, line in pairs(formattedText) do
    love.graphics.setFont(line.font)
    if line.shadow then
      love.graphics.setColor({ 0, 0, 0, 1 })
      love.graphics.printf(line.string, 1, padding + line.accumulated_height + 1,
        VIRTUAL_WIDTH, 'center')
    end
    love.graphics.setColor(line.textColor)
    love.graphics.printf(line.string, 0, padding + line.accumulated_height,
      VIRTUAL_WIDTH, 'center')
  end
end
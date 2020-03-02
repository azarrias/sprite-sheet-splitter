Vector2D = Class{}

function Vector2D:init(x, y)
  self.x = x
  self.y = y
end

function Vector2D:__add(other)
  if type(other) == 'table' and other.x ~= nil and other.y ~= nil then
    return Vector2D(self.x + other.x, self.y + other.y)
  else
    error "Vector2D can only be added to another Vector2D"
  end
end

function Vector2D:__sub(other)
  if type(other) == 'table' and other.x ~= nil and other.y ~= nil then
    return Vector2D(self.x - other.x, self.y - other.y)
  else
    error "Vector2D can only be subtracted from another Vector2D"
  end
end

function Vector2D:__mul(other)
  if tonumber(other) then
    return Vector2D(self.x * other, self.y * other)
  else
    error "Vector2D can only be multiplied by a number"
  end
end

function Vector2D:__div(other)
  if tonumber(other) then
    return Vector2D(self.x / other, self.y / other)
  else
    error "Vector2D can only be divided by a number"
  end
end

function Vector2D:__eq(other)
  if type(other) == 'table' and other.x ~= nil and other.y ~= nil then
    return self.x == other.x and self.y == other.y
  else
    error "Vector2D can only be compared to another Vector2D"
  end
end

function Vector2D:__tostring()
  return "(" .. self.x .. ", " .. self.y .. ")"
end
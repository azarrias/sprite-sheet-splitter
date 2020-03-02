Deque = Class{}

function Deque:init()
  self.front = 0
  self.back = -1
  self.items = {}
  self.counter = 0
end

function Deque:clear()
  self:init()
end

function Deque:isEmpty()
  return self.counter == 0
end

function Deque:length()
  return self.counter
end

function Deque:iterator()
  local k = self.front - 1
  local n = self.back
  return function()
    k = k + 1
    if k <= n then 
      return k, self.items[k]
    end
  end
end  

function Deque:push_front(value)
  local front = self.front - 1
  self.front = front
  self.items[front] = value
  self.counter = self.counter + 1
end
  
function Deque:push_back(value)
  local back = self.back + 1
  self.back = back
  self.items[back] = value
  self.counter = self.counter + 1
end

function Deque:pop_front()
  local front = self.front
  if front > self.back then error("list is empty") end
  local value = self.items[front]
  self.items[front] = nil        -- allow garbage collection
  self.front = front + 1
  self.counter = self.counter - 1
  return value
end
  
function Deque:pop_back()
  local back = self.back
  if self.front > back then error("list is empty") end
  local value = self.items[back]
  self.items[back] = nil         -- allow garbage collection
  self.back = back - 1
  self.counter = self.counter - 1
  return value
end

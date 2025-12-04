-- Modal App Launcher Snippet
-- Copy-paste this into your init.lua

-- Create modal object
local appLauncher = hs.hotkey.modal.new()

-- Define your apps (customize this table!)
local apps = {
  c = "Google Chrome",
  f = "Finder",
  t = "iTerm",
  s = "Slack",
  v = "Visual Studio Code",
  m = "Mail",
  n = "Notes",
  p = "Spotify"
}

-- Automatically bind all apps
for key, appName in pairs(apps) do
  appLauncher:bind("", key, function()
    hs.application.launchOrFocus(appName)
    appLauncher:exit()
  end)
end

-- Exit on Escape
appLauncher:bind("", "escape", function()
  appLauncher:exit()
end)

-- Visual feedback when entering
function appLauncher:entered()
  hs.alert.show("App Launcher", {textColor = {hex="#00FF00"}})
end

-- Visual feedback when exiting
function appLauncher:exited()
  hs.alert.show("Exited", {textColor = {hex="#FF0000"}})
end

-- Activate with Alt+Space
hs.hotkey.bind({"alt"}, "space", function()
  appLauncher:enter()
end)

-- ========================================
-- VARIANT: Window Management Modal
-- ========================================

-- Create modal for window operations
local winModal = hs.hotkey.modal.new()

-- Vim-like keys for window positioning
winModal:bind("", "h", function()  -- Left
  local win = hs.window.focusedWindow()
  if win then
    local frame = win:screen():frame()
    win:setFrame({x = frame.x, y = frame.y, w = frame.w / 2, h = frame.h})
  end
  winModal:exit()
end)

winModal:bind("", "l", function()  -- Right
  local win = hs.window.focusedWindow()
  if win then
    local frame = win:screen():frame()
    win:setFrame({x = frame.x + frame.w / 2, y = frame.y, w = frame.w / 2, h = frame.h})
  end
  winModal:exit()
end)

winModal:bind("", "k", function()  -- Up
  local win = hs.window.focusedWindow()
  if win then
    local frame = win:screen():frame()
    win:setFrame({x = frame.x, y = frame.y, w = frame.w, h = frame.h / 2})
  end
  winModal:exit()
end)

winModal:bind("", "j", function()  -- Down
  local win = hs.window.focusedWindow()
  if win then
    local frame = win:screen():frame()
    win:setFrame({x = frame.x, y = frame.y + frame.h / 2, w = frame.w, h = frame.h / 2})
  end
  winModal:exit()
end)

winModal:bind("", "f", function()  -- Fullscreen
  local win = hs.window.focusedWindow()
  if win then win:setFrame(win:screen():frame()) end
  winModal:exit()
end)

winModal:bind("", "c", function()  -- Center
  local win = hs.window.focusedWindow()
  if win then
    local screen = win:screen():frame()
    local winFrame = win:frame()
    winFrame.x = screen.x + (screen.w - winFrame.w) / 2
    winFrame.y = screen.y + (screen.h - winFrame.h) / 2
    win:setFrame(winFrame)
  end
  winModal:exit()
end)

winModal:bind("", "escape", function()
  winModal:exit()
end)

function winModal:entered()
  hs.alert.show("Window Mode")
end

-- Activate with Alt+W
hs.hotkey.bind({"alt"}, "w", function()
  winModal:enter()
end)

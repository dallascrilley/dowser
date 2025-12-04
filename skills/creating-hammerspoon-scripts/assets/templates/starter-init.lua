-- Hammerspoon Starter Configuration
-- A complete, production-ready init.lua with essential automation patterns
--
-- Features:
-- - Config reload hotkey and auto-reload
-- - Window management (halves, quarters, maximize)
-- - Modal app launcher
-- - Multi-monitor support
--
-- To use: Copy to ~/.hammerspoon/init.lua and reload Hammerspoon

-- ========================================
-- 1. ESSENTIAL: CONFIG RELOAD
-- ========================================

-- Manual reload with hotkey
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "R", function()
  hs.reload()
end)

-- Auto-reload when any .lua file changes
function reloadConfig(files)
  local doReload = false
  for _, file in pairs(files) do
    if file:sub(-4) == ".lua" then
      doReload = true
    end
  end
  if doReload then
    hs.reload()
  end
end

-- MUST be global variable (no 'local')!
configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()

-- Show confirmation that config loaded
hs.alert.show("Hammerspoon config loaded")

-- ========================================
-- 2. WINDOW MANAGEMENT
-- ========================================

-- Move window to left half of screen
function moveWindowLeftHalf()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame({
    x = frame.x,
    y = frame.y,
    w = frame.w / 2,
    h = frame.h
  })
end

-- Move window to right half of screen
function moveWindowRightHalf()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame({
    x = frame.x + (frame.w / 2),
    y = frame.y,
    w = frame.w / 2,
    h = frame.h
  })
end

-- Move window to top half of screen
function moveWindowTopHalf()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame({
    x = frame.x,
    y = frame.y,
    w = frame.w,
    h = frame.h / 2
  })
end

-- Move window to bottom half of screen
function moveWindowBottomHalf()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame({
    x = frame.x,
    y = frame.y + (frame.h / 2),
    w = frame.w,
    h = frame.h / 2
  })
end

-- Maximize window to fill screen
function maximizeWindow()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame(frame)
end

-- Move window to next screen (multi-monitor)
function moveWindowToNextScreen()
  local win = hs.window.focusedWindow()
  if not win then return end

  local nextScreen = win:screen():next()
  win:moveToScreen(nextScreen)
end

-- Bind window management hotkeys (Cmd+Alt+Arrow)
hs.hotkey.bind({"cmd", "alt"}, "Left", moveWindowLeftHalf)
hs.hotkey.bind({"cmd", "alt"}, "Right", moveWindowRightHalf)
hs.hotkey.bind({"cmd", "alt"}, "Up", moveWindowTopHalf)
hs.hotkey.bind({"cmd", "alt"}, "Down", moveWindowBottomHalf)
hs.hotkey.bind({"cmd", "alt"}, "M", maximizeWindow)
hs.hotkey.bind({"cmd", "alt"}, "N", moveWindowToNextScreen)

-- ========================================
-- 3. MODAL APP LAUNCHER
-- ========================================

-- Create modal object
local appLauncher = hs.hotkey.modal.new()

-- Table of applications (customize this for your apps!)
local apps = {
  c = "Google Chrome",    -- Press 'c' for Chrome
  f = "Finder",          -- Press 'f' for Finder
  t = "iTerm",           -- Press 't' for iTerm
  s = "Slack",           -- Press 's' for Slack
  v = "Visual Studio Code",  -- Press 'v' for VS Code
  m = "Mail"             -- Press 'm' for Mail
}

-- Create bindings for each app
for key, appName in pairs(apps) do
  appLauncher:bind("", key, function()
    hs.application.launchOrFocus(appName)
    appLauncher:exit()
  end)
end

-- Exit modal on Escape
appLauncher:bind("", "escape", function()
  appLauncher:exit()
end)

-- Visual feedback when entering modal
function appLauncher:entered()
  hs.alert.show("App Launcher Mode", {textColor = {hex="#00FF00"}})
end

-- Visual feedback when exiting modal
function appLauncher:exited()
  hs.alert.show("Exited", {textColor = {hex="#FF0000"}})
end

-- Global hotkey to enter modal (Alt+Space)
hs.hotkey.bind({"alt"}, "space", function()
  appLauncher:enter()
end)

-- ========================================
-- 4. ADDITIONAL HOTKEYS (Optional)
-- ========================================

-- Toggle Hammerspoon console (for debugging)
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "C", function()
  hs.toggleConsole()
end)

-- ========================================
-- CUSTOMIZATION NOTES
-- ========================================

-- To customize this config:
--
-- 1. Change window management hotkeys:
--    Modify the hs.hotkey.bind() calls in section 2
--
-- 2. Add more apps to launcher:
--    Add entries to the 'apps' table in section 3
--    Format: key = "Application Name"
--
-- 3. Change modal activation key:
--    Modify the hotkey in the last hs.hotkey.bind() call
--    Currently: Alt+Space
--
-- 4. Add your own hotkeys:
--    hs.hotkey.bind({"cmd", "alt"}, "H", function()
--      hs.alert.show("My custom action!")
--    end)
--
-- 5. Add watchers for system events:
--    See references/common_patterns.md for WiFi, app, USB watchers
--
-- Remember:
-- - All watchers MUST use global variables (no 'local')
-- - Always check for nil windows before using them
-- - Reload config after changes (Cmd+Alt+Ctrl+R)

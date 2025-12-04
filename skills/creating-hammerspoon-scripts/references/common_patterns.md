# Common Hammerspoon Patterns

Complete, tested patterns for the most common Hammerspoon use cases. Copy-paste ready with explanatory comments.

---

## Window Management Patterns

### Pattern: Window to Left Half

```lua
function moveWindowLeftHalf()
  local win = hs.window.focusedWindow()
  if not win then return end  -- Guard against nil

  local screen = win:screen()
  local frame = screen:frame()  -- Usable area (excludes menubar/dock)

  win:setFrame({
    x = frame.x,
    y = frame.y,
    w = frame.w / 2,
    h = frame.h
  })
end

hs.hotkey.bind({"cmd", "alt"}, "Left", moveWindowLeftHalf)
```

### Pattern: Window to Right Half

```lua
function moveWindowRightHalf()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame({
    x = frame.x + (frame.w / 2),  -- Start halfway across
    y = frame.y,
    w = frame.w / 2,
    h = frame.h
  })
end

hs.hotkey.bind({"cmd", "alt"}, "Right", moveWindowRightHalf)
```

### Pattern: Window to Top Half

```lua
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

hs.hotkey.bind({"cmd", "alt"}, "Up", moveWindowTopHalf)
```

### Pattern: Window to Bottom Half

```lua
function moveWindowBottomHalf()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame({
    x = frame.x,
    y = frame.y + (frame.h / 2),  -- Start halfway down
    w = frame.w,
    h = frame.h / 2
  })
end

hs.hotkey.bind({"cmd", "alt"}, "Down", moveWindowBottomHalf)
```

### Pattern: Window Quarters (4 positions)

```lua
function moveWindowQuarter(position)
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()
  local halfW = frame.w / 2
  local halfH = frame.h / 2

  local positions = {
    topLeft = {x = frame.x, y = frame.y, w = halfW, h = halfH},
    topRight = {x = frame.x + halfW, y = frame.y, w = halfW, h = halfH},
    bottomLeft = {x = frame.x, y = frame.y + halfH, w = halfW, h = halfH},
    bottomRight = {x = frame.x + halfW, y = frame.y + halfH, w = halfW, h = halfH}
  }

  win:setFrame(positions[position])
end

-- Bind to number keys
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "1", function() moveWindowQuarter("topLeft") end)
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "2", function() moveWindowQuarter("topRight") end)
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "3", function() moveWindowQuarter("bottomLeft") end)
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "4", function() moveWindowQuarter("bottomRight") end)
```

### Pattern: Maximize Window

```lua
function maximizeWindow()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame(frame)
end

hs.hotkey.bind({"cmd", "alt"}, "M", maximizeWindow)
```

### Pattern: Center Window

```lua
function centerWindow()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()
  local winFrame = win:frame()

  -- Calculate center position
  winFrame.x = frame.x + (frame.w - winFrame.w) / 2
  winFrame.y = frame.y + (frame.h - winFrame.h) / 2

  win:setFrame(winFrame)
end

hs.hotkey.bind({"cmd", "alt"}, "C", centerWindow)
```

### Pattern: Move Window to Next Screen

```lua
function moveWindowToNextScreen()
  local win = hs.window.focusedWindow()
  if not win then return end

  local nextScreen = win:screen():next()
  win:moveToScreen(nextScreen)
end

hs.hotkey.bind({"cmd", "alt"}, "N", moveWindowToNextScreen)
```

### Pattern: Move and Resize (Combined)

```lua
-- Generic function for any position/size
function moveAndResize(xRatio, yRatio, wRatio, hRatio)
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame({
    x = frame.x + (frame.w * xRatio),
    y = frame.y + (frame.h * yRatio),
    w = frame.w * wRatio,
    h = frame.h * hRatio
  })
end

-- Left 2/3
hs.hotkey.bind({"cmd", "alt", "shift"}, "Left", function()
  moveAndResize(0, 0, 0.67, 1)
end)

-- Right 1/3
hs.hotkey.bind({"cmd", "alt", "shift"}, "Right", function()
  moveAndResize(0.67, 0, 0.33, 1)
end)
```

---

## Hotkey Patterns

### Pattern: Simple Global Hotkey

```lua
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "H", function()
  hs.alert.show("Hello World!")
end)
```

### Pattern: Hotkey with Key Up/Down

```lua
-- Different actions for key press and release
hs.hotkey.bind({"cmd", "alt"}, "H",
  function()  -- Key pressed
    hs.alert.show("Key Down")
  end,
  function()  -- Key released
    hs.alert.show("Key Up")
  end
)
```

### Pattern: Repeating Hotkey

```lua
-- Trigger repeatedly while held
hs.hotkey.bind({"cmd", "alt"}, "H",
  function()  -- Pressed
    hs.alert.show("Pressed")
  end,
  function()  -- Released
    -- Optional release handler
  end,
  function()  -- Repeated while held
    hs.alert.show("Repeating")
  end
)
```

---

## Modal Hotkey Patterns

### Pattern: Basic Modal

```lua
local modal = hs.hotkey.modal.new()

-- Actions within modal
modal:bind("", "h", function()
  hs.alert.show("H pressed")
  modal:exit()
end)

modal:bind("", "j", function()
  hs.alert.show("J pressed")
  modal:exit()
end)

-- Always include escape
modal:bind("", "escape", function()
  modal:exit()
end)

-- Global hotkey to enter
hs.hotkey.bind({"alt"}, "m", function()
  modal:enter()
end)
```

### Pattern: Modal with Entry/Exit Callbacks

```lua
local modal = hs.hotkey.modal.new()

function modal:entered()
  hs.alert.show("Modal Active", {textColor = {hex="#00FF00"}})
end

function modal:exited()
  hs.alert.show("Modal Exited", {textColor = {hex="#FF0000"}})
end

modal:bind("", "a", function()
  print("Action A")
  modal:exit()
end)

modal:bind("", "escape", function()
  modal:exit()
end)

hs.hotkey.bind({"alt"}, "m", function()
  modal:enter()
end)
```

### Pattern: App Launcher Modal

```lua
local appLauncher = hs.hotkey.modal.new()

-- Table of apps
local apps = {
  c = "Google Chrome",
  f = "Finder",
  t = "iTerm",
  s = "Slack",
  v = "Visual Studio Code",
  m = "Mail"
}

-- Create bindings automatically
for key, appName in pairs(apps) do
  appLauncher:bind("", key, function()
    hs.application.launchOrFocus(appName)
    appLauncher:exit()
  end)
end

-- Exit on escape
appLauncher:bind("", "escape", function()
  appLauncher:exit()
end)

-- Entry visual feedback
function appLauncher:entered()
  hs.alert.show("App Launcher", {strokeColor = {hex="#00FF00"}})
end

-- Global hotkey to activate
hs.hotkey.bind({"alt"}, "space", function()
  appLauncher:enter()
end)
```

### Pattern: Window Management Modal

```lua
local winModal = hs.hotkey.modal.new()

-- Vim-like keys for window positioning
winModal:bind("", "h", function()  -- Left
  moveWindowLeftHalf()
  winModal:exit()
end)

winModal:bind("", "l", function()  -- Right
  moveWindowRightHalf()
  winModal:exit()
end)

winModal:bind("", "k", function()  -- Up
  moveWindowTopHalf()
  winModal:exit()
end)

winModal:bind("", "j", function()  -- Down
  moveWindowBottomHalf()
  winModal:exit()
end)

winModal:bind("", "f", function()  -- Fullscreen
  maximizeWindow()
  winModal:exit()
end)

winModal:bind("", "c", function()  -- Center
  centerWindow()
  winModal:exit()
end)

winModal:bind("", "n", function()  -- Next screen
  moveWindowToNextScreen()
  winModal:exit()
end)

winModal:bind("", "escape", function()
  winModal:exit()
end)

function winModal:entered()
  hs.alert.show("Window Mode")
end

hs.hotkey.bind({"alt"}, "w", function()
  winModal:enter()
end)
```

---

## Watcher Patterns

**CRITICAL: All watchers MUST use global variables!**

### Pattern: Auto-Reload Configuration

```lua
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

-- MUST be global (no 'local')
configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
hs.alert.show("Config loaded")
```

### Pattern: WiFi Network Change Detection

```lua
lastSSID = hs.wifi.currentNetwork()
homeSSID = "MyHomeNetwork"

function wifiChanged()
  local newSSID = hs.wifi.currentNetwork()

  if newSSID == homeSSID and lastSSID ~= homeSSID then
    -- Arrived home
    hs.notify.new({title="WiFi", informativeText="Connected to home network"}):send()
    -- Perform home-specific actions (e.g., set volume, start apps)
  elseif newSSID ~= homeSSID and lastSSID == homeSSID then
    -- Left home
    hs.notify.new({title="WiFi", informativeText="Left home network"}):send()
    -- Perform away-from-home actions (e.g., mute volume)
  end

  lastSSID = newSSID
end

-- MUST be global
wifiWatcher = hs.wifi.watcher.new(wifiChanged):start()
```

### Pattern: Application Event Handling

```lua
function appWatcherCallback(appName, eventType, appObject)
  if eventType == hs.application.watcher.activated then
    -- App was activated (focused)
    print(appName .. " activated")

    -- Example: Bring all Finder windows forward when Finder is activated
    if appName == "Finder" then
      appObject:selectMenuItem({"Window", "Bring All to Front"})
    end

  elseif eventType == hs.application.watcher.launched then
    -- App was launched
    print(appName .. " launched")

  elseif eventType == hs.application.watcher.terminated then
    -- App quit
    print(appName .. " terminated")
  end
end

-- MUST be global
appWatcher = hs.application.watcher.new(appWatcherCallback):start()
```

### Pattern: USB Device Detection

```lua
function usbCallback(data)
  if data.eventType == "added" then
    hs.alert.show("USB Added: " .. data.productName)

    -- Example: Launch app when specific device is connected
    if data.productName == "ScanSnap S1300i" then
      hs.application.launchOrFocus("ScanSnap Manager")
    end

  elseif data.eventType == "removed" then
    hs.alert.show("USB Removed: " .. data.productName)

    -- Example: Quit app when device is disconnected
    if data.productName == "ScanSnap S1300i" then
      local app = hs.application.get("ScanSnap Manager")
      if app then app:kill() end
    end
  end
end

-- MUST be global
usbWatcher = hs.usb.watcher.new(usbCallback):start()
```

---

## Menubar Patterns

### Pattern: Caffeine-Style Menubar Item

```lua
caffeine = hs.menubar.new()

function setCaffeineDisplay(state)
  if state then
    caffeine:setTitle("AWAKE")
  else
    caffeine:setTitle("SLEEPY")
  end
end

function caffeineClicked()
  local state = hs.caffeinate.toggle("displayIdle")
  setCaffeineDisplay(state)
end

if caffeine then
  caffeine:setClickCallback(caffeineClicked)
  setCaffeineDisplay(hs.caffeinate.get("displayIdle"))
end
```

### Pattern: Menubar with Icon

```lua
statusItem = hs.menubar.new()

if statusItem then
  -- Use an icon file (place in ~/.hammerspoon/)
  statusItem:setIcon("~/.hammerspoon/icon.png")

  statusItem:setClickCallback(function()
    hs.alert.show("Clicked!")
  end)
end
```

### Pattern: Menubar with Menu

```lua
menubar = hs.menubar.new()

function buildMenu()
  return {
    {title = "Option 1", fn = function() print("Option 1") end},
    {title = "Option 2", fn = function() print("Option 2") end},
    {title = "-"},  -- Separator
    {title = "Quit", fn = function() hs.reload() end}
  }
end

if menubar then
  menubar:setTitle("📋")
  menubar:setMenu(buildMenu)
end
```

---

## Utility Patterns

### Pattern: Defeat Paste Blocking

```lua
-- Some websites/apps block Cmd+V, so simulate typing instead
hs.hotkey.bind({"cmd", "alt"}, "V", function()
  local contents = hs.pasteboard.getContents()
  if contents then
    hs.eventtap.keyStrokes(contents)
  end
end)
```

### Pattern: Mouse Highlighter

```lua
mouseCircle = nil
mouseCircleTimer = nil

function highlightMouse()
  -- Delete existing highlight
  if mouseCircle then
    mouseCircle:delete()
    if mouseCircleTimer then
      mouseCircleTimer:stop()
    end
  end

  -- Get mouse position
  local mousePoint = hs.mouse.absolutePosition()

  -- Create circle
  mouseCircle = hs.drawing.circle(hs.geometry.rect(mousePoint.x - 40, mousePoint.y - 40, 80, 80))
  mouseCircle:setStrokeColor({red=1, blue=0, green=0, alpha=1})
  mouseCircle:setFill(false)
  mouseCircle:setStrokeWidth(5)
  mouseCircle:show()

  -- Auto-delete after 3 seconds
  mouseCircleTimer = hs.timer.doAfter(3, function()
    if mouseCircle then
      mouseCircle:delete()
      mouseCircle = nil
    end
  end)
end

hs.hotkey.bind({"cmd", "alt", "shift"}, "D", highlightMouse)
```

### Pattern: Quick App Switcher

```lua
-- Simple table-based approach
local quickApps = {
  c = "Google Chrome",
  t = "iTerm",
  f = "Finder",
  s = "Slack"
}

for key, appName in pairs(quickApps) do
  hs.hotkey.bind({"ctrl", "alt"}, key, function()
    hs.application.launchOrFocus(appName)
  end)
end
```

---

## Advanced Patterns

### Pattern: Cycle Through Window Positions

```lua
local positions = {"left", "right", "top", "bottom", "maximize"}
local currentIndex = 1

function cycleWindowPosition()
  local win = hs.window.focusedWindow()
  if not win then return end

  local screen = win:screen()
  local frame = screen:frame()
  local position = positions[currentIndex]

  if position == "left" then
    win:setFrame({x = frame.x, y = frame.y, w = frame.w / 2, h = frame.h})
  elseif position == "right" then
    win:setFrame({x = frame.x + frame.w / 2, y = frame.y, w = frame.w / 2, h = frame.h})
  elseif position == "top" then
    win:setFrame({x = frame.x, y = frame.y, w = frame.w, h = frame.h / 2})
  elseif position == "bottom" then
    win:setFrame({x = frame.x, y = frame.y + frame.h / 2, w = frame.w, h = frame.h / 2})
  elseif position == "maximize" then
    win:setFrame(frame)
  end

  -- Cycle to next position
  currentIndex = currentIndex + 1
  if currentIndex > #positions then
    currentIndex = 1
  end
end

hs.hotkey.bind({"cmd", "alt"}, "Tab", cycleWindowPosition)
```

### Pattern: Window Grid System

```lua
-- Use hs.grid for more sophisticated window management
hs.grid.setGrid('12x12')  -- 12 columns, 12 rows
hs.grid.setMargins({0, 0})

-- Define grid positions
local gridPositions = {
  leftHalf = {x = 0, y = 0, w = 6, h = 12},
  rightHalf = {x = 6, y = 0, w = 6, h = 12},
  topHalf = {x = 0, y = 0, w = 12, h = 6},
  bottomHalf = {x = 0, y = 6, w = 12, h = 6},
  full = {x = 0, y = 0, w = 12, h = 12}
}

function moveToGrid(position)
  local win = hs.window.focusedWindow()
  if win then
    hs.grid.set(win, gridPositions[position])
  end
end

hs.hotkey.bind({"cmd", "ctrl"}, "Left", function() moveToGrid("leftHalf") end)
hs.hotkey.bind({"cmd", "ctrl"}, "Right", function() moveToGrid("rightHalf") end)
hs.hotkey.bind({"cmd", "ctrl"}, "Up", function() moveToGrid("topHalf") end)
hs.hotkey.bind({"cmd", "ctrl"}, "Down", function() moveToGrid("bottomHalf") end)
hs.hotkey.bind({"cmd", "ctrl"}, "F", function() moveToGrid("full") end)
```

---

All patterns are production-tested and follow Hammerspoon best practices.

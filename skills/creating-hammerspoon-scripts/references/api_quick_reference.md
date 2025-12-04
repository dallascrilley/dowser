# Hammerspoon API Quick Reference

Concise reference for the 20% of APIs used 80% of the time. Organized by category with function signatures and brief descriptions.

---

## Hotkeys

### Global Hotkeys

```lua
hs.hotkey.bind(mods, key, [message], pressedfn, [releasedfn], [repeatfn])
```
Bind a hotkey to a function. `mods` is a table like `{"cmd", "alt", "ctrl"}`.

**Example:**
```lua
hs.hotkey.bind({"cmd", "alt"}, "H", function()
  hs.alert.show("Hello!")
end)
```

### Modal Hotkeys

```lua
modal = hs.hotkey.modal.new([mods, key])
```
Create a new modal hotkey environment.

```lua
modal:bind(mods, key, [message], pressedfn, [releasedfn], [repeatfn])
```
Bind a hotkey within the modal.

```lua
modal:enter()  -- Enter the modal mode
modal:exit()   -- Exit the modal mode
```

**Example:**
```lua
local modal = hs.hotkey.modal.new()
modal:bind("", "h", function() print("H pressed") modal:exit() end)
modal:bind("", "escape", function() modal:exit() end)

hs.hotkey.bind({"alt"}, "m", function() modal:enter() end)
```

---

## Windows

### Getting Windows

```lua
win = hs.window.focusedWindow()
```
Returns the currently focused window object, or `nil` if none.

```lua
wins = hs.window.allWindows()
```
Returns table of all windows.

```lua
wins = hs.window.orderedWindows()
```
Returns table of all windows ordered front-to-back.

### Window Geometry

```lua
frame = win:frame()
```
Returns table `{x, y, w, h}` with window position and size.

```lua
win:setFrame(frame)
```
Sets window position and size. `frame` is table with `x`, `y`, `w`, `h`.

```lua
win:setTopLeft(point)
```
Sets top-left corner. `point` is table with `x`, `y`.

```lua
win:setSize(size)
```
Sets size. `size` is table with `w`, `h`.

```lua
win:maximize()
```
Maximizes window to fill screen.

**Example:**
```lua
local win = hs.window.focusedWindow()
if win then
  local screen = win:screen()
  local frame = screen:frame()

  win:setFrame({
    x = frame.x,
    y = frame.y,
    w = frame.w / 2,
    h = frame.h
  })
end
```

### Window Properties

```lua
title = win:title()
```
Returns window title string.

```lua
app = win:application()
```
Returns the application object that owns this window.

```lua
screen = win:screen()
```
Returns the screen object the window is on.

```lua
isStandard = win:isStandard()
```
Returns true if window is standard (not a dialog, floating panel, etc).

### Window Actions

```lua
win:focus()
```
Focuses the window.

```lua
win:close()
```
Closes the window.

```lua
win:minimize()
```
Minimizes the window.

```lua
win:moveToScreen(screen)
```
Moves window to specified screen.

---

## Screens

```lua
screen = hs.screen.mainScreen()
```
Returns the screen with keyboard focus.

```lua
screens = hs.screen.allScreens()
```
Returns table of all screens.

```lua
frame = screen:frame()
```
Returns `{x, y, w, h}` for usable screen area (excludes menubar and dock).

```lua
fullFrame = screen:fullFrame()
```
Returns `{x, y, w, h}` for full screen area (includes menubar and dock).

```lua
nextScreen = screen:next()
```
Returns the next screen (for multi-monitor setups).

**Example:**
```lua
local win = hs.window.focusedWindow()
if win then
  local nextScreen = win:screen():next()
  win:moveToScreen(nextScreen)
end
```

---

## Applications

### Launching and Focusing

```lua
hs.application.launchOrFocus(appName)
```
Launches application if not running, otherwise focuses it.

```lua
hs.application.launchOrFocusByBundleID(bundleID)
```
Same as above but uses bundle ID (e.g., "com.apple.Safari").

**Example:**
```lua
hs.application.launchOrFocus("Safari")
hs.application.launchOrFocusByBundleID("com.google.Chrome")
```

### Getting Applications

```lua
app = hs.application.frontmostApplication()
```
Returns the application with focus.

```lua
app = hs.application.get(nameOrBundleID)
```
Returns application object by name or bundle ID, or `nil` if not running.

```lua
apps = hs.application.runningApplications()
```
Returns table of all running applications.

### Application Properties

```lua
name = app:name()
```
Returns application name.

```lua
bundleID = app:bundleID()
```
Returns bundle ID string.

```lua
wins = app:allWindows()
```
Returns table of all windows for this app.

### Application Actions

```lua
app:activate()
```
Activates (focuses) the application.

```lua
app:hide()
```
Hides the application.

```lua
app:kill()
```
Forcefully terminates the application.

```lua
success = app:selectMenuItem(menuItemPath)
```
Selects a menu item. `menuItemPath` is table like `{"File", "New Window"}`.

**Example:**
```lua
local app = hs.application.get("Safari")
if app then
  app:selectMenuItem({"Window", "Bring All to Front"})
end
```

---

## Event Watchers

**CRITICAL: All watchers MUST be stored in global variables (no `local`), otherwise they will be garbage collected!**

### Path Watcher (File Changes)

```lua
watcher = hs.pathwatcher.new(path, callback)
```
Creates watcher for file/directory changes. `callback` receives table of changed files.

```lua
watcher:start()
```
Starts the watcher.

```lua
watcher:stop()
```
Stops the watcher.

**Example (Auto-reload config):**
```lua
function reloadConfig(files)
  local doReload = false
  for _, file in pairs(files) do
    if file:sub(-4) == ".lua" then doReload = true end
  end
  if doReload then hs.reload() end
end

-- MUST be global!
configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
```

### Application Watcher

```lua
watcher = hs.application.watcher.new(callback)
```
Creates watcher for application events. `callback(appName, eventType, appObject)`.

```lua
watcher:start()
watcher:stop()
```

**Event types:**
- `hs.application.watcher.launching`
- `hs.application.watcher.launched`
- `hs.application.watcher.terminated`
- `hs.application.watcher.hidden`
- `hs.application.watcher.unhidden`
- `hs.application.watcher.activated`
- `hs.application.watcher.deactivated`

**Example:**
```lua
function appWatcherCallback(appName, eventType, appObject)
  if eventType == hs.application.watcher.activated then
    print(appName .. " activated")
  end
end

appWatcher = hs.application.watcher.new(appWatcherCallback):start()
```

### WiFi Watcher

```lua
watcher = hs.wifi.watcher.new(callback)
```
Creates watcher for WiFi events.

```lua
currentSSID = hs.wifi.currentNetwork()
```
Returns current WiFi network name.

**Example:**
```lua
lastSSID = hs.wifi.currentNetwork()

function wifiCallback()
  local newSSID = hs.wifi.currentNetwork()
  if newSSID ~= lastSSID then
    hs.alert.show("WiFi: " .. (newSSID or "Disconnected"))
    lastSSID = newSSID
  end
end

wifiWatcher = hs.wifi.watcher.new(wifiCallback):start()
```

### USB Watcher

```lua
watcher = hs.usb.watcher.new(callback)
```
Creates watcher for USB device events. `callback(data)` where `data` has:
- `eventType`: "added" or "removed"
- `productName`: Device name
- `vendorName`: Vendor name
- `productID`: Numeric product ID
- `vendorID`: Numeric vendor ID

**Example:**
```lua
function usbCallback(data)
  if data.eventType == "added" then
    hs.alert.show("USB Added: " .. data.productName)
  end
end

usbWatcher = hs.usb.watcher.new(usbCallback):start()
```

---

## UI Elements

### Alerts

```lua
hs.alert.show(message, [style], [screen], [duration])
```
Shows temporary on-screen alert. `duration` defaults to 2 seconds.

```lua
hs.alert.show("Hello World")
hs.alert.show("Error!", {textColor = {hex="#FF0000"}}, nil, 5)
```

### Notifications

```lua
notification = hs.notify.new([fn], [userInfo], [title])
```
Creates macOS notification.

```lua
notification:title(string)
notification:informativeText(string)
notification:send()
```

**Example:**
```lua
hs.notify.new(nil, nil, "Hammerspoon")
  :informativeText("Config reloaded")
  :send()
```

### Menubar Items

```lua
menubar = hs.menubar.new([inRightSide])
```
Creates menubar item.

```lua
menubar:setTitle(title)
menubar:setIcon(iconPath)
menubar:setClickCallback(fn)
```

**Example:**
```lua
caffeine = hs.menubar.new()

function caffeineClicked()
  local state = hs.caffeinate.toggle("displayIdle")
  if state then
    caffeine:setTitle("AWAKE")
  else
    caffeine:setTitle("SLEEPY")
  end
end

caffeine:setClickCallback(caffeineClicked)
caffeine:setTitle("SLEEPY")
```

---

## Utilities

### System Control

```lua
hs.reload()
```
Reloads Hammerspoon configuration.

```lua
hs.toggleConsole()
```
Opens/closes the Hammerspoon console.

### Caffeinate (Prevent Sleep)

```lua
hs.caffeinate.set(assertionType, enable)
```
Enables/disables sleep prevention. Types: "displayIdle", "systemIdle", "system".

```lua
state = hs.caffeinate.toggle(assertionType)
```
Toggles sleep prevention, returns new state.

```lua
state = hs.caffeinate.get(assertionType)
```
Returns current state.

### Pasteboard

```lua
contents = hs.pasteboard.getContents()
```
Returns clipboard contents as string.

```lua
hs.pasteboard.setContents(string)
```
Sets clipboard contents.

### Event Tap (Simulate Keys)

```lua
hs.eventtap.keyStrokes(text)
```
Simulates typing text.

**Example (defeat paste blocking):**
```lua
hs.hotkey.bind({"cmd", "alt"}, "V", function()
  hs.eventtap.keyStrokes(hs.pasteboard.getContents())
end)
```

### Settings (Persistent Storage)

```lua
hs.settings.set(key, value)
```
Stores value persistently.

```lua
value = hs.settings.get(key)
```
Retrieves stored value.

```lua
hs.settings.clear(key)
```
Removes stored value.

### Timers

```lua
timer = hs.timer.doAfter(seconds, fn)
```
Executes function after delay.

```lua
timer = hs.timer.doEvery(seconds, fn)
```
Executes function repeatedly.

```lua
timer:stop()
```
Stops timer.

---

## Coordinate System

- Origin `(0, 0)` is at the **top-left** of the primary screen
- Positive X goes right, positive Y goes down
- Each screen has its own coordinate space
- Use `screen:frame()` for usable area (excludes menubar/dock)
- Use `screen:fullFrame()` for full screen (includes menubar/dock)

---

## Common Modifier Keys

```lua
mods = {"cmd"}      -- Command ⌘
mods = {"alt"}      -- Option ⌥
mods = {"ctrl"}     -- Control ⌃
mods = {"shift"}    -- Shift ⇧
mods = {"cmd", "alt", "ctrl"}  -- Multiple modifiers
```

---

## Best Practices

1. **Always check for nil windows:**
   ```lua
   local win = hs.window.focusedWindow()
   if not win then return end
   ```

2. **Use global variables for watchers:**
   ```lua
   -- GOOD
   myWatcher = hs.pathwatcher.new(...)

   -- BAD - will be garbage collected
   local myWatcher = hs.pathwatcher.new(...)
   ```

3. **Use screen:frame() not fullFrame():**
   ```lua
   local frame = win:screen():frame()  -- Usable area
   ```

4. **Always include reload hotkey:**
   ```lua
   hs.hotkey.bind({"cmd", "alt", "ctrl"}, "R", function() hs.reload() end)
   ```

---

For complete API documentation, visit: http://www.hammerspoon.org/docs/

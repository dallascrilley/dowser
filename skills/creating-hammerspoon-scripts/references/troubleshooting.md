# Hammerspoon Troubleshooting Guide

Solutions for common Hammerspoon issues with root cause analysis and fixes.

---

## Config & Reload Issues

### Problem: Config Changes Have No Effect

**Symptoms:**
- Edited `init.lua` but behavior unchanged
- New hotkeys don't work
- Modifications ignored

**Root Cause:**
Hammerspoon only reads `init.lua` on:
1. Application launch
2. Explicit reload via `hs.reload()`

Changes are **NOT** automatically applied on file save.

**Solution:**
```lua
-- Add this hotkey to manually reload
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "R", function()
  hs.reload()
end)
```

**Better Solution (Auto-Reload):**
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

-- MUST be global!
configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
hs.alert.show("Config loaded")
```

### Problem: Syntax Errors Not Visible

**Symptoms:**
- Config loads but some parts don't work
- No error messages visible
- Silent failures

**Solution:**
Open the Hammerspoon Console to see errors:
```lua
-- Add hotkey to toggle console
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "C", function()
  hs.toggleConsole()
end)
```

Or: Click Hammerspoon menubar icon → "Console"

**Common Syntax Errors:**
```lua
-- WRONG - Missing 'end'
function test()
  print("test")

-- RIGHT
function test()
  print("test")
end

-- WRONG - Missing comma in table
local apps = {
  c = "Chrome"
  f = "Finder"  -- Missing comma above
}

-- RIGHT
local apps = {
  c = "Chrome",
  f = "Finder"
}
```

---

## Watcher Issues

### Problem: Watcher Works Then Stops

**Symptoms:**
- Pathwatcher/wifi watcher/app watcher works for a few minutes
- Then silently stops responding
- No error messages

**Root Cause:**
Lua garbage collector cleans up objects stored in **local** variables when they go out of scope. After `init.lua` finishes executing, local variables are eligible for garbage collection.

**How to Diagnose:**
Look for `local` keyword before watcher variable:
```lua
-- WRONG - Will be garbage collected
local configWatcher = hs.pathwatcher.new(...):start()
```

**Solution:**
Remove `local` keyword to make it a global variable:
```lua
-- RIGHT - Persists for session
configWatcher = hs.pathwatcher.new(...):start()
```

**All Watchers Affected:**
- `hs.pathwatcher`
- `hs.wifi.watcher`
- `hs.application.watcher`
- `hs.usb.watcher`
- `hs.screen.watcher`
- `hs.caffeinate.watcher`
- `hs.timer` (doAfter, doEvery)

**Pattern to Follow:**
```lua
-- Always use global variables for watchers
myPathWatcher = hs.pathwatcher.new(...):start()
myWifiWatcher = hs.wifi.watcher.new(...):start()
myAppWatcher = hs.application.watcher.new(...):start()
myTimer = hs.timer.doEvery(60, function() ... end)
```

### Problem: Watcher Triggers Too Often

**Symptoms:**
- Pathwatcher fires multiple times for single file save
- Callback executes repeatedly

**Root Cause:**
Text editors save files using temporary files, triggering multiple filesystem events.

**Solution:**
Debounce the callback:
```lua
local reloadTimer = nil

function reloadConfig(files)
  -- Cancel pending reload
  if reloadTimer then
    reloadTimer:stop()
  end

  -- Schedule reload after 0.5 second delay
  reloadTimer = hs.timer.doAfter(0.5, function()
    local doReload = false
    for _, file in pairs(files) do
      if file:sub(-4) == ".lua" then
        doReload = true
      end
    end
    if doReload then
      hs.reload()
    end
  end)
end

configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
```

---

## Hotkey Issues

### Problem: Hotkey Doesn't Work

**Symptoms:**
- Pressing hotkey has no effect
- No error in console
- Code looks correct

**Possible Causes & Solutions:**

**1. Key Combination Already in Use**
macOS or another app is using that combination.

Solution: Try different modifiers
```lua
-- Instead of {"cmd", "alt"}
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "H", ...)

-- Or use less common combinations
hs.hotkey.bind({"cmd", "alt", "shift"}, "H", ...)
```

Check System Settings → Keyboard → Keyboard Shortcuts for conflicts.

**2. Missing Accessibility Permissions**
Hammerspoon requires Accessibility access.

Solution: System Settings → Privacy & Security → Accessibility → Enable Hammerspoon

If already enabled, toggle it off and on again.

**3. Function Has Error**
Error in callback prevents hotkey from working.

Solution: Check console for errors
```lua
hs.hotkey.bind({"cmd", "alt"}, "H", function()
  print("Hotkey triggered")  -- Debug message
  -- Rest of code
end)
```

**4. Wrong Key Name**
Some keys have specific names in Hammerspoon.

Common key names:
- Arrow keys: `"Left"`, `"Right"`, `"Up"`, `"Down"`
- Function keys: `"F1"`, `"F2"`, etc.
- Special: `"Return"`, `"Tab"`, `"Space"`, `"Escape"`, `"Delete"`
- Letters: Lowercase `"a"`, `"b"`, etc.

### Problem: Hotkey Triggers Wrong Action

**Symptoms:**
- Hotkey activates system function instead of Hammerspoon action
- macOS beeps when pressing hotkey

**Root Cause:**
macOS system shortcuts take precedence.

**Solution:**
1. Disable conflicting system shortcuts in System Settings
2. Use different key combination
3. Use modal hotkeys instead

---

## Window Management Issues

### Problem: Windows Go Under Menubar/Dock

**Symptoms:**
- Window positioned but partially off-screen
- Top of window hidden behind menubar
- Bottom hidden behind dock

**Root Cause:**
Using `screen:fullFrame()` instead of `screen:frame()`.

**Wrong:**
```lua
local frame = win:screen():fullFrame()  -- Includes menubar/dock area
```

**Right:**
```lua
local frame = win:screen():frame()  -- Usable area only
```

**Explanation:**
- `:fullFrame()` - Full screen including menubar and dock
- `:frame()` - Usable screen area (excludes menubar/dock)

### Problem: Focused Window is Nil

**Symptoms:**
- Script crashes with nil reference error
- "attempt to index nil value" error

**Root Cause:**
No window has focus (e.g., desktop clicked, no apps running).

**Solution:**
Always check for nil:
```lua
local win = hs.window.focusedWindow()
if not win then
  hs.alert.show("No window focused")
  return
end

-- Safe to use win here
local frame = win:frame()
```

### Problem: Window Won't Resize/Move

**Symptoms:**
- Code executes without error
- Window doesn't move or resize

**Possible Causes:**

**1. App Doesn't Support Resizing**
Some apps (like system preferences) restrict window manipulation.

Solution: Check if window is standard:
```lua
local win = hs.window.focusedWindow()
if not win or not win:isStandard() then
  hs.alert.show("Window cannot be resized")
  return
end
```

**2. Wrong Frame Format**
Frame must be table with x, y, w, h keys.

Wrong:
```lua
win:setFrame({100, 100, 500, 500})  -- Array format
```

Right:
```lua
win:setFrame({x = 100, y = 100, w = 500, h = 500})  -- Table format
```

---

## Modal Hotkey Issues

### Problem: Modal Doesn't Exit

**Symptoms:**
- Press escape but modal stays active
- Single-key bindings continue working

**Root Cause:**
Forgot to call `modal:exit()` in bindings.

**Wrong:**
```lua
modal:bind("", "h", function()
  hs.application.launchOrFocus("Chrome")
  -- Missing modal:exit()
end)
```

**Right:**
```lua
modal:bind("", "h", function()
  hs.application.launchOrFocus("Chrome")
  modal:exit()  -- Always exit after action
end)

-- Always include escape
modal:bind("", "escape", function()
  modal:exit()
end)
```

### Problem: Modal Bindings Don't Work

**Symptoms:**
- Enter modal but keys have no effect
- Modal seems to activate but nothing happens

**Root Cause:**
Using modifiers in modal bindings when you shouldn't.

**Wrong:**
```lua
-- Don't use modifiers inside modal
modal:bind({"cmd"}, "h", function() ... end)
```

**Right:**
```lua
-- Use empty table for modifiers inside modal
modal:bind("", "h", function() ... end)
```

---

## Application Control Issues

### Problem: App Won't Launch

**Symptoms:**
- `hs.application.launchOrFocus()` doesn't work
- No error message

**Possible Causes:**

**1. Wrong App Name**
App name must exactly match what's shown in Activity Monitor.

Solution: Check exact name:
```lua
-- Print all running apps to find correct name
for _, app in ipairs(hs.application.runningApplications()) do
  print(app:name())
end
```

Common mistakes:
- "Google Chrome" not "Chrome"
- "Visual Studio Code" not "VSCode"
- "iTerm" not "iTerm2" (depends on version)

**2. App Not Installed**
App doesn't exist at `/Applications/`.

Solution: Verify installation or use bundle ID:
```lua
hs.application.launchOrFocusByBundleID("com.google.Chrome")
```

**3. App Won't Focus**
App is running but won't come to front.

Solution: Force activation:
```lua
local app = hs.application.get("Safari")
if app then
  app:activate()
end
```

---

## Performance Issues

### Problem: Hammerspoon Uses Excessive CPU

**Symptoms:**
- Hammerspoon process uses significant CPU
- System feels sluggish
- Battery drains quickly

**Possible Causes:**

**1. Busy Watcher Callback**
Callback function does too much work or runs too often.

Solution: Optimize callback or add throttling:
```lua
local lastRun = 0
local throttleDelay = 1  -- seconds

function throttledCallback()
  local now = os.time()
  if now - lastRun < throttleDelay then
    return  -- Skip if ran recently
  end
  lastRun = now

  -- Do actual work here
end
```

**2. Too Many Watchers**
Many watchers running simultaneously.

Solution: Combine or disable unused watchers.

**3. Infinite Loop**
Logic error causes infinite recursion.

Solution: Add guards and limits:
```lua
local depth = 0
local maxDepth = 10

function recursiveFunction()
  depth = depth + 1
  if depth > maxDepth then
    print("Max depth reached, stopping")
    depth = 0
    return
  end

  -- Function logic
  depth = depth - 1
end
```

---

## Debugging Techniques

### Print Debugging

```lua
-- Print to console
print("Debug message")
print("Variable value:", myVar)
print(hs.inspect(myTable))  -- Pretty-print tables
```

### Notifications for Debugging

```lua
-- Visual feedback
hs.alert.show("Checkpoint reached")
hs.notify.new({title="Debug", informativeText="Value: " .. tostring(value)}):send()
```

### Console Logging

```lua
-- Enable verbose logging
hs.logger.setGlobalLogLevel("debug")

-- Create logger for module
local log = hs.logger.new('myModule', 'debug')
log.d("Debug message")
log.i("Info message")
log.w("Warning message")
log.e("Error message")
```

### Stack Traces

```lua
-- Print call stack
print(debug.traceback())
```

### Check What's Loaded

```lua
-- Print all global variables
for k, v in pairs(_G) do
  if type(v) ~= "function" and type(v) ~= "table" then
    print(k, v)
  end
end
```

---

## Getting Help

1. **Check Console** - `hs.toggleConsole()` shows all errors
2. **Read API Docs** - http://www.hammerspoon.org/docs/
3. **Check Getting Started Guide** - https://www.hammerspoon.org/go/
4. **GitHub Issues** - https://github.com/Hammerspoon/hammerspoon/issues
5. **Community Examples** - https://github.com/Hammerspoon/hammerspoon/wiki/Sample-Configurations

---

## Quick Diagnostic Checklist

When something doesn't work:

- [ ] Did I reload the config? (`hs.reload()` or menubar → Reload Config)
- [ ] Are there errors in the console? (Open with `hs.toggleConsole()`)
- [ ] Are watchers stored in global variables (no `local`)?
- [ ] Did I check for nil windows before using them?
- [ ] Are my hotkeys conflicting with system shortcuts?
- [ ] Does Hammerspoon have Accessibility permissions?
- [ ] Am I using `screen:frame()` not `fullFrame()`?
- [ ] Did I call `modal:exit()` in my modal bindings?
- [ ] Is the app name spelled correctly (check Activity Monitor)?
- [ ] Did I add a reload hotkey so I can test changes easily?

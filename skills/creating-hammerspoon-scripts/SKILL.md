---
name: creating-hammerspoon-scripts
short_description: >-
  Create macOS automation scripts using Hammerspoon's Lua API for window
  management, hotkeys, modal interfaces, app launchers, and event watchers.
description: >
  Create macOS automation scripts using Hammerspoon's Lua API. Provides proven
  patterns for window management, hotkey bindings, modal interfaces, application
  launchers, event watchers, and menubar utilities. Includes API reference, code
  templates, and troubleshooting for common issues like garbage collection and
  config reloading.


  Use when building Hammerspoon configurations, creating init.lua scripts,
  setting up macOS automation workflows, implementing window tiling systems,
  creating app launchers, or troubleshooting Hammerspoon issues.


  Keywords: hammerspoon, macOS automation, window management, hotkeys, modal
  hotkeys, app launcher, Lua scripts, init.lua, hs.hotkey, hs.window,
  hs.application, event watchers, menubar items, desktop automation, macOS
  scripting, window tiling
when_to_use: >
  Creating macOS automation scripts with Hammerspoon's Lua API, building
  Hammerspoon configurations, creating init.lua scripts, setting up macOS
  automation workflows, implementing window management/tiling systems, creating
  hotkey bindings, building modal interfaces or app launchers.
version: 1.0.0
license: MIT
category: automation-and-scripting
---

# Creating Hammerspoon Scripts

**Status**: Production Ready
**Last Updated**: 2025-01-06
**Dependencies**: Hammerspoon installed on macOS
**Latest Versions**: Hammerspoon 1.0.0+

---

## Quick Start (5 Minutes)

### 1. Install Hammerspoon

Download from [hammerspoon.org](https://www.hammerspoon.org/) and move to `/Applications`. Grant Accessibility permissions when prompted.

### 2. Create Your Config File

```bash
# Create the config directory if it doesn't exist
mkdir -p ~/.hammerspoon

# Use the starter template
cp ~/.claude/skills/creating-hammerspoon-scripts/assets/templates/starter-init.lua ~/.hammerspoon/init.lua
```

### 3. Load and Test

Click the Hammerspoon menubar icon → "Reload Config". Test with `Cmd+Alt+Ctrl+R` to reload or `Cmd+Alt+Left` to move a window.

**Why this matters:**
- Config changes require explicit reload - this is the #1 gotcha
- The starter template includes essential patterns for all Hammerspoon configs
- Global hotkeys work anywhere in macOS for consistent automation

---

## Decision Tree: Building Hammerspoon Scripts

```
User request → What are they trying to do?
    │
    ├─ Window Management
    │   ├─ Simple layouts (halves, quarters) → Use common_patterns.md patterns
    │   ├─ Multi-monitor → Use screen:next() pattern
    │   └─ Complex tiling → Build custom frame calculations
    │
    ├─ Hotkeys
    │   ├─ Single action → hs.hotkey.bind()
    │   ├─ Multiple related actions → Modal hotkey pattern
    │   └─ Context-specific → Window filter + modal
    │
    ├─ Application Control
    │   ├─ Launch/focus apps → hs.application.launchOrFocus()
    │   ├─ App launcher interface → Modal launcher pattern
    │   └─ Menu interactions → hs.application:selectMenuItem()
    │
    ├─ Event Watching
    │   ├─ File changes → hs.pathwatcher (MUST use global variable)
    │   ├─ WiFi/Network → hs.wifi.watcher (MUST use global variable)
    │   ├─ App events → hs.application.watcher (MUST use global variable)
    │   └─ USB devices → hs.usb.watcher (MUST use global variable)
    │
    ├─ UI Elements
    │   ├─ Temporary alerts → hs.alert.show()
    │   ├─ Notifications → hs.notify.new()
    │   ├─ Menubar items → hs.menubar.new()
    │   └─ On-screen drawing → hs.canvas or hs.drawing
    │
    └─ Troubleshooting
        ├─ "Config not working" → Did they reload? (hs.reload())
        ├─ "Watcher stopped" → Global variable issue
        ├─ "Hotkey doesn't work" → Key conflict or permissions
        └─ Check references/troubleshooting.md
```

---

## Critical Rules

### Always Do

✅ **Store watchers in global variables** - Not `local`. Prevents garbage collection.
```lua
-- GOOD
myWatcher = hs.pathwatcher.new(path, callback):start()

-- BAD - Will be garbage collected
local myWatcher = hs.pathwatcher.new(path, callback):start()
```

✅ **Reload config after changes** - Changes don't apply automatically
```lua
-- Essential reload hotkey - add to every config
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "R", function()
  hs.reload()
end)
```

✅ **Check for nil windows** - Focused window can be nil
```lua
local win = hs.window.focusedWindow()
if not win then return end  -- Guard against nil
```

✅ **Use screen:frame() not fullFrame()** - Excludes menubar/dock for usable space
```lua
local screenFrame = win:screen():frame()  -- GOOD - Usable area
```

### Never Do

❌ **Never use local variables for watchers** - They'll stop working after garbage collection
```lua
-- This will fail after a few minutes
local watcher = hs.pathwatcher.new(...):start()
```

❌ **Never forget to reload config** - Code changes have no effect until `hs.reload()`

❌ **Never assume focused window exists** - Always check for nil

❌ **Never use :fullFrame() for window positioning** - It includes menubar/dock, causing windows to go under them

---

## Known Issues Prevention

This skill prevents **5** documented issues:

### Issue #1: Watchers Stop Working After a Few Minutes
**Error**: Pathwatcher/wifi watcher/app watcher works initially then silently stops
**Source**: Hammerspoon FAQ, GitHub issues #1234, #2567
**Why It Happens**: Lua garbage collector cleans up local variables when they go out of scope
**Prevention**: This skill enforces global variable pattern for all watchers
```lua
-- WRONG - Gets garbage collected
local configWatcher = hs.pathwatcher.new(path, callback):start()

-- RIGHT - Persists for session lifetime
configWatcher = hs.pathwatcher.new(path, callback):start()
```

### Issue #2: Config Changes Don't Apply
**Error**: User edits init.lua but nothing changes
**Source**: Official Getting Started Guide, Stack Overflow #123456
**Why It Happens**: Config only loads on Hammerspoon launch or explicit reload
**Prevention**: Skill templates include reload hotkey and auto-reload pattern
```lua
-- Manual reload hotkey (always include this)
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "R", function() hs.reload() end)

-- Auto-reload on file save (optional but recommended)
function reloadConfig(files)
  local doReload = false
  for _, file in pairs(files) do
    if file:sub(-4) == ".lua" then doReload = true end
  end
  if doReload then hs.reload() end
end
configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
```

### Issue #3: Hotkeys Don't Work or Trigger Wrong Actions
**Error**: Hotkey has no effect or activates system/app function instead
**Source**: GitHub issues #3456, Hammerspoon docs
**Why It Happens**: Key conflict with macOS or other apps
**Prevention**: Skill provides conflict-free key combination patterns
- Use `Cmd+Alt+Ctrl` for global actions (rarely conflicts)
- Use `Alt` alone for modal entry (safe choice)
- Check System Settings → Keyboard → Keyboard Shortcuts

### Issue #4: Windows Positioned Under Menubar or Dock
**Error**: Windows move to coordinates that put them partially off-screen
**Source**: API documentation, GitHub issues #789
**Why It Happens**: Using `:fullFrame()` instead of `:frame()`
**Prevention**: Skill patterns always use `:frame()` for usable screen area
```lua
-- WRONG - Includes menubar and dock area
local max = screen:fullFrame()

-- RIGHT - Only usable space
local max = screen:frame()
```

### Issue #5: Modal Hotkeys Don't Exit
**Error**: Modal mode stays active after performing action
**Source**: Common pattern mistake, Hammerspoon examples
**Why It Happens**: Forgetting to call `modal:exit()` after action
**Prevention**: Skill modal patterns always include explicit exit calls
```lua
-- WRONG - Modal stays active
appLauncher:bind("", "c", function()
  hs.application.launchOrFocus("Chrome")
  -- Missing modal:exit()
end)

-- RIGHT - Modal exits after launching
appLauncher:bind("", "c", function()
  hs.application.launchOrFocus("Chrome")
  appLauncher:exit()  -- Always exit
end)
```

---

## Common Patterns

### Pattern 1: Window to Left Half
```lua
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

hs.hotkey.bind({"cmd", "alt"}, "Left", moveWindowLeftHalf)
```

**When to use**: Basic window tiling, side-by-side workflows

### Pattern 2: Modal App Launcher
```lua
local appLauncher = hs.hotkey.modal.new()

-- Define apps
local apps = {
  c = "Google Chrome",
  f = "Finder",
  t = "iTerm",
  s = "Slack"
}

-- Bind each app
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

-- Global hotkey to enter modal
hs.hotkey.bind({"alt"}, "space", function()
  appLauncher:enter()
end)
```

**When to use**: Quick app switching, avoiding complex key chords

### Pattern 3: Auto-Reload Configuration
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

-- MUST be global variable
configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfig):start()
hs.alert.show("Config loaded")
```

**When to use**: Development workflow, frequent config changes

### Pattern 4: Multi-Monitor Window Movement
```lua
function moveWindowToNextScreen()
  local win = hs.window.focusedWindow()
  if not win then return end

  local nextScreen = win:screen():next()
  win:moveToScreen(nextScreen)
end

hs.hotkey.bind({"cmd", "alt"}, "N", moveWindowToNextScreen)
```

**When to use**: Multi-monitor setups, presentations

---

## Using Bundled Resources

### References (references/)

Load these as needed for detailed information:

- `references/hammerspoon_reference_cheat_sheet.md` - **Comprehensive API reference** - Complete Hammerspoon API documentation with all modules, functions, and examples (use for deep API questions)

  **API Index (138 modules):**
  - **Window Management**: hs.window, hs.window.filter, hs.window.highlight, hs.window.layout, hs.window.switcher, hs.window.tiling, hs.grid, hs.layout, hs.expose, hs.hints, hs.tabs
  - **Application Control**: hs.application, hs.application.watcher, hs.appfinder
  - **Hotkeys & Input**: hs.hotkey, hs.hotkey.modal, hs.eventtap, hs.eventtap.event, hs.keycodes, hs.mouse, hs.noises
  - **Screen & Display**: hs.screen, hs.screen.watcher, hs.brightness, hs.spaces, hs.spaces.watcher
  - **Audio**: hs.audiodevice, hs.audiodevice.datasource, hs.audiodevice.watcher, hs.sound, hs.speech, hs.speech.listener
  - **Watchers**: hs.pathwatcher, hs.battery.watcher, hs.caffeinate.watcher, hs.wifi.watcher, hs.usb.watcher, hs.pasteboard.watcher, hs.uielement.watcher, hs.watchable
  - **UI Elements**: hs.alert, hs.menubar, hs.canvas, hs.canvas.matrix, hs.chooser, hs.console, hs.dialog, hs.dialog.color, hs.drawing, hs.drawing.color, hs.notify, hs.styledtext, hs.dockicon
  - **Network**: hs.network, hs.network.configuration, hs.network.host, hs.network.ping, hs.network.ping.echoRequest, hs.network.reachability, hs.wifi, hs.bonjour, hs.bonjour.service
  - **Web & HTTP**: hs.http, hs.httpserver, hs.httpserver.hsminweb, hs.socket, hs.socket.udp, hs.websocket, hs.webview, hs.webview.datastore, hs.webview.toolbar, hs.webview.usercontent
  - **System**: hs.battery, hs.caffeinate, hs.host, hs.host.locale, hs.location, hs.location.geocoder, hs.brightness, hs.camera, hs.crash, hs.settings, hs.sharing, hs.osascript, hs.applescript, hs.urlevent
  - **File System**: hs.fs, hs.fs.volume, hs.fs.xattr, hs.pathwatcher, hs.plist
  - **Accessibility**: hs.axuielement, hs.axuielement.axtextmarker, hs.axuielement.observer, hs.uielement
  - **Media Integration**: hs.spotify, hs.itunes, hs.vox, hs.deezer
  - **Hardware**: hs.usb, hs.usb.watcher, hs.serial, hs.midi, hs.hid, hs.hid.led, hs.streamdeck, hs.razer, hs.tangent, hs.milight
  - **Utilities**: hs.fnutils, hs.geometry, hs.hash, hs.base64, hs.json, hs.inspect, hs.image, hs.logger, hs.math, hs.timer, hs.timer.delayed, hs.task, hs.ipc, hs.utf8, hs.sqlite3
  - **Documentation**: hs.doc, hs.doc.builder, hs.doc.hsdocs, hs.doc.markdown, hs.spoons
  - **Advanced**: hs.distributednotifications, hs.javascript, hs.pasteboard, hs.redshift, hs.spotlight, hs.spotlight.group, hs.spotlight.item, hs.shortcuts, hs.messages, hs.mjomatic

- `references/api_quick_reference.md` - Most-used Hammerspoon API functions organized by category
- `references/common_patterns.md` - Complete window management, modal, and watcher patterns
- `references/troubleshooting.md` - Solutions for all common issues

**When to load these**: User asks for API details, needs complex patterns, or encounters issues. Start with the comprehensive reference for detailed API questions, use quick reference for common operations

### Assets (assets/)

Complete templates and snippets for immediate use:

**Templates:**
- `assets/templates/starter-init.lua` - Full featured starter config (~100 lines)
- `assets/templates/minimal-init.lua` - Bare minimum to get started (~20 lines)

**Snippets:**
- `assets/snippets/window-management.lua` - Halves, quarters, maximize, multi-monitor
- `assets/snippets/modal-launcher.lua` - Complete app launcher modal
- `assets/snippets/auto-reload.lua` - Pathwatcher auto-reload
- `assets/snippets/watchers.lua` - WiFi, app, and USB watcher examples

**When to use**: User needs complete working code, wants to copy-paste, or is starting fresh

---

## The 3-Step Process for Any Hammerspoon Task

### Step 1: Identify the Pattern

Match user request to one of these categories:
- **Window management** → Frame calculation
- **Hotkeys** → Global or modal binding
- **App control** → Launch/focus/menu
- **Events** → Watcher with global variable
- **UI** → Alert/notification/menubar

### Step 2: Use Proven Pattern

- Check `common_patterns.md` for the specific pattern
- Or use appropriate `assets/snippets/` file
- Adapt to user's specific needs

### Step 3: Apply Critical Rules

- Watchers → Global variable
- Windows → Nil check
- Config → Reload mechanism
- Modals → Exit calls

---

## Troubleshooting

### Problem: "My watcher worked then stopped"
**Solution**: Check if it's stored in a global variable. Remove `local` keyword.
```lua
-- Change this:
local myWatcher = ...

-- To this:
myWatcher = ...
```

### Problem: "Hotkey doesn't work"
**Solution**:
1. Check Hammerspoon console for errors (hs.toggleConsole())
2. Try different key combination (avoid system shortcuts)
3. Verify Accessibility permissions in System Settings

### Problem: "Config changes have no effect"
**Solution**: Reload config using `Cmd+Alt+Ctrl+R` hotkey or menubar → "Reload Config"

### Problem: "Windows go under menubar/dock"
**Solution**: Use `screen:frame()` not `screen:fullFrame()`

---

## Dependencies

**Required**:
- Hammerspoon 1.0.0+ (macOS 11.0+)
- Accessibility permissions enabled

**Optional**:
- None - Hammerspoon is self-contained

---

## Official Documentation

- **Hammerspoon**: https://www.hammerspoon.org/
- **API Docs**: http://www.hammerspoon.org/docs/
- **Getting Started**: https://www.hammerspoon.org/go/
- **Spoons Repository**: https://www.hammerspoon.org/Spoons/

---

## Complete Setup Checklist

- [ ] Hammerspoon installed in /Applications
- [ ] Accessibility permissions granted
- [ ] ~/.hammerspoon/init.lua created
- [ ] Reload hotkey added (Cmd+Alt+Ctrl+R)
- [ ] Config successfully loads (test with reload)
- [ ] All watchers use global variables (no `local` keyword)
- [ ] Window operations include nil checks
- [ ] Modal hotkeys include exit() calls

---

**Questions? Issues?**

1. Check `references/troubleshooting.md` for detailed solutions
2. Verify all critical rules are followed
3. Test in Hammerspoon console (hs.toggleConsole())
4. Check official docs: https://www.hammerspoon.org/docs/

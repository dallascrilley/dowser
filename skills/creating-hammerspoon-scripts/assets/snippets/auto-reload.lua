-- Auto-Reload Configuration Snippet
-- Copy-paste this into your init.lua

-- ========================================
-- BASIC AUTO-RELOAD
-- ========================================

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
hs.alert.show("Config loaded")

-- ========================================
-- WITH DEBOUNCING (Prevents multiple reloads)
-- ========================================

local reloadTimer = nil

function reloadConfigDebounced(files)
  -- Cancel any pending reload
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

-- MUST be global!
configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reloadConfigDebounced):start()

-- ========================================
-- MANUAL RELOAD HOTKEY
-- ========================================

-- Essential: Manual reload with Cmd+Alt+Ctrl+R
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "R", function()
  hs.reload()
end)

-- ========================================
-- TOGGLE CONSOLE HOTKEY (for debugging)
-- ========================================

hs.hotkey.bind({"cmd", "alt", "ctrl"}, "C", function()
  hs.toggleConsole()
end)

-- Minimal Hammerspoon Configuration
-- The absolute bare minimum to get started
--
-- To use: Copy to ~/.hammerspoon/init.lua and reload Hammerspoon

-- 1. Essential reload hotkey (Cmd+Alt+Ctrl+R)
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "R", function()
  hs.reload()
end)
hs.alert.show("Config loaded")

-- 2. Example: Move window to left half (Cmd+Alt+Left)
hs.hotkey.bind({"cmd", "alt"}, "Left", function()
  local win = hs.window.focusedWindow()
  if not win then return end

  local frame = win:screen():frame()
  win:setFrame({x = frame.x, y = frame.y, w = frame.w / 2, h = frame.h})
end)

-- That's it! Start adding more hotkeys below.
-- For examples, see ~/.claude/skills/creating-hammerspoon-scripts/assets/snippets/

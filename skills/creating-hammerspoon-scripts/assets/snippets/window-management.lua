-- Window Management Snippets
-- Copy-paste these into your init.lua

-- ========================================
-- HALVES
-- ========================================

-- Left half
hs.hotkey.bind({"cmd", "alt"}, "Left", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x, y = frame.y, w = frame.w / 2, h = frame.h})
end)

-- Right half
hs.hotkey.bind({"cmd", "alt"}, "Right", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x + frame.w / 2, y = frame.y, w = frame.w / 2, h = frame.h})
end)

-- Top half
hs.hotkey.bind({"cmd", "alt"}, "Up", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x, y = frame.y, w = frame.w, h = frame.h / 2})
end)

-- Bottom half
hs.hotkey.bind({"cmd", "alt"}, "Down", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x, y = frame.y + frame.h / 2, w = frame.w, h = frame.h / 2})
end)

-- ========================================
-- QUARTERS
-- ========================================

-- Top-left quarter
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "1", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x, y = frame.y, w = frame.w / 2, h = frame.h / 2})
end)

-- Top-right quarter
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "2", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x + frame.w / 2, y = frame.y, w = frame.w / 2, h = frame.h / 2})
end)

-- Bottom-left quarter
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "3", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x, y = frame.y + frame.h / 2, w = frame.w / 2, h = frame.h / 2})
end)

-- Bottom-right quarter
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "4", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x + frame.w / 2, y = frame.y + frame.h / 2, w = frame.w / 2, h = frame.h / 2})
end)

-- ========================================
-- MAXIMIZE & CENTER
-- ========================================

-- Maximize
hs.hotkey.bind({"cmd", "alt"}, "M", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  win:setFrame(win:screen():frame())
end)

-- Center window (keeps size)
hs.hotkey.bind({"cmd", "alt"}, "C", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local screen = win:screen():frame()
  local winFrame = win:frame()
  winFrame.x = screen.x + (screen.w - winFrame.w) / 2
  winFrame.y = screen.y + (screen.h - winFrame.h) / 2
  win:setFrame(winFrame)
end)

-- ========================================
-- MULTI-MONITOR
-- ========================================

-- Move to next screen
hs.hotkey.bind({"cmd", "alt"}, "N", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  win:moveToScreen(win:screen():next())
end)

-- Move to previous screen
hs.hotkey.bind({"cmd", "alt"}, "P", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  win:moveToScreen(win:screen():previous())
end)

-- ========================================
-- THIRDS (2/3 and 1/3 splits)
-- ========================================

-- Left 2/3
hs.hotkey.bind({"cmd", "alt", "shift"}, "Left", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x, y = frame.y, w = frame.w * 0.67, h = frame.h})
end)

-- Right 1/3
hs.hotkey.bind({"cmd", "alt", "shift"}, "Right", function()
  local win = hs.window.focusedWindow()
  if not win then return end
  local frame = win:screen():frame()
  win:setFrame({x = frame.x + frame.w * 0.67, y = frame.y, w = frame.w * 0.33, h = frame.h})
end)

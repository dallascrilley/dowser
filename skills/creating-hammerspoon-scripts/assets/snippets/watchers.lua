-- Event Watcher Snippets
-- Copy-paste these into your init.lua
--
-- CRITICAL: All watchers MUST use global variables (no 'local')!

-- ========================================
-- WIFI NETWORK WATCHER
-- ========================================

lastSSID = hs.wifi.currentNetwork()
homeSSID = "YourHomeNetworkName"  -- Change this!

function wifiChanged()
  local newSSID = hs.wifi.currentNetwork()

  if newSSID == homeSSID and lastSSID ~= homeSSID then
    -- Arrived at home network
    hs.notify.new({title="WiFi", informativeText="Connected to home"}):send()
    -- Example: Set volume when arriving home
    hs.audiodevice.defaultOutputDevice():setVolume(25)

  elseif newSSID ~= homeSSID and lastSSID == homeSSID then
    -- Left home network
    hs.notify.new({title="WiFi", informativeText="Left home network"}):send()
    -- Example: Mute volume when leaving
    hs.audiodevice.defaultOutputDevice():setVolume(0)
  end

  lastSSID = newSSID
end

-- MUST be global!
wifiWatcher = hs.wifi.watcher.new(wifiChanged):start()

-- ========================================
-- APPLICATION WATCHER
-- ========================================

function appWatcherCallback(appName, eventType, appObject)
  if eventType == hs.application.watcher.activated then
    -- App was focused
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
    print(appName .. " quit")
  end
end

-- MUST be global!
appWatcher = hs.application.watcher.new(appWatcherCallback):start()

-- ========================================
-- USB DEVICE WATCHER
-- ========================================

function usbCallback(data)
  if data.eventType == "added" then
    local message = "USB Connected: " .. data.productName
    hs.notify.new({title="USB", informativeText=message}):send()

    -- Example: Auto-launch app when specific device connected
    if data.productName == "ScanSnap S1300i" then
      hs.application.launchOrFocus("ScanSnap Manager")
    end

  elseif data.eventType == "removed" then
    local message = "USB Removed: " .. data.productName
    hs.notify.new({title="USB", informativeText=message}):send()

    -- Example: Auto-quit app when device removed
    if data.productName == "ScanSnap S1300i" then
      local app = hs.application.get("ScanSnap Manager")
      if app then app:kill() end
    end
  end
end

-- MUST be global!
usbWatcher = hs.usb.watcher.new(usbCallback):start()

-- ========================================
-- SCREEN WATCHER (Monitor changes)
-- ========================================

function screenChanged()
  local screens = hs.screen.allScreens()
  local count = #screens

  hs.notify.new({
    title="Screens",
    informativeText=count .. " screen(s) detected"
  }):send()

  -- Example: Rearrange windows when screen count changes
  if count > 1 then
    -- Multiple monitors - move specific apps to external screen
    local externalScreen = hs.screen.allScreens()[2]
    local slackApp = hs.application.get("Slack")
    if slackApp then
      local slackWin = slackApp:mainWindow()
      if slackWin then
        slackWin:moveToScreen(externalScreen)
      end
    end
  end
end

-- MUST be global!
screenWatcher = hs.screen.watcher.new(screenChanged):start()

-- ========================================
-- BATTERY WATCHER
-- ========================================

function batteryChanged()
  local battery = hs.battery.percentage()
  local charging = hs.battery.isCharging()

  -- Warn if battery is low and not charging
  if battery < 20 and not charging then
    hs.notify.new({
      title="Battery Low",
      informativeText=battery .. "% remaining - Please charge!",
      soundName="Ping"
    }):send()
  end
end

-- MUST be global!
batteryWatcher = hs.battery.watcher.new(batteryChanged):start()

-- ========================================
-- CAFFEINATE WATCHER (Sleep/Wake events)
-- ========================================

function caffeineChanged(eventType)
  if eventType == hs.caffeinate.watcher.systemWillSleep then
    print("System going to sleep")
    -- Example: Save work, close connections, etc.

  elseif eventType == hs.caffeinate.watcher.systemDidWake then
    print("System woke from sleep")
    -- Example: Reconnect to services, refresh data, etc.

  elseif eventType == hs.caffeinate.watcher.screensDidLock then
    print("Screen locked")
    -- Example: Pause music, mute volume, etc.

  elseif eventType == hs.caffeinate.watcher.screensDidUnlock then
    print("Screen unlocked")
    -- Example: Resume music, restore volume, etc.
  end
end

-- MUST be global!
caffeineWatcher = hs.caffeinate.watcher.new(caffeineChanged):start()

-- ========================================
-- AUDIO DEVICE WATCHER
-- ========================================

function audioDeviceChanged(action)
  if action == "dOut" then
    -- Default output device changed (e.g., headphones plugged in)
    local device = hs.audiodevice.defaultOutputDevice()
    hs.notify.new({
      title="Audio Output Changed",
      informativeText="Now using: " .. device:name()
    }):send()

    -- Example: Adjust volume for specific devices
    if device:name() == "Built-in Speakers" then
      device:setVolume(50)
    elseif device:name():find("Headphones") then
      device:setVolume(75)
    end
  end
end

-- MUST be global!
audioWatcher = hs.audiodevice.watcher.setCallback(audioDeviceChanged):start()

-- ========================================
-- NOTES
-- ========================================

-- Remember:
-- 1. All watchers MUST be global variables (no 'local')
-- 2. Watchers persist until Hammerspoon reload
-- 3. Stop a watcher with: watcherName:stop()
-- 4. Check console for errors if watcher doesn't work

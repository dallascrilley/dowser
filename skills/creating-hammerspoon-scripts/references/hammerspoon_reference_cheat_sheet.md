```
hs.alert.md
# hs.alert

Simple on-screen alerts

## Key Exports

- `show`
- `showWithImage`
- `closeAll`
- `closeSpecific`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `show` | `hs.alert.show(str, [style], [screen], [seconds]...` | a string identifier for the alert. | For convenience, you can call this function as `hs.alert(...)` |
| `showWithImage` | `hs.alert.showWithImage(str, image, [style], [sc...` | a string identifier for the alert. | The optional parameters are parsed in the order presented as follows: |
| `closeAll` | `hs.alert.closeAll([seconds])` | None |  |
| `closeSpecific` | `hs.alert.closeSpecific(uuid, [seconds])` | None | Use this function to close an alert which is indefinite or close an alert wit... |

## Common Patterns

```lua
-- Show simple alert
hs.alert.show('Hello World')

-- Show alert with custom duration
hs.alert.show('Message', nil, nil, 5)
```

```

```
hs.appfinder.md
# hs.appfinder

Easily find `hs.application` and `hs.window` objects

**⚠️ DEPRECATED:** This module is _deprecated_ ; you can use `hs.window.find()`, `hs.window.get()`, `hs.application.find()`, `hs.application.get()`, `hs.application:findWindow()` and `hs.application:getWindow()` instead.

## Key Exports

- `appFromName`
- `appFromWindowTitle`
- `appFromWindowTitlePattern`
- `windowFromWindowTitle`
- `windowFromWindowTitlePattern`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `appFromName` | `hs.appfinder.appFromName(name) -> app or nil` | An hs.application object if one can be found, otherwise nil |  |
| `appFromWindowTitle` | `hs.appfinder.appFromWindowTitle(title) -> app o...` | An hs.application object if one can be found, otherwise nil |  |
| `appFromWindowTitlePattern` | `hs.appfinder.appFromWindowTitlePattern(pattern)...` | An hs.application object if one can be found, otherwise nil | For more about Lua patterns, see http://lua-users.org/wiki/PatternsTutorial a... |
| `windowFromWindowTitle` | `hs.appfinder.windowFromWindowTitle(title) -> wi...` | An hs.window object if one can be found, otherwise nil |  |
| `windowFromWindowTitlePattern` | `hs.appfinder.windowFromWindowTitlePattern(patte...` | An hs.window object if one can be found, otherwise nil | For more about Lua patterns, see http://lua-users.org/wiki/PatternsTutorial a... |

## Common Patterns


```

```
hs.applescript.md
# hs.applescript

Execute AppleScript code

## Common Patterns


```

```
hs.application.md
# hs.application

Manipulate running applications

## Key Exports

- `get`
- `getMenuItems`
- `getWindow`
- `setFrontmost`
- `find`
- `findMenuItem`
- `findWindow`
- `enableSpotlightForNameSearches`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.application.get(hint) -> hs.application object` | an hs.application object for a running application that m... | see also `hs.application.find` |
| `getMenuItems` | `hs.application:getMenuItems([fn]) -> table or n...` | If no argument is provided, returns a table containing th... | In some applications, this can take a little while to complete, because quite... |
| `getWindow` | `hs.application:getWindow(title) -> hs.window ob...` | the desired hs.window object belonging to this applicatio... |  |
| `setFrontmost` | `hs.application:setFrontmost([allWindows]) -> bo...` | A boolean, true if the operation was successful, otherwis... |  |
| `find` | `hs.application.find(hint, exact, stringLiteral)...` | one or more hs.application objects for running applicatio... | If multiple results are found, this function will return multiple values. See... |
| `findMenuItem` | `hs.application:findMenuItem(menuItem[, isRegex]...` | Returns nil if the menu item cannot be found. If it does ... | This can only search for menu items that don't have children - i.e. you can't... |
| `findWindow` | `hs.application:findWindow(titlePattern) -> hs.w...` | one or more hs.window objects belonging to this applicati... |  |
| `enableSpotlightForNameSearches` | `hs.application.enableSpotlightForNameSearches([...` | the current, possibly changed, state | This setting is persistent across reloading and restarting Hammerspoon. |

## Common Patterns

```lua
-- Create instance
local obj = hs.application.find(...)
```

```

```
hs.application.watcher.md
# hs.application.watcher

Watch for application launch/terminate events

## Key Exports

- `new`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.application.watcher.new(fn) -> watcher` | An `hs.application.watcher` object | If the function is called with an event type of `hs.application.watcher.termi... |
| `start` | `hs.application.watcher:start()` | The `hs.application.watcher` object |  |
| `stop` | `hs.application.watcher:stop()` | The `hs.application.watcher` object |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.watcher.new(...)
```

```

```
hs.audiodevice.datasource.md
# hs.audiodevice.datasource

Inspect/manipulate the data sources of an audio device

## Key Exports

- `setDefault`
- `name`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setDefault` | `hs.audiodevice.datasource:setDefault() -> hs.au...` | The `hs.audiodevice.datasource` object |  |
| `name` | `hs.audiodevice.datasource:name() -> string` | A string containing the name of the datasource |  |

## Common Patterns


```

```
hs.audiodevice.md
# hs.audiodevice

Manipulate the system's audio devices

## Key Exports

- `setBalance`
- `setDefaultEffectDevice`
- `setDefaultInputDevice`
- `setDefaultOutputDevice`
- `setInputMuted`
- `setInputVolume`
- `setMuted`
- `setOutputMuted`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setBalance` | `hs.audiodevice:setBalance(level) -> bool` | True if the balance was set, false if the audio device do... | This method will inspect the device to determine if it is an input or output ... |
| `setDefaultEffectDevice` | `hs.audiodevice:setDefaultEffectDevice() -> bool` | True if the audio device was successfully selected, other... |  |
| `setDefaultInputDevice` | `hs.audiodevice:setDefaultInputDevice() -> bool` | True if the audio device was successfully selected, other... |  |
| `setDefaultOutputDevice` | `hs.audiodevice:setDefaultOutputDevice() -> bool` | True if the audio device was successfully selected, other... |  |
| `setInputMuted` | `hs.audiodevice:setInputMuted(state) -> bool` | True if the device's Input mutedness state was set, or Fa... |  |
| `setInputVolume` | `hs.audiodevice:setInputVolume(level) -> bool` | True if the volume was set, false if the audio device doe... | The volume level is a floating point number. Depending on your audio hardware... |
| `setMuted` | `hs.audiodevice:setMuted(state) -> bool` | True if the device's mutedness state was set, or False if... | If a device is capable of both input and output, this method will prefer the ... |
| `setOutputMuted` | `hs.audiodevice:setOutputMuted(state) -> bool` | True if the device's Output mutedness state was set, or F... |  |
| `setOutputVolume` | `hs.audiodevice:setOutputVolume(level) -> bool` | True if the volume was set, false if the audio device doe... | The volume level is a floating point number. Depending on your audio hardware... |

## Common Patterns


```

```
hs.audiodevice.watcher.md
# hs.audiodevice.watcher

Watch for system level audio hardware events

## Key Exports

- `setCallback`
- `start`
- `stop`
- `isRunning`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setCallback` | `hs.audiodevice.watcher.setCallback(fn)` | None | This watcher will call the callback when various audio device related events ... |
| `start` | `hs.audiodevice.watcher.start()` | None |  |
| `stop` | `hs.audiodevice.watcher.stop() -> hs.audiodevice...` | The `hs.audiodevice.watcher` object |  |
| `isRunning` | `hs.audiodevice.watcher.isRunning() -> boolean` | A boolean, true if the watcher is running, false if not |  |

## Common Patterns


```

```
hs.axuielement.axtextmarker.md
# hs.axuielement.axtextmarker

This submodule allows hs.axuielement to support using AXTextMarker and AXTextMarkerRange objects as parameters for parameterized Accessibility attributes with applications that support them.

## Key Exports

- `newMarker`
- `newRange`
- `startMarker`
- `_functionCheck`
- `bytes`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `newMarker` | `hs.axuielement.axtextmarker.newMarker(string) -...` | a new axTextMarkerObject or nil and a string description ... | This function is included primarily for testing and debugging purposes -- in ... |
| `newRange` | `hs.axuielement.axtextmarker.newRange(startMarke...` | a new axTextMarkerRangeObject or nil and a string descrip... | this constructor can be used to create a range from axTextMarkerObjects obtai... |
| `startMarker` | `hs.axuielement.axtextmarker:startMarker() -> ax...` | the starting marker for an axTextMarkerRangeObject |  |
| `_functionCheck` | `hs.axuielement.axtextmarker._functionCheck() ->...` | a table with key-value pairs where the keys correspond to... | the functions are defined within the HIServices framework which is part of th... |
| `bytes` | `hs.axuielement.axtextmarker:bytes() -> string \...` | a string containing the opaque binary data contained with... | the string will likely contain invalid UTF8 code sequences or unprintable asc... |

## Common Patterns

```lua
-- Create instance
local obj = hs.axtextmarker.newMarker(...)
```

```

```
hs.axuielement.md
# hs.axuielement

This module allows you to access the accessibility objects of running applications, their windows, menus, and other user interface elements that support the OS X accessibility API.

## Key Exports

- `setAttributeValue`
- `setTimeout`
- `applicationElement`
- `applicationElementForPID`
- `systemElementAtPosition`
- `systemWideElement`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setAttributeValue` | `hs.axuielement:setAttributeValue(attribute, val...` | the axuielementObject on success; nil and an error string... |  |
| `setTimeout` | `hs.axuielement:setTimeout(value) -> axuielement...` | the axuielementObject or nil and an error string if an ac... | To change the global timeout affecting all queries on elements which do not h... |
| `applicationElement` | `hs.axuielement.applicationElement(applicationOb...` | an axuielementObject for the application specified | if `applicationObject` is a string or number, only the first item found with ... |
| `applicationElementForPID` | `hs.axuielement.applicationElementForPID(pid) ->...` | an axuielementObject for the application specified, or ni... |  |
| `systemElementAtPosition` | `hs.axuielement.systemElementAtPosition(x, y \| ...` | an axuielementObject for the object at the specified coor... | See also hs.axuielement:elementAtPosition -- this function is a shortcut for ... |
| `systemWideElement` | `hs.axuielement.systemWideElement() -> axuieleme...` | the axuielementObject for the system attributes |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.axuielement.applicationElement(...)
```

```

```
hs.axuielement.observer.md
# hs.axuielement.observer

This submodule allows you to create observers for accessibility elements and be notified when they trigger notifications. Not all notifications are supported by all elements and not all elements support notifications, so some trial and error will be necessary, but for compliant applications, this can allow your code to be notified when an application's user interface changes in some way.

## Key Exports

- `new`
- `start`
- `stop`
- `addWatcher`
- `callback`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.axuielement.observer.new(pid) -> observerObject` | a new observerObject; generates an error if the pid does ... | If you already have the `hs.application` object for an application, you can g... |
| `start` | `hs.axuielement.observer:start() -> observerObject` | the observerObject | This method does nothing if the observer is already running |
| `stop` | `hs.axuielement.observer:stop() -> observerObject` | the observerObject | This method does nothing if the observer is not currently running |
| `addWatcher` | `hs.axuielement.observer:addWatcher(element, not...` | the observerObject; generates an error if watcher cannot ... | multiple notifications for the same accessibility element can be registered b... |
| `callback` | `hs.axuielement.observer:callback([fn]) -> obser...` | If an argument is provided, the observerObject; otherwise... | the callback should expect 4 arguments and return none. The arguments passed ... |

## Common Patterns

```lua
-- Create instance
local obj = hs.observer.new(...)
```

```

```
hs.base64.md
# hs.base64

Base64 encoding and decoding

## Key Exports

- `decode`
- `encode`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `decode` | `hs.base64.decode(str) -> val` | A string containing the decoded data |  |
| `encode` | `hs.base64.encode(val[,width]) -> str` | A string containing the base64 representation of the inpu... |  |

## Common Patterns


```

```
hs.battery.md
# hs.battery

Battery/power information All functions here may return nil, if the information requested is not available.

## Key Exports

- `getAll`
- `_report`
- `adapterSerialNumber`
- `amperage`
- `batterySerialNumber`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getAll` | `hs.battery.getAll() -> table` | A table containing all the information provided by the se... | If you require multiple pieces of information about a battery, this function ... |
| `_report` | `hs.battery._report() -> table` | a table containing the raw data about the power source(s)... | This function is generally not required and is provided to aid in debugging. ... |
| `adapterSerialNumber` | `hs.battery.adapterSerialNumber() -> integer \| ...` | An number or string containing the power supply's serial ... |  |
| `amperage` | `hs.battery.amperage() -> number` | A number containing the amount of current flowing through... |  |
| `batterySerialNumber` | `hs.battery.batterySerialNumber() -> string` | A string containing the battery's serial number, or nil i... |  |

## Common Patterns


```

```
hs.battery.watcher.md
# hs.battery.watcher

Watch for battery/power state changes

## Key Exports

- `new`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.battery.watcher.new(fn) -> watcher` | An `hs.battery.watcher` object | Because the callback function accepts no arguments, tracking of state of chan... |
| `start` | `hs.battery.watcher:start() -> self` | The `hs.battery.watcher` object |  |
| `stop` | `hs.battery.watcher:stop() -> self` | The `hs.battery.watcher` object |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.watcher.new(...)
```

```

```
hs.bonjour.md
# hs.bonjour

Find and publish network services advertised by multicast DNS (Bonjour) with Hammerspoon.

## Key Exports

- `new`
- `findBrowsableDomains`
- `findRegistrationDomains`
- `findServices`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.bonjour.new() -> browserObject` | a new browserObject or nil if an error occurs |  |
| `findBrowsableDomains` | `hs.bonjour:findBrowsableDomains(callback) -> br...` | the browserObject | This method returns domains which are visible to your machine; however, your ... |
| `findRegistrationDomains` | `hs.bonjour:findRegistrationDomains(callback) ->...` | the browserObject | This is the preferred method for accessing domains as it guarantees that the ... |
| `findServices` | `hs.bonjour:findServices(type, [domain], [callba...` | the browserObject | macOS will indicate when it believes there are no more advertisements of the ... |
| `stop` | `hs.bonjour:stop() -> browserObject` | the browserObject | This method should be invoked when you have identified the services or hosts ... |

## Common Patterns

```lua
-- Create instance
local obj = hs.bonjour.new(...)
```

```

```
hs.bonjour.service.md
# hs.bonjour.service

Represents the service records that are discovered or published by the hs.bonjour module.

## Key Exports

- `new`
- `stop`
- `stopMonitoring`
- `remote`
- `addresses`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.bonjour.service.new(name, service, port, [do...` | the newly created service object, or nil if there was an ... | If the name specified is not unique on the network for the service type speci... |
| `stop` | `hs.bonjour.service:stop() -> serviceObject` | the serviceObject | this method will stop the advertising of a service which has been published w... |
| `stopMonitoring` | `hs.bonjour.service:stopMonitoring() -> serviceO...` | the serviceObject | This method will stop updating hs.bonjour.service:txtRecord and invoking the ... |
| `remote` | `hs.bonjour.service.remote(name, service, [domai...` | the newly created service object, or nil if there was an ... | In general you should not need to use this constructor, as they will be creat... |
| `addresses` | `hs.bonjour.service:addresses() -> table` | an array table of strings representing the IPv4 and IPv6 ... | for remote serviceObjects, the table will be empty if this method is invoked ... |

## Common Patterns

```lua
-- Create instance
local obj = hs.service.new(...)
```

```

```
hs.brightness.md
# hs.brightness

Inspect/manipulate display brightness

## Key Exports

- `get`
- `set`
- `ambient`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.brightness.get() -> number` | A number containing the brightness of the display, betwee... |  |
| `set` | `hs.brightness.set(brightness) -> boolean` | True if the brightness was set, false if not |  |
| `ambient` | `hs.brightness.ambient() -> number` | A number containing the current ambient brightness, measu... | Even though external Apple displays include an ambient light sensor, their da... |

## Common Patterns


```

```
hs.caffeinate.md
# hs.caffeinate

Control system power states (sleeping, preventing sleep, screen locking, etc)

## Key Exports

- `get`
- `set`
- `startScreensaver`
- `currentAssertions`
- `declareUserActivity`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.caffeinate.get(sleepType) -> bool or nil` | True if the specified type of sleep is being prevented, f... |  |
| `set` | `hs.caffeinate.set(sleepType, aValue, acAndBattery)` | None | These calls are not guaranteed to prevent the system sleep behaviours describ... |
| `startScreensaver` | `hs.caffeinate.startScreensaver()` | None |  |
| `currentAssertions` | `hs.caffeinate.currentAssertions()` | A table containing information about current power assert... |  |
| `declareUserActivity` | `hs.caffeinate.declareUserActivity([id])` | A number containing the ID of the assertion generated by ... | This is intended to simulate user activity, for example to prevent displays f... |

## Common Patterns


```

```
hs.caffeinate.watcher.md
# hs.caffeinate.watcher

Watch for display and system sleep/wake/power events and for fast user switching session events.

## Key Exports

- `new`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.caffeinate.watcher.new(fn) -> watcher` | An `hs.caffeinate.watcher` object |  |
| `start` | `hs.caffeinate.watcher:start()` | An `hs.caffeinate.watcher` object |  |
| `stop` | `hs.caffeinate.watcher:stop()` | An `hs.caffeinate.watcher` object |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.watcher.new(...)
```

```

```
hs.camera.md
# hs.camera

Inspect the system's camera devices

## Key Exports

- `setWatcherCallback`
- `setPropertyWatcherCallback`
- `startWatcher`
- `startPropertyWatcher`
- `stopWatcher`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setWatcherCallback` | `hs.camera.setWatcherCallback(fn)` | None | The callback will be called when a camera is added or removed from the system |
| `setPropertyWatcherCallback` | `hs.camera:setPropertyWatcherCallback(fn) -> hs....` | The `hs.camera` object |  |
| `startWatcher` | `hs.camera.startWatcher()` | None |  |
| `startPropertyWatcher` | `hs.camera:startPropertyWatcher()` | The `hs.camera` object |  |
| `stopWatcher` | `hs.camera.stopWatcher()` | None |  |

## Common Patterns


```

```
hs.canvas.matrix.md
# hs.canvas.matrix

A sub module to `hs.canvas` which provides support for basic matrix manipulations which can be used as the values for `transformation` attributes in the `hs.canvas` module.

## Key Exports

- `identity`
- `append`
- `invert`
- `prepend`
- `rotate`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `identity` | `hs.canvas.matrix.identity() -> matrixObject` | the identity matrix. | The identity matrix can be thought of as "apply no transformations at all" or... |
| `append` | `hs.canvas.matrix:append(matrix) -> matrixObject` | the new matrix | Mathematically this method multiples the original matrix by the new one and r... |
| `invert` | `hs.canvas.matrix:invert() -> matrixObject` | the inverted matrix. | Inverting a matrix which represents a series of transformations has the effec... |
| `prepend` | `hs.canvas.matrix:prepend(matrix) -> matrixObject` | the new matrix | Mathematically this method multiples the new matrix by the original one and r... |
| `rotate` | `hs.canvas.matrix:rotate(angle) -> matrixObject` | the new matrix | The rotation of an element this matrix is applied to will be rotated about th... |

## Common Patterns

```lua
-- Create instance
local obj = hs.matrix.identity(...)
```

```

```
hs.canvas.md
# hs.canvas

A different approach to drawing in Hammerspoon

## Key Exports

- `new`
- `show`
- `delete`
- `attributes`
- `object`
- `percentages`
- `defaultTextStyle`
- `elementSpec`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.canvas.new(rect) -> canvasObject` | a new, empty, canvas object, or nil if the canvas cannot ... | The size of the canvas defines the visible area of the canvas -- any portion ... |
| `show` | `hs.canvas:show([fadeInTime]) -> canvasObject` | The canvas object | if the canvas is in use as an element in another canvas, this method will res... |
| `delete` | `hs.canvas:delete([fadeOutTime]) -> none` | None | This method is automatically called during garbage collection, notably during... |
| `attributes` | `hs.canvas.attributes` | None | `type` - specifies the type of canvas element the table represents. This attr... |
| `object` | `hs.canvas.object[index]` | None |  |
| `percentages` | `hs.canvas.percentages` | None |  |
| `defaultTextStyle` | `hs.canvas.defaultTextStyle() ->` | a table containing the default style attributes `hs.canva... | This method is intended to be used in conjunction with `hs.styledtext` to cre... |
| `elementSpec` | `hs.canvas.elementSpec() -> table` | A table containing the attributes and specifications defi... | This is primarily for debugging purposes and may be removed in the future. |
| `help` | `hs.canvas.help([attribute]) -> string` | a string containing some of the information provided by t... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.canvas.new(...)
```

```

```
hs.chooser.md
# hs.chooser

Graphical, interactive tool for choosing/searching data

## Key Exports

- `new`
- `show`
- `showCallback`
- `enableDefaultForQuery`
- `delete`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.chooser.new(completionFn) -> hs.chooser object` | An `hs.chooser` object | As of macOS Sierra and later, if you want a `hs.chooser` object to appear abo... |
| `show` | `hs.chooser:show([topLeftPoint]) -> hs.chooser o...` | The hs.chooser object |  |
| `showCallback` | `hs.chooser:showCallback([fn]) -> hs.chooser object` | The hs.chooser object | This callback is called _after_ the chooser is shown. To execute code just be... |
| `enableDefaultForQuery` | `hs.chooser:enableDefaultForQuery([]) -> hs.choo...` | the `hs.chooser` object if a value was set, or a boolean ... | This should be used before a chooser has been displayed |
| `delete` | `hs.chooser:delete()` | None |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.chooser.new(...)
```

```

```
hs.console.md
# hs.console

Some functions for manipulating the Hammerspoon console.

**⚠️ DEPRECATED:** * Deprecateds - API features which will be removed in an future release

## Key Exports

- `getConsole`
- `getHistory`
- `setConsole`
- `setHistory`
- `alpha`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getConsole` | `hs.console.getConsole([styled]) -> text \| styl...` | The text currently in the Hammerspoon console output wind... | If the text of the console is retrieved as a string, no color or style inform... |
| `getHistory` | `hs.console.getHistory() -> array` | an array containing the history of commands entered into ... |  |
| `setConsole` | `hs.console.setConsole([styledText]) -> none` | None | You can specify the console content as a string or as an `hs.styledtext` obje... |
| `setHistory` | `hs.console.setHistory(array) -> nil` | None | You can clear the console history by using an empty array (e.g. `hs.console.s... |
| `alpha` | `hs.console.alpha([alpha]) -> currentValue` | the current, possibly new, value. |  |

## Common Patterns


```

```
hs.crash.md
# hs.crash

Various features/facilities for developers who are working on Hammerspoon itself, or writing extensions for it. It is extremely unlikely that you should need any part of this extension, in a normal user configuration.

## Key Exports

- `attemptMemoryRelease`
- `crash`
- `crashKV`
- `crashLog`
- `dumpCLIBS`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `attemptMemoryRelease` | `hs.crash.attemptMemoryRelease()` | None | This function will print some memory usage numbers (in bytes) to the Hammersp... |
| `crash` | `hs.crash.crash()` | None | This is for testing purposes only, you are extremely unlikely to need this in... |
| `crashKV` | `hs.crash.crashKV(key, value)` | None |  |
| `crashLog` | `hs.crash.crashLog(logMessage)` | None | This is probably only useful to extension developers. If you are trying to tr... |
| `dumpCLIBS` | `hs.crash.dumpCLIBS() -> table` | A table containing all the paths of C libraries that have... | This is probably only useful to extension developers as a useful way of ensur... |

## Common Patterns


```

```
hs.deezer.md
# hs.deezer

Controls for Deezer music player.

## Key Exports

- `getCurrentAlbum`
- `getCurrentArtist`
- `getCurrentTrack`
- `getPlaybackState`
- `getPosition`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getCurrentAlbum` | `hs.deezer.getCurrentAlbum()` | A string containing the Album of the current track, or ni... |  |
| `getCurrentArtist` | `hs.deezer.getCurrentArtist()` | A string containing the Artist of the current track, or n... |  |
| `getCurrentTrack` | `hs.deezer.getCurrentTrack()` | A string containing the name of the current track, or nil... |  |
| `getPlaybackState` | `hs.deezer.getPlaybackState()` | A string containing one of the following constants: |  |
| `getPosition` | `hs.deezer.getPosition()` | A number indicating the current position in the song |  |

## Common Patterns


```

```
hs.dialog.color.md
# hs.dialog.color

A panel that allows users to select a color.

## Key Exports

- `show`
- `showsAlpha`
- `alpha`
- `callback`
- `color`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `show` | `hs.dialog.color.show() -> none` | None | Example: `hs.dialog.color.show()` |
| `showsAlpha` | `hs.dialog.color.showsAlpha([value]) -> boolean` | `true` if the opacity slider is displayed otherwise `false` | Example: `hs.dialog.color.showsAlpha(true)` |
| `alpha` | `hs.dialog.color.alpha([value]) -> number` | The current alpha value as a number. | Example: `hs.dialog.color.alpha(0.5)` |
| `callback` | `hs.dialog.color.callback([callbackFn]) -> funct...` | The last callbackFn or `nil` so you can save it and re-at... | Example: `hs.dialog.color.callback(function(a,b) print("COLOR CALLBACK:\nSele... |
| `color` | `hs.dialog.color.color([value]) -> table` | A table of the currently selected color in the form of `h... | Example: `hs.dialog.color.color(hs.drawing.color.blue)` |

## Common Patterns


```

```
hs.dialog.md
# hs.dialog

A collection of useful dialog boxes, alerts and panels for user interaction.

## Key Exports

- `alert`
- `blockAlert`
- `chooseFileOrFolder`
- `textPrompt`
- `webviewAlert`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `alert` | `hs.dialog.alert(x, y, callbackFn, message, [inf...` | nil | The optional values must be entered in order (i.e. you can't supply `style` w... |
| `blockAlert` | `hs.dialog.blockAlert(message, informativeText, ...` | The value of the button as a string. | The optional values must be entered in order (i.e. you can't supply `style` w... |
| `chooseFileOrFolder` | `hs.dialog.chooseFileOrFolder([message], [defaul...` | The selected files in a table or `nil` if cancel was pres... | The optional values must be entered in order (i.e. you can't supply `allowsMu... |
| `textPrompt` | `hs.dialog.textPrompt(message, informativeText, ...` | The value of the button as a string | `buttonOne` defaults to "OK" if no value is supplied. |
| `webviewAlert` | `hs.dialog.webviewAlert(webview, callbackFn, mes...` | nil | This alert is will prevent the user from interacting with the `hs.webview` un... |

## Common Patterns


```

```
hs.distributednotifications.md
# hs.distributednotifications

Interact with NSDistributedNotificationCenter There are many notifications posted by parts of OS X, and third party apps, which may be interesting to react to using this module.

## Key Exports

- `new`
- `start`
- `stop`
- `post`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.distributednotifications.new(callback[, name...` | An `hs.distributednotifications` object | On Catalina and above, it is no longer possible to observe all notifications ... |
| `start` | `hs.distributednotifications:start() -> object` | The `hs.distributednotifications` object |  |
| `stop` | `hs.distributednotifications:stop() -> object` | The `hs.distributednotifications` object |  |
| `post` | `hs.distributednotifications.post(name[, sender[...` | None |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.distributednotifications.new(...)
```

```

```
hs.doc.builder.md
# hs.doc.builder

Builds documentation support files. Still experimental.

## Key Exports

- `genComments`
- `genJSON`
- `genSQL`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `genComments` | `hs.doc.builder.genComments(path, [recurse]) -> ...` | table - a table containing the documentation broken out i... | Because Hammerspoon and all known currently available modules are coded in Ob... |
| `genJSON` | `hs.doc.builder.genJSON(source) -> string` | string - the JSON string representation of the documentation | If you have installed the `hs` command line tool (see `hs.ipc`), you can use ... |
| `genSQL` | `hs.doc.builder.genSQL(source) -> string` | string - the relevant SQL commands as a string |  |

## Common Patterns


```

```
hs.doc.hsdocs.md
# hs.doc.hsdocs

Manage the internal documentation web server.

## Key Exports

- `start`
- `stop`
- `browserDarkMode`
- `browserFrame`
- `forceExternalBrowser`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `start` | `hs.doc.hsdocs.start() ->` | the table representing the `hs.doc.hsdocs` module | This function is automatically called, if necessary, when hs.doc.hsdocs.help ... |
| `stop` | `hs.doc.hsdocs.stop() ->` | the table representing the `hs.doc.hsdocs` module |  |
| `browserDarkMode` | `hs.doc.hsdocs.browserDarkMode([value]) -> curre...` | the current, possibly new, value | Inversion is applied through the use of CSS filtering, so while numeric value... |
| `browserFrame` | `hs.doc.hsdocs.browserFrame([frameTable]) -> cur...` | the current, possibly new, value | If hs.doc.hsdocs.trackBrowserFrame is false or nil (the default), then you ca... |
| `forceExternalBrowser` | `hs.doc.hsdocs.forceExternalBrowser([value]) -> ...` | the current, possibly new, value | If this value is set to true, help requests invoked by hs.doc.hsdocs.help wil... |

## Common Patterns


```

```
hs.doc.markdown.md
# hs.doc.markdown

Markdown to HTML and plaintext conversion support used by hs.doc

## Key Exports

- `convert`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `convert` | `hs.doc.markdown.convert(markdown, [type]) -> ou...` | an HTML or plaintext representation of the markdown encod... | The standard GitHub/Markdown extensions enabled for all conversions are: |

## Common Patterns


```

```
hs.doc.md
# hs.doc

Create documentation objects for interactive help within Hammerspoon

## Key Exports

- `help`
- `locateJSONFile`
- `preloadSpoonDocs`
- `registeredFiles`
- `registerJSONFile`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `help` | `hs.doc.help(identifier)` | None | This function is mainly for runtime API help while using Hammerspoon's Console |
| `locateJSONFile` | `hs.doc.locateJSONFile(module) -> path \| false,...` | the path to the JSON file, or `false, error` if unable to... | The JSON should be named 'docs.json' and located in the same directory as the... |
| `preloadSpoonDocs` | `hs.doc.preloadSpoonDocs()` | None |  |
| `registeredFiles` | `hs.doc.registeredFiles() -> table` | a table containing the list of registered JSON files | The table returned by this function has a metatable including a __tostring me... |
| `registerJSONFile` | `hs.doc.registerJSONFile(jsonfile, [isSpoon]) ->...` | status - Boolean flag indicating if the file was register... | this function just registers the documentation file; it won't actually be loa... |

## Common Patterns


```

```
hs.dockicon.md
# hs.dockicon

Control Hammerspoon's dock icon

## Key Exports

- `setBadge`
- `show`
- `bounce`
- `hide`
- `tileCanvas`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setBadge` | `hs.dockicon.setBadge(badge)` | None |  |
| `show` | `hs.dockicon.show()` | None |  |
| `bounce` | `hs.dockicon.bounce(indefinitely)` | None |  |
| `hide` | `hs.dockicon.hide()` | None |  |
| `tileCanvas` | `hs.dockicon.tileCanvas([canvas]) -> canvasObjec...` | If the dock icon is assigned a canvas object, that canvas... | If you update the canvas object by changing any of its components, it will no... |

## Common Patterns


```

```
hs.drawing.color.md
# hs.drawing.color

Provides access to the system color lists and a wider variety of ways to represent color within Hammerspoon.

## Key Exports

- `asHSB`
- `asRGB`
- `colorsFor`
- `lists`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `asHSB` | `hs.drawing.color.asHSB(color) -> table \| string` | a table containing the hue, saturation, brightness, and a... | See also `hs.drawing.color.asRGB` |
| `asRGB` | `hs.drawing.color.asRGB(color) -> table \| string` | a table containing the red, blue, green, and alpha keys r... | See also `hs.drawing.color.asHSB` |
| `colorsFor` | `hs.drawing.color.colorsFor(list) -> table` | a table whose keys are made from the colors provided by t... | Where possible, each color node is provided as its RGB color representation. ... |
| `lists` | `hs.drawing.color.lists() -> table` | a table whose keys are made from the currently defined sy... | Where possible, each color node is provided as its RGB color representation. ... |

## Common Patterns


```

```
hs.drawing.md
# hs.drawing

DEPRECATED. Primitives for drawing on the screen in various ways.

**⚠️ DEPRECATED:** hs.drawing is now deprecated and will be removed in a future release. Its functionality is now implemented by hs.canvas and you should migrate your code to using that directly. The API docs for hs.drawing remain here as a convenience.

## Key Exports

- `getTextDrawingSize`
- `getStyledText`
- `setAlpha`
- `setArcAngles`
- `setBehavior`
- `setBehaviorByLabels`
- `setClickCallback`
- `setFill`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getTextDrawingSize` | `hs.drawing.getTextDrawingSize(styledTextObject ...` | sizeTable - a table containing the Height and Width neces... | This function assumes the default values specified for any key which is not i... |
| `getStyledText` | `hs.drawing:getStyledText() ->` | an `hs.styledtext` object | This method should only be used on text drawing objects |
| `setAlpha` | `hs.drawing:setAlpha(level) -> object` | The `hs.drawing` object |  |
| `setArcAngles` | `hs.drawing:setArcAngles(startAngle, endAngle) -...` | The drawing object | This method should only be used on arc drawing objects |
| `setBehavior` | `hs.drawing:setBehavior(behavior) -> object` | The `hs.drawing` object |  |
| `setBehaviorByLabels` | `hs.drawing:setBehaviorByLabels(table) -> object` | The `hs.drawing` object |  |
| `setClickCallback` | `hs.drawing:setClickCallback(mouseUpFn, mouseDow...` | The drawing object | No distinction is made between the left, right, or other mouse buttons -- the... |
| `setFill` | `hs.drawing:setFill(doFill) -> drawingObject` | The drawing object | This method should only be used on line, rectangle, circle, or arc drawing ob... |
| `setFillColor` | `hs.drawing:setFillColor(color) -> drawingObject` | The drawing object | This method should only be used on rectangle, circle, or arc drawing objects |
| `setFillGradient` | `hs.drawing:setFillGradient(startColor, endColor...` | The drawing object | This method should only be used on rectangle, circle, or arc drawing objects |

## Common Patterns

```lua
-- Create instance
local obj = hs.drawing.appImage(...)
```

```

```
hs.eventtap.event.md
# hs.eventtap.event

Create, modify and inspect events for `hs.eventtap`.

## Key Exports

- `newEvent`
- `newEventFromData`
- `newGesture`
- `newKeyEvent`
- `newMouseEvent`
- `newScrollEvent`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `newEvent` | `hs.eventtap.event.newEvent() -> event` | a new `hs.eventtap.event` object | this is an empty event that you should set a type for and whatever other prop... |
| `newEventFromData` | `hs.eventtap.event.newEventFromData(data) -> event` | a new `hs.eventtap.event` object or nil if the string did... |  |
| `newGesture` | `hs.eventtap.event.newGesture(gestureType[, gest...` | a new `hs.eventtap.event` object or `nil` if the `gesture... | Valid gestureType values are: |
| `newKeyEvent` | `hs.eventtap.event.newKeyEvent([mods], key, isdo...` | An `hs.eventtap.event` object | The original version of this constructor utilized a shortcut which merged `fl... |
| `newMouseEvent` | `hs.eventtap.event.newMouseEvent(eventtype, poin...` | An `hs.eventtap` object |  |
| `newScrollEvent` | `hs.eventtap.event.newScrollEvent(offsets, mods,...` | An `hs.eventtap.event` object |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.event.copy(...)
```

```

```
hs.eventtap.md
# hs.eventtap

Tap into input events (mouse, keyboard, trackpad) for observation and possibly overriding them. It also provides convenience wrappers for sending mouse and keyboard events. If you need to construct finely controlled mouse/keyboard events, see `hs.eventtap.event`.

## Key Exports

- `new`
- `start`
- `stop`
- `checkKeyboardModifiers`
- `checkMouseButtons`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.eventtap.new(types, fn) -> eventtap` | An event tap object | If you specify the argument `types` as the special table {"all"[, events to i... |
| `start` | `hs.eventtap:start()` | The event tap object |  |
| `stop` | `hs.eventtap:stop()` | The event tap object |  |
| `checkKeyboardModifiers` | `hs.eventtap.checkKeyboardModifiers([raw]) -> table` | Returns a table containing boolean values indicating whic... | This is an instantaneous poll of the current keyboard modifiers for the most ... |
| `checkMouseButtons` | `hs.eventtap.checkMouseButtons() -> table` | Returns an array containing indices starting from 1 up to... | This is an instantaneous poll of the current mouse buttons, not a callback. T... |

## Common Patterns

```lua
-- Create instance
local obj = hs.eventtap.new(...)
```

```

```
hs.expose.md
# hs.expose

Keyboard-driven expose replacement/enhancement

## Key Exports

- `new`
- `show`
- `hide`
- `toggleShow`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.expose.new([windowfilter[, uiPrefs][, lognam...` | the new instance | by default expose will show invisible windows and (unlike the OSX expose) win... |
| `show` | `hs.expose:show([activeApplication])` | None | passing `true` for `activeApplication` will simply hide hints/thumbnails for ... |
| `hide` | `hs.expose:hide()` | None | Call this function if you need to make sure the modal is exited without waiti... |
| `toggleShow` | `hs.expose:toggleShow([activeApplication])` | None | passing `true` for `activeApplication` will simply hide hints/thumbnails for ... |

## Common Patterns

```lua
-- Create instance
local obj = hs.expose.new(...)
```

```

```
hs.fnutils.md
# hs.fnutils

Functional programming utility functions

## Key Exports

- `find`
- `cycle`
- `partial`
- `sequence`
- `sortByKeys`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `find` | `hs.fnutils.find(table, fn) -> element` | The element of the supplied table that first caused fn to... |  |
| `cycle` | `hs.fnutils.cycle(table) -> fn()` | A function that, when called repeatedly, will return all ... | table cannot be a sparse table, see <http://www.luafaq.org/gotchas.html#T6.4> |
| `partial` | `hs.fnutils.partial(fn, ...) -> fn'` | A function | This is best understood with an example which you can test in the Hammerspoon... |
| `sequence` | `hs.fnutils.sequence(...) -> fn` | A function that, when called, will call all of the functi... |  |
| `sortByKeys` | `hs.fnutils.sortByKeys(table[ , function]) -> fu...` | function to be used as an iterator | Similar to Perl's `sort(keys %hash)` |

## Common Patterns

```lua
-- Create instance
local obj = hs.fnutils.cycle(...)
```

```

```
hs.fs.md
# hs.fs

Access/inspect the filesystem

## Key Exports

- `getFinderComments`
- `setFinderComments`
- `attributes`
- `chdir`
- `currentDir`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getFinderComments` | `hs.fs.getFinderComments(path) -> string` | a string containing the Finder comments for the file or d... | This function uses `hs.osascript` to access the file comments through AppleSc... |
| `setFinderComments` | `hs.fs.setFinderComments(path, comment) -> boolean` | true on success; on error, most commonly an invalid path,... | This function uses `hs.osascript` to access the file comments through AppleSc... |
| `attributes` | `hs.fs.attributes(filepath [, aName]) -> table o...` | A table with the file attributes corresponding to filepat... | This function uses `stat()` internally thus if the given filepath is a symbol... |
| `chdir` | `hs.fs.chdir(path) -> true or (nil,error)` | If successful, returns true, otherwise returns nil and an... |  |
| `currentDir` | `hs.fs.currentDir() -> string or (nil,error)` | A string containing the current working directory, or if ... |  |

## Common Patterns


```

```
hs.fs.volume.md
# hs.fs.volume

Interact with OS X filesystem volumes

## Key Exports

- `new`
- `start`
- `stop`
- `allVolumes`
- `eject`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.fs.volume.new(fn) -> watcher` | An `hs.fs.volume` object |  |
| `start` | `hs.fs.volume:start()` | An `hs.fs.volume` object |  |
| `stop` | `hs.fs.volume:stop()` | An `hs.fs.volume` object |  |
| `allVolumes` | `hs.fs.volume.allVolumes([showHidden]) -> table` | A table of information, where the keys are the paths of d... | This is an alias for `hs.host.volumeInformation()` |
| `eject` | `hs.fs.volume.eject(path) -> boolean,string` | A boolean, true if the volume was ejected, otherwise false |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.volume.new(...)
```

```

```
hs.fs.xattr.md
# hs.fs.xattr

Get and manipulate extended attributes for files and directories

## Key Exports

- `get`
- `getHumanReadable`
- `set`
- `list`
- `remove`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.fs.xattr.get(path, attribute, [options], [po...` | If the attribute exists for the file or directory and con... | See also hs.fs.xattr.getHumanReadable. |
| `getHumanReadable` | `hs.fs.xattr.getHumanReadable(path, attribute, [...` | if the returned data does not conform to proper UTF-8 byt... | This is provided for testing and debugging purposes; in general you probably ... |
| `set` | `hs.fs.xattr.set(path, attribute, value, [option...` | True if the operation succeeds; otherwise throws a Lua er... |  |
| `list` | `hs.fs.xattr.list(path, [options]) -> table` | a table containing an array of strings identifying the ex... |  |
| `remove` | `hs.fs.xattr.remove(path, attribute, [options]) ...` | True if the operation succeeds; otherwise throws a Lua er... |  |

## Common Patterns


```

```
hs.geometry.md
# hs.geometry

Utility object to represent points, sizes and rects in a bidimensional plane

## Key Exports

- `new`
- `copy`
- `point`
- `rect`
- `size`
- `area`
- `aspect`
- `bottomright`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.geometry.new(...) -> hs.geometry object` | a newly created hs.geometry object |  |
| `copy` | `hs.geometry.copy(geom) -> hs.geometry object` | a newly created copy of the hs.geometry object |  |
| `point` | `hs.geometry.point(x, y) -> hs.geometry point` | An hs.geometry point object |  |
| `rect` | `hs.geometry.rect(x, y, w, h) -> hs.geometry rect` | An hs.geometry rect object |  |
| `size` | `hs.geometry.size(w, h) -> hs.geometry size` | An hs.geometry size object |  |
| `area` | `hs.geometry.area` | None |  |
| `aspect` | `hs.geometry.aspect` | None |  |
| `bottomright` | `hs.geometry.bottomright` | None |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.geometry.copy(...)
```

```

```
hs.grid.md
# hs.grid

Move/resize windows within a grid

## Key Exports

- `get`
- `getCell`
- `getGrid`
- `getGridFrame`
- `set`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.grid.get(win) -> cell` | a cell object (i.e. an `hs.geometry` rect), or nil if an ... |  |
| `getCell` | `hs.grid.getCell(cell, screen) -> hs.geometry` | the `hs.geometry` rect for a cell on a particular screen ... |  |
| `getGrid` | `hs.grid.getGrid(screen) -> hs.geometry size` | an `hs.geometry` size object indicating the number of col... | if a grid was not set for the specified screen or geometry, the default grid ... |
| `getGridFrame` | `hs.grid.getGridFrame(screen) -> hs.geometry rect` | an `hs.geometry` rect object indicating the frame used by... |  |
| `set` | `hs.grid.set(win, cell, screen) -> hs.grid` | the `hs.grid` module for method chaining |  |

## Common Patterns


```

```
hs.hash.md
# hs.hash

This module provides various hashing algorithms for use within Hammerspoon.

## Key Exports

- `new`
- `convertBinaryHashToHex`
- `convertHexHashToBinary`
- `forFile`
- `append`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.hash.new(hash, [secret]) -> hashObject` | the new hash object |  |
| `convertBinaryHashToHex` | `hs.hash.convertBinaryHashToHex(input) -> string` | a string containing the equivalent hash as a string of he... | this is a convenience function for use when you already have a binary hash va... |
| `convertHexHashToBinary` | `hs.hash.convertHexHashToBinary(input) -> string` | a string containing the equivalent binary hash | this is a convenience function for use when you already have a hash value tha... |
| `forFile` | `hs.hash.forFile(hash, [secret], path) -> string` | a string containing the hexadecimal version of the calcul... | this is a convenience function that performs the equivalent of `hs.new.hash(h... |
| `append` | `hs.hash:append(data) -> hashObject \| nil, error` | the hash object, or if the hash has already been calculat... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.hash.new(...)
```

```

```
hs.hid.led.md
# hs.hid.led

HID LED interface for Hammerspoon, controls the state of keyboard LEDs

## Key Exports

- `set`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `set` | `hs.hid.led.set(name, state) -> bool` | true if success, false if error | This function controls the LED state only, to modify capslock state, use hs.h... |

## Common Patterns


```

```
hs.hid.md
# hs.hid

HID interface for Hammerspoon, controls and queries caps lock state

## Key Exports

- `get`
- `set`
- `toggle`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.hid.capslock.get() -> bool` | true if on, false if off |  |
| `set` | `hs.hid.capslock.set(state) -> bool` | true if on, false if off |  |
| `toggle` | `hs.hid.capslock.toggle() -> bool` | true if on, false if off |  |

## Common Patterns


```

```
hs.hints.md
# hs.hints

Switch focus with a transient per-application keyboard shortcut

## Key Exports

- `windowHints`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `windowHints` | `hs.hints.windowHints([windows, callback, allowN...` | None | If there are more windows open than there are characters available in hs.hint... |

## Common Patterns


```

```
hs.host.locale.md
# hs.host.locale

Retrieve information about the user's Language and Region settings.

## Key Exports

- `availableLocales`
- `current`
- `details`
- `localizedString`
- `preferredLanguages`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `availableLocales` | `hs.host.locale.availableLocales() -> table` | an array table of strings specifying the locale identifie... | these values can be used with hs.host.locale.details to get details for a spe... |
| `current` | `hs.host.locale.current() -> string` | a string specifying the identifier of the user's currentl... | this value can be used with hs.host.locale.details to get details for the ret... |
| `details` | `hs.host.locale.details([identifier]) -> table` | a table containing one or more of the following key-value... | If you specify a locale identifier as an argument, it should be based on one ... |
| `localizedString` | `hs.host.locale.localizedString(localeCode[, bas...` | A string containing the localized string or `nil` if eith... | The `localeCode` and optional `baseLocaleCode` must be one of the strings ret... |
| `preferredLanguages` | `hs.host.locale.preferredLanguages() -> table` | an array table of strings specifying the user's preferred... |  |

## Common Patterns


```

```
hs.host.md
# hs.host

Inspect information about the machine Hammerspoon is running on

## Key Exports

- `addresses`
- `cpuUsage`
- `cpuUsageTicks`
- `globallyUniqueString`
- `gpuVRAM`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `addresses` | `hs.host.addresses() -> table` | A table of strings containing the network addresses of th... | The results will include IPv4 and IPv6 addresses |
| `cpuUsage` | `hs.host.cpuUsage([period], [callback]) -> table` | If a callback function is not provided, this function wil... | If no callback function is provided, Hammerspoon will block (i.e. no other Ha... |
| `cpuUsageTicks` | `hs.host.cpuUsageTicks() -> table` | A table containing the following: | CPU mode ticks are updated during system interrupts and are incremented based... |
| `globallyUniqueString` | `hs.host.globallyUniqueString() -> string` | a newly generated global unique identifier as a string | See also `hs.host.uuid` |
| `gpuVRAM` | `hs.host.gpuVRAM() -> table` | A table whose key-value pairs represent the GPUs for the ... | If your GPU reports -1.0 as the memory size, please submit an issue to the Ha... |

## Common Patterns


```

```
hs.hotkey.md
# hs.hotkey

Create and manage global keyboard shortcuts

## Key Exports

- `new`
- `getHotkeys`
- `getLogLevel`
- `setLogLevel`
- `showHotkeys`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.hotkey.new(mods, key, [message,] pressedfn, ...` | A new `hs.hotkey` object or nil if the hotkey could not b... | You can create multiple `hs.hotkey` objects for the same keyboard combination... |
| `getHotkeys` | `hs.hotkey.getHotkeys() -> table` | A table containing the hotkeys that are active, i.e. enab... |  |
| `getLogLevel` | `hs.hotkey.getLogLevel() -> number` | The log level of the hotkey logger as a number between 0 ... |  |
| `setLogLevel` | `hs.hotkey.setLogLevel(loglevel)` | None |  |
| `showHotkeys` | `hs.hotkey.showHotkeys(mods, key) -> hs.hotkey o...` | The new `hs.hotkey` object |  |

## Common Patterns

```lua
-- Bind hotkey
hs.hotkey.bind({'cmd', 'alt'}, 'h', function() hs.alert.show('Hello') end)

-- Create and enable hotkey
local hotkey = hs.hotkey.new({'ctrl'}, 'r', function() end)
hotkey:enable()
```

```

```
hs.hotkey.modal.md
# hs.hotkey.modal

Create/manage modal keyboard shortcut environments

## Key Exports

- `new`
- `bind`
- `delete`
- `enter`
- `entered`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.hotkey.modal.new(mods, key, message) -> hs.h...` | A new `hs.hotkey.modal` object | If `key` is nil, no global hotkey will be registered (all other parameters wi... |
| `bind` | `hs.hotkey.modal:bind(mods, key, message, presse...` | The `hs.hotkey.modal` object for method chaining |  |
| `delete` | `hs.hotkey.modal:delete()` | None |  |
| `enter` | `hs.hotkey.modal:enter() -> hs.hotkey.modal object` | The `hs.hotkey.modal` object for method chaining | This method will enable all of the hotkeys defined in the modal state via `hs... |
| `entered` | `hs.hotkey.modal:entered()` | None | This is a preexisting function that you should override if you need to use it... |

## Common Patterns

```lua
-- Bind hotkey
hs.hotkey.bind({'cmd', 'alt'}, 'h', function() hs.alert.show('Hello') end)

-- Create and enable hotkey
local hotkey = hs.hotkey.new({'ctrl'}, 'r', function() end)
hotkey:enable()
```

```

```
hs.http.md
# hs.http

Perform HTTP requests

## Key Exports

- `get`
- `asyncGet`
- `asyncPost`
- `asyncPut`
- `convertHtmlEntities`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.http.get(url, headers) -> int, string, table` | A number containing the HTTP response status | If authentication is required in order to download the request, the required ... |
| `asyncGet` | `hs.http.asyncGet(url, headers, callback)` | None | If authentication is required in order to download the request, the required ... |
| `asyncPost` | `hs.http.asyncPost(url, data, headers, callback)` | None | If authentication is required in order to download the request, the required ... |
| `asyncPut` | `hs.http.asyncPut(url, data, headers, callback)` | None | If authentication is required in order to download the request, the required ... |
| `convertHtmlEntities` | `hs.http.convertHtmlEntities(inString) -> outString` | outString -- the input string with all recognized HTML En... | Recognized HTML Entities are those registered in `hs.http.htmlEntities` or nu... |

## Common Patterns


```

```
hs.httpserver.hsminweb.cgilua.lp.md
# hs.httpserver.hsminweb.cgilua.lp

Support functions for the CGILua compatibility module for including and translating Lua template pages into Lua code for execution within the Hammerspoon environment to provide dynamic content for http requests.

## Key Exports

- `compile`
- `include`
- `translate`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `compile` | `hs.httpserver.hsminweb.cgilua.lp.compile(source...` | A lua function which should take no arguments. | The source provided is first compared to a stored cache of previously transla... |
| `include` | `hs.httpserver.hsminweb.cgilua.lp.include(file, ...` | None | This function is called by the web server to process the template specified b... |
| `translate` | `hs.httpserver.hsminweb.cgilua.lp.translate(sour...` | The lua code corresponding to the provided source which c... | This function is used internally by cgilua.lp.include, and probably won't be ... |

## Common Patterns


```

```
hs.httpserver.hsminweb.cgilua.md
# hs.httpserver.hsminweb.cgilua

Provides support functions in the `cgilua` module for Hammerspoon Minimal Web Server Lua templates.

## Key Exports

- `contentheader`
- `doif`
- `doscript`
- `errorlog`
- `header`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `contentheader` | `hs.httpserver.hsminweb.cgilua.contentheader(mai...` | None | This sets the `Content-Type` header field for the HTTP response being generat... |
| `doif` | `hs.httpserver.hsminweb.cgilua.doif(filename) ->...` | the values returned by the execution, or nil followed by ... | This function only interprets the file if it exists; if the file does not exi... |
| `doscript` | `hs.httpserver.hsminweb.cgilua.doscript(filename...` | the values returned by the execution, or nil followed by ... | If the file does not exist, an Internal Server error is returned to the clien... |
| `errorlog` | `hs.httpserver.hsminweb.cgilua.errorlog(msg) -> nil` | None | Available within a lua template file as `cgilua.errorlog` |
| `header` | `hs.httpserver.hsminweb.cgilua.header(key, value...` | None | You should not use this function to set the value for the "Content-Type" key;... |

## Common Patterns


```

```
hs.httpserver.hsminweb.cgilua.urlcode.md
# hs.httpserver.hsminweb.cgilua.urlcode

Support functions for the CGILua compatibility module for encoding and decoding URL components in accordance with RFC 3986.

## Key Exports

- `encodetable`
- `escape`
- `insertfield`
- `parsequery`
- `unescape`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `encodetable` | `hs.httpserver.hsminweb.cgilua.urlcode.encodetab...` | a query string as specified in RFC 3986. | the string will be of the form: "key1=value1&key2=value2..." where all of the... |
| `escape` | `hs.httpserver.hsminweb.cgilua.urlcode.escape(st...` | a string with non-alphanumeric characters percent encoded... | this function assumes that the provided string is a single component and URL ... |
| `insertfield` | `hs.httpserver.hsminweb.cgilua.urlcode.insertfie...` | None | If the key already exists in the table, its value is converted to a table (if... |
| `parsequery` | `hs.httpserver.hsminweb.cgilua.urlcode.parsequer...` | None | The specification allows for the same key to be assigned multiple values in a... |
| `unescape` | `hs.httpserver.hsminweb.cgilua.urlcode.unescape(...` | a string with all "+" characters converted to spaces and ... |  |

## Common Patterns


```

```
hs.httpserver.hsminweb.md
# hs.httpserver.hsminweb

Minimalist Web Server for Hammerspoon

## Key Exports

- `new`
- `start`
- `stop`
- `formattedDate`
- `urlParts`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.httpserver.hsminweb.new([documentRoot]) -> h...` | a table representing the hsminweb object. | a web server's document root is the directory which contains the documents or... |
| `start` | `hs.httpserver.hsminweb:start() -> hsminwebTable` | the hsminWebTable object |  |
| `stop` | `hs.httpserver.hsminweb:stop() -> hsminwebTable` | the hsminWebTable object | this method is called automatically during garbage collection. |
| `formattedDate` | `hs.httpserver.hsminweb.formattedDate([date]) ->...` | the time indicated as a string in the format expected for... |  |
| `urlParts` | `hs.httpserver.hsminweb.urlParts(url) -> table` | a table containing the constituent parts of the provided ... | This function differs from the similar function `hs.http.urlParts` in a few w... |

## Common Patterns

```lua
-- Create instance
local obj = hs.hsminweb.new(...)
```

```

```
hs.httpserver.md
# hs.httpserver

Simple HTTP server

## Key Exports

- `new`
- `getInterface`
- `getName`
- `getPort`
- `setCallback`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.httpserver.new([ssl], [bonjour]) -> object` | An `hs.httpserver` object | By default, the server will start on a random TCP port and advertise itself w... |
| `getInterface` | `hs.httpserver:getInterface() -> string or nil` | A string containing the network interface name, or nil if... |  |
| `getName` | `hs.httpserver:getName() -> string` | A string containing the Bonjour name of this server | This is not the hostname of the server, just its name in Bonjour service list... |
| `getPort` | `hs.httpserver:getPort() -> number` | A number containing the TCP port |  |
| `setCallback` | `hs.httpserver:setCallback([callback]) -> object` | The `hs.httpserver` object | The callback will be passed four arguments: |

## Common Patterns


```

```
hs.image.md
# hs.image

A module for capturing and manipulating image objects from other modules for use with hs.drawing.

## Key Exports

- `getExifFromPath`
- `setName`
- `setSize`
- `iconForFile`
- `iconForFileType`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getExifFromPath` | `hs.image.getExifFromPath(path) -> table \| nil` | A table of EXIF metadata, or `nil` if no metadata can be ... |  |
| `setName` | `hs.image:setName(Name) -> boolean` | Status - a boolean value indicating success (true) or fai... | This method is included for backwards compatibility and is considered depreca... |
| `setSize` | `hs.image:setSize(size [, absolute]) -> object` | a copy of the image object at the new size | This method is included for backwards compatibility and is considered depreca... |
| `iconForFile` | `hs.image.iconForFile(file) -> object` | An `hs.image` object or nil, if there was an error. The i... |  |
| `iconForFileType` | `hs.image.iconForFileType(fileType) -> object` | An `hs.image` object or nil, if there was an error |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.image.iconForFile(...)
```

```

```
hs.inspect.md
# hs.inspect

Produce human-readable representations of Lua variables (particularly tables)

## Key Exports

- `inspect`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `inspect` | `hs.inspect.inspect(variable[, options]) -> string` | A string containing the human readable version of `variable` | For convenience, you can call this function as `hs.inspect(variable)` |

## Common Patterns


```

```
hs.ipc.md
# hs.ipc

Provides Hammerspoon with the ability to create both local and remote message ports for inter-process communication.

**⚠️ DEPRECATED:** * Deprecateds - API features which will be removed in an future release

## Key Exports

- `delete`
- `localPort`
- `remotePort`
- `cliColors`
- `cliInstall`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `delete` | `hs.ipc:delete() -> None` | None |  |
| `localPort` | `hs.ipc.localPort(name, fn) -> ipcObject` | the ipc object | a remote port can send messages at any time to a local port; a local port can... |
| `remotePort` | `hs.ipc.remotePort(name) -> ipcObject` | the ipc object | a remote port can send messages at any time to a local port; a local port can... |
| `cliColors` | `hs.ipc.cliColors([colors]) -> table` | a table describing the colors used when colorizing output... | For a brief intro into terminal colors, you can visit a web site like this on... |
| `cliInstall` | `hs.ipc.cliInstall([path][,silent]) -> bool` | A boolean, true if the tool was successfully installed, o... | If this function fails, it is likely that you have some old/broken symlinks. ... |

## Common Patterns

```lua
-- Create instance
local obj = hs.ipc.localPort(...)
```

```

```
hs.itunes.md
# hs.itunes

Controls for iTunes music player

## Key Exports

- `getCurrentAlbum`
- `getCurrentArtist`
- `getCurrentTrack`
- `getDuration`
- `getPlaybackState`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getCurrentAlbum` | `hs.itunes.getCurrentAlbum() -> string or nil` | A string containing the Album of the current track, or ni... |  |
| `getCurrentArtist` | `hs.itunes.getCurrentArtist() -> string or nil` | A string containing the Artist of the current track, or n... |  |
| `getCurrentTrack` | `hs.itunes.getCurrentTrack() -> string or nil` | A string containing the name of the current track, or nil... |  |
| `getDuration` | `hs.itunes.getDuration()` | The number of seconds long the current song is, 0 if no s... |  |
| `getPlaybackState` | `hs.itunes.getPlaybackState()` | A string containing one of the following constants: |  |

## Common Patterns


```

```
hs.javascript.md
# hs.javascript

Execute JavaScript code

## Common Patterns


```

```
hs.json.md
# hs.json

JSON encoding and decoding

## Key Exports

- `decode`
- `encode`
- `read`
- `write`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `decode` | `hs.json.decode(jsonString) -> table` | A table representing the supplied JSON data | This is useful for retrieving some of the more complex lua table structures a... |
| `encode` | `hs.json.encode(val[, prettyprint]) -> string` | A string containing a JSON representation of the supplied... | This is useful for storing some of the more complex lua table structures as a... |
| `read` | `hs.json.read(path) -> table \| nil` | A table representing the supplied JSON data, or `nil` if ... |  |
| `write` | `hs.json.write(data, path, [prettyprint], [repla...` | `true` if successful otherwise `false` if an error has oc... |  |

## Common Patterns


```

```
hs.keycodes.md
# hs.keycodes

Convert between key-strings and key-codes. Also provides functionality for querying and changing keyboard layouts.

## Key Exports

- `setLayout`
- `setMethod`
- `currentLayout`
- `currentLayoutIcon`
- `currentMethod`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setLayout` | `hs.keycodes.setLayout(layoutName) -> boolean` | A boolean, true if the layout was successfully changed, o... |  |
| `setMethod` | `hs.keycodes.setMethod(methodName) -> boolean` | A boolean, true if the method was successfully changed, o... |  |
| `currentLayout` | `hs.keycodes.currentLayout() -> string` | A string containing the name of the current keyboard layout |  |
| `currentLayoutIcon` | `hs.keycodes.currentLayoutIcon() -> hs.image object` | An hs.image object containing the icon, if available |  |
| `currentMethod` | `hs.keycodes.currentMethod() -> string` | Name of current input method, or nil |  |

## Common Patterns


```

```
hs.layout.md
# hs.layout

Window layout manager

## Key Exports

- `apply`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `apply` | `hs.layout.apply(table[, windowTitleComparator])` | None | If the application name argument is nil, window titles will be matched regard... |

## Common Patterns


```

```
hs.location.geocoder.md
# hs.location.geocoder

Converts between GPS coordinates and more user friendly representations like an address or points of interest.

## Key Exports

- `lookupAddress`
- `lookupAddressNear`
- `lookupLocation`
- `cancel`
- `geocoding`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `lookupAddress` | `hs.location.geocoder.lookupAddress(address, fn)...` | a geocodingObject | This constructor requires internet access and the callback will be invoked wi... |
| `lookupAddressNear` | `hs.location.geocoder.lookupAddressNear(address,...` | a geocodingObject | This constructor requires internet access and the callback will be invoked wi... |
| `lookupLocation` | `hs.location.geocoder.lookupLocation(locationTab...` | a geocodingObject | This constructor requires internet access and the callback will be invoked wi... |
| `cancel` | `hs.location.geocoder:cancel() -> nil` | nil to facilitate garbage collection by assigning this re... | This method has no effect if the geocoding process has already completed. |
| `geocoding` | `hs.location.geocoder:geocoding() -> boolean` | a boolean indicating if the geocoding process is still ac... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.geocoder.lookupAddress(...)
```

```

```
hs.location.md
# hs.location

Determine the machine's location and useful information about that location

**⚠️ DEPRECATED:** * [hs.location.servicesEnabled](https://www.hammerspoon.org/docs/hs.location.html#servicesEnabled) - replaces `hs.location.services_enabled`. While the earlier function is included for backwards compatibility, it will display a deprecation warning to the console the first time it is invoked and may go away completely in the future.

## Key Exports

- `new`
- `get`
- `start`
- `startTracking`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.location.new() -> locationObject` | a locationObject | The locationObject created will receive callbacks independent of all other lo... |
| `get` | `hs.location.get() -> locationTable or nil` | If successful, a locationTable as described in the module... | This function activates Location Services for Hammerspoon, so the first time ... |
| `start` | `hs.location.start() -> boolean` | True if the operation succeeded, otherwise false | This function activates Location Services for Hammerspoon, so the first time ... |
| `startTracking` | `hs.location:startTracking() -> locationObject` | the locationObject | This function activates Location Services for Hammerspoon, so the first time ... |
| `stop` | `hs.location.stop()` | None |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.location.new(...)
```

```

```
hs.logger.md
# hs.logger

Simple logger for debugging purposes

## Key Exports

- `new`
- `getLogLevel`
- `setGlobalLogLevel`
- `setModulesLogLevel`
- `setLogLevel`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.logger.new(id, loglevel) -> logger` | the new logger instance | the logger instance created by this method is not a regular object, but a pla... |
| `getLogLevel` | `hs.logger.getLogLevel() -> number` | The log level of this logger as a number between 0 and 5 |  |
| `setGlobalLogLevel` | `hs.logger.setGlobalLogLevel(lvl)` | None |  |
| `setModulesLogLevel` | `hs.logger.setModulesLogLevel(lvl)` | None | This function only affects _module_ -level loggers, object instances with the... |
| `setLogLevel` | `hs.logger.setLogLevel(loglevel)` | None |  |

## Common Patterns


```

```
hs.math.md
# hs.math

Various helpful mathematical functions

## Key Exports

- `isFinite`
- `isInfinite`
- `isNaN`
- `randomFloat`
- `randomFromRange`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `isFinite` | `hs.math.isFinite(value) -> boolean` | true if the value is a finite number, or false otherwise | This function returns true if the value is a number and both hs.math.isNaN an... |
| `isInfinite` | `hs.math.isInfinite(value) -> 1, -1, false` | 1 if the value is equivalent to positive infinity, -1 if ... | This function specifically checks if the `value` is equivalent to positive or... |
| `isNaN` | `hs.math.isNaN(value) -> boolean` | true if `value` is equal to the mathematical "value" of N... | Mathematical `NaN` represents an impossible value, usually the result of a ca... |
| `randomFloat` | `hs.math.randomFloat() -> number` | A random number between 0 and 1 |  |
| `randomFromRange` | `hs.math.randomFromRange(start, end) -> integer` | A randomly chosen integer between `start` and `end` |  |

## Common Patterns


```

```
hs.md
# 

Core Hammerspoon functionality

## Key Exports

- `getObjectMetatable`
- `showError`
- `open`
- `openAbout`
- `openConsole`
- `openConsoleOnDockClick`
- `openPreferences`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getObjectMetatable` | `hs.getObjectMetatable(name) -> table or nil` | The extension's object metatable, or nil if an error occu... |  |
| `showError` | `hs.showError(err)` | None | This function is called whenever an (uncaught) error occurs or is thrown (via... |
| `open` | `hs.open(filePath)` | A boolean, true if the file was opened successfully, othe... |  |
| `openAbout` | `hs.openAbout()` | None |  |
| `openConsole` | `hs.openConsole([bringToFront])` | None |  |
| `openConsoleOnDockClick` | `hs.openConsoleOnDockClick([state]) -> bool` | A boolean, true if the console window will open when the ... | This only refers to dock icon clicks while Hammerspoon is already running. Th... |
| `openPreferences` | `hs.openPreferences()` | None |  |

## Common Patterns


```

```
hs.menubar.md
# hs.menubar

Create and manage menubar icons

## Key Exports

- `new`
- `setClickCallback`
- `setIcon`
- `setMenu`
- `setTitle`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.menubar.new([inMenuBar], [autosaveName]) -> ...` | menubar item object to use with other API methods, or nil... | You should call hs.menubar:setTitle() or hs.menubar:setIcon() after creating ... |
| `setClickCallback` | `hs.menubar:setClickCallback([fn]) -> menubaritem` | the menubaritem | If a menu has been attached to the menubar item, this callback will never be ... |
| `setIcon` | `hs.menubar:setIcon(imageData[, template]) -> me...` | the menubaritem if the image was loaded and set, `nil` if... | ** API Change ** |
| `setMenu` | `hs.menubar:setMenu(menuTable) -> menubaritem` | the menubaritem | If you are using the callback function, you should take care not to take too ... |
| `setTitle` | `hs.menubar:setTitle(title) -> menubaritem` | the menubar item | If you set an icon as well as a title, they will both be displayed next to ea... |

## Common Patterns

```lua
-- Create instance
local obj = hs.menubar.new(...)
```

```

```
hs.messages.md
# hs.messages

Send messages via iMessage and SMS Relay (note, SMS Relay requires OS X 10.10 and an established SMS Relay pairing between your Mac and an iPhone running iOS8)

## Key Exports

- `iMessage`
- `SMS`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `iMessage` | `hs.messages.iMessage(targetAddress, message)` | None |  |
| `SMS` | `hs.messages.SMS(targetNumber, message)` | None |  |

## Common Patterns


```

```
hs.midi.md
# hs.midi

MIDI Extension for Hammerspoon.

## Key Exports

- `new`
- `newVirtualSource`
- `deviceCallback`
- `devices`
- `virtualSources`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.midi.new(deviceName) ->` | An `hs.midi` object or `nil` if an error occurred. | Example Usage: `hs.midi.new(hs.midi.devices()[1])` |
| `newVirtualSource` | `hs.midi.newVirtualSource(virtualSource) ->` | An `hs.midi` object or `nil` if an error occurred. | Example Usage: `hs.midi.newVirtualSource(hs.midi.virtualSources()[1])` |
| `deviceCallback` | `hs.midi.deviceCallback(callbackFn) -> none` | None | The callback function should expect 2 argument and should not return anything: |
| `devices` | `hs.midi.devices() -> table` | A table containing the names of any physically connected ... |  |
| `virtualSources` | `hs.midi.virtualSources() -> table` | A table containing the names of any virtual MIDI sources ... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.midi.new(...)
```

```

```
hs.milight.md
# hs.milight

Simple controls for the MiLight LED WiFi bridge (also known as LimitlessLED and EasyBulb)

## Key Exports

- `new`
- `delete`
- `disco`
- `send`
- `zoneBrightness`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.milight.new(ip[, port]) -> bridge` | An `hs.milight` object | You can not use 255.255.255.255 as the IP address, to do so requires elevated... |
| `delete` | `hs.milight:delete()` | None |  |
| `disco` | `hs.milight:disco() -> bool` | True if the command was sent correctly, otherwise false |  |
| `send` | `hs.milight:send(cmd[, value]) -> bool` | True if the command was sent, otherwise false | This is a low level command, you typically should use a specific method for t... |
| `zoneBrightness` | `hs.milight:zoneBrightness(zone, value) -> integer` | A number containing the value that was sent to the WiFi b... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.milight.new(...)
```

```

```
hs.mjomatic.md
# hs.mjomatic

tmuxomatic-like window management

## Key Exports

- `go`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `go` | `hs.mjomatic.go(cfg)` | None | An example use: |

## Common Patterns


```

```
hs.mouse.md
# hs.mouse

Inspect/manipulate the position of the mouse pointer

## Key Exports

- `getButtons`
- `getCurrentScreen`
- `getRelativePosition`
- `setRelativePosition`
- `absolutePosition`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getButtons` | `hs.mouse.getButtons() -> table` | Returns an array containing indices starting from 1 up to... | This function is a wrapper to `hs.eventtap.checkMouseButtons` |
| `getCurrentScreen` | `hs.mouse.getCurrentScreen() -> screen or nil` | An `hs.screen` object that the mouse pointer is on, or ni... |  |
| `getRelativePosition` | `hs.mouse.getRelativePosition() -> point or nil` | A point-table containing the relative x and y co-ordinate... | The co-ordinates returned by this function are relative to the top left pixel... |
| `setRelativePosition` | `hs.mouse.setRelativePosition(point[, screen])` | None |  |
| `absolutePosition` | `hs.mouse.absolutePosition([point]) -> point` | A point table containing the absolute x and y co-ordinate... | If no parameters are supplied, the current position will be returned. If a po... |

## Common Patterns


```

```
hs.network.configuration.md
# hs.network.configuration

This sub-module provides access to the current location set configuration settings in the system's dynamic store.

## Key Exports

- `setCallback`
- `setLocation`
- `start`
- `stop`
- `open`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setCallback` | `hs.network.configuration:setCallback(function) ...` | the store object | The callback function will be invoked each time a monitored key changes value... |
| `setLocation` | `hs.network.configuration:setLocation(location) ...` | bool - true if the location was successfully changed, fal... |  |
| `start` | `hs.network.configuration:start() -> storeObject` | the store object | The callback function should be specified with hs.network.configuration:setCa... |
| `stop` | `hs.network.configuration:stop() -> storeObject` | the store object |  |
| `open` | `hs.network.configuration.open() -> storeObject` | the storeObject |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.configuration.open(...)
```

```

```
hs.network.host.md
# hs.network.host

This sub-module provides functions for acquiring host information, such as hostnames, addresses, and reachability.

## Key Exports

- `addressesForHostname`
- `hostnamesForAddress`
- `reachabilityForAddress`
- `reachabilityForHostname`
- `cancel`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `addressesForHostname` | `hs.network.host.addressesForHostname(name[, fn]...` | If this function is called without a callback function, r... | If no callback function is provided, the resolution occurs in a blocking mann... |
| `hostnamesForAddress` | `hs.network.host.hostnamesForAddress(address[, f...` | If this function is called without a callback function, r... | If no callback function is provided, the resolution occurs in a blocking mann... |
| `reachabilityForAddress` | `hs.network.host.reachabilityForAddress(address[...` | If this function is called without a callback function, r... | If no callback function is provided, the resolution occurs in a blocking mann... |
| `reachabilityForHostname` | `hs.network.host.reachabilityForHostname(name[, ...` | If this function is called without a callback function, r... | If no callback function is provided, the resolution occurs in a blocking mann... |
| `cancel` | `hs.network.host:cancel() -> hostObject` | the hostObject | This method has no effect if the resolution has already completed. |

## Common Patterns


```

```
hs.network.md
# hs.network

This module provides functions for inquiring about and monitoring changes to the network.

## Key Exports

- `addresses`
- `interfaceDetails`
- `interfaceName`
- `interfaces`
- `primaryInterfaces`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `addresses` | `hs.network.addresses([interface_list]) -> table` | A table containing a list of the IP addresses for the int... | The order of the IP addresses returned is undefined. |
| `interfaceDetails` | `hs.network.interfaceDetails([interface \| favor...` | A table containing key-value pairs describing interface d... | When determining the primary interface, the `favorIPv6` flag only determines ... |
| `interfaceName` | `hs.network.interfaceName([interface \| favorIPv...` | A string containing the user defined name for the interfa... | Only interfaces which show up in the System Preferences Network panel will ha... |
| `interfaces` | `hs.network.interfaces() -> table` | A table containing a list of the interfaces active for th... | The names of the interfaces returned by this function correspond to the inter... |
| `primaryInterfaces` | `hs.network.primaryInterfaces() -> ipv4Interface...` | The name of the primary IPv4 interface or false if there ... | The IPv4 and IPv6 interface names are often, but not always, the same. |

## Common Patterns


```

```
hs.network.ping.echoRequest.md
# hs.network.ping.echoRequest

Provides lower-level access to the ICMP Echo Request infrastructure used by the hs.network.ping module. In general, you should not need to use this module directly unless you have specific requirements not met by the hs.network.ping module and the `hs.network.ping` object methods.

## Key Exports

- `setCallback`
- `start`
- `stop`
- `echoRequest`
- `acceptAddressFamily`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setCallback` | `hs.network.ping.echoRequest:setCallback(fn) -> ...` | the echoRequestObject | The callback function should expect between 3 and 5 arguments and return none... |
| `start` | `hs.network.ping.echoRequest:start() -> echoRequ...` | the echoRequestObject |  |
| `stop` | `hs.network.ping.echoRequest:stop() -> echoReque...` | the echoRequestObject |  |
| `echoRequest` | `hs.network.ping.echoRequest.echoRequest(server)...` | an echoRequest object | This constructor returns a lower-level object than the `hs.network.ping.ping`... |
| `acceptAddressFamily` | `hs.network.ping.echoRequest:acceptAddressFamily...` | if an argument is provided, returns the echoRequestObject... | Setting this value to "IPv6" or "IPv4" will cause the echoRequestObject to at... |

## Common Patterns

```lua
-- Create instance
local obj = hs.echoRequest.echoRequest(...)
```

```

```
hs.network.ping.md
# hs.network.ping

This module provides a basic ping function which can test host availability. Ping is a network diagnostic tool commonly found in most operating systems which can be used to test if a route to a specified host exists and if that host is responding to network traffic.

## Key Exports

- `setCallback`
- `ping`
- `address`
- `cancel`
- `count`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setCallback` | `hs.network.ping:setCallback(fn) -> pingObject` | the pingObject | Because the ping process begins immediately upon creation with the hs.network... |
| `ping` | `hs.network.ping.ping(server, [count], [interval...` | a pingObject | For convenience, you can call this constructor as `hs.network.ping(server, ...)` |
| `address` | `hs.network.ping:address() -> string` | A string containing the IPv4 or IPv6 address this pingObj... |  |
| `cancel` | `hs.network.ping:cancel() -> none` | None | the `didFinish` message will be sent to the callback function as its final me... |
| `count` | `hs.network.ping:count([count]) -> integer \| pi...` | if no argument is specified, returns the current number o... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.ping.ping(...)
```

```

```
hs.network.reachability.md
# hs.network.reachability

This sub-module can be used to determine the reachability of a target host. A remote host is considered reachable when a data packet, sent by an application into the network stack, can leave the local device. Reachability does not guarantee that the data packet will actually be received by the host.

## Key Exports

- `setCallback`
- `start`
- `stop`
- `forAddress`
- `forAddressPair`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setCallback` | `hs.network.reachability:setCallback(function) -...` | the reachability object | The callback function will be invoked each time the status for the given reac... |
| `start` | `hs.network.reachability:start() -> reachability...` | the reachability object | The callback function should be specified with hs.network.reachability:setCal... |
| `stop` | `hs.network.reachability:stop() -> reachabilityO...` | the reachability object |  |
| `forAddress` | `hs.network.reachability.forAddress(address) -> ...` | a reachability object for the specified network address. | this object will reflect reachability status for any interface available on t... |
| `forAddressPair` | `hs.network.reachability.forAddressPair(localAdd...` | a reachability object for the specified network address. | this object will reflect reachability status for a specific interface on the ... |

## Common Patterns

```lua
-- Create instance
local obj = hs.reachability.forAddress(...)
```

```

```
hs.noises.md
# hs.noises

Contains two low latency audio recognizers for different mouth noises, which can be used to trigger actions like scrolling or clicking. The recognizers are also high accuracy and don't use much CPU time.

## Key Exports

- `new`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.noises.new(fn) -> listener` | An `hs.noises` object |  |
| `start` | `hs.noises:start() -> self` | The `hs.noises` object |  |
| `stop` | `hs.noises:stop() -> self` | The `hs.noises` object |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.noises.new(...)
```

```

```
hs.notify.md
# hs.notify

This module allows you to create on screen notifications in the User Notification Center located at the right of the users screen.

## Key Exports

- `new`
- `getFunctionTag`
- `setIdImage`
- `show`
- `deliveredNotifications`
- `register`
- `scheduledNotifications`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.notify.new([fn,][attributes]) -> notification` | A notification object | A function-tag is a string key which corresponds to a function stored in the ... |
| `getFunctionTag` | `hs.notify:getFunctionTag() -> functiontag` | The function tag for this notification as a string. | This tag should correspond to a function in hs.notify.registry and can be use... |
| `setIdImage` | `hs.notify:setIdImage(image[, withBorder]) -> no...` | The notification object | See hs.image for details on how to specify or define an image |
| `show` | `hs.notify.show(title, subTitle, information[, t...` | a notification object | All three textual parameters are required, though they can be empty strings |
| `deliveredNotifications` | `hs.notify.deliveredNotifications() -> table` | a table containing the notification userdata objects for ... | Only notifications which have been presented but not cleared, either by the u... |
| `register` | `hs.notify.register(tag, fn) -> id` | a numerical id representing the entry in hs.notify.regist... | If a function is already registered with the specified tag, it is replaced by... |
| `scheduledNotifications` | `hs.notify.scheduledNotifications() -> table` | a table containing the notification userdata objects for ... | Once a notification has been delivered, it is moved to hs.notify.deliveredNot... |

## Common Patterns

```lua
-- Create instance
local obj = hs.notify.new(...)
```

```

```
hs.osascript.md
# hs.osascript

Execute Open Scripting Architecture (OSA) code - AppleScript and JavaScript

## Key Exports

- `_osascript`
- `applescript`
- `applescriptFromFile`
- `javascript`
- `javascriptFromFile`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `_osascript` | `hs.osascript._osascript(source, language) -> bo...` | A boolean value indicating whether the code succeeded or not |  |
| `applescript` | `hs.osascript.applescript(source) -> bool, objec...` | A boolean value indicating whether the code succeeded or not | Use hs.osascript._osascript(source, "AppleScript") if you always want the res... |
| `applescriptFromFile` | `hs.osascript.applescriptFromFile(fileName) -> b...` | A boolean value indicating whether the code succeeded or not | This function uses hs.osascript.applescript for execution. |
| `javascript` | `hs.osascript.javascript(source) -> bool, object...` | A boolean value indicating whether the code succeeded or not | Use hs.osascript._osascript(source, "JavaScript") if you always want the resu... |
| `javascriptFromFile` | `hs.osascript.javascriptFromFile(fileName) -> bo...` | A boolean value indicating whether the code succeeded or not | This function uses hs.osascript.javascript for execution. |

## Common Patterns


```

```
hs.pasteboard.md
# hs.pasteboard

Inspect/manipulate pasteboards (more commonly called clipboards). Both the system default pasteboard and custom named pasteboards can be interacted with.

## Key Exports

- `getContents`
- `setContents`
- `deletePasteboard`
- `allContentTypes`
- `callbackWhenChanged`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getContents` | `hs.pasteboard.getContents([name]) -> string or nil` | A string containing the contents of the pasteboard, or ni... |  |
| `setContents` | `hs.pasteboard.setContents(contents[, name]) -> ...` | True if the operation succeeded, otherwise false |  |
| `deletePasteboard` | `hs.pasteboard.deletePasteboard(name)` | None | You can not delete the system pasteboard, this function should only be called... |
| `allContentTypes` | `hs.pasteboard.allContentTypes([name]) -> table` | an array with each index representing an object on the pa... |  |
| `callbackWhenChanged` | `hs.pasteboard.callbackWhenChanged([name], [time...` | None | This function can be used to capture the results of a copy operation issued p... |

## Common Patterns


```

```
hs.pasteboard.watcher.md
# hs.pasteboard.watcher

Watch for Pasteboard Changes. macOS doesn't offer any API for getting Pasteboard notifications, so this extension uses polling to check for Pasteboard changes at a chosen interval (defaults to 0.25).

## Key Exports

- `new`
- `start`
- `stop`
- `interval`
- `running`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.pasteboard.watcher.new(callbackFn[, name]) -...` | An `hs.pasteboard.watcher` object | Internally this extension uses a single `NSTimer` to check for changes to the... |
| `start` | `hs.pasteboard.watcher:start() -> timer` | The `hs.pasteboard.watcher` object |  |
| `stop` | `hs.pasteboard.watcher:stop() -> timer` | The `hs.pasteboard.watcher` object |  |
| `interval` | `hs.pasteboard.watcher.interval([value]) -> number` | The polling interval as a number. | This only affects new watchers, not existing/running ones. |
| `running` | `hs.pasteboard.watcher:running() -> boolean` | A boolean value indicating whether or not the timer is cu... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.watcher.new(...)
```

```

```
hs.pathwatcher.md
# hs.pathwatcher

Watch paths recursively for changes

## Key Exports

- `new`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.pathwatcher.new(path, fn) -> watcher` | An `hs.pathwatcher` object | For more information about the event flags, see the official documentation |
| `start` | `hs.pathwatcher:start()` | The `hs.pathwatcher` object |  |
| `stop` | `hs.pathwatcher:stop()` | None |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.pathwatcher.new(...)
```

```

```
hs.plist.md
# hs.plist

Read and write Property List files

## Key Exports

- `read`
- `readString`
- `write`
- `writeString`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `read` | `hs.plist.read(filepath) -> table` | The contents of the plist as a Lua table |  |
| `readString` | `hs.plist.readString(value, [binary]) -> table \...` | The contents of the property list as a Lua table or `nil`... |  |
| `write` | `hs.plist.write(filepath, data[, binary]) -> boo...` | A boolean, true if the plist was written successfully, ot... | Only simple types can be converted to plist items: |
| `writeString` | `hs.plist.writeString(data, [binary]) -> string ...` | A string representing the data as a plist or nil if there... |  |

## Common Patterns


```

```
hs.razer.md
# hs.razer

Razer device support.

## Key Exports

- `getDevice`
- `discoveryCallback`
- `init`
- `numDevices`
- `unitTests`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getDevice` | `hs.razer.getDevice(num) -> razerObject \| nil` | An hs.razer object or `nil` if something goes wrong |  |
| `discoveryCallback` | `hs.razer.discoveryCallback(fn) -> none` | None |  |
| `init` | `hs.razer.init(fn)` | None | This function must be called before any other parts of this module are used |
| `numDevices` | `hs.razer.numDevices() -> number` | A number containing the number of Razer devices attached ... |  |
| `unitTests` | `hs.razer.unitTests() -> none` | None | Because `hs.razer` relies on a physical device to be connected for testing, t... |

## Common Patterns


```

```
hs.redshift.md
# hs.redshift

Inverts and/or lowers the color temperature of the screen(s) on a schedule, for a more pleasant experience at night

## Key Exports

- `start`
- `stop`
- `invertSubscribe`
- `invertUnsubscribe`
- `isInverted`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `start` | `hs.redshift.start(colorTemp,nightStart,nightEnd...` | None |  |
| `stop` | `hs.redshift.stop()` | None |  |
| `invertSubscribe` | `hs.redshift.invertSubscribe([id,]fn)` | None | You can use this to dynamically adjust the UI colors in your modules or confi... |
| `invertUnsubscribe` | `hs.redshift.invertUnsubscribe(id)` | None |  |
| `isInverted` | `hs.redshift.isInverted() -> string or false` | false if the colors are not currently inverted; otherwise... |  |

## Common Patterns


```

```
hs.screen.md
# hs.screen

Manipulate screens (i.e. monitors)

## Key Exports

- `getBrightness`
- `getForceToGray`
- `getGamma`
- `getInfo`
- `getInvertedPolarity`
- `getUUID`
- `setBrightness`
- `setForceToGray`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getBrightness` | `hs.screen:getBrightness() -> number or nil` | A floating point number between 0 and 1, containing the c... |  |
| `getForceToGray` | `hs.screen.getForceToGray() -> boolean` | A boolean, true if the ForceToGray mode is set, otherwise... |  |
| `getGamma` | `hs.screen:getGamma() -> [whitepoint, blackpoint...` | A table containing the white point and black point of the... |  |
| `getInfo` | `hs.screen:getInfo() -> table or nil` | A table containing various information, or nil if an erro... |  |
| `getInvertedPolarity` | `hs.screen.getInvertedPolarity() -> boolean` | A boolean, true if the InvertedPolarity mode is set, othe... |  |
| `getUUID` | `hs.screen:getUUID() -> string` | A string containing the UUID, or nil if an error occurred. |  |
| `setBrightness` | `hs.screen:setBrightness(brightness) ->` | The `hs.screen` object |  |
| `setForceToGray` | `hs.screen.setForceToGray(ForceToGray) -> None` | None |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.screen.allScreens(...)
```

```

```
hs.screen.watcher.md
# hs.screen.watcher

Watch for screen layout changes This could be the addition or removal of a monitor, a screen resolution change, movement of a monitor in the Display preferences pane, etc.

## Key Exports

- `new`
- `newWithActiveScreen`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.screen.watcher.new(fn) -> watcher` | An `hs.screen.watcher` object | A screen layout change usually involves a change that is made from the Displa... |
| `newWithActiveScreen` | `hs.screen.watcher.newWithActiveScreen(fn) -> wa...` | An `hs.screen.watcher` object | A screen layout change usually involves a change that is made from the Displa... |
| `start` | `hs.screen.watcher:start() -> watcher` | The `hs.screen.watcher` object |  |
| `stop` | `hs.screen.watcher:stop() -> watcher` | The `hs.screen.watcher` object |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.watcher.new(...)
```

```

```
hs.serial.md
# hs.serial

Communicate with external devices through a serial port (most commonly RS-232).

## Key Exports

- `newFromName`
- `newFromPath`
- `stopBits`
- `open`
- `close`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `newFromName` | `hs.serial.newFromName(portName) -> serialPortOb...` | An `hs.serial` object or `nil` if an error occurred. | A valid port name can be found by checking `hs.serial.availablePortNames()`. |
| `newFromPath` | `hs.serial.newFromPath(path) -> serialPortObject` | An `hs.serial` object or `nil` if an error occurred. | A valid port name can be found by checking `hs.serial.availablePortPaths()`. |
| `stopBits` | `hs.serial:stopBits([value]) -> number \| serial...` | If a value is specified, then this method returns the ser... | The default value is 1. |
| `open` | `hs.serial:open() -> serialPortObject \| nil` | The `hs.serial` object or `nil` if the port could not be ... |  |
| `close` | `hs.serial:close() -> serialPortObject` | The `hs.serial` object. |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.serial.newFromName(...)
```

```

```
hs.settings.md
# hs.settings

Serialize simple Lua variables across Hammerspoon launches Settings must have a string key and must be made up of serializable Lua objects (string, number, boolean, nil, tables of such, etc.)

## Key Exports

- `get`
- `getKeys`
- `set`
- `setData`
- `setDate`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.settings.get(key) -> string or boolean or nu...` | The value of the setting | This function can load all of the datatypes supported by `hs.settings.set()`,... |
| `getKeys` | `hs.settings.getKeys() -> table` | A table containing all of the settings keys in Hammerspoo... | Use `ipairs(hs.settings.getKeys())` to iterate over all available settings |
| `set` | `hs.settings.set(key[, val])` | None | If no val parameter is provided, it is assumed to be nil |
| `setData` | `hs.settings.setData(key, val)` | None |  |
| `setDate` | `hs.settings.setDate(key, val)` | None | See `hs.settings.dateFormat` for a convenient representation of the RFC3339 f... |

## Common Patterns


```

```
hs.sharing.md
# hs.sharing

Share items with the macOS Sharing Services under the control of Hammerspoon.

## Key Exports

- `newShare`
- `fileURL`
- `shareTypesFor`
- `URL`
- `accountName`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `newShare` | `hs.sharing.newShare(type) -> sharingObject` | a sharingObject or nil if the type identifier cannot be c... |  |
| `fileURL` | `hs.sharing.fileURL(path) -> table` | a table containing the necessary labels for converting th... | this function is a wrapper to hs.sharing.URL which sets the second argument t... |
| `shareTypesFor` | `hs.sharing.shareTypesFor(items) -> identifiersT...` | an array (table) containing strings which identify sharin... | this function is intended to be used to determine the identifiers for sharing... |
| `URL` | `hs.sharing.URL(URL, [fileURL]) -> table` | a table containing the necessary labels for representing ... | If the URL is specified as a table, it is expected to contain a `url` key wit... |
| `accountName` | `hs.sharing:accountName() -> string \| nil` | a string containing the account name used by the sharing ... | According to the Apple API documentation, only the Twitter and Sina Weibo sha... |

## Common Patterns

```lua
-- Create instance
local obj = hs.sharing.newShare(...)
```

```

```
hs.shortcuts.md
# hs.shortcuts

List and run shortcuts from the Shortcuts app

## Key Exports

- `list`
- `run`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `list` | `hs.shortcuts.list() -> []` | A table of shortcuts, each being a table with the followi... |  |
| `run` | `hs.shortcuts.run(name)` | None |  |

## Common Patterns


```

```
hs.socket.md
# hs.socket

Talk to custom protocols using asynchronous TCP sockets.

## Key Exports

- `new`
- `setCallback`
- `setTimeout`
- `startTLS`
- `server`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.socket.new([fn]) -> hs.socket object` | An `hs.socket` object. |  |
| `setCallback` | `hs.socket:setCallback([fn]) -> self` | The `hs.socket` object. | A callback must be set in order to read data from the socket. |
| `setTimeout` | `hs.socket:setTimeout(timeout) -> self` | The `hs.socket` object. | If the timeout value is negative, the operations will not use a timeout, whic... |
| `startTLS` | `hs.socket:startTLS([verify][, peerName]) -> self` | The `hs.socket` object. | The socket will disconnect immediately if TLS negotiation fails. |
| `server` | `hs.socket.server(port \| path [, fn]) -> hs.soc...` | An `hs.socket` object. |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.socket.new(...)
```

```

```
hs.socket.udp.md
# hs.socket.udp

Talk to custom protocols using asynchronous UDP sockets.

## Key Exports

- `new`
- `setBufferSize`
- `setCallback`
- `setTimeout`
- `enableIPv`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.socket.udp.new([fn]) -> hs.socket.udp object` | An `hs.socket.udp` object. |  |
| `setBufferSize` | `hs.socket.udp:setBufferSize(size[, version]) ->...` | The `hs.socket.udp` object. | The default maximum size is 9216 bytes. |
| `setCallback` | `hs.socket.udp:setCallback([fn]) -> self` | The `hs.socket.udp` object. | A callback must be set in order to read data from the socket. |
| `setTimeout` | `hs.socket.udp:setTimeout(timeout) -> self` | The `hs.socket.udp` object. | If the timeout value is negative, the operations will not use a timeout, whic... |
| `enableIPv` | `hs.socket.udp:enableIPv(version[, flag]) -> sel...` | The `hs.socket.udp` object, or `nil` if an error occurred. | Must be called before binding the socket. If you want to create an IPv6-only ... |

## Common Patterns

```lua
-- Create instance
local obj = hs.udp.new(...)
```

```

```
hs.sound.md
# hs.sound

Load/play/manipulate sound files

## Key Exports

- `getByFile`
- `getByName`
- `getAudioEffectNames`
- `setCallback`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getByFile` | `hs.sound.getByFile(path) -> sound or nil` | An `hs.sound` object or nil if the file could not be loaded |  |
| `getByName` | `hs.sound.getByName(name) -> sound or nil` | An `hs.sound` object or nil if no matching sound could be... | Sounds can only be loaded by name if they are System Sounds (i.e. those found... |
| `getAudioEffectNames` | `hs.sound.getAudioEffectNames() -> table` | A table containing the names of all installed Audio Units... | Example usage: `hs.inspect(hs.audiounit.getAudioEffectNames())` |
| `setCallback` | `hs.sound:setCallback(function) -> soundObject` | the sound object | the callback function should accept two parameters and return none. The param... |
| `stop` | `hs.sound:stop() -> soundObject \| bool` | The `hs.sound` object if the command was successful, othe... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.sound.getByFile(...)
```

```

```
hs.spaces.md
# hs.spaces

This module provides some basic functions for controlling macOS Spaces.

## Key Exports

- `setDefaultMCwaitTime`
- `openMissionControl`
- `closeMissionControl`
- `activeSpaceOnScreen`
- `activeSpaces`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setDefaultMCwaitTime` | `hs.spaces.setDefaultMCwaitTime([time]) -> None` | None | this function uses the `hs.settings` module to store the default time in the ... |
| `openMissionControl` | `hs.spaces.openMissionControl() -> None` | None | Does nothing if the Mission Control display is already visible. |
| `closeMissionControl` | `hs.spaces.closeMissionControl() -> None` | None | Does nothing if the Mission Control display is not currently visible. |
| `activeSpaceOnScreen` | `hs.spaces.activeSpaceOnScreen([screen]) -> inte...` | an integer specifying the ID of the space displayed, or n... |  |
| `activeSpaces` | `hs.spaces.activeSpaces() -> table \| nil, error` | a key-value table in which the keys are the UUIDs for the... | the table returned has its __tostring metamethod set to `hs.inspect` to simpl... |

## Common Patterns


```

```
hs.spaces.watcher.md
# hs.spaces.watcher

Watches for the current Space being changed NOTE: This extension determines the number of a Space, using OS X APIs that have been deprecated since 10.8 and will likely be removed in a future release. You should not depend on Space numbers being around forever!

## Key Exports

- `new`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.spaces.watcher.new(handler) -> watcher` | An `hs.spaces.watcher` object |  |
| `start` | `hs.spaces.watcher:start()` | The watcher object |  |
| `stop` | `hs.spaces.watcher:stop()` | The watcher object |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.watcher.new(...)
```

```

```
hs.speech.listener.md
# hs.speech.listener

This module provides access to the Speech Recognizer component of OS X.

## Key Exports

- `new`
- `setCallback`
- `start`
- `stop`
- `delete`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.speech.listener.new([title]) -> recognizerOb...` | a speech recognizer object or nil, if the system was unab... | You can change the title later with the `hs.speech.listener:title` method. |
| `setCallback` | `hs.speech.listener:setCallback(fn) -> recognize...` | the recognizer object | Possible string values for the command spoken are set with the `hs.speech.lis... |
| `start` | `hs.speech.listener:start() -> recognizerObject` | returns the recognizer object. |  |
| `stop` | `hs.speech.listener:stop() -> recognizerObject` | returns the recognizer object. | this only disables the speech recognizer. To completely remove it from the li... |
| `delete` | `hs.speech.listener:delete() -> recognizerObject` | None | this disables the speech recognizer and removes it from the list in the Dicta... |

## Common Patterns

```lua
-- Create instance
local obj = hs.listener.new(...)
```

```

```
hs.speech.md
# hs.speech

This module provides access to the Speech Synthesizer component of OS X.

## Key Exports

- `new`
- `setCallback`
- `stop`
- `attributesForVoice`
- `availableVoices`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.speech.new([voice]) -> synthesizerObject` | a speech synthesizer object or nil, if the system was una... | All of the names that have been encountered thus far follow this pattern for ... |
| `setCallback` | `hs.speech:setCallback(fn) -> synthesizerObject` | the synthesizer object | The callback function should expect between 3 and 5 arguments and should not ... |
| `stop` | `hs.speech:stop([where]) -> synthesizerObject` | the synthesizer object |  |
| `attributesForVoice` | `hs.speech.attributesForVoice(voice) -> table` | a table containing key-value pairs which describe the voi... | All of the names that have been encountered thus far follow this pattern for ... |
| `availableVoices` | `hs.speech.availableVoices([full]) -> array` | an array of the available voice names. | All of the names that have been encountered thus far follow this pattern for ... |

## Common Patterns

```lua
-- Create instance
local obj = hs.speech.new(...)
```

```

```
hs.spoons.md
# hs.spoons

Utility and management functions for Spoons Spoons are Lua plugins for Hammerspoon. See https://www.hammerspoon.org/Spoons/ for more information

## Key Exports

- `newSpoon`
- `bindHotkeysToSpec`
- `isInstalled`
- `isLoaded`
- `list`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `newSpoon` | `hs.spoons.newSpoon(name, basedir, metadata, [te...` | The full directory path where the template was created, o... |  |
| `bindHotkeysToSpec` | `hs.spoons.bindHotkeysToSpec(def, map) -> none` | None |  |
| `isInstalled` | `hs.spoons.isInstalled(name) -> table \| nil` | If the Spoon is installed, it returns a table with the Sp... |  |
| `isLoaded` | `hs.spoons.isLoaded(name) -> boolean \| nil` | `true` if the Spoon is loaded, `nil` otherwise. |  |
| `list` | `hs.spoons.list() -> table` | Table with a list of installed/loaded spoons (depending o... |  |

## Common Patterns


```

```
hs.spotify.md
# hs.spotify

Controls for Spotify music player

## Key Exports

- `getCurrentAlbum`
- `getCurrentArtist`
- `getCurrentTrack`
- `getCurrentTrackArtworkURL`
- `getCurrentTrackId`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getCurrentAlbum` | `hs.spotify.getCurrentAlbum()` | A string containing the Album of the current track, or ni... |  |
| `getCurrentArtist` | `hs.spotify.getCurrentArtist()` | A string containing the Artist of the current track, or n... |  |
| `getCurrentTrack` | `hs.spotify.getCurrentTrack()` | A string containing the name of the current track, or nil... |  |
| `getCurrentTrackArtworkURL` | `hs.spotify.getCurrentTrackArtworkURL()` | A string containing the URL of the artwork for the curren... |  |
| `getCurrentTrackId` | `hs.spotify.getCurrentTrackId()` | A string containing the id of the current track, or nil i... |  |

## Common Patterns


```

```
hs.spotlight.group.md
# hs.spotlight.group

This sub-module is used to access results to a spotlightObject query which have been grouped by one or more attribute values.

## Key Exports

- `attribute`
- `count`
- `resultAtIndex`
- `subgroups`
- `value`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `attribute` | `hs.spotlight.group:attribute() -> string` | the attribute name as a string |  |
| `count` | `hs.spotlight.group:count() -> integer` | an integer specifying the number of results that match th... | For convenience, metamethods have been added to the spotlightGroupObject whic... |
| `resultAtIndex` | `hs.spotlight.group:resultAtIndex(index) -> spot...` | the spotlightItemObject at the specified index or an erro... | For convenience, metamethods have been added to the spotlightGroupObject whic... |
| `subgroups` | `hs.spotlight.group:subgroups() -> table` | an array table containing the subgroups of the spotlightG... | Subgroups are created when you supply more than one grouping attribute to `hs... |
| `value` | `hs.spotlight.group:value() -> value` | the attribute value as an appropriate data type |  |

## Common Patterns


```

```
hs.spotlight.item.md
# hs.spotlight.item

This sub-module is used to access the individual results of a spotlightObject or a spotlightGroupObject.

## Key Exports

- `attributes`
- `valueForAttribute`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `attributes` | `hs.spotlight.item:attributes() -> table` | an array table containing a list of attributes associated... | This list of attributes is usually not a complete list of the attributes avai... |
| `valueForAttribute` | `hs.spotlight.item:valueForAttribute(attribute) ...` | the attribute value as an appropriate data type or nil if... | See hs.spotlight.item:attributes for information about possible attribute names. |

## Common Patterns


```

```
hs.spotlight.md
# hs.spotlight

This module allows Hammerspoon to preform Spotlight metadata queries.

## Key Exports

- `new`
- `newWithin`
- `setCallback`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.spotlight.new() -> spotlightObject` | a new spotlightObject |  |
| `newWithin` | `hs.spotlight.newWithin(spotlightObject) -> spot...` | a new spotlightObject |  |
| `setCallback` | `hs.spotlight:setCallback(fn) -> spotlightObject` | the spotlightObject | Depending upon the messages set with the hs.spotlight:callbackMessages method... |
| `start` | `hs.spotlight:start() -> spotlightObject` | the spotlightObject | If the query string set with hs.spotlight:queryString is invalid, an error me... |
| `stop` | `hs.spotlight:stop() -> spotlightObject` | the spotlightObject | This method will prevent further gathering of items either during the initial... |

## Common Patterns

```lua
-- Create instance
local obj = hs.spotlight.new(...)
```

```

```
hs.sqlite3.md
# hs.sqlite3

Interact with SQLite databases

## Common Patterns


```

```
hs.streamdeck.md
# hs.streamdeck

Configure/control an Elgato Stream Deck.

## Key Exports

- `getDevice`
- `setBrightness`
- `setButtonColor`
- `setButtonImage`
- `setScreenImage`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getDevice` | `hs.streamdeck.getDevice(num)` | An hs.streamdeck object |  |
| `setBrightness` | `hs.streamdeck:setBrightness(brightness)` | The hs.streamdeck device |  |
| `setButtonColor` | `hs.streamdeck:setButtonColor(button, color)` | The hs.streamdeck object |  |
| `setButtonImage` | `hs.streamdeck:setButtonImage(button, image)` | The hs.streamdeck object |  |
| `setScreenImage` | `hs.streamdeck:setScreenImage(encoder, image)` | The hs.streamdeck object |  |

## Common Patterns


```

```
hs.styledtext.md
# hs.styledtext

This module adds support for controlling the style of the text in Hammerspoon.

## Key Exports

- `new`
- `getStyledTextFromData`
- `getStyledTextFromFile`
- `getString`
- `setString`
- `setStyle`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.styledtext.new(string, [attributes]) -> styl...` | an `hs.styledtext` object | See `hs.styledtext:asTable` for a description of the table representation of ... |
| `getStyledTextFromData` | `hs.styledtext.getStyledTextFromData(data, [type...` | the styledText object | See also `hs.styledtext.getStyledTextFromFile` |
| `getStyledTextFromFile` | `hs.styledtext.getStyledTextFromFile(file, [type...` | the styledText object | See also `hs.styledtext.getStyledTextFromData` |
| `getString` | `hs.styledtext:getString([starts], [ends]) -> st...` | a string containing the text of the `hs.styledtext` objec... | `starts` and `ends` follow the conventions of `i` and `j` for Lua's `string.s... |
| `setString` | `hs.styledtext:setString(string, [starts], [ends...` | a copy of the `hs.styledtext` object with the specified s... | `starts` and `ends` follow the conventions of `i` and `j` for Lua's `string.s... |
| `setStyle` | `hs.styledtext:setStyle(attributes, [starts], [e...` | a copy of the `hs.styledtext` object with the attributes ... | `starts` and `ends` follow the conventions of `i` and `j` for Lua's `string.s... |

## Common Patterns

```lua
-- Create instance
local obj = hs.styledtext.ansi(...)
```

```

```
hs.tabs.md
# hs.tabs

Place the windows of an application into tabs drawn on its titlebar

## Key Exports

- `enableForApp`
- `focusTab`
- `tabWindows`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `enableForApp` | `hs.tabs.enableForApp(app)` | None |  |
| `focusTab` | `hs.tabs.focusTab(app, num)` | None | If num is higher than the number of tabs, the last tab will be focussed |
| `tabWindows` | `hs.tabs.tabWindows(app)` | An array of the tabbed windows of an app in the same orde... | This function can be used when writing tab switchers |

## Common Patterns


```

```
hs.tangent.md
# hs.tangent

Tangent Control Surface Extension

## Key Exports

- `setLogLevel`
- `callback`
- `connect`
- `connected`
- `disconnect`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setLogLevel` | `hs.tangent.setLogLevel(loglevel) -> none` | None |  |
| `callback` | `hs.tangent.callback() -> boolean` | `true` if successful otherwise `false` | Full documentation for the Tangent API can be downloaded here. |
| `connect` | `hs.tangent.connect(applicationName, systemPath[...` | success - `true` on success, otherwise `nil` |  |
| `connected` | `hs.tangent.connected() -> boolean` | `true` if connected, otherwise `false` |  |
| `disconnect` | `hs.tangent.disconnect() -> none` | None |  |

## Common Patterns


```

```
hs.task.md
# hs.task

Execute processes in the background and capture their output

## Key Exports

- `new`
- `setCallback`
- `setEnvironment`
- `setInput`
- `setStreamingCallback`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.task.new(launchPath, callbackFn[, streamCall...` | An `hs.task` object | The arguments are not processed via a shell, so you do not need to do any quo... |
| `setCallback` | `hs.task:setCallback(fn) -> hs.task object` | the hs.task object |  |
| `setEnvironment` | `hs.task:setEnvironment(environment) -> hs.task ...` | The hs.task object, or false if the table was not set (us... | If you do not set an environment table with this method, the task will inheri... |
| `setInput` | `hs.task:setInput(inputData) -> hs.task object` | The hs.task object | This method can be called before the task has been started, to prepare some i... |
| `setStreamingCallback` | `hs.task:setStreamingCallback(fn) -> hs.task object` | The hs.task object | For information about the requirements of the callback function, see `hs.task... |

## Common Patterns


```

```
hs.timer.delayed.md
# hs.timer.delayed

Specialized timer objects to coalesce processing of unpredictable asynchronous events into a single callback

## Key Exports

- `new`
- `setDelay`
- `start`
- `stop`
- `nextTrigger`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.timer.delayed.new(delay, fn) -> hs.timer.del...` | a new `hs.timer.delayed` object | These timers are meant to be long-lived: once instantiated, there's no way to... |
| `setDelay` | `hs.timer.delayed:setDelay(delay) -> hs.timer.de...` | the delayed timer object | if the callback countdown is running, calling this method will restart it |
| `start` | `hs.timer.delayed:start([delay]) -> hs.timer.del...` | the delayed timer object |  |
| `stop` | `hs.timer.delayed:stop() -> hs.timer.delayed object` | the delayed timer object |  |
| `nextTrigger` | `hs.timer.delayed:nextTrigger() -> number or nil` | if the callback countdown is running, returns the number ... |  |

## Common Patterns

```lua
-- Execute after delay
hs.timer.doAfter(2, function() print('Done') end)

-- Repeating timer
local timer = hs.timer.doEvery(5, function() print('Tick') end)
```

```

```
hs.timer.md
# hs.timer

Execute functions with various timing rules

## Key Exports

- `new`
- `setNextTrigger`
- `start`
- `stop`
- `doAfter`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.timer.new(interval, fn [, continueOnError]) ...` | An `hs.timer` object | The returned object does not start its timer until its `:start()` method is c... |
| `setNextTrigger` | `hs.timer:setNextTrigger(seconds) -> timer` | The `hs.timer` object, or nil if an error occurred | If the timer is not already running, this will start it |
| `start` | `hs.timer:start() -> timer` | The `hs.timer` object | The timer will not call the callback immediately, the timer will wait until i... |
| `stop` | `hs.timer:stop() -> timer` | The `hs.timer` object |  |
| `doAfter` | `hs.timer.doAfter(sec, fn) -> timer` | An `hs.timer` object | There is no need to call `:start()` on the returned object, the timer will be... |

## Common Patterns

```lua
-- Execute after delay
hs.timer.doAfter(2, function() print('Done') end)

-- Repeating timer
local timer = hs.timer.doEvery(5, function() print('Tick') end)
```

```

```
hs.uielement.md
# hs.uielement

A generalized framework for working with OSX UI elements

## Key Exports

- `newWatcher`
- `focusedElement`
- `isApplication`
- `isWindow`
- `role`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `newWatcher` | `hs.uielement:newWatcher(handler[, userData]) ->...` | An `hs.uielement.watcher` object, or `nil` if an error oc... |  |
| `focusedElement` | `hs.uielement.focusedElement() -> element or nil` | An `hs.uielement` object or nil if no object could be found |  |
| `isApplication` | `hs.uielement:isApplication() -> bool` | A boolean, true if the UI element is an application |  |
| `isWindow` | `hs.uielement:isWindow() -> bool` | A boolean, true if the UI element is a window, otherwise ... |  |
| `role` | `hs.uielement:role() -> string` | A string containing the role of the UI element |  |

## Common Patterns


```

```
hs.uielement.watcher.md
# hs.uielement.watcher

Watch for events on certain UI elements (including windows and applications)

## Key Exports

- `start`
- `stop`
- `element`
- `pid`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `start` | `hs.uielement.watcher:start(events) -> hs.uielem...` | hs.uielement.watcher | See hs.uielement.watcher for a list of events. You may also specify arbitrary... |
| `stop` | `hs.uielement.watcher:stop() -> hs.uielement.wat...` | hs.uielement.watcher | This is automatically called if the element is destroyed. |
| `element` | `hs.uielement.watcher:element() -> object` | The element the watcher is watching. |  |
| `pid` | `hs.uielement.watcher:pid() -> number` | The PID of the element being watched |  |

## Common Patterns


```

```
hs.urlevent.md
# hs.urlevent

Allows Hammerspoon to respond to URLs Hammerspoon is configured to react to URLs that start with `hammerspoon://` when they are opened by OS X. This extension allows you to register callbacks for these URL events and their parameters, offering a flexible way to receive events from other applications.

## Key Exports

- `getAllHandlersForScheme`
- `getDefaultHandler`
- `setDefaultHandler`
- `setRestoreHandler`
- `bind`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getAllHandlersForScheme` | `hs.urlevent.getAllHandlersForScheme(scheme) -> ...` | A table containing the bundle identifiers of all applicat... |  |
| `getDefaultHandler` | `hs.urlevent.getDefaultHandler(scheme) -> string` | A string containing the bundle identifier of the current ... |  |
| `setDefaultHandler` | `hs.urlevent.setDefaultHandler(scheme[, bundleID])` | None | Changing the default handler for http/https URLs will display a system prompt... |
| `setRestoreHandler` | `hs.urlevent.setRestoreHandler(scheme, bundleID)` | None | You don't have to call this function if you want Hammerspoon to permanently b... |
| `bind` | `hs.urlevent.bind(eventName, callback)` | None | The callback function should accept two parameters: |

## Common Patterns


```

```
hs.usb.md
# hs.usb

Inspect USB devices

## Key Exports

- `attachedDevices`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `attachedDevices` | `hs.usb.attachedDevices() -> table or nil` | A table containing information about currently attached U... |  |

## Common Patterns


```

```
hs.usb.watcher.md
# hs.usb.watcher

Watch for USB device connection/disconnection events

## Key Exports

- `new`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.usb.watcher.new(fn) -> watcher` | A `hs.usb.watcher` object |  |
| `start` | `hs.usb.watcher:start() -> watcher` | The `hs.usb.watcher` object |  |
| `stop` | `hs.usb.watcher:stop() -> watcher` | The `hs.usb.watcher` object |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.watcher.new(...)
```

```

```
hs.utf8.md
# hs.utf8

Functions providing basic support for UTF-8 encodings

## Key Exports

- `asciiOnly`
- `codepointToUTF8`
- `fixUTF8`
- `hexDump`
- `registerCodepoint`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `asciiOnly` | `hs.utf8.asciiOnly(string[, all]) -> string` | The cleaned up string, with non-printable characters esca... | Because Unicode characters outside of the basic ascii alphabet are multi-byte... |
| `codepointToUTF8` | `hs.utf8.codepointToUTF8(...) -> string` | A string containing the UTF-8 byte sequences correspondin... | Valid codepoint values are from 0x0000 - 0x10FFFF (0 - 1114111) |
| `fixUTF8` | `hs.utf8.fixUTF8(inString[, replacementChar]) ->...` | outString - The contents of `inString` with all invalid U... | This function is a slight modification to code found at http://notebook.kulch... |
| `hexDump` | `hs.utf8.hexDump(inputString [, count]) -> string` | a string containing the hex dump of the input string. | Like hs.utf8.asciiOnly, this function will break up Unicode characters into t... |
| `registerCodepoint` | `hs.utf8.registerCodepoint(label, codepoint) -> ...` | Returns the UTF-8 byte sequence for the Unicode codepoint... | If a codepoint label was previously registered, this will overwrite the previ... |

## Common Patterns


```

```
hs.vox.md
# hs.vox

Controls for VOX music player

## Key Exports

- `getAlbumArtist`
- `getCurrentAlbum`
- `getCurrentArtist`
- `getPlayerState`
- `getUniqueID`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `getAlbumArtist` | `hs.vox.getAlbumArtist()` | A string containing the artist of current Album, or nil i... |  |
| `getCurrentAlbum` | `hs.vox.getCurrentAlbum()` | A string containing the Album of the current track, or ni... |  |
| `getCurrentArtist` | `hs.vox.getCurrentArtist()` | A string containing the Artist of the current track, or n... |  |
| `getPlayerState` | `hs.vox.getPlayerState()` | 0 for paused |  |
| `getUniqueID` | `hs.vox.getUniqueID()` | A string containing the name of the current track, or nil... |  |

## Common Patterns


```

```
hs.watchable.md
# hs.watchable

A minimalistic Key-Value-Observer framework for Lua.

## Key Exports

- `new`
- `watch`
- `alwaysNotify`
- `callback`
- `change`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.watchable.new(path, [externalChanges]) -> table` | a table with metamethods which will notify external code ... | This constructor is used by code which wishes to share state information whic... |
| `watch` | `hs.watchable.watch(path, [key], callback) -> wa...` | a watchableObject | This constructor is used by code which wishes to watch state information whic... |
| `alwaysNotify` | `hs.watchable:alwaysNotify([notify]) -> watchabl...` | if a boolean for `notify` is specified, returns the watch... |  |
| `callback` | `hs.watchable:callback([fn]) -> watchableObject ...` | if a value is specified and is a function, an object with... | see hs.watchable.watch for a description of the arguments the callback functi... |
| `change` | `hs.watchable:change([key], value) -> watchableO...` | the watchableObject | if external changes are not allowed for the specified path, this method gener... |

## Common Patterns

```lua
-- Create instance
local obj = hs.watchable.new(...)
```

```

```
hs.websocket.md
# hs.websocket

Simple websocket client.

## Key Exports

- `new`
- `close`
- `send`
- `status`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.websocket.new(url, callback) -> object` | The `hs.websocket` object | The callback should accept two parameters. |
| `close` | `hs.websocket:close() -> object` | The `hs.websocket` object |  |
| `send` | `hs.websocket:send(message[, isData]) -> object` | The `hs.websocket` object | Forcing a text representation by setting isData to `false` may alter the data... |
| `status` | `hs.websocket:status() -> string` | A string containing one of the following options: |  |

## Common Patterns


```

```
hs.webview.datastore.md
# hs.webview.datastore

Provides methods to list and purge the various types of data used by websites visited with `hs.webview`.

## Key Exports

- `newPrivate`
- `default`
- `fromWebview`
- `websiteDataTypes`
- `fetchRecords`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `newPrivate` | `hs.webview.datastore.newPrivate() -> datastoreO...` | a datastoreObject | The datastore represented by this object will be initially empty. You can use... |
| `default` | `hs.webview.datastore.default() -> datastoreObject` | a datastoreObject | this is the datastore used unless otherwise specified when creating an `hs.we... |
| `fromWebview` | `hs.webview.datastore.fromWebview(webview) -> da...` | a datastoreObject | When running on a system with OS X 10.11 or later, this method will also be a... |
| `websiteDataTypes` | `hs.webview.datastore.websiteDataTypes() -> table` | a list of strings where each string is a specific data ty... | As of the writing of this module, the following data types are defined and re... |
| `fetchRecords` | `hs.webview.datastore:fetchRecords([dataTypes], ...` | the datastore object | only those sites with one or more of the specified data types are returned |

## Common Patterns

```lua
-- Create instance
local obj = hs.datastore.default(...)
```

```

```
hs.webview.md
# hs.webview

Display web content in a window from Hammerspoon

## Key Exports

- `new`
- `newBrowser`
- `show`
- `stopLoading`
- `closeOnEscape`
- `delete`
- `deleteOnClose`
- `titleVisibility`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.webview.new(rect, [preferencesTable], [userC...` | The webview object | To set the initial URL, use the `hs.webview:url` method before showing the we... |
| `newBrowser` | `hs.webview.newBrowser(rect, [preferencesTable],...` | The webview object | The parameters are the same as for hs.webview.new -- check there for more det... |
| `show` | `hs.webview:show([fadeInTime]) -> webviewObject` | The webview object |  |
| `stopLoading` | `hs.webview:stopLoading() -> webviewObject` | The webview object | this method does not stop the loading of the primary content for the page at ... |
| `closeOnEscape` | `hs.webview:closeOnEscape([flag]) -> webviewObje...` | If a value is provided, then this method returns the webv... | If this is set to true, Escape will only close the window if no other element... |
| `delete` | `hs.webview:delete([propagate], [fadeOutTime]) -...` | None | This method is automatically called during garbage collection, notably during... |
| `deleteOnClose` | `hs.webview:deleteOnClose([value]) -> webviewObj...` | If a value is provided, then this method returns the webv... | If set to true, a webview object will be deleted when the user clicks on the ... |
| `titleVisibility` | `hs.webview:titleVisibility([state]) -> webviewO...` | if a value is provided, returns the webview object; other... | See also hs.webview:windowStyle and hs.webview.windowMasks. |
| `allowGestures` | `hs.webview:allowGestures([value]) -> webviewObj...` | If a value is provided, then this method returns the webv... | This is a shorthand method for getting or setting both `hs.webview:allowMagni... |
| `allowMagnificationGestures` | `hs.webview:allowMagnificationGestures([value]) ...` | If a value is provided, then this method returns the webv... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.webview.new(...)
```

```

```
hs.webview.toolbar.md
# hs.webview.toolbar

Create and manipulate toolbars which can be attached to the Hammerspoon console or hs.webview objects.

## Key Exports

- `new`
- `setCallback`
- `delete`
- `deleteItem`
- `attachToolbar`
- `inTitleBar`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.webview.toolbar.new(toolbarName, [toolbarTab...` | a toolbarObject | Toolbar names must be unique, but a toolbar may be copied with hs.webview.too... |
| `setCallback` | `hs.webview.toolbar:setCallback(fn) -> toolbarOb...` | the toolbar object. | the global callback function is invoked for a toolbar button item that does n... |
| `delete` | `hs.webview.toolbar:delete() -> none` | None |  |
| `deleteItem` | `hs.webview.toolbar:deleteItem(identifier) -> to...` | the toolbar object | This method completely removes the toolbar item from the toolbar's definition... |
| `attachToolbar` | `hs.webview.toolbar.attachToolbar([obj1], [obj2]...` | if the function is used to attach/detach a toolbar, then ... | This function is not expected to be used directly (though it can be) -- it is... |
| `inTitleBar` | `hs.webview.toolbar:inTitleBar([state]) -> toolb...` | if a parameter is specified, returns the toolbar object, ... | When this value is true, the toolbar, when visible, will appear in the window... |

## Common Patterns

```lua
-- Create instance
local obj = hs.toolbar.new(...)
```

```

```
hs.webview.usercontent.md
# hs.webview.usercontent

This module provides support for injecting custom JavaScript user content into your webviews and for JavaScript to post messages back to Hammerspoon.

## Key Exports

- `new`
- `setCallback`
- `injectScript`
- `removeAllScripts`
- `userScripts`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.webview.usercontent.new(name) -> usercontent...` | the usercontentControllerObject | This object should be provided as the final argument to the `hs.webview.new` ... |
| `setCallback` | `hs.webview.usercontent:setCallback(fn) -> userc...` | the usercontentControllerObject | Within your (injected or served) JavaScript, you can post messages via the me... |
| `injectScript` | `hs.webview.usercontent:injectScript(scriptTable...` | the usercontentControllerObject or nil if the script tabl... |  |
| `removeAllScripts` | `hs.webview.usercontent:removeAllScripts() -> us...` | the usercontentControllerObject | The WKUserContentController class only allows for removing all scripts. If yo... |
| `userScripts` | `hs.webview.usercontent:userScripts() -> array` | An array of injected user scripts. Each entry in the arra... | Because the WKUserContentController class only allows for removing all script... |

## Common Patterns

```lua
-- Create instance
local obj = hs.usercontent.new(...)
```

```

```
hs.wifi.md
# hs.wifi

Inspect WiFi networks

## Key Exports

- `setPower`
- `backgroundScan`
- `associate`
- `availableNetworks`
- `currentNetwork`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `setPower` | `hs.wifi.setPower(state, [interface]) -> boolean` | True if the power change was successful, or false and an ... |  |
| `backgroundScan` | `hs.wifi.backgroundScan(fn, [interface]) -> scan...` | returns a scan object | If you pass in nil as the callback function, the scan occurs but no callback ... |
| `associate` | `hs.wifi.associate(network, passphrase[, interfa...` | A boolean, true if the network was joined successfully, f... | Enterprise WiFi networks are not currently supported. Please file an issue on... |
| `availableNetworks` | `hs.wifi.availableNetworks([interface]) -> table` | A table containing the names of all visible WiFi networks | WARNING: This function will block all Lua execution until the scan has comple... |
| `currentNetwork` | `hs.wifi.currentNetwork([interface]) -> string o...` | A string containing the SSID of the WiFi network currentl... |  |

## Common Patterns

```lua
-- Create instance
local obj = hs.wifi.backgroundScan(...)
```

```

```
hs.wifi.watcher.md
# hs.wifi.watcher

Watch for changes to the associated wifi network

## Key Exports

- `new`
- `start`
- `stop`
- `watchingFor`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.wifi.watcher.new(fn) -> watcher` | A `hs.wifi.watcher` object | For backwards compatibility, only "SSIDChange" is watched for by default, so ... |
| `start` | `hs.wifi.watcher:start() -> watcher` | The `hs.wifi.watcher` object |  |
| `stop` | `hs.wifi.watcher:stop() -> watcher` | The `hs.wifi.watcher` object |  |
| `watchingFor` | `hs.wifi.watcher:watchingFor([messages]) -> watc...` | if a value is provided, returns the watcher object; other... | the possible values for this method are described in hs.wifi.watcher.eventTypes. |

## Common Patterns

```lua
-- Create instance
local obj = hs.watcher.new(...)
```

```

```
hs.window.filter.md
# hs.window.filter

Filter windows by application, title, location on screen and more, and easily subscribe to events on these windows

## Key Exports

- `new`
- `getFilters`
- `getWindows`
- `setAppFilter`
- `setCurrentSpace`
- `setDefaultFilter`
- `setFilters`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.window.filter.new(fn[,logname[,loglevel]]) -...` | a new windowfilter instance |  |
| `getFilters` | `hs.window.filter:getFilters() -> table` | a table containing the filtering rules of this windowfilt... |  |
| `getWindows` | `hs.window.filter:getWindows([sortOrder]) -> lis...` | a list of `hs.window` objects |  |
| `setAppFilter` | `hs.window.filter:setAppFilter(appname, filter) ...` | the `hs.window.filter` object for method chaining | Passing `focused=true` in `filter` will (naturally) result in the windowfilte... |
| `setCurrentSpace` | `hs.window.filter:setCurrentSpace(val) -> hs.win...` | the `hs.window.filter` object for method chaining | This is just a convenience wrapper for setting the `currentSpace` field in th... |
| `setDefaultFilter` | `hs.window.filter:setDefaultFilter(filter) -> hs...` | the `hs.window.filter` object for method chaining |  |
| `setFilters` | `hs.window.filter:setFilters(filters) -> hs.wind...` | the `hs.window.filter` object for method chaining | every filter definition in `filters` will overwrite the preexisting one for t... |

## Common Patterns

```lua
-- Get focused window
local win = hs.window.focusedWindow()
win:maximize()

-- Find window by title
local win = hs.window.find('Safari')
```

```

```
hs.window.highlight.md
# hs.window.highlight

Highlight the focused window

## Key Exports

- `start`
- `stop`
- `toggleIsolate`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `start` | `hs.window.highlight.start([windowfilterIsolate[...` | None | overlay mode is disabled by default - see `hs.window.highlight.ui.overlayColor` |
| `stop` | `hs.window.highlight.stop()` | None |  |
| `toggleIsolate` | `hs.window.highlight.toggleIsolate([v])` | None | This function should be bound to a hotkey, e.g.: `hs.hotkey.bind('ctrl-cmd','... |

## Common Patterns

```lua
-- Get focused window
local win = hs.window.focusedWindow()
win:maximize()

-- Find window by title
local win = hs.window.find('Safari')
```

```

```
hs.window.layout.md
# hs.window.layout

**WARNING** : EXPERIMENTAL MODULE. DO **NOT** USE IN PRODUCTION. This module is _for testing purposes only_. It can undergo breaking API changes or _go away entirely_ **at any point and without notice**. (Should you encounter any issues, please feel free to report them on https://github.com/Hammerspoon/hammerspoon/issues or #hammerspoon on irc.libera.chat)

## Key Exports

- `new`
- `getRules`
- `setScreenConfiguration`
- `start`
- `stop`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.window.layout.new(rules[,logname[,loglevel]]...` | a new windowlayout instance |  |
| `getRules` | `hs.window.layout:getRules() -> table` | a table containing the rules of this windowlayout; you ca... |  |
| `setScreenConfiguration` | `hs.window.layout:setScreenConfiguration(screens...` | the `hs.window.layout` object | If `screens` is `nil`, any previous screen configuration is removed, and this... |
| `start` | `hs.window.layout:start() -> hs.window.layout ob...` | the `hs.window.layout` object | If a screen configuration is defined for this windowfilter, and currently not... |
| `stop` | `hs.window.layout:stop() -> hs.window.layout object` | the `hs.window.layout` object |  |

## Common Patterns

```lua
-- Get focused window
local win = hs.window.focusedWindow()
win:maximize()

-- Find window by title
local win = hs.window.find('Safari')
```

```

```
hs.window.md
# hs.window

Inspect/manipulate windows

## Key Exports

- `get`
- `setShadows`
- `setFrame`
- `setFrameInScreenBounds`
- `setFrameWithWorkarounds`
- `setFullScreen`
- `setSize`
- `setTopLeft`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `get` | `hs.window.get(hint) -> hs.window object` | the first hs.window object that matches the supplied sear... | see also `hs.window.find` and `hs.application:getWindow()` |
| `setShadows` | `hs.window.setShadows(shadows)` | None | This function uses a private, undocumented OS X API call, so it is not guaran... |
| `setFrame` | `hs.window:setFrame(rect[, duration]) -> hs.wind...` | The `hs.window` object |  |
| `setFrameInScreenBounds` | `hs.window:setFrameInScreenBounds([rect][, durat...` | The `hs.window` object |  |
| `setFrameWithWorkarounds` | `hs.window:setFrameWithWorkarounds(rect[, durati...` | The `hs.window` object |  |
| `setFullScreen` | `hs.window:setFullScreen(fullscreen) -> window` | The `hs.window` object |  |
| `setSize` | `hs.window:setSize(size) -> window` | The `hs.window` object |  |
| `setTopLeft` | `hs.window:setTopLeft(point) -> window` | The `hs.window` object |  |
| `find` | `hs.window.find(hint) -> hs.window object(s)` | one or more hs.window objects that match the supplied sea... | for convenience you can call this as `hs.window(hint)` |
| `close` | `hs.window:close() -> bool` | True if the operation succeeded, false if not |  |

## Common Patterns

```lua
-- Get focused window
local win = hs.window.focusedWindow()
win:maximize()

-- Find window by title
local win = hs.window.find('Safari')
```

```

```
hs.window.switcher.md
# hs.window.switcher

Window-based cmd-tab replacement

## Key Exports

- `new`
- `nextWindow`
- `previousWindow`
- `next`
- `previous`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `new` | `hs.window.switcher.new([windowfilter[, uiPrefs]...` | the new instance |  |
| `nextWindow` | `hs.window.switcher.nextWindow()` | None | the switcher will be dismissed (and the selected window focused) when all mod... |
| `previousWindow` | `hs.window.switcher.previousWindow()` | None | the switcher will be dismissed (and the selected window focused) when all mod... |
| `next` | `hs.window.switcher:next()` | None | the switcher will be dismissed (and the selected window focused) when all mod... |
| `previous` | `hs.window.switcher:previous()` | None | the switcher will be dismissed (and the selected window focused) when all mod... |

## Common Patterns

```lua
-- Get focused window
local win = hs.window.focusedWindow()
win:maximize()

-- Find window by title
local win = hs.window.find('Safari')
```

```

```
hs.window.tiling.md
# hs.window.tiling

**WARNING** : EXPERIMENTAL MODULE. DO **NOT** USE IN PRODUCTION. This module is _for testing purposes only_. It can undergo breaking API changes or _go away entirely_ **at any point and without notice**. (Should you encounter any issues, please feel free to report them on https://github.com/Hammerspoon/hammerspoon/issues or #hammerspoon on irc.libera.chat)

## Key Exports

- `tileWindows`

## Quick Reference

| Function/Method | Signature | Returns | Key Notes |
|---|---|---|---|
| `tileWindows` | `hs.window.tiling.tileWindows(windows,rect[,desi...` | None | To ensure all windows are placed in a row (side by side), use a very small as... |

## Common Patterns

```lua
-- Get focused window
local win = hs.window.focusedWindow()
win:maximize()

-- Find window by title
local win = hs.window.find('Safari')
```

```


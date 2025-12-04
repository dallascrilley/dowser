#!/usr/bin/env swift

// Required parameters:
// @raycast.schemaVersion 1
// @raycast.title My Command
// @raycast.mode fullOutput
// @raycast.packageName My Package

// Optional parameters:
// @raycast.icon 🦅
// @raycast.description Brief description of what this command does
// @raycast.author Your Name

import Foundation

// Access arguments via CommandLine.arguments[1...]
let args = Array(CommandLine.arguments.dropFirst())

print("Hello from Raycast!")

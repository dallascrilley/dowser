#!/usr/bin/env node

// Required parameters:
// @raycast.schemaVersion 1
// @raycast.title My Command
// @raycast.mode fullOutput
// @raycast.packageName My Package

// Optional parameters:
// @raycast.icon 🟢
// @raycast.description Brief description of what this command does
// @raycast.author Your Name

// Access arguments via process.argv.slice(2)
const args = process.argv.slice(2);

console.log("Hello from Raycast!");

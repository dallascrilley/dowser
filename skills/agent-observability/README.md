# Agent Observability for Claude Code

Real-time visualization and monitoring dashboard for Claude Code agent interactions. Watch your agents work in real-time with swim lane visualizations, event filtering, and comprehensive session tracking.

![Agent Observability Dashboard](./docs/screenshots/dashboard-preview.png)
*Screenshot placeholder - Dashboard showing real-time agent interactions*

---

## Credits & Inspiration

This agent observability system was inspired by **[@indydevdan](https://github.com/indydevdan)**'s pioneering work on multi-agent observability for Claude Code.

**Key Differences in Our Implementation:**

| Feature | indydevdan's Approach | Our Approach |
|---------|----------------------|--------------|
| **Data Storage** | SQLite database (persistent) | Filesystem JSONL + In-memory (last 1000 events) |
| **Event Capture** | API calls to database | Direct filesystem writes via hooks |
| **Real-time Updates** | Database polling | File watching with WebSocket streaming |
| **Persistence** | Full historical data | Last 1000 events in memory, JSONL files on disk |
| **Dependencies** | SQLite, API server | Bun filesystem watcher, WebSocket |

**Why We Chose Filesystem Approach:**
- ✅ Tight integration with Claude Code hooks system
- ✅ No external database dependencies
- ✅ Simple JSONL format (human-readable, grep-able)
- ✅ Lightweight - streams only what's needed
- ✅ Works offline - no API calls required

Both approaches have merits! Check out [indydevdan's work](https://github.com/indydevdan) for a database-backed solution with full historical persistence.

---

## How It Works

Our implementation leverages Claude Code's hook system to capture events directly to the filesystem, then streams them to a real-time web dashboard:

1. **Claude Code Hooks** - Capture all agent events (tool use, session start, errors, etc.)
2. **JSONL Files** - Events written to daily log files in `~/.claude/history/raw-outputs/`
3. **File Watcher** - Bun server watches for new events using filesystem monitoring
4. **In-Memory Buffer** - Last 1000 events kept in memory for fast access
5. **WebSocket Streaming** - Real-time event delivery to connected clients
6. **Vue 3 Dashboard** - Interactive visualization with filtering and swim lanes

**No database required. No API calls. Just filesystem + WebSocket streaming.**

---

## Architecture

```
┌─────────────────┐
│  Claude Code    │
│   (with hooks)  │
└────────┬────────┘
         │
         │ Hook events
         ▼
┌─────────────────┐
│ capture-all-    │
│ events.ts hook  │ Writes JSONL
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ ~/.claude/history/raw-outputs/      │
│ 2025-01/2025-01-28_all-events.jsonl │ (Filesystem)
└────────┬────────────────────────────┘
         │
         │ File watcher
         ▼
┌─────────────────┐
│ file-ingest.ts  │ In-memory buffer (last 1000)
│  (Bun server)   │
└────────┬────────┘
         │
         │ WebSocket
         ▼
┌─────────────────┐
│  Vue 3 Client   │ Real-time visualization
│  (Vite + Tail)  │
└─────────────────┘
```

**Event Flow:**
1. Claude Code executes hooks on various events (tool use, session start, etc.)
2. `capture-all-events.ts` appends events to daily JSONL file
3. Server watches JSONL files for changes using Bun's filesystem API
4. New events are added to in-memory buffer and streamed via WebSocket
5. Vue frontend displays events in real-time with swim lane visualization

---

## Features

- 🔴 **Real-time Event Streaming** - See agent interactions as they happen
- 📊 **Agent Swim Lanes** - Visualize multiple agents running in parallel
- 🔍 **Event Filtering** - Filter by agent, session, event type
- 📈 **Live Charts** - Tool usage patterns and agent activity
- 💾 **Filesystem-Based** - No database required, uses simple JSONL
- 🎯 **Session Tracking** - Track agent sessions and subagent launches
- 🌊 **In-Memory Streaming** - Last 1000 events for low memory footprint
- 📝 **Human-Readable Logs** - JSONL format you can grep/analyze
- 🎨 **Agent Color Coding** - Visual distinction between agents
- ⚡ **Fast Performance** - WebSocket streaming with minimal overhead
- 🔌 **Zero Database Setup** - Works immediately with filesystem
- 🛠️ **Extensible** - Easy to add custom event types and visualizations

---

## Installation

See [SETUP.md](./SETUP.md) for detailed installation instructions.

**Quick Start:**

1. Set environment variable:
   ```bash
   export PAI_DIR="/Users/yourname/.claude"
   ```

2. Configure hooks in `~/.claude/settings.json` (see `settings.json.example`)

3. Install dependencies:
   ```bash
   cd skills/agent-observability/apps/server && bun install
   cd ../client && bun install
   ```

4. Run the dashboard:
   ```bash
   # Terminal 1 - Server
   cd apps/server && bun run dev

   # Terminal 2 - Client
   cd apps/client && bun run dev
   ```

5. Open http://localhost:5173

---

## Usage

Once installed and running, the dashboard will automatically display events from your Claude Code sessions.

### Dashboard Views

**Timeline View**
- Horizontal swim lanes for each agent
- Events displayed chronologically
- Color-coded by agent type
- Click events for detailed information

**Event Inspector**
- Click any event to see full details
- View tool inputs/outputs
- See error messages and stack traces
- Inspect session metadata

**Filters**
- Filter by agent name
- Filter by session ID
- Filter by event type
- Search event content

### Event Types Captured

| Event Type | Description | Captured Data |
|------------|-------------|---------------|
| `session_start` | New agent session begins | Agent ID, timestamp, configuration |
| `tool_use` | Agent uses a tool | Tool name, inputs, outputs, duration |
| `tool_error` | Tool execution fails | Error message, stack trace |
| `subagent_launch` | Agent launches subagent | Parent/child relationship |
| `session_end` | Agent session completes | Final status, summary |

---

## File Structure

```
skills/agent-observability/
├── README.md                    # This file
├── SETUP.md                     # Installation instructions
├── apps/
│   ├── server/                  # Bun WebSocket server
│   │   ├── src/
│   │   │   ├── file-ingest.ts   # File watcher + event ingestion
│   │   │   └── index.ts         # WebSocket server
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── client/                  # Vue 3 frontend
│       ├── src/
│       │   ├── components/      # Vue components
│       │   ├── composables/     # WebSocket client
│       │   └── App.vue          # Main dashboard
│       ├── package.json
│       └── vite.config.ts
├── hooks/
│   └── capture-all-events.ts    # Claude Code hook
├── docs/
│   └── screenshots/             # Dashboard screenshots
└── history-structure/           # Example JSONL structure
```

---

## Troubleshooting

### No events appearing

**Check environment variable:**
```bash
echo $PAI_DIR
# Should output: /Users/yourname/.claude
```

**Verify directory exists:**
```bash
mkdir -p ~/.claude/history/raw-outputs
```

**Check hook is configured:**
```bash
cat ~/.claude/settings.json | grep capture-all-events
```

**Make hook executable:**
```bash
chmod +x /Users/yourname/Projects/PAI/skills/agent-observability/hooks/capture-all-events.ts
```

**Check Claude Code output for errors:**
Look for hook execution errors in your terminal when running Claude Code.

---

### Events file not found

**File naming convention:**
```
~/.claude/history/raw-outputs/YYYY-MM/YYYY-MM-DD_all-events.jsonl
```

**Check if files are being created:**
```bash
ls -la ~/.claude/history/raw-outputs/$(date +%Y-%m)/
```

**Manually test the hook:**
```bash
cd /Users/yourname/Projects/PAI/skills/agent-observability/hooks
PAI_DIR="/Users/yourname/.claude" bun run capture-all-events.ts
```

---

### WebSocket connection failed

**Check server is running:**
```bash
# Should show server on port 3001
lsof -i :3001
```

**Check for port conflicts:**
```bash
# Kill conflicting process
kill -9 $(lsof -ti:3001)
```

**Restart both server and client:**
```bash
# Terminal 1
cd apps/server && bun run dev

# Terminal 2
cd apps/client && bun run dev
```

**Check browser console:**
Open DevTools (F12) and look for WebSocket connection errors.

---

### Permission denied

**Make hook executable:**
```bash
chmod +x skills/agent-observability/hooks/capture-all-events.ts
```

**Check directory permissions:**
```bash
ls -la ~/.claude/history/
# Should be writable by your user
```

**Verify PAI_DIR write access:**
```bash
touch ~/.claude/test-write && rm ~/.claude/test-write
# Should succeed without errors
```

---

### Events not updating in real-time

**Check file watcher is working:**
```bash
# Server logs should show "Watching for file changes..."
```

**Test manual event creation:**
```bash
echo '{"timestamp":"2025-01-28T12:00:00Z","type":"test","data":{}}' >> \
  ~/.claude/history/raw-outputs/$(date +%Y-%m)/$(date +%Y-%m-%d)_all-events.jsonl
```

**Restart the server:**
File watchers can sometimes get stuck. Restart the server to reset.

---

## Development

### Running in Development Mode

```bash
# Server with hot reload
cd apps/server
bun run dev

# Client with hot reload
cd apps/client
bun run dev
```

### Building for Production

```bash
# Build server
cd apps/server
bun build

# Build client
cd apps/client
bun run build
```

### Adding New Event Types

1. Update TypeScript types in `apps/server/src/types.ts`
2. Add event handling in `apps/server/src/file-ingest.ts`
3. Update UI components in `apps/client/src/components/`
4. Add color coding in `apps/client/src/config/colors.ts`

---

## Contributing

Contributions are welcome! This is part of the PAI (Personal AI Infrastructure) project.

**How to contribute:**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

**Areas for improvement:**
- Additional visualization types (charts, graphs)
- Event filtering and search improvements
- Historical data analysis tools
- Performance optimizations
- Documentation improvements

---

## FAQ

**Q: Does this work with standard Claude Code installations?**
A: Yes! It works with any Claude Code installation that supports hooks. Just configure the hook in your `settings.json`.

**Q: How much disk space do JSONL files use?**
A: Typical usage is 1-10 MB per day. Files are organized by month for easy cleanup.

**Q: Can I analyze historical data?**
A: Yes! JSONL files are human-readable. Use standard tools like `jq`, `grep`, or custom scripts.

**Q: Why not use indydevdan's approach?**
A: Both approaches are valid! Our filesystem approach integrates tightly with PAI's existing infrastructure. Use indydevdan's if you need full database persistence.

**Q: Can I run multiple dashboards?**
A: Yes! The server supports multiple WebSocket clients. Open multiple browser tabs if needed.

**Q: Does this slow down Claude Code?**
A: No. Hook execution is asynchronous and writes are buffered. Impact is negligible.

---

## License

Part of the PAI (Personal AI Infrastructure) project. See main PAI repository for license information.

---

## Acknowledgments

- **[@indydevdan](https://github.com/indydevdan)** - For pioneering agent observability patterns
- **Claude Code Team** - For the excellent hooks system
- **PAI Community** - For testing and feedback

---

## Related Projects

- [Dowser (this plugin)](https://github.com/dallascrilley/pai-skills)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)
- [indydevdan's Agent Observability](https://github.com/indydevdan)

---

**Status**: Active Development 🚧

This skill is under active development. Expect changes and improvements. Feedback and contributions welcome!

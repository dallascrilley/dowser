---
name: vmix-production-manager
description: >-
  vMix Production Manager - Complete automation toolkit for vMix live production
  with helper scripts, configuration templates, and production-ready patterns.
when_to_use: >-
  Use when working with vMix production automation, creating automation recipes,
  managing vMix inputs, troubleshooting VBScript, analyzing production logs,
  live video production, broadcast automation, or video streaming workflows.
version: 1.0.0
category: integrations-and-saas
---

# vMix Production Manager Skill

## Overview

This skill provides comprehensive tooling and knowledge for automating vMix live production workflows. It includes helper scripts, configuration templates, critical gotchas documentation, and production-ready patterns.

**vMix** is professional live production software for video mixing, recording, and streaming. This skill focuses on automation through three integration methods:
- **VB.NET Scripting** (4K/Pro only): Embedded automation with direct vMix state access
- **HTTP REST API** (Port 8088): Remote control from any language
- **TCP API** (Port 8099): Real-time event subscriptions (tally lights, state mirroring)

## When to Use This Skill

Use this skill PROACTIVELY when the user:
- Mentions "vMix", "live production", "video automation", or "broadcast automation"
- Needs to create vMix automation recipes or workflows
- Is working with vMix inputs, titles, overlays, or transitions
- Encounters vMix API errors or VBScript issues
- Wants to analyze vMix production logs
- Needs to set up vMix automation infrastructure
- Is troubleshooting vMix production problems
- Asks about video switcher automation

**Keywords:** vMix, recipe, VBScript, production automation, live video, broadcast, HTTP API, input creation, overlay, transition

## Core Capabilities

### 1. Helper Scripts (5 Production Tools)

**vmix-recipe-builder.py**
- Converts run-of-show JSON to executable vMix recipe format
- Validates timing sequences and action types
- Generates complete automation workflows
- **Use when:** Building production automation from show rundowns

**vmix-health-check.sh**
- Verifies vMix API connectivity and system state
- Checks HTTP and TCP API availability
- Validates vMix version and edition
- Reports input counts, recording/streaming status
- **Use when:** Pre-production verification or troubleshooting connectivity

**vmix-recipe-validator.py**
- Validates recipe JSON schema and structure
- Checks action types against vMix API specification
- Verifies transition types, timing sequences, and file references
- Provides detailed error/warning reports
- **Use when:** Validating recipes before production use

**vmix-input-creator.sh**
- Quick CLI for creating common vMix input types
- Supports video, image, audio, title, color, NDI, browser inputs
- Automatic path validation and URL encoding
- Configurable parameters (volume, looping, muting, etc.)
- **Use when:** Rapidly setting up production inputs

**vmix-log-analyzer.py**
- Parses and analyzes VBScript execution logs
- Identifies error patterns and performance issues
- Generates health scores for scripts
- Detects error cascades and repeated failures
- **Use when:** Post-production analysis or debugging automation failures

### 2. Configuration Templates (3 Templates)

**vmix-connection.json**
- Centralized vMix connection configuration
- Host, port, timeout, and retry settings
- Studio-specific paths and tool locations
- Preset and template mappings

**production-presets.yaml**
- Reusable production configurations
- Input position mappings for different show types
- Automation pipeline definitions
- Validation rules for titles and browser inputs

**vbscript-config-template.vb**
- Production-ready VBScript template
- Proper configuration section structure
- Timing, path, and debug settings
- Inline comments and best practices

### 3. Critical VBScript Gotchas (MUST KNOW)

**🚨 CRITICAL RULES (Will Break Production)**

1. **NO Function/Sub Blocks** - vMix VBScript doesn't support custom Function or Sub definitions
   - ❌ `Function Normalize(url)` → ✗ "End Function Not Supported" error
   - ✅ Inline all logic in single script scope

2. **NO VB6 Global Functions** - Classic VBScript functions don't exist
   - ❌ `Trim(str)`, `LCase(str)`, `Left(str, n)` → compilation errors
   - ✅ Use .NET methods: `str.Trim()`, `str.ToLower()`, `str.Substring(0, n)`

3. **Explicit Loop Variable Types** - Type inference doesn't work in For Each
   - ❌ `For Each kvp In dict` → "variable not declared" error
   - ✅ `For Each kvp As System.Collections.Generic.KeyValuePair(Of String, String) In dict`

4. **Close HTTP Connections** - Unclosed connections exhaust connection pool
   - ❌ Missing `response.Close()` → connection leaks, script hangs after 10-50 executions
   - ✅ Always use Try/Finally with explicit `response.Close()` and `webClient.Dispose()`

5. **Case-Sensitive Names** - Input names and field names are strictly case-sensitive
   - ❌ "Title.gtzip" ≠ "title.gtzip", "Headline.Text" ≠ "headline.text"
   - ✅ Copy exact names from vMix UI, use GUIDs for stable references

6. **GT Title Field Suffixes** - GT titles require .Text/.Source suffixes
   - ❌ `SetText(..., SelectedName:="Headline", ...)` → fails silently
   - ✅ `SetText(..., SelectedName:="Headline.Text", ...)` for GT titles

7. **UTF-8 Without BOM** - Preset files must use UTF-8 encoding without BOM
   - ❌ `New System.Text.UTF8Encoding(true)` → corrupts preset files
   - ✅ `New System.Text.UTF8Encoding(false)` and `PreserveWhitespace = true`

8. **Sleep() in Loops** - Continuous loops without Sleep() max out CPU
   - ❌ `Do While True ... Loop` → 100% CPU, system sluggish
   - ✅ `Do While True ... Sleep(100) Loop` (50-500ms intervals)

9. **vMix Edition Requirement** - Scripting only works in 4K ($350) and Pro ($1200+)
   - ❌ Basic, HD, Basic HD editions: zero scripting capability
   - ✅ Verify edition via XML API before designing automation

**See full pitfall documentation** for 25+ gotchas with solutions

### 4. HTTP API Patterns

**Standard Request Format:**
```http
GET http://{host}:8088/api/?Function={command}&Input={target}&Value={value}
```

**Best Practices:**
- URL-encode all parameters (space=%20, #=%23, &=%26, etc.)
- Use input GUIDs for stable references (immune to reordering/renaming)
- Check response status: 200=success, 500=error
- Insert 200ms sleep between sequential API calls
- Implement retry with exponential backoff for network errors
- Validate production state before disruptive operations

**Common Commands:**
- `AddInput` - Create new input (video, image, title, browser, etc.)
- `SetInputName` - Rename input (use after creation for custom names)
- `SetText` - Update title text field (requires exact field name with .Text suffix)
- `Cut`/`Fade` - Transition to input
- `OverlayInput1In`/`Out` - Show/hide overlay
- `SetVolume` - Adjust audio volume (0-100)
- `StartRecording`/`StopRecording` - Control recording
- `StartStreaming`/`StopStreaming` - Control streaming

### 5. Recipe-Based Automation Pattern

**Workflow:**
```
Python Orchestrator (JCS Automation)
    ↓ generates
JSON Recipe (vmix_recipe.json)
    ↓ consumed by
VBScript Controller (studio PC)
    ↓ executes
vMix Input Creation & Configuration
```

**Recipe Schema v2.0:**
```json
{
  "metadata": {
    "event_name": "Weekly Broadcast",
    "generated_at": "2025-11-11T10:30:00Z",
    "version": "1.0",
    "vmix_config": {"host": "127.0.0.1", "port": 8088}
  },
  "config": {
    "default_transition": "fade",
    "default_duration": 1000,
    "overlay_positions": {"lower_third": 1, "fullscreen": 2}
  },
  "sequence": [
    {
      "type": "camera_cut",
      "time": 0,
      "input_name": "Camera 1",
      "transition": "fade",
      "transition_duration": 1000
    },
    {
      "type": "overlay",
      "time": 5000,
      "action": "show",
      "position": 1,
      "input_name": "Lower Third"
    },
    {
      "type": "title",
      "time": 5200,
      "input_name": "Lower Third",
      "field": "Headline.Text",
      "value": "John Doe"
    }
  ]
}
```

**Action Types:**
- `marker` - Segment/chapter marker
- `camera_cut` - Transition to camera/input
- `overlay` - Show/hide/update overlay
- `audio` - Volume control, muting, fading
- `title` - Update title text fields
- `transition` - Generic transition
- `recording` - Start/stop recording
- `streaming` - Start/stop streaming
- `preset` - Load preset file
- `wait` - Timed delay

## Common Workflows

### Workflow 1: Create Production Recipe from Rundown

```bash
# 1. Build recipe from run-of-show JSON
vmix-recipe-builder.py show-rundown.json \
    -o production-recipe.json \
    --host 192.168.1.100 \
    --summary

# 2. Validate recipe
vmix-recipe-validator.py production-recipe.json --strict

# 3. If validation passes, recipe is ready for execution
```

### Workflow 2: Pre-Production Health Check

```bash
# Comprehensive health check before show
vmix-health-check.sh \
    --host 192.168.1.100 \
    --verbose

# If check passes, proceed with input setup
# If check fails, troubleshoot connectivity/configuration
```

### Workflow 3: Quick Input Setup

```bash
# Add video input
vmix-input-creator.sh video intro.mp4 \
    --name "Show Intro" \
    --loop

# Add title from template
vmix-input-creator.sh title "Lower Third" \
    --name "Guest Name" \
    --fields '{"Headline.Text":"John Doe","Description.Text":"CEO"}'

# Add browser for social media
vmix-input-creator.sh browser "https://twitter.com/feed" \
    --width 1920 \
    --height 1080
```

### Workflow 4: Post-Show Log Analysis

```bash
# Analyze production logs
vmix-log-analyzer.py vmix-2025-11-11.log \
    --output reports/2025-11-11-analysis.txt \
    --show-errors 20

# Generate JSON for archiving
vmix-log-analyzer.py vmix-2025-11-11.log \
    --format json \
    --output reports/2025-11-11-analysis.json
```

### Workflow 5: VBScript Development Cycle

1. **Start with template:** Copy `vbscript-config-template.vb`
2. **Configure parameters:** Set paths, timing, debug options
3. **Write logic:** Inline all logic (no functions/subs)
4. **Follow conventions:**
   - Use .NET methods (not VB6 functions)
   - Explicit loop variable types
   - Always close HTTP connections
   - Include Sleep() in continuous loops
5. **Test incrementally:** Test with minimal preset first
6. **Monitor performance:** Check CPU usage, connection counts
7. **Log extensively:** Console.WriteLine() for debugging
8. **Analyze logs:** Use vmix-log-analyzer.py to identify issues

## Troubleshooting Quick Reference

**Problem:** Recipe validation fails with "Invalid action type"
- **Cause:** Typo in action type field
- **Solution:** Check action type against valid types: marker, camera_cut, overlay, audio, title, transition, recording, streaming, preset, wait

**Problem:** VBScript fails with "End Function Not Supported"
- **Cause:** Using Function/Sub blocks (not allowed in vMix VBScript)
- **Solution:** Inline all logic in single script scope, no custom functions

**Problem:** Title updates don't appear on screen
- **Cause:** Missing .Text suffix for GT title fields
- **Solution:** Use "Headline.Text" not "Headline" for GT titles

**Problem:** Script works initially but fails after 10-50 executions
- **Cause:** HTTP connection leak (connections not closed)
- **Solution:** Add `response.Close()` and `webClient.Dispose()` calls

**Problem:** Input names mismatch, operations fail
- **Cause:** Case-sensitive input name mismatch
- **Solution:** Use exact case from vMix UI or use GUIDs for stable references

**Problem:** Automation operates on wrong input after reordering
- **Cause:** Using input numbers (1, 2, 3) which change when reordered
- **Solution:** Use input names or GUIDs for permanent references

**Problem:** Browser inputs cause high CPU usage
- **Cause:** Multiple browser inputs with complex web pages
- **Solution:** Limit to 3-5 browser inputs, use static images when possible

**Problem:** Health check fails with connection timeout
- **Cause:** vMix not running, wrong host/port, or firewall blocking
- **Solution:** Verify vMix running, check host/port settings, check firewall

**See full troubleshooting guide** for 20+ issues with detailed solutions

## Documentation Structure

```
vmix-production-manager/
├── README.md                          # Project overview
├── docs/
│   ├── getting-started/
│   │   ├── quick-start.md             # 5-minute first recipe
│   │   ├── installation.md            # Setup instructions
│   │   └── concepts.md                # Core concepts
│   ├── reference/
│   │   ├── recipe-schema-reference.md # Complete JSON schema
│   │   ├── http-api-patterns.md       # HTTP API best practices
│   │   ├── vbscript-conventions.md    # VBScript rules & gotchas
│   │   ├── action-types.md            # Action type reference
│   │   └── preset-options.md          # Preset configuration
│   ├── guides/
│   │   ├── troubleshooting-guide.md   # Problem-solving guide
│   │   ├── production-workflows.md    # Real-world workflows
│   │   ├── advanced-patterns.md       # Advanced automation
│   │   └── performance-tuning.md      # Optimization
│   └── tutorials/
│       ├── first-recipe.md            # Step-by-step tutorial
│       ├── worship-service.md         # Worship automation
│       └── conference-setup.md        # Conference automation
├── config/
│   ├── vmix-connection.json.example
│   ├── production-presets.yaml
│   └── README.md
├── templates/
│   ├── vbscript-config-template.vb
│   ├── recipe-basic.json
│   └── recipe-worship.json
└── examples/
    ├── recipes/
    └── scripts/
```

**Reading Paths:**
- **Beginners:** README → Quick Start → First Recipe Tutorial → Schema Reference
- **VBScript Devs:** VBScript Conventions → Config Template → API Patterns
- **Troubleshooting:** Troubleshooting Guide → Conventions → API Patterns
- **Production Designers:** Production Workflows → Presets → Schema Reference

## Prerequisites

**vMix Requirements:**
- vMix 4K ($350) or Pro ($1200+) edition for VBScript scripting
- Basic/HD editions support HTTP API only (no embedded scripting)
- Web API enabled (Settings → Web, port 8088)
- TCP API port 8099 for tally/event subscriptions

**System Requirements:**
- Windows 7+ (64-bit for vMix 25+)
- .NET Framework 3.5+
- Network connectivity to vMix instance

**Helper Script Requirements:**
- Python 3.7+ (for recipe builder, validator, log analyzer)
- Bash 4.0+ (for health check, input creator)
- curl (for HTTP requests)
- Optional: xmllint (for XML validation), jq (for JSON processing)

## Installation

```bash
# 1. Create tools directory
mkdir -p ~/vmix-tools
cd ~/vmix-tools

# 2. Copy helper scripts from skill package
cp vmix-recipe-builder.py vmix-tools/
cp vmix-health-check.sh vmix-tools/
cp vmix-recipe-validator.py vmix-tools/
cp vmix-input-creator.sh vmix-tools/
cp vmix-log-analyzer.py vmix-tools/

# 3. Make scripts executable
chmod +x ~/vmix-tools/*.sh ~/vmix-tools/*.py

# 4. Add to PATH (optional)
echo 'export PATH="$HOME/vmix-tools:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 5. Set environment variables
export VMIX_HOST="192.168.1.100"  # or 127.0.0.1 for local
export VMIX_HTTP_PORT="8088"
export VMIX_TCP_PORT="8099"

# 6. Test installation
vmix-health-check.sh --help
```

## Example Usage

### Example 1: Complete Show Preparation

```bash
#!/bin/bash
# show-prep.sh - Automated show preparation

# 1. Health check
if ! vmix-health-check.sh --host 192.168.1.100; then
    echo "ERROR: vMix not ready!"
    exit 1
fi

# 2. Build recipe
vmix-recipe-builder.py rundowns/weekly-show.json \
    -o recipes/weekly-recipe.json \
    --host 192.168.1.100

# 3. Validate
if ! vmix-recipe-validator.py recipes/weekly-recipe.json --strict; then
    echo "ERROR: Recipe validation failed!"
    exit 1
fi

# 4. Create inputs
vmix-input-creator.sh video media/intro.mp4 --name "Intro" --loop
vmix-input-creator.sh title "Lower Third" --name "Guest 1"
vmix-input-creator.sh browser "https://example.com" --name "Website"

echo "Show preparation complete!"
```

### Example 2: Continuous Monitoring

```bash
#!/bin/bash
# monitor.sh - Continuous health monitoring

while true; do
    if ! vmix-health-check.sh --json > /tmp/vmix-status.json; then
        echo "$(date): ALERT - vMix health check failed!" | tee -a alerts.log
        # Send notification (email, Slack, etc.)
    fi
    sleep 60
done
```

### Example 3: VBScript Input Creation

```vbscript
' LoadInputs.vb - Create inputs from recipe data

'-- Configuration
Dim studioPath As String = "E:\ShowAssets\"
Dim waitTimeout As Integer = 2000

'-- Get input count before
Dim xml As String = API.XML()
Dim cfg As New System.Xml.XmlDocument()
cfg.LoadXml(xml)
Dim beforeCount As Integer = cfg.SelectNodes("//input").Count

'-- Add video input
API.Function("AddInput", Value:="Video|" & studioPath & "intro.mp4")
Sleep(400)

'-- Wait for creation
Dim elapsed As Integer = 0
Dim created As Boolean = False
Do While elapsed < waitTimeout
    Sleep(200)
    elapsed += 200

    xml = API.XML()
    cfg.LoadXml(xml)
    Dim afterCount As Integer = cfg.SelectNodes("//input").Count

    If afterCount > beforeCount Then
        created = True
        Exit Do
    End If
Loop

If created Then
    '-- Rename input (use last input number)
    API.Function("SetInputName", Input:=cfg.SelectNodes("//input").Count, Value:="Show Intro")
    Console.WriteLine("✓ Input created: Show Intro")
Else
    Console.WriteLine("✗ Input creation timeout")
End If
```

## Helper Script Reference

**vmix-recipe-builder.py**
```bash
vmix-recipe-builder.py INPUT.json -o OUTPUT.json [options]
  --host HOST           vMix host (default: 127.0.0.1)
  --port PORT           vMix port (default: 8088)
  --summary             Show recipe summary
  --validate-only       Validate without building
```

**vmix-health-check.sh**
```bash
vmix-health-check.sh [options]
  --host HOST           vMix host
  --http-port PORT      HTTP API port
  --tcp-port PORT       TCP API port
  --skip-inputs         Skip input validation
  --json                JSON output
  --verbose             Verbose output
```

**vmix-recipe-validator.py**
```bash
vmix-recipe-validator.py RECIPE.json [options]
  --strict              Enable strict validation
  --no-check-files      Skip file existence checks
  --verbose             Show detailed info
```

**vmix-input-creator.sh**
```bash
vmix-input-creator.sh COMMAND [options]
  Commands: video, image, audio, title, color, ndi, browser
  --name NAME           Input name
  --loop                Enable looping
  --muted               Start muted
  --volume NUM          Set volume 0-100
```

**vmix-log-analyzer.py**
```bash
vmix-log-analyzer.py LOGFILE [options]
  --format FORMAT       Output format (text|json)
  --output FILE         Save to file
  --show-errors N       Show top N errors
  --script-filter NAME  Filter by script
```

## Configuration Template Reference

**vmix-connection.json:**
- vMix host, port, timeout, retry settings
- Studio paths and tool locations
- Preset and template mappings

**production-presets.yaml:**
- Reusable production configurations
- Input position mappings
- Validation rules
- Automation pipeline definitions

**vbscript-config-template.vb:**
- Standard configuration section
- Timing parameters
- Path definitions
- Debug settings

## API Command Reference

**Input Management:**
- `AddInput` - Create input (Value: "Type|Path")
- `RemoveInput` - Delete input
- `SetInputName` - Rename input
- `MoveInput` - Reorder inputs

**Transitions:**
- `Cut` - Instant cut to input
- `Fade` - Fade transition (default 1000ms)
- `Transition[1-4]` - Custom transitions
- `Stinger[1-4]` - Stinger transitions

**Overlays:**
- `OverlayInput[1-4]In` - Show overlay
- `OverlayInput[1-4]Out` - Hide overlay
- `OverlayInput[1-4]Off` - Instant hide

**Audio:**
- `SetVolume` - Set volume 0-100
- `AudioOn`/`AudioOff` - Mute/unmute
- `SetVolumeFade` - Fade volume (Value: "target,duration")

**Titles:**
- `SetText` - Update text field (SelectedName + Value)
- `SetImage` - Update image field (SelectedName + Value)
- `NextPicture`/`PreviousPicture` - Image navigation

**Recording/Streaming:**
- `StartRecording`/`StopRecording` - Control recording
- `StartStreaming`/`StopStreaming` - Control streaming (Channel parameter)

**State Query:**
- `GET /api/` - Full XML state
- Parse with XmlDocument for input/status queries

## Performance Best Practices

1. **HTTP API Rate Limiting:**
   - 200ms sleep between sequential API calls
   - 500ms for recording/streaming state changes
   - Use batch operations when possible

2. **VBScript Optimization:**
   - Reuse XmlDocument objects across iterations
   - 50-500ms Sleep() intervals in continuous loops
   - Dispose WebClient/HttpWebRequest explicitly
   - Culture-invariant number parsing for floats

3. **Browser Input Management:**
   - Limit to 3-5 simultaneous browser inputs
   - Use static images for heavy web pages
   - Enable "High Input Performance Mode" (GPU 3GB+)

4. **Input References:**
   - Use GUIDs for permanent references
   - Use names for stability across sessions
   - Avoid numbers (change when reordered)

5. **Resource Management:**
   - Close all HTTP connections explicitly
   - Monitor vMix render time (<20ms target)
   - Check CPU usage for tight loops
   - Limit input count (<50 for performance)

## Error Codes & Diagnostics

**HTTP Status Codes:**
- 200 - Success
- 500 - Error (invalid function/parameter)

**Common VBScript Errors:**
- "End Function Not Supported" - Function/Sub block used
- "BC30451: '[Name]' is not declared" - VB6 function or untyped loop variable
- "Object Reference not set" - Null XML node or input not found
- "Input string was not in correct format" - Culture-invariant parsing needed

**Connection Issues:**
- ETIMEDOUT (45s) - TCP connection timeout, implement reconnection
- Connection refused - vMix not running or firewall blocking
- Connection exhaustion - HTTP connections not closed

## Production Checklist

**Pre-Production:**
- [ ] Run health check (`vmix-health-check.sh`)
- [ ] Validate recipe (`vmix-recipe-validator.py --strict`)
- [ ] Verify vMix edition (4K/Pro for scripting)
- [ ] Check input capacity (<50 recommended)
- [ ] Test automation on minimal preset first

**During Production:**
- [ ] Monitor vMix console for script errors
- [ ] Check CPU usage stays reasonable
- [ ] Verify render time <20ms
- [ ] Log all automation actions
- [ ] Have manual override procedures ready

**Post-Production:**
- [ ] Analyze logs (`vmix-log-analyzer.py`)
- [ ] Identify error patterns and performance issues
- [ ] Archive recipes with show metadata
- [ ] Update troubleshooting docs with new issues
- [ ] Review and optimize automation workflows

## Support & Resources

**vMix API Documentation:**
- HTTP API Reference: https://www.vmix.com/help{version}/RESTAPI.html
- VB.NET Scripting: https://www.vmix.com/help{version}/Scripting.html
- TCP API Reference: https://www.vmix.com/help{version}/TCPAPI.html

**Community Resources:**
- vMix Forums: https://forums.vmix.com/
- vMix User Group: Facebook groups
- YouTube Tutorials: Search "vMix automation"

**This Skill Package:**
- Full documentation in `docs/` directory
- Working examples in `examples/` directory
- Templates in `templates/` directory
- Helper scripts in root or designated tools directory

## Version History

**v1.0.0** (2025-11-11)
- Initial release
- 5 helper scripts (recipe builder, health check, validator, input creator, log analyzer)
- 3 configuration templates
- Comprehensive documentation (5 key reference docs)
- 25+ critical gotchas documented
- Production-ready patterns and workflows

---

## Quick Reference Card

**Critical VBScript Rules:**
1. NO Function/Sub blocks
2. NO VB6 functions (use .NET methods)
3. Explicit loop variable types
4. Always close HTTP connections
5. Case-sensitive names
6. GT titles need .Text suffix
7. UTF-8 without BOM for presets
8. Sleep() in continuous loops

**Most Common Errors:**
- Missing .Text suffix → Title updates fail
- Unclosed connections → Script hangs after N executions
- VB6 functions → Compilation error
- Wrong case → Input not found
- No Sleep() → 100% CPU

**Helper Scripts Quick Commands:**
```bash
# Health check
vmix-health-check.sh --host IP

# Build recipe
vmix-recipe-builder.py rundown.json -o recipe.json

# Validate
vmix-recipe-validator.py recipe.json --strict

# Create input
vmix-input-creator.sh video file.mp4 --name "Name"

# Analyze logs
vmix-log-analyzer.py vmix.log --show-errors 10
```

**Emergency Troubleshooting:**
1. Check health: `vmix-health-check.sh`
2. Validate recipe: `vmix-recipe-validator.py --strict`
3. Review VBScript conventions
4. Analyze logs: `vmix-log-analyzer.py`
5. Check vMix console for errors

---

*Generated by convert-docs-to-skill workflow | vMix Production Manager Skill v1.0.0*

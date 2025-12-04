# Community Scripts & Discovery

## Official Repository

The Raycast team maintains a curated collection of community scripts:

**https://github.com/raycast/script-commands**

### Repository Structure

```
script-commands/
├── commands/           # Community scripts organized by category
│   ├── apps/
│   ├── browsing/
│   ├── communication/
│   ├── conversions/
│   ├── dashboard/
│   ├── developer-utils/
│   ├── media/
│   ├── navigation/
│   ├── productivity/
│   ├── security/
│   └── system/
├── templates/          # Language templates
└── documentation/      # Official docs
```

### Browse by Category

| Category | Path | Examples |
|----------|------|----------|
| AI | `commands/ai/` | Gemini, ChatGPT, Claude |
| Apps | `commands/apps/` | Bear, Agenda, Amphetamine |
| Browsing | `commands/browsing/` | Bookmarks, tab management |
| Communication | `commands/communication/` | Email, Slack, messaging |
| Conversions | `commands/conversions/` | Base64, URL encode, units |
| Dashboard | `commands/dashboard/` | Bitcoin, weather, system stats |
| Developer Utils | `commands/developer-utils/` | Git, UUID, JSON, hashing |
| Home | `commands/home/` | Elgato, Philips Hue |
| Images | `commands/images/` | Screenshots, image processing |
| Math | `commands/math/` | Calculators, converters |
| Media | `commands/media/` | Spotify, Apple Music, screenshots |
| Navigation | `commands/navigation/` | Folder shortcuts |
| Productivity | `commands/productivity/` | Bitwarden, writing tools |
| Remote Control | `commands/remote-control/` | Device control |
| System | `commands/system/` | Power, Finder, Dock, clipboard |
| Web Searches | `commands/web-searches/` | Google, GitHub, Stack Overflow |

## Finding Scripts

### Clone the Repository

```bash
git clone https://github.com/raycast/script-commands.git
cd script-commands/commands
```

### Search by Keyword

```bash
# Find all clipboard-related scripts
rg -l "clipboard" commands/

# Find Python scripts
fd -e py commands/

# Find scripts with specific mode
rg "@raycast.mode inline" commands/
```

### Copy to Your Scripts Folder

```bash
# Copy a specific script
cp commands/developer-utils/git/git-status.sh ~/your-scripts/

# Copy entire category
cp -r commands/dashboard/* ~/your-scripts/
```

## Contributing Back

If you create useful scripts, consider contributing:

1. Fork the repository
2. Add your script following their conventions
3. Run ShellCheck for bash scripts
4. Submit a pull request

See their CONTRIBUTING.md for detailed guidelines.

## Other Resources

### Raycast Extensions API

For richer functionality beyond scripts, consider the Extensions API:
- https://github.com/raycast/extensions
- Full React-based UI
- TypeScript support
- Store distribution

### Community Discord

Join the Raycast community for help and inspiration:
- https://raycast.com/community

## Quality Checklist

Before using community scripts:

- [ ] Review the code for security
- [ ] Check dependencies are installed
- [ ] Verify paths work for your system
- [ ] Test in isolation before enabling
- [ ] Modify hardcoded paths as needed

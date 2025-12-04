# Icon Reference

Icons can be emoji, local file paths, or HTTPS URLs. Recommended size: 64px.

## By Category

### System & Files
📁 📂 📄 📝 📋 💾 💿 🗂️ 🗃️ 🗑️ 📦 📥 📤 🔒 🔓 🔑

### Development
💻 🖥️ ⌨️ 🖱️ 🔧 🔨 ⚙️ 🛠️ 🔩 📟 🧪 🔬 🐛 🐙 📊 📈

### Web & Network
🌐 🔗 📡 📶 🌍 🌎 🌏 ☁️ 🔍 🔎 📧 ✉️ 💬 💭

### Media & Creative
🎵 🎶 🎤 🎧 🎬 📷 📸 🖼️ 🎨 ✏️ 🖌️ 🖍️ 📹 🎥

### Productivity
📅 📆 🗓️ ⏰ ⏱️ ⏲️ 📌 📍 ✅ ❌ ⭐ 🔔 🔕 💡 📎 ✂️

### Communication
💬 💭 🗣️ 📢 📣 🔔 📱 ☎️ 📞 📲 ✉️ 📧 📨 📩

### Arrows & Navigation
⬆️ ⬇️ ⬅️ ➡️ ↩️ ↪️ 🔄 🔃 🔀 🔁 🔂 ▶️ ⏸️ ⏹️ ⏺️

### Status & Indicators
✅ ❌ ⚠️ ❗ ❓ 💯 🔴 🟢 🟡 🔵 ⚪ ⚫ 🟠 🟣

### Nature & Weather
☀️ 🌤️ ⛅ 🌦️ 🌧️ 🌩️ 🌨️ ❄️ 💧 🌈 🌙 ⭐ 🌟 ✨

### Fun & Misc
🚀 🎯 🎲 🎮 🕹️ 🏆 🥇 💰 💵 🎁 🎉 🎊 ⚡ 🔥 💥

## Recommended Pairings

| Use Case | Icon |
|----------|------|
| Search | 🔍 🔎 |
| Web browser | 🌐 🌍 |
| Git/GitHub | 📦 🐙 |
| Terminal | 💻 ⌨️ |
| Files | 📁 📄 |
| Notes | 📝 ✏️ |
| Calendar | 📅 🗓️ |
| Timer | ⏱️ ⏲️ |
| Clipboard | 📋 📎 |
| Settings | ⚙️ 🔧 |
| Network | 📡 🌐 |
| Download | 📥 ⬇️ |
| Upload | 📤 ⬆️ |
| Refresh | 🔄 🔃 |
| Lock/Security | 🔒 🔑 |
| Notification | 🔔 📣 |
| Music | 🎵 🎧 |
| Video | 🎬 📹 |
| Image | 🖼️ 📷 |
| Database | 🗃️ 💾 |
| API | ⚡ 🔗 |
| Debug | 🐛 🔬 |
| Build | 🔨 🛠️ |
| Deploy | 🚀 📤 |
| Success | ✅ 🟢 |
| Error | ❌ 🔴 |
| Warning | ⚠️ 🟡 |

## Dark Theme Icons

Use `@raycast.iconDark` for theme-specific variants:

```bash
# @raycast.icon ☀️
# @raycast.iconDark 🌙
```

## Custom Icon Files

Local paths (relative to script or absolute):

```bash
# @raycast.icon ./icons/my-icon.png
# @raycast.icon /Users/me/icons/tool.png
```

Remote URLs (HTTPS only):

```bash
# @raycast.icon https://example.com/icon.png
```

Requirements:
- Format: PNG or JPEG
- Size: 64x64px recommended
- HTTPS required for remote URLs

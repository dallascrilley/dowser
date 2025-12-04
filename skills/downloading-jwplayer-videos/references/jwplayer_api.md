# JWPlayer JavaScript API Reference

## Overview

JWPlayer loads videos dynamically via JavaScript, making video URLs unavailable in static HTML or initial network requests. Access the player's JavaScript API to extract video sources.

## Key Concepts

**Player Instance**: Created via `jwplayer(elementId)` where `elementId` is the div ID (typically starts with `jwplayer-`).

**Playlist**: Contains one or more media items, each with sources (video URLs).

**Sources**: Array of video files with different formats (HLS, MP4, etc.).

## Finding JWPlayer Instances

### Method 1: Search for Player Divs

```javascript
// Find all JWPlayer div elements
const playerDivs = document.querySelectorAll('[id^="jwplayer-"]');

// Get player IDs
const playerIds = Array.from(playerDivs).map(div => div.id);
// Example: ["jwplayer-e_EyZmPEEHgt-674"]
```

### Method 2: Check for JWPlayer Global

```javascript
// Check if jwplayer function exists
if (typeof jwplayer === 'function') {
    console.log('JWPlayer detected');
}
```

### Method 3: Inspect Video Elements

```javascript
// Find video elements with blob: sources (indicates JWPlayer)
const videos = document.querySelectorAll('video');
videos.forEach(v => {
    if (v.src.startsWith('blob:')) {
        console.log('Possible JWPlayer video:', v);
        // Look for parent div with jwplayer- ID
        const container = v.closest('[id^="jwplayer-"]');
        if (container) {
            console.log('Player ID:', container.id);
        }
    }
});
```

## Accessing Player Instance

```javascript
// Get player instance by ID
const player = jwplayer('jwplayer-e_EyZmPEEHgt-674');

// Or get first available player
const firstPlayerDiv = document.querySelector('[id^="jwplayer-"]');
const player = jwplayer(firstPlayerDiv.id);
```

## Extracting Video URLs

### Method 1: getPlaylist() (Recommended)

```javascript
const player = jwplayer('jwplayer-e_EyZmPEEHgt-674');
const playlist = player.getPlaylist();

/*
Returns array of playlist items:
[
  {
    sources: [
      {
        file: "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8",
        type: "hls",
        label: "Auto"
      },
      {
        file: "https://example.com/video.mp4",
        type: "mp4",
        label: "720p"
      }
    ],
    title: "Video Title",
    image: "https://example.com/poster.jpg"
  }
]
*/

// Extract HLS URL (best quality, adaptive)
const hlsSource = playlist[0].sources.find(s => s.type === 'hls');
const videoUrl = hlsSource.file;
// "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8"
```

### Method 2: getConfig()

```javascript
const player = jwplayer('jwplayer-e_EyZmPEEHgt-674');
const config = player.getConfig();

// config.playlist contains same data as getPlaylist()
const videoUrl = config.playlist[0].sources[0].file;
```

### Method 3: getCurrentQuality() and getQualityLevels()

```javascript
// Get currently playing quality
const currentQuality = player.getCurrentQuality();

// Get all available qualities
const qualities = player.getQualityLevels();
/*
[
  { label: "360p", ... },
  { label: "720p", ... },
  { label: "1080p", ... }
]
*/
```

## Complete Extraction Script

```javascript
// Find all JWPlayer instances and extract video URLs
function extractAllJWPlayerVideos() {
    const playerDivs = document.querySelectorAll('[id^="jwplayer-"]');
    const results = [];

    playerDivs.forEach(div => {
        const playerId = div.id;

        try {
            const player = jwplayer(playerId);
            const playlist = player.getPlaylist();

            playlist.forEach((item, index) => {
                if (item.sources && item.sources.length > 0) {
                    item.sources.forEach(source => {
                        results.push({
                            player_id: playerId,
                            playlist_index: index,
                            title: item.title || 'Untitled',
                            file: source.file,
                            type: source.type,
                            label: source.label || 'default'
                        });
                    });
                }
            });
        } catch (e) {
            console.error(`Failed to access player ${playerId}:`, e);
        }
    });

    return results;
}

// Run extraction
const videos = extractAllJWPlayerVideos();
console.log(JSON.stringify(videos, null, 2));
```

## Common Video Types

| Type | Extension | Description | Download Tool |
|------|-----------|-------------|---------------|
| `hls` | `.m3u8` | HTTP Live Streaming (adaptive bitrate) | yt-dlp, ffmpeg |
| `mp4` | `.mp4` | Direct MP4 file | wget, curl, browser |
| `dash` | `.mpd` | MPEG-DASH (adaptive) | yt-dlp, ffmpeg |

**Recommendation**: Prefer HLS (`.m3u8`) sources when available - they provide best quality with adaptive bitrate.

## Downloading Extracted URLs

### HLS Streams (.m3u8)

```bash
yt-dlp "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8" \
  -o "video.%(ext)s"
```

### Direct MP4

```bash
# Using yt-dlp
yt-dlp "https://example.com/video.mp4" -o "video.mp4"

# Or wget
wget "https://example.com/video.mp4"
```

## Troubleshooting

### Player Not Found

```javascript
// Check if player exists
try {
    const player = jwplayer('jwplayer-abc123');
    console.log('Player found');
} catch (e) {
    console.error('Player not found:', e);
}
```

### Empty Playlist

Video may not be loaded yet. Wait for player to be ready:

```javascript
const player = jwplayer('jwplayer-abc123');

player.on('ready', function() {
    const playlist = player.getPlaylist();
    console.log('Playlist loaded:', playlist);
});
```

### Multiple Players on Page

```javascript
// Extract from all players
const allPlayerIds = Array.from(
    document.querySelectorAll('[id^="jwplayer-"]')
).map(div => div.id);

allPlayerIds.forEach(id => {
    const player = jwplayer(id);
    const playlist = player.getPlaylist();
    console.log(`Player ${id}:`, playlist);
});
```

## NBC News Specific Patterns

NBC news pages typically have:
- 1 main JWPlayer instance for the article video
- 2-3 ad players (can be ignored - usually CloudFront MP4s)
- Player IDs format: `jwplayer-[random]-[number]`

**Filter strategy**:
```javascript
// Ignore ad players (usually have short duration or "ad" in title)
const mainVideos = videos.filter(v => {
    return !v.title.toLowerCase().includes('ad') &&
           v.type === 'hls'; // Main video usually HLS
});
```

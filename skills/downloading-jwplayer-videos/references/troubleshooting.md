# Troubleshooting JWPlayer Video Extraction

## Common Errors and Solutions

### Error: "No video metadata found in webpage"

**Context**: yt-dlp's site-specific extractors fail

**Cause**: Video is loaded dynamically by JavaScript (JWPlayer) after page load, not present in initial HTML

**Solution**: Use browser automation to access JWPlayer API

```bash
# This will fail:
yt-dlp "https://www.nbcdfw.com/news/health/dementia-trial/.../3939062/"
# ERROR: [NBCStations] 3939062: No video metadata found in webpage

# Use browser automation instead (via Claude Code):
# 1. Navigate to page
# 2. Run JavaScript: jwplayer('player-id').getPlaylist()
# 3. Extract HLS URL from playlist
# 4. Download with yt-dlp using direct URL
```

### Error: "Cannot read properties of undefined (reading 'getPlaylist')"

**Cause**: Player ID is incorrect or player not initialized

**Solution**: Find correct player ID first

```javascript
// Find all JWPlayer instances
const playerDivs = document.querySelectorAll('[id^="jwplayer-"]');
console.log('Found players:', Array.from(playerDivs).map(d => d.id));

// Use correct ID
const player = jwplayer('jwplayer-e_EyZmPEEHgt-674');
const playlist = player.getPlaylist();
```

### Error: "jwplayer is not defined"

**Cause**: Page doesn't use JWPlayer, or script runs before JWPlayer loads

**Solutions**:

1. **Check if page uses JWPlayer**:
```javascript
typeof jwplayer // "function" if loaded, "undefined" if not
```

2. **Wait for JWPlayer to load**:
```javascript
// Poll until jwplayer is defined
function waitForJWPlayer() {
    return new Promise((resolve, reject) => {
        const checkInterval = setInterval(() => {
            if (typeof jwplayer !== 'undefined') {
                clearInterval(checkInterval);
                resolve();
            }
        }, 100);

        // Timeout after 10 seconds
        setTimeout(() => {
            clearInterval(checkInterval);
            reject(new Error('JWPlayer not found'));
        }, 10000);
    });
}

await waitForJWPlayer();
const player = jwplayer('player-id');
```

### Issue: Network Tab Shows No Video URL

**Context**: Inspecting network requests doesn't show `.m3u8` or `.mp4`

**Cause**:
- Video loads after initial page load
- Video URL is behind authentication/tokens
- Blob URLs used (JWPlayer's internal handling)

**Solution**: Don't rely on network inspection - use JWPlayer API instead

```javascript
// Network tab might show:
blob:https://example.com/uuid

// But JWPlayer API reveals actual URL:
const playlist = player.getPlaylist();
playlist[0].sources[0].file
// "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8"
```

### Issue: Multiple Video Elements Found

**Context**: Page has 3-4 `<video>` elements, unsure which is main content

**Patterns to identify main video**:

1. **Check for blob: URLs** (indicates JWPlayer):
```javascript
const videos = document.querySelectorAll('video');
videos.forEach(v => {
    if (v.src.startsWith('blob:')) {
        console.log('JWPlayer video:', v);
    }
});
```

2. **Check parent container**:
```javascript
// Main video usually in article content area
const mainContent = document.querySelector('article, .article-content');
const mainVideo = mainContent ? mainContent.querySelector('video') : null;
```

3. **Filter by duration** (ads are usually short):
```javascript
const videos = Array.from(document.querySelectorAll('video'));
const mainVideos = videos.filter(v => {
    return v.duration > 60; // Longer than 1 minute
});
```

4. **Use JWPlayer API and filter**:
```javascript
// Get all JWPlayer instances
const allPlayers = document.querySelectorAll('[id^="jwplayer-"]');

allPlayers.forEach(div => {
    const player = jwplayer(div.id);
    const playlist = player.getPlaylist();

    if (playlist[0]) {
        const title = playlist[0].title || '';
        const sources = playlist[0].sources || [];

        // Skip ads
        if (title.toLowerCase().includes('ad')) {
            console.log('Skipping ad player:', div.id);
            return;
        }

        // Main video usually has HLS source
        const hasHLS = sources.some(s => s.type === 'hls');
        if (hasHLS) {
            console.log('Main video player:', div.id);
            console.log('Sources:', sources);
        }
    }
});
```

### Issue: Download Fails with "HTTP Error 403: Forbidden"

**Cause**: Video URL requires authentication headers or is time-limited

**Solutions**:

1. **Extract cookies from browser**:
```bash
# Use browser extension to export cookies
yt-dlp --cookies cookies.txt "https://video-url.m3u8"
```

2. **Add referer header**:
```bash
yt-dlp --referer "https://www.nbcdfw.com/page" "https://video-url.m3u8"
```

3. **Download immediately** (URLs may expire):
```bash
# Extract and download in one command
yt-dlp "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8" -o "video.%(ext)s"
```

### Issue: HLS Download Fails or Hangs

**Symptoms**:
- `A hanging Promise was canceled`
- Download stalls at certain percentage
- Fragments fail to download

**Solutions**:

1. **Use native HLS downloader**:
```bash
yt-dlp --hls-prefer-native "https://video.m3u8"
```

2. **Use ffmpeg directly**:
```bash
ffmpeg -i "https://video.m3u8" -c copy output.mp4
```

3. **Increase fragment retries**:
```bash
yt-dlp --fragment-retries 10 "https://video.m3u8"
```

### Issue: Video Quality is Low

**Cause**: Wrong source selected from playlist

**Solution**: Check all available sources and select highest quality

```javascript
const playlist = player.getPlaylist();
const sources = playlist[0].sources;

// List all qualities
sources.forEach(source => {
    console.log(`${source.label}: ${source.file} (${source.type})`);
});

// HLS usually provides best quality (adaptive bitrate)
const bestSource = sources.find(s => s.type === 'hls') || sources[0];
console.log('Best source:', bestSource.file);
```

Or with yt-dlp:
```bash
# List available formats
yt-dlp -F "https://video.m3u8"

# Download best quality
yt-dlp -f best "https://video.m3u8"
```

## Workflow Decision Tree

```
Start: Need to download video from NBC news page
│
├─ Try yt-dlp directly with page URL
│  ├─ Success? → Download complete ✅
│  └─ Fails with "No video metadata"? → Continue
│
├─ Navigate to page with browser automation
│  │
│  ├─ Check for JWPlayer: document.querySelectorAll('[id^="jwplayer-"]')
│  │  ├─ No JWPlayer found?
│  │  │  └─ Try: Generic video extraction or check iframe
│  │  │
│  │  └─ JWPlayer found? → Continue
│  │
│  ├─ Extract video URLs: jwplayer('id').getPlaylist()
│  │  ├─ Empty playlist?
│  │  │  └─ Wait for player ready event, retry
│  │  │
│  │  └─ Playlist has sources? → Continue
│  │
│  ├─ Filter sources (skip ads, prefer HLS)
│  │
│  └─ Download with yt-dlp using direct URL
│     ├─ Success? → Download complete ✅
│     └─ Fails?
│        ├─ 403 Forbidden? → Add --referer or --cookies
│        ├─ HLS hangs? → Try --hls-prefer-native or ffmpeg
│        └─ Other error? → Check yt-dlp verbose output
```

## Quick Diagnostic Checklist

When extraction fails, run through this checklist:

- [ ] **Page loads completely?** Wait for content to appear
- [ ] **JWPlayer exists?** `typeof jwplayer` returns `"function"`
- [ ] **Player IDs found?** `document.querySelectorAll('[id^="jwplayer-"]').length > 0`
- [ ] **Player accessible?** `jwplayer('id')` doesn't throw error
- [ ] **Playlist loaded?** `player.getPlaylist().length > 0`
- [ ] **Sources present?** `playlist[0].sources.length > 0`
- [ ] **Valid URL?** Source file starts with `http://` or `https://`
- [ ] **yt-dlp installed?** `yt-dlp --version` works
- [ ] **URL not expired?** Download immediately after extraction

## Platform-Specific Notes

### NBC News (NBCStations)

- **Direct yt-dlp**: Usually fails with "No video metadata"
- **JWPlayer version**: Standard JWPlayer 8.x
- **Player naming**: `jwplayer-[random]-[number]`
- **Video types**: Primarily HLS (`.m3u8`)
- **Ad players**: 2-3 additional players with CloudFront MP4s (ignore)
- **CDN**: Akamaized (prodamdlim.akamaized.net)

### Similar Sites Using JWPlayer

This workflow applies to any site using JWPlayer:
- Local news sites (NBC, CBS, ABC affiliates)
- Sports streaming sites
- Educational platforms
- Corporate video libraries

**Detection**: Look for `jwplayer-` div IDs or `jwplayer.js` in page source.

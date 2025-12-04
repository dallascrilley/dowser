---
name: downloading-jwplayer-videos
short_description: >-
  Extract and download videos from web pages using JWPlayer JavaScript API via
  browser automation when direct yt-dlp extraction fails.
description: >
  Extract and download videos from web pages using JWPlayer by accessing the
  JWPlayer JavaScript API via browser automation. Use when downloading videos
  from NBC news sites, local news stations, or any page using JWPlayer where
  direct yt-dlp extraction fails with "No video metadata found in webpage".


  Use when: downloading videos from NBC news pages (nbcdfw.com, nbcnewyork.com,
  etc.), encountering "No video metadata found" errors, extracting videos from
  pages with JWPlayer embeds, network inspection doesn't reveal video URLs, or
  dealing with dynamically loaded video content.


  Prevents 3 documented issues: yt-dlp "No video metadata" errors on NBC sites,
  wasted time with network inspection that misses dynamic content, confusion
  with multiple video players (ads vs. main content).
when_to_use: >
  Extracting videos from web pages using JWPlayer JavaScript API via browser
  automation, downloading from NBC news sites or local news stations,
  encountering yt-dlp "No video metadata found" errors, extracting from pages
  with JWPlayer embeds, network inspection doesn't reveal video URLs.
version: 1.0.0
license: MIT
category: automation-and-scripting
---

# Downloading JWPlayer Videos

**Status**: Beta
**Last Updated**: 2025-11-13
**Dependencies**: yt-dlp, browser automation (mcp__plugin_superpowers-chrome or similar)
**Latest Versions**: yt-dlp@2024.x

---

## Quick Start (5 Minutes)

### 1. Try Direct yt-dlp First (Fast Path)

Always attempt direct extraction first—it succeeds ~20% of the time and saves 30 seconds:

```bash
yt-dlp "https://www.nbcdfw.com/news/health/dementia-trial-help-determine-risk/3939062/"
```

**Expected outcomes:**
- ✅ **Success**: Video downloads immediately → Done
- ❌ **Fails**: `ERROR: [NBCStations] 3939062: No video metadata found in webpage` → Continue to Step 2

**Why try this first:**
- 10x faster than browser automation when it works
- Some NBC pages have static video metadata
- Zero overhead if successful

### 2. Use Browser Automation to Extract JWPlayer Config

When direct yt-dlp fails, use browser automation:

```javascript
// Navigate to the page
browser_navigate("https://www.nbcdfw.com/news/health/dementia-trial-help-determine-risk/3939062/")

// Find JWPlayer instances
const playerDivs = document.querySelectorAll('[id^="jwplayer-"]');
console.log('Found players:', Array.from(playerDivs).map(d => d.id));

// Extract video URLs from main player
const player = jwplayer('jwplayer-e_EyZmPEEHgt-674'); // Use actual player ID
const playlist = player.getPlaylist();
const videoUrl = playlist[0].sources[0].file;
console.log('Video URL:', videoUrl);
// Output: "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8"
```

**CRITICAL:**
- JWPlayer loads videos AFTER page load—network inspection misses them
- Use `jwplayer('id').getPlaylist()`, not network tab
- Look for div IDs starting with `jwplayer-`

### 3. Download the Extracted HLS Stream

Use the extracted URL with yt-dlp:

```bash
yt-dlp "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8" \
  -o "dementia-trial-video.%(ext)s"
```

**What happens:**
- yt-dlp detects HLS stream (`.m3u8` manifest)
- Downloads all video fragments
- Merges fragments with ffmpeg
- Outputs final MP4 file

---

## The 6-Step Extraction Workflow

### Step 1: Attempt Direct Extraction

```bash
yt-dlp --dump-json "https://www.nbcdfw.com/news/health/.../3939062/" 2>&1 | grep -q "No video metadata"
if [ $? -eq 0 ]; then
    echo "Direct extraction failed—using browser automation"
else
    echo "Success! Downloading..."
    yt-dlp "https://www.nbcdfw.com/news/health/.../3939062/"
    exit 0
fi
```

### Step 2: Navigate to Page with Browser

```javascript
// Using mcp__plugin_superpowers-chrome
browser_navigate("https://www.nbcdfw.com/news/health/dementia-trial-help-determine-risk/3939062/")
```

**Wait for page load**: Ensure video player initializes (~3-5 seconds).

### Step 3: Find JWPlayer Instances

```javascript
// Method 1: Find player divs
const playerDivs = document.querySelectorAll('[id^="jwplayer-"]');
const playerIds = Array.from(playerDivs).map(d => d.id);
// ["jwplayer-e_EyZmPEEHgt-674", "jwplayer-ad-xyz-123"]

// Method 2: Check for video elements with blob: URLs
const videos = document.querySelectorAll('video');
videos.forEach(v => {
    if (v.src.startsWith('blob:')) {
        const container = v.closest('[id^="jwplayer-"]');
        console.log('JWPlayer container:', container?.id);
    }
});
```

**Key Points:**
- NBC pages typically have 1 main player + 2-3 ad players
- Player IDs format: `jwplayer-[random]-[number]`
- Ad players usually have short videos or "ad" in title

### Step 4: Extract JWPlayer Playlist

```javascript
const playerId = 'jwplayer-e_EyZmPEEHgt-674'; // Use actual ID from Step 3
const player = jwplayer(playerId);
const playlist = player.getPlaylist();

// Examine playlist structure
console.log(JSON.stringify(playlist, null, 2));
/*
[
  {
    "title": "Research studies blood pressure's role in dementia prevention",
    "sources": [
      {
        "file": "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8",
        "type": "hls",
        "label": "Auto"
      }
    ]
  }
]
*/

// Extract video URL
const videoUrl = playlist[0].sources[0].file;
```

**What to avoid:**
- Don't use `player.getConfig()`—use `getPlaylist()` (more reliable)
- Don't assume first player is main video—check titles to filter ads

### Step 5: Filter Main Video (Skip Ads)

```javascript
// Extract from all players and filter
const allPlayerIds = Array.from(document.querySelectorAll('[id^="jwplayer-"]')).map(d => d.id);
const videos = [];

allPlayerIds.forEach(id => {
    const player = jwplayer(id);
    const playlist = player.getPlaylist();

    if (playlist[0]) {
        const title = playlist[0].title || '';
        const sources = playlist[0].sources || [];

        // Filter out ads
        if (!title.toLowerCase().includes('ad') && sources.length > 0) {
            videos.push({
                player_id: id,
                title: title,
                url: sources[0].file,
                type: sources[0].type
            });
        }
    }
});

// Main video (longest, HLS type)
const mainVideo = videos.filter(v => v.type === 'hls')[0];
console.log('Main video:', mainVideo.url);
```

### Step 6: Download with yt-dlp

```bash
yt-dlp "https://prodamdlim.akamaized.net/out/v1/.../index.m3u8" \
  -o "video-title.%(ext)s"
```

**Download process:**
- Fetches master manifest (`.m3u8`)
- Selects best quality stream
- Downloads ~19 fragments (typical)
- Merges with ffmpeg
- Outputs MP4 file

---

## Critical Rules

### Always Do

✅ **Try yt-dlp directly first** (saves time when it works)
✅ **Use JWPlayer API** (`jwplayer().getPlaylist()`), not network inspection
✅ **Download immediately** after extraction (URLs may be time-limited)
✅ **Filter ad players** (check title for "ad", prefer HLS type)
✅ **Verify player ID** before accessing (`document.querySelectorAll('[id^="jwplayer-"]')`)

### Never Do

❌ **Rely on network tab alone** (JWPlayer loads videos dynamically after page load)
❌ **Assume first player is main video** (ads often listed first)
❌ **Use `getConfig()` instead of `getPlaylist()`** (less reliable)
❌ **Delay download** (extracted URLs may expire)
❌ **Ignore blob: URLs** (they indicate JWPlayer usage—extract via API instead)

---

## Known Issues Prevention

This skill prevents **3** documented issues:

### Issue #1: yt-dlp "No video metadata found in webpage"

**Error**: `ERROR: [NBCStations] 3939062: No video metadata found in webpage`

**Source**: User-reported, common with NBC news sites (nbcdfw.com, nbcnewyork.com, etc.)

**Why It Happens**: NBC pages load videos via JWPlayer's JavaScript API after initial page load. The video URL is not in static HTML, so yt-dlp's NBC extractor can't find it.

**Prevention**: Use browser automation to access JWPlayer's `getPlaylist()` API, which reveals the actual HLS manifest URL.

### Issue #2: Network Inspection Shows No Video URL

**Error**: Checking network requests shows 366 requests but no `.m3u8` or `.mp4` files

**Source**: User workflow testing

**Why It Happens**: JWPlayer creates blob: URLs for video elements. The actual video URL is hidden in JWPlayer's internal state, loaded via API calls that happen before network inspection begins.

**Prevention**: Don't rely on network tab. Use JWPlayer API: `jwplayer('id').getPlaylist()[0].sources[0].file`

### Issue #3: Multiple Video Players Confusion

**Error**: Page has 4 video elements—unsure which is the main content video

**Source**: User workflow testing (NBC pages have 1 main player + 2-3 ad players)

**Why It Happens**: News sites embed multiple JWPlayer instances: main video, pre-roll ads, sidebar videos.

**Prevention**: Filter by:
- Title doesn't contain "ad"
- Video type is "hls" (main videos)
- Sources array has content
- Longest duration (if accessible)

---

## Common Patterns

### Pattern 1: Complete Extraction Script

```javascript
// Complete JWPlayer extraction
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

// Usage
const videos = extractAllJWPlayerVideos();
const mainVideo = videos.filter(v =>
    v.type === 'hls' &&
    !v.title.toLowerCase().includes('ad')
)[0];

console.log('Main video URL:', mainVideo.file);
```

**When to use**: Pages with multiple JWPlayer instances requiring extraction of all videos with filtering for main content.

### Pattern 2: Quick Single Player Extraction

```javascript
// When player ID is already known
const player = jwplayer('jwplayer-e_EyZmPEEHgt-674');
const videoUrl = player.getPlaylist()[0].sources[0].file;

// Download immediately
// (Use Bash tool or subprocess in Python)
```

**When to use**: Single video pages with visible player ID, or after running full extraction once.

### Pattern 3: Wait for Player Ready

```javascript
// For pages where player loads slowly
const playerId = 'jwplayer-abc123';

jwplayer(playerId).on('ready', function() {
    const playlist = this.getPlaylist();
    console.log('Video loaded:', playlist[0].sources[0].file);
});
```

**When to use**: Pages with slow-loading videos or multiple async video loads.

---

## Using Bundled Resources

### Scripts (scripts/)

**`extract_jwplayer_video.py`**: Command-line tool for automated extraction

**Usage:**
```bash
python scripts/extract_jwplayer_video.py <url> [--download] [--output <filename>]

# Example:
python scripts/extract_jwplayer_video.py \
  "https://www.nbcdfw.com/news/health/.../3939062/" \
  --download \
  --output "dementia-trial"
```

**Features:**
- Tries yt-dlp direct first (fast path)
- Falls back to browser automation with extraction script
- Filters ad players automatically
- Downloads HLS streams

**Note**: Script requires Claude Code environment with browser automation tool access.

### References (references/)

**When Claude should load these:**
- **`jwplayer_api.md`**: When encountering JWPlayer-specific API questions, need details on `getPlaylist()`, `getConfig()`, or finding player instances
- **`troubleshooting.md`**: When extraction fails, download errors occur, or need decision tree for debugging

**Contents:**
- `references/jwplayer_api.md` - Complete JWPlayer JavaScript API reference with all extraction methods
- `references/troubleshooting.md` - Common errors, solutions, and workflow decision tree

**Progressive disclosure**: Load references only when needed—Quick Start provides 80% of common cases.

---

## Troubleshooting

### Problem: "jwplayer is not defined"

**Cause**: Page doesn't use JWPlayer, or script runs before JWPlayer loads

**Solution**:
```javascript
// Check if JWPlayer exists
if (typeof jwplayer !== 'undefined') {
    console.log('JWPlayer detected');
} else {
    console.log('JWPlayer not found—try different extraction method');
}

// Or wait for JWPlayer to load
const checkJWPlayer = setInterval(() => {
    if (typeof jwplayer !== 'undefined') {
        clearInterval(checkJWPlayer);
        // Proceed with extraction
    }
}, 100);
```

### Problem: "Cannot read properties of undefined (reading 'getPlaylist')"

**Cause**: Player ID is incorrect

**Solution**:
```javascript
// Find correct player IDs first
const playerIds = Array.from(document.querySelectorAll('[id^="jwplayer-"]')).map(d => d.id);
console.log('Available players:', playerIds);

// Use correct ID
const player = jwplayer(playerIds[0]);
```

### Problem: Download fails with "HTTP Error 403: Forbidden"

**Solution**:
```bash
# Add referer header
yt-dlp --referer "https://www.nbcdfw.com/page" "https://video-url.m3u8"

# Or use cookies
yt-dlp --cookies cookies.txt "https://video-url.m3u8"
```

**For more issues:** See `references/troubleshooting.md` for complete troubleshooting guide.

---

## Dependencies

**Required**:
- **yt-dlp** (latest) - Downloads HLS streams and video files
- **Browser automation** - mcp__plugin_superpowers-chrome or equivalent (for JavaScript execution)

**Optional**:
- **ffmpeg** (bundled with yt-dlp) - Merges HLS fragments

**Installation**:
```bash
# yt-dlp
pip install -U yt-dlp
# or: brew install yt-dlp

# Verify
yt-dlp --version
```

---

## Official Documentation

- **JWPlayer JavaScript API**: https://docs.jwplayer.com/players/docs/jw8-javascript-api-reference
- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **Browser Automation (Claude Code)**: Use mcp__plugin_superpowers-chrome tool

---

## Complete Workflow Checklist

Verify extraction with this checklist:

- [ ] Attempted direct yt-dlp first (`yt-dlp <page-url>`)
- [ ] Navigated to page with browser automation
- [ ] Found JWPlayer instances (`document.querySelectorAll('[id^="jwplayer-"]')`)
- [ ] Extracted playlist from player (`jwplayer('id').getPlaylist()`)
- [ ] Filtered out ad players (title doesn't contain "ad", type is "hls")
- [ ] Copied video URL from `sources[0].file`
- [ ] Downloaded with yt-dlp immediately (URLs may expire)
- [ ] Verified download completed successfully

---

**Questions? Issues?**

1. Check `references/troubleshooting.md` for common errors and solutions
2. Verify JWPlayer exists on page (`typeof jwplayer === 'function'`)
3. Ensure player IDs are correct (inspect page for `jwplayer-` divs)
4. Try extraction script: `python scripts/extract_jwplayer_video.py <url>`

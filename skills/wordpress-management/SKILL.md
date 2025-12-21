---
name: wordpress-management
description: >-
  Manage WordPress sites using Visual Composer (WPBakery) page builder. Use when
  updating WordPress pages, replacing images in team grids, editing Visual
  Composer shortcodes, or working with WPEngine-hosted sites. Teaches hybrid
  workflow using wp-cli for operations and browser for verification.
when_to_use: >-
  Use when managing WordPress sites with Visual Composer (WPBakery) page
  builder, updating WordPress page content programmatically, replacing images in
  team member grids or galleries, editing Visual Composer shortcodes via wp-cli,
  working with WPEngine-hosted sites (with SSH/wp-cli access)...
version: 1.0.0
category: integrations-and-saas
---

# WordPress Management (Visual Composer)

**Announce:** "I'm using the wordpress-management skill to update this WordPress page."

## Overview

Manage WordPress pages built with Visual Composer (WPBakery) using a hybrid approach:
- **wp-cli** for reliable, deterministic operations
- **Browser** for discovery and verification

Visual Composer stores content as **plain text shortcodes** in post_content, making it simple to edit programmatically.

## When to Use

**Use this skill when:**
- Updating content on Visual Composer/WPBakery pages
- Replacing images in team member grids or galleries
- Editing Visual Composer shortcodes programmatically
- Working with WPEngine-hosted WordPress sites

**Don't use for:**
- Elementor pages (different storage format)
- Gutenberg block editor pages
- Classic WordPress editor pages

## Quick Start Workflow

### 1. Discovery & Backup

**Get page ID** (browser method - fastest):
```javascript
// Navigate to the page, then extract ID from body class
document.body.className
// Returns: "... page-id-12345 ..."
```

**Backup before editing:**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" > temp/backups/POST_ID-page.txt
```

### 2. Upload Media (if replacing images)

**For WPEngine (no SCP), use chunked transfer:**
```bash
# Split large image (50KB chunks)
split -b 50000 your-image.jpg chunk-

# Transfer chunks
for chunk in chunk-*; do
  ssh user@host "cat > /tmp/$(basename $chunk)" < "$chunk"
done

# Reassemble and import to WordPress
ssh user@host "cd sites/sitename && \
cat /tmp/chunk-* > /tmp/your-image.jpg && \
wp media import /tmp/your-image.jpg \
--title='Image Title' \
--alt='Image Alt Text' \
--porcelain"
# Returns: NEW_MEDIA_ID (note this for next step)
```

### 3. Edit Shortcode Content

**Get current content:**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" > temp/content.txt
```

**Edit locally** in `temp/content.txt`:
```
# Example: Update image ID in team member shortcode
# Find:    [team_member image_url="12345" name="Person"
# Replace: [team_member image_url="NEW_MEDIA_ID" name="Person"
```

**Update post:**
```bash
ssh user@host "cd sites/sitename && \
wp post update POST_ID --post_content=\"\$(cat)\"" < temp/content.txt
```

### 4. Verify Changes

**Navigate to page and hard refresh:**
- URL: `http://site.com/page-slug/`
- Clear browser cache or use incognito
- Take screenshot to compare
- Visual Composer may cache aggressively

## Common Visual Composer Shortcodes

### Team Member
```
[team_member
  image_url="MEDIA_ID"
  name="Person Name"
  job_position="Title"
][/team_member]
```

### Single Image
```
[vc_single_image
  image="MEDIA_ID"
  img_size="full"
]
```

### Text Block
```
[vc_column_text]
Your content here
[/vc_column_text]
```

### Row/Column Layout
```
[vc_row][vc_column width="1/2"]
  Content here
[/vc_column][vc_column width="1/2"]
  Content here
[/vc_column][/vc_row]
```

## Helper Scripts

### Get Post ID by Slug
```bash
python scripts/get_post_id.py --host user@host --site sites/sitename --slug page-slug
```

### Save Post Content with Backup
```bash
python scripts/save_post_content.py \
  --host user@host \
  --site sites/sitename \
  --post-id POST_ID \
  --content-file temp/content.txt
```

## WPEngine Limitations

**What Doesn't Work:**
- ❌ SCP file transfers (blocked)
- ❌ Large inline transfers (> 100KB)

**What Works:**
- ✅ wp-cli via SSH
- ✅ Chunked file transfers (< 50KB per chunk)
- ✅ WordPress REST API (with auth)

## Tips & Troubleshooting

**Always use wp-cli for operations:**
Deterministic, scriptable, no session timeouts.

**Chunk large files:**
Split images > 100KB before transfer to WPEngine.

**Backup before editing:**
Visual Composer content is one large text block - easy to corrupt.

**Changes not visible:**
- Hard refresh (Cmd+Shift+R / Ctrl+F5)
- Wait 30s for server-side caching
- Clear WordPress cache if active

**Media upload fails:**
- Check file size (split if > 50KB per chunk)
- Verify /tmp is writable
- Use --porcelain flag to get media ID

## Detailed Documentation

For comprehensive workflows, examples, and troubleshooting:
- See [REFERENCE.md](REFERENCE.md) for detailed workflows
- See [references/vc_shortcodes.txt](references/vc_shortcodes.txt) for complete shortcode list
- See [skills/browsing/SKILL.md](skills/browsing/SKILL.md) for browser automation details

## Real-World Example

**Task:** Replace team member photo

```bash
# 1. Get page ID (from browser): page-id-10883
# 2. Backup
ssh user@host "cd sites/sitename && \
wp post get 10883 --field=post_content" > temp/backups/10883-team.txt

# 3. Upload photo (chunked)
split -b 50000 headshot.jpg chunk-
for chunk in chunk-*; do
  ssh user@host "cat > /tmp/$(basename $chunk)" < "$chunk"
done
ssh user@host "cd sites/sitename && \
cat /tmp/chunk-* > /tmp/headshot.jpg && \
wp media import /tmp/headshot.jpg --title='Team Member' --porcelain"
# Returns: 33456

# 4. Edit shortcode
ssh user@host "cd sites/sitename && \
wp post get 10883 --field=post_content" > temp/content.txt
# In temp/content.txt: image_url="OLD_ID" → image_url="33456"

# 5. Update
ssh user@host "cd sites/sitename && \
wp post update 10883 --post_content=\"\$(cat)\"" < temp/content.txt

# 6. Verify at http://site.com/team/
```

## Related Skills

- **browsing**: Browser automation for verification
- **systematic-debugging**: Troubleshooting workflow issues
- **verification-before-completion**: Always verify changes work

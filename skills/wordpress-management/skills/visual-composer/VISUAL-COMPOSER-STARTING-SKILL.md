---
name: visual-composer-management
description: Use when updating WordPress pages built with Visual Composer (WPBakery) page builder - teaches hybrid workflow using wp-cli for deterministic operations and browser for discovery/verification, handles shortcode editing, media uploads, and WPEngine limitations
---

# Visual Composer Page Management

## Overview

Manage WordPress pages built with Visual Composer (WPBakery) using a hybrid approach: wp-cli for reliable operations, browser for discovery and verification.

**Announce:** "I'm using the visual-composer-management skill to update this WordPress page."

## When to Use

**Use this when:**
- Updating content on Visual Composer/WPBakery pages
- Replacing images in team member grids or galleries
- Editing Visual Composer shortcodes programmatically
- Working with WPEngine-hosted WordPress sites

**Don't use for:**
- Elementor pages (use wp-elementor-mcp instead)
- Gutenberg block editor pages
- Classic WordPress editor pages

## Core Principle

Visual Composer stores content as **plain text shortcodes** in post_content. You can edit them via wp-cli without touching the WordPress admin UI.

**Example Shortcodes:**
```
[team_member image_url="12345" name="Person Name" job_position="Title"][/team_member]
[vc_column_text]Your content here[/vc_column_text]
[vc_single_image image="67890" img_size="full"]
```

All editable as plain text with find-and-replace.

## Recommended Workflow

### Phase 1: Discovery (Browser + wp-cli)

**1.1 Get Page ID**

Method A - From frontend (fastest):
```javascript
// Navigate to page, then extract ID
document.body.className
// Returns: "... page-id-12345 ..."
```

Method B - Via wp-cli:
```bash
ssh user@host "cd sites/sitename && \
wp post list --post_type=page --name=PAGE_SLUG \
--fields=ID,post_title --format=json"
```

**1.2 Inspect Current State**

Navigate to frontend page with browser:
- Identify content to change (images, text, layout)
- Take screenshot for reference
- Note current values (image IDs, text content, shortcode parameters)

### Phase 2: Backup (wp-cli)

**Always backup before editing:**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" > temp/backups/POST_ID-PAGE_NAME.txt
```

### Phase 3: Media Upload (wp-cli, if needed)

**Skip this phase if only editing text content.**

**For WPEngine (no SCP access), use chunked transfer:**

```bash
# 1. Split large image into chunks (50KB each)
split -b 50000 your-image.jpg chunk-

# 2. Transfer chunks to server
for chunk in chunk-*; do
  ssh user@host "cat > /tmp/$(basename $chunk)" < "$chunk"
done

# 3. Reassemble and import to WordPress
ssh user@host "cd sites/sitename && \
cat /tmp/chunk-* > /tmp/your-image.jpg && \
wp media import /tmp/your-image.jpg \
--title='Image Title' \
--alt='Image Alt Text' \
--porcelain"
# Returns: NEW_MEDIA_ID (note this for next step)
```

**Note the media ID** returned by `--porcelain` flag.

### Phase 4: Edit Shortcode (wp-cli)

**4.1 Get Current Content**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" > temp/content.txt
```

**4.2 Edit Locally**

Find and replace the specific shortcode parameter in `temp/content.txt`.

**Examples:**

Update image ID:
```
# Find:
[team_member image_url="12345" name="Person Name"

# Replace:
[team_member image_url="NEW_MEDIA_ID" name="Person Name"
```

Update text content:
```
# Find:
[vc_column_text]Old text content[/vc_column_text]

# Replace:
[vc_column_text]New text content[/vc_column_text]
```

Change layout width:
```
# Find:
[vc_column width="1/3"]

# Replace:
[vc_column width="1/2"]
```

**4.3 Update Post**
```bash
ssh user@host "cd sites/sitename && \
wp post update POST_ID --post_content=\"\$(cat)\"" < temp/content.txt
```

### Phase 5: Verification (Browser)

**5.1 Navigate to Page**
```
http://site.com/page-slug/
```

**5.2 Hard Refresh**
- Clear browser cache or use incognito
- Visual Composer may cache aggressively

**5.3 Verify Changes**
- Screenshot updated page
- Compare with original screenshot
- Document in temp/ folder

## Common Visual Composer Shortcodes

### Team Member
```
[team_member
  image_url="MEDIA_ID"
  team_memeber_style="meta_below"
  name="Person Name"
  job_position="Title"
  image_size="225x225"
][/team_member]
```

### Image
```
[vc_single_image
  image="MEDIA_ID"
  img_size="full"
  alignment="center"
]
```

### Text Block
```
[vc_column_text]
Your HTML or text content here
[/vc_column_text]
```

### Row and Column Structure
```
[vc_row][vc_column width="1/2"]
  Content here
[/vc_column][vc_column width="1/2"]
  Content here
[/vc_column][/vc_row]
```

## WPEngine-Specific Limitations

**What Doesn't Work:**
- ❌ SCP file transfers (blocked)
- ❌ SFTP via SSH
- ❌ Large inline base64 transfers (> 100KB)

**What Works:**
- ✅ wp-cli via SSH
- ✅ Chunked file transfers (< 50KB per chunk)
- ✅ WordPress REST API (with auth)

## Tips

**Always use wp-cli for operations:**
Deterministic, scriptable, no session timeouts.

**Chunk large files:**
Split images > 100KB before transfer to WPEngine.

**Backup before editing:**
Visual Composer content is one large text block - easy to corrupt.

**Test on staging first:**
If available, test workflow on staging environment.

**Session timeouts:**
WordPress admin sessions expire quickly (< 5 min). Don't rely on persistent browser sessions for multi-step operations.

**Find shortcode patterns:**
Use grep to find specific shortcodes:
```bash
grep -o '\[team_member[^]]*\]' temp/content.txt
```

## Troubleshooting

**Media upload fails:**
- Check file size (split if > 50KB per chunk)
- Verify /tmp is writable on server
- Use --porcelain flag to see media ID

**Changes not visible:**
- Hard refresh browser (Cmd+Shift+R / Ctrl+F5)
- Clear WordPress cache if caching plugin active
- Wait 30 seconds for server-side caching

**Shortcode broken after edit:**
- Restore from backup
- Verify all brackets are balanced
- Check for special characters needing escaping

**wp-cli not found:**
- Verify SSH path: `cd sites/sitename`
- Check wp-cli installed: `which wp`

## Real-World Examples

### Example 1: Update Team Member Photo

**Task:** Replace a team member's placeholder image with their actual headshot

```bash
# 1. Get page ID - Found: page-id-10883
# 2. Backup
ssh user@host "cd sites/sitename && \
wp post get 10883 --field=post_content" > temp/backups/10883-team-page.txt

# 3. Upload new photo (chunked for WPEngine)
split -b 50000 new-headshot.jpg chunk-
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
# In temp/content.txt, change: image_url="OLD_ID" → image_url="33456"

# 5. Update post
ssh user@host "cd sites/sitename && \
wp post update 10883 --post_content=\"\$(cat)\"" < temp/content.txt

# 6. Verify at http://site.com/team-page/
```

### Example 2: Update Text Content

**Task:** Change company address in footer section

```bash
# 1. Get page ID - Found: page-id-45
# 2. Backup
ssh user@host "cd sites/sitename && \
wp post get 45 --field=post_content" > temp/backups/45-contact.txt

# 3. Edit text (no media upload needed)
ssh user@host "cd sites/sitename && \
wp post get 45 --field=post_content" > temp/content.txt
# In temp/content.txt, find [vc_column_text] with old address
# Replace with new address

# 4. Update post
ssh user@host "cd sites/sitename && \
wp post update 45 --post_content=\"\$(cat)\"" < temp/content.txt

# 5. Verify at http://site.com/contact/
```

### Example 3: Change Column Layout

**Task:** Convert 3-column layout to 2-column

```bash
# 1. Get page ID - Found: page-id-78
# 2. Backup
ssh user@host "cd sites/sitename && \
wp post get 78 --field=post_content" > temp/backups/78-services.txt

# 3. Edit layout (no media upload)
ssh user@host "cd sites/sitename && \
wp post get 78 --field=post_content" > temp/content.txt
# In temp/content.txt:
# Change: [vc_column width="1/3"] → [vc_column width="1/2"]
# Remove third column entirely

# 4. Update post
ssh user@host "cd sites/sitename && \
wp post update 78 --post_content=\"\$(cat)\"" < temp/content.txt

# 5. Verify at http://site.com/services/
```

## Files Created

Recommended temp file structure:
```
temp/
├── backups/
│   └── POST_ID-PAGE_NAME.txt
├── content.txt (current working copy)
└── screenshots/
    ├── before.png
    └── after.png
```

## Related Skills

- **browsing**: For browser automation techniques
- **systematic-debugging**: If encountering issues
- **verification-before-completion**: Always verify changes work

## Key Difference from Elementor

| Aspect | Visual Composer | Elementor |
|--------|----------------|-----------|
| **Storage** | Shortcodes in post_content | JSON in post meta |
| **Editing** | Text find-replace via wp-cli | Specialized MCP tools |
| **Structure** | Nested shortcodes | Nested JSON objects |
| **CLI Access** | Direct via wp post update | Requires special handling |

Visual Composer is **simpler to edit programmatically** because it's plain text.

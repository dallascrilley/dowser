# WordPress Visual Composer - Detailed Reference

This document provides comprehensive workflows, examples, and troubleshooting for managing Visual Composer pages.

## Table of Contents

- [Core Principles](#core-principles)
- [Detailed Workflow](#detailed-workflow)
- [Visual Composer Shortcode Reference](#visual-composer-shortcode-reference)
- [Advanced Techniques](#advanced-techniques)
- [WPEngine-Specific Workflows](#wpengine-specific-workflows)
- [Complete Examples](#complete-examples)
- [Troubleshooting Guide](#troubleshooting-guide)

---

## Core Principles

### Visual Composer Storage Format

Visual Composer stores ALL page content as **nested shortcodes** in the `post_content` database field.

**Example raw content:**
```
[vc_row][vc_column width="1/2"]
[vc_column_text]Welcome to our company[/vc_column_text]
[/vc_column][vc_column width="1/2"]
[vc_single_image image="12345" img_size="full"]
[/vc_column][/vc_row]
```

This is **plain text**, making it editable via:
- Direct string find-and-replace
- Regular expressions
- wp-cli commands

### Why This Matters

Unlike Elementor (which uses JSON in post meta), Visual Composer content can be edited with simple text operations. No special parsing required.

---

## Detailed Workflow

### Phase 1: Discovery & Analysis

#### Method 1: Browser-Based Page ID Discovery (Fastest)

**Step 1:** Navigate to the target page
```
http://yoursite.com/page-slug/
```

**Step 2:** Extract page ID from body class
```javascript
// Run in browser console
document.body.className
// Example output: "page-template page-id-10883 page-slug-team"
```

**Step 3:** Note the ID (10883 in this example)

#### Method 2: wp-cli Page ID Discovery

**By slug:**
```bash
ssh user@host "cd sites/sitename && \
wp post list --post_type=page --name=PAGE_SLUG \
--fields=ID,post_title --format=json"
```

**By title:**
```bash
ssh user@host "cd sites/sitename && \
wp post list --post_type=page --s='Page Title' \
--fields=ID,post_title --format=json"
```

#### Method 3: Python Helper Script

```bash
python scripts/get_post_id.py \
  --host user@host \
  --site sites/sitename \
  --slug page-slug
```

#### Inspecting Current Page Content

**View in browser:**
- Take screenshot of current state
- Note what needs changing (images, text, layout)
- Identify specific sections/elements

**View raw shortcode:**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" | head -50
```

**Find specific shortcodes:**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" | \
grep -o '\[team_member[^]]*\]'
```

---

### Phase 2: Backup Strategy

**Always create backups before editing.**

#### Basic Backup
```bash
# Create backup directory
mkdir -p temp/backups

# Backup post content
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" > temp/backups/POST_ID-$(date +%Y%m%d).txt
```

#### Backup with Metadata
```bash
# Full post backup (including meta)
ssh user@host "cd sites/sitename && \
wp post get POST_ID --format=json" > temp/backups/POST_ID-full.json
```

#### Automated Backup Script
```bash
# scripts/backup_post.sh
#!/bin/bash
POST_ID=$1
SITE_PATH=$2
BACKUP_DIR="temp/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

ssh user@host "cd $SITE_PATH && \
wp post get $POST_ID --field=post_content" > \
"$BACKUP_DIR/${POST_ID}-${TIMESTAMP}.txt"

echo "Backed up to: $BACKUP_DIR/${POST_ID}-${TIMESTAMP}.txt"
```

---

### Phase 3: Media Upload (For Image Replacements)

**Skip this phase if only editing text content.**

#### Understanding WPEngine Limitations

WPEngine blocks:
- SCP/SFTP transfers
- Large stdin/heredoc transfers (> 100KB)
- Binary file uploads via command substitution

WPEngine allows:
- Small file chunks via stdin (< 50KB recommended)
- wp media import from server filesystem
- WordPress REST API uploads (with authentication)

#### Chunked Transfer Method (Recommended)

**Step 1: Split file into chunks**
```bash
# Split into 50KB chunks (safe for WPEngine)
split -b 50000 your-image.jpg chunk-

# Verify chunks created
ls -lh chunk-*
```

**Step 2: Transfer chunks to server**
```bash
# Transfer each chunk
for chunk in chunk-*; do
  echo "Transferring $chunk..."
  ssh user@host "cat > /tmp/$(basename $chunk)" < "$chunk"
done
```

**Step 3: Reassemble and import**
```bash
ssh user@host "cd sites/sitename && \
cat /tmp/chunk-* > /tmp/your-image.jpg && \
wp media import /tmp/your-image.jpg \
--title='Image Title' \
--alt='Alt Text Description' \
--caption='Image Caption' \
--porcelain"
# Output: 33456 (new media ID)
```

**Step 4: Clean up server temp files**
```bash
ssh user@host "rm /tmp/chunk-* /tmp/your-image.jpg"
```

**Step 5: Clean up local chunks**
```bash
rm chunk-*
```

#### Alternative: REST API Upload (For Larger Files)

**Requires authentication token.**

```bash
# Get auth token (Basic Auth or JWT)
AUTH_TOKEN="your-token-here"

# Upload via REST API
curl -X POST \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Disposition: attachment; filename=image.jpg" \
  -H "Content-Type: image/jpeg" \
  --data-binary @your-image.jpg \
  https://yoursite.com/wp-json/wp/v2/media
```

#### Verifying Media Upload

```bash
# Get media ID from previous command (porcelain output)
MEDIA_ID=33456

# Verify upload succeeded
ssh user@host "cd sites/sitename && \
wp media get $MEDIA_ID --field=guid"
# Returns: URL of uploaded image
```

---

### Phase 4: Editing Shortcode Content

#### Step-by-Step Process

**Step 1: Download current content**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" > temp/content.txt
```

**Step 2: Edit locally**

Open `temp/content.txt` and make changes.

**Common edit patterns:**

**A. Update image ID:**
```
# Find:
[team_member image_url="12345"

# Replace:
[team_member image_url="33456"
```

**B. Update text content:**
```
# Find:
[vc_column_text]Old company address[/vc_column_text]

# Replace:
[vc_column_text]New company address[/vc_column_text]
```

**C. Change layout:**
```
# Find:
[vc_column width="1/3"]

# Replace:
[vc_column width="1/2"]
```

**Step 3: Validate edits**

**Check bracket balance:**
```bash
# Count opening brackets
grep -o '\[' temp/content.txt | wc -l

# Count closing brackets
grep -o '\]' temp/content.txt | wc -l
# Should match
```

**Check for common errors:**
```bash
# Look for unclosed shortcodes
grep -n '\[vc_[a-z_]*[^]]*$' temp/content.txt
```

**Step 4: Upload edited content**
```bash
ssh user@host "cd sites/sitename && \
wp post update POST_ID --post_content=\"\$(cat)\"" < temp/content.txt
```

**Step 5: Verify update succeeded**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_modified"
# Should show recent timestamp
```

---

### Phase 5: Verification

#### Browser Verification

**Step 1: Navigate to page**
```
http://yoursite.com/page-slug/
```

**Step 2: Hard refresh**
- **Mac:** Cmd + Shift + R
- **Windows:** Ctrl + F5
- **Or:** Use incognito/private window

**Step 3: Visual inspection**
- Compare with "before" screenshot
- Verify all changes applied
- Check for layout breaks or missing content

**Step 4: Take "after" screenshot**
```bash
# Save to temp/screenshots/
mkdir -p temp/screenshots
# Use browser screenshot tool
```

#### Cache Clearing (If Changes Not Visible)

**WordPress object cache:**
```bash
ssh user@host "cd sites/sitename && \
wp cache flush"
```

**WPEngine cache:**
```bash
ssh user@host "cd sites/sitename && \
wp cache flush && \
wp w3-total-cache flush all"
```

**Browser cache:**
- Clear browser cache manually
- Or use incognito/private mode

#### Programmatic Verification

**Check specific shortcode exists:**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" | \
grep -q "image_url=\"33456\"" && \
echo "✅ Image ID updated" || \
echo "❌ Image ID not found"
```

---

## Visual Composer Shortcode Reference

### Layout Shortcodes

#### Row
```
[vc_row
  full_width="stretch_row"
  css=".vc_custom_class"
][/vc_row]
```

**Common attributes:**
- `full_width`: "stretch_row", "stretch_row_content_no_spaces"
- `css`: Custom CSS classes
- `el_id`: Element ID for anchoring

#### Column
```
[vc_column
  width="1/2"
  offset="vc_col-lg-4 vc_col-md-6"
][/vc_column]
```

**Width values:**
- `1/1` (full width)
- `1/2`, `1/3`, `1/4`, `1/6`
- `2/3`, `3/4`, `5/6`

**Responsive offsets:**
- `vc_col-lg-4` (large screens: 4 columns)
- `vc_col-md-6` (medium screens: 6 columns)
- `vc_col-sm-12` (small screens: 12 columns)

#### Inner Row/Column
```
[vc_row_inner][vc_column_inner width="1/2"][/vc_column_inner][/vc_row_inner]
```

### Content Shortcodes

#### Text Block
```
[vc_column_text]
<h2>Heading</h2>
<p>Your content here with <strong>HTML</strong> formatting.</p>
[/vc_column_text]
```

#### Single Image
```
[vc_single_image
  image="12345"
  img_size="full"
  alignment="center"
  onclick="link_image"
  img_link_target="_blank"
]
```

**Image sizes:**
- `full`, `large`, `medium`, `thumbnail`
- Custom: `300x300`

#### Custom Heading
```
[vc_custom_heading
  text="Your Heading"
  font_container="tag:h2|text_align:center"
  use_theme_fonts="yes"
]
```

#### Button
```
[vc_btn
  title="Click Me"
  color="primary"
  size="lg"
  align="center"
  link="url:https%3A%2F%2Fexample.com|title:Example|target:_blank"
]
```

### Team/People Shortcodes

#### Team Member (Theme-Specific)
```
[team_member
  image_url="12345"
  team_memeber_style="meta_below"
  name="John Doe"
  job_position="CEO"
  image_size="225x225"
  twitter="#"
  linkedin="#"
][/team_member]
```

**Note:** This is often a **custom shortcode** added by themes. Check your theme's shortcode definitions.

### Media Shortcodes

#### Gallery
```
[vc_gallery
  type="image_grid"
  images="123,456,789"
  img_size="medium"
  onclick="link_image"
]
```

**Gallery types:**
- `image_grid`
- `flexslider_slide`
- `flexslider_fade`
- `nivo`

#### Video
```
[vc_video
  link="https://www.youtube.com/watch?v=VIDEO_ID"
  align="center"
]
```

### Advanced Shortcodes

#### Tabs
```
[vc_tabs]
  [vc_tab title="Tab 1" tab_id="tab-1"]
    Content for tab 1
  [/vc_tab]
  [vc_tab title="Tab 2" tab_id="tab-2"]
    Content for tab 2
  [/vc_tab]
[/vc_tabs]
```

#### Accordion
```
[vc_accordion]
  [vc_accordion_tab title="Section 1"]
    Content for section 1
  [/vc_accordion_tab]
  [vc_accordion_tab title="Section 2"]
    Content for section 2
  [/vc_accordion_tab]
[/vc_accordion]
```

#### Progress Bar
```
[vc_progress_bar
  values="%5B%7B%22label%22%3A%22Development%22%2C%22value%22%3A%2290%22%7D%5D"
  units="%"
  bgcolor="bar_blue"
]
```

**Note:** Values are URL-encoded JSON.

---

## Advanced Techniques

### Using Regular Expressions

**Find all image IDs:**
```bash
grep -oP 'image_url="\K[0-9]+' temp/content.txt
```

**Find all team members:**
```bash
grep -oP '\[team_member[^\]]*\]' temp/content.txt
```

**Replace all instances of an image:**
```bash
sed -i 's/image_url="12345"/image_url="33456"/g' temp/content.txt
```

### Batch Operations

**Update multiple images at once:**
```bash
# Map old IDs to new IDs
declare -A IMAGE_MAP=(
  ["12345"]="33456"
  ["67890"]="33457"
  ["11111"]="33458"
)

# Apply all replacements
for old_id in "${!IMAGE_MAP[@]}"; do
  new_id="${IMAGE_MAP[$old_id]}"
  sed -i "s/image_url=\"$old_id\"/image_url=\"$new_id\"/g" temp/content.txt
done
```

### Extracting Specific Sections

**Get only team member shortcodes:**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_content" | \
grep -oP '\[team_member[^\]]*\][^\[]*\[/team_member\]' > temp/team-members.txt
```

---

## WPEngine-Specific Workflows

### File Transfer Limits

**Maximum chunk size:** 50KB (recommended)
**Timeout:** 30 seconds per SSH command
**Temp directory:** `/tmp/` (world-writable)

### Optimized Chunking Script

```bash
#!/bin/bash
# scripts/wpengine_upload.sh

FILE=$1
SITE_PATH=$2
CHUNK_SIZE=50000

# Split file
split -b $CHUNK_SIZE "$FILE" chunk-

# Transfer
for chunk in chunk-*; do
  ssh user@host "cat > /tmp/$(basename $chunk)" < "$chunk" || {
    echo "❌ Failed to transfer $chunk"
    exit 1
  }
done

# Reassemble and import
FILENAME=$(basename "$FILE")
ssh user@host "cd $SITE_PATH && \
cat /tmp/chunk-* > /tmp/$FILENAME && \
wp media import /tmp/$FILENAME --porcelain && \
rm /tmp/chunk-* /tmp/$FILENAME"

# Clean up local
rm chunk-*
```

**Usage:**
```bash
./scripts/wpengine_upload.sh headshot.jpg sites/sitename
```

---

## Complete Examples

### Example 1: Replace Team Member Photo

**Scenario:** Update a placeholder headshot with actual photo

```bash
# Setup
POST_ID=10883
SITE="sites/yoursite"
HOST="user@yoursite.ssh.wpengine.net"
OLD_IMAGE_ID="12345"

# 1. Backup
mkdir -p temp/backups
ssh $HOST "cd $SITE && \
wp post get $POST_ID --field=post_content" > temp/backups/$POST_ID-team.txt

# 2. Upload new photo
split -b 50000 headshot.jpg chunk-
for chunk in chunk-*; do
  ssh $HOST "cat > /tmp/$(basename $chunk)" < "$chunk"
done

NEW_IMAGE_ID=$(ssh $HOST "cd $SITE && \
cat /tmp/chunk-* > /tmp/headshot.jpg && \
wp media import /tmp/headshot.jpg \
--title='Team Member Headshot' \
--alt='John Doe headshot' \
--porcelain && \
rm /tmp/chunk-* /tmp/headshot.jpg")

rm chunk-*

echo "✅ Uploaded new image: $NEW_IMAGE_ID"

# 3. Update shortcode
ssh $HOST "cd $SITE && \
wp post get $POST_ID --field=post_content" > temp/content.txt

sed -i "s/image_url=\"$OLD_IMAGE_ID\"/image_url=\"$NEW_IMAGE_ID\"/g" temp/content.txt

ssh $HOST "cd $SITE && \
wp post update $POST_ID --post_content=\"\$(cat)\"" < temp/content.txt

echo "✅ Post updated"

# 4. Verify
ssh $HOST "cd $SITE && \
wp post get $POST_ID --field=post_content" | \
grep -q "image_url=\"$NEW_IMAGE_ID\"" && \
echo "✅ Verified: Image ID updated" || \
echo "❌ Verification failed"
```

### Example 2: Update Multiple Text Blocks

**Scenario:** Update company address across multiple text blocks

```bash
POST_ID=45
SITE="sites/yoursite"
HOST="user@host"

# Backup
ssh $HOST "cd $SITE && \
wp post get $POST_ID --field=post_content" > temp/backups/$POST_ID-contact.txt

# Download and edit
ssh $HOST "cd $SITE && \
wp post get $POST_ID --field=post_content" > temp/content.txt

# Replace all instances
sed -i 's/123 Old Street/456 New Avenue/g' temp/content.txt
sed -i 's/Old City, OS 12345/New City, NS 67890/g' temp/content.txt

# Update
ssh $HOST "cd $SITE && \
wp post update $POST_ID --post_content=\"\$(cat)\"" < temp/content.txt

echo "✅ Address updated across all text blocks"
```

### Example 3: Change Layout from 3-Column to 2-Column

**Scenario:** Restructure services page layout

```bash
POST_ID=78
SITE="sites/yoursite"
HOST="user@host"

# Backup
ssh $HOST "cd $SITE && \
wp post get $POST_ID --field=post_content" > temp/backups/$POST_ID-services.txt

# Download
ssh $HOST "cd $SITE && \
wp post get $POST_ID --field=post_content" > temp/content.txt

# Change column widths from 1/3 to 1/2
sed -i 's/\[vc_column width="1\/3"\]/[vc_column width="1\/2"]/g' temp/content.txt

# Manually remove third column in editor
# (Complex restructuring best done manually)

# Update
ssh $HOST "cd $SITE && \
wp post update $POST_ID --post_content=\"\$(cat)\"" < temp/content.txt
```

---

## Troubleshooting Guide

### Problem: Media upload fails

**Symptoms:**
- "Failed to import" error
- Timeout during transfer
- Corrupted image on server

**Solutions:**

**1. Verify chunk size:**
```bash
# Check chunk sizes
ls -lh chunk-*
# All should be < 50KB
```

**2. Test server /tmp access:**
```bash
ssh user@host "echo 'test' > /tmp/test.txt && cat /tmp/test.txt && rm /tmp/test.txt"
# Should output: test
```

**3. Verify reassembly:**
```bash
# Check file integrity after reassembly
ssh user@host "cd sites/sitename && \
cat /tmp/chunk-* > /tmp/test.jpg && \
file /tmp/test.jpg"
# Should report: JPEG image data
```

**4. Use smaller chunks:**
```bash
# Try 25KB chunks instead
split -b 25000 your-image.jpg chunk-
```

### Problem: Changes not visible after update

**Symptoms:**
- Post updated successfully via wp-cli
- No changes visible in browser
- Old content still shows

**Solutions:**

**1. Clear all caches:**
```bash
# WordPress object cache
ssh user@host "cd sites/sitename && wp cache flush"

# Clear opcode cache (if available)
ssh user@host "cd sites/sitename && wp cli cache clear"

# WPEngine cache
ssh user@host "cd sites/sitename && wp w3-total-cache flush all"
```

**2. Wait for cache TTL:**
```bash
# Wait 60 seconds, then check again
sleep 60
```

**3. Hard refresh browser:**
- Cmd + Shift + R (Mac)
- Ctrl + F5 (Windows)
- Use incognito mode

**4. Verify post_modified timestamp:**
```bash
ssh user@host "cd sites/sitename && \
wp post get POST_ID --field=post_modified"
# Should show recent time
```

### Problem: Shortcode broken after edit

**Symptoms:**
- Visual Composer shows errors
- Content displays as raw shortcodes
- Layout completely broken

**Solutions:**

**1. Restore from backup immediately:**
```bash
ssh user@host "cd sites/sitename && \
wp post update POST_ID --post_content=\"\$(cat)\"" < temp/backups/POST_ID-backup.txt
```

**2. Check bracket balance:**
```bash
# Opening brackets
grep -o '\[' temp/content.txt | wc -l

# Closing brackets
grep -o '\]' temp/content.txt | wc -l
```

**3. Validate shortcode structure:**
```bash
# Find unclosed shortcodes
grep -n '\[vc_[a-z_]*[^]]*$' temp/content.txt
```

**4. Check for special characters:**
```bash
# Look for problematic characters
grep -n '[<>"]' temp/content.txt
```

### Problem: wp-cli command fails

**Symptoms:**
- "command not found: wp"
- Permission errors
- Database connection errors

**Solutions:**

**1. Verify wp-cli path:**
```bash
ssh user@host "which wp"
# Should output: /usr/local/bin/wp or similar
```

**2. Check site path:**
```bash
ssh user@host "cd sites/sitename && pwd"
# Should show correct directory
```

**3. Test wp-cli connection:**
```bash
ssh user@host "cd sites/sitename && wp cli info"
# Should show wp-cli version and environment
```

**4. Check wp-config.php:**
```bash
ssh user@host "cd sites/sitename && wp config get DB_NAME"
# Should show database name
```

### Problem: SSH connection issues

**Symptoms:**
- Connection timeouts
- Authentication failures
- Command hangs

**Solutions:**

**1. Test basic SSH:**
```bash
ssh user@host "echo 'test'"
# Should output: test
```

**2. Check SSH config:**
```bash
cat ~/.ssh/config
# Look for Host entries matching your site
```

**3. Increase timeout:**
```bash
ssh -o ConnectTimeout=60 user@host "command"
```

**4. Use verbose mode:**
```bash
ssh -v user@host "command"
# Shows detailed connection info
```

---

## File Organization

Recommended temp file structure:

```
temp/
├── backups/
│   ├── 10883-team-20251020.txt
│   ├── 45-contact-20251020.txt
│   └── 78-services-20251020.txt
├── content.txt (current working copy)
├── screenshots/
│   ├── team-before.png
│   ├── team-after.png
│   ├── contact-before.png
│   └── contact-after.png
└── uploads/
    ├── headshot.jpg
    └── logo.png
```

---

## Related Documentation

- [SKILL.md](SKILL.md) - Quick reference and overview
- [references/vc_shortcodes.txt](references/vc_shortcodes.txt) - Complete shortcode list
- [skills/browsing/SKILL.md](skills/browsing/SKILL.md) - Browser automation
- [skills/wp-cli/SKILL.md](skills/wp-cli/SKILL.md) - wp-cli reference

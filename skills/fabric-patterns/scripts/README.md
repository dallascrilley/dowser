# Fabric Pattern Scripts

Ready-to-use scripts for common Fabric workflows.

## Available Scripts

### 1. `fabric_run_pattern.sh`
Run a single Fabric pattern on a file or directory.

**Usage:**
```bash
./fabric_run_pattern.sh <pattern_name> <input_path> [output_file]
```

**Examples:**
```bash
# Extract wisdom from all articles in a directory
./fabric_run_pattern.sh extract_wisdom ./articles

# Summarize a single file
./fabric_run_pattern.sh summarize ./blog_post.md

# Custom output location
./fabric_run_pattern.sh analyze_claims ./data/ ./analysis_results.md
```

### 2. `fabric_pipeline.sh`
Chain multiple patterns in sequence. Default pipeline:
- extract_wisdom → capture_thinkers_work → label_and_rate

**Usage:**
```bash
./fabric_pipeline.sh <input_path> [output_root]
```

**Examples:**
```bash
# Run default pipeline on directory
./fabric_pipeline.sh ./research_papers

# Custom output location
./fabric_pipeline.sh ./meeting_notes ./analysis_output
```

**Customize Pipeline:**
Edit the `patterns` array in the script:
```bash
# Research Analysis
local patterns=(
  "extract_wisdom"
  "capture_thinkers_work"
  "label_and_rate"
)

# Security Analysis
local patterns=(
  "analyze_threat_report"
  "create_sigma_rules"
  "create_stride_threat_model"
)

# Content Creation
local patterns=(
  "extract_ideas"
  "create_story_explanation"
  "improve_writing"
)
```

### 3. `fabric_quick_commands.sh`
Interactive command reference with copy-paste ready commands.

**Usage:**
```bash
# List all available command functions
./fabric_quick_commands.sh

# Or source it and use individual functions
source ./fabric_quick_commands.sh
fabric_extract_wisdom
fabric_summarize
fabric_analyze_claims
```

**Available Functions:**
- `fabric_extract_wisdom` - Extract insights and ideas
- `fabric_extract_ideas` - Pull novel concepts
- `fabric_extract_recommendations` - Get actionable advice
- `fabric_summarize` - Various summary options
- `fabric_youtube_summary` - Summarize YouTube videos
- `fabric_analyze_claims` - Fact checking
- `fabric_analyze_code` - Code review
- `fabric_threat_model` - Security threat modeling
- `fabric_analyze_malware` - Malware analysis
- `fabric_improve_writing` - Writing enhancement
- `fabric_create_email` - Professional emails
- `fabric_tweet` - Social media posts
- `fabric_create_mermaid` - Diagrams
- `fabric_create_mindmap` - Mind maps
- `fabric_git_commit` - Commit messages
- `fabric_create_pr` - Pull requests

## Installation

All scripts are executable. If needed:
```bash
chmod +x *.sh
```

## Common Workflows

### Deep Research Analysis
```bash
# Step 1: Combine and extract wisdom
./fabric_run_pattern.sh extract_wisdom ./research_papers ./wisdom.md

# Step 2: Capture key concepts
./fabric_run_pattern.sh capture_thinkers_work ./wisdom.md ./concepts.md

# Step 3: Categorize and rate
./fabric_run_pattern.sh label_and_rate ./concepts.md ./final.md
```

Or use the pipeline:
```bash
./fabric_pipeline.sh ./research_papers
```

### YouTube Video Analysis
```bash
# Quick reference for commands
source ./fabric_quick_commands.sh
fabric_youtube_summary

# Then copy-paste the command shown
fabric -y 'https://youtube.com/watch?v=VIDEO_ID' --pattern youtube_summary
```

### Code Review Workflow
```bash
# Get review of current changes
git diff | fabric --pattern review_code > code_review.md

# Or use the quick commands
source ./fabric_quick_commands.sh
fabric_analyze_code
```

### Content Creation Pipeline
```bash
# Custom pipeline for blog posts
# Edit fabric_pipeline.sh with:
local patterns=(
  "extract_main_idea"
  "create_story_explanation"
  "improve_writing"
)

# Then run
./fabric_pipeline.sh ./rough_draft.md ./polished_output
```

## Tips

1. **Use streaming for long content:**
   ```bash
   fabric --stream --pattern extract_wisdom
   ```

2. **Save outputs:**
   All scripts automatically save to timestamped files

3. **Chain patterns:**
   Output from one pattern becomes input to the next

4. **Customize pipelines:**
   Edit the `patterns` array in `fabric_pipeline.sh` for your needs

5. **Quick reference:**
   Keep `fabric_quick_commands.sh` sourced in your shell for instant access

## Troubleshooting

**Script not executable:**
```bash
chmod +x script_name.sh
```

**Fabric command not found:**
```bash
fabric --setup
```

**Pattern not found:**
```bash
fabric --updatepatterns
```

**Need help:**
```bash
./script_name.sh --help
```

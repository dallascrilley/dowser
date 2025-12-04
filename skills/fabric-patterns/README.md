# Fabric Patterns Skill

Intelligent pattern selector for Fabric CLI - suggests the most relevant patterns from 242+ specialized AI prompts based on user intent.

## What This Skill Does

This skill helps you:
1. **Find the right Fabric pattern** for any task
2. **Get copy-paste ready commands** with all syntax variations
3. **Chain patterns together** for multi-step workflows
4. **Use ready-made scripts** for common use cases

## When to Use This Skill

- "What fabric pattern should I use for..."
- "Help me analyze/summarize/extract..."
- Processing content (articles, videos, podcasts, code)
- Security analysis, threat modeling, code review
- Any text-based workflow

## Skill Structure

```
fabric-patterns/
├── SKILL.md                    # Main skill file (loaded by Claude)
├── README.md                   # This file
├── scripts/                    # Ready-to-use scripts
│   ├── README.md              # Script documentation
│   ├── fabric_run_pattern.sh  # Single pattern runner
│   ├── fabric_pipeline.sh     # Multi-pattern pipeline
│   └── fabric_quick_commands.sh # Command reference
└── references/                 # Reference documentation
    ├── README.md              # Reference guide
    ├── pattern-database.md    # Complete pattern catalog
    └── fabric-readme.md       # Official Fabric docs
```

## Quick Start

### 1. Ask Claude for Pattern Recommendations

Simply ask Claude:
```
"What fabric pattern should I use to extract insights from a research paper?"
"Help me analyze security threat reports"
"I need to summarize a YouTube video"
```

Claude will:
- Suggest the best pattern(s)
- Explain why they fit
- Provide copy-paste ready commands
- Show multi-step workflows if applicable

### 2. Use Ready-Made Scripts

**Run single pattern:**
```bash
./scripts/fabric_run_pattern.sh extract_wisdom ./articles/
```

**Run multi-pattern pipeline:**
```bash
./scripts/fabric_pipeline.sh ./research_papers/
```

**Get command reference:**
```bash
./scripts/fabric_quick_commands.sh
# Or source it:
source ./scripts/fabric_quick_commands.sh
fabric_extract_wisdom
```

### 3. Browse Pattern Database

See `references/pattern-database.md` for the complete catalog of 242+ patterns organized by category.

## Examples

### Example 1: Research Analysis
```
User: "I have a directory of research papers. Help me extract the key insights."

Claude: "I recommend using the research analysis pipeline:

Primary Pattern: extract_wisdom
Copy-paste command:
  ./scripts/fabric_run_pattern.sh extract_wisdom ./research_papers/

Or use the full pipeline:
  ./scripts/fabric_pipeline.sh ./research_papers/

This will run:
  1. extract_wisdom - Extract insights, ideas, quotes
  2. capture_thinkers_work - Capture key concepts
  3. label_and_rate - Categorize and evaluate
```

### Example 2: Code Review
```
User: "Review my code changes"

Claude: "For code review, use:

git diff | fabric --pattern review_code

Or for explanation first:
  git diff | fabric --pattern explain_code > explanation.md
  git diff | fabric --pattern review_code > review.md
```

### Example 3: YouTube Summary
```
User: "Summarize this YouTube video about AI"

Claude: "Use the youtube_summary pattern:

fabric -y "https://youtube.com/watch?v=VIDEO_ID" --pattern youtube_summary

This will:
- Extract the transcript
- Identify key points
- Create timestamped summary
```

## Pattern Categories

The skill covers 20+ categories:

- **Extraction** - extract_wisdom, extract_ideas, extract_recommendations
- **Summarization** - summarize, create_micro_summary, youtube_summary
- **Analysis** - analyze_claims, analyze_paper, compare_and_contrast
- **Development** - explain_code, review_code, create_git_diff_commit
- **Security** - create_stride_threat_model, analyze_malware
- **Writing** - improve_writing, clean_text, create_formal_email
- **Visualization** - create_mermaid_visualization, create_markmap_visualization
- **And 13+ more...**

See `references/pattern-database.md` for the complete list.

## Common Workflows

### Deep Research Analysis
```bash
# Pipeline approach
./scripts/fabric_pipeline.sh ./articles/

# Manual approach
fabric --pattern extract_wisdom < articles.md > wisdom.md
fabric --pattern capture_thinkers_work < wisdom.md > concepts.md
fabric --pattern label_and_rate < concepts.md > final.md
```

### Security Analysis
```bash
# Custom pipeline in fabric_pipeline.sh
local patterns=(
  "analyze_threat_report"
  "create_sigma_rules"
  "create_stride_threat_model"
)
./scripts/fabric_pipeline.sh ./threat_reports/
```

### Content Creation
```bash
# Extract ideas and create content
fabric --pattern extract_ideas < research.md > ideas.md
fabric --pattern create_story_explanation < ideas.md > story.md
fabric --pattern improve_writing < story.md > polished.md
```

## How the Skill Works

When you ask Claude about Fabric patterns, the skill:

1. **Analyzes your intent**
   - What's your goal? (extract, analyze, summarize, create)
   - What type of content?
   - What output format?

2. **Matches to categories**
   - Maps to 20+ pattern categories
   - Considers primary and alternative patterns
   - Identifies multi-step workflows

3. **Provides structured output**
   - Recommended patterns with explanations
   - Copy-paste ready commands (clipboard, file, URL, YouTube)
   - Multi-pattern workflows
   - Script recommendations

4. **Offers ready-to-use scripts**
   - Single pattern execution
   - Pipeline processing
   - Command reference

## Files Explained

### SKILL.md
Main skill file that Claude loads. Contains:
- Pattern matching logic
- Category definitions
- Usage examples
- Command templates

### scripts/
Ready-to-use bash scripts:
- `fabric_run_pattern.sh` - Run any pattern on files/directories
- `fabric_pipeline.sh` - Chain multiple patterns (customizable)
- `fabric_quick_commands.sh` - Interactive command reference

### references/
Documentation and reference materials:
- `pattern-database.md` - Complete catalog of 242+ patterns
- `fabric-readme.md` - Official Fabric documentation
- `README.md` - Reference guide

## Customization

### Customize Pipeline
Edit `scripts/fabric_pipeline.sh`:
```bash
# Change this array to your preferred patterns
local patterns=(
  "your_pattern_1"
  "your_pattern_2"
  "your_pattern_3"
)
```

### Add Custom Patterns
Create in `~/.config/fabric/patterns/`:
```bash
mkdir -p ~/.config/fabric/patterns/my-pattern
echo "Your pattern content..." > ~/.config/fabric/patterns/my-pattern/system.md
```

Then use:
```bash
fabric --pattern my-pattern
```

## Updating

### Update Patterns
```bash
fabric --updatepatterns
```

### Update Pattern Database
After updating patterns, check for new ones:
```bash
fabric --list
```

Then update `references/pattern-database.md` if needed.

## Troubleshooting

**Skill not activating:**
- Make sure to mention "fabric" or describe a pattern-matching task
- Check that SKILL.md has proper frontmatter

**Pattern not found:**
```bash
fabric --updatepatterns
```

**Script permission denied:**
```bash
chmod +x scripts/*.sh
```

**Command not found:**
Make sure Fabric is installed:
```bash
fabric --setup
```

## Integration with PAI

This skill is part of the PAI (Personal AI Infrastructure) skills system.

**Skill location:** `~/.claude/skills/productivity/fabric-patterns/`

**Activation:** Automatic when user mentions fabric or pattern-matching tasks

**Dependencies:** Fabric CLI must be installed and configured

## Resources

- **Fabric GitHub**: https://github.com/danielmiessler/fabric
- **Pattern Directory**: https://github.com/danielmiessler/fabric/tree/main/data/patterns
- **Official Docs**: See `references/fabric-readme.md`

## Contributing

### Add New Patterns
1. Update via `fabric --updatepatterns`
2. Document in `references/pattern-database.md`
3. Add examples to SKILL.md if commonly used

### Add New Scripts
1. Create script in `scripts/`
2. Make executable: `chmod +x scripts/your_script.sh`
3. Document in `scripts/README.md`

### Improve Skill
1. Edit `SKILL.md` for pattern matching logic
2. Test with various user queries
3. Update examples and templates

## License

This skill is part of the PAI system. Fabric is an open-source project - see the official repository for license details.

---

**Version:** 1.0.0
**Last Updated:** 2025-11-16
**Maintained by:** Dallas Crilley

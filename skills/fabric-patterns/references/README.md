# Fabric Patterns - Reference Materials

This directory contains comprehensive reference documentation for the Fabric patterns skill.

## Files

### pattern-database.md
**Complete catalog of 242+ Fabric patterns**

Organized by category with:
- Pattern descriptions
- Usage examples
- Copy-paste ready commands
- Popular pattern highlights
- Multi-step workflow suggestions

**Categories covered:**
- AI & Patterns
- Analysis
- Extraction
- Summarization
- Writing
- Development
- Security
- Business
- Learning
- Visualization
- Conversion
- Research
- Review
- Critical Thinking
- Strategy
- Creativity
- Gaming
- Wellness
- Personal Development

### fabric-readme.md
**Official Fabric documentation**

Includes:
- What is Fabric
- Installation and setup
- Complete usage guide
- Command-line options
- Pattern structure
- Custom pattern creation
- Helper apps
- Web interface

## Quick Start

### Find a Pattern
```bash
# Search the pattern database
grep -i "summary" pattern-database.md

# Or use Fabric's built-in tool
fabric --pattern suggest_pattern
```

### Common Commands
```bash
# List all patterns
fabric --list

# Update to latest patterns
fabric --updatepatterns

# Get pattern help
fabric --pattern PATTERN_NAME --help
```

### Pattern Selection Guide

**Not sure which pattern to use?**

1. **Ask Fabric:**
   ```bash
   echo "I want to extract key insights from research papers" | fabric --pattern suggest_pattern
   ```

2. **Browse by category** in `pattern-database.md`

3. **Try popular patterns first:**
   - `extract_wisdom` - Universal insight extraction
   - `summarize` - General summarization
   - `analyze_claims` - Fact checking
   - `improve_writing` - Writing enhancement
   - `review_code` - Code review

## Pattern Categories at a Glance

| Category | Count | Top Patterns |
|----------|-------|--------------|
| **Extraction** | 40+ | extract_wisdom, extract_ideas, extract_recommendations |
| **Summarization** | 15+ | summarize, create_micro_summary, youtube_summary |
| **Analysis** | 35+ | analyze_claims, analyze_paper, compare_and_contrast |
| **Development** | 25+ | explain_code, review_code, create_git_diff_commit |
| **Security** | 20+ | create_stride_threat_model, analyze_malware |
| **Writing** | 30+ | improve_writing, clean_text, create_formal_email |
| **Visualization** | 10+ | create_mermaid_visualization, create_markmap_visualization |
| **AI & Patterns** | 11 | suggest_pattern, create_pattern, improve_prompt |

## Multi-Step Workflows

### Deep Research Analysis
```bash
extract_wisdom → capture_thinkers_work → label_and_rate
```

### Security Assessment
```bash
analyze_threat_report → create_sigma_rules → create_stride_threat_model
```

### Content Creation
```bash
extract_ideas → create_story_explanation → improve_writing
```

### Code Review
```bash
explain_code → review_code → create_git_diff_commit
```

## Advanced Usage

### Chaining Patterns
```bash
# Extract and then analyze
fabric --pattern extract_wisdom < article.md | fabric --pattern label_and_rate
```

### Using Context
```bash
# Add background context to pattern
fabric --pattern analyze_claims --context background.md < article.md
```

### Custom Models
```bash
# Use specific model
fabric --model gpt-4 --pattern extract_wisdom
```

### Streaming Output
```bash
# Get results in real-time
fabric --stream --pattern summarize
```

## Creating Custom Patterns

### Pattern Structure
```markdown
# IDENTITY and PURPOSE
You are...

# STEPS
- Step 1
- Step 2

# OUTPUT INSTRUCTIONS
- Format as...
- Include...

# INPUT
INPUT:
```

### Create New Pattern
```bash
# Get help designing a pattern
echo "I need a pattern that extracts action items from meeting notes" | fabric --pattern create_pattern

# Save to custom patterns directory
# ~/.config/fabric/patterns/extract_action_items/system.md
```

## Troubleshooting

### Pattern not found
```bash
fabric --updatepatterns
```

### Fabric not configured
```bash
fabric --setup
```

### Model errors
Check `~/.config/fabric/.env` for API keys

### Want different output
Try these pattern variants:
- `summarize` vs `create_micro_summary` vs `summarize_micro`
- `extract_wisdom` vs `extract_wisdom_short` vs `extract_wisdom_nometa`
- `analyze_paper` vs `analyze_paper_simple`

## Resources

- **Official Fabric**: https://github.com/danielmiessler/fabric
- **Pattern Directory**: https://github.com/danielmiessler/fabric/tree/main/data/patterns
- **Community Patterns**: Check GitHub discussions
- **Documentation**: See `fabric-readme.md`

## Contributing

### Found an Error?
Update the pattern database by:
1. Running `fabric --updatepatterns`
2. Checking the latest patterns with `fabric --list`
3. Updating `pattern-database.md` if needed

### New Patterns?
When Fabric adds new patterns:
1. Update via `fabric --updatepatterns`
2. Document new patterns in `pattern-database.md`
3. Add examples to common workflows

---

*For skill usage instructions, see the main SKILL.md file*

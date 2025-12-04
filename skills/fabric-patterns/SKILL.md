---
name: fabric-patterns
short_description: >-
  Intelligent pattern selector for Fabric CLI suggesting relevant patterns from
  242+ specialized AI prompts based on user intent.
description: >-
  Intelligent pattern selector for Fabric CLI - suggests most relevant patterns
  from 242+ specialized AI prompts based on user intent. Provides copy-paste
  ready commands and chainable scripts. USE WHEN user mentions fabric, needs to
  process/analyze content, extract insights, summarize text, create content, or
  transform data. Covers analysis, security, development, writing,
  visualization, and 20+ categories.
when_to_use: >-
  when user mentions fabric, processing content, analyzing data, creating
  summaries, threat modeling, transforming text, extracting insights, code
  review, or working with any text-based workflow
version: 1.0.0
category: productivity
---

# Fabric Patterns - Intelligent Pattern Selection

## When to Activate This Skill

- User mentions "fabric" or "fabric pattern"
- "What fabric pattern should I use for..."
- "Help me analyze/summarize/extract..."
- Processing content (articles, videos, podcasts, code)
- Creating structured outputs (summaries, reports, analyses)
- Transforming text between formats
- Security analysis, threat modeling, code review
- Any text-based workflow that could benefit from AI processing

## What is Fabric?

Fabric is an open-source framework for augmenting human capabilities with AI. It organizes 242+ specialized AI prompts (called "Patterns") into task-based categories, making it easy to apply the right AI solution for any workflow.

**Common usage**: `fabric --pattern <pattern_name>`

## Core Workflow: Pattern Selection

When user asks for help with Fabric:

### 1. Understand the Intent
Ask yourself:
- What is the user's primary goal? (extract, analyze, summarize, create, transform)
- What type of content? (text, code, video transcript, data)
- What output format? (summary, report, visualization, structured data)
- Is this a single step or multi-step workflow?

### 2. Match to Categories

**EXTRACT** - Pull specific information from content
- `extract_wisdom` - Insights, ideas, quotes, habits from any content
- `extract_article_wisdom` - Wisdom from articles specifically
- `extract_ideas` - Novel concepts and applications
- `extract_recommendations` - Actionable advice and guidance
- `extract_questions` - Q&A extraction
- `extract_references` - Citations and sources

**SUMMARIZE** - Condense content at various levels
- `summarize` - General-purpose summarization
- `create_micro_summary` - Concise one-sentence + key points
- `create_5_sentence_summary` - Progressive detail levels
- `youtube_summary` - YouTube videos with timestamps
- `summarize_paper` - Academic papers with findings

**ANALYSIS** - Evaluate, assess, compare
- `analyze_claims` - Truth evaluation with evidence
- `analyze_paper` - Scientific paper analysis
- `analyze_prose` - Writing quality evaluation
- `compare_and_contrast` - Side-by-side comparison tables
- `find_logical_fallacies` - Argument validity check
- `rate_content` - Multi-dimensional quality scoring

**DEVELOPMENT** - Code and software workflows
- `explain_code` - Code explanation and analysis
- `review_code` - Comprehensive code review
- `create_git_diff_commit` - Smart commit messages
- `summarize_git_changes` - Change summaries
- `create_coding_project` - Project design with architecture
- `write_pull-request` - PR descriptions

**SECURITY** - Cybersecurity and threat analysis
- `create_stride_threat_model` - STRIDE threat modeling
- `analyze_malware` - Malware behavior analysis
- `analyze_threat_report` - Threat intelligence extraction
- `create_sigma_rules` - Detection rule creation
- `write_hackerone_report` - Vulnerability reports

**WRITING** - Content creation and improvement
- `improve_writing` - Enhance clarity and style
- `clean_text` - Fix formatting and structure
- `tweet` - Convert to social media posts
- `create_formal_email` - Professional email composition
- `write_essay` - Essay creation in specific styles

**VISUALIZE** - Create diagrams and visual content
- `create_mermaid_visualization` - Mermaid diagrams
- `create_markmap_visualization` - Mind maps
- `create_conceptmap` - Interactive concept maps
- `create_visualization` - ASCII art with explanations

**AI & PATTERNS** - Meta-patterns for working with AI
- `suggest_pattern` - Get pattern recommendations from Fabric itself
- `create_pattern` - Design new custom patterns
- `improve_prompt` - Enhance AI prompts

### 3. Provide Output

Format your response with:

#### 🎯 Recommended Patterns

**Primary Pattern: `pattern_name`**
- **Why**: [Explanation of why this pattern fits]
- **Command**:
```bash
fabric --pattern pattern_name
```
- **With input file**:
```bash
fabric --pattern pattern_name < input.txt
```
- **From clipboard** (macOS):
```bash
pbpaste | fabric --pattern pattern_name
```
- **From URL**:
```bash
fabric -u https://example.com/article --pattern pattern_name
```
- **From YouTube**:
```bash
fabric -y "https://youtube.com/watch?v=VIDEO_ID" --pattern pattern_name
```

**Alternative Patterns**:
- `alt_pattern_1` - [When to use this instead]
- `alt_pattern_2` - [Another approach]

#### 🔗 Multi-Pattern Workflows

For complex tasks, suggest chaining patterns:

```bash
# Example: Deep content analysis pipeline
fabric --pattern extract_wisdom < article.txt > step1_wisdom.md
fabric --pattern capture_thinkers_work < step1_wisdom.md > step2_concepts.md
fabric --pattern label_and_rate < step2_concepts.md > final_categorized.md
```

#### 📋 Ready-to-Use Scripts

Point to provided scripts in `scripts/` directory:
- `fabric_run_pattern.sh` - Run single pattern on file/directory
- `fabric_pipeline.sh` - Chain multiple patterns together
- Custom scripts for common workflows

### 4. Pattern Categories Reference

**Quick category lookup** (20+ categories):

- **AI**: ai, create_pattern, improve_prompt, suggest_pattern
- **ANALYSIS**: analyze_claims, analyze_paper, compare_and_contrast
- **BUSINESS**: create_prd, check_agreement, create_loe_document
- **CONVERSION**: convert_to_markdown, export_data_as_csv, translate
- **DEVELOPMENT**: explain_code, review_code, create_git_diff_commit
- **EXTRACT**: extract_wisdom, extract_ideas, extract_recommendations
- **SECURITY**: create_stride_threat_model, analyze_malware, analyze_threat_report
- **SUMMARIZE**: summarize, create_micro_summary, youtube_summary
- **WRITING**: improve_writing, clean_text, create_formal_email
- **VISUALIZE**: create_mermaid_visualization, create_markmap_visualization

Full pattern database available in skill frontmatter and reference files.

## Common Usage Patterns

### Basic Usage
```bash
# List all available patterns
fabric --list

# Update patterns to latest version
fabric --updatepatterns

# Stream results in real-time
fabric --stream --pattern pattern_name

# Save output to file
fabric --pattern pattern_name < input.txt > output.md

# Use with specific model
fabric --model gpt-4 --pattern pattern_name
```

### Advanced Usage
```bash
# With context file for additional background
fabric --pattern pattern_name --context background.md < input.txt

# Multiple inputs from directory
cat articles/*.md | fabric --pattern extract_wisdom > all_wisdom.md

# Chain with other tools
curl -s https://api.example.com/data | jq '.content' | fabric --pattern analyze_claims
```

## Custom Patterns

Users can create custom patterns in `~/.config/fabric/patterns/pattern-name/system.md`

Suggest using `create_pattern` pattern to design new ones:
```bash
echo "I need a pattern that does X" | fabric --pattern create_pattern
```

## Scripts Provided

### `fabric_run_pattern.sh`
Run any pattern on a file or directory:
```bash
./scripts/fabric_run_pattern.sh extract_wisdom ./articles/
./scripts/fabric_run_pattern.sh summarize ./transcript.txt output.md
```

### `fabric_pipeline.sh`
Chain patterns in sequence:
```bash
# Default pipeline: extract_wisdom → capture_thinkers_work → label_and_rate
./scripts/fabric_pipeline.sh ./articles/

# Edit script to customize pipeline patterns
```

## Key Commands Quick Reference

```bash
# Pattern selection help
fabric --pattern suggest_pattern

# List patterns
fabric -l

# Update patterns
fabric -u

# Stream output
fabric -s --pattern <name>

# From clipboard
pbpaste | fabric -p <name>

# From URL
fabric -u <url> -p <name>

# From YouTube
fabric -y <url> -p <name>

# Save output
fabric -p <name> -o output.md
```

## Best Practices

1. **Start with `suggest_pattern`** - Let Fabric recommend patterns:
   ```bash
   echo "I want to extract key insights from research papers" | fabric --pattern suggest_pattern
   ```

2. **Use streaming for long content** - Get results faster:
   ```bash
   fabric -s --pattern extract_wisdom
   ```

3. **Chain patterns for deep analysis** - Each pattern refines the previous output

4. **Create custom patterns** - For repeated specialized tasks

5. **Keep patterns updated** - Run `fabric --updatepatterns` regularly

## Examples

### Example 1: Analyze Blog Post
```bash
# Copy blog post to clipboard, then:
pbpaste | fabric --stream --pattern analyze_claims
```

### Example 2: Extract Wisdom from YouTube
```bash
fabric -y "https://youtube.com/watch?v=dQw4w9WgXcQ" --pattern extract_wisdom
```

### Example 3: Code Review
```bash
git diff main | fabric --pattern review_code
```

### Example 4: Create Threat Model
```bash
fabric --pattern create_stride_threat_model < system_design.md
```

### Example 5: Multi-Step Research Analysis
```bash
# Pipeline approach
fabric -u https://research-paper-url.com --pattern summarize_paper > summary.md
fabric --pattern extract_wisdom < summary.md > wisdom.md
fabric --pattern create_markmap_visualization < wisdom.md > mindmap.md
```

## Troubleshooting

**Pattern not found**: Run `fabric --updatepatterns`

**No output**: Check if fabric is configured with `fabric --setup`

**Model errors**: Verify API keys are set in `~/.config/fabric/.env`

**Want different model**: Use `--model` flag or change default with `fabric --changeDefaultModel`

## Reference Files

This skill includes:
- Complete pattern database with descriptions (`references/pattern-database.md`)
- Example scripts (`scripts/`)
- Fabric official documentation (`references/fabric-readme.md`)

## Pattern Database

For the complete categorized list of all 242+ patterns with descriptions, see:
`/Users/dallascrilley/PAI/.claude/skills/productivity/fabric-patterns/references/pattern-database.md`

## Next Steps After Pattern Selection

1. ✅ Run the suggested command
2. 📄 Review the output
3. 🔄 Chain with another pattern if needed
4. 💾 Save results to appropriate location
5. 🎨 Customize pattern or create new one if necessary

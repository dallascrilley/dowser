# Phase 1: Documentation Gathering

## Goal
Collect complete, clean documentation in markdown format.

## Input Methods

### Method 1: Direct Markdown Input

User provides markdown documentation directly.

**When to use:**
- Documentation is already in markdown
- User has local docs
- Small, focused documentation

**Process:**
1. Accept markdown content
2. Verify completeness
3. Ask for missing sections if needed

**Example:**
```
User: "Here's the ripgrep documentation: [markdown content]"
Claude: "Thanks! I have the documentation. Let me analyze it..."
```

### Method 2: URL Extraction (using-crawl4ai-cli)

Extract documentation from URLs using the using-crawl4ai-cli skill.

**When to use:**
- Online documentation
- Multiple pages to combine
- HTML documentation to convert

**Process:**
1. Identify documentation URLs
2. Use using-crawl4ai-cli to extract markdown:
   ```bash
   crwl https://docs.tool.com/guide -o markdown > docs.md
   ```
3. For multi-page docs, extract each page:
   ```bash
   crwl https://docs.tool.com/intro -o markdown > intro.md
   crwl https://docs.tool.com/usage -o markdown > usage.md
   crwl https://docs.tool.com/config -o markdown > config.md
   ```
4. Combine into single document

**Example:**
```
User: "Create a skill for ast-grep from https://ast-grep.github.io"
Claude: "I'll extract the documentation using crawl4ai..."
```

### Method 3: Mixed Approach

Combine crawled content with user-provided context.

**When to use:**
- Official docs + user experience
- Documentation gaps + user knowledge
- Quick start from URLs + deep context from user

**Process:**
1. Extract base documentation
2. Ask user for context:
   - Common pitfalls they've encountered
   - Workflows they use frequently
   - Configuration patterns they recommend
3. Merge extracted docs with user insights

**Example:**
```
User: "Create a skill for ffmpeg. Docs are at https://ffmpeg.org/documentation.html but I can tell you common mistakes"
Claude: "Perfect! I'll extract the official docs and then get your insights..."
```

## Deliverable

Complete documentation in markdown format, organized by section:
- Tool overview
- Installation/setup
- Basic usage
- Advanced features
- Configuration options
- Examples
- Troubleshooting
- API/CLI reference

## Validation Checkpoint

Before proceeding to Phase 2:
- [ ] Documentation is complete and readable
- [ ] All major sections are present
- [ ] Examples are included
- [ ] Configuration options documented
- [ ] Common operations covered

## Agent-Powered Extraction

When using the documentation crawler agent:

**Capabilities:**
- Single and multi-page extraction
- JavaScript-heavy sites with dynamic content
- Quality verification and cleaning
- Multi-page parallel extraction

**Agent handles:**
- Cache bypass for fresh content
- Dynamic content waiting (networkidle, delays)
- Navigation/UI artifact removal
- Content combination and organization

**See:** `.claude/agents/phase-1-documentation-gathering/documentation-crawler.md` for agent details


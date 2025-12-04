---
name: writing-technical-docs
short_description: >-
  Create and improve technical documentation including guides, READMEs, API
  docs, ADRs, and code comments with clear, accessible writing.
description: >-
  Use this skill when creating or improving technical documentation including
  user guides, tutorials, README files, API documentation, architecture docs, or
  when enhancing content clarity and accessibility. This includes writing
  getting started guides, documenting code, creating ADRs (Architecture Decision
  Records), establishing writing standards, organizing documentation structure,
  or restructuring complex technical content for better understanding.
when_to_use: >
  Use when creating or improving technical documentation, writing user guides,
  tutorials, READMEs, API docs, architecture

  documentation, ADRs, code comments, or enhancing content clarity. Applies to
  getting started guides, writing standards,

  information architecture, or restructuring technical content for better
  understanding.
version: 1.0.0
category: collaboration
---

# Technical Documentation Writing Expert

Create clear, accessible, and effective technical documentation that helps users succeed with minimal friction.

## Focus Areas

- **User guides and tutorials** with step-by-step instructions
- **README files** and getting started documentation
- **API documentation** with examples and usage patterns
- **Architecture documentation** including ADRs and design docs
- **Code comments** and inline documentation
- **Content accessibility** and plain language principles
- **Information architecture** and content organization
- **Writing standards** and style guides

## Documentation Approach

### 1. Know Your Audience

- Identify the reader's skill level and context
- Consider what they already know
- Determine what they need to accomplish
- Adapt language and depth accordingly

### 2. Lead with Outcomes

- Start with what the reader will accomplish
- State the goal before diving into steps
- Use active voice and present tense
- Make the value proposition clear upfront

**Example:**
```markdown
# Setting Up Your Development Environment

By the end of this guide, you'll have a working development environment
with Node.js, npm, and all required dependencies installed and tested.

**Time required:** ~15 minutes
**Prerequisites:** Basic terminal knowledge
```

### 3. Use Clear, Concise Language

- Write in active voice
- Choose simple words over complex ones
- Keep sentences short (under 20 words ideal)
- Break complex ideas into smaller chunks
- Use consistent terminology throughout

**Before:**
> "The utilization of this methodology facilitates the implementation of..."

**After:**
> "Use this approach to implement..."

### 4. Provide Real Examples

- Show concrete code examples, not abstract descriptions
- Include realistic scenarios users will encounter
- Demonstrate both common and edge cases
- Use syntax highlighting for code blocks

**Example:**
```javascript
// Good: Specific, realistic example
import { createServer } from 'http';

const server = createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello World\n');
});

server.listen(3000, () => {
  console.log('Server running at http://localhost:3000/');
});
```

### 5. Test Your Instructions

- Follow your own instructions exactly as written
- Test on a clean environment when possible
- Have someone else try the steps
- Update based on where people get stuck
- Verify all commands and code samples work

### 6. Structure Content Logically

- Use clear, descriptive headings
- Follow a logical progression (basics → advanced)
- Use numbered lists for sequential steps
- Use bullet points for unordered information
- Include a table of contents for longer docs

## Documentation Types and Templates

### README Files

**Essential sections:**
```markdown
# Project Name

Brief description (one sentence).

## Features

- Key feature 1
- Key feature 2
- Key feature 3

## Quick Start

\`\`\`bash
# Installation
npm install project-name

# Usage
npm start
\`\`\`

## Documentation

Link to full docs.

## License

MIT
```

**CLI tools for README badges:**
```bash
# shields.io for status badges
# Example: ![Build](https://img.shields.io/github/workflow/status/user/repo/CI)
```

### User Guides

**Structure:**
1. **Overview** - What this guide covers
2. **Prerequisites** - What you need before starting
3. **Step-by-Step Instructions** - Numbered, actionable steps
4. **Verification** - How to confirm success
5. **Troubleshooting** - Common issues and solutions
6. **Next Steps** - Where to go from here

### API Documentation

**For each endpoint/function:**
```markdown
## `functionName(param1, param2)`

**Description:** What this function does.

**Parameters:**
- `param1` (string, required) - Description
- `param2` (number, optional) - Description, default: 0

**Returns:** (Promise<object>) Description of return value

**Example:**
\`\`\`javascript
const result = await functionName('value', 42);
console.log(result);
// Output: { status: 'success', data: [...] }
\`\`\`

**Errors:**
- `InvalidParamError` - When param1 is invalid
- `NotFoundError` - When resource doesn't exist
```

### Architecture Decision Records (ADRs)

**Template:**
```markdown
# ADR-001: [Decision Title]

**Status:** Proposed | Accepted | Deprecated | Superseded

**Date:** YYYY-MM-DD

**Deciders:** [Names or roles]

## Context

What is the issue we're trying to solve? What are the constraints?

## Decision

What did we decide to do?

## Consequences

What becomes easier or harder because of this decision?

### Positive
- Benefit 1
- Benefit 2

### Negative
- Trade-off 1
- Trade-off 2

### Neutral
- Impact 1

## Alternatives Considered

What other options did we evaluate?

1. **Option 1** - Why we didn't choose this
2. **Option 2** - Why we didn't choose this
```

**CLI for ADR management:**
```bash
# Create ADR directory
mkdir -p docs/adr

# Number ADRs sequentially
# adr-001-use-react.md, adr-002-choose-database.md, etc.
```

### Tutorials

**Effective tutorial structure:**

1. **Introduction**
   - What you'll build
   - What you'll learn
   - Time required
   - Prerequisites

2. **Setup**
   - Environment preparation
   - Dependencies installation
   - Verification steps

3. **Implementation** (broken into logical sections)
   - Section 1: Basic foundation
   - Section 2: Add feature X
   - Section 3: Add feature Y
   - Each section: explain → implement → test

4. **Testing**
   - How to test what was built
   - Expected outcomes

5. **Next Steps**
   - Ideas for extension
   - Related tutorials
   - Further reading

## CLI Tools for Documentation

### File Operations
```bash
# Create documentation structure
mkdir -p docs/{guides,api,tutorials,adr}

# Find documentation files
fd . docs/ -e md

# Search documentation content
rg "pattern" docs/

# Count documentation
wc -l docs/**/*.md
```

### Validation and Quality
```bash
# Check spelling (if aspell installed)
aspell check docs/guide.md

# Check links (using markdown-link-check if installed globally)
npx markdown-link-check docs/README.md

# Lint markdown (using markdownlint-cli if installed)
npx markdownlint docs/**/*.md
```

### Git Operations for Docs
```bash
# Find recently updated docs
git log --since="1 week ago" --name-only --pretty=format: -- "*.md" | sort -u

# See doc changes
git diff main -- docs/

# Track doc contributors
git log --follow docs/guide.md
```

### Node.js Scripts for Documentation

Create utility scripts in `scripts/` directory:

```javascript
#!/usr/bin/env node
// scripts/generate-toc.js - Generate table of contents
import { readFile, writeFile } from 'fs/promises';

const markdown = await readFile('docs/guide.md', 'utf-8');
const headings = markdown
  .split('\n')
  .filter(line => line.startsWith('#'))
  .map(heading => {
    const level = heading.match(/^#+/)[0].length;
    const text = heading.replace(/^#+\s+/, '');
    const slug = text.toLowerCase().replace(/\s+/g, '-');
    const indent = '  '.repeat(level - 1);
    return `${indent}- [${text}](#${slug})`;
  });

console.log('## Table of Contents\n\n' + headings.join('\n'));
```

## Content Accessibility Principles

### Plain Language

- Use everyday words
- Keep sentences short and simple
- Use active voice
- Avoid jargon (or explain it when necessary)
- Define acronyms on first use

**Example:**
```markdown
<!-- Before -->
The instantiation of the aforementioned module necessitates...

<!-- After -->
To create this module, you need to...
```

### Inclusive Language

- Use "they/them" for generic pronouns
- Avoid assumptions about reader knowledge
- Provide context for cultural references
- Use descriptive link text (not "click here")

### Scannable Structure

- Use descriptive headings
- Include code examples
- Add visual breaks (lists, code blocks)
- Highlight important information
- Use tables for comparisons

## Writing Quality Checklist

Before publishing documentation, verify:

- [ ] **Audience** - Content matches reader's skill level
- [ ] **Goal** - Purpose is clear in first paragraph
- [ ] **Structure** - Logical flow with clear headings
- [ ] **Language** - Active voice, simple words, short sentences
- [ ] **Examples** - Code samples are tested and working
- [ ] **Accuracy** - Commands and code are current and correct
- [ ] **Completeness** - All necessary steps are included
- [ ] **Tested** - Instructions work when followed exactly
- [ ] **Links** - All URLs are valid and relevant
- [ ] **Formatting** - Consistent style and proper markdown
- [ ] **Accessibility** - Plain language, defined terms, scannable
- [ ] **Navigation** - Table of contents for long docs
- [ ] **Troubleshooting** - Common issues addressed
- [ ] **Next steps** - Clear path forward provided

## Common Documentation Pitfalls

### Problem: Assumed Knowledge

**Issue:** Documentation assumes readers know things they don't.

**Solution:**
- Define terms on first use
- Link to prerequisite knowledge
- Include "Prerequisites" section
- Test with someone unfamiliar with the topic

### Problem: Missing Context

**Issue:** Instructions work in isolation but not in real scenarios.

**Solution:**
- Show complete, working examples
- Include surrounding context
- Demonstrate integration with existing code
- Test in realistic environment

### Problem: Stale Content

**Issue:** Documentation describes old versions or deprecated features.

**Solution:**
```bash
# Tag docs with version
# docs/v2/api-guide.md

# Include last updated date
# Last updated: 2025-10-27

# Review regularly
git log --since="6 months ago" -- docs/
```

### Problem: Unclear Error Messages

**Issue:** Users encounter errors not documented.

**Solution:**
- Create troubleshooting section
- Document common errors with solutions
- Include error messages verbatim for searchability
- Link to error resolution in main docs

**Example:**
```markdown
## Troubleshooting

### Error: "ENOENT: no such file or directory"

**Cause:** Configuration file is missing.

**Solution:**
\`\`\`bash
# Create the config file
cp config.example.json config.json
\`\`\`
```

### Problem: Steps That Can't Be Followed

**Issue:** Instructions skip steps or have wrong commands.

**Solution:**
- Test instructions in clean environment
- Include every command needed
- Verify copy-paste works
- Have others test before publishing

## Documentation Organization

### Directory Structure

```
docs/
├── README.md              # Overview and navigation
├── getting-started.md     # Quick start guide
├── guides/                # How-to guides
│   ├── installation.md
│   ├── configuration.md
│   └── deployment.md
├── api/                   # API reference
│   ├── overview.md
│   └── endpoints.md
├── tutorials/             # Learning-oriented tutorials
│   ├── tutorial-1.md
│   └── tutorial-2.md
├── reference/             # Technical reference
│   └── configuration-options.md
├── adr/                   # Architecture decisions
│   ├── adr-001-choice.md
│   └── adr-002-decision.md
└── troubleshooting.md     # Common issues
```

### Documentation Types Framework

Use the [Diátaxis framework](https://diataxis.fr/):

1. **Tutorials** - Learning-oriented, takes the reader by the hand
2. **How-to guides** - Problem-oriented, shows how to solve specific problems
3. **Reference** - Information-oriented, technical descriptions
4. **Explanation** - Understanding-oriented, background and context

## Style Guide Basics

### Formatting Conventions

```markdown
# Headings
- H1: Document title (one per document)
- H2: Major sections
- H3: Subsections
- Limit to H3 depth for readability

# Code
- Use `inline code` for commands, filenames, variables
- Use code blocks with language for multi-line code
- Always specify language: ```javascript, ```bash, ```json

# Lists
- Use bullets for unordered lists
- Use numbers for sequential steps
- Indent nested lists with 2 spaces

# Emphasis
- Use **bold** for important terms or warnings
- Use *italic* for emphasis
- Use > blockquotes for notes or warnings
```

### Tone and Voice

- **Professional but approachable** - Avoid overly formal language
- **Confident but humble** - Acknowledge complexity
- **Direct and clear** - Get to the point quickly
- **Helpful and encouraging** - Support the reader's success

### Terminology

- **Be consistent** - Use the same terms throughout
- **Define once** - Explain acronyms and jargon on first use
- **Use industry standard terms** - Unless creating new concepts
- **Maintain a glossary** - For complex domains

## Output Deliverables

When creating documentation, provide:

1. **Complete, tested documentation** ready to publish
2. **Navigation aids** - TOC, links between related docs
3. **Code examples** - Verified working samples
4. **Troubleshooting section** - Common issues and solutions
5. **Next steps** - Guide readers to related content
6. **Metadata** - Last updated date, version, authors

## Validation and Testing

### Self-Review Checklist

- [ ] Read aloud - Does it sound natural?
- [ ] Follow instructions - Do they work exactly as written?
- [ ] Check links - Are all URLs valid?
- [ ] Test code - Do all examples run successfully?
- [ ] Review structure - Is the flow logical?
- [ ] Verify formatting - Is markdown correct?

### CLI Validation Commands

```bash
# Check all markdown files
fd . docs/ -e md -x cat

# Find broken links (if using markdown-link-check)
npx markdown-link-check docs/**/*.md

# Check for common issues
rg "TODO|FIXME|XXX" docs/

# Word count for documentation
wc -w docs/**/*.md
```

## Success Metrics

Good documentation achieves:

- **Users succeed on first try** - Instructions are complete and clear
- **Reduced support burden** - Common questions are answered
- **Quick navigation** - Users find what they need easily
- **Self-service** - Users can solve problems independently
- **Positive feedback** - Users appreciate the clarity

Focus on user success. Every piece of documentation should move readers closer to their goals with minimal friction.

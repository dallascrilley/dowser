# Phase 2: Documentation Analysis

## Goal
Systematically extract structure, patterns, workflows, and gotchas from documentation.

## Analysis Framework

### 1. Tool Overview Analysis

**Extract:**
- **Primary purpose**: What problem does this tool solve?
- **Key capabilities**: What are the main features?
- **Use cases**: When would someone use this tool?
- **Target audience**: Who is this tool for?

**Questions to answer:**
- What's the one-sentence description?
- What makes this tool unique?
- What are the top 3 capabilities?

### 2. Command/API Pattern Analysis

**Extract:**
- **Command structure**: How are commands formed?
- **Flag patterns**: Common flag combinations
- **Parameter types**: What kinds of inputs?
- **Output formats**: What does it produce?

**For CLIs, answer:**
- What's the basic command syntax?
- What are required vs optional flags?
- What flag combinations are common?
- What's the default behavior?

**For APIs, answer:**
- What's the authentication method?
- What are the main endpoints?
- What's the request/response format?
- What are required vs optional parameters?

### 3. Workflow Analysis

**Extract:**
- **Standard workflows**: Multi-step processes from docs
- **Task sequences**: Common operation orders
- **Dependencies**: What needs to happen first?

**Look for:**
- "Getting started" sections
- "Quick start" guides
- Tutorial workflows
- Multi-step examples

**Document each workflow:**
1. Name and purpose
2. Prerequisites
3. Step-by-step process
4. Expected output
5. Common variations

### 4. Pitfalls & Gotchas Analysis

**Critical section! This drives guardrails and validation.**

**Extract:**
- **Explicit warnings** from docs ("Warning:", "Note:", "Important:")
- **Common mistakes** sections
- **Prerequisites** often forgotten
- **Error-prone areas** mentioned
- **Version-specific issues**
- **Platform differences**

**LLM Analysis - Anticipate additional pitfalls:**
- What could go wrong with this command?
- What prerequisites might be missed?
- What's confusing about this API?
- What parameter combinations are invalid?
- What's the recovery process for errors?

**Document each pitfall:**
1. Description (what goes wrong)
2. Cause (why it happens)
3. Detection (how to spot it)
4. Prevention (how to avoid it)
5. Solution (how to fix it)

### 5. Best Practices Analysis

**Extract:**
- **Recommended approaches** from docs
- **Performance tips**
- **Security considerations**
- **Maintainability advice**

**Look for:**
- "Best practices" sections
- "Recommendations"
- "Performance" tips
- "Security" notes
- Optimization suggestions

## Analysis Deliverable Structure

Create a structured analysis document:

```markdown
# [Tool Name] Documentation Analysis

## 1. Tool Overview
[Summary from analysis]

## 2. Command/API Patterns
### Basic Syntax
[Command structure]

### Common Flags/Options
[Frequently used flags]

### Flag Combinations
[Common patterns]

## 3. Workflows
### Workflow 1: [Name]
- Prerequisites: [list]
- Steps: [numbered list]
- Expected output: [description]

## 4. Pitfalls & Gotchas
### Pitfall 1: [Name]
- Description: [what goes wrong]
- Cause: [why]
- Detection: [how to spot]
- Prevention: [how to avoid]
- Solution: [how to fix]

## 5. Best Practices
### Category 1: [Name]
- Practice 1
- Practice 2

## 6. Configuration Patterns
[Common config approaches]

## 7. Key Examples
[Critical examples from docs]
```

## Validation Checkpoint

Before proceeding to Phase 3:
- [ ] Tool overview is clear and concise
- [ ] Command/API patterns identified
- [ ] At least 3 workflows documented
- [ ] Pitfalls extracted and analyzed
- [ ] Best practices captured
- [ ] Configuration patterns noted
- [ ] Key examples collected

## Agent-Powered Analysis

**Two agents run in parallel:**

1. **Comprehensive Documentation Analyzer**
   - Complete tool analysis in single pass
   - Extracts: Tool overview, command/API patterns, workflows, configuration, best practices, key examples
   - Model: Sonnet
   - Tools: read, grep

2. **Comprehensive Pitfall Hunter**
   - Unified risk assessment from docs + web search
   - Identifies: Warnings, common mistakes, error-prone operations, prerequisites, community issues, recovery procedures
   - Model: Sonnet
   - Tools: read, grep, websearch
   - Output: Risk matrix with severity × frequency prioritization

**Speedup:** ~3x faster than sequential (3 min vs 8 min)


# Phase 5: SKILL.md Creation & Phase 6: Integration & Testing

## Phase 5: SKILL.md Creation

### Goal
Write comprehensive SKILL.md file that serves as quick reference.

### SKILL.md Structure

Use the template: `templates/tool-skill-SKILL.md.template`

#### Section 1: YAML Frontmatter

```yaml
---
name: tool-name
description: [Clear description]. Use when [use cases]. Keywords - [keywords].
---
```

**Description guidelines:**
- First sentence: What the tool does
- Second sentence: Key capabilities or methods
- Third sentence: USE WHEN triggers with examples
- Fourth sentence: Keywords for matching

#### Section 2: Title and Overview

One-paragraph overview of what the tool does and why it's useful.

#### Section 3: Prerequisites (if needed)

**Option 1: Automated Setup (Recommended)**
- Run setup script to verify installation

**Option 2: Manual Setup**
- Step-by-step manual setup instructions

#### Section 4: Quick Start

Basic usage examples:
- Basic command
- Common operation 1
- Common operation 2

#### Section 5: Core Tasks

For each task:
- Description
- Command with flags
- Options explanation
- Save to file example

#### Section 6: Command Reference

Common flags quick reference.  
**See also:** `references/cli-reference.md` for complete documentation.

#### Section 7: Configuration Files

Show basic configuration example.  
**See also:** `references/config-reference.md` for all options.

#### Section 8: Proven Patterns

**⚠️ MANDATORY:** For ALL patterns below, follow the workflow requirements.

Each pattern includes:
- Description
- Step-by-step commands
- Expected output

#### Section 9: Troubleshooting

Quick fixes table:
| Issue | Solution |

**For detailed solutions:** `references/troubleshooting.md`

#### Section 10: Helper Scripts

List all scripts with brief descriptions and usage examples.

#### Section 11: Workflow Requirements

**⚠️ MANDATORY: Always follow this workflow for [context]:**

1. Step 1 - What to do
2. Step 2 - What to do
3. Step 3 - What to do

**Why this prevents failures:**
- Step 1 [prevents mistake A]
- Step 2 [prevents mistake B]

#### Section 12: Common Workflows

Numbered workflows with step-by-step commands.

#### Section 13: Tips

Categorized tips with cross-references to detailed docs.

### Validation Checkpoint

After SKILL.md creation:
- [ ] YAML frontmatter complete with good description
- [ ] All sections present
- [ ] Examples in every section
- [ ] All file references valid
- [ ] Guardrails marked as ⚠️ MANDATORY
- [ ] Helper scripts documented
- [ ] Workflows explained
- [ ] Tips practical and specific

---

## Phase 6: Integration & Testing

### Goal
Integrate skill into PAI and validate it works correctly.

### Integration Steps

#### Step 1: Add to Global Context

Update `~/.claude/global/CLAUDE.md` in the `<available_skills>` section:

```xml
<skill>
<name>tool-name</name>
<description>Your skill description from SKILL.md frontmatter</description>
<location>user</location>
</skill>
```

**Important:** Use the EXACT description from SKILL.md frontmatter for consistency.

#### Step 2: Verify File Structure

```bash
tree ~/.claude/skills/[tool-name]
```

Expected structure:
```
tool-name/
├── SKILL.md
├── references/
│   ├── cli-reference.md
│   ├── config-reference.md
│   ├── patterns.md
│   └── troubleshooting.md
├── scripts/
│   ├── setup.sh
│   ├── [other scripts]
│   └── README.md
└── templates/
    ├── basic_config.yml
    └── [other templates]
```

### Testing Workflow

#### Test 1: Skill Activation

**Test natural language triggers:**
1. Start new Claude session
2. Try trigger phrases from description
3. Verify skill loads correctly

#### Test 2: Helper Scripts

**For each helper script:**
1. Navigate to scripts directory
2. Run script with `--help` or `-h`
3. Try with valid inputs
4. Try with invalid inputs (verify error handling)
5. Check exit codes

#### Test 3: Config Templates

**For each template:**
1. Use with actual tool
2. Verify it works
3. Check all options are valid
4. Confirm comments are accurate

#### Test 4: File References

**Check all links work:**
- Check references exist
- Check scripts exist
- Check templates exist

#### Test 5: Workflow Validation

**Run through documented workflows:**
1. Follow "First-Time Setup" workflow
2. Try each "Proven Pattern"
3. Execute "Common Workflows"
4. Verify expected outputs

### Iteration Process

Based on testing, iterate:
1. Fix broken references
2. Improve unclear sections
3. Add missing components
4. Enhance examples

### Final Validation

Before declaring skill complete:
- [ ] Skill activates with natural language
- [ ] All helper scripts work
- [ ] All config templates valid
- [ ] All file references resolve
- [ ] All workflows execute successfully
- [ ] Examples are accurate
- [ ] Documentation is clear
- [ ] No broken links
- [ ] Guardrails are effective
- [ ] User can follow docs without confusion


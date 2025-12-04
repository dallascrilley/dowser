# Phase 3: Skill Design Brainstorming

## Goal
Design all skill components that will make the tool easy and safe to use.

## Component Categories

### 1. Helper Scripts Design

**Purpose:** Automate error-prone or repetitive tasks.

**Brainstorming process:**
1. Review pitfalls - What manual steps cause errors?
2. Review workflows - What multi-step processes repeat?
3. Review prerequisites - What setup is required?

**Common helper scripts:**

**Setup/Installation Scripts:**
- Purpose: First-time tool setup
- Checks: Verify installation, dependencies, config
- Example: `setup.sh`

**Validation Scripts:**
- Purpose: Verify configurations or outputs
- Checks: Schema validation, required fields, format
- Example: `validate_config.py`

**Generator Scripts:**
- Purpose: Create configs/templates interactively
- Features: Prompts, validation, examples
- Example: `generate_config.py`

**Inspection/Debug Scripts:**
- Purpose: Troubleshoot issues
- Features: Verbose output, diagnostic checks
- Example: `inspect_state.sh`

**For each helper script, define:**
- Name, Purpose, Inputs, Outputs
- What mistakes it prevents
- Template (python or bash)
- Logic outline

### 2. Config Templates Design

**Purpose:** Provide ready-to-use configuration presets.

**Common template types:**

**Basic/Minimal:**
- Simplest working configuration
- Defaults for most use cases
- Heavily commented

**Advanced/Full-Featured:**
- All major options shown
- Production-ready settings
- Performance optimized

**Scenario-Specific:**
- Tailored to specific use cases
- Example: "dynamic content", "API extraction", "batch processing"

### 3. Guardrails Design

**Purpose:** Prevent common mistakes through enforced workflows.

**Guardrail types:**

**Mandatory Workflows:**
- Mark as ⚠️ MANDATORY in SKILL.md
- Multi-step processes that must be followed in order
- Include "why this prevents failures"

**Prerequisite Checks:**
- Built into helper scripts
- Verify requirements before proceeding
- Clear error messages if missing

**Validation Gates:**
- Run validation before next step
- Prevent bad input propagation
- Stop early on errors

### 4. Checklists Design

**Checklist types:**

**First-Time Setup Checklist:**
- Installation verification
- Dependency installation
- Initial configuration
- Test run

**Pre-Execution Checklist:**
- Prerequisites met
- Configuration valid
- Environment ready
- Dry-run successful

**Troubleshooting Checklist:**
- Common issues to check
- Diagnostic steps
- Solution patterns

### 5. Reference Structure Design

**Decide what goes where:**

**SKILL.md (quick reference):**
- Tool overview
- Quick start (minimal example)
- Core tasks (most common operations)
- Proven patterns (working examples)
- Troubleshooting table (quick fixes)
- Helper scripts list
- Workflow requirements (mandatory steps)
- Common workflows
- Tips

**references/ directory (detailed docs):**
- `cli-reference.md` / `api-reference.md` - Complete flag/option documentation
- `config-reference.md` - All configuration options
- `patterns.md` - Detailed multi-step workflows
- `troubleshooting.md` - Common issues with full context

## Brainstorming Deliverable Structure

Create a skill design document with:
- Directory structure
- Helper scripts (purpose, inputs, outputs, logic)
- Config templates (scenario, key settings, structure)
- Guardrails (type, purpose, implementation)
- Checklists (setup, pre-execution, troubleshooting)
- Reference structure (SKILL.md sections, references/ files)

## Validation Checkpoint

Before proceeding to Phase 4:
- [ ] At least 3 helper scripts designed
- [ ] At least 2 config templates designed
- [ ] At least 2 guardrails defined
- [ ] Checklists created
- [ ] Reference structure planned
- [ ] All designs prevent identified pitfalls

## Agent-Powered Design

**Skill Component Architect Agent:**
- Reviews Phase 2 analysis outputs
- Identifies automation opportunities from workflows
- Designs preventive guardrails from pitfalls
- Plans helper script specifications
- Creates configuration template designs
- Structures reference documentation

**Model:** Sonnet  
**Tools:** read, write, grep  
**Output:** Complete component design document


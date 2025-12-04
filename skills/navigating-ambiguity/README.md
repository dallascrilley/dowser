# Navigating Ambiguity

**Version:** 1.0.0
**License:** MIT
**Converted from:** ambiguity-guardian sub-agent

## Overview

This skill helps Claude preserve productive contradictions and navigate uncertainty as valuable features of knowledge, not bugs to be fixed. It's designed for situations where premature resolution would destroy insights and where mapping what we don't know is as important as what we know.

## When to Use This Skill

Use this skill when:
- **Analyzing competing theories** that fundamentally disagree (e.g., different models of consciousness, competing architectural approaches)
- **Researching emerging technologies** with significant unknowns (e.g., quantum computing, AI capabilities)
- **Encountering paradoxes** that reveal deeper truths about systems
- **Working with complex domains** where multiple valid interpretations coexist
- **Mapping unknowns** is as critical as documenting knowns
- **Premature certainty** would close off valuable insights
- **Minority viewpoints** productively challenge dominant narratives

## What This Skill Provides

### Output Formats

The skill creates four types of structured outputs:

1. **Tension Maps** - Document productive disagreements between viewpoints
2. **Uncertainty Cartography** - Map the boundaries of knowledge and confidence gradients
3. **Paradox Preservation** - Maintain paradoxes as features rather than resolving them
4. **Ambiguity Indices** - Provide navigable structures for operating under uncertainty

See `output-formats.md` for detailed templates.

### Core Capabilities

- Maintain productive disagreements without forcing artificial consensus
- Map what we know, don't know, and don't know we don't know
- Recognize where both/and thinking supersedes either/or logic
- Track epistemology - how we know and why we believe
- Identify systematic blind spots in understanding
- Preserve minority viewpoints that generate valuable insights

## Key Principles

1. **Resist premature closure** - Don't force resolution where ambiguity is productive
2. **Make uncertainty visible** - Marking what we don't know is as valuable as what we do
3. **Preserve minority views** - Alternative perspectives matter even with consensus
4. **Context over correctness** - Emphasize when/where/why rather than which is "right"
5. **Navigate, don't resolve** - Create structures for working with ambiguity

## Examples

### Example 1: Competing Software Architecture Patterns

When evaluating microservices vs monolith architectures:
- Don't pick a "winner"
- Create Tension Map showing when each excels
- Map confidence gradients for different contexts
- Preserve the productive tension
- Guide context-dependent decisions

### Example 2: AI Capabilities Research

When researching what LLMs can/cannot do:
- Map known capabilities vs unknowns
- Create confidence gradients across domains
- Distinguish hype from validated results
- Identify fundamental vs temporary limitations
- Make uncertainty navigable for planning

### Example 3: Performance Optimization Paradoxes

When data shows contradictory optimization results:
- Don't assume measurement error first
- Explore the paradox as revealing system properties
- Look for hidden state or context dependencies
- Use contradiction to understand dynamics
- Create framework for both/and thinking

## Anti-Patterns to Avoid

- **False certainty** - Obscuring genuine complexity with confident claims
- **Artificial consensus** - Papering over real disagreements
- **Binary thinking** - Missing spectrum positions between extremes
- **Premature optimization** - Racing to a single "best" answer
- **Category conflation** - Mixing "don't know yet" with "can never know"
- **Equal uncertainty** - Treating all unknowns as equally important

## File Structure

```
navigating-ambiguity/
├── SKILL.md              # Core skill instructions
├── output-formats.md     # Detailed templates for all output types
└── README.md            # This file
```

## Installation

### Personal (Global)
```bash
# From the claude-skills repository
./scripts/install-skill.sh navigating-ambiguity

# Or manually
ln -s "$(pwd)/skills/navigating-ambiguity" ~/.claude/skills/
```

### Project-Specific
```bash
# Copy to project
cp -r skills/navigating-ambiguity /path/to/project/.claude/skills/
```

## Auto-Trigger Keywords

This skill should automatically trigger when users mention:
- Competing theories, contradictions, paradoxes
- Mapping unknowns, uncertainty, confidence levels
- Multiple valid interpretations, ambiguity
- Premature certainty, forced resolution
- Productive tensions, disagreements
- Complex systems with coexisting truths

## Success Metrics

You know this skill is working when:
- Stakeholders navigate uncertainty without paralysis
- Productive tensions generate new insights rather than conflict
- Maps of unknowns guide research as effectively as maps of knowns
- Paradoxes become tools for thought rather than obstacles
- Ambiguity enriches understanding rather than blocking it

## Conversion Notes

This skill was converted from the `ambiguity-guardian` sub-agent with the following changes:

**Name:** `ambiguity-guardian` → `navigating-ambiguity` (gerund form)

**Description:** Enhanced with specific trigger keywords while preserving core use cases

**Structure:**
- Removed `tools` and `model` fields (skills inherit Claude Code capabilities)
- Preserved all core expertise and domain knowledge
- Added progressive disclosure with `output-formats.md`
- Enhanced examples with concrete scenarios
- Added CLI/research tools section
- Maintained all operating principles and anti-patterns

**Improvements:**
- More discoverable via enhanced description
- Better organized with supporting files
- Examples made more concrete and actionable
- Added installation instructions
- Clearer success criteria

## Related Skills

Works well with:
- **researching-technical-implementations** - For gathering competing viewpoints
- **managing-context** - For tracking complex, ambiguous information
- Any analytical or research-focused skills

## License

MIT License - See LICENSE file in repository root

## Contributing

Found an improvement? Submit a PR to the [claude-skills repository](https://github.com/jezweb/claude-skills).

## Version History

- **1.0.0** (2025-10-27) - Initial conversion from ambiguity-guardian sub-agent

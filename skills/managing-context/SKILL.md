---
name: managing-context
description: >-
  Context management for multi-agent workflows and long-running projects.
  Handles context capture, distribution, memory management, and session
  coordination.
when_to_use: >-
  Use when coordinating multiple agents, preserving state across sessions,
  creating project checkpoints, compressing context, multi-agent workflows,
  long-running projects, session coordination, context preservation, agent
  handoffs, or state management across sessions.
version: 1.0.0
license: MIT
category: productivity
---

# Managing Context for Multi-Agent Workflows

Maintain coherent state across multiple agent interactions and sessions for complex, long-running projects.

## When to Use This Skill

- Coordinating multiple specialized agents on a single project
- Preserving important decisions and rationale across sessions
- Managing context for projects spanning multiple days/weeks
- Creating checkpoints at major project milestones
- Distributing minimal, relevant context to different agents
- Compressing and archiving project history

## Core Responsibilities

### 1. Context Capture

Extract and preserve critical information from ongoing work:

**Capture:**
- Key decisions and their rationale
- Reusable patterns and solutions
- Integration points between components
- Unresolved issues and TODOs
- Performance benchmarks and metrics

**Implementation:**
```bash
# Review recent conversation and agent outputs
# Use TodoWrite to track open items
# Use Write to create context summaries
```

### 2. Context Distribution

Prepare minimal, relevant context for each agent or session:

**Create Agent-Specific Briefings:**
- Current task and immediate goals
- Recent decisions affecting current work
- Active blockers or dependencies
- Relevant code locations and patterns

**Maintain Context Index:**
- Quick reference to key decisions
- Map of integration points
- Index of commonly accessed information

**Prune Outdated Information:**
- Remove superseded decisions
- Archive resolved issues
- Consolidate redundant context

### 3. Memory Management

Store and organize project knowledge:

**Store Critical Decisions:**
- Architectural choices
- Technology selections
- Design patterns adopted
- Performance optimizations

**Maintain Rolling Summary:**
- Recent changes (last 7 days)
- Current work streams
- Upcoming milestones

**Create Context Checkpoints:**
- At major milestones
- Before architecture changes
- When switching focus areas

## Workflow Integration

When activated:

1. **Review Current State**
   - Read recent conversation history
   - Examine agent outputs and decisions
   - Check TodoWrite for active tasks

2. **Extract Important Context**
   - Identify decisions that will affect future work
   - Document integration points
   - Note reusable patterns

3. **Create Summary**
   - Write concise summary for next agent/session
   - Include only relevant context
   - Organize by priority (critical → nice-to-know)

4. **Update Context Index**
   - Add new decisions to index
   - Update integration map
   - Archive superseded information

5. **Suggest Compression**
   - Identify when context is getting too large
   - Recommend archiving older decisions
   - Propose context reorganization

## Context Formats

### Quick Context (< 500 tokens)

Use for immediate handoffs or focused tasks:

```markdown
## Current Task
[What we're doing right now]

## Recent Decisions
- Decision 1 (affects X)
- Decision 2 (affects Y)

## Active Blockers
- Blocker 1: [description]
- Blocker 2: [description]

## Next Steps
1. Step 1
2. Step 2
```

### Full Context (< 2000 tokens)

Use for new sessions or major transitions:

```markdown
## Project Overview
[One paragraph summary]

## Architecture
- Component A: [purpose and location]
- Component B: [purpose and location]
- Integration: [how they connect]

## Key Decisions
1. Decision 1: [what + why]
2. Decision 2: [what + why]

## Active Work Streams
- Stream 1: [status and next steps]
- Stream 2: [status and next steps]

## Integration Points
- API endpoints
- Database schema
- Event systems

## Known Issues
- Issue 1: [description and workaround]
```

### Archived Context

Store in project documentation or memory:

```markdown
## Historical Decisions
- Date: Decision with full rationale
- Date: Decision with full rationale

## Resolved Issues
- Issue: Solution that worked

## Pattern Library
- Pattern 1: [when to use + example]
- Pattern 2: [when to use + example]

## Performance Benchmarks
- Benchmark 1: [results and implications]
```

## Best Practices

### Optimize for Relevance

- **Less is More**: Include only context that affects future work
- **Time-Sensitive**: Prioritize recent decisions over historical ones
- **Action-Oriented**: Focus on "what to do" not "what happened"

### Organize Hierarchically

```
Critical (read first):
- Decisions affecting current work
- Active blockers

Important (read if time):
- Recent patterns
- Integration points

Reference (as needed):
- Historical decisions
- Resolved issues
```

### Use Clear Markers

- **[BREAKING]**: Changes that require updates elsewhere
- **[PATTERN]**: Reusable solution
- **[BLOCKER]**: Needs resolution before progress
- **[TODO]**: Action item
- **[DECISION]**: Architectural choice

### Validate Context Quality

Ask yourself:
- Would this help an agent starting fresh?
- Is outdated information removed?
- Are decisions linked to their rationale?
- Is the context actionable?

## Example: Project Checkpoint

```markdown
# Project Checkpoint: User Authentication System

## Status
Authentication system 80% complete. Core flow working, need social login integration.

## Key Decisions
1. **[DECISION]** Using JWT tokens (not sessions)
   - Rationale: Stateless, scales better
   - Files: `src/auth/jwt.ts`

2. **[PATTERN]** Refresh token rotation
   - Implementation: `src/auth/refresh.ts`
   - Prevents token theft

## Active Work
- **Next**: Integrate Google OAuth
- **Blocked**: Need OAuth credentials from client

## Integration Points
- `/api/auth/login` - Returns JWT + refresh token
- `/api/auth/refresh` - Rotates tokens
- Middleware: `src/middleware/auth.ts`

## Known Issues
- **[TODO]** Rate limiting not implemented yet
  - Required before production
  - See: planning/security-checklist.md

## Context for Next Agent
Focus on Google OAuth integration. JWT setup is complete and working. Use existing pattern from `src/auth/jwt.ts` for token generation.
```

## Common Patterns

### Agent Handoff

```markdown
## Handoff: [From Agent] → [To Agent]

**Completed:**
- Task 1
- Task 2

**Context for Next Agent:**
[Minimal brief - what they need to know]

**Files Modified:**
- file1.ts: [what changed]
- file2.ts: [what changed]

**Next Steps:**
1. Step 1
2. Step 2
```

### Session Continuity

```markdown
## Session Resume: [Date]

**Last Session:**
Completed X, Y, Z. Stopped at point P.

**Current State:**
- Component A: Working
- Component B: In progress (60%)
- Component C: Not started

**Resume Here:**
Continue with Component B. See `src/B/TODO.md` for checklist.
```

### Context Compression

When context exceeds 2000 tokens:

1. **Archive** historical decisions → separate doc
2. **Consolidate** related items
3. **Remove** resolved issues
4. **Summarize** older work streams
5. **Keep** only active context in main doc

## Tools and Techniques

### Using TodoWrite

Track context management tasks:
```
- [ ] Extract decisions from Agent A output
- [ ] Create briefing for Agent B
- [ ] Update project context index
- [ ] Archive superseded information
```

### Using Write/Edit

Create and maintain context documents:
- `CONTEXT.md` - Current project state
- `DECISIONS.md` - Architectural decisions
- `PATTERNS.md` - Reusable solutions
- `HANDOFFS.md` - Agent-to-agent briefings

### File Organization

```
project-root/
├── .context/
│   ├── current.md          # Active context
│   ├── decisions.md        # Key decisions
│   ├── patterns.md         # Reusable patterns
│   └── archive/
│       └── 2025-10-01.md   # Historical checkpoint
```

## Success Metrics

Good context management achieves:

- ✅ Agents can start productive work within 1 minute of handoff
- ✅ No redundant questions about past decisions
- ✅ Clear understanding of integration points
- ✅ Active blockers are visible and tracked
- ✅ Context size stays under 2000 tokens (for full context)

Poor context management looks like:

- ❌ "What were we doing again?"
- ❌ Repeating already-made decisions
- ❌ Searching for integration points
- ❌ Untracked blockers causing delays
- ❌ Context bloat (>5000 tokens)

## Remember

**Good context accelerates work. Bad context creates confusion.**

Focus on:
- Relevance over completeness
- Actionable over historical
- Minimal over comprehensive
- Fresh over stale

The goal is to make the next agent (or session) immediately productive, not to document everything that happened.

---
name: cleaning-up-post-task
short_description: >-
  Review git status, remove temporary artifacts, and ensure adherence to project
  philosophy principles after task completion.
description: >-
  Use when tasks or todo lists are completed to review git status, remove
  temporary artifacts, eliminate unnecessary complexity, and ensure adherence to
  project philosophy principles. Proactively invoked after task completion to
  maintain codebase hygiene and ruthless simplicity. Triggers include "task
  completed", "todo list done", "cleanup needed", "ensure simplicity", "remove
  cruft", "check for temporary files", or after major implementation work.
when_to_use: >-
  Use when tasks or todo lists are completed to review git status, remove
  temporary artifacts (planning docs, test scripts, debug

  files), eliminate unnecessary complexity, ensure adherence to Implementation
  Philosophy and Modular Design Philosophy principles,

  maintain codebase hygiene...
version: 1.0.0
category: productivity
---

You are a Post-Task Cleanup Specialist, the guardian of codebase hygiene who ensures ruthless simplicity and modular clarity after every task completion. You embody the Wabi-sabi philosophy of removing all but the essential, treating every completed task as an opportunity to reduce complexity and eliminate cruft.

**Core Mission:**
You are invoked after todo lists are completed to ensure the codebase remains pristine. You review all changes, remove temporary artifacts, eliminate unnecessary complexity, and ensure strict adherence to the project's implementation and modular design philosophies.

**Primary Responsibilities:**

## 1. Git Status Analysis

First action: Always run `git status` to identify:

- New untracked files created during the task
- Modified files that need review
- Staged changes awaiting commit

```bash
git status --porcelain  # For programmatic parsing
git diff HEAD --name-only  # For all changed files
```

## 2. Philosophy Compliance Check

Review all touched files against the Implementation Philosophy and Modular Design Philosophy (see reference sections below):

**Ruthless Simplicity Violations to Find:**

- Backwards compatibility code (unless explicitly required in conversation history)
- Future-proofing for hypothetical scenarios
- Unnecessary abstractions or layers
- Over-engineered solutions
- Complex state management
- Excessive error handling for unlikely scenarios

**Modular Design Violations to Find:**

- Modules not following "bricks & studs" pattern
- Missing or unclear contracts
- Cross-module internal dependencies
- Modules doing more than one clear responsibility

## 3. Artifact Cleanup Categories

**Must Remove:**

- Temporary planning documents (`__plan.md`, `__notes.md`, `implementation_guide.md`)
- Test artifacts (`test_*.py` files created just for validation, not proper tests)
- Sample/example files (`example*.py`, `sample*.json`)
- Mock implementations (any mocks used as workarounds)
- Debug files (`debug__.log`, `*.debug`)
- Scratch files (`scratch.py`, `temp*.py`, `tmp*`)
- IDE artifacts (`.idea/`, `.vscode/` if accidentally added)
- Backup files (`*.bak`, `*.backup`, `*_old.py`)

**Must Review for Removal:**

- Documentation created during implementation (keep only if explicitly requested)
- Scripts created for one-time tasks
- Configuration files no longer needed
- Test data files used temporarily

## 4. Code Review Checklist

For files that remain, check for:

- No commented-out code blocks
- No TODO/FIXME comments from the just-completed task
- No console.log/print debugging statements
- No unused imports
- No mock data hardcoded in production code
- No backwards compatibility shims
- All files end with newline

## 5. Action Protocol

You CAN directly:

- Suggest (but don't do):
  - Temporary artifacts to delete: `rm <file>`
  - Reorganization of files: `mv <source> <destination>`
  - Rename files for clarity: `mv <old_name> <new_name>`
  - Remove empty directories: `rmdir <directory>`

You CANNOT directly:

- Delete, move, rename files (suggest so that others that have more context can decide what to do)
- Modify code within files (delegate to appropriate sub-agent)
- Refactor existing implementations (delegate to appropriate agent)
- Fix bugs you discover (delegate to appropriate agent)

## 6. Delegation Instructions

When you find issues requiring code changes:

### Issues Requiring Code Changes

#### Issue 1: [Description]

**File**: [path/to/file.py:line]
**Problem**: [Specific violation of philosophy]
**Recommendation**: Use the [agent-name] agent to [specific action]
**Rationale**: [Why this violates our principles]

#### Issue 2: [Description]

...

## 7. Final Report Format

Always conclude with a structured report:

```markdown
# Post-Task Cleanup Report

## Cleanup Actions Suggested

### Files To Remove

- `path/to/file1.py` - Reason: Temporary test script
- `path/to/file2.md` - Reason: Implementation planning document
- [etc...]

### Files To Move/Rename

- `old/path` → `new/path` - Reason: Better organization
- [etc...]

## Issues Found Requiring Attention

### High Priority (Violates Core Philosophy)

1. **[Issue Title]**
   - File: [path:line]
   - Problem: [description]
   - Action Required: Use [agent] to [action]

### Medium Priority (Could Be Simpler)

1. **[Issue Title]**
   - File: [path:line]
   - Suggestion: [improvement]
   - Optional: Use [agent] if you want to optimize

### Low Priority (Style/Convention)

1. **[Issue Title]**
   - Note: [observation]

## Philosophy Adherence Score

- Ruthless Simplicity: [✅/⚠️/❌]
- Modular Design: [✅/⚠️/❌]
- No Future-Proofing: [✅/⚠️/❌]
- Library Usage: [✅/⚠️/❌]

## Recommendations for Next Time

- [Preventive measure 1]
- [Preventive measure 2]

## Status: [CLEAN/NEEDS_ATTENTION]
```

## Decision Framework

For every file encountered, ask:

1. "Is this file essential to the completed feature?"
2. "Does this file serve the production codebase?"
3. "Will this file be needed tomorrow?"
4. "Does this follow our simplicity principles?"
5. "Is this the simplest possible solution?"

If any answer is "no" → Remove or flag for revision

## Key Principles

- **Be Ruthless**: If in doubt, remove it. Code not in the repo has no bugs.
- **Trust Git**: As long as they have been previously committed (IMPORTANT REQUIREMENT), deleted files can be recovered if truly needed
- **Preserve Working Code**: Never break functionality in pursuit of cleanup
- **Document Decisions**: Always explain why something should be removed or has otherwise been flagged
- **Delegate Wisely**: You're the inspector, not the fixer

Remember: Your role is to ensure every completed task leaves the codebase cleaner than before. You are the final quality gate that prevents technical debt accumulation.

---

# Reference: Implementation Philosophy

Core implementation philosophy and guidelines for software development projects—a central reference for decision-making and development approach.

## Core Philosophy

Zen-like minimalism valuing simplicity and clarity:

- **Wabi-sabi philosophy**: Embrace simplicity and the essential
- **Occam's Razor**: Simple as possible, no simpler
- **Trust in emergence**: Complex systems from simple components
- **Present-moment focus**: Current needs, not future scenarios
- **Pragmatic trust**: Handle failures as they occur

Values clear documentation, readable code, and emergent architecture.

## Core Design Principles

### 1. Ruthless Simplicity

- Simple as possible, no simpler
- Every abstraction must justify itself
- Start minimal, grow as needed
- Don't build for hypothetical futures
- Regularly challenge complexity

### 2. Architectural Integrity with Minimal Implementation

- Preserve key patterns (MCP, SSE, separate I/O channels)
- Maintain benefits with simpler code
- Lightweight implementations, solid foundations
- Complete flows over perfect components

### 3. Library vs Custom Code

A judgment call evolving with requirements. No rigid rules—understand trade-offs and revisit as needed.

**Evolution:** Start simple → Switch when complex → Return to custom when outgrowing library

**Custom code when:** Need is simple, exact requirements, libraries need workarounds, unique domain problem

**Libraries when:** Solve complex problems, align well, battle-tested, complexity exceeds integration cost

**Making the call:** Alignment with needs? Fighting or working with library? Clean integration? Future requirements within capabilities? Problem complex enough for dependency?

**Stay flexible:** Minimal, isolated integration points. No shame switching approaches.

## Technical Implementation Guidelines

**API Layer:** Essential endpoints, minimal middleware, clear errors, consistent patterns

**Database:** Simple schema, TEXT/JSON fields to avoid early normalization, add indexes when needed

**MCP:** Streamlined client, use FastMCP when possible, core functionality, simple lifecycle, essential health checks

**SSE:** Basic connection management, simple subscriptions, direct delivery, minimal state

**Event System:** Simple pub/sub, direct delivery, clear minimal payloads, basic error handling

**LLM Integration:** Direct PydanticAI, minimal transformation, handle common errors, skip elaborate caching initially

**Message Routing:** Simplified queue-based processing, direct routing

## Development Approach

**Vertical Slices:** End-to-end functionality, core journeys first, data through all layers early

**Iterative:** 80/20 principle, one working > multiple partial, validate before enhancing, refactor as patterns emerge

**Testing:** Integration and e2e emphasis, manual testability, critical path first, unit tests for complex logic (60% unit, 30% integration, 10% e2e)

**Errors:** Handle common robustly, log detailed info, clear user messages, fail fast and visibly in development

## Decision-Making Framework

1. **Necessity**: Need this now?
2. **Simplicity**: Simplest solution?
3. **Directness**: More direct approach?
4. **Value**: Complexity adds proportional value?
5. **Maintenance**: Easy to understand and change?

## Areas to Embrace Complexity

1. Security fundamentals
2. Data integrity
3. Core user experience
4. Error visibility

## Areas to Aggressively Simplify

1. Internal abstractions
2. Generic "future-proof" code
3. Edge case handling
4. Framework usage
5. State management

## Practical Examples

### Good: Direct SSE Implementation

```python
class SseManager:
    def __init__(self):
        self.connections = {}

    async def add_connection(self, resource_id, user_id):
        connection_id = str(uuid.uuid4())
        queue = asyncio.Queue()
        self.connections[connection_id] = {
            "resource_id": resource_id,
            "user_id": user_id,
            "queue": queue
        }
        return queue, connection_id

    async def send_event(self, resource_id, event_type, data):
        for conn_id, conn in self.connections.items():
            if conn["resource_id"] == resource_id:
                await conn["queue"].put({
                    "event": event_type,
                    "data": data
                })
```

### Bad: Over-engineered SSE

```python
class ConnectionRegistry:
    def __init__(self, metrics_collector, cleanup_interval=60):
        self.connections_by_id = {}
        self.connections_by_resource = defaultdict(list)
        self.connections_by_user = defaultdict(list)
        self.metrics_collector = metrics_collector
        self.cleanup_task = asyncio.create_task(self._cleanup_loop(cleanup_interval))
    # [50+ more lines of complex indexing and state management]
```

### Good: Simple MCP Client

```python
class McpClient:
    def __init__(self, endpoint: str, service_name: str):
        self.endpoint = endpoint
        self.service_name = service_name
        self.client = None

    async def connect(self):
        if self.client is not None:
            return
        try:
            async with sse_client(self.endpoint) as (read_stream, write_stream):
                self.client = ClientSession(read_stream, write_stream)
                await self.client.initialize()
        except Exception as e:
            self.client = None
            raise RuntimeError(f"Failed to connect to {self.service_name}: {str(e)}")

    async def call_tool(self, name: str, arguments: dict):
        if not self.client:
            await self.connect()
        return await self.client.call_tool(name=name, arguments=arguments)
```

### Bad: Over-engineered MCP Client

```python
class EnhancedMcpClient:
    def __init__(self, endpoint, service_name, retry_strategy, health_check_interval):
        self.endpoint = endpoint
        self.service_name = service_name
        self.state = ConnectionState.DISCONNECTED
        self.retry_strategy = retry_strategy
        self.connection_attempts = 0
        self.last_error = None
        self.health_check_interval = health_check_interval
        # [50+ more lines of complex state tracking and retry logic]
```

## Remember

- Easier to add complexity later than remove it
- Code you don't write has no bugs
- Favor clarity over cleverness
- Best code is often simplest

---

# Reference: Modular Design Philosophy

_By Brian Krabach, 3/28/2025_

Imagine building a complex construction brick spaceship. You follow a blueprint step by step, and each piece snaps together correctly. **Now imagine those bricks could assemble themselves** when given the right instructions. This is our AI-driven software development approach: **we provide the blueprint, and AI builds the product, one modular piece at a time.**

Like a brick model, our software comprises small, clear modules. Each module is a self-contained "brick" with defined connectors (interfaces) to the rest of the system. Because these connection points are standard and stable, we can generate or regenerate any module independently without breaking the whole. Need to improve user login? Have AI rebuild just that piece according to spec, then snap it back in --- seamlessly. For broad, cross-cutting changes, we hand AI a bigger blueprint and let it rebuild that entire chunk. **Crucially, the external system contracts remain unchanged.** A regenerated system still fits perfectly into its environment, though internally it's rebuilt with fresh optimizations.

When using LLM-powered tools, even tiny edits mean the LLM generates new code from specifications. We embrace this: **we treat code as something to describe and let AI generate.** By keeping each task _small and self-contained_, we ensure AI has the context needed to generate correctly. The system prefers regenerating modules within bounded contexts rather than challenging code-level edits. The result: code consistently in sync with its specification.

## The Human Role: From Code Mechanics to Architects

Humans shift from code mechanics to architects and quality inspectors. Like a master builder, humans define the vision and specifications --- the blueprint. Once handed off, they don't hover over every brick placement or read the code. Instead, they focus on whether the product meets the vision. They work at the specification level: designing requirements, clarifying behavior, and evaluating the finished module by testing its behavior. If login is rebuilt, the human tests whether users can log in smoothly --- not by reviewing source code. This elevates human involvement where it's most valuable.

## Building in Parallel

The biggest leap: we can build multiple solutions simultaneously. Because AI builders work quickly and handle modular instructions well, we can spawn multiple software versions in parallel. Imagine generating and testing multiple feature variants at once --- different recommendation algorithms tested side by side, or the same application built for multiple platforms simultaneously. Each variant teaches us something. We refine our specifications and regenerate again for another iteration. This cycle of parallel experimentation and rapid regeneration means faster, fearless innovation --- a development playground on an unprecedented scale.

In short, this brick-inspired, AI-driven approach flips software development. We break work into defined pieces, let AI assemble and reassemble them, and keep humans focused on guiding vision and validating results. The outcome: more flexible, faster, and liberating. We reshape software as easily as rebuilding a model and build multiple versions in parallel. For stakeholders, this means delivering the right solution faster, adapting without fear, and continually exploring new ideas --- brick by brick, at a new standard for innovation.

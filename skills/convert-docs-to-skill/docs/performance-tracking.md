# Performance Tracking

Track time, tokens, and cache hit rate per phase to monitor optimization effectiveness.

## Usage

### In Skill Creation Workflow

```python
from scripts.performance_tracker import init_tracker, start_phase, end_phase, finalize_and_report

# Initialize tracker
tracker = init_tracker("ripgrep", "14.0.0")

# Track each phase
start_phase("Phase 1: Documentation Gathering", agent_count=1)
# ... do work ...
end_phase(tokens_used=5000)

start_phase("Phase 2: Analysis & Design", agent_count=2, cache_hit=False)
# ... do work ...
end_phase(tokens_used=25000)

# Finalize and get report
report = finalize_and_report()
print(report)
```

### Command Line

```bash
# View performance report for a tool
python scripts/performance_tracker.py report ripgrep
```

## Metrics Tracked

### Per Phase
- **Duration** - Time spent in phase (seconds)
- **Tokens Used** - Estimated token consumption
- **Cache Hit** - Whether phase used cached results
- **Agent Count** - Number of agents used
- **Errors** - Any errors encountered

### Overall
- **Total Duration** - End-to-end time
- **Total Tokens** - Sum of all phase tokens
- **Estimated Cost** - Cost based on token usage
- **Cache Hit Rate** - Percentage of phases using cache
- **Speedup** - Comparison to manual/previous approaches

## Performance Logs

Logs are saved to `.cache/performance/` directory:

```
.cache/performance/
├── ripgrep-20251108-120000.json
├── jq-20251108-130000.json
└── ast-grep-20251108-140000.json
```

Each log file contains complete metrics in JSON format.

## Example Report

```
============================================================
Skill Creation Performance Report: ripgrep
============================================================

Phase Breakdown:
------------------------------------------------------------
  Phase 1: Documentation Gathering: 180.0s (5,000 tokens) (1 agents)
  Phase 2: Analysis & Design: 240.0s (25,000 tokens) (2 agents)
  Phase 4: Artifact Creation: 120.0s (15,000 tokens) (2 agents)
  Phase 5: SKILL.md Creation: 300.0s (10,000 tokens)
  Phase 6: Integration & Testing: 180.0s (5,000 tokens) (1 agents)

Summary:
------------------------------------------------------------
  Total Time: 1020.0 seconds (17.0 minutes)
  Total Tokens: 60,000
  Estimated Cost: $0.0600
  Cache Hits: 0
  Cache Hit Rate: 0.0%

Performance Comparison:
------------------------------------------------------------
  vs Manual (31 min): 1.8x faster
  vs Previous (19 min): 1.1x faster
============================================================
```

## Cache Hit Example

When cache is used:

```
Phase Breakdown:
------------------------------------------------------------
  Phase 1: Documentation Gathering: 180.0s (5,000 tokens) (1 agents)
  Phase 2: Analysis & Design: 5.0s (cached) (0 agents)
  Phase 4: Artifact Creation: 120.0s (15,000 tokens) (2 agents)
  ...

Summary:
------------------------------------------------------------
  Total Time: 785.0 seconds (13.1 minutes)
  Cache Hits: 1
  Cache Hit Rate: 20.0%
```

## Integration

Add tracking to skill creation workflow:

1. Initialize tracker at start
2. Track each phase (start/end)
3. Record tokens and cache hits
4. Generate report at end

**See:** `scripts/performance_tracker.py` for implementation


#!/usr/bin/env python3
"""
Performance tracking for convert-docs-to-skill workflow.

Tracks time, tokens, and cache hit rate per phase.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict

PERF_LOG_DIR = Path(__file__).parent.parent / ".cache" / "performance"
PERF_LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class PhaseMetrics:
    """Metrics for a single phase."""
    phase: str
    start_time: float
    end_time: Optional[float] = None
    duration_seconds: Optional[float] = None
    tokens_used: Optional[int] = None
    cache_hit: bool = False
    agent_count: int = 0
    error: Optional[str] = None


@dataclass
class SkillCreationMetrics:
    """Complete metrics for skill creation."""
    tool_name: str
    version: str
    start_time: str
    end_time: Optional[str] = None
    total_duration_seconds: Optional[float] = None
    total_tokens: int = 0
    total_cost: float = 0.0
    cache_hits: int = 0
    phases: list[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.phases is None:
            self.phases = []


class PerformanceTracker:
    """Track performance metrics for skill creation."""
    
    def __init__(self, tool_name: str, version: str = "unknown"):
        self.tool_name = tool_name
        self.version = version
        self.metrics = SkillCreationMetrics(
            tool_name=tool_name,
            version=version,
            start_time=datetime.now().isoformat()
        )
        self.current_phase: Optional[PhaseMetrics] = None
    
    def start_phase(self, phase: str, agent_count: int = 0, cache_hit: bool = False):
        """Start tracking a phase."""
        if self.current_phase:
            self.end_phase()
        
        self.current_phase = PhaseMetrics(
            phase=phase,
            start_time=time.time(),
            agent_count=agent_count,
            cache_hit=cache_hit
        )
    
    def end_phase(self, tokens_used: Optional[int] = None, error: Optional[str] = None):
        """End tracking current phase."""
        if not self.current_phase:
            return
        
        self.current_phase.end_time = time.time()
        self.current_phase.duration_seconds = (
            self.current_phase.end_time - self.current_phase.start_time
        )
        
        if tokens_used:
            self.current_phase.tokens_used = tokens_used
            self.metrics.total_tokens += tokens_used
        
        if error:
            self.current_phase.error = error
        
        # Add to phases list
        self.metrics.phases.append(asdict(self.current_phase))
        
        # Update cache hit count
        if self.current_phase.cache_hit:
            self.metrics.cache_hits += 1
        
        self.current_phase = None
    
    def estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token usage."""
        # Rough estimates: Sonnet $3/1M input, $15/1M output; Haiku $0.25/1M input, $1.25/1M output
        # Assume 50/50 input/output split for simplicity
        sonnet_cost_per_1M = (3 + 15) / 2  # $9 per 1M tokens
        haiku_cost_per_1M = (0.25 + 1.25) / 2  # $0.75 per 1M tokens
        
        # Estimate: Phase 2 uses Sonnet (analysis), Phase 4 uses Haiku (generation)
        # Rough estimate: 60% Sonnet, 40% Haiku
        avg_cost_per_1M = (0.6 * sonnet_cost_per_1M) + (0.4 * haiku_cost_per_1M)
        
        return (tokens / 1_000_000) * avg_cost_per_1M
    
    def finalize(self):
        """Finalize metrics and save to log."""
        if self.current_phase:
            self.end_phase()
        
        self.metrics.end_time = datetime.now().isoformat()
        
        # Calculate total duration
        start = datetime.fromisoformat(self.metrics.start_time)
        end = datetime.fromisoformat(self.metrics.end_time)
        self.metrics.total_duration_seconds = (end - start).total_seconds()
        
        # Estimate cost
        if self.metrics.total_tokens > 0:
            self.metrics.total_cost = self.estimate_cost(self.metrics.total_tokens)
        
        # Save to log file
        self._save_log()
        
        return self.metrics
    
    def _save_log(self):
        """Save metrics to log file."""
        log_file = PERF_LOG_DIR / f"{self.tool_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(log_file, "w") as f:
            json.dump(asdict(self.metrics), f, indent=2)
    
    def generate_report(self) -> str:
        """Generate human-readable performance report."""
        if not self.metrics.phases:
            return "No metrics collected yet."
        
        report = []
        report.append("=" * 60)
        report.append(f"Skill Creation Performance Report: {self.tool_name}")
        report.append("=" * 60)
        report.append("")
        
        # Phase breakdown
        report.append("Phase Breakdown:")
        report.append("-" * 60)
        for phase_data in self.metrics.phases:
            phase = phase_data["phase"]
            duration = phase_data.get("duration_seconds", 0)
            tokens = phase_data.get("tokens_used", 0)
            cache_hit = phase_data.get("cache_hit", False)
            agents = phase_data.get("agent_count", 0)
            
            cache_indicator = " (cached)" if cache_hit else ""
            agent_info = f" ({agents} agents)" if agents > 0 else ""
            
            report.append(f"  {phase}: {duration:.1f}s{tokens and f' ({tokens:,} tokens)' or ''}{cache_indicator}{agent_info}")
        
        report.append("")
        
        # Summary
        report.append("Summary:")
        report.append("-" * 60)
        report.append(f"  Total Time: {self.metrics.total_duration_seconds:.1f} seconds ({self.metrics.total_duration_seconds/60:.1f} minutes)")
        report.append(f"  Total Tokens: {self.metrics.total_tokens:,}")
        report.append(f"  Estimated Cost: ${self.metrics.total_cost:.4f}")
        report.append(f"  Cache Hits: {self.metrics.cache_hits}")
        report.append(f"  Cache Hit Rate: {self.metrics.cache_hits / len(self.metrics.phases) * 100:.1f}%")
        report.append("")
        
        # Performance comparison
        report.append("Performance Comparison:")
        report.append("-" * 60)
        report.append(f"  vs Manual (31 min): {31*60 / self.metrics.total_duration_seconds:.1f}x faster")
        report.append(f"  vs Previous (19 min): {19*60 / self.metrics.total_duration_seconds:.1f}x faster")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# Convenience functions for use in skill workflow

_tracker: Optional[PerformanceTracker] = None


def init_tracker(tool_name: str, version: str = "unknown") -> PerformanceTracker:
    """Initialize global performance tracker."""
    global _tracker
    _tracker = PerformanceTracker(tool_name, version)
    return _tracker


def get_tracker() -> Optional[PerformanceTracker]:
    """Get current performance tracker."""
    return _tracker


def start_phase(phase: str, agent_count: int = 0, cache_hit: bool = False):
    """Start tracking a phase."""
    if _tracker:
        _tracker.start_phase(phase, agent_count, cache_hit)


def end_phase(tokens_used: Optional[int] = None, error: Optional[str] = None):
    """End tracking current phase."""
    if _tracker:
        _tracker.end_phase(tokens_used, error)


def finalize_and_report() -> str:
    """Finalize metrics and return report."""
    if _tracker:
        metrics = _tracker.finalize()
        return _tracker.generate_report()
    return "No tracker initialized."


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: performance_tracker.py <command> [args]")
        print("Commands: report <tool-name>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "report":
        if len(sys.argv) < 3:
            print("Usage: performance_tracker.py report <tool-name>")
            sys.exit(1)
        
        tool_name = sys.argv[2]
        
        # Find most recent log for this tool
        log_files = sorted(
            PERF_LOG_DIR.glob(f"{tool_name}-*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not log_files:
            print(f"No performance logs found for {tool_name}")
            sys.exit(1)
        
        # Load and display most recent
        with open(log_files[0]) as f:
            metrics_data = json.load(f)
        
        tracker = SkillCreationMetrics(**metrics_data)
        temp_tracker = PerformanceTracker(tool_name, tracker.version)
        temp_tracker.metrics = tracker
        
        print(temp_tracker.generate_report())


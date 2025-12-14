#!/usr/bin/env bun
/**
 * Generate individual markdown files from improvement plan JSON
 *
 * Usage:
 *   bun run scripts/generate-plan-docs.ts                    # Use embedded JSON
 *   bun run scripts/generate-plan-docs.ts --input plan.json  # Use external JSON file
 *   bun run scripts/generate-plan-docs.ts --output ./plans   # Custom output directory
 */

import { writeFileSync, mkdirSync, existsSync, readFileSync } from 'fs';
import { join } from 'path';

interface Scores {
  impact: number;
  effort: number;
  expertise: number;
  risk: number;
  novelty: number;
}

interface Improvement {
  id: string;
  title: string;
  category: 'Conventional' | 'Creative' | 'Moonshot';
  type: string;
  area: string;
  owner_role: string;
  scores: Scores;
  priority_score: number;
  targets: string[];
  search_tokens: string[];
  implementation_steps: string[];
  acceptance_criteria: string[];
  test_plan: string[];
  dependencies: string[];
  risk_mitigation: string;
  experiment?: string;
  success_metric?: string;
  rollback_plan?: string;
}

interface Epic {
  id: string;
  title: string;
  improvement_ids: string[];
}

interface FocusSummary {
  purpose: string;
  key_flows: string[];
  constraints: string[];
  risks_or_unknowns: string[];
}

interface PlanData {
  focus_summary: FocusSummary;
  improvements: Improvement[];
  epics: Epic[];
  recommended_sequence: string[];
}

// Embedded plan data - can be overridden with --input flag
const PLAN_DATA: PlanData = {
  "focus_summary": {
    "purpose": "Personal skills library with 100+ domain-specific skills, automatic skill suggestion via hybrid search (Fuse.js + TF-IDF + rules), metrics tracking, and maintenance tooling",
    "key_flows": [
      "UserPromptSubmit hook analyzes prompts and suggests relevant skills",
      "SessionStart hook injects PAI context automatically",
      "Garden scripts validate skill frontmatter, links, and coverage",
      "Metrics track suggestions, activations, searches, and gaps"
    ],
    "constraints": [
      "Bun runtime required",
      "Skills must have SKILL.md with valid YAML frontmatter",
      "Metrics stored in lib/skill-metrics.json (gitignored)"
    ],
    "risks_or_unknowns": [
      "Massive suggestion-to-activation gap (1193 suggestions, 3 activations) indicates skill relevance issues",
      "1679-line analyzer file is complex and hard to maintain",
      "No automated skill quality scoring beyond frontmatter validation",
      "Gap detection is passive - requires manual review"
    ]
  },
  "improvements": [
    {
      "id": "IMP-001",
      "title": "Add skill effectiveness scoring to close suggestion-activation gap",
      "category": "Conventional",
      "type": "observability",
      "area": "backend",
      "owner_role": "Fullstack",
      "scores": {
        "impact": 5,
        "effort": 2,
        "expertise": 2,
        "risk": 1,
        "novelty": 2
      },
      "priority_score": 2.5,
      "targets": [
        "hooks/prompt-submit/analyze-prompt-skills.ts:420-443",
        "scripts/view-metrics.ts"
      ],
      "search_tokens": ["recordSkillSuggestions", "recordSkillActivation", "SkillMetrics"],
      "implementation_steps": [
        "Add `effectiveness` field to SkillMetrics interface: Record<string, {suggestions: number, activations: number, rate: number}>",
        "Calculate activation rate on each recordSkillActivation call: activations[skill] / suggestions[skill]",
        "Add --effectiveness flag to view-metrics.ts showing activation rates sorted by gap",
        "Update formatSkillSuggestions to deprioritize skills with <5% activation rate after 50+ suggestions",
        "Add periodic console warning when top-suggested skill has <10% activation rate"
      ],
      "acceptance_criteria": [
        "[ ] Running `bun run scripts/view-metrics.ts --effectiveness` shows activation rates for all suggested skills",
        "[ ] Skills with <5% activation rate after 50+ suggestions are marked with ⚠️ in suggestions output",
        "[ ] Metrics JSON includes effectiveness field with calculated rates",
        "[ ] Existing tests pass"
      ],
      "test_plan": [
        "Unit test: recordSkillActivation calculates rate correctly (hooks/__tests__/)",
        "Integration test: view-metrics.ts --effectiveness outputs expected format",
        "Manual test: Activate a skill and verify rate updates in metrics"
      ],
      "dependencies": [],
      "risk_mitigation": "Non-breaking change - adds new metrics field, existing behavior unchanged",
      "experiment": "",
      "success_metric": "",
      "rollback_plan": ""
    },
    {
      "id": "IMP-002",
      "title": "Create auto-fix command for common frontmatter issues",
      "category": "Conventional",
      "type": "DX",
      "area": "build",
      "owner_role": "Fullstack",
      "scores": {
        "impact": 4,
        "effort": 2,
        "expertise": 2,
        "risk": 1,
        "novelty": 2
      },
      "priority_score": 2.0,
      "targets": [
        "scripts/check-frontmatter.sh",
        "scripts/garden.sh"
      ],
      "search_tokens": ["missing_version", "long_when_to_use", "add_issue_json"],
      "implementation_steps": [
        "Create scripts/fix-frontmatter.ts with Bun to parse and modify YAML frontmatter",
        "Implement auto-fixes: add missing version (1.0.0), truncate long when_to_use to 300 chars with ellipsis",
        "Add --fix flag to garden.sh that runs fix-frontmatter.ts after check-frontmatter.sh",
        "Support --dry-run flag to preview changes without writing",
        "Log all changes to stdout for review"
      ],
      "acceptance_criteria": [
        "[ ] Running `./scripts/garden.sh --fix` auto-adds missing version fields",
        "[ ] Long when_to_use fields are truncated to 300 chars with '...'",
        "[ ] --dry-run shows changes without modifying files",
        "[ ] Running garden.sh again after fix shows fewer warnings"
      ],
      "test_plan": [
        "Unit test: fix-frontmatter.ts correctly modifies test SKILL.md files",
        "Integration test: garden.sh --fix reduces warning count",
        "Manual test: Run on actual skills directory, verify changes are sensible"
      ],
      "dependencies": [],
      "risk_mitigation": "--dry-run flag required for first run; changes logged for review before commit",
      "experiment": "",
      "success_metric": "",
      "rollback_plan": ""
    },
    {
      "id": "IMP-003",
      "title": "Implement lazy skill indexing with persistent cache",
      "category": "Conventional",
      "type": "perf",
      "area": "backend",
      "owner_role": "Fullstack",
      "scores": {
        "impact": 4,
        "effort": 2,
        "expertise": 3,
        "risk": 2,
        "novelty": 2
      },
      "priority_score": 2.0,
      "targets": [
        "hooks/prompt-submit/analyze-prompt-skills.ts:732-776"
      ],
      "search_tokens": ["discoverSkillsCached", "skillCache", "CacheEntry"],
      "implementation_steps": [
        "Create lib/skill-index.json to persist skill cache across sessions",
        "On hook startup, load skill-index.json if exists and mtime < 1 hour",
        "Store Fuse.js serialized index in cache for O(1) search initialization",
        "Add --rebuild-index flag to force cache invalidation",
        "Add cache hit/miss logging when SKILL_ANALYZER_DEBUG=1"
      ],
      "acceptance_criteria": [
        "[ ] Second hook invocation within 1 hour uses cached index (visible in debug output)",
        "[ ] Cache invalidates when any SKILL.md mtime changes",
        "[ ] --rebuild-index flag forces fresh index build",
        "[ ] Hook latency reduced by >30% on cache hit (measure with `time`)"
      ],
      "test_plan": [
        "Unit test: Cache loads correctly from disk",
        "Unit test: Cache invalidates on file change",
        "Performance test: Measure hook latency with and without cache"
      ],
      "dependencies": [],
      "risk_mitigation": "Stale cache fallback: if cache load fails, rebuild silently",
      "experiment": "",
      "success_metric": "",
      "rollback_plan": ""
    },
    {
      "id": "IMP-004",
      "title": "Add skill scaffolding CLI with templates",
      "category": "Conventional",
      "type": "DX",
      "area": "build",
      "owner_role": "Fullstack",
      "scores": {
        "impact": 4,
        "effort": 3,
        "expertise": 2,
        "risk": 1,
        "novelty": 2
      },
      "priority_score": 1.33,
      "targets": [
        "scripts/"
      ],
      "search_tokens": ["create-skill", "skill-skeleton", "template-skill"],
      "implementation_steps": [
        "Create scripts/create-skill.ts as interactive CLI",
        "Prompt for: name (kebab-case), display name, category, short description",
        "Generate SKILL.md with valid frontmatter from template",
        "Create references/ and examples/ subdirectories if requested",
        "Add skill to skill-rules.json with default keywords from name tokens",
        "Output path to created skill and next steps"
      ],
      "acceptance_criteria": [
        "[ ] Running `bun run scripts/create-skill.ts` prompts for skill details",
        "[ ] Generated SKILL.md passes all garden.sh checks",
        "[ ] Skill appears in hook suggestions when queried by name",
        "[ ] References directory created when requested"
      ],
      "test_plan": [
        "Integration test: create-skill.ts generates valid skill structure",
        "Integration test: Created skill is discoverable by analyzer",
        "Manual test: Full workflow from creation to suggestion"
      ],
      "dependencies": [],
      "risk_mitigation": "Non-destructive - only creates new files, never overwrites",
      "experiment": "",
      "success_metric": "",
      "rollback_plan": ""
    },
    {
      "id": "IMP-005",
      "title": "Extract skill analyzer into modular library",
      "category": "Conventional",
      "type": "refactor",
      "area": "backend",
      "owner_role": "Fullstack",
      "scores": {
        "impact": 3,
        "effort": 3,
        "expertise": 3,
        "risk": 2,
        "novelty": 1
      },
      "priority_score": 1.0,
      "targets": [
        "hooks/prompt-submit/analyze-prompt-skills.ts"
      ],
      "search_tokens": ["scoreSkillRelevanceFuzzy", "scoreSkillsWithFuse", "scoreSkillsWithTfIdf", "loadSkillRules"],
      "implementation_steps": [
        "Create lib/skill-analyzer/ directory structure",
        "Extract scoring functions into lib/skill-analyzer/scoring.ts",
        "Extract caching logic into lib/skill-analyzer/cache.ts",
        "Extract metrics into lib/skill-analyzer/metrics.ts",
        "Extract discovery into lib/skill-analyzer/discovery.ts",
        "Keep hook as thin orchestrator importing from lib/"
      ],
      "acceptance_criteria": [
        "[ ] analyze-prompt-skills.ts reduced to <200 lines",
        "[ ] All existing tests pass without modification",
        "[ ] Each module has single responsibility and clear exports",
        "[ ] No circular dependencies between modules"
      ],
      "test_plan": [
        "Unit tests: Each extracted module has dedicated test file",
        "Integration test: Hook still produces identical output for same input",
        "Regression test: evals/run-evals.ts shows same pass rate"
      ],
      "dependencies": [],
      "risk_mitigation": "Pure refactor - no behavior changes; run evals before and after to verify",
      "experiment": "",
      "success_metric": "",
      "rollback_plan": ""
    },
    {
      "id": "IMP-006",
      "title": "Build session-aware skill recommendation engine",
      "category": "Creative",
      "type": "feature",
      "area": "backend",
      "owner_role": "Fullstack",
      "scores": {
        "impact": 5,
        "effort": 4,
        "expertise": 4,
        "risk": 2,
        "novelty": 4
      },
      "priority_score": 1.25,
      "targets": [
        "hooks/session-start/load-core-context.ts",
        "hooks/prompt-submit/analyze-prompt-skills.ts"
      ],
      "search_tokens": ["additionalContext", "SessionStart", "hookSpecificOutput"],
      "implementation_steps": [
        "Track session context: files read, tools used, skills activated in memory",
        "Build session skill profile: { domain: 'frontend' | 'backend' | 'infra', stack: string[], patterns: string[] }",
        "Weight skill scores by session profile match (e.g., frontend session boosts React skills)",
        "Add 'related skills' suggestions when a skill is activated",
        "Persist session profile to temp file for resumption"
      ],
      "acceptance_criteria": [
        "[ ] After reading React files, React-related skills rank higher for ambiguous queries",
        "[ ] Activating one skill suggests related skills in output",
        "[ ] Session profile visible in debug mode",
        "[ ] Profile persists across hook invocations within session"
      ],
      "test_plan": [
        "Unit test: Session profile builds correctly from mock file reads",
        "Integration test: Skill rankings change based on session context",
        "A/B test: Compare suggestion relevance with/without session awareness"
      ],
      "dependencies": [],
      "risk_mitigation": "Feature flag SKILL_SESSION_AWARE=1 to enable; default off initially",
      "experiment": "1-2 hour version: Add session context tracking without scoring changes, log to debug output to validate data collection",
      "success_metric": "Session profile correctly identifies domain in 80% of sessions based on manual review of 20 sessions",
      "rollback_plan": "Remove feature flag check to disable; no data dependencies"
    },
    {
      "id": "IMP-007",
      "title": "Add OpenTelemetry tracing for skill search pipeline",
      "category": "Creative",
      "type": "observability",
      "area": "backend",
      "owner_role": "Fullstack",
      "scores": {
        "impact": 4,
        "effort": 3,
        "expertise": 3,
        "risk": 1,
        "novelty": 3
      },
      "priority_score": 1.33,
      "targets": [
        "hooks/prompt-submit/analyze-prompt-skills.ts:1332-1387"
      ],
      "search_tokens": ["scoreSkillRelevanceHybrid", "findRelevantSkills", "fuseScores", "tfidfScores"],
      "implementation_steps": [
        "Add @opentelemetry/sdk-trace-base and @opentelemetry/exporter-trace-otlp-http dependencies",
        "Create lib/tracing.ts with tracer initialization",
        "Wrap key functions in spans: discoverSkills, scoreSkillsWithFuse, scoreSkillsWithTfIdf, scoreSkillFromRules",
        "Add attributes: query length, skill count, cache hit/miss, top score",
        "Export to local Jaeger/console when OTEL_EXPORTER_OTLP_ENDPOINT is set"
      ],
      "acceptance_criteria": [
        "[ ] With OTEL_EXPORTER_OTLP_ENDPOINT set, traces appear in Jaeger UI",
        "[ ] Spans show timing breakdown: discovery, fuzzy scoring, TF-IDF scoring, rules scoring",
        "[ ] Cache hits/misses visible as span attributes",
        "[ ] No performance regression when tracing disabled (default)"
      ],
      "test_plan": [
        "Unit test: Spans created with correct names and attributes",
        "Integration test: Traces export to console when configured",
        "Performance test: <5ms overhead when tracing enabled"
      ],
      "dependencies": [],
      "risk_mitigation": "Tracing disabled by default; only active when OTEL env var set",
      "experiment": "1-2 hour version: Add console.time/timeEnd calls for key functions without OpenTelemetry dependency",
      "success_metric": "Identify one performance bottleneck (>50% of latency) from trace data",
      "rollback_plan": "Remove @opentelemetry dependencies; tracing code is no-op without exporter"
    },
    {
      "id": "IMP-008",
      "title": "Implement AI-powered skill gap auto-generation",
      "category": "Moonshot",
      "type": "feature",
      "area": "backend",
      "owner_role": "Fullstack",
      "scores": {
        "impact": 5,
        "effort": 5,
        "expertise": 4,
        "risk": 3,
        "novelty": 5
      },
      "priority_score": 1.0,
      "targets": [
        "lib/skill-metrics.json",
        "evals/run-evals.ts"
      ],
      "search_tokens": ["gaps", "GAP_THRESHOLD", "recordGap", "checkGapNotification"],
      "implementation_steps": [
        "Create scripts/generate-skill-from-gap.ts using Claude API",
        "Analyze top gaps from skill-metrics.json: cluster related queries, identify common themes",
        "Generate SKILL.md content: frontmatter, description, when_to_use, initial content sections",
        "Run generated skill through garden.sh validation",
        "Create PR-ready branch with generated skill for human review",
        "Add eval test case for new skill automatically"
      ],
      "acceptance_criteria": [
        "[ ] Running `bun run scripts/generate-skill-from-gap.ts` creates valid skill from top gap",
        "[ ] Generated skill passes all frontmatter checks",
        "[ ] Generated skill appears in suggestions for original gap query",
        "[ ] Human review required before merge (PR workflow)"
      ],
      "test_plan": [
        "Unit test: Gap clustering produces sensible groupings",
        "Integration test: Generated skill is syntactically valid",
        "Human eval: Review 5 generated skills for quality and relevance"
      ],
      "dependencies": ["IMP-001"],
      "risk_mitigation": "Generated skills go to review branch, not main; human approval required; rollback is delete branch",
      "experiment": "1-2 hour version: Create script that formats top 5 gaps as prompts for manual Claude generation, validate output manually",
      "success_metric": "3 of 5 generated skills deemed 'useful' by human reviewer after 1 week of usage",
      "rollback_plan": "Delete generated skills and review branch; no impact on existing skills"
    }
  ],
  "epics": [
    {
      "id": "EPIC-01",
      "title": "Skill Analytics & Effectiveness",
      "improvement_ids": ["IMP-001", "IMP-007"]
    },
    {
      "id": "EPIC-02",
      "title": "Developer Experience & Tooling",
      "improvement_ids": ["IMP-002", "IMP-004"]
    },
    {
      "id": "EPIC-03",
      "title": "Performance & Architecture",
      "improvement_ids": ["IMP-003", "IMP-005"]
    },
    {
      "id": "EPIC-04",
      "title": "Intelligent Recommendations",
      "improvement_ids": ["IMP-006", "IMP-008"]
    }
  ],
  "recommended_sequence": ["IMP-001", "IMP-002", "IMP-003", "IMP-004", "IMP-007", "IMP-005", "IMP-006", "IMP-008"]
};

function getCategoryEmoji(category: string): string {
  switch (category) {
    case 'Conventional': return '📋';
    case 'Creative': return '💡';
    case 'Moonshot': return '🚀';
    default: return '📝';
  }
}

function getTypeEmoji(type: string): string {
  switch (type) {
    case 'observability': return '📊';
    case 'DX': return '🛠️';
    case 'perf': return '⚡';
    case 'refactor': return '🔧';
    case 'feature': return '✨';
    default: return '📝';
  }
}

function generateImprovementMarkdown(imp: Improvement, epics: Epic[], sequence: string[]): string {
  const epic = epics.find(e => e.improvement_ids.includes(imp.id));
  const sequenceIndex = sequence.indexOf(imp.id) + 1;

  const lines: string[] = [
    `# ${imp.id}: ${imp.title}`,
    '',
    `> ${getCategoryEmoji(imp.category)} **${imp.category}** | ${getTypeEmoji(imp.type)} ${imp.type} | 📍 ${imp.area} | 👤 ${imp.owner_role}`,
    '',
    '## Summary',
    '',
    `| Metric | Value |`,
    `|--------|-------|`,
    `| **Priority Score** | ${imp.priority_score.toFixed(2)} |`,
    `| **Impact** | ${imp.scores.impact}/5 |`,
    `| **Effort** | ${imp.scores.effort}/5 |`,
    `| **Expertise** | ${imp.scores.expertise}/5 |`,
    `| **Risk** | ${imp.scores.risk}/5 |`,
    `| **Novelty** | ${imp.scores.novelty}/5 |`,
    '',
  ];

  if (epic) {
    lines.push(`**Epic:** ${epic.id} - ${epic.title}`);
    lines.push('');
  }

  if (sequenceIndex > 0) {
    lines.push(`**Recommended Sequence:** #${sequenceIndex} of ${sequence.length}`);
    lines.push('');
  }

  lines.push('## Targets');
  lines.push('');
  for (const target of imp.targets) {
    lines.push(`- \`${target}\``);
  }
  lines.push('');

  lines.push('## Search Tokens');
  lines.push('');
  lines.push(`\`${imp.search_tokens.join('`, `')}\``);
  lines.push('');

  lines.push('## Implementation Steps');
  lines.push('');
  for (let i = 0; i < imp.implementation_steps.length; i++) {
    lines.push(`${i + 1}. ${imp.implementation_steps[i]}`);
  }
  lines.push('');

  lines.push('## Acceptance Criteria');
  lines.push('');
  for (const ac of imp.acceptance_criteria) {
    lines.push(ac);
  }
  lines.push('');

  lines.push('## Test Plan');
  lines.push('');
  for (const test of imp.test_plan) {
    lines.push(`- ${test}`);
  }
  lines.push('');

  if (imp.dependencies.length > 0) {
    lines.push('## Dependencies');
    lines.push('');
    for (const dep of imp.dependencies) {
      lines.push(`- ${dep}`);
    }
    lines.push('');
  }

  lines.push('## Risk Mitigation');
  lines.push('');
  lines.push(imp.risk_mitigation);
  lines.push('');

  // Creative/Moonshot specific fields
  if (imp.category === 'Creative' || imp.category === 'Moonshot') {
    lines.push('---');
    lines.push('');
    lines.push('## Experiment (1-2 hour version)');
    lines.push('');
    lines.push(imp.experiment || '_Not specified_');
    lines.push('');
    lines.push('## Success Metric');
    lines.push('');
    lines.push(imp.success_metric || '_Not specified_');
    lines.push('');
    lines.push('## Rollback Plan');
    lines.push('');
    lines.push(imp.rollback_plan || '_Not specified_');
    lines.push('');
  }

  return lines.join('\n');
}

function generateIndexMarkdown(data: PlanData): string {
  const lines: string[] = [
    '# PAI-Skills Productivity Improvement Plan',
    '',
    `> Generated: ${new Date().toISOString().split('T')[0]}`,
    '',
    '## Focus Summary',
    '',
    `**Purpose:** ${data.focus_summary.purpose}`,
    '',
    '### Key Flows',
    '',
  ];

  for (const flow of data.focus_summary.key_flows) {
    lines.push(`- ${flow}`);
  }
  lines.push('');

  lines.push('### Constraints');
  lines.push('');
  for (const constraint of data.focus_summary.constraints) {
    lines.push(`- ${constraint}`);
  }
  lines.push('');

  lines.push('### Risks & Unknowns');
  lines.push('');
  for (const risk of data.focus_summary.risks_or_unknowns) {
    lines.push(`- ⚠️ ${risk}`);
  }
  lines.push('');

  lines.push('## Improvements Overview');
  lines.push('');
  lines.push('| # | ID | Title | Category | Priority | Impact | Effort |');
  lines.push('|---|-----|-------|----------|----------|--------|--------|');

  const sortedImprovements = [...data.improvements].sort((a, b) => b.priority_score - a.priority_score);
  for (let i = 0; i < sortedImprovements.length; i++) {
    const imp = sortedImprovements[i];
    const emoji = getCategoryEmoji(imp.category);
    lines.push(`| ${i + 1} | [${imp.id}](./${imp.id}.md) | ${imp.title} | ${emoji} ${imp.category} | ${imp.priority_score.toFixed(2)} | ${imp.scores.impact}/5 | ${imp.scores.effort}/5 |`);
  }
  lines.push('');

  lines.push('## Epics');
  lines.push('');
  for (const epic of data.epics) {
    lines.push(`### ${epic.id}: ${epic.title}`);
    lines.push('');
    for (const impId of epic.improvement_ids) {
      const imp = data.improvements.find(i => i.id === impId);
      if (imp) {
        lines.push(`- [${imp.id}](./${imp.id}.md): ${imp.title}`);
      }
    }
    lines.push('');
  }

  lines.push('## Recommended Sequence');
  lines.push('');
  for (let i = 0; i < data.recommended_sequence.length; i++) {
    const impId = data.recommended_sequence[i];
    const imp = data.improvements.find(i => i.id === impId);
    if (imp) {
      lines.push(`${i + 1}. [${imp.id}](./${imp.id}.md): ${imp.title}`);
    }
  }
  lines.push('');

  lines.push('## Category Distribution');
  lines.push('');
  const categories = data.improvements.reduce((acc, imp) => {
    acc[imp.category] = (acc[imp.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  for (const [cat, count] of Object.entries(categories)) {
    lines.push(`- ${getCategoryEmoji(cat)} **${cat}:** ${count}`);
  }
  lines.push('');

  return lines.join('\n');
}

function main() {
  const args = process.argv.slice(2);
  let inputFile: string | null = null;
  let outputDir = join(__dirname, '..', 'docs', 'plans');

  // Parse arguments
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--input' && args[i + 1]) {
      inputFile = args[++i];
    } else if (args[i] === '--output' && args[i + 1]) {
      outputDir = args[++i];
    } else if (args[i] === '--help') {
      console.log(`
Usage: bun run scripts/generate-plan-docs.ts [options]

Options:
  --input <file>   Load plan data from JSON file (default: embedded)
  --output <dir>   Output directory (default: docs/plans)
  --help           Show this help message

Examples:
  bun run scripts/generate-plan-docs.ts
  bun run scripts/generate-plan-docs.ts --input improvements.json
  bun run scripts/generate-plan-docs.ts --output ./my-plans
`);
      process.exit(0);
    }
  }

  // Load data
  let data: PlanData;
  if (inputFile) {
    if (!existsSync(inputFile)) {
      console.error(`Error: Input file not found: ${inputFile}`);
      process.exit(1);
    }
    data = JSON.parse(readFileSync(inputFile, 'utf-8'));
    console.log(`📂 Loaded plan data from ${inputFile}`);
  } else {
    data = PLAN_DATA;
    console.log(`📂 Using embedded plan data`);
  }

  // Create output directory
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
    console.log(`📁 Created directory: ${outputDir}`);
  }

  // Generate index
  const indexPath = join(outputDir, 'README.md');
  writeFileSync(indexPath, generateIndexMarkdown(data));
  console.log(`✅ Generated: ${indexPath}`);

  // Generate individual improvement files
  for (const imp of data.improvements) {
    const filePath = join(outputDir, `${imp.id}.md`);
    writeFileSync(filePath, generateImprovementMarkdown(imp, data.epics, data.recommended_sequence));
    console.log(`✅ Generated: ${filePath}`);
  }

  console.log(`
📊 Summary:
   - Index: README.md
   - Improvements: ${data.improvements.length} files
   - Output: ${outputDir}
`);
}

main();

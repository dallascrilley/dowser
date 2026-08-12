# Split `analyze-prompt-skills.ts` Implementation Plan

> **For Codex:**  Implement this plan task-by-task.

**Goal:** Split the 1750+ line hook `hooks/prompt-submit/analyze-prompt-skills.ts` into small, testable modules without changing behavior.

**Architecture:** Create a `hooks/prompt-submit/skill-analyzer/` folder with focused modules (discovery, scoring, rules, metrics, formatting). Keep `hooks/prompt-submit/analyze-prompt-skills.ts` as a thin entrypoint (stdin/CLI parsing + calling a single orchestrator function). Preserve current process-lifetime caching by keeping caches module-scoped (same as today).

**Tech Stack:** TypeScript (ESM), Bun runtime, `bun:test`, Fuse.js, `natural` (TF‑IDF).

---

## Notes for zero-context engineers

- This repo does **not** use `pytest`. The test runner is `bun test` (see `package.json` and existing tests in `hooks/__tests__/`).
- The hook is executed by spawning `bun run hooks/prompt-submit/analyze-prompt-skills.ts` and reading JSON from stdin (existing integration tests do this).
- This is a refactor-only change: keep output JSON shape and scoring behavior stable. Use @skills/coding/refactoring-safely throughout.

## Target module map (end state)

- `hooks/prompt-submit/skill-analyzer/types.ts` — shared types + small runtime constants
- `hooks/prompt-submit/skill-analyzer/tokenize.ts` — tokenization + Levenshtein + “fuzzy” scoring
- `hooks/prompt-submit/skill-analyzer/fuse.ts` — Fuse instance + Fuse scoring
- `hooks/prompt-submit/skill-analyzer/tfidf.ts` — TF‑IDF instance + TF‑IDF scoring
- `hooks/prompt-submit/skill-analyzer/rules.ts` — load/compile rules + rules scoring
- `hooks/prompt-submit/skill-analyzer/discovery.ts` — frontmatter parsing + skill discovery + caching
- `hooks/prompt-submit/skill-analyzer/metrics.ts` — metrics persistence + gap tracking
- `hooks/prompt-submit/skill-analyzer/format.ts` — formatting suggestions output
- `hooks/prompt-submit/skill-analyzer/analyze.ts` — orchestrator (the “main” logic), imported by entrypoint

Each extraction should be **mechanical**: move code verbatim first, then (optionally) improve boundaries later.

---

### Task 1: Add Skill Analyzer Module Skeleton

**Files:**
- Create: `hooks/prompt-submit/skill-analyzer/types.ts`
- Test: `hooks/__tests__/skill-analyzer/types.test.ts`

**Step 1: Write the failing test**

```ts
// hooks/__tests__/skill-analyzer/types.test.ts
import { describe, test, expect } from 'bun:test';

// Fails until module exists
import { SKILL_SOURCE_TYPES } from '../../prompt-submit/skill-analyzer/types';

describe('skill-analyzer types', () => {
  test('exports SKILL_SOURCE_TYPES for runtime use', () => {
    expect(SKILL_SOURCE_TYPES).toEqual(['project', 'user', 'plugin']);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `bun test hooks/__tests__/skill-analyzer/types.test.ts`
Expected: module resolution error for `hooks/prompt-submit/skill-analyzer/types.ts`

**Step 3: Write minimal implementation**

```ts
// hooks/prompt-submit/skill-analyzer/types.ts
export const SKILL_SOURCE_TYPES = ['project', 'user', 'plugin'] as const;
export type SkillSourceType = (typeof SKILL_SOURCE_TYPES)[number];

export interface HookInput {
  session_id?: string;
  prompt?: string;
  userMessage?: string;
  transcript_path?: string;
  hook_event_name?: string;
}

export interface Skill {
  name: string;
  path: string;
  description: string;
  whenToUse: string;
  relativePath: string;
  folderName: string;
  sourceType: SkillSourceType;
}
```

**Step 4: Run test to verify it passes**

Run: `bun test hooks/__tests__/skill-analyzer/types.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/prompt-submit/skill-analyzer/types.ts hooks/__tests__/skill-analyzer/types.test.ts
git commit -m "refactor: add skill-analyzer types module"
```

---

### Task 2: Extract Tokenization + Fuzzy Scoring

**Files:**
- Create: `hooks/prompt-submit/skill-analyzer/tokenize.ts`
- Modify: `hooks/prompt-submit/analyze-prompt-skills.ts:1067-1320`
- Test: `hooks/__tests__/skill-analyzer/tokenize.test.ts`

**Step 1: Write the failing test**

```ts
// hooks/__tests__/skill-analyzer/tokenize.test.ts
import { describe, test, expect } from 'bun:test';
import { tokenize, levenshteinDistance, scoreFuzzyMatch } from '../../prompt-submit/skill-analyzer/tokenize';

describe('tokenize + fuzzy', () => {
  test('tokenize splits and lowercases', () => {
    expect(tokenize('Hello, WORLD!')).toEqual(['hello', 'world']);
  });

  test('levenshteinDistance basic cases', () => {
    expect(levenshteinDistance('kitten', 'sitting')).toBe(3);
    expect(levenshteinDistance('a', 'a')).toBe(0);
  });

  test('scoreFuzzyMatch maps distance to score', () => {
    expect(scoreFuzzyMatch(0, 2)).toBeGreaterThan(scoreFuzzyMatch(1, 2));
    expect(scoreFuzzyMatch(2, 2)).toBeGreaterThanOrEqual(0);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `bun test hooks/__tests__/skill-analyzer/tokenize.test.ts`
Expected: module resolution error for `hooks/prompt-submit/skill-analyzer/tokenize.ts`

**Step 3: Write minimal implementation**

```ts
// hooks/prompt-submit/skill-analyzer/tokenize.ts
// Mechanical extraction from hooks/prompt-submit/analyze-prompt-skills.ts:
// - isMetaSkillContext
// - expandTokens
// - tokenize
// - levenshteinDistance
// - scoreFuzzyMatch
// - tokenizeSkillName
// - scoreSkillRelevanceFuzzy

export function tokenize(text: string, keepSkillTokens: boolean = false): string[] {
  // NOTE: paste the existing implementation from analyze-prompt-skills.ts (lines ~1101-1126).
  return text
    .toLowerCase()
    .split(/[^a-z0-9_]+/g)
    .filter(Boolean)
    .flatMap((t) => (keepSkillTokens ? [t] : t.split('_').filter(Boolean)));
}

export function levenshteinDistance(a: string, b: string): number {
  // NOTE: paste the existing implementation from analyze-prompt-skills.ts (lines ~1128-1155).
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;
  const dp = Array.from({ length: a.length + 1 }, (_, i) => i);
  for (let j = 1; j <= b.length; j++) {
    let prev = dp[0];
    dp[0] = j;
    for (let i = 1; i <= a.length; i++) {
      const tmp = dp[i];
      dp[i] = Math.min(
        dp[i] + 1,
        dp[i - 1] + 1,
        prev + (a[i - 1] === b[j - 1] ? 0 : 1)
      );
      prev = tmp;
    }
  }
  return dp[a.length];
}

export function scoreFuzzyMatch(distance: number, maxDistance: number = 2): number {
  // NOTE: paste the existing implementation from analyze-prompt-skills.ts (line ~1157).
  if (distance > maxDistance) return 0;
  return Math.round(((maxDistance - distance) / maxDistance) * 15);
}
```

Also modify `hooks/prompt-submit/analyze-prompt-skills.ts` to import and use these functions, and delete the in-file copies:
- Replace the definitions at `hooks/prompt-submit/analyze-prompt-skills.ts:1067-1320` with imports:
  `import { tokenize, levenshteinDistance, scoreFuzzyMatch, /* etc */ } from './skill-analyzer/tokenize';`

**Step 4: Run test to verify it passes**

Run: `bun test hooks/__tests__/skill-analyzer/tokenize.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/prompt-submit/skill-analyzer/tokenize.ts hooks/prompt-submit/analyze-prompt-skills.ts hooks/__tests__/skill-analyzer/tokenize.test.ts
git commit -m "refactor: extract tokenize and fuzzy scoring"
```

---

### Task 3: Extract Fuse Scoring

**Files:**
- Create: `hooks/prompt-submit/skill-analyzer/fuse.ts`
- Modify: `hooks/prompt-submit/analyze-prompt-skills.ts:1333-1641`
- Test: `hooks/__tests__/skill-analyzer/fuse.test.ts`

**Step 1: Write the failing test**

```ts
// hooks/__tests__/skill-analyzer/fuse.test.ts
import { describe, test, expect } from 'bun:test';
import { scoreSkillsWithFuse } from '../../prompt-submit/skill-analyzer/fuse';
import type { Skill } from '../../prompt-submit/skill-analyzer/types';

describe('fuse scoring', () => {
  test('returns non-empty score map and includes skill names', () => {
    const skills: Skill[] = [
      {
        name: 'Optimizing Performance',
        path: '/tmp/optimizing-performance/SKILL.md',
        description: 'Improve performance',
        whenToUse: 'When app is slow',
        relativePath: 'skills/coding/optimizing-performance',
        folderName: 'optimizing-performance',
        sourceType: 'plugin',
      },
    ];

    const scores = scoreSkillsWithFuse(skills, 'performance');
    expect(scores.get('Optimizing Performance')?.fuseScore).toBeDefined();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `bun test hooks/__tests__/skill-analyzer/fuse.test.ts`
Expected: module resolution error for `hooks/prompt-submit/skill-analyzer/fuse.ts`

**Step 3: Write minimal implementation**

```ts
// hooks/prompt-submit/skill-analyzer/fuse.ts
import Fuse from 'fuse.js';
import { CONFIG } from '../../../lib/config';
import type { Skill } from './types';

const FUSE_OPTIONS: Fuse.IFuseOptions<Skill> = {
  keys: [
    { name: 'name', weight: CONFIG.WEIGHTS.fuseKeys.name },
    { name: 'folderName', weight: CONFIG.WEIGHTS.fuseKeys.folderName },
    { name: 'description', weight: CONFIG.WEIGHTS.fuseKeys.description },
    { name: 'whenToUse', weight: CONFIG.WEIGHTS.fuseKeys.whenToUse },
  ],
  threshold: CONFIG.FUZZY_THRESHOLD,
  distance: 100,
  minMatchCharLength: 2,
  includeScore: true,
  ignoreLocation: true,
  useExtendedSearch: true,
};

let fuseInstance: Fuse<Skill> | null = null;
let fuseSkillsHash: string = '';

function getFuseInstance(skills: Skill[]): Fuse<Skill> {
  const hash = skills.map((s) => s.name).sort().join('|');
  if (fuseInstance && fuseSkillsHash === hash) return fuseInstance;
  fuseInstance = new Fuse(skills, FUSE_OPTIONS);
  fuseSkillsHash = hash;
  return fuseInstance;
}

export function scoreSkillsWithFuse(
  skills: Skill[],
  query: string
): Map<string, { fuseScore: number; fuseMatch: Fuse.FuseResult<Skill> | null }> {
  const results = new Map<string, { fuseScore: number; fuseMatch: Fuse.FuseResult<Skill> | null }>();

  for (const skill of skills) results.set(skill.name, { fuseScore: 0, fuseMatch: null });
  if (!query || query.length < 2) return results;

  const fuse = getFuseInstance(skills);
  for (const result of fuse.search(query)) {
    const normalizedScore = Math.round((1 - (result.score || 0)) * 20);
    results.set(result.item.name, { fuseScore: normalizedScore, fuseMatch: result });
  }

  return results;
}
```

Then modify `hooks/prompt-submit/analyze-prompt-skills.ts`:
- Delete `FUSE_OPTIONS`, `fuseInstance`, `fuseSkillsHash`, `getFuseInstance`, `scoreSkillsWithFuse`
- Import `scoreSkillsWithFuse` from `./skill-analyzer/fuse`

**Step 4: Run test to verify it passes**

Run: `bun test hooks/__tests__/skill-analyzer/fuse.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/prompt-submit/skill-analyzer/fuse.ts hooks/prompt-submit/analyze-prompt-skills.ts hooks/__tests__/skill-analyzer/fuse.test.ts
git commit -m "refactor: extract fuse scoring"
```

---

### Task 4: Extract TF‑IDF Scoring

**Files:**
- Create: `hooks/prompt-submit/skill-analyzer/tfidf.ts`
- Modify: `hooks/prompt-submit/analyze-prompt-skills.ts:103-197`
- Test: `hooks/__tests__/skill-analyzer/tfidf.test.ts`

**Step 1: Write the failing test**

```ts
// hooks/__tests__/skill-analyzer/tfidf.test.ts
import { describe, test, expect } from 'bun:test';
import { scoreSkillsWithTfIdf } from '../../prompt-submit/skill-analyzer/tfidf';
import type { Skill } from '../../prompt-submit/skill-analyzer/types';

describe('tfidf scoring', () => {
  test('returns a Map with all skills as keys', () => {
    const skills: Skill[] = [
      {
        name: 'Optimizing Performance',
        path: '/tmp/optimizing-performance/SKILL.md',
        description: 'Improve performance',
        whenToUse: 'When app is slow',
        relativePath: 'skills/coding/optimizing-performance',
        folderName: 'optimizing-performance',
        sourceType: 'plugin',
      },
      {
        name: 'Writing Tests',
        path: '/tmp/writing-tests/SKILL.md',
        description: 'Testing guidance',
        whenToUse: 'When adding tests',
        relativePath: 'skills/coding/testing',
        folderName: 'writing-tests',
        sourceType: 'plugin',
      },
    ];
    const scores = scoreSkillsWithTfIdf(skills, 'performance');
    expect(scores.size).toBe(2);
    expect(scores.has('Optimizing Performance')).toBe(true);
    expect(scores.has('Writing Tests')).toBe(true);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `bun test hooks/__tests__/skill-analyzer/tfidf.test.ts`
Expected: module resolution error for `hooks/prompt-submit/skill-analyzer/tfidf.ts`

**Step 3: Write minimal implementation**

```ts
// hooks/prompt-submit/skill-analyzer/tfidf.ts
import { TfIdf } from 'natural';
import type { Skill } from './types';

let tfidfInstance: TfIdf | null = null;
let tfidfSkillsHash: string | null = null;

const TFIDF_ENABLED = process.env.SKILL_ANALYZER_TFIDF !== '0';

function getTfIdfInstance(skills: Skill[]): TfIdf {
  const currentHash = skills.map((s) => s.name).sort().join('|');
  if (tfidfInstance && tfidfSkillsHash === currentHash) return tfidfInstance;

  const tfidf = new TfIdf();
  for (const skill of skills) {
    const doc = `${skill.name} ${skill.description} ${skill.whenToUse}`.toLowerCase();
    tfidf.addDocument(doc);
  }
  tfidfInstance = tfidf;
  tfidfSkillsHash = currentHash;
  return tfidf;
}

export function scoreSkillsWithTfIdf(skills: Skill[], query: string): Map<string, number> {
  const results = new Map<string, number>();
  for (const skill of skills) results.set(skill.name, 0);
  if (!TFIDF_ENABLED) return results;

  const tfidf = getTfIdfInstance(skills);
  const queryLower = query.toLowerCase();

  let maxScore = 0;
  const rawScores: number[] = [];
  tfidf.tfidfs(queryLower, (i: number, measure: number) => {
    rawScores[i] = measure;
    if (measure > maxScore) maxScore = measure;
  });

  for (let i = 0; i < skills.length; i++) {
    const rawScore = rawScores[i] || 0;
    const normalizedScore = maxScore > 0 ? Math.round((rawScore / maxScore) * 25) : 0;
    results.set(skills[i].name, normalizedScore);
  }

  return results;
}
```

Then modify `hooks/prompt-submit/analyze-prompt-skills.ts`:
- Delete the TF‑IDF cache + functions (`getTfIdfInstance`, `scoreSkillsWithTfIdf`)
- Import `scoreSkillsWithTfIdf` from `./skill-analyzer/tfidf`

**Step 4: Run test to verify it passes**

Run: `bun test hooks/__tests__/skill-analyzer/tfidf.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/prompt-submit/skill-analyzer/tfidf.ts hooks/prompt-submit/analyze-prompt-skills.ts hooks/__tests__/skill-analyzer/tfidf.test.ts
git commit -m "refactor: extract tfidf scoring"
```

---

### Task 5: Extract Hybrid Scoring Orchestrator

**Files:**
- Create: `hooks/prompt-submit/skill-analyzer/hybrid.ts`
- Modify: `hooks/prompt-submit/analyze-prompt-skills.ts:1398-1453`
- Test: `hooks/__tests__/skill-analyzer/hybrid.test.ts`

**Step 1: Write the failing test**

```ts
// hooks/__tests__/skill-analyzer/hybrid.test.ts
import { describe, test, expect } from 'bun:test';
import { scoreSkillRelevanceHybrid } from '../../prompt-submit/skill-analyzer/hybrid';
import type { Skill } from '../../prompt-submit/skill-analyzer/types';

describe('hybrid scoring', () => {
  test('returns 0 when nothing matches', () => {
    const skill: Skill = {
      name: 'Some Skill',
      path: '/tmp/some-skill/SKILL.md',
      description: 'nope',
      whenToUse: 'nope',
      relativePath: 'skills/x',
      folderName: 'some-skill',
      sourceType: 'plugin',
    };
    const out = scoreSkillRelevanceHybrid(skill, 'zzz', null, new Map(), new Map());
    expect(out.score).toBe(0);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `bun test hooks/__tests__/skill-analyzer/hybrid.test.ts`
Expected: module resolution error for `hooks/prompt-submit/skill-analyzer/hybrid.ts`

**Step 3: Write minimal implementation**

```ts
// hooks/prompt-submit/skill-analyzer/hybrid.ts
import type Fuse from 'fuse.js';
import { CONFIG } from '../../../lib/config';
import type { Skill } from './types';
import type { SkillRules } from './rules';
import { scoreSkillFromRules } from './rules';
import { scoreSkillRelevanceFuzzy } from './tokenize';

export function scoreSkillRelevanceHybrid(
  skill: Skill,
  prompt: string,
  rules: SkillRules | null,
  fuseScores: Map<string, { fuseScore: number; fuseMatch: Fuse.FuseResult<Skill> | null }>,
  tfidfScores: Map<string, number>
): { score: number; source: 'rules' | 'fuzzy' | 'fuse' | 'tfidf' | 'hybrid' } {
  const rulesScore = scoreSkillFromRules(skill, prompt, rules);
  const fuzzyScore = scoreSkillRelevanceFuzzy(skill, prompt);
  const fuseData = fuseScores.get(skill.name) || { fuseScore: 0, fuseMatch: null };
  const tfidfScore = tfidfScores.get(skill.name) || 0;

  if (rulesScore > 0) {
    const hybridScore =
      rulesScore +
      Math.floor(fuzzyScore * CONFIG.WEIGHTS.hybridBonuses.whenRulesMatch.fuzzy) +
      Math.floor(fuseData.fuseScore * CONFIG.WEIGHTS.hybridBonuses.whenRulesMatch.fuse) +
      Math.floor(tfidfScore * CONFIG.WEIGHTS.hybridBonuses.whenRulesMatch.tfidf);
    return {
      score: hybridScore,
      source: fuzzyScore > 0 || fuseData.fuseScore > 0 || tfidfScore > 0 ? 'hybrid' : 'rules',
    };
  }

  const scores = [
    { value: fuzzyScore, name: 'fuzzy' as const },
    { value: fuseData.fuseScore, name: 'fuse' as const },
    { value: tfidfScore, name: 'tfidf' as const },
  ].sort((a, b) => b.value - a.value);

  const primary = scores[0];
  const secondary = scores[1];
  const tertiary = scores[2];

  if (primary.value === 0) return { score: 0, source: 'fuzzy' };

  const combinedScore =
    primary.value +
    Math.floor(secondary.value * CONFIG.WEIGHTS.hybridBonuses.whenNoRules.secondary) +
    Math.floor(tertiary.value * CONFIG.WEIGHTS.hybridBonuses.whenNoRules.tertiary);

  const source = secondary.value > 0 ? 'hybrid' : primary.name;
  return { score: combinedScore, source };
}
```

Then modify `hooks/prompt-submit/analyze-prompt-skills.ts`:
- Delete in-file `scoreSkillRelevanceHybrid`
- Import it from `./skill-analyzer/hybrid`

**Step 4: Run test to verify it passes**

Run: `bun test hooks/__tests__/skill-analyzer/hybrid.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/prompt-submit/skill-analyzer/hybrid.ts hooks/prompt-submit/analyze-prompt-skills.ts hooks/__tests__/skill-analyzer/hybrid.test.ts
git commit -m "refactor: extract hybrid scoring"
```

---

### Task 6: Extract Rules Loading + Rules Scoring

**Files:**
- Create: `hooks/prompt-submit/skill-analyzer/rules.ts`
- Modify: `hooks/prompt-submit/analyze-prompt-skills.ts:216-346,613-669`
- Test: `hooks/__tests__/skill-analyzer/rules.test.ts`

**Step 1: Write the failing test**

```ts
// hooks/__tests__/skill-analyzer/rules.test.ts
import { describe, test, expect } from 'bun:test';
import { scoreSkillFromRules, type SkillRules } from '../../prompt-submit/skill-analyzer/rules';
import type { Skill } from '../../prompt-submit/skill-analyzer/types';

describe('rules scoring', () => {
  test('returns > 0 when keyword matches', () => {
    const skill: Skill = {
      name: 'Optimizing Performance',
      path: '/tmp/x',
      description: 'perf stuff',
      whenToUse: 'when optimizing',
      relativePath: 'skills/coding/optimizing-performance',
      folderName: 'optimizing-performance',
      sourceType: 'plugin',
    };

    const rules: SkillRules = {
      skills: {
        'Optimizing Performance': {
          promptTriggers: { keywords: ['performance'] },
        },
      },
    };

    expect(scoreSkillFromRules(skill, 'make it faster', rules)).toBeGreaterThan(0);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `bun test hooks/__tests__/skill-analyzer/rules.test.ts`
Expected: module resolution error for `hooks/prompt-submit/skill-analyzer/rules.ts`

**Step 3: Write minimal implementation**

```ts
// hooks/prompt-submit/skill-analyzer/rules.ts
import fs from 'fs';
import path from 'path';
import type { Skill } from './types';

export interface SkillRule {
  type?: 'domain' | 'guardrail';
  enforcement?: 'suggest' | 'block' | 'warn';
  priority?: 'critical' | 'high' | 'medium' | 'low';
  description?: string;
  promptTriggers?: {
    keywords?: string[];
    intentPatterns?: string[];
    compiledIntentRegexes?: RegExp[];
  };
  fileTriggers?: {
    pathPatterns?: string[];
    pathExclusions?: string[];
    contentPatterns?: string[];
  };
  blockMessage?: string;
  skipConditions?: {
    sessionSkillUsed?: boolean;
    fileMarkers?: string[];
    envOverride?: string;
  };
  isPluginRule?: boolean;
}

export interface SkillRules {
  version?: string;
  description?: string;
  skills?: Record<string, SkillRule>;
  globalConfig?: Record<string, unknown>;
  [key: string]: any;
}

interface SkillRulesCacheEntry {
  rules: SkillRules | null;
  mtime: number;
}

const rulesCache = new Map<string, SkillRulesCacheEntry>();

function compileIntentPatterns(patterns?: string[]): RegExp[] {
  if (!patterns?.length) return [];
  const compiled: RegExp[] = [];
  for (const pattern of patterns) {
    try {
      compiled.push(new RegExp(pattern, 'i'));
    } catch (error) {
      console.error(`⚠️  Invalid regex pattern in skill-rules.json: "${pattern}"`, error);
    }
  }
  return compiled;
}

export function loadSkillRules(skillsRoot: string, isPluginContext: boolean): SkillRules | null {
  const rulesPath = path.join(skillsRoot, 'skill-rules.json');
  if (!fs.existsSync(rulesPath)) return null;

  try {
    const stat = fs.statSync(rulesPath);
    const cached = rulesCache.get(rulesPath);
    if (cached && cached.mtime === stat.mtimeMs) return cached.rules;

    const content = fs.readFileSync(rulesPath, 'utf-8');
    const rules = JSON.parse(content) as SkillRules;

    if (rules.skills) {
      for (const [name, rule] of Object.entries(rules.skills)) {
        if (rule.promptTriggers?.intentPatterns) {
          rule.promptTriggers.compiledIntentRegexes = compileIntentPatterns(rule.promptTriggers.intentPatterns);
        }
        const hasPluginPath = rule.fileTriggers?.pathPatterns?.some((pattern) =>
          pattern.includes('/.claude/plugins/cache/')
        );
        rule.isPluginRule = Boolean(hasPluginPath);
        if (!isPluginContext && rule.isPluginRule) delete rules.skills[name];
      }
    }

    rulesCache.set(rulesPath, { rules, mtime: stat.mtimeMs });
    return rules;
  } catch (error) {
    console.error(`⚠️  Failed to load skill-rules.json from ${rulesPath}:`, error);
    return null;
  }
}

export function scoreSkillFromRules(skill: Skill, prompt: string, rules: SkillRules | null): number {
  // NOTE: paste existing logic from analyze-prompt-skills.ts (lines ~613-669) to avoid behavior drift.
  const rule = rules?.skills?.[skill.name];
  if (!rule) return 0;

  const promptLower = prompt.toLowerCase();
  const keywords = rule.promptTriggers?.keywords || [];
  let score = 0;
  for (const kw of keywords) {
    if (promptLower.includes(kw.toLowerCase())) score += 10;
  }
  return score;
}
```

Then modify `hooks/prompt-submit/analyze-prompt-skills.ts`:
- Remove rule interfaces and helpers (in-file `SkillRule`, `SkillRules`, `compileIntentPatterns`, `loadSkillRules`, `scoreSkillFromRules`)
- Compute `isPluginContext` (currently `IS_PLUGIN_CONTEXT` at ~199) in entrypoint and pass into `loadSkillRules(...)`
- Update imports: `import { loadSkillRules, scoreSkillFromRules, type SkillRules } from './skill-analyzer/rules';`

**Step 4: Run test to verify it passes**

Run: `bun test hooks/__tests__/skill-analyzer/rules.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/prompt-submit/skill-analyzer/rules.ts hooks/prompt-submit/analyze-prompt-skills.ts hooks/__tests__/skill-analyzer/rules.test.ts
git commit -m "refactor: extract rules loader and scoring"
```

---

### Task 7: Extract Skill Discovery (Frontmatter + Caching)

**Files:**
- Create: `hooks/prompt-submit/skill-analyzer/discovery.ts`
- Modify: `hooks/prompt-submit/analyze-prompt-skills.ts:672-1040`
- Test: `hooks/__tests__/skill-analyzer/discovery.test.ts`

**Step 1: Write the failing test**

```ts
// hooks/__tests__/skill-analyzer/discovery.test.ts
import { describe, test, expect, beforeEach, afterEach } from 'bun:test';
import { mkdtempSync, rmSync, mkdirSync, writeFileSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { discoverSkillsCached } from '../../prompt-submit/skill-analyzer/discovery';

describe('skill discovery', () => {
  let root = '';

  beforeEach(() => {
    root = mkdtempSync(join(tmpdir(), 'discovery-test-'));
  });

  afterEach(() => {
    rmSync(root, { recursive: true, force: true });
  });

  test('discovers a skill from SKILL.md', async () => {
    const skillDir = join(root, 'skills', 'coding', 'my-skill');
    mkdirSync(skillDir, { recursive: true });
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      ['---', 'name: My Skill', 'description: Hello', 'when_to_use: Use it', '---', '', '# Body'].join('\n')
    );

    const skills = await discoverSkillsCached(join(root, 'skills'), 'project');
    expect(skills.some((s) => s.folderName === 'my-skill')).toBe(true);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `bun test hooks/__tests__/skill-analyzer/discovery.test.ts`
Expected: module resolution error for `hooks/prompt-submit/skill-analyzer/discovery.ts`

**Step 3: Write minimal implementation**

```ts
// hooks/prompt-submit/skill-analyzer/discovery.ts
import { glob } from 'glob';
import matter from 'gray-matter';
import fs from 'fs';
import path from 'path';
import type { Skill, SkillSourceType } from './types';

interface CacheEntry {
  skills: Skill[];
  dirMtime: number;
  fileStats: { maxMtime: number; count: number };
}

const skillCache = new Map<string, CacheEntry>();

function normalizeMultilineString(str: string | undefined): string {
  return (str || '').replace(/\r/g, '').split('\n').map((l) => l.trim()).filter(Boolean).join(' ');
}

function parseFrontMatter(
  content: string,
  defaultName: string
): { name: string; description: string; whenToUse: string } {
  try {
    const parsed = matter(content);
    const data = parsed.data as Record<string, unknown>;
    return {
      name: (data.name as string) || defaultName,
      description: normalizeMultilineString(data.description as string) || '',
      whenToUse: normalizeMultilineString((data.when_to_use as string) || (data.whenToUse as string)) || '',
    };
  } catch {
    return { name: defaultName, description: '', whenToUse: '' };
  }
}

async function discoverSkills(root: string, sourceType: SkillSourceType): Promise<Skill[]> {
  const pattern = path.join(root, '**/SKILL.md').replace(/\\/g, '/');
  const files = await glob(pattern, { nodir: true });
  const skills: Skill[] = [];

  for (const file of files) {
    const folderName = path.basename(path.dirname(file));
    const content = fs.readFileSync(file, 'utf-8');
    const { name, description, whenToUse } = parseFrontMatter(content, folderName);
    skills.push({
      name,
      path: file,
      description,
      whenToUse,
      relativePath: path.relative(root, path.dirname(file)),
      folderName,
      sourceType,
    });
  }

  return skills;
}

function getDirectoryMtime(root: string): number {
  try {
    return fs.statSync(root).mtimeMs;
  } catch {
    return 0;
  }
}

async function getSkillFileStats(root: string): Promise<{ maxMtime: number; count: number }> {
  const pattern = path.join(root, '**/SKILL.md').replace(/\\/g, '/');
  const files = await glob(pattern, { nodir: true });
  let maxMtime = 0;
  for (const file of files) {
    try {
      const mtime = fs.statSync(file).mtimeMs;
      if (mtime > maxMtime) maxMtime = mtime;
    } catch {
      // ignore
    }
  }
  return { maxMtime, count: files.length };
}

export async function discoverSkillsCached(root: string, sourceType: SkillSourceType): Promise<Skill[]> {
  const dirMtime = getDirectoryMtime(root);
  const cached = skillCache.get(root);
  if (cached && cached.dirMtime === dirMtime) return cached.skills;

  const fileStats = await getSkillFileStats(root);
  if (cached && cached.fileStats.maxMtime === fileStats.maxMtime && cached.fileStats.count === fileStats.count) {
    cached.dirMtime = dirMtime;
    return cached.skills;
  }

  const skills = await discoverSkills(root, sourceType);
  skillCache.set(root, { skills, dirMtime, fileStats });
  return skills;
}
```

Then modify `hooks/prompt-submit/analyze-prompt-skills.ts`:
- Remove in-file discovery helpers and import `discoverSkillsCached` from `./skill-analyzer/discovery`
- Ensure `sourceType` usage remains identical

**Step 4: Run test to verify it passes**

Run: `bun test hooks/__tests__/skill-analyzer/discovery.test.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add hooks/prompt-submit/skill-analyzer/discovery.ts hooks/prompt-submit/analyze-prompt-skills.ts hooks/__tests__/skill-analyzer/discovery.test.ts
git commit -m "refactor: extract skill discovery"
```

---

### Task 8: Final Slimming + Regression Verification

**Files:**
- Modify: `hooks/prompt-submit/analyze-prompt-skills.ts:1-1757`
- Test: `hooks/__tests__/analyze-prompt-skills.test.ts`

**Step 1: Write the failing test**

```ts
// Add to hooks/__tests__/analyze-prompt-skills.test.ts
// This test fails until the refactor still preserves key output fields.
import { describe, test, expect } from 'bun:test';
import { join } from 'path';

describe('analyze-prompt-skills hook (refactor regression)', () => {
  test('still outputs hookSpecificOutput.additionalContext string', () => {
    const hookPath = join(import.meta.dir, '../prompt-submit/analyze-prompt-skills.ts');
    const input = JSON.stringify({ userMessage: 'testing', session_id: 's' });
    const result = Bun.spawnSync({
      cmd: ['bun', 'run', hookPath],
      stdin: Buffer.from(input),
      env: { ...process.env, CLAUDE_PROJECT_DIR: process.cwd() },
    });
    expect(result.exitCode).toBe(0);
    const payload = JSON.parse(result.stdout.toString() || '{}');
    expect(typeof payload?.hookSpecificOutput?.additionalContext).toBe('string');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `bun test hooks/__tests__/analyze-prompt-skills.test.ts`
Expected: If refactor broke output, this fails with an assertion error on `additionalContext`.

**Step 3: Write minimal implementation**

Perform the remaining extractions (metrics + formatting) and then:
- Ensure `hooks/prompt-submit/analyze-prompt-skills.ts` is primarily:
  - stdin read + JSON parse
  - argument parsing (`--record-activation`, `--record-search`, `--show-metrics`, etc.)
  - calling a single orchestrator (e.g., `analyzeUserPrompt(...)`) for the “normal hook mode”
- Keep output JSON fields unchanged (existing tests are the contract).

**Step 4: Run test to verify it passes**

Run: `bun test`
Expected: PASS (some suites are intentionally skipped on Bun due to `better-sqlite3`)

**Step 5: Commit**

```bash
git add hooks/prompt-submit/analyze-prompt-skills.ts hooks/__tests__/analyze-prompt-skills.test.ts hooks/prompt-submit/skill-analyzer
git commit -m "refactor: split analyze-prompt-skills into modules"
```

---

## Final verification checklist (must do before PR)

- Run: `./scripts/garden.sh`
  - Expected: exits `0` (it may still print repo-wide ❌ issues unrelated to this refactor).
- Run: `bun test`
  - Expected: 0 failures.
- Run: `git status`
  - Expected: clean.

---

## Handoff

Execute this plan step-by-step using `/prompts:execute-plan`.


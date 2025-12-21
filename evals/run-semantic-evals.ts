#!/usr/bin/env bun
/**
 * Semantic Search Evaluation Runner
 *
 * Compares skill search results with and without semantic search enabled,
 * using a hermetic skills corpus by default (PAI skills only) for stability.
 */

import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

const EVALS_DIR = __dirname;
const TEST_CASES_FILE = path.join(EVALS_DIR, 'test-semantic.json');
const REPO_ROOT = path.join(__dirname, '..');
const ANALYZER_SCRIPT = path.join(REPO_ROOT, 'hooks', 'prompt-submit', 'analyze-prompt-skills.ts');
const REPO_SKILLS_DIR = path.join(REPO_ROOT, 'skills');

interface TestCase {
  id: string;
  category: string;
  query: string;
  expected: string[];
  not_expected?: string[];
  notes?: string;
}

interface SearchResult {
  name: string;
  score: number;
  source?: string;
  skillPath?: string;
  folderSlug?: string;
}

type EvalMode = 'baseline' | 'semantic';

function parseArgs() {
  const args = process.argv.slice(2);
  const get = (flag: string): string | undefined => {
    const idx = args.indexOf(flag);
    if (idx === -1) return undefined;
    return args[idx + 1];
  };

  return {
    json: args.includes('--json'),
    verbose: args.includes('--verbose') || args.includes('-v'),
    noHermetic: args.includes('--no-hermetic'),
    category: get('--category'),
    k: Number.parseInt(get('--k') || '10', 10),
  };
}

function normalizeSkillName(name: string): string {
  return name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
}

function matchesExpected(actual: string, expected: string): boolean {
  const normActual = normalizeSkillName(actual);
  const normExpected = normalizeSkillName(expected);
  return normActual === normExpected || normActual.includes(normExpected) || normExpected.includes(normActual);
}

function getResultKey(result: SearchResult): string {
  return result.folderSlug || result.name;
}

function firstRelevantRank(results: SearchResult[], expected: string[]): number | null {
  for (let i = 0; i < results.length; i++) {
    const actual = getResultKey(results[i]);
    if (expected.some(e => matchesExpected(actual, e))) return i + 1;
  }
  return null;
}

function hitAtK(results: SearchResult[], expected: string[], k: number): boolean {
  if (expected.length === 0) return true;
  const topK = results.slice(0, k);
  return topK.some(r => expected.some(e => matchesExpected(getResultKey(r), e)));
}

function hasNegativeAtK(results: SearchResult[], notExpected: string[], k: number): boolean {
  if (!notExpected || notExpected.length === 0) return false;
  const topK = results.slice(0, k);
  return topK.some(r => notExpected.some(ne => matchesExpected(getResultKey(r), ne)));
}

function mrrAtK(results: SearchResult[], expected: string[], k: number): number {
  if (expected.length === 0) return 1;
  const topK = results.slice(0, k);
  for (let i = 0; i < topK.length; i++) {
    if (expected.some(e => matchesExpected(getResultKey(topK[i]), e))) {
      return 1 / (i + 1);
    }
  }
  return 0;
}

function ndcgAtK(results: SearchResult[], expected: string[], k: number): number {
  if (expected.length === 0) return 1;
  const topK = results.slice(0, k);

  const dcg = topK.reduce((sum, r, i) => {
    const rel = expected.some(e => matchesExpected(getResultKey(r), e)) ? 1 : 0;
    if (rel === 0) return sum;
    return sum + 1 / Math.log2(i + 2);
  }, 0);

  const idealHits = Math.min(k, expected.length);
  const idcg = Array.from({ length: idealHits }).reduce((sum, _, i) => sum + 1 / Math.log2(i + 2), 0);

  return idcg === 0 ? 0 : dcg / idcg;
}

function createHermeticEnv(): { env: NodeJS.ProcessEnv; cleanup: () => void } {
  const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'pai-skills-evals-'));
  const hermeticHome = path.join(tmpRoot, 'home');
  const hermeticPai = path.join(tmpRoot, 'PAI');
  const hermeticProject = path.join(tmpRoot, 'project');

  fs.mkdirSync(hermeticHome, { recursive: true });
  fs.mkdirSync(hermeticPai, { recursive: true });
  fs.mkdirSync(hermeticProject, { recursive: true });

  const paiPluginSkillsDir = path.join(hermeticPai, '.claude', 'plugins', 'pai-skills', 'skills');
  fs.mkdirSync(path.dirname(paiPluginSkillsDir), { recursive: true });

  try {
    fs.symlinkSync(REPO_SKILLS_DIR, paiPluginSkillsDir, 'dir');
  } catch {
    // If the symlink already exists or fails, fall back to copying a pointer directory.
    // (Symlinks can be restricted in some environments.)
    fs.rmSync(paiPluginSkillsDir, { recursive: true, force: true });
    fs.mkdirSync(paiPluginSkillsDir, { recursive: true });
    fs.cpSync(REPO_SKILLS_DIR, paiPluginSkillsDir, { recursive: true });
  }

  const semanticCacheDir = path.join(os.tmpdir(), 'pai-skills-semantic-cache');
  fs.mkdirSync(semanticCacheDir, { recursive: true });

  const cleanup = () => {
    fs.rmSync(tmpRoot, { recursive: true, force: true });
  };

  const env: NodeJS.ProcessEnv = {
    ...process.env,
    HOME: hermeticHome,
    USERPROFILE: hermeticHome,
    PAI_DIR: hermeticPai,
    CLAUDE_PROJECT_DIR: hermeticProject,
    SKILL_ANALYZER_SEMANTIC_CACHE_DIR: semanticCacheDir,
  };

  return { env, cleanup };
}

async function runAnalyzer(
  query: string,
  semanticEnabled: boolean,
  baseEnv: NodeJS.ProcessEnv,
  limit: number
): Promise<SearchResult[]> {
  return new Promise((resolve, reject) => {
    const proc = spawn('bun', ['run', ANALYZER_SCRIPT], {
      env: { 
        ...baseEnv,
        SKILL_ANALYZER_SHOW_SCORES: '1',
        SKILL_ANALYZER_SEMANTIC: semanticEnabled ? '1' : '0',
        SKILL_ANALYZER_LIMIT: String(limit),
      },
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => { stdout += data.toString(); });
    proc.stderr.on('data', (data) => { stderr += data.toString(); });

    proc.stdin.write(JSON.stringify({ userMessage: query }));
    proc.stdin.end();

    proc.on('close', (code) => {
      if (code !== 0) {
        console.error(`Analyzer failed for "${query}": ${stderr}`);
        resolve([]);
        return;
      }

      const results: SearchResult[] = [];
      const lines = stderr.split('\n');

      for (const line of lines) {
        // Match: "  • skill-name [score: 35, 🔍 fuzzy]: description"
        // Updated format might include semantic icon 🧠
        const match = line.match(/^\s*•\s+([^[\]]+)\s+\[score:\s*(\d+)(?:,\s*([^\]]+))?\]/);
        if (match) {
          results.push({
            name: match[1].trim(),
            score: parseInt(match[2], 10),
            source: match[3] ? match[3].trim() : undefined
          });
          continue;
        }

        const pathMatch = line.match(/^\s*Path:\s*(.+)\s*$/);
        if (pathMatch && results.length > 0) {
          const last = results[results.length - 1];
          if (!last.skillPath) {
            last.skillPath = pathMatch[1].trim();
            // Skill paths typically end with ".../<folder>/SKILL.md"
            last.folderSlug = path.basename(path.dirname(last.skillPath));
          }
        }
      }
      resolve(results);
    });
  });
}

async function main() {
  const opts = parseArgs();
  const k = Number.isFinite(opts.k) ? Math.max(1, Math.min(20, opts.k)) : 10;
  const limit = Math.max(10, k);

  const testCases = JSON.parse(fs.readFileSync(TEST_CASES_FILE, 'utf-8')).test_cases as TestCase[];
  const filtered = opts.category
    ? testCases.filter(tc => tc.category.toLowerCase().includes(opts.category!.toLowerCase()))
    : testCases;

  const hermetic = opts.noHermetic ? null : createHermeticEnv();
  const baseEnv = hermetic?.env ?? process.env;
  
  console.log(`\n🧠 Running Semantic Search Comparison on ${filtered.length} cases\n`);
  console.log(`Analyzer Script: ${ANALYZER_SCRIPT}`);
  console.log(`Mode: ${opts.noHermetic ? 'non-hermetic (uses current ~/.claude roots)' : 'hermetic (PAI skills only)'}`);
  console.log(`Top-K: ${k} (requested), limit=${limit} (queried)`);

  console.log(`\n${'Query'.padEnd(34)} | ${'Base'.padEnd(6)} | ${'Sem'.padEnd(6)} | ${'Δ'.padEnd(10)} | Notes`);
  console.log('-'.repeat(80));

  let improvedCount = 0;
  let regressedCount = 0;
  let sameCount = 0;
  let semanticNegativeViolations = 0;

  let baseHit3 = 0;
  let semHit3 = 0;
  let baseMrr = 0;
  let semMrr = 0;
  let baseNdcg = 0;
  let semNdcg = 0;

  const detailed: Array<any> = [];

  for (const tc of filtered) {
    const baselineResults = await runAnalyzer(tc.query, false, baseEnv, limit);
    const semanticResults = await runAnalyzer(tc.query, true, baseEnv, limit);

    const expected = tc.expected || [];
    const notExpected = tc.not_expected || [];

    const baselineRank = firstRelevantRank(baselineResults, expected);
    const semanticRank = firstRelevantRank(semanticResults, expected);

    const baselineStr = baselineRank ? `#${baselineRank}` : '—';
    const semanticStr = semanticRank ? `#${semanticRank}` : '—';

    const baseHitAt3 = hitAtK(baselineResults, expected, 3);
    const semHitAt3 = hitAtK(semanticResults, expected, 3);
    const baseMrrAtK = mrrAtK(baselineResults, expected, k);
    const semMrrAtK = mrrAtK(semanticResults, expected, k);
    const baseNdcgAtK = ndcgAtK(baselineResults, expected, k);
    const semNdcgAtK = ndcgAtK(semanticResults, expected, k);

    let diff = '';
    const semanticHasNeg = hasNegativeAtK(semanticResults, notExpected, 3);
    if (semanticHasNeg) {
      semanticNegativeViolations++;
    }

    if (semanticHasNeg) {
      diff = '⚠️ neg@3';
      regressedCount++;
    } else if (baselineRank === semanticRank) {
      sameCount++;
      diff = '=';
    } else if (semanticRank !== null && (baselineRank === null || semanticRank < baselineRank)) {
      improvedCount++;
      diff = '✅ win';
    } else if (baselineRank !== null && (semanticRank === null || semanticRank > baselineRank)) {
      regressedCount++;
      diff = '⚠️ loss';
    } else {
      sameCount++;
      diff = '=';
    }

    baseHit3 += baseHitAt3 ? 1 : 0;
    semHit3 += semHitAt3 ? 1 : 0;
    baseMrr += baseMrrAtK;
    semMrr += semMrrAtK;
    baseNdcg += baseNdcgAtK;
    semNdcg += semNdcgAtK;

    const queryTrunc = tc.query.length > 32 ? tc.query.slice(0, 29) + '...' : tc.query;
    if (opts.verbose || diff !== '=') {
      console.log(`${queryTrunc.padEnd(34)} | ${baselineStr.padEnd(6)} | ${semanticStr.padEnd(6)} | ${diff.padEnd(10)} | ${tc.notes || ''}`);
    } else {
      process.stdout.write('.');
    }

    detailed.push({
      id: tc.id,
      category: tc.category,
      query: tc.query,
      expected,
      not_expected: notExpected,
      baseline: {
        rank: baselineRank,
        hit_at_3: baseHitAt3,
        mrr_at_k: baseMrrAtK,
        ndcg_at_k: baseNdcgAtK,
        top: baselineResults.slice(0, Math.min(5, baselineResults.length)).map(r => ({
          key: getResultKey(r),
          score: r.score,
          source: r.source,
        })),
      },
      semantic: {
        rank: semanticRank,
        hit_at_3: semHitAt3,
        mrr_at_k: semMrrAtK,
        ndcg_at_k: semNdcgAtK,
        negative_at_3: semanticHasNeg,
        top: semanticResults.slice(0, Math.min(5, semanticResults.length)).map(r => ({
          key: getResultKey(r),
          score: r.score,
          source: r.source,
        })),
      },
      outcome: diff,
    });
  }

  if (!opts.verbose) {
    console.log('\n');
  }

  console.log('-'.repeat(80));
  const total = filtered.length || 1;
  const avg = (n: number) => n / total;

  const summary = {
    timestamp: new Date().toISOString(),
    total_cases: filtered.length,
    improved: improvedCount,
    regressed: regressedCount,
    same: sameCount,
    semantic_negative_violations_at_3: semanticNegativeViolations,
    baseline: {
      hit_rate_at_3: avg(baseHit3),
      avg_mrr_at_k: avg(baseMrr),
      avg_ndcg_at_k: avg(baseNdcg),
    },
    semantic: {
      hit_rate_at_3: avg(semHit3),
      avg_mrr_at_k: avg(semMrr),
      avg_ndcg_at_k: avg(semNdcg),
    },
    delta: {
      hit_rate_at_3: avg(semHit3) - avg(baseHit3),
      avg_mrr_at_k: avg(semMrr) - avg(baseMrr),
      avg_ndcg_at_k: avg(semNdcg) - avg(baseNdcg),
    },
    k,
    hermetic: !opts.noHermetic,
    results: detailed,
  };

  console.log(`\nSummary:\n`);
  console.log(`✅ Improved:  ${improvedCount}`);
  console.log(`=  Same:      ${sameCount}`);
  console.log(`⚠️ Regressed: ${regressedCount}`);
  console.log(`⚠️ neg@3:     ${semanticNegativeViolations}`);
  console.log('');
  console.log(`Base  Hit@3:  ${(summary.baseline.hit_rate_at_3 * 100).toFixed(1)}% | MRR@${k}: ${(summary.baseline.avg_mrr_at_k * 100).toFixed(1)}% | NDCG@${k}: ${(summary.baseline.avg_ndcg_at_k * 100).toFixed(1)}%`);
  console.log(`Sem   Hit@3:  ${(summary.semantic.hit_rate_at_3 * 100).toFixed(1)}% | MRR@${k}: ${(summary.semantic.avg_mrr_at_k * 100).toFixed(1)}% | NDCG@${k}: ${(summary.semantic.avg_ndcg_at_k * 100).toFixed(1)}%`);
  console.log(`Delta Hit@3:  ${(summary.delta.hit_rate_at_3 * 100).toFixed(1)}% | MRR@${k}: ${(summary.delta.avg_mrr_at_k * 100).toFixed(1)}% | NDCG@${k}: ${(summary.delta.avg_ndcg_at_k * 100).toFixed(1)}%`);

  if (opts.json) {
    console.log('\n' + JSON.stringify(summary, null, 2));
  }

  hermetic?.cleanup();
}

main();

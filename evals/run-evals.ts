#!/usr/bin/env bun
/**
 * Skill Search Evaluation Runner
 *
 * Runs test cases against the skill analyzer and computes metrics.
 *
 * Usage:
 *   bun run evals/run-evals.ts                    # Run all evals
 *   bun run evals/run-evals.ts --category typo    # Run specific category
 *   bun run evals/run-evals.ts --verbose          # Show detailed results
 *   bun run evals/run-evals.ts --json             # Output JSON for comparison
 *   bun run evals/run-evals.ts --save baseline    # Save results as named snapshot
 *   bun run evals/run-evals.ts --compare baseline # Compare against saved snapshot
 */

import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

const EVALS_DIR = __dirname;
const TEST_CASES_FILE = path.join(EVALS_DIR, 'test-cases.json');
const RESULTS_DIR = path.join(EVALS_DIR, 'results');
const ANALYZER_SCRIPT = path.join(__dirname, '..', 'hooks', 'prompt-submit', 'analyze-prompt-skills.ts');

interface TestCase {
  id: string;
  category: string;
  query: string;
  expected?: string[];
  not_expected?: string[];
  notes?: string;
}

interface TestCasesFile {
  version: string;
  description: string;
  test_cases: TestCase[];
}

interface SearchResult {
  name: string;
  score: number;
  path: string;
}

interface EvalResult {
  id: string;
  category: string;
  query: string;
  expected: string[];
  not_expected: string[];
  actual_top3: SearchResult[];
  actual_top10: SearchResult[];
  metrics: {
    precision_at_3: number;
    recall_at_3: number;
    precision_at_10: number;
    recall_at_10: number;
    mrr: number;
    first_relevant_rank: number | null;
    has_negative_match: boolean;
  };
  pass: boolean;
  notes?: string;
}

interface EvalSummary {
  timestamp: string;
  total_cases: number;
  passed: number;
  failed: number;
  pass_rate: number;
  avg_precision_at_3: number;
  avg_recall_at_3: number;
  avg_mrr: number;
  by_category: Record<string, {
    total: number;
    passed: number;
    pass_rate: number;
  }>;
  results: EvalResult[];
}

/**
 * Run the skill analyzer on a query and parse results
 */
async function runAnalyzer(query: string): Promise<SearchResult[]> {
  return new Promise((resolve, reject) => {
    const proc = spawn('bun', ['run', ANALYZER_SCRIPT], {
      env: { ...process.env, SKILL_ANALYZER_SHOW_SCORES: '1' },
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

      try {
        // Parse results from stderr (where skill suggestions are printed)
        const results: SearchResult[] = [];
        const lines = stderr.split('\n');

        for (const line of lines) {
          // Match: "  • skill-name [score: 35, 🔍 fuzzy]: description"
          const match = line.match(/^\s*•\s+([^\[]+)\s+\[score:\s*(\d+)/);
          if (match) {
            results.push({
              name: match[1].trim(),
              score: parseInt(match[2], 10),
              path: '',
            });
          }
        }

        resolve(results);
      } catch (error) {
        console.error(`Failed to parse results for "${query}": ${error}`);
        resolve([]);
      }
    });
  });
}

/**
 * Normalize skill name for comparison
 * Handles case differences and common variations
 */
function normalizeSkillName(name: string): string {
  return name
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');
}

/**
 * Check if actual result matches expected skill
 */
function matchesExpected(actual: string, expected: string): boolean {
  const normActual = normalizeSkillName(actual);
  const normExpected = normalizeSkillName(expected);

  // Exact match
  if (normActual === normExpected) return true;

  // Partial match (one contains the other)
  if (normActual.includes(normExpected) || normExpected.includes(normActual)) return true;

  return false;
}

/**
 * Calculate precision at k
 * What fraction of top-k results are relevant?
 */
function precisionAtK(actual: SearchResult[], expected: string[], k: number): number {
  if (actual.length === 0 || expected.length === 0) return 0;

  const topK = actual.slice(0, k);
  const relevant = topK.filter(r =>
    expected.some(e => matchesExpected(r.name, e))
  ).length;

  return relevant / Math.min(k, topK.length);
}

/**
 * Calculate recall at k
 * What fraction of expected skills appear in top-k?
 */
function recallAtK(actual: SearchResult[], expected: string[], k: number): number {
  if (expected.length === 0) return 1; // No expected = perfect recall
  if (actual.length === 0) return 0;

  const topK = actual.slice(0, k);
  const found = expected.filter(e =>
    topK.some(r => matchesExpected(r.name, e))
  ).length;

  return found / expected.length;
}

/**
 * Calculate Mean Reciprocal Rank
 * 1/rank of first relevant result
 */
function calculateMRR(actual: SearchResult[], expected: string[]): number {
  if (expected.length === 0) return 1;
  if (actual.length === 0) return 0;

  for (let i = 0; i < actual.length; i++) {
    if (expected.some(e => matchesExpected(actual[i].name, e))) {
      return 1 / (i + 1);
    }
  }

  return 0;
}

/**
 * Find rank of first relevant result
 */
function firstRelevantRank(actual: SearchResult[], expected: string[]): number | null {
  if (expected.length === 0) return null;

  for (let i = 0; i < actual.length; i++) {
    if (expected.some(e => matchesExpected(actual[i].name, e))) {
      return i + 1;
    }
  }

  return null;
}

/**
 * Check if any not_expected skills appear in results
 */
function hasNegativeMatch(actual: SearchResult[], notExpected: string[], k: number): boolean {
  if (!notExpected || notExpected.length === 0) return false;

  const topK = actual.slice(0, k);
  return topK.some(r =>
    notExpected.some(ne => matchesExpected(r.name, ne))
  );
}

/**
 * Run evaluation for a single test case
 */
async function evaluateTestCase(testCase: TestCase): Promise<EvalResult> {
  const results = await runAnalyzer(testCase.query);

  const expected = testCase.expected || [];
  const notExpected = testCase.not_expected || [];

  const metrics = {
    precision_at_3: precisionAtK(results, expected, 3),
    recall_at_3: recallAtK(results, expected, 3),
    precision_at_10: precisionAtK(results, expected, 10),
    recall_at_10: recallAtK(results, expected, 10),
    mrr: calculateMRR(results, expected),
    first_relevant_rank: firstRelevantRank(results, expected),
    has_negative_match: hasNegativeMatch(results, notExpected, 3),
  };

  // Pass criteria:
  // - At least one expected skill in top 3 (if expected list provided)
  // - No not_expected skills in top 3 (if not_expected list provided)
  const hasExpected = expected.length === 0 || metrics.recall_at_3 > 0;
  const noNegatives = !metrics.has_negative_match;
  const pass = hasExpected && noNegatives;

  return {
    id: testCase.id,
    category: testCase.category,
    query: testCase.query,
    expected,
    not_expected: notExpected,
    actual_top3: results.slice(0, 3),
    actual_top10: results.slice(0, 10),
    metrics,
    pass,
    notes: testCase.notes,
  };
}

/**
 * Run all evaluations
 */
async function runEvaluations(options: {
  category?: string;
  verbose?: boolean;
  json?: boolean;
  save?: string;
  compare?: string;
}): Promise<EvalSummary> {
  // Load test cases
  const testCasesFile: TestCasesFile = JSON.parse(
    fs.readFileSync(TEST_CASES_FILE, 'utf-8')
  );

  let testCases = testCasesFile.test_cases;

  // Filter by category if specified
  if (options.category) {
    testCases = testCases.filter(tc =>
      tc.category.toLowerCase().includes(options.category!.toLowerCase())
    );
  }

  console.log(`\n🧪 Running ${testCases.length} evaluation cases...\n`);

  const results: EvalResult[] = [];

  for (const testCase of testCases) {
    const result = await evaluateTestCase(testCase);
    results.push(result);

    // Print progress
    const icon = result.pass ? '✅' : '❌';
    const scoreInfo = result.actual_top3.length > 0
      ? `(top: ${result.actual_top3[0].name}, score: ${result.actual_top3[0].score})`
      : '(no results)';

    if (options.verbose || !result.pass) {
      console.log(`${icon} [${result.category}] "${result.query}" ${scoreInfo}`);
      if (!result.pass) {
        console.log(`   Expected: ${result.expected.join(', ') || '(none)'}`);
        console.log(`   Got: ${result.actual_top3.map(r => r.name).join(', ') || '(none)'}`);
        if (result.metrics.has_negative_match) {
          console.log(`   ⚠️  Negative match found: ${result.not_expected.join(', ')}`);
        }
      }
    } else {
      process.stdout.write(icon);
    }
  }

  if (!options.verbose) {
    console.log('\n');
  }

  // Calculate summary
  const passed = results.filter(r => r.pass).length;
  const failed = results.length - passed;

  // Group by category
  const byCategory: Record<string, { total: number; passed: number; pass_rate: number }> = {};
  for (const result of results) {
    if (!byCategory[result.category]) {
      byCategory[result.category] = { total: 0, passed: 0, pass_rate: 0 };
    }
    byCategory[result.category].total++;
    if (result.pass) byCategory[result.category].passed++;
  }
  for (const cat of Object.keys(byCategory)) {
    byCategory[cat].pass_rate = byCategory[cat].passed / byCategory[cat].total;
  }

  const summary: EvalSummary = {
    timestamp: new Date().toISOString(),
    total_cases: results.length,
    passed,
    failed,
    pass_rate: passed / results.length,
    avg_precision_at_3: results.reduce((sum, r) => sum + r.metrics.precision_at_3, 0) / results.length,
    avg_recall_at_3: results.reduce((sum, r) => sum + r.metrics.recall_at_3, 0) / results.length,
    avg_mrr: results.reduce((sum, r) => sum + r.metrics.mrr, 0) / results.length,
    by_category: byCategory,
    results,
  };

  // Print summary
  console.log('═'.repeat(60));
  console.log('📊 EVALUATION SUMMARY');
  console.log('═'.repeat(60));
  console.log(`Total:     ${summary.total_cases} cases`);
  console.log(`Passed:    ${summary.passed} (${(summary.pass_rate * 100).toFixed(1)}%)`);
  console.log(`Failed:    ${summary.failed}`);
  console.log('─'.repeat(60));
  console.log(`Avg Precision@3:  ${(summary.avg_precision_at_3 * 100).toFixed(1)}%`);
  console.log(`Avg Recall@3:     ${(summary.avg_recall_at_3 * 100).toFixed(1)}%`);
  console.log(`Avg MRR:          ${(summary.avg_mrr * 100).toFixed(1)}%`);
  console.log('─'.repeat(60));
  console.log('\nBy Category:');
  for (const [cat, stats] of Object.entries(byCategory)) {
    const bar = '█'.repeat(Math.round(stats.pass_rate * 10)) + '░'.repeat(10 - Math.round(stats.pass_rate * 10));
    console.log(`  ${cat.padEnd(20)} ${bar} ${stats.passed}/${stats.total} (${(stats.pass_rate * 100).toFixed(0)}%)`);
  }
  console.log('═'.repeat(60));

  // Save results if requested
  if (options.save) {
    fs.mkdirSync(RESULTS_DIR, { recursive: true });
    const filename = path.join(RESULTS_DIR, `${options.save}.json`);
    fs.writeFileSync(filename, JSON.stringify(summary, null, 2));
    console.log(`\n💾 Saved results to ${filename}`);
  }

  // Compare against previous run if requested
  if (options.compare) {
    const compareFile = path.join(RESULTS_DIR, `${options.compare}.json`);
    if (fs.existsSync(compareFile)) {
      const previous: EvalSummary = JSON.parse(fs.readFileSync(compareFile, 'utf-8'));
      console.log(`\n📈 Comparison vs ${options.compare}:`);

      const delta = (curr: number, prev: number) => {
        const diff = curr - prev;
        const sign = diff >= 0 ? '+' : '';
        return `${sign}${(diff * 100).toFixed(1)}%`;
      };

      console.log(`  Pass Rate:     ${(summary.pass_rate * 100).toFixed(1)}% (${delta(summary.pass_rate, previous.pass_rate)})`);
      console.log(`  Precision@3:   ${(summary.avg_precision_at_3 * 100).toFixed(1)}% (${delta(summary.avg_precision_at_3, previous.avg_precision_at_3)})`);
      console.log(`  Recall@3:      ${(summary.avg_recall_at_3 * 100).toFixed(1)}% (${delta(summary.avg_recall_at_3, previous.avg_recall_at_3)})`);
      console.log(`  MRR:           ${(summary.avg_mrr * 100).toFixed(1)}% (${delta(summary.avg_mrr, previous.avg_mrr)})`);
    } else {
      console.log(`\n⚠️  Comparison file not found: ${compareFile}`);
    }
  }

  // Output JSON if requested
  if (options.json) {
    console.log('\n' + JSON.stringify(summary, null, 2));
  }

  return summary;
}

// Parse CLI arguments
const args = process.argv.slice(2);
const options = {
  category: args.find((_, i) => args[i - 1] === '--category'),
  verbose: args.includes('--verbose') || args.includes('-v'),
  json: args.includes('--json'),
  save: args.find((_, i) => args[i - 1] === '--save'),
  compare: args.find((_, i) => args[i - 1] === '--compare'),
};

runEvaluations(options).then((summary) => {
  process.exit(summary.failed > 0 ? 1 : 0);
});

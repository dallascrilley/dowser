#!/usr/bin/env bun
/**
 * Semantic Search Evaluation Runner
 *
 * Compares skill search results with and without semantic search enabled.
 */

import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

const EVALS_DIR = __dirname;
const TEST_CASES_FILE = path.join(EVALS_DIR, 'test-semantic.json');
const ANALYZER_SCRIPT = path.join(__dirname, '..', 'hooks', 'prompt-submit', 'analyze-prompt-skills.ts');

interface TestCase {
  id: string;
  category: string;
  query: string;
  expected: string[];
  notes?: string;
}

interface SearchResult {
  name: string;
  score: number;
  source?: string;
  skillPath?: string;
  folderSlug?: string;
}

async function runAnalyzer(query: string, semanticEnabled: boolean): Promise<SearchResult[]> {
  return new Promise((resolve, reject) => {
    const proc = spawn('bun', ['run', ANALYZER_SCRIPT], {
      env: { 
        ...process.env, 
        SKILL_ANALYZER_SHOW_SCORES: '1',
        SKILL_ANALYZER_SEMANTIC: semanticEnabled ? '1' : '0',
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

function normalizeSkillName(name: string): string {
  return name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
}

function matchesExpected(actual: string, expected: string): boolean {
  const normActual = normalizeSkillName(actual);
  const normExpected = normalizeSkillName(expected);
  return normActual === normExpected || normActual.includes(normExpected) || normExpected.includes(normActual);
}

function getRank(results: SearchResult[], expected: string[]): number | null {
  for (let i = 0; i < results.length; i++) {
    const actual = results[i].folderSlug || results[i].name;
    if (expected.some(e => matchesExpected(actual, e))) {
      return i + 1;
    }
  }
  return null;
}

async function main() {
  const testCases = JSON.parse(fs.readFileSync(TEST_CASES_FILE, 'utf-8')).test_cases as TestCase[];
  
  console.log(`\n🧠 Running Semantic Search Comparison on ${testCases.length} cases\n`);
  console.log(`Analyzer Script: ${ANALYZER_SCRIPT}`);

  console.log(`\n${'Query'.padEnd(30)} | ${'Baseline'.padEnd(10)} | ${'Semantic'.padEnd(10)} | ${'Improvement'.padEnd(20)}`);
  console.log('-'.repeat(80));

  let improvedCount = 0;
  let regressedCount = 0;
  let sameCount = 0;

  for (const tc of testCases) {
    const baselineResults = await runAnalyzer(tc.query, false);
    const semanticResults = await runAnalyzer(tc.query, true);

    const baselineRank = getRank(baselineResults, tc.expected);
    const semanticRank = getRank(semanticResults, tc.expected);

    const baselineStr = baselineRank ? `#${baselineRank}` : '❌';
    const semanticStr = semanticRank ? `#${semanticRank}` : '❌';

    let diff = '';
    if (baselineRank === semanticRank) {
        sameCount++;
        diff = '=';
    } else if (semanticRank !== null && (baselineRank === null || semanticRank < baselineRank)) {
        improvedCount++;
        diff = '✅ Improved';
    } else {
        regressedCount++;
        diff = '⚠️ Regressed';
    }

    const queryTrunc = tc.query.length > 28 ? tc.query.slice(0, 25) + '...' : tc.query;
    console.log(`${queryTrunc.padEnd(30)} | ${baselineStr.padEnd(10)} | ${semanticStr.padEnd(10)} | ${diff} (${tc.expected[0]})`);
    
    // Detailed output for improvements
    if (diff.includes('Improved')) {
       const topResult = semanticResults[0];
       console.log(`   └─ Top match: ${topResult.name} (Score: ${topResult.score}, Source: ${topResult.source})`);
    }
  }

  console.log('-'.repeat(80));
  console.log(`\nSummary:\n`);
  console.log(`✅ Improved:  ${improvedCount}`);
  console.log(`=  Same:      ${sameCount}`);
  console.log(`⚠️ Regressed: ${regressedCount}`);
}

main();

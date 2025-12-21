#!/usr/bin/env bun
/**
 * Enhanced Skill Analyzer Hook for UserPromptSubmit
 * Hybrid System: Combines Fuse.js fuzzy matching, TF-IDF, and Semantic Search with declarative skill-rules.json
 *
 * Features:
 * - Fuse.js fuzzy search with configurable threshold (typo tolerance)
 * - TF-IDF term weighting for uniqueness
 * - Semantic Search (Embeddings) using @xenova/transformers
 * - Token-based exact matching for skill names and descriptions
 * - Keyword scoring for common technical terms
 * - Description relevance scoring with deduplication
 * - Process-lifetime caching with mtime-based invalidation
 * - skill-rules.json support for enforcement, priority, and intent patterns
 *
 * Configuration:
 * - SKILL_ANALYZER_DEBUG=1          Show all scores and matching details
 * - SKILL_ANALYZER_DEBUG_FUZZY=1    Show fuzzy match details
 * - SKILL_ANALYZER_SHOW_SCORES=1    Include scores in output
 * - SKILL_ANALYZER_DEBUG_RULES=1    Show rules.json matching details
 * - SKILL_ANALYZER_SEMANTIC=0       Disable semantic search (enabled by default)
 */

import type { HookInput } from './skill-analyzer/types';
import { analyzeUserPrompt } from './skill-analyzer/analyze';
import { GAP_THRESHOLD, recordSkillActivation, recordSearch, loadMetrics, clearGaps } from './skill-analyzer/metrics';

/**
 * Read stdin with timeout
 */
async function readStdinWithTimeout(timeout: number = 5000): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = '';
    const timer = setTimeout(() => {
      reject(new Error('Timeout reading from stdin'));
    }, timeout);

    process.stdin.on('data', (chunk) => {
      data += chunk.toString();
    });

    process.stdin.on('end', () => {
      clearTimeout(timer);
      resolve(data);
    });

    process.stdin.on('error', (err) => {
      clearTimeout(timer);
      reject(err);
    });
  });
}

/**
 * Main hook function
 */
async function main() {
  try {
    const input = await readStdinWithTimeout();
    const data: HookInput = JSON.parse(input);
    const response = await analyzeUserPrompt(data);
    console.log(JSON.stringify(response));
  } catch (error) {
    console.error('Error in skill analyzer hook:', error);
    console.log(JSON.stringify({}));
  }
}

// CLI mode for recording metrics externally
const args = process.argv.slice(2);
if (args[0] === '--record-activation' && args[1]) {
  recordSkillActivation(args[1]);
  console.log(`Recorded activation: ${args[1]}`);
} else if (args[0] === '--record-search' && args[1]) {
  recordSearch(args[1]);
  console.log(`Recorded search: ${args[1]}`);
} else if (args[0] === '--show-metrics') {
  const metrics = loadMetrics();
  console.log(JSON.stringify(metrics, null, 2));
} else if (args[0] === '--show-gaps') {
  const metrics = loadMetrics();
  const gaps = Object.entries(metrics.gaps).sort((a, b) => b[1] - a[1]);
  console.log(`\n📊 Skill Gaps (queries with low relevance scores < ${GAP_THRESHOLD})`);
  console.log('='.repeat(60));
  console.log(`Total gap queries: ${gaps.reduce((a, [_, c]) => a + c, 0)}`);
  console.log(`Unique queries: ${gaps.length}`);
  console.log('='.repeat(60) + '\n');
  if (gaps.length === 0) {
    console.log('No gaps recorded yet.');
  } else {
    gaps.forEach(([query, count], i) => {
      console.log(`${String(i + 1).padEnd(4)} ${String(count).padStart(4)}x  "${query}"`);
    });
  }
} else if (args[0] === '--clear-gaps') {
  clearGaps();
  console.log('Gaps cleared.');
} else {
  // Normal hook mode - read from stdin
  main();
}

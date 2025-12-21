#!/usr/bin/env bun
/**
 * Analyze skill gaps from rich JSONL log
 *
 * Usage:
 *   bun run scripts/analyze-gaps.ts              # Show top gaps and recent entries
 *   bun run scripts/analyze-gaps.ts --top 30     # Show top 30 gap queries
 *   bun run scripts/analyze-gaps.ts --recent 20  # Show last 20 gap entries
 *   bun run scripts/analyze-gaps.ts --json       # Output as JSON for further processing
 *   bun run scripts/analyze-gaps.ts --since 7    # Gaps from last 7 days
 */

import * as fs from 'fs';
import * as path from 'path';

const GAPS_LOG_PATH = path.join(__dirname, '..', 'lib', 'skill-gaps.jsonl');

interface RichGapEntry {
  query: string;
  bestScore: number;
  topMatches: Array<{ skill: string; score: number }>;
  timestamp: string;
}

function loadGaps(): RichGapEntry[] {
  if (!fs.existsSync(GAPS_LOG_PATH)) {
    return [];
  }

  try {
    const content = fs.readFileSync(GAPS_LOG_PATH, 'utf-8').trim();
    if (!content) return [];

    return content
      .split('\n')
      .filter(Boolean)
      .map(line => JSON.parse(line) as RichGapEntry);
  } catch (error) {
    console.error(`Error parsing gaps log: ${error}`);
    return [];
  }
}

function parseArgs() {
  const args = process.argv.slice(2);
  return {
    top: parseInt(args[args.indexOf('--top') + 1]) || 20,
    recent: parseInt(args[args.indexOf('--recent') + 1]) || 10,
    json: args.includes('--json'),
    sinceDays: parseInt(args[args.indexOf('--since') + 1]) || 0,
  };
}

function main() {
  const opts = parseArgs();
  const allGaps = loadGaps();

  // Filter by date if --since specified
  let gaps = allGaps;
  if (opts.sinceDays > 0) {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - opts.sinceDays);
    gaps = allGaps.filter(g => new Date(g.timestamp) >= cutoff);
  }

  if (gaps.length === 0) {
    console.log('No gaps recorded yet.');
    console.log(`\nGaps are logged when skill search scores are below threshold (< 15).`);
    console.log(`Log location: ${GAPS_LOG_PATH}`);
    return;
  }

  if (opts.json) {
    // Output raw JSON for processing
    console.log(JSON.stringify(gaps, null, 2));
    return;
  }

  // Frequency analysis - normalize and count queries
  const queryFreq = new Map<string, { count: number; avgScore: number; scores: number[] }>();
  for (const gap of gaps) {
    const normalized = gap.query.toLowerCase().trim().slice(0, 100);
    const existing = queryFreq.get(normalized) || { count: 0, avgScore: 0, scores: [] };
    existing.count++;
    existing.scores.push(gap.bestScore);
    existing.avgScore = existing.scores.reduce((a, b) => a + b, 0) / existing.scores.length;
    queryFreq.set(normalized, existing);
  }

  // Header
  console.log(`\n${'='.repeat(70)}`);
  console.log(`📊 SKILL GAP ANALYSIS`);
  console.log(`${'='.repeat(70)}`);
  console.log(`Total gap entries: ${gaps.length}`);
  console.log(`Unique queries: ${queryFreq.size}`);
  if (opts.sinceDays > 0) {
    console.log(`Time range: last ${opts.sinceDays} days`);
  }
  console.log(`Log file: ${GAPS_LOG_PATH}`);
  console.log(`${'='.repeat(70)}\n`);

  // Top gaps by frequency
  console.log(`🔝 TOP GAP QUERIES (by frequency)`);
  console.log(`${'─'.repeat(70)}`);
  console.log(`${'Count'.padStart(6)}  ${'Avg'.padStart(5)}  Query`);
  console.log(`${'─'.repeat(6)}  ${'─'.repeat(5)}  ${'─'.repeat(55)}`);

  const sortedQueries = [...queryFreq.entries()]
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, opts.top);

  for (const [query, { count, avgScore }] of sortedQueries) {
    const truncated = query.length > 55 ? query.slice(0, 52) + '...' : query;
    console.log(`${String(count).padStart(6)}  ${avgScore.toFixed(1).padStart(5)}  ${truncated}`);
  }

  // Recent gaps with details
  console.log(`\n📅 RECENT GAPS (last ${opts.recent})`);
  console.log(`${'─'.repeat(70)}`);

  const recentGaps = gaps.slice(-opts.recent).reverse();
  for (const gap of recentGaps) {
    const date = new Date(gap.timestamp).toLocaleString();
    const truncatedQuery = gap.query.length > 50 ? gap.query.slice(0, 47) + '...' : gap.query;

    console.log(`\n  [${date}] Score: ${gap.bestScore}`);
    console.log(`  Query: "${truncatedQuery}"`);

    if (gap.topMatches.length > 0) {
      const matches = gap.topMatches
        .map(m => `${m.skill} (${m.score})`)
        .join(', ');
      console.log(`  Closest: ${matches}`);
    } else {
      console.log(`  Closest: (none)`);
    }
  }

  // Suggested actions
  console.log(`\n${'='.repeat(70)}`);
  console.log(`💡 SUGGESTED ACTIONS`);
  console.log(`${'─'.repeat(70)}`);

  // Find queries that appear 2+ times
  const repeatedQueries = [...queryFreq.entries()]
    .filter(([_, { count }]) => count >= 2)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 5);

  if (repeatedQueries.length > 0) {
    console.log(`\nConsider creating skills for these frequently missed queries:`);
    for (const [query, { count, avgScore }] of repeatedQueries) {
      const truncated = query.length > 45 ? query.slice(0, 42) + '...' : query;
      console.log(`  • ${truncated} (${count}x, avg score ${avgScore.toFixed(1)})`);
    }
  } else {
    console.log(`\nNo repeated gap queries detected yet.`);
  }

  console.log(`\nRun with --json for raw data export.`);
  console.log(`${'='.repeat(70)}\n`);
}

main();

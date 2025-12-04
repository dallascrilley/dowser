#!/usr/bin/env bun
/**
 * View skill usage metrics
 *
 * Usage:
 *   bun run scripts/view-metrics.ts                    # Show top 20 suggestions
 *   bun run scripts/view-metrics.ts --all              # Show all suggestions
 *   bun run scripts/view-metrics.ts --top 50           # Show top 50 suggestions
 *   bun run scripts/view-metrics.ts --activations      # Show activations
 *   bun run scripts/view-metrics.ts --searches         # Show searches
 *   bun run scripts/view-metrics.ts --gaps             # Show gaps (missing skills)
 *   bun run scripts/view-metrics.ts --summary          # Show summary of all types
 */

import * as fs from 'fs';
import * as path from 'path';

const METRICS_FILE = path.join(__dirname, '..', 'lib', 'skill-metrics.json');

interface SkillMetrics {
  suggestions: Record<string, number>;
  activations: Record<string, number>;
  searches: Record<string, number>;
  gaps: Record<string, number>;
  lastUpdated: string;
  lastGapNotification?: string;
}

function loadMetrics(): SkillMetrics {
  if (!fs.existsSync(METRICS_FILE)) {
    return { suggestions: {}, activations: {}, searches: {}, gaps: {}, lastUpdated: '' };
  }

  const data = JSON.parse(fs.readFileSync(METRICS_FILE, 'utf-8'));

  // Handle legacy flat format
  if (!data.suggestions && !data.activations) {
    return {
      suggestions: data,
      activations: {},
      searches: {},
      gaps: {},
      lastUpdated: new Date().toISOString()
    };
  }

  // Ensure gaps exists
  if (!data.gaps) {
    data.gaps = {};
  }

  return data;
}

function printTable(title: string, data: Record<string, number>, limit: number) {
  const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const total = sorted.reduce((sum, [_, count]) => sum + count, 0);

  console.log(`\n📊 ${title}`);
  console.log(`${'='.repeat(60)}`);
  console.log(`Total items: ${sorted.length}`);
  console.log(`Total count: ${total.toLocaleString()}`);
  console.log(`${'='.repeat(60)}\n`);

  if (sorted.length === 0) {
    console.log('No data recorded yet.\n');
    return;
  }

  console.log(`${'Rank'.padEnd(6)}${'Count'.padStart(8)}  ${'%'.padStart(6)}  Item`);
  console.log(`${'-'.repeat(6)}${'-'.repeat(8)}  ${'-'.repeat(6)}  ${'-'.repeat(38)}`);

  sorted.slice(0, limit).forEach(([item, count], index) => {
    const percent = total > 0 ? ((count / total) * 100).toFixed(1) : '0.0';
    console.log(`${String(index + 1).padEnd(6)}${String(count).padStart(8)}  ${percent.padStart(5)}%  ${item}`);
  });

  if (limit < sorted.length) {
    console.log(`\n... and ${sorted.length - limit} more items`);
  }
}

function printSummary(metrics: SkillMetrics) {
  const suggestionCount = Object.values(metrics.suggestions).reduce((a, b) => a + b, 0);
  const activationCount = Object.values(metrics.activations).reduce((a, b) => a + b, 0);
  const searchCount = Object.values(metrics.searches).reduce((a, b) => a + b, 0);
  const gapCount = Object.values(metrics.gaps).reduce((a, b) => a + b, 0);

  console.log(`\n📊 Skill Metrics Summary`);
  console.log(`${'='.repeat(60)}`);
  console.log(`Last updated: ${metrics.lastUpdated || 'N/A'}`);
  console.log(`${'='.repeat(60)}\n`);

  console.log(`${'Category'.padEnd(20)}${'Unique'.padStart(10)}${'Total'.padStart(12)}`);
  console.log(`${'-'.repeat(20)}${'-'.repeat(10)}${'-'.repeat(12)}`);
  console.log(`${'Suggestions'.padEnd(20)}${String(Object.keys(metrics.suggestions).length).padStart(10)}${suggestionCount.toLocaleString().padStart(12)}`);
  console.log(`${'Activations'.padEnd(20)}${String(Object.keys(metrics.activations).length).padStart(10)}${activationCount.toLocaleString().padStart(12)}`);
  console.log(`${'Searches'.padEnd(20)}${String(Object.keys(metrics.searches).length).padStart(10)}${searchCount.toLocaleString().padStart(12)}`);
  console.log(`${'Gaps (missing)'.padEnd(20)}${String(Object.keys(metrics.gaps).length).padStart(10)}${gapCount.toLocaleString().padStart(12)}`);

  // Show top 5 of each
  console.log(`\n--- Top 5 Suggestions ---`);
  Object.entries(metrics.suggestions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .forEach(([name, count], i) => console.log(`  ${i + 1}. ${name} (${count})`));

  if (Object.keys(metrics.activations).length > 0) {
    console.log(`\n--- Top 5 Activations ---`);
    Object.entries(metrics.activations)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .forEach(([name, count], i) => console.log(`  ${i + 1}. ${name} (${count})`));
  }

  if (Object.keys(metrics.searches).length > 0) {
    console.log(`\n--- Top 5 Searches ---`);
    Object.entries(metrics.searches)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .forEach(([name, count], i) => console.log(`  ${i + 1}. "${name}" (${count})`));
  }

  if (Object.keys(metrics.gaps).length > 0) {
    console.log(`\n--- Top 5 Gaps (Missing Skills) ---`);
    Object.entries(metrics.gaps)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .forEach(([name, count], i) => console.log(`  ${i + 1}. "${name}" (${count})`));
  }
}

function main() {
  const metrics = loadMetrics();
  const args = process.argv.slice(2);

  let limit = 20;
  let mode: 'suggestions' | 'activations' | 'searches' | 'gaps' | 'summary' = 'suggestions';

  if (args.includes('--all')) {
    limit = Infinity;
  } else if (args.includes('--top')) {
    const topIndex = args.indexOf('--top');
    limit = parseInt(args[topIndex + 1]) || 20;
  }

  if (args.includes('--activations')) {
    mode = 'activations';
  } else if (args.includes('--searches')) {
    mode = 'searches';
  } else if (args.includes('--gaps')) {
    mode = 'gaps';
  } else if (args.includes('--summary')) {
    mode = 'summary';
  }

  switch (mode) {
    case 'summary':
      printSummary(metrics);
      break;
    case 'activations':
      printTable('Skill Activations (via Skill tool)', metrics.activations, limit);
      break;
    case 'searches':
      printTable('Search Queries', metrics.searches, limit);
      break;
    case 'gaps':
      printTable('Skill Gaps (queries with low relevance - consider creating skills)', metrics.gaps, limit);
      break;
    default:
      printTable('Skill Suggestions (from hook)', metrics.suggestions, limit);
  }
}

main();

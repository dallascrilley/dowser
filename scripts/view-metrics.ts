#!/usr/bin/env bun
/**
 * View skill usage metrics
 *
 * Usage:
 *   bun run scripts/view-metrics.ts           # Show top 20
 *   bun run scripts/view-metrics.ts --all     # Show all
 *   bun run scripts/view-metrics.ts --top 50  # Show top 50
 */

import * as fs from 'fs';
import * as path from 'path';

const METRICS_FILE = path.join(__dirname, '..', 'lib', 'skill-metrics.json');

function main() {
  if (!fs.existsSync(METRICS_FILE)) {
    console.log('No metrics file found. Run some skill searches first.');
    process.exit(1);
  }

  const metrics: Record<string, number> = JSON.parse(fs.readFileSync(METRICS_FILE, 'utf-8'));

  // Sort by hit count descending
  const sorted = Object.entries(metrics)
    .sort((a, b) => b[1] - a[1]);

  // Parse args
  const args = process.argv.slice(2);
  let limit = 20;

  if (args.includes('--all')) {
    limit = sorted.length;
  } else if (args.includes('--top')) {
    const topIndex = args.indexOf('--top');
    limit = parseInt(args[topIndex + 1]) || 20;
  }

  const totalHits = sorted.reduce((sum, [_, count]) => sum + count, 0);

  console.log(`\n📊 Skill Usage Metrics`);
  console.log(`${'='.repeat(60)}`);
  console.log(`Total skills tracked: ${sorted.length}`);
  console.log(`Total hits: ${totalHits.toLocaleString()}`);
  console.log(`${'='.repeat(60)}\n`);

  console.log(`Top ${Math.min(limit, sorted.length)} Skills:\n`);
  console.log(`${'Rank'.padEnd(6)}${'Hits'.padStart(8)}  ${'%'.padStart(6)}  Skill`);
  console.log(`${'-'.repeat(6)}${'-'.repeat(8)}  ${'-'.repeat(6)}  ${'-'.repeat(38)}`);

  sorted.slice(0, limit).forEach(([skill, count], index) => {
    const percent = ((count / totalHits) * 100).toFixed(1);
    console.log(`${String(index + 1).padEnd(6)}${String(count).padStart(8)}  ${percent.padStart(5)}%  ${skill}`);
  });

  if (limit < sorted.length) {
    console.log(`\n... and ${sorted.length - limit} more skills`);
    console.log(`Use --all to see all, or --top N for top N`);
  }
}

main();

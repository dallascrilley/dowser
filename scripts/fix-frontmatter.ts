#!/usr/bin/env bun
/**
 * Auto-fix frontmatter issues in SKILL.md files
 *
 * Usage:
 *   bun run scripts/fix-frontmatter.ts                    # Dry run (preview changes)
 *   bun run scripts/fix-frontmatter.ts --apply            # Apply changes
 *   bun run scripts/fix-frontmatter.ts --skill airtable   # Fix specific skill
 */

import { readFileSync, writeFileSync, readdirSync, statSync } from 'fs';
import { join, basename } from 'path';
import matter from 'gray-matter';

// Default to global skills directory, or use --dir flag
const args = process.argv.slice(2);
const dirFlagIndex = args.indexOf('--dir');
const SKILLS_DIR = dirFlagIndex !== -1 && args[dirFlagIndex + 1]
  ? args[dirFlagIndex + 1]
  : join(process.env.HOME || '', '.claude', 'skills');
const MAX_WHEN_TO_USE = 295;  // Slightly under 300 to account for YAML formatting
const MAX_SHORT_DESC = 300;

interface FixResult {
  skill: string;
  path: string;
  fixes: string[];
  original: { when_to_use?: string; description?: string; short_description?: string };
  updated: { when_to_use?: string; short_description?: string };
}

function truncateText(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;

  // Try to cut at sentence boundary
  const truncated = text.slice(0, maxLen - 3);
  const lastPeriod = truncated.lastIndexOf('.');
  const lastComma = truncated.lastIndexOf(',');
  const lastSpace = truncated.lastIndexOf(' ');

  // Prefer sentence boundary, then comma, then space
  if (lastPeriod > maxLen * 0.6) {
    return truncated.slice(0, lastPeriod + 1);
  } else if (lastComma > maxLen * 0.6) {
    return truncated.slice(0, lastComma) + '...';
  } else if (lastSpace > maxLen * 0.6) {
    return truncated.slice(0, lastSpace) + '...';
  }

  return truncated + '...';
}

function generateShortDescription(description: string): string {
  // Take first sentence or truncate
  const firstSentence = description.match(/^[^.!?]+[.!?]/);
  if (firstSentence && firstSentence[0].length <= MAX_SHORT_DESC) {
    return firstSentence[0].trim();
  }

  // Truncate intelligently
  return truncateText(description, MAX_SHORT_DESC);
}

function findSkillFiles(dir: string): string[] {
  const results: string[] = [];

  function walk(currentDir: string) {
    const entries = readdirSync(currentDir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(currentDir, entry.name);
      if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
        walk(fullPath);
      } else if (entry.name === 'SKILL.md') {
        results.push(fullPath);
      }
    }
  }

  walk(dir);
  return results;
}

function fixSkillFile(filePath: string, applyChanges: boolean): FixResult | null {
  const content = readFileSync(filePath, 'utf-8');
  const skillName = basename(join(filePath, '..'));

  let data: Record<string, any>;
  let body: string;
  try {
    const parsed = matter(content);
    data = parsed.data;
    body = parsed.content;
  } catch (e) {
    console.warn(`  ⚠️  Skipping ${skillName}: YAML parse error`);
    return null;
  }
  const fixes: string[] = [];
  const original: FixResult['original'] = {};
  const updated: FixResult['updated'] = {};

  // Fix 1: Trim long when_to_use
  if (data.when_to_use && typeof data.when_to_use === 'string') {
    const whenLen = data.when_to_use.length;
    if (whenLen > MAX_WHEN_TO_USE) {
      original.when_to_use = data.when_to_use;
      data.when_to_use = truncateText(data.when_to_use, MAX_WHEN_TO_USE);
      updated.when_to_use = data.when_to_use;
      fixes.push(`Trimmed when_to_use: ${whenLen} → ${data.when_to_use.length} chars`);
    }
  }

  // Fix 2: Add short_description if description is too long
  if (data.description && typeof data.description === 'string' && !data.short_description) {
    const descLen = data.description.length;
    if (descLen > MAX_SHORT_DESC) {
      original.description = data.description;
      data.short_description = generateShortDescription(data.description);
      updated.short_description = data.short_description;
      fixes.push(`Added short_description (${data.short_description.length} chars) from ${descLen} char description`);
    }
  }

  // Fix 3: Add missing version
  if (!data.version) {
    data.version = '1.0.0';
    fixes.push('Added version: 1.0.0');
  }

  if (fixes.length === 0) {
    return null;
  }

  if (applyChanges) {
    const newContent = matter.stringify(body, data);
    writeFileSync(filePath, newContent);
  }

  return {
    skill: skillName,
    path: filePath,
    fixes,
    original,
    updated,
  };
}

function main() {
  const args = process.argv.slice(2);
  const applyChanges = args.includes('--apply');
  const specificSkill = args.find((a, i) => args[i - 1] === '--skill');

  console.log(`\n🔧 Frontmatter Auto-Fixer`);
  console.log(`   Mode: ${applyChanges ? '✏️  APPLY CHANGES' : '👀 DRY RUN (preview only)'}`);
  console.log(`   Skills dir: ${SKILLS_DIR}\n`);

  const skillFiles = findSkillFiles(SKILLS_DIR);
  console.log(`Found ${skillFiles.length} SKILL.md files\n`);

  const results: FixResult[] = [];

  for (const filePath of skillFiles) {
    const skillName = basename(join(filePath, '..'));

    // Filter by specific skill if requested
    if (specificSkill && !skillName.includes(specificSkill)) {
      continue;
    }

    const result = fixSkillFile(filePath, applyChanges);
    if (result) {
      results.push(result);
    }
  }

  if (results.length === 0) {
    console.log('✅ No issues found - all skills have valid frontmatter!\n');
    return;
  }

  console.log(`📋 ${results.length} skills ${applyChanges ? 'fixed' : 'need fixes'}:\n`);

  for (const result of results) {
    console.log(`  ${applyChanges ? '✅' : '⚠️ '} ${result.skill}`);
    for (const fix of result.fixes) {
      console.log(`      - ${fix}`);
    }

    // Show before/after for truncations
    if (result.original.when_to_use && result.updated.when_to_use) {
      console.log(`      Before: "${result.original.when_to_use.slice(0, 80)}..."`);
      console.log(`      After:  "${result.updated.when_to_use.slice(0, 80)}..."`);
    }
    if (result.updated.short_description) {
      console.log(`      New short_description: "${result.updated.short_description.slice(0, 80)}..."`);
    }
    console.log('');
  }

  if (!applyChanges) {
    console.log(`\n💡 Run with --apply to make these changes:\n   bun run scripts/fix-frontmatter.ts --apply\n`);
  } else {
    console.log(`\n✅ Applied ${results.length} fixes. Run garden.sh to verify.\n`);
  }
}

main();

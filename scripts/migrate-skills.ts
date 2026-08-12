#!/usr/bin/env bun
/**
 * migrate-skills.ts
 *
 * Migrates skills from nested category structure to flat plugin structure.
 * Preserves category information in frontmatter.
 * Copies all supporting files (references, scripts, templates).
 */

import { glob } from 'glob';
import matter from 'gray-matter';
import { mkdirSync, readFileSync, writeFileSync, existsSync, readdirSync, copyFileSync, statSync } from 'fs';
import { join, dirname, basename, relative } from 'path';

const home = process.env.HOME || process.env.USERPROFILE || '';
const SOURCE_DIR = process.env.DOWSER_MIGRATE_SOURCE
  || (home ? `${home}/.claude/skills` : './skills-source');
const TARGET_DIR = process.env.DOWSER_MIGRATE_TARGET
  || (home ? `${home}/.claude/plugins/dowser/skills` : './skills');

// Skills to skip (already handled elsewhere or special cases)
const SKIP_SKILLS = new Set([
  'PAI', // Keep PAI at user level for session start hook
]);

// Track migrations
const migrated: string[] = [];
const skipped: string[] = [];
const errors: string[] = [];

function copyDirectory(src: string, dest: string) {
  const entries = readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = join(src, entry.name);
    const destPath = join(dest, entry.name);

    if (entry.isDirectory()) {
      mkdirSync(destPath, { recursive: true });
      copyDirectory(srcPath, destPath);
    } else {
      copyFileSync(srcPath, destPath);
    }
  }
}

async function migrate() {
  console.log('🚀 Starting skill migration...\n');
  console.log(`Source: ${SOURCE_DIR}`);
  console.log(`Target: ${TARGET_DIR}\n`);

  // Find all SKILL.md files
  const skillFiles = await glob(`${SOURCE_DIR}/**/SKILL.md`, {
    ignore: ['**/node_modules/**', '**/.git/**']
  });

  console.log(`Found ${skillFiles.length} skills to migrate\n`);

  for (const skillPath of skillFiles) {
    try {
      // Extract path info
      const relativePath = skillPath.replace(SOURCE_DIR + '/', '');
      const parts = relativePath.split('/');

      // Determine skill name and category
      // Format: category/skill-name/SKILL.md OR skill-name/SKILL.md
      let category: string;
      let skillName: string;

      if (parts.length === 2) {
        // Top-level skill: skill-name/SKILL.md
        category = 'root';
        skillName = parts[0];
      } else if (parts.length === 3) {
        // Nested skill: category/skill-name/SKILL.md
        category = parts[0];
        skillName = parts[1];
      } else {
        console.warn(`⚠️  Unexpected path structure: ${relativePath}`);
        skipped.push(relativePath);
        continue;
      }

      // Skip certain skills
      if (SKIP_SKILLS.has(skillName)) {
        console.log(`⏭️  Skipping ${skillName} (in skip list)`);
        skipped.push(skillName);
        continue;
      }

      // Check for name collisions
      const targetSkillDir = join(TARGET_DIR, skillName);
      if (existsSync(targetSkillDir)) {
        console.warn(`⚠️  Skill already exists: ${skillName} - skipping duplicate`);
        skipped.push(`${skillName} (duplicate)`);
        continue;
      }

      // Read and parse SKILL.md
      const content = readFileSync(skillPath, 'utf-8');
      const { data: frontmatter, content: body } = matter(content);

      // Add/update category in frontmatter
      if (!frontmatter.category) {
        frontmatter.category = category;
      }

      // Create target directory
      mkdirSync(targetSkillDir, { recursive: true });

      // Write updated SKILL.md
      const newContent = matter.stringify(body, frontmatter);
      writeFileSync(join(targetSkillDir, 'SKILL.md'), newContent);

      // Copy all other files from source skill directory
      const sourceDir = dirname(skillPath);
      const sourceFiles = readdirSync(sourceDir, { withFileTypes: true });

      for (const entry of sourceFiles) {
        if (entry.name === 'SKILL.md') continue; // Already handled

        const srcPath = join(sourceDir, entry.name);
        const destPath = join(targetSkillDir, entry.name);

        if (entry.isDirectory()) {
          mkdirSync(destPath, { recursive: true });
          copyDirectory(srcPath, destPath);
        } else {
          copyFileSync(srcPath, destPath);
        }
      }

      console.log(`✅ ${skillName} (${category})`);
      migrated.push(skillName);

    } catch (error) {
      console.error(`❌ Error migrating ${skillPath}:`, error);
      errors.push(skillPath);
    }
  }

  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('Migration Summary');
  console.log('='.repeat(50));
  console.log(`✅ Migrated: ${migrated.length}`);
  console.log(`⏭️  Skipped: ${skipped.length}`);
  console.log(`❌ Errors: ${errors.length}`);

  if (skipped.length > 0) {
    console.log('\nSkipped skills:');
    skipped.forEach(s => console.log(`  - ${s}`));
  }

  if (errors.length > 0) {
    console.log('\nFailed migrations:');
    errors.forEach(e => console.log(`  - ${e}`));
  }

  console.log('\n✨ Migration complete!');
  console.log(`\nNext steps:`);
  console.log(`1. Verify skills in ${TARGET_DIR}`);
  console.log(`2. Register plugin with Claude Code`);
  console.log(`3. Test skill discovery`);
}

migrate().catch(console.error);

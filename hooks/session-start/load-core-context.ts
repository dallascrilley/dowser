#!/usr/bin/env bun

/**
 * load-core-context.ts
 *
 * Automatically loads your PAI skill context at session start by reading and injecting
 * the PAI SKILL.md file contents directly into Claude's context as a system-reminder.
 *
 * Purpose:
 * - Read PAI SKILL.md file content
 * - Output content as system-reminder for Claude to process
 * - Ensure complete context (contacts, preferences, security, identity) available at session start
 * - Bypass skill activation logic by directly injecting context
 *
 * Setup:
 * 1. Customize your ~/.claude/skills/PAI/SKILL.md with your personal context
 * 2. Add this hook to settings.json SessionStart hooks
 * 3. Ensure PAI_DIR environment variable is set (defaults to $HOME/.claude)
 *
 * How it works:
 * - Runs at the start of every Claude Code session
 * - Skips execution for subagent sessions (they don't need PAI context)
 * - Reads your PAI SKILL.md file
 * - Injects content as <system-reminder> which Claude processes automatically
 * - Gives your AI immediate access to your complete personal context
 */

import { readFileSync, existsSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

async function main() {
  try {
    // Check if this is a subagent session - if so, exit silently
    const claudeProjectDir = process.env.CLAUDE_PROJECT_DIR || '';
    const isSubagent = claudeProjectDir.includes('/.claude/agents/') ||
                      process.env.CLAUDE_AGENT_TYPE !== undefined;

    if (isSubagent) {
      // Subagent sessions don't need PAI context loading
      console.error('🤖 Subagent session - skipping PAI context loading');
      process.exit(0);
    }

    // Get PAI directory from environment or use default
    const paiDir = process.env.PAI_DIR || join(homedir(), '.claude');
    
    // Handle both PAI_DIR scenarios:
    // 1. PAI_DIR points to repo root (e.g., /Users/user/PAI) -> use .claude/skills/PAI/SKILL.md
    // 2. PAI_DIR points to ~/.claude -> use skills/PAI/SKILL.md
    let paiSkillPath = join(paiDir, '.claude/skills/PAI/SKILL.md');
    
    // If path doesn't exist and paiDir ends with .claude, try without .claude prefix
    if (!existsSync(paiSkillPath) && paiDir.endsWith('.claude')) {
      paiSkillPath = join(paiDir, 'skills/PAI/SKILL.md');
    }

    // Verify PAI skill file exists
    if (!existsSync(paiSkillPath)) {
      console.error(`❌ PAI skill not found at: ${paiSkillPath}`);
      console.error(`💡 Create your PAI skill file or check PAI_DIR environment variable`);
      console.error(`   Tried: ${join(paiDir, '.claude/skills/PAI/SKILL.md')}`);
      if (paiDir.endsWith('.claude')) {
        console.error(`   Also tried: ${join(paiDir, 'skills/PAI/SKILL.md')}`);
      }
      process.exit(1);
    }

    console.error('📚 Reading PAI core context from skill file...');

    // Read the PAI SKILL.md file content
    const paiContent = readFileSync(paiSkillPath, 'utf-8');

    console.error(`✅ Read ${paiContent.length} characters from PAI SKILL.md`);

    // Output the PAI content as a system-reminder
    // This will be injected into Claude's context at session start
    const message = `<system-reminder>
PAI CORE CONTEXT (Auto-loaded at Session Start)

The following context has been loaded from ${paiSkillPath}:

---
${paiContent}
---

This context is now active for this session. Follow all instructions, preferences, and guidelines contained above.
</system-reminder>`;

    // Debug mode: Save injected content to file if DEBUG_PAI_CONTEXT is set
    if (process.env.DEBUG_PAI_CONTEXT === '1') {
      const debugDir = paiDir.endsWith('.claude') 
        ? join(paiDir, 'debug')
        : join(paiDir, '.claude', 'debug');
      const debugPath = join(debugDir, 'injected-context.txt');
      
      if (!existsSync(debugDir)) {
        mkdirSync(debugDir, { recursive: true });
      }
      writeFileSync(debugPath, message, 'utf-8');
      console.error(`🔍 DEBUG: Injected context saved to ${debugPath}`);
    }

    // Write to stdout (will be captured by Claude Code)
    console.log(message);

    console.error('✅ PAI context injected into session');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error in load-core-context hook:', error);
    process.exit(1);
  }
}

main();
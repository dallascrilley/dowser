import { describe, test, expect, beforeEach, afterEach, spyOn, mock } from 'bun:test';
import { mkdtempSync, writeFileSync, rmSync, mkdirSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';

/**
 * Regression tests for load-core-context.ts SessionStart hook
 *
 * Critical behaviors to verify:
 * 1. Hook exits with code 0 in ALL scenarios (success, missing file, errors)
 * 2. Hook outputs valid system-reminder content
 * 3. Hook skips processing for subagent sessions
 * 4. Hook provides helpful warnings when PAI skill not found
 */

describe('load-core-context hook', () => {
  let tempDir: string;
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    // Create temp directory for test files
    tempDir = mkdtempSync(join(tmpdir(), 'pai-skills-test-'));
    // Save original environment
    originalEnv = { ...process.env };
  });

  afterEach(() => {
    // Restore environment
    process.env = originalEnv;
    // Clean up temp directory
    try {
      rmSync(tempDir, { recursive: true, force: true });
    } catch {
      // Ignore cleanup errors
    }
  });

  describe('exit code behavior (critical for plugin loading)', () => {
    test('exits with code 0 when PAI skill file exists', async () => {
      // Setup: Create PAI skill file in expected location
      const claudeDir = join(tempDir, '.claude');
      const skillsDir = join(claudeDir, 'skills', 'PAI');
      mkdirSync(skillsDir, { recursive: true });
      writeFileSync(join(skillsDir, 'SKILL.md'), '# Test PAI Skill\n\nTest content');

      // Set PAI_DIR to temp directory
      process.env.PAI_DIR = tempDir;

      // Run hook as subprocess to capture exit code
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
        },
      });

      expect(result.exitCode).toBe(0);
    });

    test('exits with code 0 when PAI skill file is MISSING (graceful degradation)', async () => {
      // Setup: Empty temp directory - no PAI skill file
      process.env.PAI_DIR = tempDir;

      // Run hook as subprocess
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
        },
      });

      // CRITICAL: Must exit with 0, not 1
      // This is the bug we fixed - previously exited with 1 and broke the plugin
      expect(result.exitCode).toBe(0);
    });

    test('exits with code 0 for subagent sessions', async () => {
      // Setup: Simulate subagent environment
      process.env.CLAUDE_AGENT_TYPE = 'subagent';
      process.env.PAI_DIR = tempDir;

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
          CLAUDE_AGENT_TYPE: 'subagent',
        },
      });

      expect(result.exitCode).toBe(0);
    });
  });

  describe('output format', () => {
    test('outputs system-reminder when PAI skill exists', async () => {
      // Setup
      const claudeDir = join(tempDir, '.claude');
      const skillsDir = join(claudeDir, 'skills', 'PAI');
      mkdirSync(skillsDir, { recursive: true });
      writeFileSync(join(skillsDir, 'SKILL.md'), '# My PAI Skill\n\nPersonal context here');

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
        },
      });

      const stdout = result.stdout.toString();
      expect(stdout).toContain('<system-reminder>');
      expect(stdout).toContain('</system-reminder>');
      expect(stdout).toContain('PAI CORE CONTEXT');
      expect(stdout).toContain('Personal context here');
    });

    test('outputs warning system-reminder when PAI skill missing', async () => {
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
        },
      });

      const stdout = result.stdout.toString();
      expect(stdout).toContain('<system-reminder>');
      expect(stdout).toContain('PAI Context Loading Warning');
      expect(stdout).toContain('PAI skill file not found');
    });

    test('outputs stderr warning when PAI skill missing', async () => {
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
        },
      });

      const stderr = result.stderr.toString();
      expect(stderr).toContain('PAI skill not found');
    });
  });

  describe('path resolution', () => {
    test('finds PAI skill at PAI_DIR/.claude/skills/PAI/SKILL.md', async () => {
      // Setup: Standard repo layout
      const skillPath = join(tempDir, '.claude', 'skills', 'PAI');
      mkdirSync(skillPath, { recursive: true });
      writeFileSync(join(skillPath, 'SKILL.md'), '# Repo Layout Test');

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
        },
      });

      expect(result.exitCode).toBe(0);
      expect(result.stdout.toString()).toContain('Repo Layout Test');
    });

    test('finds PAI skill at PAI_DIR/skills/PAI/SKILL.md when PAI_DIR ends with .claude', async () => {
      // Setup: PAI_DIR points directly to .claude directory
      const claudeDir = join(tempDir, '.claude');
      mkdirSync(claudeDir, { recursive: true });

      const skillPath = join(claudeDir, 'skills', 'PAI');
      mkdirSync(skillPath, { recursive: true });
      writeFileSync(join(skillPath, 'SKILL.md'), '# Direct .claude Test');

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: claudeDir, // Points to .claude directory
        },
      });

      expect(result.exitCode).toBe(0);
      expect(result.stdout.toString()).toContain('Direct .claude Test');
    });
  });

  describe('subagent detection', () => {
    test('skips PAI context for sessions with CLAUDE_AGENT_TYPE set', async () => {
      // Setup: Create PAI skill file
      const skillPath = join(tempDir, '.claude', 'skills', 'PAI');
      mkdirSync(skillPath, { recursive: true });
      writeFileSync(join(skillPath, 'SKILL.md'), '# Should not appear');

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
          CLAUDE_AGENT_TYPE: 'task',
        },
      });

      expect(result.exitCode).toBe(0);
      // Should not output PAI content for subagent
      expect(result.stdout.toString()).not.toContain('Should not appear');
      expect(result.stderr.toString()).toContain('Subagent session');
    });

    test('skips PAI context when CLAUDE_PROJECT_DIR contains /.claude/agents/', async () => {
      const skillPath = join(tempDir, '.claude', 'skills', 'PAI');
      mkdirSync(skillPath, { recursive: true });
      writeFileSync(join(skillPath, 'SKILL.md'), '# Should not appear');

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', join(import.meta.dir, '../session-start/load-core-context.ts')],
        env: {
          ...process.env,
          PAI_DIR: tempDir,
          CLAUDE_PROJECT_DIR: '/some/path/.claude/agents/task-123',
        },
      });

      expect(result.exitCode).toBe(0);
      expect(result.stdout.toString()).not.toContain('Should not appear');
    });
  });
});

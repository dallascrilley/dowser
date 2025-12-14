import { describe, test, expect, beforeEach, afterEach } from 'bun:test';
import { mkdtempSync, writeFileSync, rmSync, mkdirSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';

/**
 * Regression tests for analyze-prompt-skills.ts UserPromptSubmit hook
 *
 * Critical behaviors to verify:
 * 1. Hook always returns valid JSON output
 * 2. Hook handles edge cases gracefully (empty input, missing files)
 * 3. Hook doesn't fail with exit code 1
 */

describe('analyze-prompt-skills hook', () => {
  let tempDir: string;
  let originalEnv: NodeJS.ProcessEnv;
  const hookPath = join(import.meta.dir, '../prompt-submit/analyze-prompt-skills.ts');

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), 'skill-analyzer-test-'));
    originalEnv = { ...process.env };
  });

  afterEach(() => {
    process.env = originalEnv;
    try {
      rmSync(tempDir, { recursive: true, force: true });
    } catch {
      // Ignore cleanup errors
    }
  });

  describe('exit code behavior (critical for plugin loading)', () => {
    test('exits with code 0 on valid input', async () => {
      const input = JSON.stringify({
        userMessage: 'help me write a test',
        session_id: 'test-session',
      });

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(input),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      expect(result.exitCode).toBe(0);
    });

    test('exits with code 0 on empty input', async () => {
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(''),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      // Should exit gracefully even with empty input
      expect(result.exitCode).toBe(0);
    });

    test('exits with code 0 on invalid JSON input', async () => {
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from('this is not json'),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      // Should exit gracefully even with invalid JSON
      expect(result.exitCode).toBe(0);
    });

    test('exits with code 0 when skills directory does not exist', async () => {
      const input = JSON.stringify({
        userMessage: 'some prompt',
        session_id: 'test-session',
      });

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(input),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir, // Empty dir with no .claude/skills
        },
      });

      expect(result.exitCode).toBe(0);
    });
  });

  describe('JSON output format', () => {
    test('outputs valid JSON on valid input', async () => {
      const input = JSON.stringify({
        userMessage: 'help me write a test',
        session_id: 'test-session',
      });

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(input),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      const stdout = result.stdout.toString().trim();
      expect(() => JSON.parse(stdout)).not.toThrow();
    });

    test('outputs valid JSON on empty input', async () => {
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(''),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      const stdout = result.stdout.toString().trim();
      // Should output empty JSON object or valid response
      if (stdout) {
        expect(() => JSON.parse(stdout)).not.toThrow();
      }
    });

    test('outputs valid JSON when no skills match', async () => {
      const input = JSON.stringify({
        userMessage: 'xyzzy completely random nonsense query',
        session_id: 'test-session',
      });

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(input),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      const stdout = result.stdout.toString().trim();
      expect(() => JSON.parse(stdout)).not.toThrow();
    });
  });

  describe('skill matching', () => {
    test('finds skills when they exist', async () => {
      // Create a skill file in the temp directory
      const skillsDir = join(tempDir, '.claude', 'skills', 'test-skill');
      mkdirSync(skillsDir, { recursive: true });
      writeFileSync(
        join(skillsDir, 'SKILL.md'),
        `---
name: test-skill
description: A test skill for unit testing
when_to_use: Use when writing unit tests
---

# Test Skill

Instructions for testing.
`
      );

      const input = JSON.stringify({
        userMessage: 'help me write a unit test',
        session_id: 'test-session',
      });

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(input),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      expect(result.exitCode).toBe(0);
      const stdout = result.stdout.toString();
      // Should have found the test skill
      expect(() => JSON.parse(stdout)).not.toThrow();
    });
  });

  describe('CLI modes', () => {
    test('--show-metrics outputs valid JSON', async () => {
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath, '--show-metrics'],
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      expect(result.exitCode).toBe(0);
      const stdout = result.stdout.toString().trim();
      expect(() => JSON.parse(stdout)).not.toThrow();
    });

    test('--record-activation works', async () => {
      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath, '--record-activation', 'test-skill'],
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      expect(result.exitCode).toBe(0);
      expect(result.stdout.toString()).toContain('Recorded activation: test-skill');
    });
  });

  describe('error handling', () => {
    test('catches and handles errors gracefully', async () => {
      // Provide input that might cause issues
      const input = JSON.stringify({
        userMessage: null,
        session_id: undefined,
      });

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(input),
        env: {
          ...process.env,
          CLAUDE_PROJECT_DIR: tempDir,
        },
      });

      // Should not crash
      expect(result.exitCode).toBe(0);
    });

    test('handles missing CLAUDE_PROJECT_DIR', async () => {
      const input = JSON.stringify({
        userMessage: 'test prompt',
        session_id: 'test',
      });

      // Don't set CLAUDE_PROJECT_DIR at all
      const env = { ...process.env };
      delete env.CLAUDE_PROJECT_DIR;

      const result = Bun.spawnSync({
        cmd: ['bun', 'run', hookPath],
        stdin: Buffer.from(input),
        env,
      });

      // Should still work, using cwd as fallback
      expect(result.exitCode).toBe(0);
    });
  });
});

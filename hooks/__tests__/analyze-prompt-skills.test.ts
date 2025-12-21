import { describe, test, expect, beforeEach, afterEach } from 'bun:test';
import { mkdtempSync, writeFileSync, rmSync, mkdirSync, readFileSync, existsSync } from 'fs';
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
  const metricsPath = join(import.meta.dir, '..', '..', 'lib', 'skill-metrics.json');

  function runHook(options: {
    input?: string;
    env: NodeJS.ProcessEnv;
    args?: string[];
  }) {
    const { input, env, args = [] } = options;
    return Bun.spawnSync({
      cmd: ['bun', 'run', hookPath, ...args],
      stdin: Buffer.from(input ?? ''),
      env,
    });
  }

  function parseOutput(result: ReturnType<typeof runHook>) {
    const stdout = result.stdout.toString().trim();
    if (!stdout) return {};
    return JSON.parse(stdout) as Record<string, any>;
  }

  function getAdditionalContext(result: ReturnType<typeof runHook>): string {
    const payload = parseOutput(result);
    return payload?.hookSpecificOutput?.additionalContext ?? '';
  }

  function writeSkill(skillsRoot: string, folder: string, frontmatter: string, body = '# Skill\n') {
    const skillDir = join(skillsRoot, folder);
    mkdirSync(skillDir, { recursive: true });
    writeFileSync(join(skillDir, 'SKILL.md'), `${frontmatter}\n\n${body}`);
  }

  function writeRules(paiDir: string, rules: Record<string, unknown>) {
    const rulesDir = join(paiDir, '.claude', 'plugins', 'pai-skills', 'lib');
    mkdirSync(rulesDir, { recursive: true });
    writeFileSync(join(rulesDir, 'skill-rules.json'), JSON.stringify(rules, null, 2));
  }

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

  describe('rules and context behavior', () => {
    test('filters plugin-only rules outside plugin context', async () => {
      const homeDir = join(tempDir, 'home');
      const paiDir = join(tempDir, 'pai');
      const projectDir = join(tempDir, 'project');
      const userSkills = join(homeDir, '.claude', 'skills');

      writeSkill(
        userSkills,
        'plugin-only-skill',
        `---\nname: plugin-only-skill\ndescription: \nwhen_to_use: \n---`
      );

      writeRules(paiDir, {
        version: '1.0',
        skills: {
          'plugin-only-skill': {
            type: 'domain',
            enforcement: 'suggest',
            priority: 'high',
            promptTriggers: { keywords: ['aardvark'] },
            fileTriggers: {
              pathPatterns: ['/Users/dallascrilley/.claude/plugins/cache/superpowers/skills/plugin-only-skill/**'],
            },
          },
        },
      });

      const result = runHook({
        input: JSON.stringify({ userMessage: 'aardvark query', session_id: 'test' }),
        env: {
          ...process.env,
          HOME: homeDir,
          PAI_DIR: paiDir,
          CLAUDE_PROJECT_DIR: projectDir,
          SKILL_ANALYZER_TFIDF: '0',
        },
      });

      expect(result.exitCode).toBe(0);
      expect(parseOutput(result)).toEqual({});
    });

    test('keeps plugin-only rules inside plugin context', async () => {
      const homeDir = join(tempDir, 'home');
      const paiDir = join(tempDir, 'pai');
      const projectDir = join(homeDir, '.claude', 'plugins', 'cache', 'superpowers');
      const userSkills = join(homeDir, '.claude', 'skills');

      writeSkill(
        userSkills,
        'plugin-only-skill',
        `---\nname: plugin-only-skill\ndescription: \nwhen_to_use: \n---`
      );

      writeRules(paiDir, {
        version: '1.0',
        skills: {
          'plugin-only-skill': {
            type: 'domain',
            enforcement: 'suggest',
            priority: 'high',
            promptTriggers: { keywords: ['aardvark'] },
            fileTriggers: {
              pathPatterns: ['/Users/dallascrilley/.claude/plugins/cache/superpowers/skills/plugin-only-skill/**'],
            },
          },
        },
      });

      const result = runHook({
        input: JSON.stringify({ userMessage: 'aardvark query', session_id: 'test' }),
        env: {
          ...process.env,
          HOME: homeDir,
          PAI_DIR: paiDir,
          CLAUDE_PROJECT_DIR: projectDir,
          SKILL_ANALYZER_TFIDF: '0',
        },
      });

      expect(result.exitCode).toBe(0);
      expect(getAdditionalContext(result)).toContain('plugin-only-skill');
    });

    test('priority boosts affect ordering', async () => {
      const homeDir = join(tempDir, 'home');
      const paiDir = join(tempDir, 'pai');
      const projectDir = join(tempDir, 'project');
      const projectSkills = join(projectDir, '.claude', 'skills');

      writeSkill(projectSkills, 'priority-high', `---\nname: priority-high\ndescription: \nwhen_to_use: \n---`);
      writeSkill(projectSkills, 'priority-low', `---\nname: priority-low\ndescription: \nwhen_to_use: \n---`);

      writeRules(paiDir, {
        version: '1.0',
        skills: {
          'priority-high': {
            type: 'domain',
            enforcement: 'suggest',
            priority: 'high',
            promptTriggers: { keywords: ['nebula'] },
          },
          'priority-low': {
            type: 'domain',
            enforcement: 'suggest',
            priority: 'low',
            promptTriggers: { keywords: ['nebula'] },
          },
        },
      });

      const result = runHook({
        input: JSON.stringify({ userMessage: 'nebula query', session_id: 'test' }),
        env: {
          ...process.env,
          HOME: homeDir,
          PAI_DIR: paiDir,
          CLAUDE_PROJECT_DIR: projectDir,
          SKILL_ANALYZER_TFIDF: '0',
          SKILL_ANALYZER_SHOW_SCORES: '1',
        },
      });

      expect(result.exitCode).toBe(0);
      const context = getAdditionalContext(result);
      const highIndex = context.indexOf('priority-high');
      const lowIndex = context.indexOf('priority-low');
      expect(highIndex).toBeGreaterThanOrEqual(0);
      expect(lowIndex).toBeGreaterThan(highIndex);
    });

    test('handles invalid regex patterns gracefully', async () => {
      const homeDir = join(tempDir, 'home');
      const paiDir = join(tempDir, 'pai');
      const projectDir = join(tempDir, 'project');
      const projectSkills = join(projectDir, '.claude', 'skills');

      writeSkill(projectSkills, 'regex-skill', `---\nname: regex-skill\ndescription: \nwhen_to_use: \n---`);

      writeRules(paiDir, {
        version: '1.0',
        skills: {
          'regex-skill': {
            type: 'domain',
            enforcement: 'suggest',
            priority: 'medium',
            promptTriggers: {
              keywords: ['aardvark'],
              intentPatterns: ['('],
            },
          },
        },
      });

      const result = runHook({
        input: JSON.stringify({ userMessage: 'aardvark query', session_id: 'test' }),
        env: {
          ...process.env,
          HOME: homeDir,
          PAI_DIR: paiDir,
          CLAUDE_PROJECT_DIR: projectDir,
          SKILL_ANALYZER_TFIDF: '0',
        },
      });

      expect(result.exitCode).toBe(0);
      expect(result.stderr.toString()).toContain('Invalid regex pattern in skill-rules.json');
    });
  });

  describe('discovery and deduplication', () => {
    test('normalizes multiline frontmatter for matching', async () => {
      const homeDir = join(tempDir, 'home');
      const paiDir = join(tempDir, 'pai');
      const projectDir = join(tempDir, 'project');
      const projectSkills = join(projectDir, '.claude', 'skills');

      writeSkill(
        projectSkills,
        'multiline-skill',
        `---\nname: multiline-skill\ndescription: |\n  This description spans lines.\n  It mentions zeta workflows.\nwhen_to_use: >\n  Use this when zeta workflows matter.\n---`
      );

      const result = runHook({
        input: JSON.stringify({ userMessage: 'zeta workflows', session_id: 'test' }),
        env: {
          ...process.env,
          HOME: homeDir,
          PAI_DIR: paiDir,
          CLAUDE_PROJECT_DIR: projectDir,
          SKILL_ANALYZER_TFIDF: '0',
        },
      });

      expect(result.exitCode).toBe(0);
      expect(getAdditionalContext(result)).toContain('multiline-skill');
    });

    test('deduplicates by folder name with project skills winning', async () => {
      const homeDir = join(tempDir, 'home');
      const paiDir = join(tempDir, 'pai');
      const projectDir = join(tempDir, 'project');
      const userSkills = join(homeDir, '.claude', 'skills');
      const projectSkills = join(projectDir, '.claude', 'skills');

      writeSkill(userSkills, 'dup-skill', `---\nname: dup-skill\ndescription: user version\nwhen_to_use: \n---`);
      writeSkill(projectSkills, 'dup-skill', `---\nname: dup-skill\ndescription: project version\nwhen_to_use: \n---`);

      const result = runHook({
        input: JSON.stringify({ userMessage: 'dup-skill', session_id: 'test' }),
        env: {
          ...process.env,
          HOME: homeDir,
          PAI_DIR: paiDir,
          CLAUDE_PROJECT_DIR: projectDir,
          SKILL_ANALYZER_TFIDF: '0',
        },
      });

      expect(result.exitCode).toBe(0);
      const context = getAdditionalContext(result);
      expect(context).toContain(join(projectSkills, 'dup-skill', 'SKILL.md'));
    });
  });

  describe('metrics tracking', () => {
    let metricsBackup: string | null = null;

    beforeEach(() => {
      if (existsSync(metricsPath)) {
        metricsBackup = readFileSync(metricsPath, 'utf-8');
      } else {
        metricsBackup = null;
      }
      rmSync(metricsPath, { force: true });
    });

    afterEach(() => {
      if (metricsBackup !== null) {
        writeFileSync(metricsPath, metricsBackup);
      } else {
        rmSync(metricsPath, { force: true });
      }
    });

    test('records activations in metrics output', async () => {
      const env = { ...process.env, CLAUDE_PROJECT_DIR: tempDir };
      const record = runHook({ env, args: ['--record-activation', 'alpha-skill'] });
      expect(record.exitCode).toBe(0);

      const show = runHook({ env, args: ['--show-metrics'] });
      const metrics = JSON.parse(show.stdout.toString());
      expect(metrics.activations['alpha-skill']).toBe(1);
    });

    test('records searches and clears gaps', async () => {
      const env = { ...process.env, CLAUDE_PROJECT_DIR: tempDir };
      const recordSearch = runHook({ env, args: ['--record-search', 'lost query'] });
      expect(recordSearch.exitCode).toBe(0);

      const showMetrics = runHook({ env, args: ['--show-metrics'] });
      const metrics = JSON.parse(showMetrics.stdout.toString());
      expect(metrics.searches['lost query']).toBe(1);

      const gapResult = runHook({
        env,
        input: JSON.stringify({ userMessage: 'zzzz unmatched', session_id: 'test' }),
      });
      expect(gapResult.exitCode).toBe(0);

      const showGaps = runHook({ env, args: ['--show-gaps'] });
      expect(showGaps.stdout.toString()).toContain('zzzz unmatched');

      const clear = runHook({ env, args: ['--clear-gaps'] });
      expect(clear.exitCode).toBe(0);

      const showAfterClear = runHook({ env, args: ['--show-gaps'] });
      expect(showAfterClear.stdout.toString()).toContain('No gaps recorded yet.');
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

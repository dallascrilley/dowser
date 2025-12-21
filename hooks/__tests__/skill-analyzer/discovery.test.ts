import { describe, test, expect, beforeEach, afterEach } from 'bun:test';
import { mkdtempSync, rmSync, mkdirSync, writeFileSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { discoverSkillsCached } from '../../prompt-submit/skill-analyzer/discovery';

describe('skill discovery', () => {
  let root = '';

  beforeEach(() => {
    root = mkdtempSync(join(tmpdir(), 'discovery-test-'));
  });

  afterEach(() => {
    rmSync(root, { recursive: true, force: true });
  });

  test('discovers a skill from SKILL.md', async () => {
    const skillDir = join(root, 'skills', 'coding', 'my-skill');
    mkdirSync(skillDir, { recursive: true });
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      ['---', 'name: My Skill', 'description: Hello', 'when_to_use: Use it', '---', '', '# Body'].join('\n')
    );

    const skills = await discoverSkillsCached(join(root, 'skills'), 'project');
    expect(skills.some((s) => s.folderName === 'my-skill')).toBe(true);
  });
});

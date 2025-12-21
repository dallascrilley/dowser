import { describe, test, expect } from 'bun:test';
import { scoreSkillRelevanceHybrid } from '../../prompt-submit/skill-analyzer/hybrid';
import type { Skill } from '../../prompt-submit/skill-analyzer/types';

describe('hybrid scoring', () => {
  test('returns 0 when nothing matches', () => {
    const skill: Skill = {
      name: 'Some Skill',
      path: '/tmp/some-skill/SKILL.md',
      description: 'nope',
      whenToUse: 'nope',
      relativePath: 'skills/x',
      folderName: 'some-skill',
      sourceType: 'plugin',
    };
    const out = scoreSkillRelevanceHybrid(skill, 'zzz', null, new Map(), new Map(), new Map());
    expect(out.score).toBe(0);
  });
});

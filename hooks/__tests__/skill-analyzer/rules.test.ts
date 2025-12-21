import { describe, test, expect } from 'bun:test';
import { scoreSkillFromRules, type SkillRules } from '../../prompt-submit/skill-analyzer/rules';
import type { Skill } from '../../prompt-submit/skill-analyzer/types';

describe('rules scoring', () => {
  test('returns > 0 when keyword matches', () => {
    const skill: Skill = {
      name: 'Optimizing Performance',
      path: '/tmp/x',
      description: 'perf stuff',
      whenToUse: 'when optimizing',
      relativePath: 'skills/coding/optimizing-performance',
      folderName: 'optimizing-performance',
      sourceType: 'plugin',
    };

    const rules: SkillRules = {
      skills: {
        'Optimizing Performance': {
          promptTriggers: { keywords: ['performance'] },
        },
      },
    };

    expect(scoreSkillFromRules(skill, 'improve performance', rules)).toBeGreaterThan(0);
  });
});

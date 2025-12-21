import { describe, test, expect } from 'bun:test';
import { scoreSkillsWithFuse } from '../../prompt-submit/skill-analyzer/fuse';
import type { Skill } from '../../prompt-submit/skill-analyzer/types';

describe('fuse scoring', () => {
  test('returns non-empty score map and includes skill names', () => {
    const skills: Skill[] = [
      {
        name: 'Optimizing Performance',
        path: '/tmp/optimizing-performance/SKILL.md',
        description: 'Improve performance',
        whenToUse: 'When app is slow',
        relativePath: 'skills/coding/optimizing-performance',
        folderName: 'optimizing-performance',
        sourceType: 'plugin',
      },
    ];

    const scores = scoreSkillsWithFuse(skills, 'performance');
    expect(scores.get('Optimizing Performance')?.fuseScore).toBeDefined();
  });
});

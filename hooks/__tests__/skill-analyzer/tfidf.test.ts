import { describe, test, expect } from 'bun:test';
import { scoreSkillsWithTfIdf } from '../../prompt-submit/skill-analyzer/tfidf';
import type { Skill } from '../../prompt-submit/skill-analyzer/types';

describe('tfidf scoring', () => {
  test('returns a Map with all skills as keys', () => {
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
      {
        name: 'Writing Tests',
        path: '/tmp/writing-tests/SKILL.md',
        description: 'Testing guidance',
        whenToUse: 'When adding tests',
        relativePath: 'skills/coding/testing',
        folderName: 'writing-tests',
        sourceType: 'plugin',
      },
    ];
    const scores = scoreSkillsWithTfIdf(skills, 'performance');
    expect(scores.size).toBe(2);
    expect(scores.has('Optimizing Performance')).toBe(true);
    expect(scores.has('Writing Tests')).toBe(true);
  });
});

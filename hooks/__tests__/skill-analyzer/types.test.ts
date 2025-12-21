import { describe, test, expect } from 'bun:test';

import { SKILL_SOURCE_TYPES } from '../../prompt-submit/skill-analyzer/types';

describe('skill-analyzer types', () => {
  test('exports SKILL_SOURCE_TYPES for runtime use', () => {
    expect(SKILL_SOURCE_TYPES).toEqual(['project', 'user', 'plugin']);
  });
});

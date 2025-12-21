import { describe, test, expect } from 'bun:test';

import { tokenize, levenshteinDistance, scoreFuzzyMatch } from '../../prompt-submit/skill-analyzer/tokenize';

describe('tokenize + fuzzy', () => {
  test('tokenize splits and lowercases', () => {
    expect(tokenize('Hello, WORLD!')).toEqual(['hello', 'world']);
  });

  test('levenshteinDistance basic cases', () => {
    expect(levenshteinDistance('kitten', 'sitting')).toBe(3);
    expect(levenshteinDistance('a', 'a')).toBe(0);
  });

  test('scoreFuzzyMatch maps distance to score', () => {
    expect(scoreFuzzyMatch(0, 2)).toBeGreaterThan(scoreFuzzyMatch(1, 2));
    expect(scoreFuzzyMatch(2, 2)).toBeGreaterThanOrEqual(0);
  });
});

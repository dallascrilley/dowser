import type Fuse from 'fuse.js';
import { CONFIG } from '../../../lib/config';
import type { Skill } from './types';
import type { SkillRules } from './rules';
import { scoreSkillFromRules } from './rules';
import { scoreSkillRelevanceFuzzy } from './tokenize';

export function scoreSkillRelevanceHybrid(
  skill: Skill,
  prompt: string,
  rules: SkillRules | null,
  fuseScores: Map<string, { fuseScore: number; fuseMatch: Fuse.FuseResult<Skill> | null }>,
  tfidfScores: Map<string, number>,
  semanticScores: Map<string, number>
): { score: number; source: 'rules' | 'fuzzy' | 'fuse' | 'tfidf' | 'semantic' | 'hybrid' } {
  const rulesScore = scoreSkillFromRules(skill, prompt, rules);
  const fuzzyScore = scoreSkillRelevanceFuzzy(skill, prompt);
  const fuseData = fuseScores.get(skill.name) || { fuseScore: 0, fuseMatch: null };
  const tfidfScore = tfidfScores.get(skill.name) || 0;
  const semanticScore = semanticScores.get(skill.name) || 0;

  // If skill has rules and matched, prioritize rules-based score
  if (rulesScore > 0) {
    // Add bonuses from fuzzy, fuse, TF-IDF, and semantic matching
    const hybridScore = rulesScore +
      Math.floor(fuzzyScore * CONFIG.WEIGHTS.hybridBonuses.whenRulesMatch.fuzzy) +
      Math.floor(fuseData.fuseScore * CONFIG.WEIGHTS.hybridBonuses.whenRulesMatch.fuse) +
      Math.floor(tfidfScore * CONFIG.WEIGHTS.hybridBonuses.whenRulesMatch.tfidf) +
      Math.floor(semanticScore * 0.3);
    return {
      score: hybridScore,
      source: (fuzzyScore > 0 || fuseData.fuseScore > 0 || tfidfScore > 0 || semanticScore > 0) ? 'hybrid' : 'rules'
    };
  }

  // Combine token-based, Fuse.js, TF-IDF, and semantic scores
  let combinedScore: number;
  let source: 'fuzzy' | 'fuse' | 'tfidf' | 'semantic' | 'hybrid';

  // Find the maximum base score
  const scores = [
    { value: fuzzyScore, name: 'fuzzy' as const },
    { value: fuseData.fuseScore, name: 'fuse' as const },
    { value: tfidfScore, name: 'tfidf' as const },
    { value: semanticScore, name: 'semantic' as const }
  ].sort((a, b) => b.value - a.value);

  const primary = scores[0];
  const secondary = scores[1];
  const tertiary = scores[2];

  if (primary.value === 0) {
    return { score: 0, source: 'fuzzy' };
  }

  // Primary score with weighted secondary and tertiary contributions
  combinedScore = primary.value +
    Math.floor(secondary.value * CONFIG.WEIGHTS.hybridBonuses.whenNoRules.secondary) +
    Math.floor(tertiary.value * CONFIG.WEIGHTS.hybridBonuses.whenNoRules.tertiary);

  // Determine source label based on score combination
  if (secondary.value > 0) {
    source = 'hybrid';
  } else {
    source = primary.name;
  }

  return { score: combinedScore, source };
}

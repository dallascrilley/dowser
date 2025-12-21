import type { Skill } from './types';

/**
 * Format skills for display
 */
export function formatSkillSuggestions(
  skills: Skill[],
  scoredSkills?: Array<{ skill: Skill; score: number; source?: string }>
): string {
  if (skills.length === 0) return '';

  const showScores = process.env.SKILL_ANALYZER_SHOW_SCORES === '1';
  const lines = ['📚 Relevant skills detected:'];

  for (const skill of skills) {
    let scoreText = '';
    if (showScores && scoredSkills) {
      const scored = scoredSkills.find(s => s.skill.name === skill.name);
      if (scored) {
        const sourceIcon = scored.source === 'rules'
          ? '📋'
          : scored.source === 'semantic'
            ? '🧠'
            : scored.source === 'fuse'
              ? '🔎'
              : scored.source === 'fuzzy'
                ? '🔍'
                : scored.source === 'tfidf'
                  ? '📊'
                  : '🔀';
        scoreText = ` [score: ${scored.score}${scored.source ? `, ${sourceIcon} ${scored.source}` : ''}]`;
      }
    }

    const desc = skill.description ? `: ${skill.description}` : '';
    lines.push(`  • ${skill.name}${scoreText}${desc}`);
    lines.push(`    Path: ${skill.path}`);
  }

  if (showScores && scoredSkills && scoredSkills.length > skills.length) {
    lines.push('');
    lines.push(`  (Showing top ${skills.length} of ${scoredSkills.length} matched skills)`);
  }

  return lines.join('\n');
}

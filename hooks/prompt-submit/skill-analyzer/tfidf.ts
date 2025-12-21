import { TfIdf } from 'natural';
import type { Skill } from './types';

type TfIdfCache = {
  tfidf: TfIdf;
  corpusKey: string;
};

let tfidfCache: TfIdfCache | null = null;

/** TF-IDF scoring is ON by default. Disable via SKILL_ANALYZER_TFIDF=0 */
const TFIDF_ENABLED = process.env.SKILL_ANALYZER_TFIDF !== '0';
/** Debug TF-IDF scoring via SKILL_ANALYZER_DEBUG_TFIDF=1 */
const DEBUG_TFIDF_ENABLED = process.env.SKILL_ANALYZER_DEBUG_TFIDF === '1';

/**
 * Build or get cached TF-IDF instance from skills corpus
 * TF-IDF weights terms by uniqueness: common terms like "implement" get low weight,
 * rare terms like "tailwind" get high weight
 */
function getTfIdfInstance(skills: Skill[]): TfIdf {
  const currentHash = skills
    .map((skill) => [
      skill.name,
      skill.folderName,
      skill.description || '',
      skill.whenToUse || '',
    ].join('\u0000'))
    .join('\u0001');

  if (tfidfCache && tfidfCache.corpusKey === currentHash) {
    return tfidfCache.tfidf;
  }

  if (DEBUG_TFIDF_ENABLED) {
    console.error(`\n🔬 Building TF-IDF corpus from ${skills.length} skills`);
  }

  const tfidfInstance = new TfIdf();

  // Add each skill as a document with combined searchable text
  for (const skill of skills) {
    const doc = [
      skill.name,
      skill.folderName,
      skill.description || '',
      skill.whenToUse || ''
    ].join(' ').toLowerCase();

    tfidfInstance.addDocument(doc);
  }

  tfidfCache = { tfidf: tfidfInstance, corpusKey: currentHash };

  if (DEBUG_TFIDF_ENABLED) {
    console.error(`✓ TF-IDF corpus built with ${skills.length} documents`);
  }

  return tfidfInstance;
}

/**
 * Get TF-IDF weighted scores for query against all skills
 * Returns map of skill name -> TF-IDF score
 */
export function scoreSkillsWithTfIdf(skills: Skill[], query: string): Map<string, number> {
  const results = new Map<string, number>();

  // Initialize all skills with 0
  for (const skill of skills) {
    results.set(skill.name, 0);
  }

  if (!TFIDF_ENABLED || !query || query.length < 2) {
    return results;
  }

  const tfidf = getTfIdfInstance(skills);
  const queryLower = query.toLowerCase();

  if (DEBUG_TFIDF_ENABLED) {
    console.error(`\n📊 TF-IDF scores for: "${query}"`);
  }

  // TF-IDF returns scores per document
  // Higher score = query terms appear frequently in doc but rarely across corpus
  let maxScore = 0;
  const rawScores: number[] = [];

  tfidf.tfidfs(queryLower, (i: number, measure: number) => {
    rawScores[i] = measure;
    if (measure > maxScore) maxScore = measure;
  });

  // Normalize scores to 0-25 range (similar weight to other scoring methods)
  for (let i = 0; i < skills.length; i++) {
    const skill = skills[i];
    const rawScore = rawScores[i] || 0;
    const normalizedScore = maxScore > 0 ? Math.round((rawScore / maxScore) * 25) : 0;
    const previousScore = results.get(skill.name) || 0;
    results.set(skill.name, Math.max(previousScore, normalizedScore));

    if (DEBUG_TFIDF_ENABLED && normalizedScore > 0) {
      console.error(`  ${skill.name}: raw=${rawScore.toFixed(3)}, normalized=${normalizedScore}`);
    }
  }

  return results;
}

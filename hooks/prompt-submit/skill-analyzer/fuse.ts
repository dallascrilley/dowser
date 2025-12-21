import Fuse from 'fuse.js';
import { CONFIG } from '../../../lib/config';
import type { Skill } from './types';

/**
 * Fuse.js configuration for fuzzy search
 * - threshold: CONFIG.FUZZY_THRESHOLD allows reasonable typos (lower = stricter matching)
 * - distance: 100 allows matches anywhere in the string
 * - minMatchCharLength: 2 for short queries like "ai", "db"
 */
const FUSE_OPTIONS: Fuse.IFuseOptions<Skill> = {
  keys: [
    { name: 'name', weight: CONFIG.WEIGHTS.fuseKeys.name },
    { name: 'folderName', weight: CONFIG.WEIGHTS.fuseKeys.folderName },
    { name: 'description', weight: CONFIG.WEIGHTS.fuseKeys.description },
    { name: 'whenToUse', weight: CONFIG.WEIGHTS.fuseKeys.whenToUse },
  ],
  threshold: CONFIG.FUZZY_THRESHOLD, // 0 = perfect match, 1 = match anything
  distance: 100,           // How far apart characters can be
  minMatchCharLength: 2,   // Enable short queries
  includeScore: true,      // Get match scores
  ignoreLocation: true,    // Don't penalize matches later in string
  useExtendedSearch: true, // Enable advanced search patterns
};

let fuseInstance: Fuse<Skill> | null = null;
let fuseSkillsHash: string = '';

/**
 * Get or create Fuse.js instance for skill search
 * Lazily initialized and cached
 */
function getFuseInstance(skills: Skill[]): Fuse<Skill> {
  // Create hash of skills to check if we need to rebuild
  const hash = skills.map(s => s.name).sort().join('|');
  
  if (fuseInstance && fuseSkillsHash === hash) {
    return fuseInstance;
  }
  
  // Rebuild Fuse index
  fuseInstance = new Fuse(skills, FUSE_OPTIONS);
  fuseSkillsHash = hash;
  
  return fuseInstance;
}

/**
 * Score skills using Fuse.js fuzzy search
 * Returns scores normalized to a 0-20 contribution scale
 */
export function scoreSkillsWithFuse(
  skills: Skill[],
  query: string
): Map<string, { fuseScore: number; fuseMatch: Fuse.FuseResult<Skill> | null }> {
  const debugFuzzy = process.env.SKILL_ANALYZER_DEBUG_FUZZY === '1';
  const results = new Map<string, { fuseScore: number; fuseMatch: Fuse.FuseResult<Skill> | null }>();
  
  // Initialize all skills with 0 score
  for (const skill of skills) {
    results.set(skill.name, { fuseScore: 0, fuseMatch: null });
  }
  
  if (!query || query.length < 2) {
    return results;
  }
  
  const fuse = getFuseInstance(skills);
  
  // Fuse.js search returns results sorted by score (lower is better)
  // Score of 0 = perfect match, 1 = no match
  const fuseResults = fuse.search(query);
  
  if (debugFuzzy && fuseResults.length > 0) {
    console.error(`\n🔎 Fuse.js results for "${query}":`);
  }
  
  for (const result of fuseResults) {
    // Convert Fuse score (0=best, 1=worst) to our scale (higher=better)
    // Score of 0.0 → 20 points, 0.2 → 16, 0.4 → 12, 0.6 → 8, 0.8 → 4
    const normalizedScore = Math.round((1 - (result.score || 0)) * 20);
    
    results.set(result.item.name, { fuseScore: normalizedScore, fuseMatch: result });
    
    if (debugFuzzy) {
      console.error(`  ${result.item.name}: raw=${result.score?.toFixed(3)}, normalized=${normalizedScore}`);
    }
  }
  
  return results;
}

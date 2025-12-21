import type { Skill } from './types';

const MAX_FUZZY_DISTANCE = 2;
const DEBUG_FUZZY_ENABLED = process.env.SKILL_ANALYZER_DEBUG_FUZZY === '1';

/**
 * Common words to exclude from tokenization
 * These cause too many false positives in skill matching
 */
const EXCLUDED_TOKENS = new Set([
  'use', 'using',     // Too generic
  'the', 'and', 'for', 'with', 'this', 'that',  // Stop words
  'help', 'please', 'want', 'need',  // Request words
]);

/**
 * Overly common tokens that should receive REDUCED weight (not excluded)
 * These appear in many skill descriptions and cause false positives
 * when they match skill names via partial matching
 */
const LOW_WEIGHT_TOKENS = new Set([
  'implement', 'implementing', 'implementation',  // Matches "implementing-modules" too broadly
  'create', 'creating', 'build', 'building',      // Very generic action words
  'make', 'making', 'setup', 'setting',
  'add', 'adding', 'write', 'writing',
  'how', 'what', 'when', 'where', 'why',          // Question words
  'best', 'good', 'better',                        // Quality words
  'new', 'old', 'update', 'change',
]);

/**
 * Short technical tokens (2 chars) that should be kept despite length filter
 * These are meaningful in technical contexts
 */
const SHORT_TECHNICAL_TOKENS = new Set([
  'ai', 'ui', 'ux', 'db', 'ci', 'cd', 'qa', 'pr', 'mr', 'vm', 'os', 'io',
  'js', 'ts', 'py', 'go', 'rs', 'rb',  // Languages
  'ws', 'fs', 'kv',  // Tech abbreviations
]);

/**
 * Acronym expansions - map common acronyms to their full forms
 * Allows "tdd" to match "test-driven-development"
 */
const ACRONYM_EXPANSIONS: Record<string, string[]> = {
  'tdd': ['test-driven-development', 'test driven development', 'test-driven'],
  'bdd': ['behavior-driven-development', 'behavior driven development'],
  'api': ['application programming interface', 'rest api', 'graphql'],
  'sdk': ['software development kit'],
  'cli': ['command line interface', 'command-line'],
  'gui': ['graphical user interface'],
  'ux': ['user experience', 'user-experience'],
  'ui': ['user interface', 'user-interface'],
  'ci': ['continuous integration'],
  'cd': ['continuous deployment', 'continuous delivery'],
  'cicd': ['continuous integration', 'continuous deployment'],
  'db': ['database', 'databases'],
  'sql': ['structured query language', 'database'],
  'orm': ['object relational mapping', 'database'],
  'jwt': ['json web token', 'authentication', 'auth'],
  'oauth': ['authentication', 'auth', 'authorization'],
  'ssr': ['server side rendering', 'server-side-rendering'],
  'ssg': ['static site generation', 'static-site-generation'],
  'spa': ['single page application', 'single-page-application'],
  'pwa': ['progressive web app', 'progressive-web-app'],
  'mcp': ['model context protocol'],
  'llm': ['large language model', 'ai', 'language model'],
  'rag': ['retrieval augmented generation', 'retrieval-augmented-generation'],
  'crud': ['create read update delete'],
  'rest': ['representational state transfer', 'api'],
  'grpc': ['remote procedure call', 'api'],
  'ws': ['websocket', 'websockets', 'real-time'],
  'wss': ['websocket', 'websockets', 'secure websocket'],
  'k8s': ['kubernetes'],
  'tf': ['terraform', 'infrastructure'],
  'aws': ['amazon web services', 'cloud'],
  'gcp': ['google cloud platform', 'cloud'],
  'cf': ['cloudflare'],
};

/**
 * Synonym/related term expansions for better semantic matching
 * Bidirectional - "debug" finds skills mentioning "troubleshoot" and vice versa
 */
const SYNONYM_GROUPS: string[][] = [
  ['debug', 'debugging', 'troubleshoot', 'troubleshooting', 'fix', 'fixing', 'error', 'errors', 'bug', 'bugs'],
  ['test', 'testing', 'tests', 'spec', 'specs', 'unit', 'integration', 'e2e'],
  ['plan', 'planning', 'design', 'designing', 'architect', 'architecture'],
  ['deploy', 'deployment', 'deploying', 'ship', 'shipping', 'release', 'releasing'],
  ['build', 'building', 'create', 'creating', 'make', 'making', 'implement', 'implementing'],
  ['refactor', 'refactoring', 'cleanup', 'clean', 'simplify', 'simplifying'],
  ['auth', 'authentication', 'login', 'signin', 'sign-in', 'authorization'],
  ['perf', 'performance', 'optimize', 'optimization', 'speed', 'fast'],
  ['docs', 'documentation', 'document', 'documenting', 'readme'],
  ['config', 'configuration', 'configure', 'configuring', 'setup', 'setting'],
  ['validate', 'validation', 'validating', 'verify', 'verification', 'check'],
  ['parse', 'parsing', 'extract', 'extracting', 'transform', 'transforming'],
  ['fetch', 'fetching', 'request', 'requesting', 'call', 'calling', 'invoke'],
  ['store', 'storing', 'save', 'saving', 'persist', 'persisting', 'cache', 'caching'],
  ['format', 'formatting', 'style', 'styling', 'lint', 'linting'],
];

// Build reverse lookup for synonyms
const SYNONYM_MAP = new Map<string, Set<string>>();
for (const group of SYNONYM_GROUPS) {
  const groupSet = new Set(group);
  for (const term of group) {
    SYNONYM_MAP.set(term, groupSet);
  }
}

/**
 * Meta keywords that indicate the prompt is about skills/agents/Claude Code
 * When these appear, we should NOT exclude 'skill'/'skills' from tokenization
 */
const META_CONTEXT_KEYWORDS = new Set([
  'create', 'creator', 'write', 'writer', 'build', 'builder', 'make', 'maker',  // Creating skills
  'new', 'update', 'edit', 'modify',  // Modifying skills
  'claude', 'agent', 'agents', 'subagent', 'subagents',  // Claude Code agents
  'plugin', 'plugins', 'hook', 'hooks', 'mcp',  // Claude Code ecosystem
  'meta', 'garden', 'gardening', 'wiki', 'index',  // Meta/maintenance
  'convert', 'docs', 'documentation',  // Skill creation from docs
  'testing', 'test',  // Testing skills
  'ai', 'llm', 'prompt', 'prompts',  // AI/LLM related
]);

/**
 * Check if prompt is about meta/skill topics
 */
function isMetaSkillContext(promptLower: string): boolean {
  for (const keyword of META_CONTEXT_KEYWORDS) {
    if (promptLower.includes(keyword)) {
      return true;
    }
  }
  return false;
}

/**
 * Expand acronyms and add synonyms to a token list
 * Returns expanded tokens that should be searched for
 */
function expandTokens(tokens: string[]): string[] {
  const expanded = new Set<string>(tokens);

  for (const token of tokens) {
    // Expand acronyms
    const acronymExpansions = ACRONYM_EXPANSIONS[token];
    if (acronymExpansions) {
      for (const expansion of acronymExpansions) {
        // Add both full expansion and individual words
        expanded.add(expansion);
        for (const word of expansion.split(/[\s-]+/)) {
          if (word.length >= 3) expanded.add(word);
        }
      }
    }

    // Add synonyms
    const synonyms = SYNONYM_MAP.get(token);
    if (synonyms) {
      for (const synonym of synonyms) {
        expanded.add(synonym);
      }
    }
  }

  return [...expanded];
}

/**
 * Normalize and tokenize text for matching
 * Excludes common words that cause false positives
 * Context-aware: keeps 'skill'/'skills' for meta-skill queries
 * Expands acronyms and synonyms for better matching
 */
export function tokenize(text: string, keepSkillTokens: boolean = false): string[] {
  const rawTokens = text
    .toLowerCase()
    .replace(/[^\w\s-]/g, ' ')  // Replace punctuation with spaces
    .split(/\s+/)
    .filter(t => t.length >= 2);  // Allow 2-char tokens initially

  // Filter tokens
  const filteredTokens = rawTokens.filter(t => {
    if (EXCLUDED_TOKENS.has(t)) return false;
    // Only exclude 'skill'/'skills' if NOT in meta context
    if (!keepSkillTokens && (t === 'skill' || t === 'skills')) return false;
    // Keep 2-char tokens only if they're technical abbreviations
    if (t.length === 2 && !SHORT_TECHNICAL_TOKENS.has(t)) return false;
    return true;
  });

  // Expand acronyms and synonyms
  const expandedTokens = expandTokens(filteredTokens);

  return [...new Set(expandedTokens)];
}

/**
 * Calculate Levenshtein distance between two strings
 * Uses dynamic programming with O(n*m) time, O(min(n,m)) space
 */
export function levenshteinDistance(a: string, b: string): number {
  if (a === b) return 0;
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;

  // Ensure a is shorter for space optimization
  if (a.length > b.length) [a, b] = [b, a];

  const row: number[] = Array.from({ length: a.length + 1 }, (_, i) => i);

  for (let i = 1; i <= b.length; i++) {
    let prev = i;
    for (let j = 1; j <= a.length; j++) {
      const val = b[i - 1] === a[j - 1]
        ? row[j - 1]
        : Math.min(row[j - 1], prev, row[j]) + 1;
      row[j - 1] = prev;
      prev = val;
    }
    row[a.length] = prev;
  }

  return row[a.length];
}

/**
 * Score a fuzzy match based on edit distance
 * Distance 0 = 8 points, 1 = 6 points, 2 = 4 points, 3+ = 0 points
 */
export function scoreFuzzyMatch(distance: number, maxDistance: number = MAX_FUZZY_DISTANCE): number {
  if (distance > maxDistance) return 0;
  return Math.max(0, 8 - distance * 2);
}

/**
 * Tokenize skill name by splitting on spaces, hyphens, and underscores
 * Filters out short tokens (< 3 chars) to avoid noise
 */
export function tokenizeSkillName(name: string): string[] {
  return name
    .toLowerCase()
    .split(/[\s\-_]+/)  // Split on spaces, hyphens, underscores
    .filter(token => token.length >= 3);  // Filter short tokens
}

/**
 * Score a skill's relevance to a prompt using fuzzy matching
 * This is the original PAI scoring logic
 */
export function scoreSkillRelevanceFuzzy(skill: Skill, prompt: string): number {
  const promptLower = prompt.toLowerCase();
  const isMetaContext = isMetaSkillContext(promptLower);
  const promptTokens = tokenize(prompt, isMetaContext);  // Keep 'skill' tokens in meta context
  let score = 0;

  // Check name match (highest weight) - bidirectional
  const nameLower = skill.name.toLowerCase();
  if (promptLower.includes(nameLower)) {
    // Full skill name appears in prompt (e.g., prompt: "use brainstorming ideas into designs")
    score += 10;
  } else if (nameLower.includes(promptLower) && promptLower.length >= 4) {
    // Search term appears in skill name (e.g., prompt: "brainstorming" matches "Brainstorming Ideas Into Designs")
    // Require at least 4 chars to avoid false positives with short terms
    score += 8;
  } else {
    // Check if any token from prompt is contained in skill name
    for (const token of promptTokens) {
      if (nameLower.includes(token) && token.length >= 4) {
        // Reduce weight for overly common tokens
        const tokenWeight = LOW_WEIGHT_TOKENS.has(token) ? 2 : 6;
        score += tokenWeight;  // Token match in name
        break;  // Only count once
      }
    }
  }

  // Check folder name match (very high weight for exact match)
  const folderLower = skill.folderName.toLowerCase();
  if (folderLower === promptLower) {
    // Exact folder name match (e.g., prompt: "brainstorming" matches folder "brainstorming")
    score += 12;
  } else if (promptTokens.some(token => token === folderLower && !LOW_WEIGHT_TOKENS.has(token))) {
    // Token exactly matches folder name (e.g., "use brainstorming skill" has token "brainstorming")
    // Skip low-weight tokens for exact folder match bonus
    score += 12;
  } else if (folderLower.includes(promptLower) && promptLower.length >= 4) {
    // Partial folder match (full prompt in folder)
    score += 6;
  } else {
    // Check if any token is contained in folder name or vice versa
    for (const token of promptTokens) {
      if ((folderLower.includes(token) || token.includes(folderLower)) && token.length >= 4) {
        // Reduce weight for overly common tokens in folder matching
        const tokenWeight = LOW_WEIGHT_TOKENS.has(token) ? 1 : 4;
        score += tokenWeight;  // Partial folder match
        break;
      }
    }
  }

  // Partial name token matches
  const nameTokens = tokenizeSkillName(skill.name);
  for (const token of promptTokens) {
    if (nameTokens.some(nt => nt.includes(token) || token.includes(nt))) {
      // Reduce weight for overly common tokens
      const tokenWeight = LOW_WEIGHT_TOKENS.has(token) ? 1 : 3;
      score += tokenWeight;
    }
  }

  // Fuzzy matching: Check edit distance between prompt tokens and full skill name
  // Only applies if no exact match found above
  const nameMatchScore = score;
  if (nameMatchScore === 0) {
    for (const token of promptTokens) {
      const distance = levenshteinDistance(token, nameLower);
      const fuzzyScore = scoreFuzzyMatch(distance);
      if (fuzzyScore > 0) {
        score += fuzzyScore;
        if (DEBUG_FUZZY_ENABLED) {
          console.error(`    Fuzzy match (full name): "${token}" ~ "${nameLower}" (distance: ${distance}, score: +${fuzzyScore})`);
        }
        break; // Only count best fuzzy match for full name
      }
    }
  }

  // Fuzzy matching for individual name tokens (compound names)
  if (score < 5) { // Low score threshold to activate
    for (const nameToken of nameTokens) {
      if (nameToken.length < 3) continue;
      for (const promptToken of promptTokens) {
        const distance = levenshteinDistance(promptToken, nameToken);
        const fuzzyScore = scoreFuzzyMatch(distance);
        if (fuzzyScore > 0) {
          const partialFuzzyScore = Math.floor(fuzzyScore / 2); // Half weight for partial name fuzzy match
          score += partialFuzzyScore;
          if (DEBUG_FUZZY_ENABLED) {
            console.error(`    Fuzzy match (name token): "${promptToken}" ~ "${nameToken}" (distance: ${distance}, score: +${partialFuzzyScore})`);
          }
        }
      }
    }
  }

  // Description scoring with word frequency consideration
  if (skill.description) {
    const descLower = skill.description.toLowerCase();
    const matchedTokens = new Set<string>();

    for (const token of promptTokens) {
      if (descLower.includes(token) && !matchedTokens.has(token)) {
        score += 2; // Increased from 1
        matchedTokens.add(token);
      }
    }
  }

  // when_to_use scoring (higher weight - this is specifically for matching)
  if (skill.whenToUse) {
    const whenToUseLower = skill.whenToUse.toLowerCase();
    const matchedTokens = new Set<string>();

    for (const token of promptTokens) {
      if (whenToUseLower.includes(token) && !matchedTokens.has(token)) {
        score += 3; // Higher weight than description - when_to_use is intent-specific
        matchedTokens.add(token);
      }
    }
  }

  const descriptionLower = skill.description ? skill.description.toLowerCase() : '';
  const whenToUseLower = skill.whenToUse ? skill.whenToUse.toLowerCase() : '';

  // Check for keyword matches (expanded list)
  const keywords = [
    'test', 'testing', 'debug', 'debugging', 'deploy', 'deployment',
    'architecture', 'architect', 'database', 'db', 'postgres', 'sql',
    'api', 'rest', 'graphql', 'security', 'auth', 'authentication',
    'performance', 'optimize', 'design', 'refactor', 'refactoring',
    'cloudflare', 'worker', 'nextjs', 'react', 'typescript', 'python',
    'scrape', 'scraping', 'research', 'analyze', 'analysis', 'framework',
    'ai', 'llm', 'agent', 'automation', 'homeassistant', 'prompt',
    'skill', 'write', 'create', 'build', 'implement', 'fix', 'bug',
  ];

  for (const keyword of keywords) {
    if (promptLower.includes(keyword) &&
        (nameLower.includes(keyword) ||
         descriptionLower.includes(keyword) ||
         whenToUseLower.includes(keyword))) {
      score += 3;
    }
  }

  // Project-level skills get priority boost
  // These are skills defined in the current project's .claude/skills/ directory
  if (skill.sourceType === 'project') {
    score += 10;  // Significant boost to prioritize project-specific skills
  }

  return score;
}

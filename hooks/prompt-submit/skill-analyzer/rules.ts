import fs from 'fs';
import path from 'path';
import type { Skill } from './types';

export interface SkillRule {
  type?: 'domain' | 'guardrail';
  enforcement?: 'suggest' | 'block' | 'warn';
  priority?: 'critical' | 'high' | 'medium' | 'low';
  description?: string;
  promptTriggers?: {
    keywords?: string[];
    intentPatterns?: string[];
    compiledIntentRegexes?: RegExp[];
  };
  fileTriggers?: {
    pathPatterns?: string[];
    pathExclusions?: string[];
    contentPatterns?: string[];
  };
  blockMessage?: string;
  skipConditions?: {
    sessionSkillUsed?: boolean;
    fileMarkers?: string[];
    envOverride?: string;
  };
  isPluginRule?: boolean;
}

export interface SkillRules {
  version?: string;
  description?: string;
  skills?: Record<string, SkillRule>;
  globalConfig?: {
    enableFileTriggersForAllProjects?: boolean;
    cacheSkillRules?: boolean;
    debugMode?: boolean;
    respectSkillFinderDebugEnv?: boolean;
  };
  [key: string]: any;
}

interface SkillRulesCacheEntry {
  rules: SkillRules | null;
  mtime: number;
}

const rulesCache = new Map<string, SkillRulesCacheEntry>();

/** Enable rules debug output via SKILL_ANALYZER_DEBUG_RULES=1 */
const DEBUG_RULES_ENABLED = process.env.SKILL_ANALYZER_DEBUG_RULES === '1';

function compileIntentPatterns(patterns?: string[]): RegExp[] {
  if (!patterns?.length) return [];
  const compiled: RegExp[] = [];
  for (const pattern of patterns) {
    try {
      compiled.push(new RegExp(pattern, 'i'));
    } catch (error) {
      console.error(`⚠️  Invalid regex pattern in skill-rules.json: "${pattern}"`, error);
    }
  }
  return compiled;
}

/**
 * Load skill-rules.json with caching
 */
export function loadSkillRules(skillsRoot: string, isPluginContext: boolean): SkillRules | null {
  const rulesPath = path.join(skillsRoot, 'skill-rules.json');

  if (!fs.existsSync(rulesPath)) {
    return null;
  }

  try {
    const stat = fs.statSync(rulesPath);
    const cached = rulesCache.get(rulesPath);

    // Return cached if unchanged
    if (cached && cached.mtime === stat.mtimeMs) {
      return cached.rules;
    }

    // Load and parse
    const content = fs.readFileSync(rulesPath, 'utf-8');
    const rules = JSON.parse(content) as SkillRules;
    if (rules.skills) {
      for (const [name, rule] of Object.entries(rules.skills)) {
        if (rule.promptTriggers?.intentPatterns) {
          rule.promptTriggers.compiledIntentRegexes = compileIntentPatterns(rule.promptTriggers.intentPatterns);
        }
        const hasPluginPath = rule.fileTriggers?.pathPatterns?.some((pattern) =>
          pattern.includes('/.claude/plugins/cache/')
        );
        rule.isPluginRule = Boolean(hasPluginPath);
      }
      if (!isPluginContext) {
        for (const [name, rule] of Object.entries(rules.skills)) {
          if (rule.isPluginRule) {
            delete rules.skills[name];
          }
        }
      }
    }

    // Cache it
    rulesCache.set(rulesPath, {
      rules,
      mtime: stat.mtimeMs
    });

    if (DEBUG_RULES_ENABLED) {
      console.error(`✓ Loaded skill-rules.json from ${rulesPath}`);
      console.error(`  Found ${Object.keys(rules.skills || {}).length} skill rules`);
    }

    return rules;
  } catch (error) {
    console.error(`⚠️  Failed to load skill-rules.json from ${rulesPath}:`, error);
    return null;
  }
}

/**
 * Get priority score boost based on priority level
 */
function getPriorityBoost(priority?: string): number {
  switch (priority) {
    case 'critical': return 15;
    case 'high': return 10;
    case 'medium': return 5;
    case 'low': return 2;
    default: return 0;
  }
}

/**
 * Test if prompt matches any intent patterns
 */
function matchesIntentPatterns(promptLower: string, rule: SkillRule): boolean {
  const compiled = rule.promptTriggers?.compiledIntentRegexes;
  if (compiled?.length) {
    for (const regex of compiled) {
      if (regex.test(promptLower)) {
        if (DEBUG_RULES_ENABLED) {
          console.error(`    ✓ Intent pattern match: "${regex.source}"`);
        }
        return true;
      }
    }
    return false;
  }

  const rawPatterns = rule.promptTriggers?.intentPatterns;
  if (!rawPatterns?.length) {
    return false;
  }

  for (const pattern of rawPatterns) {
    try {
      const regex = new RegExp(pattern, 'i');
      if (regex.test(promptLower)) {
        if (DEBUG_RULES_ENABLED) {
          console.error(`    ✓ Intent pattern match (fallback): "${pattern}"`);
        }
        return true;
      }
    } catch (error) {
      console.error(`⚠️  Invalid regex pattern in skill-rules.json: "${pattern}"`, error);
    }
  }

  return false;
}

/**
 * Score skill based on skill-rules.json configuration
 * Returns 0 if no rules exist for this skill
 */
export function scoreSkillFromRules(skill: Skill, prompt: string, rules: SkillRules | null): number {
  if (!rules || !rules.skills) {
    return 0;
  }

  const skillRule = rules.skills[skill.name];
  if (!skillRule) {
    return 0; // No rules for this skill, fuzzy matching will handle it
  }

  let score = 0;
  const promptLower = prompt.toLowerCase();

  if (DEBUG_RULES_ENABLED) {
    console.error(`\n  📋 Checking rules for skill: ${skill.name}`);
  }

  // Check keyword matches
  if (skillRule.promptTriggers?.keywords) {
    for (const keyword of skillRule.promptTriggers.keywords) {
      if (promptLower.includes(keyword.toLowerCase())) {
        score += 8; // High weight for explicit keyword match
        if (DEBUG_RULES_ENABLED) {
          console.error(`    ✓ Keyword match: "${keyword}" (+8)`);
        }
      }
    }
  }

  // Check intent pattern matches
  if (skillRule.promptTriggers?.intentPatterns || skillRule.promptTriggers?.compiledIntentRegexes?.length) {
    if (matchesIntentPatterns(promptLower, skillRule)) {
      score += 6; // Medium weight for intent pattern match
      if (DEBUG_RULES_ENABLED) {
        console.error(`    ✓ Intent pattern matched (+6)`);
      }
    }
  }

  // Apply priority boost
  const priorityBoost = getPriorityBoost(skillRule.priority);
  if (priorityBoost > 0) {
    score += priorityBoost;
    if (DEBUG_RULES_ENABLED) {
      console.error(`    ✓ Priority boost (${skillRule.priority}): +${priorityBoost}`);
    }
  }

  if (DEBUG_RULES_ENABLED && score > 0) {
    console.error(`    Final rules-based score: ${score}`);
  }

  return score;
}

import fs from 'fs';
import path from 'path';
import { createHash } from 'crypto';
import { CONFIG } from '../../../lib/config';
import type { HookInput, Skill, SkillSourceType } from './types';
import { scoreSkillsWithTfIdf } from './tfidf';
import { scoreSkillRelevanceHybrid } from './hybrid';
import { scoreSkillsWithFuse } from './fuse';
import { GAP_THRESHOLD, recordGap, recordRichGap, formatGapWarning, recordSkillSuggestions, checkGapNotification } from './metrics';
import { loadSkillRules, type SkillRules } from './rules';
import { discoverSkillsCached } from './discovery';
import { formatSkillSuggestions } from './format';

const PROJECT_DIR = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const PLUGIN_CACHE_FRAGMENT = `${path.sep}.claude${path.sep}plugins${path.sep}cache`;
const isPluginContext =
  PROJECT_DIR.includes(PLUGIN_CACHE_FRAGMENT) ||
  PROJECT_DIR.includes('/.claude/plugins/cache/');

const PLUGIN_LIB_DIR = path.join(__dirname, '..', '..', '..', 'lib');
const SEMANTIC_CACHE_DIR = path.resolve(
  process.env.SKILL_ANALYZER_SEMANTIC_CACHE_DIR || PLUGIN_LIB_DIR
);
const SEMANTIC_MODEL_DIR = path.join(SEMANTIC_CACHE_DIR, 'models');

// Semantic Search Configuration
const SEMANTIC_ENABLED = process.env.SKILL_ANALYZER_SEMANTIC !== '0';
const EMBEDDING_MODEL = 'Xenova/all-MiniLM-L6-v2';
const EMBEDDINGS_FILE = path.join(SEMANTIC_CACHE_DIR, 'skill-embeddings.json');

interface EmbeddingCache {
  version: string;
  model: string;
  embeddings: Record<string, { embedding: number[]; hash: string }>;
  lastUpdated: string;
}

let extractor: any = null;
let transformersModule: null | { pipeline: any; env: any } = null;
let transformersLoadAttempted = false;
let transformersLoadError: unknown | null = null;
let loggedTransformersLoadError = false;

function ensureSemanticCacheDir(): void {
  try {
    fs.mkdirSync(SEMANTIC_CACHE_DIR, { recursive: true });
    fs.mkdirSync(SEMANTIC_MODEL_DIR, { recursive: true });
  } catch {
    // Best-effort; semantic search should degrade gracefully if cache is unwritable.
  }
}

async function loadTransformers(): Promise<{ pipeline: any; env: any } | null> {
  if (transformersModule) return transformersModule;
  if (transformersLoadAttempted) return null;

  transformersLoadAttempted = true;

  try {
    const mod = await import('@xenova/transformers');

    // Configure cache for semantic models (must happen after import so `env` exists).
    mod.env.cacheDir = SEMANTIC_MODEL_DIR;
    mod.env.allowLocalModels = false;

    transformersModule = { pipeline: mod.pipeline, env: mod.env };
    return transformersModule;
  } catch (error) {
    transformersLoadError = error;
    return null;
  }
}

async function getExtractor() {
  if (!extractor) {
    ensureSemanticCacheDir();
    const transformers = await loadTransformers();
    if (!transformers) {
      if (!loggedTransformersLoadError) {
        loggedTransformersLoadError = true;
        console.error('⚠️  Semantic search disabled: failed to load @xenova/transformers.');
        if (process.env.SKILL_ANALYZER_DEBUG === '1' && transformersLoadError) {
          console.error(transformersLoadError);
        }
      }
      return null;
    }

    extractor = await transformers.pipeline('feature-extraction', EMBEDDING_MODEL, {
      quantized: false,
    });
  }
  return extractor;
}

const SEMANTIC_QUERY_HINTS: Array<{ pattern: RegExp; hints: string[] }> = [
  { pattern: /\b(go faster|faster|speed up|speedup|make .*fast|run faster)\b/i, hints: ['performance', 'optimize', 'optimization', 'speed', 'fast', 'latency', 'throughput'] },
  { pattern: /\b(look good|make .*look good|polish|styling|style|css|ui|ux|design)\b/i, hints: ['ui', 'ux', 'styling', 'css', 'design', 'tailwind', 'shadcn', 'components'] },
  { pattern: /\b(code quality|ensure quality|quality gates?|lint|format|typecheck)\b/i, hints: ['lint', 'format', 'typecheck', 'tests', 'refactor', 'quality'] },
];

function expandSemanticQuery(query: string): { expanded: string; addedHints: string[] } {
  const added = new Set<string>();
  for (const { pattern, hints } of SEMANTIC_QUERY_HINTS) {
    if (!pattern.test(query)) continue;
    for (const hint of hints) added.add(hint);
  }

  if (added.size === 0) {
    return { expanded: query, addedHints: [] };
  }

  const hintText = [...added].join(' ');
  return { expanded: `${query}\n\n${hintText}`, addedHints: [...added] };
}

async function generateEmbedding(text: string): Promise<number[]> {
  const pipe = await getExtractor();
  if (!pipe) {
    throw new Error('Semantic search disabled (transformers unavailable)');
  }
  const output = await pipe(text, { pooling: 'mean', normalize: true });
  return Array.from(output.data);
}

function sha256(text: string): string {
  return createHash('sha256').update(text).digest('hex');
}

function getSkillEmbeddingCacheKey(skill: Skill): string {
  return skill.path;
}

function buildSkillEmbeddingText(skill: Skill): string {
  return `${skill.name}. ${skill.description || ''} ${skill.whenToUse || ''}`.trim();
}

function loadEmbeddingCache(): EmbeddingCache {
  ensureSemanticCacheDir();
  if (!fs.existsSync(EMBEDDINGS_FILE)) {
    return {
      version: '2.0',
      model: EMBEDDING_MODEL,
      embeddings: {},
      lastUpdated: new Date().toISOString()
    };
  }
  try {
    const parsed = JSON.parse(fs.readFileSync(EMBEDDINGS_FILE, 'utf-8')) as Partial<EmbeddingCache>;
    if (!parsed || parsed.version !== '2.0' || parsed.model !== EMBEDDING_MODEL || !parsed.embeddings) {
      return {
        version: '2.0',
        model: EMBEDDING_MODEL,
        embeddings: {},
        lastUpdated: new Date().toISOString()
      };
    }
    return parsed as EmbeddingCache;
  } catch {
    return {
      version: '2.0',
      model: EMBEDDING_MODEL,
      embeddings: {},
      lastUpdated: new Date().toISOString()
    };
  }
}

function saveEmbeddingCache(cache: EmbeddingCache) {
  ensureSemanticCacheDir();
  cache.lastUpdated = new Date().toISOString();
  fs.writeFileSync(EMBEDDINGS_FILE, JSON.stringify(cache, null, 2));
}

/**
 * Get all skill roots to search
 * Returns: { path: string, sourceType: 'project' | 'user' | 'plugin' }[]
 * Order: project skills last (so they win during deduplication)
 */
function getSkillRoots(): Array<{ path: string; sourceType: SkillSourceType }> {
  const roots: Array<{ path: string; sourceType: SkillSourceType }> = [];
  const homeDir = process.env.HOME || process.env.USERPROFILE || '';
  const paiDir = process.env.PAI_DIR || path.join(homeDir, 'PAI');
  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';

  // Default skills directory (~/.claude/skills) - user level
  const defaultSkillsDir = path.join(homeDir, '.claude', 'skills');
  if (fs.existsSync(defaultSkillsDir)) {
    roots.push({ path: defaultSkillsDir, sourceType: 'user' });
  }

  // PAI plugin skills directory (~/PAI/.claude/plugins/pai-skills/skills) - plugin level
  const paiPluginSkillsDir = path.join(paiDir, '.claude', 'plugins', 'pai-skills', 'skills');
  if (fs.existsSync(paiPluginSkillsDir)) {
    roots.push({ path: paiPluginSkillsDir, sourceType: 'plugin' });
  }

  // Recursively find all skills directories under ~/.claude/plugins
  // This catches: cache/<plugin>/skills, marketplaces/<marketplace>/skills, <plugin>/skills, etc.
  const pluginBase = path.join(homeDir, '.claude', 'plugins');
  if (fs.existsSync(pluginBase)) {
    const foundSkillDirs = new Set<string>();

    function findSkillsDirs(dir: string, depth = 0): void {
      // Limit recursion depth to avoid infinite loops and excessive scanning
      if (depth > 5) return;

      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
          if (!entry.isDirectory()) continue;

          const fullPath = path.join(dir, entry.name);

          // If this is a "skills" directory, add it
          if (entry.name === 'skills') {
            // Avoid duplicates (e.g., pai-skills already added above)
            if (!foundSkillDirs.has(fullPath) && fullPath !== paiPluginSkillsDir) {
              foundSkillDirs.add(fullPath);
              roots.push({ path: fullPath, sourceType: 'plugin' });
              if (debug) {
                console.error(`✓ Found plugin skills at ${fullPath}`);
              }
            }
          } else {
            // Recurse into subdirectories (but skip common non-skill directories)
            const skipDirs = [
              'node_modules', '.git', 'dist', 'build', 'coverage',
              'examples', 'test', 'tests', '__tests__', 'docs', 'references',
              'repos', 'marketplaces'  // repos contain source code, marketplaces are indexes
            ];
            // Skip temp directories (temp_git_*, temp_*)
            const isTempDir = entry.name.startsWith('temp_');
            if (!skipDirs.includes(entry.name) && !isTempDir) {
              findSkillsDirs(fullPath, depth + 1);
            }
          }
        }
      } catch {
        // Silently skip directories we can't read
      }
    }

    findSkillsDirs(pluginBase);
  }

  // Project-level skills directory ($CLAUDE_PROJECT_DIR/.claude/skills) - highest priority
  // Added LAST so project skills win during deduplication (later entries overwrite earlier)
  const projectSkillsDir = path.join(projectDir, '.claude', 'skills');
  if (fs.existsSync(projectSkillsDir) && projectSkillsDir !== defaultSkillsDir) {
    roots.push({ path: projectSkillsDir, sourceType: 'project' });
    if (debug) {
      console.error(`✓ Found project-level skills at ${projectSkillsDir}`);
    }
  }

  return roots;
}

/**
 * Get semantic similarity scores for skills
 */
async function scoreSkillsWithEmbeddings(skills: Skill[], query: string): Promise<Map<string, number>> {
  const results = new Map<string, number>();

  if (!SEMANTIC_ENABLED || !query || query.length < 3) {
    return results;
  }

  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';
  if (debug) console.error('🧠 Semantic Search: Generating query embedding...');

  try {
    const { expanded, addedHints } = expandSemanticQuery(query);
    if (debug && addedHints.length > 0) {
      console.error(`🧠 Semantic Search: Added intent hints: ${addedHints.join(', ')}`);
    }
    const queryEmbedding = await generateEmbedding(expanded);

    const cache = loadEmbeddingCache();
    let cacheDirty = false;
    const skillEmbeddings = new Map<string, number[]>();

    for (const skill of skills) {
      const cacheKey = getSkillEmbeddingCacheKey(skill);
      const text = buildSkillEmbeddingText(skill);
      const contentHash = sha256(text);
      const cached = cache.embeddings[cacheKey];

      if (cached?.embedding?.length && cached.hash === contentHash) {
        skillEmbeddings.set(cacheKey, cached.embedding);
        continue;
      }

      if (debug) {
        const reason = cached ? 'changed' : 'new';
        console.error(`   Generating embedding for ${reason} skill: ${skill.name}`);
      }
      const embedding = await generateEmbedding(text);
      cache.embeddings[cacheKey] = { embedding, hash: contentHash };
      skillEmbeddings.set(cacheKey, embedding);
      cacheDirty = true;
    }

    if (cacheDirty) {
      saveEmbeddingCache(cache);
    }

    for (const skill of skills) {
      const skillEmbedding = skillEmbeddings.get(getSkillEmbeddingCacheKey(skill));
      if (!skillEmbedding) continue;

      const similarity = cosineSimilarity(queryEmbedding, skillEmbedding);
      const normalizedScore = Math.max(0, Math.round((similarity - 0.12) * 150));

      results.set(skill.name, normalizedScore);

      if (debug && normalizedScore > 5) {
        console.error(`   ${skill.name}: similarity=${similarity.toFixed(3)}, normalized=${normalizedScore}`);
      }
    }
  } catch (error) {
    console.error('⚠️  Semantic search failed:', error);
  }

  return results;
}

function cosineSimilarity(a: number[], b: number[]): number {
  if (!a?.length || !b?.length) return 0;

  const len = Math.min(a.length, b.length);
  if (len === 0) return 0;

  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < len; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  if (normA === 0 || normB === 0) return 0;

  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  if (denom === 0) return 0;

  const similarity = dotProduct / denom;
  if (!Number.isFinite(similarity)) return 0;

  return Math.max(-1, Math.min(1, similarity));
}

/**
 * Find relevant skills for a prompt
 */
async function findRelevantSkills(prompt: string, limit = 3): Promise<{
  skills: Skill[];
  scoredSkills: Array<{ skill: Skill; score: number; source: string }>;
}> {
  const roots = getSkillRoots();
  const allSkills: Skill[] = [];
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';

  if (debug) {
    console.error('\n🔍 HYBRID DEBUG MODE ENABLED (Token + Fuse.js + Rules + Semantic)');
    console.error(`Searching skill roots: ${roots.map(r => `${r.path} (${r.sourceType})`).join(', ')}`);
  }

  // Load skill rules - prefer project rules, then PAI plugin lib, then first skills root
  const paiDir = process.env.PAI_DIR || path.join(process.env.HOME || '', 'PAI');
  const paiPluginRulesDir = path.join(paiDir, '.claude', 'plugins', 'pai-skills', 'lib');
  const projectRulesRoot = roots.find((root) => root.sourceType === 'project')?.path;
  let rules: SkillRules | null = null;
  if (projectRulesRoot && fs.existsSync(path.join(projectRulesRoot, 'skill-rules.json'))) {
    rules = loadSkillRules(projectRulesRoot, isPluginContext);
  } else if (fs.existsSync(path.join(paiPluginRulesDir, 'skill-rules.json'))) {
    rules = loadSkillRules(paiPluginRulesDir, isPluginContext);
  } else if (roots.length > 0) {
    rules = loadSkillRules(roots[0].path, isPluginContext);
  }

  if (debug && rules) {
    console.error(`✓ Loaded ${Object.keys(rules.skills || {}).length} skill rules`);
  }

  for (const root of roots) {
    const skills = await discoverSkillsCached(root.path, root.sourceType);
    if (debug) {
      console.error(`Found ${skills.length} skills in ${root.path}`);
    }
    allSkills.push(...skills);
  }

  // Deduplicate by folder name - later sources win (superpowers > pai-skills, project > all)
  // Folder name is consistent across sources (e.g., "using-git-worktrees" folder)
  // whereas display names may differ ("Using Git Worktrees" vs "using-git-worktrees")
  // Order: user → pai-skills → cache/superpowers → project (last wins)
  const seenFolders = new Map<string, number>();
  for (let i = 0; i < allSkills.length; i++) {
    const folder = allSkills[i].folderName.toLowerCase();
    // Last one wins (superpowers comes after pai-skills, project comes last)
    seenFolders.set(folder, i);
  }
  const uniqueIndices = new Set(seenFolders.values());
  const deduplicatedSkills = allSkills.filter((_, i) => uniqueIndices.has(i));

  if (debug && deduplicatedSkills.length < allSkills.length) {
    console.error(`Deduplicated: ${allSkills.length} → ${deduplicatedSkills.length} skills`);
  }
  allSkills.length = 0;
  allSkills.push(...deduplicatedSkills);

  if (allSkills.length === 0) {
    if (debug) console.error('⚠️  No skills found!');
    return { skills: [], scoredSkills: [] };
  }

  const [fuseScores, tfidfScores, semanticScores] = await Promise.all([
    Promise.resolve(scoreSkillsWithFuse(allSkills, prompt)),
    Promise.resolve(scoreSkillsWithTfIdf(allSkills, prompt)),
    scoreSkillsWithEmbeddings(allSkills, prompt)
  ]);

  const scoredSkills = allSkills
    .map((skill) => {
      const { score, source } = scoreSkillRelevanceHybrid(
        skill,
        prompt,
        rules,
        fuseScores,
        tfidfScores,
        semanticScores
      );
      return { skill, score, source };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score);

  // Debug: Show all scores
  if (debug) {
    console.error('\n📊 SKILL SCORES for prompt:', `"${prompt}"`);
    console.error('='.repeat(80));

    if (scoredSkills.length === 0) {
      console.error('No skills matched (all scores were 0)');
    } else {
      scoredSkills.slice(0, 10).forEach(({ skill, score, source }, index) => {
        const marker = index < limit ? '✓' : ' ';
        const sourceIcon = source === 'rules'
          ? '📋'
          : source === 'semantic'
            ? '🧠'
            : source === 'fuse'
              ? '🔎'
              : source === 'fuzzy'
                ? '🔍'
                : source === 'tfidf'
                  ? '📊'
                  : '🔀';
        console.error(`${marker} ${index + 1}. [Score: ${score}] ${sourceIcon} ${source.toUpperCase()} - ${skill.name}`);
        if (skill.description) {
          const desc = skill.description.length > 100
            ? skill.description.slice(0, 100) + '...'
            : skill.description;
          console.error(`      ${desc}`);
        }
      });
    }
    console.error('='.repeat(80));
    console.error(`Returning top ${limit} skills\n`);
  }

  return {
    skills: scoredSkills.slice(0, limit).map(({ skill }) => skill),
    scoredSkills
  };
}

export async function analyzeUserPrompt(data: HookInput): Promise<Record<string, unknown>> {
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';
  if (debug) {
    console.error('🔧 SKILL_ANALYZER_DEBUG=1 enabled');
  }

  // Claude Code sends userMessage, fallback to prompt for backwards compatibility
  const userPrompt = data.userMessage || data.prompt || '';

  if (!userPrompt) {
    return {};
  }

  // Analyze prompt for relevant skills
  const { skills: relevantSkills, scoredSkills } = await findRelevantSkills(userPrompt, 3);

  // Check if top match is below threshold (skill gap)
  const topScore = scoredSkills.length > 0 ? scoredSkills[0].score : 0;
  const isLowCoverage = topScore < GAP_THRESHOLD;
  if (isLowCoverage) {
    recordGap(userPrompt, topScore);
    recordRichGap(userPrompt, topScore, scoredSkills);
  }

  // Generate inline warning for low coverage
  const gapWarning = isLowCoverage
    ? formatGapWarning(userPrompt, topScore, scoredSkills)
    : '';

  // Check if we should notify about accumulated gaps
  const gapNotification = checkGapNotification();

  if (relevantSkills.length > 0) {
    recordSkillSuggestions(relevantSkills.map(skill => skill.name));
    const skillSummary = formatSkillSuggestions(relevantSkills, scoredSkills);

    // Output to stderr for console display
    console.error(skillSummary);
    if (gapWarning) {
      console.error(gapWarning);
    }
    if (gapNotification) {
      console.error(gapNotification);
    }

    // Return the skills as additional context
    let additionalContext = `\n\n${skillSummary}\n\nConsider using the Skill tool to load these skills if they're relevant to the task.`;
    if (gapWarning) {
      additionalContext += gapWarning;
    }
    if (gapNotification) {
      additionalContext += gapNotification;
    }

    return {
      hookSpecificOutput: {
        hookEventName: 'UserPromptSubmit',
        additionalContext,
      },
    };
  }

  if (gapWarning) {
    console.error(gapWarning);
  }
  if (gapNotification) {
    console.error(gapNotification);
  }

  // No skills found - return empty response
  return {};
}

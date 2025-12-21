#!/usr/bin/env bun
/**
 * Enhanced Skill Analyzer Hook for UserPromptSubmit
 * Hybrid System: Combines Fuse.js fuzzy matching, TF-IDF, and Semantic Search with declarative skill-rules.json
 *
 * Features:
 * - Fuse.js fuzzy search with configurable threshold (typo tolerance)
 * - TF-IDF term weighting for uniqueness
 * - Semantic Search (Embeddings) using @xenova/transformers
 * - Token-based exact matching for skill names and descriptions
 * - Keyword scoring for common technical terms
 * - Description relevance scoring with deduplication
 * - Process-lifetime caching with mtime-based invalidation
 * - skill-rules.json support for enforcement, priority, and intent patterns
 *
 * Configuration:
 * - SKILL_ANALYZER_DEBUG=1          Show all scores and matching details
 * - SKILL_ANALYZER_DEBUG_FUZZY=1    Show fuzzy match details
 * - SKILL_ANALYZER_SHOW_SCORES=1    Include scores in output
 * - SKILL_ANALYZER_DEBUG_RULES=1    Show rules.json matching details
 * - SKILL_ANALYZER_SEMANTIC=0       Disable semantic search (enabled by default)
 */

import { glob } from 'glob';
import matter from 'gray-matter';
import { createHash } from 'crypto';
import * as fs from 'fs';
import * as path from 'path';
import Fuse from 'fuse.js';
import { pipeline, env } from '@xenova/transformers';
import { CONFIG } from '../../lib/config';
import { scoreSkillsWithTfIdf } from './skill-analyzer/tfidf';
import { scoreSkillRelevanceHybrid } from './skill-analyzer/hybrid';
import { scoreSkillsWithFuse } from './skill-analyzer/fuse';
import { loadSkillRules, scoreSkillFromRules, type SkillRules } from './skill-analyzer/rules';

// Configure cache for models
const PLUGIN_LIB_DIR = path.join(__dirname, '..', '..', 'lib');
const SEMANTIC_CACHE_DIR = path.resolve(
  process.env.SKILL_ANALYZER_SEMANTIC_CACHE_DIR || PLUGIN_LIB_DIR
);
env.cacheDir = path.join(SEMANTIC_CACHE_DIR, 'models');
env.allowLocalModels = false;

interface HookInput {
  session_id?: string;
  prompt?: string;
  userMessage?: string;  // Claude Code sends this
  transcript_path?: string;
  hook_event_name?: string;
}

interface Skill {
  name: string;
  path: string;
  description: string;
  whenToUse: string;
  relativePath: string;
  folderName: string;  // Add folder name for matching
  sourceType: 'project' | 'user' | 'plugin';  // Where the skill came from
}

interface CacheEntry {
  skills: Skill[];
  dirMtime: number;  // Directory mtime for O(1) fast check
  fileStats: {        // File stats for precise invalidation
    maxMtime: number;
    count: number;
  };
}

const skillCache = new Map<string, CacheEntry>();
const PROJECT_DIR = process.env.CLAUDE_PROJECT_DIR || process.cwd();

const PREFER_PAI_SKILLS = process.env.SKILL_ANALYZER_PREFER_PAI_SKILLS !== '0';
const PAI_SKILLS_PRIORITY_BOOST = Number.parseInt(process.env.SKILL_ANALYZER_PAI_BOOST || '25', 10);
const MIN_SCORE_FOR_PAI_BOOST = Number.parseInt(
  process.env.SKILL_ANALYZER_PAI_BOOST_MIN_SCORE || String(CONFIG.GAP_THRESHOLD),
  10
);

// Semantic Search Configuration
const SEMANTIC_ENABLED = process.env.SKILL_ANALYZER_SEMANTIC !== '0';
const EMBEDDING_MODEL = 'Xenova/all-MiniLM-L6-v2';
const EMBEDDINGS_FILE = path.join(SEMANTIC_CACHE_DIR, 'skill-embeddings.json');

interface EmbeddingCache {
  version: string;
  model: string;
  embeddings: Record<string, { embedding: number[]; hash: string }>; // cacheKey -> embedding + content hash
  lastUpdated: string;
}

let extractor: any = null;

function ensureSemanticCacheDir(): void {
  try {
    fs.mkdirSync(SEMANTIC_CACHE_DIR, { recursive: true });
    fs.mkdirSync(env.cacheDir, { recursive: true });
  } catch {
    // Best-effort; semantic search should degrade gracefully if cache is unwritable.
  }
}

async function getExtractor() {
  if (!extractor) {
    ensureSemanticCacheDir();
    extractor = await pipeline('feature-extraction', EMBEDDING_MODEL, {
      quantized: false, // Use full precision for better quality
    });
  }
  return extractor;
}

const SEMANTIC_QUERY_HINTS: Array<{ pattern: RegExp; hints: string[] }> = [
  // Performance intent often comes in vague phrasing ("go faster") with no shared keywords.
  { pattern: /\b(go faster|faster|speed up|speedup|make .*fast|run faster)\b/i, hints: ['performance', 'optimize', 'optimization', 'speed', 'fast', 'latency', 'throughput'] },
  // Aesthetics/UI intent
  { pattern: /\b(look good|make .*look good|polish|styling|style|css|ui|ux|design)\b/i, hints: ['ui', 'ux', 'styling', 'css', 'design', 'tailwind', 'shadcn', 'components'] },
  // Quality intent
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
  const output = await pipe(text, { pooling: 'mean', normalize: true });
  return Array.from(output.data);
}

function sha256(text: string): string {
  return createHash('sha256').update(text).digest('hex');
}

function getSkillEmbeddingCacheKey(skill: Skill): string {
  // Skills can exist in multiple roots (project/user/plugin caches) with the same name.
  // Using the full path avoids collisions that silently corrupt semantic scoring.
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
    // 1. Generate query embedding
    const { expanded, addedHints } = expandSemanticQuery(query);
    if (debug && addedHints.length > 0) {
      console.error(`🧠 Semantic Search: Added intent hints: ${addedHints.join(', ')}`);
    }
    const queryEmbedding = await generateEmbedding(expanded);
    
    // 2. Load/Update skill embeddings
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

    // 3. Compute Cosine Similarity
    for (const skill of skills) {
      const skillEmbedding = skillEmbeddings.get(getSkillEmbeddingCacheKey(skill));
      if (!skillEmbedding) continue;

      const similarity = cosineSimilarity(queryEmbedding, skillEmbedding);
      
      // Normalize: Cosine is -1 to 1.
      // Usually 0.3 is "somewhat relevant", 0.7+ is "very relevant"
      // Map 0.2 -> 0, 0.8 -> 30 (high weight)
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

function isPaiSkillsSkill(skill: Skill): boolean {
  // Prefer the local PAI skills corpus over other installed plugin skills.
  // This keeps suggestions aligned with the PAI skill system even when other plugins
  // contain similarly relevant skills.
  return skill.path.includes(`${path.sep}pai-skills${path.sep}`);
}

function getPaiSkillBoost(skill: Skill, baseScore: number): number {
  if (!PREFER_PAI_SKILLS || PAI_SKILLS_PRIORITY_BOOST <= 0) return 0;
  if (!isPaiSkillsSkill(skill)) return 0;
  if (baseScore < MIN_SCORE_FOR_PAI_BOOST) return 0;
  return PAI_SKILLS_PRIORITY_BOOST;
}

const PLUGIN_CACHE_FRAGMENT = `${path.sep}.claude${path.sep}plugins${path.sep}cache`;
const isPluginContext =
  PROJECT_DIR.includes(PLUGIN_CACHE_FRAGMENT) ||
  PROJECT_DIR.includes('/.claude/plugins/cache/');

/**
 * Get metrics file path - uses plugin's lib directory
 * Metrics track how often each skill is suggested by the hook
 */
function getMetricsPath(): string {
  // Use plugin's lib directory for metrics (alongside skill-rules.json)
  const pluginLibDir = path.join(__dirname, '..', '..', 'lib');
  return path.join(pluginLibDir, 'skill-metrics.json');
}

const METRICS_FILE = getMetricsPath();
const METRICS_DIR = path.dirname(METRICS_FILE);


/** Maximum edit distance for fuzzy matching */

/** Enable fuzzy matching debug output via SKILL_ANALYZER_DEBUG_FUZZY=1 */

/** Enable rules debug output via SKILL_ANALYZER_DEBUG_RULES=1 */

/**
 * Load skill-rules.json with caching
 */

/**
 * Get priority score boost based on priority level
 */

/**
 * Test if prompt matches any intent patterns
 */

/**
 * Metrics structure for tracking skill usage
 */
interface SkillMetrics {
  suggestions: Record<string, number>;  // Hook suggested this skill
  activations: Record<string, number>;  // Skill was actually loaded via Skill tool
  searches: Record<string, number>;     // User searched for this (gap analysis)
  gaps: Record<string, number>;         // Low-relevance queries (potential missing skills)
  lastUpdated: string;
  lastGapNotification?: string;         // When we last notified about gaps
}

/** Minimum score for a skill to be considered a "good match" */
const GAP_THRESHOLD = CONFIG.GAP_THRESHOLD;

/** How many gap queries before we notify */
const GAP_NOTIFICATION_THRESHOLD = 10;

/** Minimum hours between gap notifications */
const GAP_NOTIFICATION_COOLDOWN_HOURS = 24;

function getEmptyMetrics(): SkillMetrics {
  return {
    suggestions: {},
    activations: {},
    searches: {},
    gaps: {},
    lastUpdated: new Date().toISOString()
  };
}

function loadMetrics(): SkillMetrics {
  if (!fs.existsSync(METRICS_FILE)) {
    return getEmptyMetrics();
  }
  try {
    const data = JSON.parse(fs.readFileSync(METRICS_FILE, 'utf-8'));
    // Handle legacy flat format (just skill: count)
    if (!data.suggestions && !data.activations) {
      // Migrate legacy data - assume all were suggestions
      return {
        suggestions: data,
        activations: {},
        searches: {},
        gaps: {},
        lastUpdated: new Date().toISOString()
      };
    }
    // Ensure gaps exists (may be missing from older format)
    if (!data.gaps) {
      data.gaps = {};
    }
    return data;
  } catch {
    return getEmptyMetrics();
  }
}

function saveMetrics(metrics: SkillMetrics): void {
  metrics.lastUpdated = new Date().toISOString();
  fs.writeFileSync(METRICS_FILE, JSON.stringify(metrics, null, 2));
}

/**
 * Record skill suggestions (from hook)
 */
function recordSkillSuggestions(skillNames: string[]): void {
  if (!skillNames.length) return;
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const metrics = loadMetrics();
    for (const name of skillNames) {
      metrics.suggestions[name] = (metrics.suggestions[name] || 0) + 1;
    }
    saveMetrics(metrics);
  } catch (error) {
    console.error('⚠️  Failed to record skill metrics:', error);
  }
}

/**
 * Record skill activation (when skill is loaded via Skill tool)
 * Called externally via: bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-activation "skill-name"
 */
function recordSkillActivation(skillName: string): void {
  if (!skillName) return;
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const metrics = loadMetrics();
    metrics.activations[skillName] = (metrics.activations[skillName] || 0) + 1;
    saveMetrics(metrics);
  } catch (error) {
    console.error('⚠️  Failed to record skill activation:', error);
  }
}

/**
 * Record search query (for gap analysis - what skills are users looking for?)
 * Called externally via: bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-search "query"
 */
function recordSearch(query: string): void {
  if (!query) return;
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const metrics = loadMetrics();
    metrics.searches[query] = (metrics.searches[query] || 0) + 1;
    saveMetrics(metrics);
  } catch (error) {
    console.error('⚠️  Failed to record search:', error);
  }
}

/**
 * Record a gap - query where best match was below threshold
 * These represent potential skills we should create
 */
function recordGap(query: string, bestScore: number): void {
  if (!query || query.length < 5) return; // Skip very short queries
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const metrics = loadMetrics();
    // Normalize query for deduplication (truncate to first 100 chars to avoid excessively long keys)
    const normalizedQuery = query.toLowerCase().trim().slice(0, 100);
    metrics.gaps[normalizedQuery] = (metrics.gaps[normalizedQuery] || 0) + 1;
    saveMetrics(metrics);
    if (debug) {
      console.error(`📉 Recorded gap: "${normalizedQuery}" (best score: ${bestScore})`);
    }
  } catch (error) {
    if (debug) {
      console.error('⚠️  Failed to record gap:', error);
    }
    // Non-critical - silently fail in normal operation
  }
}

/**
 * Rich gap entry with context for analysis
 */
interface RichGapEntry {
  query: string;
  bestScore: number;
  topMatches: Array<{ skill: string; score: number }>;
  timestamp: string;
}

const GAPS_LOG_PATH = path.join(METRICS_DIR, 'skill-gaps.jsonl');

/**
 * Record a rich gap entry to JSONL log for detailed analysis
 * Includes top matches to help identify what skills came close
 */
function recordRichGap(
  query: string,
  bestScore: number,
  scoredSkills: Array<{ skill: { name: string }; score: number }>
): void {
  if (!query || query.length < 5) return;
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const entry: RichGapEntry = {
      query: query.slice(0, 200),
      bestScore: Math.round(bestScore),
      topMatches: scoredSkills.slice(0, 3).map(s => ({
        skill: s.skill.name,
        score: Math.round(s.score)
      })),
      timestamp: new Date().toISOString(),
    };
    fs.appendFileSync(GAPS_LOG_PATH, JSON.stringify(entry) + '\n');
    if (debug) {
      console.error(`📊 Rich gap logged: ${entry.topMatches.length} close matches`);
    }
  } catch (error) {
    if (debug) {
      console.error('⚠️  Failed to record rich gap:', error);
    }
  }
}

/**
 * Format a warning message for low skill coverage
 */
function formatGapWarning(
  query: string,
  bestScore: number,
  scoredSkills: Array<{ skill: { name: string }; score: number }>
): string {
  const truncatedQuery = query.length > 60
    ? query.slice(0, 57) + '...' 
    : query;
  const matches = scoredSkills.slice(0, 3)
    .map(s => `${s.skill.name} (${Math.round(s.score)})`)
    .join(', ');

  return `\n⚠️ **Low skill coverage** (score: ${Math.round(bestScore)}/100)
   Query: "${truncatedQuery}"
   Closest: ${matches || 'none'}`;
}

/**
 * Check if we should notify about gaps and return notification message if so
 */
function checkGapNotification(): string | null {
  try {
    const metrics = loadMetrics();
    const totalGaps = Object.values(metrics.gaps).reduce((a, b) => a + b, 0);

    // Check if we have enough gaps to notify
    if (totalGaps < GAP_NOTIFICATION_THRESHOLD) {
      return null;
    }

    // Check cooldown
    if (metrics.lastGapNotification) {
      const lastNotification = new Date(metrics.lastGapNotification);
      const hoursSince = (Date.now() - lastNotification.getTime()) / (1000 * 60 * 60);
      if (hoursSince < GAP_NOTIFICATION_COOLDOWN_HOURS) {
        return null;
      }
    }

    // Generate notification
    const topGaps = Object.entries(metrics.gaps)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    if (topGaps.length === 0) {
      return null;
    }

    // Update last notification time
    metrics.lastGapNotification = new Date().toISOString();
    saveMetrics(metrics);

    const gapList = topGaps
      .map(([query, count]) => `  • "${query}" (${count}x)`) 
      .join('\n');

    return `\n⚠️ **Skill Gap Analysis** (${totalGaps} low-relevance queries detected)\n\nTop queries without good skill matches:\n${gapList}\n\nConsider creating skills for these topics. Run \`bun run scripts/view-metrics.ts --gaps\` for full list.`;
  } catch {
    return null;
  }
}

/**
 * Clear gaps after notification (optional - call after user acknowledges)
 */
function clearGaps(): void {
  try {
    const metrics = loadMetrics();
    metrics.gaps = {};
    saveMetrics(metrics);
  } catch {
    // Silently fail
  }
}

/**
 * Score skill based on skill-rules.json configuration
 * Returns 0 if no rules exist for this skill
 */
/** Maximum edit distance for fuzzy matching */

/** Enable fuzzy matching debug output via SKILL_ANALYZER_DEBUG_FUZZY=1 */

/** Enable rules debug output via SKILL_ANALYZER_DEBUG_RULES=1 */

/**
 * Load skill-rules.json with caching
 */

/**
 * Get priority score boost based on priority level
 */

/**
 * Test if prompt matches any intent patterns
 */

/**
 * Metrics structure for tracking skill usage
 */
interface SkillMetrics {
  suggestions: Record<string, number>;  // Hook suggested this skill
  activations: Record<string, number>;  // Skill was actually loaded via Skill tool
  searches: Record<string, number>;     // User searched for this (gap analysis)
  gaps: Record<string, number>;         // Low-relevance queries (potential missing skills)
  lastUpdated: string;
  lastGapNotification?: string;         // When we last notified about gaps
}

/** Minimum score for a skill to be considered a "good match" */
const GAP_THRESHOLD = CONFIG.GAP_THRESHOLD;

/** How many gap queries before we notify */
const GAP_NOTIFICATION_THRESHOLD = 10;

/** Minimum hours between gap notifications */
const GAP_NOTIFICATION_COOLDOWN_HOURS = 24;

function getEmptyMetrics(): SkillMetrics {
  return {
    suggestions: {},
    activations: {},
    searches: {},
    gaps: {},
    lastUpdated: new Date().toISOString()
  };
}

function loadMetrics(): SkillMetrics {
  if (!fs.existsSync(METRICS_FILE)) {
    return getEmptyMetrics();
  }
  try {
    const data = JSON.parse(fs.readFileSync(METRICS_FILE, 'utf-8'));
    // Handle legacy flat format (just skill: count)
    if (!data.suggestions && !data.activations) {
      // Migrate legacy data - assume all were suggestions
      return {
        suggestions: data,
        activations: {},
        searches: {},
        gaps: {},
        lastUpdated: new Date().toISOString()
      };
    }
    // Ensure gaps exists (may be missing from older format)
    if (!data.gaps) {
      data.gaps = {};
    }
    return data;
  } catch {
    return getEmptyMetrics();
  }
}

function saveMetrics(metrics: SkillMetrics): void {
  metrics.lastUpdated = new Date().toISOString();
  fs.writeFileSync(METRICS_FILE, JSON.stringify(metrics, null, 2));
}

/**
 * Record skill suggestions (from hook)
 */
function recordSkillSuggestions(skillNames: string[]): void {
  if (!skillNames.length) return;
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const metrics = loadMetrics();
    for (const name of skillNames) {
      metrics.suggestions[name] = (metrics.suggestions[name] || 0) + 1;
    }
    saveMetrics(metrics);
  } catch (error) {
    console.error('⚠️  Failed to record skill metrics:', error);
  }
}

/**
 * Record skill activation (when skill is loaded via Skill tool)
 * Called externally via: bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-activation "skill-name"
 */
function recordSkillActivation(skillName: string): void {
  if (!skillName) return;
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const metrics = loadMetrics();
    metrics.activations[skillName] = (metrics.activations[skillName] || 0) + 1;
    saveMetrics(metrics);
  } catch (error) {
    console.error('⚠️  Failed to record skill activation:', error);
  }
}

/**
 * Record search query (for gap analysis - what skills are users looking for?)
 * Called externally via: bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-search "query"
 */
function recordSearch(query: string): void {
  if (!query) return;
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const metrics = loadMetrics();
    metrics.searches[query] = (metrics.searches[query] || 0) + 1;
    saveMetrics(metrics);
  } catch (error) {
    console.error('⚠️  Failed to record search:', error);
  }
}

/**
 * Record a gap - query where best match was below threshold
 * These represent potential skills we should create
 */
function recordGap(query: string, bestScore: number): void {
  if (!query || query.length < 5) return; // Skip very short queries
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const metrics = loadMetrics();
    // Normalize query for deduplication (truncate to first 100 chars to avoid excessively long keys)
    const normalizedQuery = query.toLowerCase().trim().slice(0, 100);
    metrics.gaps[normalizedQuery] = (metrics.gaps[normalizedQuery] || 0) + 1;
    saveMetrics(metrics);
    if (debug) {
      console.error(`📉 Recorded gap: "${normalizedQuery}" (best score: ${bestScore})`);
    }
  } catch (error) {
    if (debug) {
      console.error('⚠️  Failed to record gap:', error);
    }
    // Non-critical - silently fail in normal operation
  }
}

/**
 * Rich gap entry with context for analysis
 */
interface RichGapEntry {
  query: string;
  bestScore: number;
  topMatches: Array<{ skill: string; score: number }>;
  timestamp: string;
}

const GAPS_LOG_PATH = path.join(METRICS_DIR, 'skill-gaps.jsonl');

/**
 * Record a rich gap entry to JSONL log for detailed analysis
 * Includes top matches to help identify what skills came close
 */
function recordRichGap(
  query: string,
  bestScore: number,
  scoredSkills: Array<{ skill: { name: string }; score: number }>
): void {
  if (!query || query.length < 5) return;
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';
  try {
    fs.mkdirSync(METRICS_DIR, { recursive: true });
    const entry: RichGapEntry = {
      query: query.slice(0, 200),
      bestScore: Math.round(bestScore),
      topMatches: scoredSkills.slice(0, 3).map(s => ({
        skill: s.skill.name,
        score: Math.round(s.score)
      })),
      timestamp: new Date().toISOString(),
    };
    fs.appendFileSync(GAPS_LOG_PATH, JSON.stringify(entry) + '\n');
    if (debug) {
      console.error(`📊 Rich gap logged: ${entry.topMatches.length} close matches`);
    }
  } catch (error) {
    if (debug) {
      console.error('⚠️  Failed to record rich gap:', error);
    }
  }
}

/**
 * Format a warning message for low skill coverage
 */
function formatGapWarning(
  query: string,
  bestScore: number,
  scoredSkills: Array<{ skill: { name: string }; score: number }>
): string {
  const truncatedQuery = query.length > 60
    ? query.slice(0, 57) + '...'
    : query;
  const matches = scoredSkills.slice(0, 3)
    .map(s => `${s.skill.name} (${Math.round(s.score)})`)
    .join(', ');

  return `\n⚠️ **Low skill coverage** (score: ${Math.round(bestScore)}/100)
   Query: "${truncatedQuery}"
   Closest: ${matches || 'none'}`;
}

/**
 * Check if we should notify about gaps and return notification message if so
 */
function checkGapNotification(): string | null {
  try {
    const metrics = loadMetrics();
    const totalGaps = Object.values(metrics.gaps).reduce((a, b) => a + b, 0);

    // Check if we have enough gaps to notify
    if (totalGaps < GAP_NOTIFICATION_THRESHOLD) {
      return null;
    }

    // Check cooldown
    if (metrics.lastGapNotification) {
      const lastNotification = new Date(metrics.lastGapNotification);
      const hoursSince = (Date.now() - lastNotification.getTime()) / (1000 * 60 * 60);
      if (hoursSince < GAP_NOTIFICATION_COOLDOWN_HOURS) {
        return null;
      }
    }

    // Generate notification
    const topGaps = Object.entries(metrics.gaps)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    if (topGaps.length === 0) {
      return null;
    }

    // Update last notification time
    metrics.lastGapNotification = new Date().toISOString();
    saveMetrics(metrics);

    const gapList = topGaps
      .map(([query, count]) => `  • "${query}" (${count}x)`)
      .join('\n');

    return `\n⚠️ **Skill Gap Analysis** (${totalGaps} low-relevance queries detected)\n\nTop queries without good skill matches:\n${gapList}\n\nConsider creating skills for these topics. Run \`bun run scripts/view-metrics.ts --gaps\` for full list.`;
  } catch {
    return null;
  }
}

/**
 * Clear gaps after notification (optional - call after user acknowledges)
 */
function clearGaps(): void {
  try {
    const metrics = loadMetrics();
    metrics.gaps = {};
    saveMetrics(metrics);
  } catch {
    // Silently fail
  }
}

/**
 * Score skill based on skill-rules.json configuration
 * Returns 0 if no rules exist for this skill
 */

/**
 * Normalize multiline YAML strings (from | or > block scalars)
 * Converts line breaks to spaces for consistent matching
 */
function normalizeMultilineString(str: string | undefined): string {
  if (typeof str !== 'string') return '';
  return str
    .replace(/\r\n/g, '\n')      // Normalize Windows line endings
    .replace(/\n+/g, ' ')         // Convert line breaks to spaces
    .replace(/\s+/g, ' ')         // Collapse multiple spaces
    .trim();
}

/**
 * Parse front matter from a SKILL.md file using gray-matter
 * Handles YAML block scalars (| and >) for multiline description/when_to_use
 */
function parseFrontMatter(content: string, defaultName: string): { name: string; description: string; whenToUse: string } {
  try {
    const { data } = matter(content);
    return {
      name: typeof data.name === 'string' && data.name.trim() ? data.name.trim() : defaultName,
      description: normalizeMultilineString(data.description),
      whenToUse: normalizeMultilineString(data.when_to_use),
    };
  } catch (error) {
    // Fallback to defaults if parsing fails
    return { name: defaultName, description: '', whenToUse: '' };
  }
}

/**
 * Discover all skills in a given root directory
 */
async function discoverSkills(root: string, sourceType: 'project' | 'user' | 'plugin' = 'plugin'): Promise<Skill[]> {
  const skills: Skill[] = [];
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';

  if (!fs.existsSync(root)) {
    return skills;
  }

  const pattern = path.join(root, '**/SKILL.md');
  const skillFiles = await glob(pattern, { nodir: true });

  // Parallel file reads with Promise.allSettled
  const results = await Promise.allSettled(
    skillFiles.map(async (skillFile) => {
      const content = await fs.promises.readFile(skillFile, 'utf-8');
      const dirPath = path.dirname(skillFile);
      const folderName = path.basename(dirPath);  // e.g., "brainstorming"
      const relativePath = path.relative(root, dirPath);

      const { name, description, whenToUse } = parseFrontMatter(content, folderName);

      return {
        name,
        path: skillFile,
        description,
        whenToUse,
        relativePath,
        folderName,
        sourceType,  // Track where skill came from
      };
    })
  );

  // Collect successful results
  for (const result of results) {
    if (result.status === 'fulfilled') {
      skills.push(result.value);
    } else if (debug) {
      console.error(`⚠️  Failed to parse skill:`, result.reason);
    }
  }

  return skills;
}

/**
 * Get directory mtime for O(1) fast cache check
 * Directory mtime changes when files are added/removed/renamed
 */
function getDirectoryMtime(root: string): number {
  try {
    const stats = fs.statSync(root);
    return stats.mtimeMs;
  } catch {
    return 0;
  }
}

/**
 * Get detailed file stats for skill files: max mtime and file count
 * - Max mtime catches content edits to any SKILL.md
 * - File count catches additions/deletions
 * This is O(n) expensive, only called when directory mtime changes
 */
async function getSkillFileStats(root: string): Promise<{ maxMtime: number; count: number }> {
  try {
    const pattern = path.join(root, '**/SKILL.md');
    const skillFiles = await glob(pattern, { nodir: true });

    if (skillFiles.length === 0) return { maxMtime: 0, count: 0 };

    // Get all file mtimes in parallel
    const mtimes = await Promise.all(
      skillFiles.map(async (file) => {
        try {
          const stats = await fs.promises.stat(file);
          return stats.mtimeMs;
        } catch {
          return 0;
        }
      })
    );

    return {
      maxMtime: Math.max(...mtimes),
      count: skillFiles.length
    };
  } catch {
    return { maxMtime: 0, count: 0 };
  }
}

/**
 * Discover skills with two-level process-lifetime caching
 * Level 1 (O(1)): Directory mtime catches structural changes (add/remove/rename)
 * Level 2 (O(n)): File stats catch content edits - only checked if directory changed
 */
async function discoverSkillsCached(root: string, sourceType: 'project' | 'user' | 'plugin' = 'plugin'): Promise<Skill[]> {
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';
  const cached = skillCache.get(root);

  // Level 1: Fast O(1) directory mtime check
  const dirMtime = getDirectoryMtime(root);

  if (cached && cached.dirMtime === dirMtime) {
    // Directory unchanged - structure is same, return cached skills
    if (debug) {
      console.error(`✓ Cache hit (O(1)) for ${root} (dirMtime: ${dirMtime})`);
    }
    return cached.skills;
  }

  // Level 2: Directory changed, do expensive O(n) file stats check
  const fileStats = await getSkillFileStats(root);

  // Check if we can still use cached skills despite directory mtime change
  // (e.g., temp files created/deleted, but SKILL.md files unchanged)
  if (cached &&
      cached.fileStats.maxMtime === fileStats.maxMtime &&
      cached.fileStats.count === fileStats.count) {
    if (debug) {
      console.error(`✓ Cache preserved after dir change for ${root} (SKILL.md files unchanged)`);
    }
    // Update dirMtime in cache to avoid re-checking next time
    cached.dirMtime = dirMtime;
    return cached.skills;
  }

  // Cache invalid - rebuild
  if (debug) {
    if (cached) {
      console.error(`⟳ Cache invalidated for ${root} (dirMtime: ${cached.dirMtime}→${dirMtime}, count: ${cached.fileStats.count}→${fileStats.count})`);
    } else {
      console.error(`⟳ Building initial cache for ${root}`);
    }
  }

  const skills = await discoverSkills(root, sourceType);
  skillCache.set(root, { skills, dirMtime, fileStats });
  return skills;
}

/**
 * Get all skill roots to search
 * Returns: { path: string, sourceType: 'project' | 'user' | 'plugin' }[]
 * Order: project skills last (so they win during deduplication) - highest priority
 */
function getSkillRoots(): Array<{ path: string; sourceType: 'project' | 'user' | 'plugin' }> {
  const roots: Array<{ path: string; sourceType: 'project' | 'user' | 'plugin' }> = [];
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
      } catch (error) {
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
 * Hybrid scoring: Combines rules-based, token-based, Fuse.js fuzzy matching, TF-IDF, and Semantic Search
 * TF-IDF adds term weighting: common terms get low weight, unique terms get high weight
 * Semantic Search: Captures intent and conceptual similarity
 */

/**
 * Find relevant skills for a prompt
 */
async function findRelevantSkills(prompt: string, limit = 3): Promise<{
  skills: Skill[],
  scoredSkills: Array<{ skill: Skill; score: number; source: string }>
}> {
  const roots = getSkillRoots();
  const allSkills: Skill[] = [];
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';

  if (debug) {
    console.error('\n🔍 HYBRID DEBUG MODE ENABLED (Token + Fuse.js + Rules + Semantic)');
    console.error(`Searching skill roots: ${roots.map(r => `${r.path} (${r.sourceType})`).join(', ')}`);
  }

  // Load skill rules - check PAI plugin lib first, then first skills root
  const paiDir = process.env.PAI_DIR || path.join(process.env.HOME || '', 'PAI');
  const paiPluginRulesDir = path.join(paiDir, '.claude', 'plugins', 'pai-skills', 'lib');
  let rules: SkillRules | null = null;
  if (fs.existsSync(path.join(paiPluginRulesDir, 'skill-rules.json'))) {
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

  // Deduplicate by folder name
  const seenFolders = new Map<string, number>();
  for (let i = 0; i < allSkills.length; i++) {
    const folder = allSkills[i].folderName.toLowerCase();
    seenFolders.set(folder, i);
  }
  const uniqueIndices = new Set(seenFolders.values());
  const deduplicatedSkills = allSkills.filter((_, i) => uniqueIndices.has(i));

  allSkills.length = 0;
  allSkills.push(...deduplicatedSkills);

  if (allSkills.length === 0) {
    if (debug) console.error('⚠️  No skills found!');
    return { skills: [], scoredSkills: [] };
  }

  // Calculate all scores in parallel where possible
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
        const sourceIcon = source === 'rules' ? '📋' : source === 'semantic' ? '🧠' : source === 'fuse' ? '🔎' : source === 'fuzzy' ? '🔍' : source === 'tfidf' ? '📊' : '🔀';
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

/**
 * Format skills for display
 */
function formatSkillSuggestions(
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
        const sourceIcon = scored.source === 'rules' ? '📋' : scored.source === 'semantic' ? '🧠' : scored.source === 'fuse' ? '🔎' : scored.source === 'fuzzy' ? '🔍' : scored.source === 'tfidf' ? '📊' : '🔀';
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

/**
 * Read stdin with timeout
 */
async function readStdinWithTimeout(timeout: number = 5000): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = '';
    const timer = setTimeout(() => {
      reject(new Error('Timeout reading from stdin'));
    }, timeout);

    process.stdin.on('data', (chunk) => {
      data += chunk.toString();
    });

    process.stdin.on('end', () => {
      clearTimeout(timer);
      resolve(data);
    });

    process.stdin.on('error', (err) => {
      clearTimeout(timer);
      reject(err);
    });
  });
}

/**
 * Main hook function
 */
async function main() {
  const debug = process.env.SKILL_ANALYZER_DEBUG === '1';
  if (debug) {
    console.error('🔧 SKILL_ANALYZER_DEBUG=1 enabled');
  }
  
  try {
    const input = await readStdinWithTimeout();
    const data: HookInput = JSON.parse(input);

    // Claude Code sends userMessage, fallback to prompt for backwards compatibility
    const userPrompt = data.userMessage || data.prompt || '';

    if (!userPrompt) {
      console.log(JSON.stringify({}));
      return;
    }

    // Analyze prompt for relevant skills
    const rawLimit = Number.parseInt(process.env.SKILL_ANALYZER_LIMIT || '3', 10);
    const limit = Number.isFinite(rawLimit) ? Math.min(20, Math.max(1, rawLimit)) : 3;
    const { skills: relevantSkills, scoredSkills } = await findRelevantSkills(userPrompt, limit);

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

    if (relevantSkills.length > 0) {
      recordSkillSuggestions(relevantSkills.map(skill => skill.name));
      const skillSummary = formatSkillSuggestions(relevantSkills, scoredSkills);

      // Check if we should notify about accumulated gaps
      const gapNotification = checkGapNotification();

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

      const response = {
        hookSpecificOutput: {
          hookEventName: 'UserPromptSubmit',
          additionalContext,
        },
      };

      console.log(JSON.stringify(response));
    } else {
      // No skills found - return empty response
      console.log(JSON.stringify({}));
    }
  } catch (error) {
    console.error('Error in skill analyzer hook:', error);
    console.log(JSON.stringify({}));
  }
}

// CLI mode for recording metrics externally
const args = process.argv.slice(2);
if (args[0] === '--record-activation' && args[1]) {
  recordSkillActivation(args[1]);
  console.log(`Recorded activation: ${args[1]}`);
} else if (args[0] === '--record-search' && args[1]) {
  recordSearch(args[1]);
  console.log(`Recorded search: ${args[1]}`);
} else if (args[0] === '--show-metrics') {
  const metrics = loadMetrics();
  console.log(JSON.stringify(metrics, null, 2));
} else if (args[0] === '--show-gaps') {
  const metrics = loadMetrics();
  const gaps = Object.entries(metrics.gaps).sort((a, b) => b[1] - a[1]);
  console.log(`\n📊 Skill Gaps (queries with low relevance scores < ${GAP_THRESHOLD})
`);
  console.log('='.repeat(60));
  console.log(`Total gap queries: ${gaps.reduce((a, [_, c]) => a + c, 0)}`);
  console.log(`Unique queries: ${gaps.length}`);
  console.log('='.repeat(60) + '\n');
  if (gaps.length === 0) {
    console.log('No gaps recorded yet.');
  } else {
    gaps.forEach(([query, count], i) => {
      console.log(`${String(i + 1).padEnd(4)} ${String(count).padStart(4)}x  "${query}"`);
    });
  }
} else if (args[0] === '--clear-gaps') {
  clearGaps();
  console.log('Gaps cleared.');
} else {
  // Normal hook mode - read from stdin
  main();
}

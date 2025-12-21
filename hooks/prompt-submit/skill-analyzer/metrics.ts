import fs from 'fs';
import path from 'path';
import { CONFIG } from '../../../lib/config';

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
export const GAP_THRESHOLD = CONFIG.GAP_THRESHOLD;

/** How many gap queries before we notify */
const GAP_NOTIFICATION_THRESHOLD = 10;

/** Minimum hours between gap notifications */
const GAP_NOTIFICATION_COOLDOWN_HOURS = 24;

function getMetricsPath(): string {
  // Use plugin root lib directory for metrics (alongside skill-rules.json)
  const pluginLibDir = path.join(__dirname, '..', '..', '..', 'lib');
  return path.join(pluginLibDir, 'skill-metrics.json');
}

const METRICS_FILE = getMetricsPath();
const METRICS_DIR = path.dirname(METRICS_FILE);
const GAPS_LOG_PATH = path.join(METRICS_DIR, 'skill-gaps.jsonl');

function getEmptyMetrics(): SkillMetrics {
  return {
    suggestions: {},
    activations: {},
    searches: {},
    gaps: {},
    lastUpdated: new Date().toISOString()
  };
}

export function loadMetrics(): SkillMetrics {
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
  const tmpPath = `${METRICS_FILE}.tmp`;
  fs.writeFileSync(tmpPath, JSON.stringify(metrics, null, 2));
  fs.renameSync(tmpPath, METRICS_FILE);
}

/**
 * Record skill suggestions (from hook)
 */
export function recordSkillSuggestions(skillNames: string[]): void {
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
export function recordSkillActivation(skillName: string): void {
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
export function recordSearch(query: string): void {
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
export function recordGap(query: string, bestScore: number): void {
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

/**
 * Record a rich gap entry to JSONL log for detailed analysis
 * Includes top matches to help identify what skills came close
 */
export function recordRichGap(
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
export function formatGapWarning(
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
export function checkGapNotification(): string | null {
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
export function clearGaps(): void {
  try {
    const metrics = loadMetrics();
    metrics.gaps = {};
    saveMetrics(metrics);
  } catch {
    // Silently fail
  }
}

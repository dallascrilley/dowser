import { glob } from 'glob';
import matter from 'gray-matter';
import fs from 'fs';
import path from 'path';
import type { Skill, SkillSourceType } from './types';

interface CacheEntry {
  skills: Skill[];
  dirMtime: number;
  fileStats: { maxMtime: number; count: number };
}

const skillCache = new Map<string, CacheEntry>();

function normalizeMultilineString(str: string | undefined): string {
  return (str || '').replace(/\r/g, '').split('\n').map((l) => l.trim()).filter(Boolean).join(' ');
}

function parseFrontMatter(
  content: string,
  defaultName: string
): { name: string; description: string; whenToUse: string } {
  try {
    const parsed = matter(content);
    const data = parsed.data as Record<string, unknown>;
    return {
      name: (data.name as string) || defaultName,
      description: normalizeMultilineString(data.description as string) || '',
      whenToUse: normalizeMultilineString((data.when_to_use as string) || (data.whenToUse as string)) || '',
    };
  } catch {
    return { name: defaultName, description: '', whenToUse: '' };
  }
}

async function discoverSkills(root: string, sourceType: SkillSourceType): Promise<Skill[]> {
  const pattern = path.join(root, '**/SKILL.md').replace(/\\/g, '/');
  const files = await glob(pattern, { nodir: true });
  const skills: Skill[] = [];

  for (const file of files) {
    const folderName = path.basename(path.dirname(file));
    const content = await fs.promises.readFile(file, 'utf-8');
    const { name, description, whenToUse } = parseFrontMatter(content, folderName);
    skills.push({
      name,
      path: file,
      description,
      whenToUse,
      relativePath: path.relative(root, path.dirname(file)),
      folderName,
      sourceType,
    });
  }

  return skills;
}

function getDirectoryMtime(root: string): number {
  try {
    return fs.statSync(root).mtimeMs;
  } catch {
    return 0;
  }
}

async function getSkillFileStats(root: string): Promise<{ maxMtime: number; count: number }> {
  const pattern = path.join(root, '**/SKILL.md').replace(/\\/g, '/');
  const files = await glob(pattern, { nodir: true });
  let maxMtime = 0;
  for (const file of files) {
    try {
      const mtime = fs.statSync(file).mtimeMs;
      if (mtime > maxMtime) maxMtime = mtime;
    } catch {
      // ignore
    }
  }
  return { maxMtime, count: files.length };
}

export async function discoverSkillsCached(root: string, sourceType: SkillSourceType): Promise<Skill[]> {
  const dirMtime = getDirectoryMtime(root);
  const cached = skillCache.get(root);
  if (cached && cached.dirMtime === dirMtime) return cached.skills;

  const fileStats = await getSkillFileStats(root);
  if (cached && cached.fileStats.maxMtime === fileStats.maxMtime && cached.fileStats.count === fileStats.count) {
    cached.dirMtime = dirMtime;
    return cached.skills;
  }

  const skills = await discoverSkills(root, sourceType);
  skillCache.set(root, { skills, dirMtime, fileStats });
  return skills;
}

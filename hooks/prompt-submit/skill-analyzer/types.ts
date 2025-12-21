export const SKILL_SOURCE_TYPES = ['project', 'user', 'plugin'] as const;
export type SkillSourceType = (typeof SKILL_SOURCE_TYPES)[number];

export interface HookInput {
  session_id?: string;
  prompt?: string;
  userMessage?: string;
  transcript_path?: string;
  hook_event_name?: string;
}

export interface Skill {
  name: string;
  path: string;
  description: string;
  whenToUse: string;
  relativePath: string;
  folderName: string;
  sourceType: SkillSourceType;
}

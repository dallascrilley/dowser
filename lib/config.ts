export const CONFIG = {
  GAP_THRESHOLD: 15,
  FUZZY_THRESHOLD: 0.4,
  WEIGHTS: {
    fuseKeys: {
      name: 0.4,
      folderName: 0.35,
      description: 0.15,
      whenToUse: 0.1,
    },
    hybridBonuses: {
      whenRulesMatch: {
        fuzzy: 0.3,
        fuse: 0.3,
        tfidf: 0.2,
      },
      whenNoRules: {
        secondary: 0.3,
        tertiary: 0.2,
      },
    },
  },
} as const;


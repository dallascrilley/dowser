---
name: extracting-knowledge-concepts
description: >-
  Use this skill when processing articles, papers, or documents to extract
  structured knowledge components including atomic concepts, relationships,
  tensions, and uncertainties. This skill should be used when building knowledge
  bases from text, analyzing research papers, synthesizing ideas from multiple
  sources, documenting contradictions between viewpoints, or creating structured
  representations of complex information for later synthesis or analysis.
when_to_use: >
  Use when processing articles/papers/documents to extract structured knowledge
  (atomic concepts, relationships, tensions, uncertainties), building knowledge
  bases, analyzing research papers, or synthesizing ideas from multiple sources.
version: 1.0.0
category: research-and-learning
short_description: >-
  Use this skill when processing articles, papers, or documents to extract
  structured knowledge components including atomic concepts, relationships,
  tensions, and uncertainties.
---

# Knowledge Concept Extraction Expert

Identify and extract knowledge components from articles, papers, and documents with surgical precision. Focus on creating structured, atomic representations suitable for knowledge synthesis and analysis.

## Core Responsibilities

1. **Extract Atomic Concepts**
   - Identify the smallest, most fundamental units of knowledge
   - Use consistent naming across all extractions
   - Distinguish between concepts, techniques, patterns, problems, and tools
   - Track concept evolution across articles

2. **Extract Relationships (SPO Triples)**
   - Subject-Predicate-Object triples with 1-3 word predicates
   - Types: hierarchical, dependency, alternative, complement, conflict
   - Preserve bidirectional relationships
   - Note relationship confidence levels

3. **Preserve Tensions and Contradictions**
   - Never force resolution of disagreements
   - Document conflicting viewpoints with equal weight
   - Mark tensions as productive features, not bugs
   - Track which articles support which positions

4. **Handle Uncertainty**
   - Explicitly mark "we don't know" states
   - Document confidence levels (high/medium/low/unknown)
   - Identify what would help resolve uncertainty
   - Preserve questions raised but not answered

## Extraction Methodology

### Phase 1: Initial Scan

Analyze the document's context:
- Identify article type (tutorial, opinion, case study, theory)
- Note publication date and author perspective
- Mark emotional tone and confidence level
- Understand the domain and scope

### Phase 2: Concept Identification

For each concept found, extract:

```json
{
  "name": "canonical_concept_name",
  "type": "concept|technique|pattern|problem|tool",
  "definition": "working definition from article",
  "article_source": "article_filename",
  "confidence": "high|medium|low",
  "related_concepts": ["concept1", "concept2"],
  "open_questions": ["question1", "question2"]
}
```

**Guidelines:**
- Use lowercase with underscores for concept names
- Ensure names are consistent across extractions
- Keep definitions concise but complete
- Always include the source article
- Be realistic about confidence levels

### Phase 3: Relationship Extraction

For each relationship between concepts:

```json
{
  "subject": "concept_a",
  "predicate": "enables",
  "object": "concept_b",
  "source": "article_filename",
  "confidence": 0.8,
  "type": "dependency|hierarchy|conflict|complement|alternative",
  "is_inferred": false
}
```

**Relationship Types:**
- **dependency**: One concept requires or enables another
- **hierarchy**: One concept is a type/part of another
- **conflict**: Concepts contradict or oppose each other
- **complement**: Concepts work well together
- **alternative**: Concepts are different approaches to same goal

**Predicate Examples:**
- "enables", "requires", "depends_on"
- "is_type_of", "contains", "part_of"
- "conflicts_with", "contradicts"
- "complements", "enhances"
- "alternative_to", "competes_with"

### Phase 4: Tension Documentation

For each contradiction or productive tension:

```json
{
  "tension_name": "descriptive_name",
  "position_a": {
    "claim": "what position A states",
    "supporters": ["article1", "article2"],
    "evidence": "key supporting points"
  },
  "position_b": {
    "claim": "what position B states",
    "supporters": ["article3"],
    "evidence": "key supporting points"
  },
  "why_productive": "why this tension advances understanding",
  "resolution_experiments": ["potential test 1", "potential test 2"]
}
```

**Important:**
- Give equal weight to all positions
- Don't editorialize or take sides
- Document the value of maintaining the tension
- Suggest experiments that could help resolve uncertainty

### Phase 5: Uncertainty Documentation

For each significant uncertainty:

```json
{
  "question": "what we don't know",
  "why_matters": "impact on understanding",
  "evidence_needed": "what would help resolve this",
  "related_concepts": ["concept1", "concept2"],
  "mentioned_in": ["article1"]
}
```

## Complete Output Format

Always return structured JSON with these sections:

```json
{
  "concepts": [
    {
      "name": "concept_name",
      "type": "concept",
      "definition": "definition text",
      "article_source": "source.md",
      "confidence": "high",
      "related_concepts": [],
      "open_questions": []
    }
  ],
  "relationships": [
    {
      "subject": "concept_a",
      "predicate": "enables",
      "object": "concept_b",
      "source": "source.md",
      "confidence": 0.9,
      "type": "dependency",
      "is_inferred": false
    }
  ],
  "tensions": [
    {
      "tension_name": "name",
      "position_a": {
        "claim": "claim text",
        "supporters": ["article1"],
        "evidence": "evidence text"
      },
      "position_b": {
        "claim": "claim text",
        "supporters": ["article2"],
        "evidence": "evidence text"
      },
      "why_productive": "explanation",
      "resolution_experiments": []
    }
  ],
  "uncertainties": [
    {
      "question": "what we don't know",
      "why_matters": "why it matters",
      "evidence_needed": "what's needed",
      "related_concepts": [],
      "mentioned_in": []
    }
  ],
  "metadata": {
    "total_concepts": 0,
    "total_relationships": 0,
    "total_tensions": 0,
    "total_uncertainties": 0,
    "average_confidence": 0.0,
    "extraction_date": "YYYY-MM-DD",
    "source_article": "filename"
  }
}
```

## Quality Verification Checklist

Before returning results, verify:

- [ ] All concepts are atomic (can't be split further without losing meaning)
- [ ] Concept names are standardized and consistent
- [ ] All predicates are 1-3 words maximum
- [ ] Contradictions are preserved, not resolved
- [ ] Confidence levels are realistic, not inflated
- [ ] All open questions are captured
- [ ] Source attribution is complete
- [ ] Metadata statistics are accurate
- [ ] JSON is valid and properly formatted

## Common Patterns and Examples

### Example: Distributed Systems Article

**Extracted Concepts:**
```json
{
  "name": "cap_theorem",
  "type": "concept",
  "definition": "theorem stating distributed systems can only guarantee 2 of 3: consistency, availability, partition tolerance",
  "article_source": "intro_to_distributed_systems.md",
  "confidence": "high",
  "related_concepts": ["consistency", "availability", "partition_tolerance"],
  "open_questions": ["how does this apply to modern cloud architectures?"]
}
```

**Extracted Relationship:**
```json
{
  "subject": "microservices",
  "predicate": "requires",
  "object": "distributed_consensus",
  "source": "intro_to_distributed_systems.md",
  "confidence": 0.7,
  "type": "dependency",
  "is_inferred": true
}
```

**Extracted Tension:**
```json
{
  "tension_name": "consistency_vs_availability_tradeoff",
  "position_a": {
    "claim": "systems should prioritize consistency over availability",
    "supporters": ["banking_systems_paper.md"],
    "evidence": "financial transactions require guaranteed consistency"
  },
  "position_b": {
    "claim": "systems should prioritize availability over consistency",
    "supporters": ["social_media_architecture.md"],
    "evidence": "user experience suffers with downtime, eventual consistency acceptable"
  },
  "why_productive": "highlights that optimal choice depends on use case domain",
  "resolution_experiments": [
    "measure user tolerance for stale data in different domains",
    "compare business impact of downtime vs inconsistency"
  ]
}
```

## What NOT to Do

Critical mistakes to avoid:

- **Don't merge similar concepts** without explicit evidence they're identical
- **Don't resolve contradictions** by averaging or choosing sides
- **Don't ignore uncertainty** - "I don't know" is valuable information
- **Don't create unsupported relationships** - only extract what's stated or strongly implied
- **Don't inflate confidence** - be honest about uncertainty
- **Don't editorialize** - preserve the source material's perspective
- **Don't skip metadata** - always include source attribution and confidence

## Best Practices

1. **Start Small**: Extract from one section at a time
2. **Use Canonical Names**: Standardize concept names early
3. **Track Sources**: Always attribute to source article
4. **Preserve Context**: Include enough definition to understand standalone
5. **Be Atomic**: Break concepts down to fundamental units
6. **Document Everything**: Capture all uncertainties and questions
7. **Respect Tensions**: Contradictions are features, not bugs
8. **Validate JSON**: Ensure output is properly formatted

## Use Cases

**Building Knowledge Bases:**
- Process research papers into structured knowledge
- Create concept maps from documentation
- Build semantic networks from articles

**Synthesizing Information:**
- Extract concepts from multiple sources for comparison
- Identify common patterns across different authors
- Document evolution of ideas over time

**Preserving Complexity:**
- Maintain productive tensions between viewpoints
- Document disagreements in research literature
- Track uncertainty and open questions

**Enabling Analysis:**
- Create machine-readable knowledge representations
- Support graph-based knowledge queries
- Enable automated concept relationship discovery

## Working with Node.js

If processing multiple files or automating extraction:

```javascript
#!/usr/bin/env node
import { readFile, writeFile } from 'fs/promises';
import { glob } from 'glob';

// Process multiple markdown files
const files = await glob('articles/**/*.md');

for (const file of files) {
  const content = await readFile(file, 'utf-8');

  // Claude processes each file with this skill
  // Output saved to structured JSON
  const outputPath = file.replace('.md', '_concepts.json');

  console.log(`Processing: ${file}`);
  // Results written to outputPath
}
```

**CLI Tools:**
- `jq` - Query extracted JSON structures
- `node` - Script batch processing
- `git` - Track knowledge base changes over time

## Template Reference

See `./extraction-output-template.json` for a complete output template with all fields documented.

---

**Remember:** Your role is extraction and preservation, not interpretation or resolution. The messiness and uncertainty you preserve become the raw material for revolutionary insights. Maintain the integrity of source material while structuring it for downstream synthesis.

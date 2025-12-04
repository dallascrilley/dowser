# Best Practices & Quality Checklists

## Documentation Analysis Best Practices

1. **Read completely** before starting analysis
2. **Take notes** on patterns you see
3. **Look for implicit workflows** not explicitly documented
4. **Anticipate mistakes** beyond what docs mention
5. **Consider edge cases** and error scenarios

## Component Design Best Practices

1. **Start simple** - Add complexity as needed
2. **Validate early** - Test scripts as you write them
3. **DRY principle** - Reuse logic across scripts
4. **User-friendly** - Clear messages, good defaults
5. **Fail fast** - Catch errors early with clear messages

## Skill Writing Best Practices

1. **Progressive disclosure** - Quick start → Details
2. **Examples everywhere** - Every section needs examples
3. **Consistent formatting** - Follow template structure
4. **Cross-reference** - Link related sections
5. **Test as you write** - Verify examples work

## Testing Best Practices

1. **Fresh start** - Test in new session
2. **Follow docs literally** - Don't assume knowledge
3. **Try to break it** - Invalid inputs, edge cases
4. **Real scenarios** - Use actual use cases
5. **Document issues** - Note everything that's unclear

## Quality Checklists

### Documentation Analysis Quality

- [ ] Complete tool overview extracted
- [ ] All command/API patterns documented
- [ ] Minimum 3 workflows identified
- [ ] All explicit warnings captured
- [ ] Anticipated pitfalls documented
- [ ] Best practices extracted
- [ ] Configuration patterns noted

### Skill Design Quality

- [ ] At least 3 helper scripts designed
- [ ] At least 2 config templates designed
- [ ] Critical guardrails identified
- [ ] Mandatory workflows defined
- [ ] Checklists created
- [ ] Reference structure planned

### Artifact Quality

- [ ] All helper scripts work correctly
- [ ] Scripts have clear error messages
- [ ] Config templates are valid
- [ ] Templates are well-commented
- [ ] Reference docs are complete
- [ ] scripts/README.md is clear

### SKILL.md Quality

- [ ] YAML frontmatter complete
- [ ] Description has clear triggers
- [ ] All template sections included
- [ ] Examples in every section
- [ ] All file references valid
- [ ] Guardrails marked MANDATORY
- [ ] Workflows explained clearly

### Integration Quality

- [ ] Added to global context correctly
- [ ] Skill activates with natural language
- [ ] All file references work
- [ ] Helper scripts executable
- [ ] Config templates usable
- [ ] Workflows tested

## Common Pitfalls

### Pitfall 1: Incomplete Documentation Analysis

**Symptom:** Missing critical workflows or pitfalls

**Cause:** Skimming docs instead of thorough analysis

**Solution:**
- Read all sections completely
- Take notes on every pattern
- Ask: "What could go wrong here?"
- Document implicit workflows

### Pitfall 2: Over-Engineering Helper Scripts

**Symptom:** Complex scripts that are hard to maintain

**Cause:** Trying to handle every edge case

**Solution:**
- Start with simple version
- Add features based on actual need
- Keep logic clear and readable
- Document complex parts well

### Pitfall 3: Template Overload

**Symptom:** Too many templates, user confused

**Cause:** Creating template for every variation

**Solution:**
- Stick to 2-4 key templates
- Use comments to show variations
- Document when to use each
- Make basic template really basic

### Pitfall 4: Weak Guardrails

**Symptom:** Users still making common mistakes

**Cause:** Guardrails not enforced strongly enough

**Solution:**
- Use ⚠️ MANDATORY prominently
- Explain "why this prevents failures"
- Build validation into scripts
- Make it hard to skip critical steps

### Pitfall 5: Stale Examples

**Symptom:** Examples don't work as shown

**Cause:** Not testing examples after writing

**Solution:**
- Run every example as you write it
- Use actual tool to verify
- Include expected output
- Update when tool changes

### Pitfall 6: Missing Context

**Symptom:** Users confused about when to use features

**Cause:** Assuming knowledge not stated

**Solution:**
- Explain prerequisites clearly
- State when to use each approach
- Provide context for options
- Link to background info

## Success Criteria

A skill is complete and production-ready when:

1. **Comprehensive**
   - Covers all major tool features
   - Includes common workflows
   - Documents pitfalls and solutions

2. **Automated**
   - Helper scripts for error-prone tasks
   - Validation prevents mistakes
   - Setup is largely automated

3. **Safe**
   - Guardrails prevent common mistakes
   - Mandatory workflows enforced
   - Prerequisites checked

4. **Clear**
   - Examples work as shown
   - Instructions are unambiguous
   - Structure is consistent

5. **Tested**
   - All scripts run successfully
   - All templates are valid
   - All workflows execute correctly

6. **Maintainable**
   - Well-organized structure
   - Clear documentation
   - Easy to update


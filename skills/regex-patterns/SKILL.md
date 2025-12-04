---
name: regex-patterns
description: >-
  Create, validate, and apply regular expression patterns for data validation,
  text extraction, and transformation tasks
when_to_use: >
  Use when creating/validating regex patterns, performing data validation
  (email, URL, phone, etc.), extracting text (emails, URLs,

  hashtags, mentions), parsing log files, transforming text (case conversion,
  sanitization), or performing advanced search/replace

  with pattern matching.
version: 1.0.0
category: coding
---

# Regular Expressions (Regex) Skill

This skill provides comprehensive regex pattern creation, validation, extraction, and transformation capabilities for working with text data, log files, and structured content.

## Capabilities

Create and apply regex patterns for:
- **Data Validation**: Email, URL, phone, credit card, date, password, IPv4, hex color validation
- **Text Extraction**: Extract emails, URLs, hashtags, mentions, phone numbers, code blocks from text
- **Log Parsing**: Parse structured log files and extract key information
- **Text Transformation**: Case conversion, sanitization, HTML stripping, masking, truncation
- **Search and Replace**: Advanced text search and replacement with pattern matching
- **Pattern Testing**: Test regex patterns with edge cases and validation

## Input Requirements

Depending on the task, provide:
- **Text to analyze**: Raw text, log files, documents, or code
- **Pattern type**: Validation, extraction, or transformation
- **Target format**: What you want to validate, extract, or transform
- **Options**: Case sensitivity, multi-line mode, global matching

Input formats accepted:
- Plain text strings
- JSON with text fields
- Log files (text format)
- CSV or structured data
- Code snippets

## Output Formats

Results include:
- **Validation Results**: Boolean validation with detailed error messages
- **Extracted Data**: Lists of matched patterns (emails, URLs, etc.)
- **Transformed Text**: Modified text with applied transformations
- **Match Details**: Capture groups, positions, and matched strings
- **Pattern Explanation**: Human-readable explanation of regex patterns

## How to Use

Example invocations:
- "Validate this email address using regex patterns"
- "Extract all URLs from this text document"
- "Parse this log file and extract timestamps, error codes, and messages"
- "Sanitize this filename to remove special characters"
- "Mask credit card numbers in this text"
- "Convert this text to title case using regex"

## Scripts

- `regex_validator.py`: Common validation patterns (email, URL, phone, credit card, etc.)
- `regex_extractor.py`: Data extraction patterns (URLs, emails, hashtags, code blocks, logs)
- `regex_transformer.py`: Text transformation utilities (case conversion, sanitization, masking)

## Best Practices

1. **Use Named Capture Groups**: Makes patterns more readable and maintainable
2. **Comment Complex Patterns**: Use verbose mode (`re.VERBOSE`) for clarity
3. **Test Edge Cases**: Always test with boundary conditions and invalid inputs
4. **Avoid Catastrophic Backtracking**: Be careful with nested quantifiers
5. **Pre-compile Patterns**: Use `re.compile()` for frequently used patterns
6. **Validate Input**: Always sanitize input before applying regex
7. **Use Raw Strings**: Use `r''` notation to avoid escaping issues
8. **Consider Performance**: Complex patterns on large texts can be slow
9. **Escape Special Characters**: Use `re.escape()` for literal matching
10. **Document Assumptions**: Clearly state what format your patterns expect

## Pattern Categories

### Validation Patterns
- Email addresses (RFC-compliant)
- URLs and URIs
- Phone numbers (US and international)
- Credit card numbers
- Dates (multiple formats)
- Passwords (complexity rules)
- IPv4 addresses
- Hex color codes

### Extraction Patterns
- URLs from text
- Email addresses
- Social media hashtags
- @mentions
- Phone numbers
- Code blocks (markdown, HTML)
- Log entries (structured parsing)

### Transformation Patterns
- Case conversion (title, camel, snake, kebab)
- Filename sanitization
- HTML tag stripping
- Credit card masking
- Text truncation (word-aware)
- Whitespace normalization

## Resources

- **Regex101**: https://regex101.com/ - Online regex tester with explanations
- **RegExr**: https://regexr.com/ - Visual regex builder and testing
- **MDN Regex Guide**: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
- **Python re Module**: https://docs.python.org/3/library/re.html

## Limitations

- Complex regex patterns can have performance issues on large texts
- Some validation patterns are simplified (real-world validation is more complex)
- Email validation is basic (full RFC 5322 compliance is extremely complex)
- Phone number validation assumes common formats (international formats vary widely)
- Credit card validation checks format only, not actual card validity
- Some patterns may need adjustment for specific use cases or locales
- Regex is not suitable for parsing nested structures (use proper parsers instead)

# How to Use the Regex Patterns Skill

Hey Claude—I just added the "regex-patterns" skill. Can you help me validate, extract, or transform text using regular expressions?

## Example Invocations

### Validation Examples

**Example 1: Email Validation**
```
Hey Claude—I just added the "regex-patterns" skill. Can you validate if this email address is properly formatted: user@example.com?
```

**Example 2: Multiple Validations**
```
Hey Claude—I just added the "regex-patterns" skill. Can you validate this data:
- Email: support@company.com
- URL: https://www.example.com/page
- Phone: (555) 123-4567
- Password: SecureP@ss123
```

**Example 3: Credit Card Validation**
```
Hey Claude—I just added the "regex-patterns" skill. Can you check if this credit card number format is valid: 4532 1234 5678 9010?
```

### Extraction Examples

**Example 4: Extract URLs and Emails**
```
Hey Claude—I just added the "regex-patterns" skill. Can you extract all URLs and email addresses from this document?

[Paste your text here]
```

**Example 5: Social Media Extraction**
```
Hey Claude—I just added the "regex-patterns" skill. Can you extract all hashtags and @mentions from this social media post?

"Check out our new product! #Innovation #TechNews Follow us @CompanyName for updates!"
```

**Example 6: Log File Parsing**
```
Hey Claude—I just added the "regex-patterns" skill. Can you parse this log file and extract timestamps, log levels, and messages?

[Paste your log file content here]
```

### Transformation Examples

**Example 7: Case Conversion**
```
Hey Claude—I just added the "regex-patterns" skill. Can you convert this text to:
- Title Case
- camelCase
- snake_case
- kebab-case

Text: "This is my sample text"
```

**Example 8: Filename Sanitization**
```
Hey Claude—I just added the "regex-patterns" skill. Can you sanitize this filename to remove special characters: "My Document (Final) v2.3 [DRAFT].pdf"?
```

**Example 9: Credit Card Masking**
```
Hey Claude—I just added the "regex-patterns" skill. Can you mask the credit card numbers in this text for security?

"Customer paid with card 4532 1234 5678 9010 and backup card 5425 2334 5566 7788."
```

**Example 10: HTML Tag Removal**
```
Hey Claude—I just added the "regex-patterns" skill. Can you strip all HTML tags from this content?

"<p>This is <strong>important</strong> text with <a href='#'>links</a>.</p>"
```

## What to Provide

### For Validation Tasks:
- Data to validate (email, URL, phone, credit card, date, password, IP address, hex color)
- Format specification (e.g., ISO date vs US date)

### For Extraction Tasks:
- Text content (document, webpage, log file, social media post)
- What to extract (URLs, emails, hashtags, phone numbers, code blocks)

### For Transformation Tasks:
- Text to transform
- Desired transformation (case conversion, sanitization, masking, truncation)

### For Custom Patterns:
- Text to process
- Custom regex pattern
- Replacement pattern (for find-and-replace)

## What You'll Get

### Validation Results:
- Boolean valid/invalid status
- Detailed validation messages
- Specific issues identified (for failures)

### Extraction Results:
- Lists of extracted items
- Structured data (for log parsing)
- Match positions and details (if requested)

### Transformation Results:
- Transformed text
- Before/after comparison
- Multiple format options (if applicable)

## Common Use Cases

1. **Form Validation**: Validate user input (emails, phones, URLs, passwords)
2. **Data Extraction**: Extract contact info from documents
3. **Log Analysis**: Parse and analyze log files
4. **Content Processing**: Clean and format text content
5. **Data Masking**: Protect sensitive information (credit cards, emails)
6. **Code Processing**: Extract code blocks from documentation
7. **Social Media**: Extract hashtags and mentions
8. **Text Normalization**: Standardize text formatting
9. **Filename Cleanup**: Sanitize filenames for storage
10. **Search and Replace**: Advanced text manipulation

## Tips for Best Results

- Be specific about the format you're expecting
- Provide sample data for custom patterns
- Mention edge cases you want to handle
- Specify the output format you need
- For complex patterns, describe the logic in plain English first

## Pattern Complexity Levels

**Simple**: Email, URL, phone validation
**Medium**: Log parsing, credit card masking, case conversion
**Advanced**: Custom patterns with capture groups, complex transformations

Start simple and progressively add complexity as needed!

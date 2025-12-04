# Contract Specification Template

This template provides a complete contract specification format for modules. Use this to create README.md files that fully document module contracts.

## Complete Contract Template

```markdown
# Module Name

**Purpose:** [One sentence: What problem does this module solve?]

**Version:** [Semantic version: 1.0.0]

**Status:** [Development | Beta | Production | Deprecated]

**Maintainer:** [Team or person name]

---

## Overview

[2-3 paragraphs explaining]:
- What problem this module solves
- How it fits into the larger system
- Key design decisions and tradeoffs
- When to use this module vs alternatives

---

## Contract Summary

### Inputs

- **Primary Type:** `TypeName`
- **Structure:** `{ field1: type1, field2: type2 }`
- **Constraints:**
  - field1: [constraint description]
  - field2: [constraint description]
- **Validation:** [What validation is performed, what errors raised]

### Outputs

- **Primary Type:** `TypeName`
- **Structure:** `{ field1: type1, field2: type2 }`
- **Format:** [Description of output format]
- **Guarantees:** [What the module guarantees about output]

### Side Effects

[Choose one]:
- **None** - Pure function, no side effects
OR
- **File System:** [What files/directories are read/written]
- **Network:** [What external APIs/services are called]
- **Database:** [What tables/collections are accessed]
- **Cache:** [What caching is performed]
- **Logging:** [What is logged and where]

### Dependencies

- **Required:**
  - `package_name>=version` - [Why needed, what it's used for]
- **Optional:**
  - `package_name>=version` - [When needed, what feature requires it]

---

## Public Interface

### Functions

#### `function_name(param1: Type1, param2: Type2) -> ReturnType`

[One sentence describing what this function does]

**Parameters:**
- `param1` (Type1): [Description, valid values, examples]
- `param2` (Type2): [Description, valid values, examples, defaults]

**Returns:**
- ReturnType: [Description of return value, structure, guarantees]

**Raises:**
- `ExceptionType1`: [When this is raised, what it means]
- `ExceptionType2`: [When this is raised, what it means]

**Performance:**
- Time complexity: [O(n), O(log n), etc.]
- Memory usage: [Approximate memory usage]
- Typical duration: [Expected execution time]

**Examples:**
```python
# Basic usage
from module_name import function_name

result = function_name(param1_value, param2_value)
print(result)

# With error handling
try:
    result = function_name(param1_value, param2_value)
except ExceptionType1 as e:
    print(f"Error: {e}")

# Advanced usage
result = function_name(
    param1=complex_value,
    param2=optional_value
)
```

### Classes (if any)

#### `ClassName`

[One sentence describing what this class represents]

**Attributes:**
- `attribute1` (Type1): [Description, constraints]
- `attribute2` (Type2): [Description, constraints, defaults]

**Methods:**
- `method_name(args) -> ReturnType`: [Brief description]

**Examples:**
```python
# Creating instance
obj = ClassName(attribute1=value1, attribute2=value2)

# Using methods
result = obj.method_name(args)
```

### Data Models

#### `ModelName`

[One sentence describing what this model represents]

**Fields:**
- `field1` (Type1): [Description, constraints, validation]
  - Required: [Yes/No]
  - Default: [Default value if any]
  - Example: `field1="value"`

**Validation:**
- [List validation rules applied]
- [What errors are raised for invalid data]

**JSON Schema:**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Example:**
```python
from module_name import ModelName

# Create instance
model = ModelName(field1="value1", field2="value2")

# Serialize to JSON
json_data = model.model_dump_json()

# Deserialize from JSON
model = ModelName.model_validate_json(json_data)
```

---

## Error Handling

| Error Type         | Condition                      | Recovery Strategy                  | HTTP Status (if API) |
|--------------------|--------------------------------|-----------------------------------|---------------------|
| `ValueError`       | [When this occurs]             | [How to handle/recover]           | 400                 |
| `TypeError`        | [When this occurs]             | [How to handle/recover]           | 400                 |
| `TimeoutError`     | [When this occurs]             | [How to handle/recover]           | 504                 |
| `CustomError`      | [When this occurs]             | [How to handle/recover]           | 500                 |

**Error Response Format:**
```python
# For functions
raise ValueError("Descriptive error message with context")

# For Results
Result(
    status="error",
    error="Descriptive error message",
    data={"error_code": "ERROR_CODE", "details": {...}}
)
```

---

## Performance Characteristics

### Time Complexity

- **Operation 1:** O(n) where n = [description]
- **Operation 2:** O(log n) where n = [description]
- **Worst case:** [Complexity and scenario]
- **Best case:** [Complexity and scenario]

### Memory Usage

- **Base memory:** ~[MB] for initialization
- **Per item:** ~[KB/MB] per [item/request/document]
- **Peak memory:** ~[MB] under [scenario]

### Throughput

- **Sequential:** [N] items/second
- **Parallel:** [N] items/second with [N] workers
- **Sustained load:** [N] requests/minute

### Limits

- **Max concurrent requests:** [N]
- **Max item size:** [N MB/KB]
- **Timeout:** [N] seconds
- **Rate limits:** [N] requests per [minute/second]

---

## Configuration

### Default Configuration

```python
DEFAULT_CONFIG = {
    "setting1": value1,  # Description of what this controls
    "setting2": value2,  # Description of what this controls
    "setting3": value3,  # Description of what this controls
}
```

### Environment Variables

- `MODULE_SETTING1` - [Description, type, default]
- `MODULE_SETTING2` - [Description, type, default]
- `MODULE_SETTING3` - [Description, type, default]

### Configuration Examples

```python
# Using default configuration
from module_name import function_name
result = function_name(input)

# With custom configuration
from module_name import function_name, Config
config = Config(setting1=custom_value)
result = function_name(input, config=config)

# Via environment variables
import os
os.environ["MODULE_SETTING1"] = "custom_value"
from module_name import function_name
result = function_name(input)
```

---

## Testing

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_contract.py

# With coverage
pytest --cov=module_name tests/

# Specific test function
pytest tests/test_core.py::test_function_name -v

# Contract tests only
pytest tests/test_contract.py -v

# Documentation tests
pytest tests/test_documentation.py -v
```

### Test Categories

- **Contract Tests:** Validate public interface matches specification
- **Documentation Tests:** Verify examples in docs actually work
- **Unit Tests:** Test individual functions and classes
- **Integration Tests:** Test module working with dependencies
- **Performance Tests:** Verify performance characteristics

### Coverage Requirements

- **Overall:** ≥ 90%
- **Public functions:** 100%
- **Contract validation:** 100%
- **Documentation examples:** 100%

---

## Examples

See `examples/` directory for complete working examples:

- `basic_usage.py` - Getting started, simple use case
- `advanced_usage.py` - Complex scenarios, edge cases
- `integration.py` - Integration with other modules
- `error_handling.py` - Proper error handling patterns
- `performance.py` - Performance optimization techniques

### Quick Start Example

```python
# examples/basic_usage.py
from module_name import function_name, ModelName

# Step 1: Create input
input_data = ModelName(field1="value1", field2="value2")

# Step 2: Process
result = function_name(input_data)

# Step 3: Handle result
if result.status == "success":
    print(f"Success: {result.data}")
else:
    print(f"Error: {result.error}")
```

---

## API Reference (if HTTP API)

### Base URL

```
http://localhost:8000/api
OR
https://api.example.com
```

### Authentication

```http
Authorization: Bearer <token>
```

### Endpoints

#### POST /process

Process an item.

**Request:**
```http
POST /api/process
Content-Type: application/json

{
  "field1": "value1",
  "field2": "value2"
}
```

**Response (Success):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "data": {
    "result": "processed",
    "metadata": {}
  }
}
```

**Response (Error):**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "status": "error",
  "error": "Invalid input format",
  "details": {
    "field": "field1",
    "issue": "Required field missing"
  }
}
```

---

## Regeneration Specification

This module can be completely regenerated from this specification alone.

### Key Invariants (MUST preserve)

These cannot change without breaking the contract:

- **Public function signatures**
  - `function_name(param1: Type1) -> ReturnType`
- **Data model structures**
  - ModelName fields and types
- **Error types and conditions**
  - What errors are raised and when
- **Side effect behaviors**
  - What external changes occur
- **Performance characteristics**
  - Time/space complexity guarantees

### Implementation Details (CAN change)

These can be modified during regeneration:

- **Internal algorithms**
  - How functions are implemented
- **Private helper functions**
  - Internal utilities and helpers
- **File organization**
  - How code is split across files
- **Variable names**
  - Internal variable naming
- **Optimization techniques**
  - Performance optimizations

### Regeneration Checklist

Before regenerating, verify:

- [ ] README.md contains complete contract
- [ ] All public interfaces documented
- [ ] Error conditions specified
- [ ] Performance characteristics documented
- [ ] Examples provided and tested
- [ ] Contract tests exist and pass
- [ ] Documentation tests exist and pass

After regenerating:

- [ ] All contract tests pass
- [ ] All documentation tests pass
- [ ] Public API unchanged
- [ ] Error handling unchanged
- [ ] Performance characteristics maintained
- [ ] Examples still work

---

## Version History

See `CHANGELOG.md` for detailed version history.

### Version 1.0.0 (Current)

- Initial production release
- [List of features]
- [List of breaking changes from beta]

### Migration Guides

See `docs/migration.md` for guidance on upgrading between versions.

---

## Troubleshooting

See `docs/troubleshooting.md` for common issues and solutions.

### Common Issues

**Issue:** [Common problem]
**Cause:** [Why it happens]
**Solution:** [How to fix]

---

## Contributing

[Guidelines for contributing to this module]

---

## License

[License information - typically MIT]

---

## Contact

- **Maintainer:** [Name/Team]
- **Email:** [Contact email]
- **Issues:** [GitHub issues URL]
- **Documentation:** [Docs URL]

```

## Contract Writing Best Practices

### 1. Be Specific About Constraints

❌ Bad:
```markdown
### Inputs
- text: string
```

✅ Good:
```markdown
### Inputs
- `text` (str): Document text content
  - Constraints: 1-1,000,000 characters
  - Must not be empty or whitespace-only
  - Unicode supported
  - Validation: Raises ValueError if invalid
```

### 2. Document All Error Conditions

❌ Bad:
```markdown
May raise errors if input is invalid.
```

✅ Good:
```markdown
**Raises:**
- `ValueError`: If content is empty (< 1 char) or exceeds 1M chars
- `TypeError`: If content is not a string
- `TimeoutError`: If processing exceeds 30 seconds
- `ProcessingError`: If external service unavailable
```

### 3. Provide Executable Examples

❌ Bad:
```python
# Use the function
result = process(data)
```

✅ Good:
```python
# Complete example that can be copy-pasted
from document_processor import process_document, Document

# Create input
doc = Document(
    content="This is a sample document",
    metadata={"source": "api"}
)

# Process
result = process_document(doc)

# Check result
assert result.status == "success"
print(f"Processed {result.data['tokens']} tokens")
```

### 4. Specify Performance Characteristics

❌ Bad:
```markdown
Function is fast.
```

✅ Good:
```markdown
### Performance Characteristics
- Time Complexity: O(n) where n = document length
- Memory Usage: ~100MB per 1000 documents
- Typical Duration: 50-100ms for 1KB document
- Throughput: 1000 documents/second
- Max Concurrent: 10 simultaneous requests
```

### 5. Define Clear Side Effects

❌ Bad:
```markdown
May write to disk.
```

✅ Good:
```markdown
### Side Effects
- **File System:**
  - Writes cache to `/tmp/doc_cache/`
  - Creates `~/.doc_processor/` if not exists
- **Network:**
  - Calls `https://api.sentiment.com/analyze` for sentiment analysis
  - Rate limit: 100 requests/minute
- **Database:**
  - Reads from `documents` table (read-only)
  - No writes or updates
```

## Using the Template

### Step 1: Copy Template

```bash
cp contract-specification-template.md module_name/README.md
```

### Step 2: Fill in All Sections

Work through each section systematically:
1. Module name and metadata
2. Overview and problem statement
3. Contract summary (inputs, outputs, side effects)
4. Public interface details
5. Error handling table
6. Performance characteristics
7. Configuration options
8. Examples

### Step 3: Write Contract Tests

```python
# tests/test_contract.py
def test_contract_matches_readme():
    """Verify implementation matches README.md contract"""
    # Test each specified behavior
    pass
```

### Step 4: Validate Examples

```bash
# Run all examples to verify they work
python examples/basic_usage.py
python examples/advanced_usage.py
```

### Step 5: Review Regeneration Specification

- Can module be rebuilt from README.md alone?
- Are all invariants documented?
- Are implementation details clearly separated?

## Summary

A complete contract specification:

- Enables regeneration from documentation alone
- Provides clear public interface definition
- Documents all error conditions and recovery
- Specifies performance characteristics
- Includes working, tested examples
- Separates invariants from implementation details
- Serves as authoritative reference for module behavior

Use this template to create README.md files that are complete contracts for your modules.

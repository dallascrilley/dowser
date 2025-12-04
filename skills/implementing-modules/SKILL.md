---
name: implementing-modules
short_description: >-
  Implement code from specifications following the 'bricks and studs' philosophy
  to create self-contained, regeneratable modules with clear contracts.
description: >-
  Use this skill when implementing code from specifications, building
  self-contained modules, creating regeneratable components, or following the
  'bricks and studs' modular design philosophy. This includes implementing
  modules with clear contracts, creating isolated components with public
  interfaces, building documentation-first modules, or structuring code into
  self-contained directories. Applies when working with specifications from
  architecture designs, creating Python modules with proper boundaries, or
  ensuring modules can be regenerated from specifications alone.
when_to_use: >
  Implementing code from specifications, building self-contained modules,
  creating regeneratable components, following 'bricks and studs' philosophy,
  working with architecture specifications, creating Python modules with proper
  boundaries, ensuring modules can be regenerated from specs.
version: 1.0.0
category: architecture
---

Build code from specifications following the "bricks and studs" philosophy to create self-contained, regeneratable modules with clear contracts.

## Core Principles

Follow these fundamental principles when implementing modules:

### Brick Philosophy

- **A brick** = Self-contained directory/module with ONE clear responsibility
- **A stud** = Public contract (functions, API, data model) others connect to
- **Regeneratable** = Can be rebuilt from spec without breaking connections
- **Isolated** = All code, tests, fixtures inside the brick's folder

For detailed philosophy explanation, see `./bricks-and-studs-philosophy.md`

## Implementation Process

### 1. Receive Specifications

When given specifications from architecture design or user requirements:

- Review the module contracts and boundaries
- Understand inputs, outputs, and side effects
- Note dependencies and constraints
- Identify test requirements

### 2. Build the Module

**Create documentation-first module structure:**

```
module_name/
├── __init__.py         # Public interface ONLY
├── README.md           # MANDATORY contract documentation
├── API.md              # API reference (if module exposes API)
├── CHANGELOG.md        # Version history and migration guides
├── core.py             # Main implementation
├── models.py           # Data structures with docstrings
├── utils.py            # Internal helpers
├── config.py           # Configuration with defaults
├── tests/
│   ├── test_contract.py      # Contract validation tests
│   ├── test_documentation.py # Documentation accuracy tests
│   ├── test_examples.py      # Verify all examples work
│   ├── test_core.py          # Unit tests
│   └── fixtures/             # Test data
├── examples/
│   ├── basic_usage.py        # Simple example
│   ├── advanced_usage.py     # Complex scenarios
│   ├── integration.py        # How to integrate
│   └── README.md            # Guide to examples
└── docs/
    ├── architecture.md       # Internal design decisions
    ├── benchmarks.md        # Performance measurements
    └── troubleshooting.md  # Common issues and solutions
```

See `./module-structure-guide.md` for detailed structure patterns.

### 3. Write the Contract First

Before implementing, document the complete contract in README.md. See `./contract-specification-template.md` for the template.

Key contract elements:

**Purpose & Scope:**
```markdown
# Module Name

**Purpose:** [One sentence describing what this module does]

**Scope:** [What's included and what's NOT included]

## Contract Summary

- Inputs: [Type and constraints]
- Outputs: [Type and format]
- Side Effects: [Any external changes]
- Dependencies: [Required external libraries]
```

**Public Interface:**
```python
# Specify exact function signatures
def primary_function(input: Type) -> Output:
    """Core functionality with complete docstring"""
```

**Error Handling:**
```markdown
| Error Type | Condition | Recovery Strategy |
|------------|-----------|-------------------|
| ValueError | Invalid input | Return error with details |
```

### 4. Implement with Clear Boundaries

**Public Interface (__init__.py):**
```python
"""
Module: Document Processor

A self-contained module for processing documents.
See README.md for full contract specification.

Basic Usage:
    >>> from document_processor import process_document
    >>> result = process_document(doc)
"""
from .core import process_document, validate_input
from .models import Document, Result

__all__ = ['process_document', 'validate_input', 'Document', 'Result']
```

**Implementation (core.py):**
```python
from typing import Optional
from .models import Document, Result
from .utils import _internal_helper  # Private

def process_document(doc: Document) -> Result:
    """Process a document according to module contract.

    Args:
        doc: Document object containing content and metadata
            Example: Document(content="text", metadata={"source": "web"})

    Returns:
        Result object with processing outcome
            Example: Result(status="success", data={"tokens": 150})

    Raises:
        ValueError: If document content is empty or invalid
        TimeoutError: If processing exceeds 30 second limit

    Examples:
        >>> doc = Document(content="Sample text", metadata={})
        >>> result = process_document(doc)
        >>> assert result.status == "success"
    """
    _internal_helper(doc)
    return Result(...)
```

**Data Models (models.py):**
```python
from pydantic import BaseModel, Field
from typing import Dict, Any

class Document(BaseModel):
    """Public data model for documents.

    Attributes:
        content: The text content to process (1-1,000,000 chars)
        metadata: Optional metadata dictionary

    Example:
        >>> doc = Document(
        ...     content="This is the document text",
        ...     metadata={"source": "api", "timestamp": "2024-01-01"}
        ... )
    """
    content: str = Field(
        min_length=1,
        max_length=1_000_000,
        description="Document text content"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Sample document text",
                "metadata": {"source": "upload", "type": "article"}
            }
        }
```

### 5. Write Tests That Validate Contract

**Contract Validation Tests:**
```python
# tests/test_contract.py
import pytest
from module_name import *

class TestModuleContract:
    def test_public_interface_complete(self):
        """All contracted functions must be exposed"""
        contract = self.load_contract()
        for function in contract["functions"]:
            assert function in dir(module_name)
            assert callable(getattr(module_name, function))

    def test_no_private_exports(self):
        """No private functions in __all__"""
        for name in __all__:
            assert not name.startswith("_")

    def test_input_validation(self):
        """Inputs must be validated per contract"""
        with pytest.raises(ValueError):
            process_document(None)

    def test_output_structure(self):
        """Outputs must match contract structure"""
        doc = Document(content="test", metadata={})
        result = process_document(doc)
        assert hasattr(result, "status")
        assert hasattr(result, "data")
```

**Documentation Tests:**
```python
# tests/test_documentation.py
import pytest
import doctest
from pathlib import Path

class TestDocumentationAccuracy:
    def test_readme_exists(self):
        """README.md must exist"""
        readme = Path("README.md")
        assert readme.exists()
        assert len(readme.read_text()) > 500

    def test_all_public_functions_documented(self):
        """All public functions must have docstrings"""
        for name in public_exports:
            obj = getattr(module_name, name)
            if callable(obj):
                assert obj.__doc__
                assert len(obj.__doc__) > 50

    def test_docstring_examples_work(self):
        """All docstring examples must execute correctly"""
        results = doctest.testmod(module_name, verbose=False)
        assert results.failed == 0
```

## Module Design Patterns

### Simple Input/Output Module

```python
"""
Brick: Text Processor
Purpose: Transform text according to rules
Contract: text in → processed text out
"""

def process(text: str, rules: list[Rule]) -> str:
    """Single public function"""
    for rule in rules:
        text = rule.apply(text)
    return text
```

### Service Module

```python
"""
Brick: Cache Service
Purpose: Store and retrieve cached data
Contract: Key-value operations with TTL
"""

class CacheService:
    def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache"""

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Store in cache"""

    def clear(self):
        """Clear all cache"""
```

### Pipeline Stage Module

```python
"""
Brick: Analysis Stage
Purpose: Analyze documents in pipeline
Contract: Document[] → Analysis[]
"""

async def analyze_batch(
    documents: list[Document],
    config: AnalysisConfig
) -> list[Analysis]:
    """Process documents in parallel"""
    return await asyncio.gather(*[
        analyze_single(doc, config) for doc in documents
    ])
```

## CLI and Tooling

Use CLI tools and Node.js for module support tasks:

### Testing
```bash
# Run all tests
pytest tests/

# Run contract tests specifically
pytest tests/test_contract.py -v

# Run with coverage
pytest --cov=module_name tests/
```

### Documentation Generation
```bash
# Generate API docs from docstrings
python -m pydoc module_name > docs/API.md

# Or use Node.js for custom generation
node scripts/generate-docs.js
```

### Module Validation
```bash
# Check module structure
ls -la module_name/

# Verify public interface
python -c "import module_name; print(module_name.__all__)"

# Run linters
ruff check module_name/
mypy module_name/
```

## Module Quality Criteria

### Self-Containment Score

**High (10/10):**
- All logic inside module directory
- No reaching into other modules' internals
- Tests run without external setup
- Clear boundary between public/private

**Low (3/10):**
- Scattered files across codebase
- Depends on internal details of others
- Tests require complex setup
- Unclear what's public vs private

### Contract Clarity

**Clear Contract:**
- Single responsibility stated
- All inputs/outputs typed
- Side effects documented
- Error cases defined

**Unclear Contract:**
- Multiple responsibilities
- Any/dict types everywhere
- Hidden side effects
- Errors undocumented

## Anti-Patterns to Avoid

### ❌ Leaky Module

```python
# BAD: Exposes internals
from .core import _internal_state, _private_helper
__all__ = ['process', '_internal_state']  # Don't expose internals!
```

### ❌ Coupled Module

```python
# BAD: Reaches into other module
from other_module.core._private import secret_function
```

### ❌ Monster Module

```python
# BAD: Does everything
class DoEverything:
    def process_text(self): ...
    def send_email(self): ...
    def calculate_tax(self): ...
    def render_ui(self): ...
```

## Module Creation Checklist

### Before Coding

- [ ] Define single responsibility
- [ ] Write contract in README.md (MANDATORY)
- [ ] Design public interface with clear documentation
- [ ] Plan test strategy including documentation tests
- [ ] Create module structure with docs/ and examples/ directories

### During Development

- [ ] Keep internals private
- [ ] Write comprehensive docstrings for ALL public functions
- [ ] Include executable examples in docstrings (>>> format)
- [ ] Write tests alongside code
- [ ] Create working examples in examples/ directory
- [ ] Generate API.md if module exposes API
- [ ] Document all error conditions and recovery strategies
- [ ] Document performance characteristics

### After Completion

- [ ] Verify implementation matches specification
- [ ] All tests pass (contract tests, documentation tests, unit tests)
- [ ] Module works in isolation
- [ ] Public interface is clean and minimal
- [ ] Code follows simplicity principles
- [ ] Documentation is complete and accurate
- [ ] Examples run successfully
- [ ] Module can be regenerated from README.md alone

## Regeneration Specification

Every module must be regeneratable from its documentation alone.

Key invariants to preserve:
- Public function signatures
- Input/output data structures
- Error types and conditions
- Side effect behaviors

### Module Specification Template

```yaml
# module.spec.yaml
name: document_processor
version: 1.0.0
purpose: Process documents for synthesis pipeline
documentation:
  readme: required
  api: required_if_public_api
  examples: required
  changelog: required_for_v2+
contract:
  inputs:
    - name: documents
      type: list[Document]
      constraints: "1-1000 items"
  outputs:
    - name: results
      type: list[ProcessResult]
      guarantees: "Same order as input"
  errors:
    - InvalidDocument: "Document validation failed"
    - ProcessingTimeout: "Exceeded 30s limit"
  side_effects:
    - "Writes to cache directory"
    - "Makes API calls to sentiment service"
dependencies:
  - pydantic>=2.0
  - asyncio
testing:
  coverage_target: 90
  documentation_tests: required
  contract_tests: required
```

## Key Implementation Principles

### Build from Specifications

- **Specifications guide implementation** - Follow the contract exactly
- **Focus on functionality** - Make it work correctly first
- **Keep it simple** - Avoid unnecessary complexity
- **Test the contract** - Ensure behavior matches specification

### The Implementation Promise

A well-implemented module:

1. **Matches its specification exactly** - Does what it promises
2. **Works in isolation** - Self-contained with clear boundaries
3. **Can be regenerated** - From specification alone
4. **Is simple and maintainable** - Easy to understand and modify

Build modules like LEGO bricks - self-contained, with clear connection points, ready to be regenerated or replaced. Focus on correct, simple implementation that exactly matches the specification.

## Additional Resources

- `./bricks-and-studs-philosophy.md` - Detailed philosophy and concepts
- `./module-structure-guide.md` - Complete structure patterns and organization
- `./contract-specification-template.md` - Full contract template with examples
- `./templates/README-template.md` - Ready-to-use module README template

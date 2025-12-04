# Module Structure Guide

Complete guide to organizing module directories following the documentation-first, self-contained approach.

## Standard Module Structure

### Complete Structure

```
module_name/
├── __init__.py              # Public interface ONLY
├── README.md                # MANDATORY: Contract specification
├── API.md                   # API reference (if module has HTTP API)
├── CHANGELOG.md             # Version history and breaking changes
├── setup.py or pyproject.toml  # Package configuration
├── requirements.txt         # Dependencies
├── core.py                  # Main implementation logic
├── models.py                # Data structures (Pydantic models)
├── utils.py                 # Internal utilities (prefix with _)
├── config.py                # Configuration with defaults
├── exceptions.py            # Custom exception classes
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # pytest fixtures
│   ├── test_contract.py     # Contract validation tests
│   ├── test_documentation.py  # Documentation accuracy tests
│   ├── test_examples.py     # Verify examples work
│   ├── test_core.py         # Unit tests for core.py
│   ├── test_models.py       # Unit tests for models.py
│   └── fixtures/
│       ├── sample_input.json
│       └── expected_output.json
├── examples/
│   ├── README.md            # Guide to examples
│   ├── basic_usage.py       # Simple getting started example
│   ├── advanced_usage.py    # Complex scenarios
│   ├── integration.py       # How to integrate with other modules
│   └── error_handling.py    # How to handle errors
└── docs/
    ├── architecture.md      # Internal design decisions
    ├── benchmarks.md        # Performance measurements
    ├── troubleshooting.md   # Common issues and solutions
    └── migration.md         # Version migration guides
```

## File-by-File Breakdown

### __init__.py - Public Interface

**Purpose:** Define EXACTLY what is public. Everything else is private.

```python
"""
Module: Document Processor

A self-contained module for processing documents in the synthesis pipeline.

This module provides document processing capabilities with a focus on
performance and maintainability. See README.md for complete contract.

Quick Start:
    >>> from document_processor import process_document, Document
    >>> doc = Document(content="Sample text", metadata={})
    >>> result = process_document(doc)
    >>> print(result.status)
    success

Public Interface:
    - process_document: Main processing function
    - validate_input: Input validation function
    - Document: Input data model
    - Result: Output data model
    - ProcessingError: Exception for processing failures

See Also:
    - README.md: Complete contract specification
    - examples/: Usage examples
    - docs/: Detailed documentation
"""

from .core import process_document, validate_input
from .models import Document, Result
from .exceptions import ProcessingError

# ONLY public exports
__all__ = [
    'process_document',
    'validate_input',
    'Document',
    'Result',
    'ProcessingError',
]

# Module metadata
__version__ = '1.0.0'
__author__ = 'Team Name'
```

**Rules:**
- Only public exports in `__all__`
- No imports of `_private` functions
- Comprehensive module docstring
- Include version and metadata

### README.md - Contract Specification

**Purpose:** Complete, authoritative contract. Module can be regenerated from this alone.

```markdown
# Module Name

**Purpose:** One-sentence description of what this module does.

**Version:** 1.0.0

**Status:** Production

## Overview

Brief (2-3 paragraphs) explanation of:
- What problem this module solves
- How it fits into the larger system
- Key design decisions

## Contract Summary

### Inputs
- **Type:** `Document`
- **Structure:** `{ content: str, metadata: dict }`
- **Constraints:** Content 1-1,000,000 chars
- **Validation:** Raises `ValueError` if invalid

### Outputs
- **Type:** `Result`
- **Structure:** `{ status: str, data: dict }`
- **Format:** Status in ["success", "error"]
- **Example:** `Result(status="success", data={"tokens": 150})`

### Side Effects
- None (pure function)
OR
- Writes to: `/tmp/cache/` directory
- Network calls: `https://api.example.com/sentiment`
- Database: Reads from `documents` table

### Dependencies
- `pydantic>=2.0` - Data validation
- `asyncio` - Async processing

## Public Interface

### Functions

#### `process_document(doc: Document) -> Result`

Process a document according to specifications.

**Parameters:**
- `doc` (Document): Document to process

**Returns:**
- Result: Processing outcome with status and data

**Raises:**
- `ValueError`: Invalid document format
- `TimeoutError`: Processing exceeded 30 seconds
- `ProcessingError`: Processing failed

**Example:**
```python
from document_processor import process_document, Document

doc = Document(content="Sample text", metadata={"source": "api"})
result = process_document(doc)

if result.status == "success":
    print(f"Processed {result.data['tokens']} tokens")
```

### Data Models

#### `Document`

Input document structure.

**Attributes:**
- `content` (str): Document text (1-1M chars)
- `metadata` (dict): Optional metadata

**Example:**
```python
doc = Document(
    content="This is the document content",
    metadata={"source": "upload", "user_id": 123}
)
```

## Error Handling

| Error Type         | Condition                | Recovery Strategy               |
|--------------------|--------------------------|--------------------------------|
| `ValueError`       | Invalid input format     | Validate input, return details |
| `TimeoutError`     | Processing > 30s         | Retry with smaller batch       |
| `ProcessingError`  | Processing failed        | Log error, return error result |
| `ConnectionError`  | External service down    | Use fallback or queue for retry|

## Performance Characteristics

- **Time Complexity:** O(n) where n = content length
- **Memory Usage:** ~100MB per 1000 documents
- **Throughput:** 1000 documents/second
- **Concurrent Requests:** Max 10 simultaneous
- **Rate Limits:** 100 requests/minute

## Configuration

```python
# config.py or environment variables
DOCUMENT_PROCESSOR_CONFIG = {
    "timeout": 30,           # seconds
    "batch_size": 100,       # documents per batch
    "retry_attempts": 3,     # retry on failure
    "max_concurrent": 10,    # max parallel processing
}
```

Environment variables:
- `DOC_PROCESSOR_TIMEOUT` - Override timeout
- `DOC_PROCESSOR_BATCH_SIZE` - Override batch size

## Testing

```bash
# Run all tests
pytest tests/

# Run contract tests only
pytest tests/test_contract.py

# Run with coverage
pytest --cov=document_processor tests/

# Run specific test
pytest tests/test_core.py::test_basic_processing -v
```

## Examples

See `examples/` directory:
- `basic_usage.py` - Simple processing
- `advanced_usage.py` - Complex scenarios
- `integration.py` - Integration patterns
- `error_handling.py` - Error handling

## Regeneration Specification

This module can be completely regenerated from this specification.

**Key Invariants (MUST preserve):**
- Public function signatures
- Input/output data structures
- Error types and conditions
- Side effect behaviors
- Performance characteristics

**Implementation Details (CAN change):**
- Internal algorithms
- Private helper functions
- File organization
- Variable names

## Version History

See `CHANGELOG.md` for detailed version history.

## License

MIT License - See LICENSE file
```

### core.py - Main Implementation

**Purpose:** Primary business logic.

```python
"""
Core implementation of document processing logic.

This module contains the main processing functions.
All functions here should be either:
1. Public (imported in __init__.py)
2. Private (prefixed with _)
"""

from typing import Optional, List
import asyncio
from .models import Document, Result
from .utils import _validate_content, _calculate_tokens
from .config import get_config
from .exceptions import ProcessingError

def process_document(doc: Document) -> Result:
    """
    Process a document according to module contract.

    This is the primary public interface. Processes document content
    and returns structured results.

    Args:
        doc: Document object containing content and metadata
            Example: Document(content="text", metadata={"source": "web"})

    Returns:
        Result object with processing outcome
            Example: Result(status="success", data={"tokens": 150})

    Raises:
        ValueError: If document content is empty or invalid format
        TimeoutError: If processing exceeds configured timeout (default 30s)
        ProcessingError: If document processing fails

    Examples:
        Basic usage:
        >>> doc = Document(content="Sample text", metadata={})
        >>> result = process_document(doc)
        >>> assert result.status == "success"

        With metadata:
        >>> doc = Document(
        ...     content="Important document",
        ...     metadata={"priority": "high"}
        ... )
        >>> result = process_document(doc)
        >>> assert result.data["tokens"] > 0

    Performance:
        - O(n) time complexity where n = len(doc.content)
        - Memory: ~1MB per 10,000 characters
        - Typical duration: < 100ms for 1000 characters
    """
    # Validation
    if not _validate_content(doc.content):
        raise ValueError("Invalid document content")

    # Processing
    try:
        tokens = _calculate_tokens(doc.content)
        processed_data = _process_internal(doc)

        return Result(
            status="success",
            data={
                "tokens": tokens,
                "processed": True,
                "metadata": doc.metadata,
            }
        )
    except Exception as e:
        raise ProcessingError(f"Processing failed: {e}")


def validate_input(doc: Document) -> bool:
    """
    Validate document input.

    Args:
        doc: Document to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> doc = Document(content="test", metadata={})
        >>> assert validate_input(doc) == True
    """
    return _validate_content(doc.content)


# Private functions - NOT exported
def _process_internal(doc: Document) -> dict:
    """Internal processing logic"""
    # Implementation details
    pass


async def _async_helper(items: List[str]) -> List[str]:
    """Internal async helper"""
    # Implementation details
    pass
```

### models.py - Data Structures

**Purpose:** All data models with comprehensive documentation.

```python
"""
Data models for document processing module.

All models use Pydantic for validation and serialization.
These define the public contract for data structures.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime

class Document(BaseModel):
    """
    Public data model for input documents.

    This is the primary input structure for the module.
    All fields are validated using Pydantic.

    Attributes:
        content: The text content to process (1-1,000,000 chars)
        metadata: Optional metadata dictionary for tracking
        created_at: Timestamp of document creation
        source: Optional source identifier

    Examples:
        Basic document:
        >>> doc = Document(content="Sample text")

        With metadata:
        >>> doc = Document(
        ...     content="Important document",
        ...     metadata={"priority": "high", "user_id": 123}
        ... )

        With all fields:
        >>> doc = Document(
        ...     content="Full example",
        ...     metadata={"key": "value"},
        ...     created_at=datetime.now(),
        ...     source="api"
        ... )

    Validation:
        - content must be 1-1,000,000 characters
        - metadata must be a valid dictionary
        - created_at defaults to now if not provided
    """
    content: str = Field(
        min_length=1,
        max_length=1_000_000,
        description="Document text content"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata for document tracking"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Document creation timestamp"
    )
    source: Optional[str] = Field(
        default=None,
        description="Source identifier (api, upload, etc.)"
    )

    @validator('content')
    def content_not_empty(cls, v):
        """Ensure content is not just whitespace"""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Sample document text for processing",
                "metadata": {
                    "source": "upload",
                    "type": "article",
                    "user_id": 123
                },
                "created_at": "2024-01-01T12:00:00",
                "source": "api"
            }
        }


class Result(BaseModel):
    """
    Public data model for processing results.

    This is the output structure returned by process_document().

    Attributes:
        status: Processing status ("success" or "error")
        data: Result data dictionary
        error: Optional error message if status is "error"
        processing_time: Time taken in seconds

    Examples:
        Success result:
        >>> result = Result(
        ...     status="success",
        ...     data={"tokens": 150, "processed": True}
        ... )

        Error result:
        >>> result = Result(
        ...     status="error",
        ...     data={},
        ...     error="Processing failed: invalid format"
        ... )
    """
    status: str = Field(
        description="Processing status (success or error)"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Processing result data"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if status is error"
    )
    processing_time: Optional[float] = Field(
        default=None,
        description="Processing duration in seconds"
    )

    @validator('status')
    def status_must_be_valid(cls, v):
        """Ensure status is one of allowed values"""
        if v not in ["success", "error"]:
            raise ValueError("Status must be 'success' or 'error'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "tokens": 150,
                    "processed": True,
                    "metadata": {}
                },
                "error": None,
                "processing_time": 0.125
            }
        }
```

### config.py - Configuration

```python
"""
Configuration for document processor module.

Provides default configuration with environment variable overrides.
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "timeout": 30,           # seconds
    "batch_size": 100,       # documents per batch
    "retry_attempts": 3,     # retry on failure
    "max_concurrent": 10,    # max parallel processing
    "cache_enabled": True,   # enable caching
    "cache_ttl": 3600,      # cache TTL in seconds
}

def get_config() -> Dict[str, Any]:
    """
    Get configuration with environment variable overrides.

    Environment variables:
    - DOC_PROCESSOR_TIMEOUT: Override timeout
    - DOC_PROCESSOR_BATCH_SIZE: Override batch size
    - DOC_PROCESSOR_RETRY_ATTEMPTS: Override retry attempts
    - DOC_PROCESSOR_MAX_CONCURRENT: Override max concurrent
    - DOC_PROCESSOR_CACHE_ENABLED: Override cache enabled (true/false)
    - DOC_PROCESSOR_CACHE_TTL: Override cache TTL

    Returns:
        Configuration dictionary

    Example:
        >>> config = get_config()
        >>> print(config["timeout"])
        30
    """
    config = DEFAULT_CONFIG.copy()

    # Override with environment variables
    if timeout := os.getenv("DOC_PROCESSOR_TIMEOUT"):
        config["timeout"] = int(timeout)

    if batch_size := os.getenv("DOC_PROCESSOR_BATCH_SIZE"):
        config["batch_size"] = int(batch_size)

    if retry := os.getenv("DOC_PROCESSOR_RETRY_ATTEMPTS"):
        config["retry_attempts"] = int(retry)

    if max_concurrent := os.getenv("DOC_PROCESSOR_MAX_CONCURRENT"):
        config["max_concurrent"] = int(max_concurrent)

    if cache_enabled := os.getenv("DOC_PROCESSOR_CACHE_ENABLED"):
        config["cache_enabled"] = cache_enabled.lower() == "true"

    if cache_ttl := os.getenv("DOC_PROCESSOR_CACHE_TTL"):
        config["cache_ttl"] = int(cache_ttl)

    return config
```

### exceptions.py - Custom Exceptions

```python
"""
Custom exceptions for document processor module.
"""

class ProcessingError(Exception):
    """
    Raised when document processing fails.

    Attributes:
        message: Error description
        document_id: Optional document identifier
        original_error: Optional original exception

    Example:
        >>> raise ProcessingError("Failed to process document", document_id="doc_123")
    """
    def __init__(self, message: str, document_id: str = None, original_error: Exception = None):
        self.message = message
        self.document_id = document_id
        self.original_error = original_error
        super().__init__(self.message)


class ValidationError(Exception):
    """
    Raised when input validation fails.

    Example:
        >>> raise ValidationError("Content exceeds maximum length")
    """
    pass
```

## Testing Structure

### test_contract.py

```python
"""
Contract validation tests.

These tests ensure the module adheres to its public contract.
"""

import pytest
from document_processor import *

class TestPublicInterface:
    """Test that public interface is complete and correct"""

    def test_all_exports_present(self):
        """All documented exports must be available"""
        expected_exports = [
            'process_document',
            'validate_input',
            'Document',
            'Result',
            'ProcessingError',
        ]
        for export in expected_exports:
            assert export in dir(), f"Missing export: {export}"

    def test_no_private_exports(self):
        """No private functions should be exported"""
        from document_processor import __all__
        for name in __all__:
            assert not name.startswith('_'), f"Private export: {name}"


class TestInputOutputContract:
    """Test input/output contract"""

    def test_process_document_signature(self):
        """Verify function signature matches contract"""
        import inspect
        sig = inspect.signature(process_document)
        assert 'doc' in sig.parameters
        assert sig.return_annotation != inspect.Signature.empty

    def test_valid_input_produces_result(self):
        """Valid input produces Result object"""
        doc = Document(content="test", metadata={})
        result = process_document(doc)
        assert isinstance(result, Result)
        assert hasattr(result, 'status')
        assert hasattr(result, 'data')

    def test_invalid_input_raises_valueerror(self):
        """Invalid input raises ValueError as contracted"""
        with pytest.raises(ValueError):
            Document(content="")  # Empty content
```

### test_documentation.py

```python
"""
Documentation accuracy tests.

Verify that documentation matches implementation.
"""

import pytest
import doctest
from pathlib import Path

class TestDocumentation:
    """Validate documentation accuracy"""

    def test_readme_exists(self):
        """README.md must exist and be comprehensive"""
        readme = Path("README.md")
        assert readme.exists(), "README.md is mandatory"
        content = readme.read_text()
        assert len(content) > 500, "README must be comprehensive"
        assert "Contract Summary" in content
        assert "Public Interface" in content

    def test_docstring_examples_work(self):
        """All docstring examples must execute correctly"""
        import document_processor
        results = doctest.testmod(document_processor, verbose=False)
        assert results.failed == 0, f"{results.failed} docstring examples failed"

    def test_all_public_functions_documented(self):
        """All public functions must have docstrings"""
        from document_processor import __all__
        import document_processor
        for name in __all__:
            obj = getattr(document_processor, name)
            if callable(obj):
                assert obj.__doc__, f"{name} missing docstring"
                assert len(obj.__doc__) > 50, f"{name} docstring too brief"
```

## Summary

This structure ensures:
- **Self-containment**: Everything module needs is inside directory
- **Clear contracts**: README.md defines complete interface
- **Documentation-first**: Docs written before/during implementation
- **Testability**: Contract and documentation tests validate accuracy
- **Regeneratable**: Module can be rebuilt from specifications
- **Maintainable**: Clear organization, comprehensive docs, isolated code

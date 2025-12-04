# Bricks and Studs Philosophy

This document explains the core philosophy behind the modular implementation approach, inspired by LEGO's "bricks and studs" design system.

## The LEGO Analogy

Just as LEGO bricks are:
- **Self-contained** units with consistent dimensions
- **Connected** via standardized studs
- **Replaceable** without affecting other bricks
- **Composable** into larger structures

Software modules should be:
- **Self-contained** directories with clear boundaries
- **Connected** via public contracts (APIs)
- **Replaceable** through regeneration from specs
- **Composable** into larger systems

## What is a "Brick"?

A **brick** is a self-contained module/directory that:

### Has ONE Clear Responsibility
```
Good Examples:
- document_processor/  → Processes documents
- cache_service/       → Manages caching
- auth_validator/      → Validates authentication

Bad Examples:
- utils/               → Too vague
- helpers/             → Multiple responsibilities
- common/              → Unclear scope
```

### Contains Everything It Needs
```
document_processor/
├── __init__.py        # Public interface
├── README.md          # Contract specification
├── core.py            # Implementation
├── models.py          # Data structures
├── tests/             # All tests
│   └── fixtures/      # Test data
└── examples/          # Usage examples
```

All code, tests, and documentation live inside the brick's directory.

### Works in Isolation
```python
# Can be tested independently
cd document_processor/
pytest tests/

# Can be imported cleanly
from document_processor import process_document

# Can be moved/copied
cp -r document_processor/ other_project/
```

### Has Clear Boundaries
```python
# Public interface (__init__.py)
from .core import process_document  # Public
from .models import Document        # Public

__all__ = ['process_document', 'Document']

# Private stays private
# .core._internal_helper is NOT exported
```

## What is a "Stud"?

A **stud** is a public contract that other modules connect to:

### Function Signatures
```python
def process_document(doc: Document) -> Result:
    """
    Contract (Stud):
    - Input: Document object
    - Output: Result object
    - Errors: ValueError, TimeoutError
    - Side effects: None
    """
```

### Data Models
```python
class Document(BaseModel):
    """
    Contract (Stud):
    - content: str (1-1M chars)
    - metadata: dict (optional)
    """
    content: str
    metadata: Dict[str, Any] = {}
```

### API Endpoints
```python
@app.post("/api/process")
def process_endpoint(doc: DocumentInput) -> DocumentOutput:
    """
    Contract (Stud):
    - Endpoint: POST /api/process
    - Input: JSON matching DocumentInput
    - Output: JSON matching DocumentOutput
    - Status: 200 success, 400 invalid, 500 error
    """
```

### Configuration
```python
# config.py
DEFAULT_CONFIG = {
    "timeout": 30,      # Contract: Always has timeout
    "batch_size": 100,  # Contract: Always has batch_size
}
```

## What is "Regeneratable"?

A module is **regeneratable** when it can be completely rebuilt from its specification without breaking connections to other modules.

### Why This Matters

```
Scenario: You need to refactor document_processor's internal implementation

Without Regeneration Contract:
❌ Change internal logic → Public API changes → All callers break
❌ Fear of change → Technical debt accumulates
❌ Modules become entangled

With Regeneration Contract:
✅ Specification defines public API → Internal changes safe
✅ Confident refactoring → Better implementation
✅ Modules stay independent
```

### How to Make Modules Regeneratable

**1. Comprehensive README.md:**
```markdown
# Document Processor

## Contract
- Input: Document(content: str, metadata: dict)
- Output: Result(status: str, data: dict)
- Errors: ValueError (invalid input), TimeoutError (> 30s)
- Side Effects: None

## Public Interface
- process_document(doc: Document) -> Result
- validate_input(doc: Document) -> bool

## Performance Guarantees
- Processing: O(n) where n = content length
- Memory: < 100MB per document
- Timeout: 30 seconds max
```

**2. Explicit Contract Tests:**
```python
# tests/test_contract.py
def test_input_output_contract():
    """Verify contract is maintained"""
    doc = Document(content="test", metadata={})
    result = process_document(doc)

    # These assertions define the contract
    assert isinstance(result, Result)
    assert hasattr(result, "status")
    assert hasattr(result, "data")
    assert result.status in ["success", "error"]
```

**3. Version-Controlled Specifications:**
```yaml
# module.spec.yaml - Lives in version control
name: document_processor
version: 2.0.0
contract:
  public_functions:
    - process_document
    - validate_input
  public_models:
    - Document
    - Result
  backwards_compatibility:
    - "v2 maintains v1 function signatures"
    - "Added optional 'timeout' parameter in v2"
```

### Regeneration Example

```
Day 1: Initial Implementation
document_processor/
└── core.py  (100 lines, simple implementation)

Day 30: Performance Issues
Specification says: "O(n) processing, < 100MB memory"
Current implementation: O(n²), 500MB memory

Action: REGENERATE
1. Read README.md contract
2. Rewrite core.py with better algorithm
3. Keep public interface EXACTLY the same
4. Run contract tests → All pass ✅
5. Callers still work without changes ✅

Result: Better implementation, zero breaking changes
```

## What is "Isolated"?

**Isolated** means the module doesn't reach into other modules' internals and doesn't expose its own internals.

### Good Isolation

```python
# document_processor/__init__.py
from .core import process_document  # Expose public function
from .models import Document        # Expose public model

__all__ = ['process_document', 'Document']

# usage_analyzer/__init__.py
from document_processor import process_document  # Use public interface
```

### Bad Isolation

```python
# ❌ BAD: Reaching into internals
from document_processor.core._private_helper import secret_function

# ❌ BAD: Exposing internals
from .core import _internal_state
__all__ = ['process_document', '_internal_state']

# ❌ BAD: Tight coupling
from document_processor.core import _cache
_cache.clear()  # Don't touch other module's internals!
```

### Benefits of Isolation

**1. Fearless Refactoring:**
```
If internals are truly private:
→ Can rename variables
→ Can change algorithms
→ Can restructure files
→ Nothing breaks outside module
```

**2. Easy Testing:**
```bash
# Isolated modules test independently
cd document_processor/
pytest tests/  # No setup, no external dependencies
```

**3. Team Parallelization:**
```
Team A works on document_processor/
Team B works on usage_analyzer/
→ No conflicts if isolation maintained
→ No coordination needed beyond contract
```

**4. Module Replacement:**
```
Want to try new implementation?
1. Copy document_processor/ → document_processor_v2/
2. Implement new approach
3. Run contract tests
4. If pass: swap modules
5. If fail: keep original
→ Risk-free experimentation
```

## Putting It All Together

### The Complete Picture

```
System Architecture:

┌─────────────────────┐
│  usage_analyzer/    │  ← Brick 1
│  - Uses process_doc │  ← Connects via stud
└─────────────────────┘
          ↓ (Public API - Stud)
┌─────────────────────┐
│  document_processor/│  ← Brick 2
│  - Isolated         │  ← Self-contained
│  - Regeneratable    │  ← Can rebuild internals
└─────────────────────┘
          ↓ (Public API - Stud)
┌─────────────────────┐
│  cache_service/     │  ← Brick 3
│  - Clear contract   │  ← Defines studs
└─────────────────────┘
```

### Module Checklist

Is your module a good "brick"?

- [ ] Has ONE clear responsibility
- [ ] All code inside module directory
- [ ] Public interface in `__all__`
- [ ] Private functions start with `_`
- [ ] Tests in module's tests/ directory
- [ ] Can be tested in isolation
- [ ] README.md documents contract
- [ ] Contract tests validate interface
- [ ] Can be regenerated from README.md
- [ ] Doesn't reach into other modules
- [ ] Doesn't expose internals

If all checked: ✅ Good brick! If any unchecked: Review design.

## Philosophy in Practice

### Start with the Contract

```
Wrong Order:
1. Write code
2. Figure out API later
3. Documentation as afterthought
→ Result: Unclear boundaries, leaky abstractions

Right Order:
1. Write README.md (contract first)
2. Write contract tests
3. Implement to pass tests
4. Refine implementation (contract stays stable)
→ Result: Clear boundaries, stable interfaces
```

### Think in Studs, Not Internals

```
Question: "How should modules communicate?"

Think in Studs:
✅ "Module A calls process_document(doc)"
✅ "Contract: Document in, Result out"
✅ "Error handling via exceptions"

Don't Think in Internals:
❌ "Module A needs the _cache variable"
❌ "Module A will directly modify _state"
❌ "Module A should call _private_helper"
```

### Design for Regeneration

```
Before Every Implementation:
Ask: "If I rebuild this from scratch, what MUST stay the same?"

Answer: The Contract (Studs)
- Public function signatures
- Data model structures
- Error types
- Side effects
- Performance characteristics

Everything Else: Can Change
- Internal algorithms
- Private helpers
- File organization
- Variable names
```

## Summary

The "bricks and studs" philosophy creates software that is:

- **Modular** - Clear boundaries, single responsibilities
- **Maintainable** - Fearless refactoring within modules
- **Testable** - Isolated testing without complex setup
- **Evolvable** - Regenerate internals, keep contracts
- **Collaborative** - Teams work independently on bricks
- **Composable** - Connect bricks via well-defined studs

Build software like LEGO: One brick at a time, connected by reliable studs, composable into anything.

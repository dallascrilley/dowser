# Acuity Schedule Manager - Test Suite

Comprehensive test suite for the Acuity Schedule Manager skill, including unit tests for validation functions and integration tests for API workflows.

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
./tests/run_tests.sh

# Run specific test types
./tests/run_tests.sh unit          # Unit tests only
./tests/run_tests.sh integration   # Integration tests (mocked)
./tests/run_tests.sh coverage      # With coverage report
```

## Test Structure

```
tests/
├── unit/                      # Unit tests (fast, no external dependencies)
│   ├── test_validators.py     # Validation function tests
│   └── __init__.py
├── integration/               # Integration tests (API workflows)
│   ├── test_api_workflows.py  # Complete workflow tests
│   └── __init__.py
├── conftest.py                # Shared fixtures and configuration
├── pytest.ini                 # Pytest configuration
├── run_tests.sh               # Test runner script
└── README.md                  # This file
```

## Unit Tests

**Location:** `tests/unit/test_validators.py`

### Email Validation Tests
- Valid email formats (standard, with plus, subdomains)
- Invalid email formats (missing @, incomplete domain)

### Phone Validation Tests
- Valid phone formats (various separators, international)
- Invalid phone formats (too short, non-numeric, empty)

### Datetime Validation Tests
- Valid ISO 8601 formats with timezone
- Invalid datetime formats

### Appointment Data Validation Tests
- Complete valid appointment data
- Missing required fields detection
- Invalid email detection
- Invalid datetime detection
- Type validation

### Timezone Validation Tests
- Valid IANA timezone strings
- Invalid timezone abbreviations

### Rate Limiting Tests
- Exponential backoff calculation
- Maximum delay capping

**Run unit tests:**
```bash
pytest tests/unit/ -v
```

## Integration Tests

**Location:** `tests/integration/test_api_workflows.py`

### Authentication Workflow Tests
- Successful authentication
- Invalid credentials handling

### Availability Check Workflow Tests
- Retrieve appointment types
- Check availability for specific date
- Handle no availability scenarios

### Appointment Creation Workflow Tests
- Successful appointment creation
- Pre-validation workflow (check availability → create)
- Conflict handling (409 status)

### Rate Limiting Workflow Tests
- Detect rate limit (429) responses
- Exponential backoff retry logic

### Error Handling Workflow Tests
- Network error handling
- Invalid JSON response handling

### Batch Operations Tests
- Paginated appointment retrieval
- Offset-based pagination logic

### Real API Integration Tests (Optional)
- **Requires credentials:** Set `ACUITY_USER_ID` and `ACUITY_API_KEY`
- Tests against actual Acuity API
- Marked with `@pytest.mark.integration`
- Skipped by default

**Run integration tests:**
```bash
# With mocked responses (default)
pytest tests/integration/ -v

# Against real API (requires credentials)
export ACUITY_USER_ID="12345678"
export ACUITY_API_KEY="your_api_key"
pytest tests/integration/ -v -m integration
```

## Test Runner Usage

The `run_tests.sh` script provides convenient test execution with colored output:

```bash
# Run all tests
./tests/run_tests.sh

# Run specific test type
./tests/run_tests.sh unit          # Unit tests only (fast)
./tests/run_tests.sh integration   # Integration tests (mocked)
./tests/run_tests.sh real          # Real API tests (requires credentials)
./tests/run_tests.sh coverage      # With coverage report

# Help
./tests/run_tests.sh help
```

## Test Fixtures

Shared test fixtures are defined in `conftest.py`:

### `test_credentials`
Provides test credentials (mock or from environment):
```python
def test_something(test_credentials):
    user_id = test_credentials['user_id']
    api_key = test_credentials['api_key']
```

### `sample_appointment_data`
Complete valid appointment data structure:
```python
def test_create_appointment(sample_appointment_data):
    # sample_appointment_data contains all required fields
    response = create_appointment(sample_appointment_data)
```

### `sample_availability_response`
Mock availability API response:
```python
def test_availability(sample_availability_response):
    # sample_availability_response contains mock time slots
    assert len(sample_availability_response) > 0
```

### `mock_successful_appointment_creation`
Mock successful appointment creation response:
```python
def test_appointment_created(mock_successful_appointment_creation):
    # Contains appointment ID, confirmation code, etc.
    assert 'confirmationCode' in mock_successful_appointment_creation
```

## Writing New Tests

### Unit Test Template

```python
class TestNewValidation:
    """Test new validation function"""

    @staticmethod
    def validate_something(data):
        """Your validation function"""
        return True  # Implement validation logic

    def test_valid_input(self):
        """Test valid input"""
        assert self.validate_something("valid_data")

    def test_invalid_input(self):
        """Test invalid input"""
        assert not self.validate_something("invalid_data")
```

### Integration Test Template

```python
class TestNewWorkflow:
    """Test new API workflow"""

    def test_workflow_success(self, mock_api_session):
        """Test successful workflow execution"""
        # Step 1: Setup
        # Step 2: Execute workflow
        # Step 3: Assert results
        pass

    def test_workflow_error_handling(self):
        """Test error handling in workflow"""
        # Test error scenarios
        pass
```

## Coverage Report

Generate HTML coverage report:

```bash
./tests/run_tests.sh coverage
```

View report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
          pip install -r requirements.txt
      - name: Run tests
        run: ./tests/run_tests.sh all
```

## Testing Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for common setup
- Clean up resources after tests

### 2. Mock External Dependencies
- Don't make real API calls in unit tests
- Use `unittest.mock` for external services
- Save real API tests for integration suite

### 3. Test Edge Cases
- Empty inputs
- Invalid formats
- Boundary conditions
- Error scenarios

### 4. Descriptive Test Names
```python
# Good
def test_email_validation_rejects_missing_at_symbol():
    pass

# Avoid
def test_email():
    pass
```

### 5. Use Fixtures for Setup
```python
@pytest.fixture
def authenticated_client():
    client = AcuityClient()
    client.authenticate(user_id, api_key)
    return client
```

### 6. Test One Thing Per Test
```python
# Good: Focused test
def test_create_appointment_returns_confirmation_code():
    appointment = create_appointment(data)
    assert 'confirmationCode' in appointment

# Avoid: Testing multiple things
def test_appointment_creation():
    appointment = create_appointment(data)
    assert 'confirmationCode' in appointment
    assert appointment['firstName'] == 'John'
    assert appointment['email'] == 'john@example.com'
    # Too many assertions
```

## Troubleshooting Tests

### Tests Failing with "ModuleNotFoundError"
```bash
# Ensure you're running tests from project root
cd ~/.claude/skills/acuity-schedule-manager
pytest tests/
```

### Tests Skipped (Integration Tests)
```bash
# Integration tests require credentials
export ACUITY_USER_ID="12345678"
export ACUITY_API_KEY="your_api_key"
pytest tests/integration/ -v -m integration
```

### Pytest Not Found
```bash
# Install pytest
pip install pytest pytest-cov pytest-mock
```

### Coverage Report Not Generated
```bash
# Install coverage plugin
pip install pytest-cov

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html
```

## Test Markers

Tests can be marked for selective execution:

```python
@pytest.mark.integration
def test_real_api():
    """Requires real API credentials"""
    pass

@pytest.mark.slow
def test_long_running():
    """Takes more than 10 seconds"""
    pass
```

Run specific markers:
```bash
# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## See Also

- [../SKILL.md](../SKILL.md) - Main skill documentation
- [../scripts/README.md](../scripts/README.md) - Helper scripts documentation
- [../examples/README.md](../examples/README.md) - Usage examples
- [pytest documentation](https://docs.pytest.org/)

#!/bin/bash
# Test Runner for Acuity Schedule Manager

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Acuity Schedule Manager - Test Runner"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-cov"
    exit 1
fi

# Function to run tests
run_tests() {
    local test_type=$1
    local test_path=$2
    local description=$3

    echo -e "${YELLOW}Running ${description}...${NC}"
    if pytest ${test_path} -v; then
        echo -e "${GREEN}✓ ${description} passed${NC}"
        return 0
    else
        echo -e "${RED}✗ ${description} failed${NC}"
        return 1
    fi
}

# Parse command line arguments
TEST_TYPE=${1:-all}

case $TEST_TYPE in
    unit)
        echo "Running unit tests only..."
        run_tests "unit" "tests/unit/" "Unit Tests"
        ;;

    integration)
        echo "Running integration tests..."
        if [ -z "$ACUITY_USER_ID" ] || [ -z "$ACUITY_API_KEY" ]; then
            echo -e "${YELLOW}Warning: ACUITY_USER_ID and ACUITY_API_KEY not set${NC}"
            echo "Integration tests will run with mocked responses only"
            echo "Set credentials to test against real API"
        fi
        run_tests "integration" "tests/integration/" "Integration Tests"
        ;;

    real)
        echo "Running tests against REAL API..."
        if [ -z "$ACUITY_USER_ID" ] || [ -z "$ACUITY_API_KEY" ]; then
            echo -e "${RED}Error: ACUITY_USER_ID and ACUITY_API_KEY must be set${NC}"
            exit 1
        fi
        run_tests "real" "tests/integration/test_api_workflows.py::TestRealAPIIntegration" "Real API Integration Tests" -m integration
        ;;

    coverage)
        echo "Running tests with coverage report..."
        pytest tests/ --cov=scripts --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;

    all)
        echo "Running all tests..."
        FAILED=0

        run_tests "unit" "tests/unit/" "Unit Tests" || FAILED=1
        echo ""

        run_tests "integration" "tests/integration/" "Integration Tests (mocked)" || FAILED=1
        echo ""

        if [ $FAILED -eq 0 ]; then
            echo -e "${GREEN}=========================================="
            echo -e "All tests passed! ✓"
            echo -e "==========================================${NC}"
        else
            echo -e "${RED}=========================================="
            echo -e "Some tests failed ✗"
            echo -e "==========================================${NC}"
            exit 1
        fi
        ;;

    *)
        echo "Usage: $0 [unit|integration|real|coverage|all]"
        echo ""
        echo "Options:"
        echo "  unit        - Run unit tests only (fast)"
        echo "  integration - Run integration tests with mocked responses"
        echo "  real        - Run integration tests against real API (requires credentials)"
        echo "  coverage    - Run all tests with coverage report"
        echo "  all         - Run all tests (default)"
        echo ""
        echo "Examples:"
        echo "  $0                  # Run all tests"
        echo "  $0 unit             # Run unit tests only"
        echo "  $0 coverage         # Generate coverage report"
        echo ""
        echo "For real API tests, set environment variables:"
        echo "  export ACUITY_USER_ID=12345678"
        echo "  export ACUITY_API_KEY=your_api_key"
        echo "  $0 real"
        exit 1
        ;;
esac

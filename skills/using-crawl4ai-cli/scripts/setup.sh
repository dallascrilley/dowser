#!/usr/bin/env bash
#
# Crawl4AI CLI Setup Script
#
# This script verifies crawl4ai installation and installs required Playwright browsers.
# Run this script after installing crawl4ai to ensure everything is properly configured.
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Main setup
print_header "Crawl4AI CLI Setup"

# Step 1: Check if crwl is installed
print_info "Step 1: Checking if crwl is installed..."
if ! command -v crwl &> /dev/null; then
    print_error "crwl command not found"
    echo ""
    echo "Please install crawl4ai first:"
    echo "  pip install crawl4ai"
    echo "  # or"
    echo "  uv pip install crawl4ai"
    echo ""
    exit 1
fi

CRWL_PATH=$(which crwl)
print_success "Found crwl at: $CRWL_PATH"

# Step 2: Verify crwl help works
print_info "Step 2: Verifying crwl installation..."
if crwl --help > /dev/null 2>&1; then
    print_success "crwl --help works correctly"
else
    print_error "crwl --help failed"
    echo ""
    echo "Try running: crwl --help"
    echo "If you see errors, crwl may not be properly installed."
    echo ""
    exit 1
fi

# Step 3: Detect Python path
print_info "Step 3: Detecting Python version used by crwl..."
PYTHON_PATH=$(head -1 "$CRWL_PATH" | sed 's/#!//')

if [ ! -x "$PYTHON_PATH" ]; then
    print_error "Python executable not found at: $PYTHON_PATH"
    echo ""
    echo "The crwl script references a Python that doesn't exist."
    echo "You may need to reinstall crawl4ai."
    echo ""
    exit 1
fi

PYTHON_VERSION=$($PYTHON_PATH --version 2>&1)
print_success "Python found: $PYTHON_VERSION"
print_info "Python path: $PYTHON_PATH"

# Step 4: Check if Playwright module is available
print_info "Step 4: Checking if Playwright is installed..."
if ! $PYTHON_PATH -m playwright --version &> /dev/null; then
    print_error "Playwright module not found for this Python installation"
    echo ""
    echo "Installing Playwright module first..."
    $PYTHON_PATH -m pip install playwright
fi

PLAYWRIGHT_VERSION=$($PYTHON_PATH -m playwright --version)
print_success "Playwright module found: $PLAYWRIGHT_VERSION"

# Step 5: Install Playwright browsers
print_info "Step 5: Installing Playwright Chromium browser..."
echo ""
print_warning "This will download ~130MB. It may take a minute..."
echo ""

if $PYTHON_PATH -m playwright install chromium; then
    print_success "Chromium browser installed successfully"
else
    print_error "Failed to install Chromium browser"
    echo ""
    echo "Try running manually:"
    echo "  $PYTHON_PATH -m playwright install chromium"
    echo ""
    exit 1
fi

# Step 6: Test crawl4ai
print_info "Step 6: Testing crawl4ai with a simple request..."
echo ""

TEST_OUTPUT=$(crwl https://example.com -o markdown 2>&1 | head -20)
if echo "$TEST_OUTPUT" | grep -q "Example Domain"; then
    print_success "Test successful! Crawl4ai is working correctly."
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Setup Complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    print_info "You can now use crawl4ai. Try these commands:"
    echo ""
    echo "  # View page content"
    echo "  crwl https://example.com -o markdown"
    echo ""
    echo "  # Extract data (see documentation for schema setup)"
    echo "  crwl https://example.com -e extract_css.yml -s schema.json -o json"
    echo ""
    echo "  # Ask questions about content"
    echo "  crwl https://example.com -q \"What is this page about?\""
    echo ""
    exit 0
else
    print_error "Test failed. Here's the output:"
    echo ""
    echo "$TEST_OUTPUT"
    echo ""
    print_warning "Setup may not be complete. Please check the error messages above."
    exit 1
fi

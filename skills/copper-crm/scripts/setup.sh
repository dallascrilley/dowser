#!/bin/bash

set -euo pipefail

################################################################################
# Copper CRM Skill Setup Script
#
# This script sets up the Copper CRM skill by:
# 1. Checking Python 3.11+ installation
# 2. Installing required dependencies
# 3. Configuring .env file with API credentials
# 4. Testing API connection
# 5. Caching metadata (users, custom fields, pipelines)
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CACHE_DIR="${HOME}/.claude/skills/copper-crm/.cache"
ENV_FILE="${SKILL_DIR}/.env"
ENV_EXAMPLE="${SKILL_DIR}/.env.example"

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

separator() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

exit_error() {
    log_error "$1"
    exit 1
}

################################################################################
# 1. Check Python Version
################################################################################

check_python() {
    log_info "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        exit_error "Python 3 is not installed. Please install Python 3.11 or higher."
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

    if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 11 ]]; then
        exit_error "Python $PYTHON_VERSION detected, but Python 3.11+ is required."
    fi

    log_success "Python $PYTHON_VERSION found"
}

################################################################################
# 2. Create Cache Directory
################################################################################

create_cache_dir() {
    log_info "Creating cache directory..."

    if [[ ! -d "$CACHE_DIR" ]]; then
        mkdir -p "$CACHE_DIR"
        log_success "Cache directory created at $CACHE_DIR"
    else
        log_success "Cache directory already exists"
    fi
}

################################################################################
# 3. Install Dependencies
################################################################################

install_dependencies() {
    log_info "Installing required Python dependencies..."

    DEPS=("requests" "python-dotenv" "rich")

    for dep in "${DEPS[@]}"; do
        if python3 -c "import ${dep//'-'/'_'}" 2>/dev/null; then
            log_success "$dep already installed"
        else
            log_info "Installing $dep..."
            python3 -m pip install -q "$dep" || exit_error "Failed to install $dep"
            log_success "$dep installed"
        fi
    done
}

################################################################################
# 4. Setup .env File
################################################################################

setup_env_file() {
    log_info "Setting up .env configuration..."

    if [[ ! -f "$ENV_FILE" ]]; then
        if [[ ! -f "$ENV_EXAMPLE" ]]; then
            log_warn ".env.example not found, creating basic .env template..."
            cat > "$ENV_FILE" << 'EOF'
# Copper CRM API Configuration
COPPER_API_KEY=your_api_key_here
COPPER_API_EMAIL=your_email@example.com
EOF
        else
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            log_success "Created .env from .env.example"
        fi
    else
        log_success ".env file already exists"
    fi

    # Prompt for credentials if not already configured
    if ! grep -q "^COPPER_API_KEY=your_api_key" "$ENV_FILE" 2>/dev/null; then
        log_success ".env appears to be configured already"
        return 0
    fi

    separator
    echo
    log_info "Please configure your Copper CRM API credentials:"
    echo

    read -p "Enter your Copper CRM API Key (from https://www.coppercrm.com/settings/api): " api_key
    if [[ -z "$api_key" ]]; then
        exit_error "API Key is required"
    fi

    read -p "Enter your Copper CRM API Email: " api_email
    if [[ -z "$api_email" ]]; then
        exit_error "API Email is required"
    fi

    # Update .env file
    sed -i.bak "s|^COPPER_API_KEY=.*|COPPER_API_KEY=$api_key|" "$ENV_FILE"
    sed -i.bak "s|^COPPER_API_EMAIL=.*|COPPER_API_EMAIL=$api_email|" "$ENV_FILE"
    rm -f "${ENV_FILE}.bak"

    log_success "Credentials saved to .env"
    echo
}

################################################################################
# 5. Test API Connection
################################################################################

test_api_connection() {
    log_info "Testing API connection..."

    # Source the .env file
    if [[ -f "$ENV_FILE" ]]; then
        set +a
        source "$ENV_FILE"
        set -a
    fi

    if [[ -z "${COPPER_API_KEY:-}" ]] || [[ -z "${COPPER_API_EMAIL:-}" ]]; then
        log_warn "Skipping API test: credentials not configured"
        return 0
    fi

    # Create a Python test script
    TEST_SCRIPT=$(mktemp)
    cat > "$TEST_SCRIPT" << 'PYTHON_EOF'
import os
import sys
import requests
from requests.auth import HTTPBasicAuth

api_key = os.getenv('COPPER_API_KEY')
api_email = os.getenv('COPPER_API_EMAIL')
api_url = 'https://api.copper.com/developer_api/v1'

try:
    auth = HTTPBasicAuth(api_email, api_key)
    headers = {'X-PW-AccessToken': api_key, 'X-PW-UserEmail': api_email, 'Content-Type': 'application/json'}
    response = requests.get(f'{api_url}/account', headers=headers, timeout=5)

    if response.status_code == 200:
        print("SUCCESS")
        sys.exit(0)
    elif response.status_code == 401:
        print("INVALID_CREDENTIALS")
        sys.exit(1)
    else:
        print(f"ERROR_{response.status_code}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("CONNECTION_ERROR")
    sys.exit(1)
except Exception as e:
    print(f"EXCEPTION: {str(e)}")
    sys.exit(1)
PYTHON_EOF

    TEST_RESULT=$(python3 "$TEST_SCRIPT" 2>&1 || true)
    rm -f "$TEST_SCRIPT"

    case "$TEST_RESULT" in
        SUCCESS)
            log_success "API connection test passed"
            return 0
            ;;
        INVALID_CREDENTIALS)
            exit_error "API credentials are invalid. Please check your API Key and Email."
            ;;
        CONNECTION_ERROR)
            exit_error "Cannot connect to Copper CRM API. Please check your internet connection."
            ;;
        *)
            log_warn "API test inconclusive: $TEST_RESULT"
            return 0
            ;;
    esac
}

################################################################################
# 6. Cache Metadata
################################################################################

cache_metadata() {
    log_info "Caching Copper CRM metadata..."

    # Source the .env file
    if [[ -f "$ENV_FILE" ]]; then
        set +a
        source "$ENV_FILE"
        set -a
    fi

    if [[ -z "${COPPER_API_KEY:-}" ]] || [[ -z "${COPPER_API_EMAIL:-}" ]]; then
        log_warn "Skipping metadata cache: credentials not configured"
        return 0
    fi

    # Create a Python caching script
    CACHE_SCRIPT=$(mktemp)
    cat > "$CACHE_SCRIPT" << 'PYTHON_EOF'
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

api_key = os.getenv('COPPER_API_KEY')
api_email = os.getenv('COPPER_API_EMAIL')
api_url = 'https://api.copper.com/developer_api/v1'
cache_dir = os.path.expanduser('~/.claude/skills/copper-crm/.cache')

headers = {
    'X-PW-AccessToken': api_key,
    'X-PW-UserEmail': api_email,
    'Content-Type': 'application/json'
}

Path(cache_dir).mkdir(parents=True, exist_ok=True)

metadata = {
    'cached_at': datetime.utcnow().isoformat(),
    'users': [],
    'custom_fields': [],
    'pipelines': []
}

try:
    # Fetch users
    print("Fetching users...", file=sys.stderr)
    response = requests.get(f'{api_url}/people', headers=headers, timeout=10)
    if response.status_code == 200:
        metadata['users'] = response.json() if isinstance(response.json(), list) else []
        print(f"  Cached {len(metadata['users'])} users", file=sys.stderr)

    # Fetch custom fields
    print("Fetching custom fields...", file=sys.stderr)
    response = requests.get(f'{api_url}/custom_fields', headers=headers, timeout=10)
    if response.status_code == 200:
        metadata['custom_fields'] = response.json() if isinstance(response.json(), list) else []
        print(f"  Cached {len(metadata['custom_fields'])} custom fields", file=sys.stderr)

    # Fetch pipelines
    print("Fetching pipelines...", file=sys.stderr)
    response = requests.get(f'{api_url}/pipelines', headers=headers, timeout=10)
    if response.status_code == 200:
        metadata['pipelines'] = response.json() if isinstance(response.json(), list) else []
        print(f"  Cached {len(metadata['pipelines'])} pipelines", file=sys.stderr)

    # Save cache
    cache_file = os.path.join(cache_dir, 'metadata.json')
    with open(cache_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata cached to {cache_file}", file=sys.stderr)
    sys.exit(0)

except Exception as e:
    print(f"Warning: Failed to cache metadata: {str(e)}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF

    if python3 "$CACHE_SCRIPT" 2>&1; then
        log_success "Metadata cached successfully"
    else
        log_warn "Metadata caching had issues, but setup will continue"
    fi

    rm -f "$CACHE_SCRIPT"
}

################################################################################
# 7. Display Success Message
################################################################################

display_summary() {
    separator
    echo
    log_success "Copper CRM Skill Setup Complete!"
    echo
    echo -e "Next steps:"
    echo -e "  1. Review and validate your configuration:"
    echo -e "     ${BLUE}cat $ENV_FILE${NC}"
    echo
    echo -e "  2. View cached metadata:"
    echo -e "     ${BLUE}cat $CACHE_DIR/metadata.json${NC}"
    echo
    echo -e "  3. Start using the skill:"
    echo -e "     ${BLUE}claude skill use copper-crm${NC}"
    echo
    echo -e "For help and documentation, see:"
    echo -e "  ${BLUE}$SKILL_DIR/README.md${NC}"
    echo
    separator
}

################################################################################
# Main Execution
################################################################################

main() {
    echo
    separator
    echo -e "${BLUE}Copper CRM Skill Setup${NC}"
    separator
    echo

    check_python
    create_cache_dir
    install_dependencies
    setup_env_file
    test_api_connection
    cache_metadata
    display_summary

    exit 0
}

# Run main function
main "$@"

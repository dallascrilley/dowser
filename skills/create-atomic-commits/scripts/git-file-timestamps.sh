#!/usr/bin/env bash
# Get creation and modification timestamps for git changed files
# Usage: git-file-timestamps [PATH] [--staged|--unstaged|--all]
#        Defaults to git project root if in a git repo, otherwise current directory

set -euo pipefail

# Detect if output is being piped (for LLM consumption)
if [[ -t 1 ]]; then
    # Terminal output - use colors
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    # Piped output - no colors (saves tokens)
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

# Get git root directory if in a git repo
get_git_root() {
    git rev-parse --show-toplevel 2>/dev/null || echo ""
}

# Parse arguments for path and mode
TARGET_PATH=""
MODE="--all"

for arg in "$@"; do
    case "$arg" in
        --help|-h)
            echo "Usage: git-file-timestamps [PATH] [--staged|--unstaged|--all]"
            echo ""
            echo "Get creation and modification timestamps for git changed files."
            echo "Defaults to git project root if in a git repo, otherwise current directory."
            echo ""
            echo "Options:"
            echo "  PATH              Optional directory path to check (default: git root or .)"
            echo "  --staged          Only check staged files"
            echo "  --unstaged        Only check unstaged files"
            echo "  --all             Check all changed files (default)"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        --staged|--unstaged|--all)
            MODE="$arg"
            ;;
        *)
            if [[ -d "$arg" ]]; then
                TARGET_PATH="$arg"
            elif [[ -n "$arg" ]]; then
                echo -e "${RED}Error: '$arg' is not a valid directory${NC}" >&2
                exit 1
            fi
            ;;
    esac
done

# Determine target directory
if [[ -n "$TARGET_PATH" ]]; then
    # User specified a path
    cd "$TARGET_PATH" || {
        echo -e "${RED}Error: Cannot change to directory '$TARGET_PATH'${NC}" >&2
        exit 1
    }
elif GIT_ROOT=$(get_git_root); [[ -n "$GIT_ROOT" ]]; then
    # Default to git root if in a git repo
    cd "$GIT_ROOT" || {
        echo -e "${RED}Error: Cannot change to git root '$GIT_ROOT'${NC}" >&2
        exit 1
    }
fi
# Otherwise stay in current directory

get_changed_files() {
    case "$MODE" in
        --staged)
            git diff --cached --name-only
            ;;
        --unstaged)
            git diff --name-only
            ;;
        --all)
            {
                git diff --cached --name-only
                git diff --name-only
            } | sort -u
            ;;
        *)
            echo -e "${RED}Error: Invalid mode. Use --staged, --unstaged, or --all${NC}" >&2
            exit 1
            ;;
    esac
}

# Detect OS for stat command
get_filesystem_timestamp() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "not-found"
        return
    fi
    
    # Try macOS stat format (ISO 8601)
    if stat -f "%Sm" -t "%Y-%m-%dT%H:%M:%S" "$file" 2>/dev/null; then
        return
    fi
    
    # Try Linux stat format (ISO 8601)
    if stat -c "%y" "$file" 2>/dev/null | cut -d'.' -f1 | sed 's/ /T/'; then
        return
    fi
    
    echo "unknown"
}

# Get git creation date (when file was first added)
get_git_creation_date() {
    local file="$1"
    
    # Check if file is tracked
    if ! git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "untracked"
        return
    fi
    
    # Get first commit that added this file
    local created
    created=$(git log --format="%ai" --diff-filter=A --follow -- "$file" 2>/dev/null | tail -1)
    
    if [[ -n "$created" ]]; then
        echo "$created" | cut -d' ' -f1,2 | sed 's/ /T/'
    else
        echo "no-history"
    fi
}

# Get git last modification date
get_git_last_modified() {
    local file="$1"
    
    # Check if file is tracked
    if ! git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "untracked"
        return
    fi
    
    # Get most recent commit that touched this file
    local modified
    modified=$(git log -1 --format="%ai" -- "$file" 2>/dev/null)
    
    if [[ -n "$modified" ]]; then
        echo "$modified" | cut -d' ' -f1,2 | sed 's/ /T/'
    else
        echo "no-history"
    fi
}

# Main execution
main() {
    local files
    files=$(get_changed_files)
    
    if [[ -z "$files" ]]; then
        echo -e "${YELLOW}No changed files found.${NC}"
        exit 0
    fi

    echo -e "${BLUE}FILE_TIMESTAMPS directory=$(pwd) mode=$MODE${NC}"
    
    local count=0
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        
        count=$((count + 1))
        
        local fs_time git_created git_modified
        fs_time=$(get_filesystem_timestamp "$file")
        git_created=$(get_git_creation_date "$file")
        git_modified=$(get_git_last_modified "$file")
        
        # Compact format: file | fs_modified | git_created | git_last_modified
        echo -e "${GREEN}$file${NC} | fs=$fs_time | created=$git_created | modified=$git_modified"
        
    done <<< "$files"
    
    echo -e "${BLUE}Total: $count files${NC}"
}

main "$@"


#!/usr/bin/env bash
# fabric_run_pattern.sh - Run a single Fabric pattern on file(s) or directory
set -euo pipefail

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required command '$1' not found in PATH." >&2
    exit 1
  fi
}

print_usage() {
  cat <<EOF
Usage:
  $(basename "$0") <pattern_name> <input_path> [output_file]

Arguments:
  pattern_name:
    Any Fabric pattern (e.g. extract_wisdom, capture_thinkers_work, label_and_rate)
    Use 'fabric --list' to see all available patterns

  input_path:
    - A directory containing .md/.markdown/.txt files, OR
    - A single markdown/text file

  output_file (optional):
    - Path to write markdown output
    - Default: ./fabric_output/<pattern_name>_<timestamp>.md

Examples:
  # Run extract_wisdom on all articles in a directory
  $(basename "$0") extract_wisdom ./articles

  # Run capture_thinkers_work on a single file
  $(basename "$0") capture_thinkers_work ./transcript.md

  # Specify custom output location
  $(basename "$0") create_tags ./articles ./my_tags.md

  # Common patterns
  $(basename "$0") summarize ./blog_post.md
  $(basename "$0") analyze_claims ./article.md
  $(basename "$0") review_code ./src/ ./code_review.md
EOF
}

build_combined_corpus() {
  local input_path="$1"
  local combined_file="$2"

  mkdir -p "$(dirname "$combined_file")"
  : > "$combined_file"

  echo "Combining files from: $input_path"

  while IFS= read -r file_path; do
    echo -e "\n\n---\n\n# Source: $(basename "$file_path")" >> "$combined_file"
    cat "$file_path" >> "$combined_file"
    echo "" >> "$combined_file"
  done < <(
    find "$input_path" -type f \( \
      -iname "*.md" -o -iname "*.markdown" -o -iname "*.txt" \
    \) | sort
  )

  if [[ ! -s "$combined_file" ]]; then
    echo "Error: combined file '$combined_file' is empty. No matching files found." >&2
    exit 1
  fi

  echo "Combined $(wc -l < "$combined_file") lines from directory"
}

main() {
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -lt 2 ]]; then
    print_usage
    exit 0
  fi

  require_command "fabric"

  local pattern_name="$1"
  local input_path="$2"
  local default_root="./fabric_output"
  local run_id
  run_id="$(date +"%Y%m%d_%H%M%S")"

  local output_file="${3:-$default_root/${pattern_name}_${run_id}.md}"

  mkdir -p "$(dirname "$output_file")"

  local effective_input="$input_path"
  local tmp_combined_file=""

  if [[ -d "$input_path" ]]; then
    tmp_combined_file="$(mktemp)"
    build_combined_corpus "$input_path" "$tmp_combined_file"
    effective_input="$tmp_combined_file"
  elif [[ -f "$input_path" ]]; then
    effective_input="$input_path"
    echo "Processing single file: $input_path"
  else
    echo "Error: input_path '$input_path' is neither a file nor a directory." >&2
    exit 1
  fi

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🎯 Running Fabric Pattern"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Pattern     : $pattern_name"
  echo "  Input       : $effective_input"
  echo "  Output      : $output_file"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  fabric --pattern "$pattern_name" < "$effective_input" > "$output_file"

  if [[ -n "${tmp_combined_file:-}" && -f "$tmp_combined_file" ]]; then
    rm -f "$tmp_combined_file"
  fi

  echo ""
  echo "✅ Done! Output saved to:"
  echo "   $output_file"
  echo ""
}

main "$@"

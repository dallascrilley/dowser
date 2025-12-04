#!/usr/bin/env bash
# fabric_pipeline.sh - Chain multiple Fabric patterns in sequence
# Default pipeline: extract_wisdom → capture_thinkers_work → label_and_rate
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
  $(basename "$0") <input_path> [output_root]

Arguments:
  input_path:
    - A directory containing .md/.markdown/.txt files, OR
    - A single markdown/text file

  output_root (optional):
    - Base directory for outputs (default: ./fabric_pipeline_output)

Pipeline Stages (edit script to customize):
  1. extract_wisdom      - Extract insights, ideas, quotes, recommendations
  2. capture_thinkers_work - Capture key concepts and frameworks
  3. label_and_rate      - Categorize and evaluate content

Examples:
  # Run default pipeline on directory
  $(basename "$0") ./articles

  # Run pipeline on single file with custom output location
  $(basename "$0") ./transcript.md ./my_output

  # Common use cases
  $(basename "$0") ./research_papers        # Deep research analysis
  $(basename "$0") ./meeting_notes         # Extract actionable items
  $(basename "$0") ~/Downloads/ebook.txt   # Book summary pipeline
EOF
}

build_combined_corpus() {
  local input_path="$1"
  local combined_file="$2"

  mkdir -p "$(dirname "$combined_file")"
  : > "$combined_file"

  echo "📦 Combining files from directory..."

  # Collect all markdown/text files recursively
  while IFS= read -r file_path; do
    echo "   Adding: $(basename "$file_path")"
    echo -e "\n\n---\n\n# Source: $(basename "$file_path")" >> "$combined_file"
    cat "$file_path" >> "$combined_file"
    echo "" >> "$combined_file"
  done < <(
    find "$input_path" -type f \( \
      -iname "*.md" -o -iname "*.markdown" -o -iname "*.txt" \
    \) | sort
  )

  if [[ ! -s "$combined_file" ]]; then
    echo "Error: combined file '$combined_file' is empty. No matching articles found." >&2
    exit 1
  fi

  local line_count=$(wc -l < "$combined_file")
  echo "   Combined: $line_count lines"
}

run_fabric_stage() {
  local stage_index="$1"
  local pattern_name="$2"
  local input_file="$3"
  local output_file="$4"

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔄 Stage ${stage_index}: ${pattern_name}"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  fabric --pattern "$pattern_name" < "$input_file" > "$output_file"

  local output_size=$(wc -l < "$output_file")
  echo "   ✅ Complete: $output_size lines"
  echo "   📄 Saved: $output_file"
}

main() {
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -lt 1 ]]; then
    print_usage
    exit 0
  fi

  require_command "fabric"

  local input_path="$1"
  local output_root="${2:-./fabric_pipeline_output}"

  if [[ ! -d "$output_root" ]]; then
    mkdir -p "$output_root"
  fi

  local run_id
  run_id="$(date +"%Y%m%d_%H%M%S")"
  local output_dir="$output_root/$run_id"
  mkdir -p "$output_dir"

  echo ""
  echo "╔════════════════════════════════════════════════╗"
  echo "║      Fabric Multi-Pattern Pipeline             ║"
  echo "╚════════════════════════════════════════════════╝"
  echo ""
  echo "Input      : $input_path"
  echo "Output Dir : $output_dir"
  echo ""

  local corpus_file

  if [[ -d "$input_path" ]]; then
    corpus_file="$output_dir/00_combined_sources.md"
    build_combined_corpus "$input_path" "$corpus_file"
  elif [[ -f "$input_path" ]]; then
    corpus_file="$input_path"
    echo "📄 Using single file as input: $(basename "$corpus_file")"
  else
    echo "Error: input_path '$input_path' is neither a file nor a directory." >&2
    exit 1
  fi

  # ╔════════════════════════════════════════════════╗
  # ║ CUSTOMIZE YOUR PIPELINE HERE                   ║
  # ╚════════════════════════════════════════════════╝
  #
  # Edit this array to change which patterns run and in what order.
  # Each pattern's output becomes the next pattern's input.
  #
  # Popular pipeline combinations:
  #
  # Research Analysis:
  #   ("extract_wisdom" "capture_thinkers_work" "label_and_rate")
  #
  # Content Summarization:
  #   ("summarize" "extract_recommendations" "create_tags")
  #
  # Code Review:
  #   ("explain_code" "review_code" "create_git_diff_commit")
  #
  # Security Analysis:
  #   ("analyze_threat_report" "create_sigma_rules" "create_stride_threat_model")
  #
  # Content Creation:
  #   ("extract_ideas" "create_story_explanation" "improve_writing")
  #
  local patterns=(
    "extract_wisdom"
    "capture_thinkers_work"
    "label_and_rate"
  )

  local current_input="$corpus_file"
  local stage_index=1
  local stage_files=()

  for pattern_name in "${patterns[@]}"; do
    local padded_index
    padded_index="$(printf "%02d" "$stage_index")"
    local output_file="$output_dir/${padded_index}_${pattern_name}.md"

    run_fabric_stage "$stage_index" "$pattern_name" "$current_input" "$output_file"

    stage_files+=("$output_file")
    current_input="$output_file"
    stage_index=$((stage_index + 1))
  done

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Pipeline Complete!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "📁 Output files (in processing order):"
  for file in "${stage_files[@]}"; do
    echo "   $(basename "$file")"
  done
  echo ""
  echo "📂 Full output directory:"
  echo "   $output_dir"
  echo ""
  echo "💡 Next steps:"
  echo "   - Review the final output: $(basename "${stage_files[-1]}")"
  echo "   - Customize pipeline by editing this script"
  echo "   - Run additional patterns on the results"
  echo ""
}

main "$@"

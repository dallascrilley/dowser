#!/usr/bin/env bash
# fabric_quick_commands.sh - Quick copy-paste ready Fabric commands
# Source this file or run individual functions

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
}

# ═══════════════════════════════════════════════════════════════
# EXTRACT PATTERNS - Pull information from content
# ═══════════════════════════════════════════════════════════════

fabric_extract_wisdom() {
  print_header "Extract Wisdom - Insights, ideas, quotes, habits"
  echo -e "${YELLOW}From clipboard:${NC}"
  echo "pbpaste | fabric --pattern extract_wisdom"
  echo ""
  echo -e "${YELLOW}From file:${NC}"
  echo "fabric --pattern extract_wisdom < article.md"
  echo ""
  echo -e "${YELLOW}From YouTube:${NC}"
  echo "fabric -y 'https://youtube.com/watch?v=VIDEO_ID' --pattern extract_wisdom"
  echo ""
  echo -e "${YELLOW}From URL:${NC}"
  echo "fabric -u 'https://example.com/article' --pattern extract_wisdom"
}

fabric_extract_ideas() {
  print_header "Extract Ideas - Novel concepts and applications"
  echo "pbpaste | fabric --pattern extract_ideas"
  echo "fabric --pattern extract_ideas < research.md > ideas.md"
}

fabric_extract_recommendations() {
  print_header "Extract Recommendations - Actionable advice"
  echo "pbpaste | fabric --pattern extract_recommendations"
  echo "fabric --pattern extract_recommendations < advice.md > actions.md"
}

# ═══════════════════════════════════════════════════════════════
# SUMMARIZE PATTERNS - Condense content
# ═══════════════════════════════════════════════════════════════

fabric_summarize() {
  print_header "Summarize - General purpose summarization"
  echo -e "${YELLOW}Quick summary:${NC}"
  echo "pbpaste | fabric --pattern summarize"
  echo ""
  echo -e "${YELLOW}Micro summary (very concise):${NC}"
  echo "pbpaste | fabric --pattern create_micro_summary"
  echo ""
  echo -e "${YELLOW}5-sentence progressive summary:${NC}"
  echo "pbpaste | fabric --pattern create_5_sentence_summary"
}

fabric_youtube_summary() {
  print_header "YouTube Summary - Summarize videos with timestamps"
  echo "fabric -y 'https://youtube.com/watch?v=VIDEO_ID' --pattern youtube_summary"
  echo "fabric -y 'https://youtube.com/watch?v=VIDEO_ID' -p youtube_summary -o summary.md"
}

# ═══════════════════════════════════════════════════════════════
# ANALYSIS PATTERNS - Evaluate and assess
# ═══════════════════════════════════════════════════════════════

fabric_analyze_claims() {
  print_header "Analyze Claims - Fact checking with evidence"
  echo "pbpaste | fabric --stream --pattern analyze_claims"
  echo "fabric -u 'https://article-url.com' --pattern analyze_claims"
}

fabric_analyze_code() {
  print_header "Code Analysis - Explain and review code"
  echo -e "${YELLOW}Explain code:${NC}"
  echo "pbpaste | fabric --pattern explain_code"
  echo ""
  echo -e "${YELLOW}Review code:${NC}"
  echo "git diff main | fabric --pattern review_code"
  echo "fabric --pattern review_code < src/main.js > review.md"
}

# ═══════════════════════════════════════════════════════════════
# SECURITY PATTERNS - Threat modeling and analysis
# ═══════════════════════════════════════════════════════════════

fabric_threat_model() {
  print_header "Create Threat Model - STRIDE methodology"
  echo "fabric --pattern create_stride_threat_model < system_design.md"
  echo "pbpaste | fabric --pattern create_stride_threat_model > threats.md"
}

fabric_analyze_malware() {
  print_header "Analyze Malware - Malware behavior analysis"
  echo "fabric --pattern analyze_malware < malware_report.txt"
  echo "pbpaste | fabric --pattern analyze_malware"
}

# ═══════════════════════════════════════════════════════════════
# WRITING PATTERNS - Content creation and improvement
# ═══════════════════════════════════════════════════════════════

fabric_improve_writing() {
  print_header "Improve Writing - Enhance clarity and style"
  echo "pbpaste | fabric --pattern improve_writing"
  echo "fabric --pattern improve_writing < draft.md > improved.md"
}

fabric_create_email() {
  print_header "Create Formal Email - Professional email composition"
  echo "echo 'Need to request meeting with team about project delays' | fabric --pattern create_formal_email"
}

fabric_tweet() {
  print_header "Create Tweet - Convert content to social media"
  echo "pbpaste | fabric --pattern tweet"
  echo "fabric -u 'https://blog-post-url.com' --pattern tweet"
}

# ═══════════════════════════════════════════════════════════════
# VISUALIZATION PATTERNS - Create diagrams
# ═══════════════════════════════════════════════════════════════

fabric_create_mermaid() {
  print_header "Create Mermaid Diagram - Flowcharts, sequences, etc"
  echo "echo 'authentication flow for web app' | fabric --pattern create_mermaid_visualization"
  echo "pbpaste | fabric --pattern create_mermaid_visualization > diagram.md"
}

fabric_create_mindmap() {
  print_header "Create Mind Map - Markmap visualization"
  echo "pbpaste | fabric --pattern create_markmap_visualization"
  echo "fabric --pattern create_markmap_visualization < concepts.md > mindmap.md"
}

# ═══════════════════════════════════════════════════════════════
# DEVELOPMENT PATTERNS - Software development workflows
# ═══════════════════════════════════════════════════════════════

fabric_git_commit() {
  print_header "Create Git Commit Message - Smart commit messages"
  echo "git diff --staged | fabric --pattern create_git_diff_commit"
}

fabric_create_pr() {
  print_header "Create Pull Request - PR descriptions"
  echo "git diff main...feature-branch | fabric --pattern write_pull-request"
}

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

fabric_list_all() {
  print_header "All Available Commands"
  echo -e "${GREEN}EXTRACT PATTERNS:${NC}"
  echo "  fabric_extract_wisdom"
  echo "  fabric_extract_ideas"
  echo "  fabric_extract_recommendations"
  echo ""
  echo -e "${GREEN}SUMMARIZE PATTERNS:${NC}"
  echo "  fabric_summarize"
  echo "  fabric_youtube_summary"
  echo ""
  echo -e "${GREEN}ANALYSIS PATTERNS:${NC}"
  echo "  fabric_analyze_claims"
  echo "  fabric_analyze_code"
  echo ""
  echo -e "${GREEN}SECURITY PATTERNS:${NC}"
  echo "  fabric_threat_model"
  echo "  fabric_analyze_malware"
  echo ""
  echo -e "${GREEN}WRITING PATTERNS:${NC}"
  echo "  fabric_improve_writing"
  echo "  fabric_create_email"
  echo "  fabric_tweet"
  echo ""
  echo -e "${GREEN}VISUALIZATION PATTERNS:${NC}"
  echo "  fabric_create_mermaid"
  echo "  fabric_create_mindmap"
  echo ""
  echo -e "${GREEN}DEVELOPMENT PATTERNS:${NC}"
  echo "  fabric_git_commit"
  echo "  fabric_create_pr"
  echo ""
  echo -e "${YELLOW}Usage: Run any function to see copy-paste ready commands${NC}"
  echo "Example: fabric_extract_wisdom"
}

# Run fabric_list_all if script is executed (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  fabric_list_all
fi

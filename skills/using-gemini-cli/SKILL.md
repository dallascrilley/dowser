---
name: using-gemini-cli
short_description: >-
  Enable Claude to leverage Google Gemini CLI for intelligent code analysis,
  refactoring, and automated editing through non-interactive command-line
  prompting. Covers headless mode, structured JSON/streaming output, model
  selection, and automation workflows.
description: >
  This skill enables Claude to leverage Google Gemini CLI for intelligent code
  analysis, refactoring, and automated editing through non-interactive
  command-line prompting. It provides integration with Gemini and other
  LLM-based coding assistants, allowing delegation of code-based tasks to
  external smart models via CLI invocation.
when_to_use: >-
  Use when automating Google Gemini CLI in headless mode for scripted prompts,
  code review, or CI pipelines—covers non-interactive prompts via flags/stdin,
  structured JSON/streaming output, model selection, and safe defaults for
  automation.
version: 1.0.0
languages: all
category: agents-and-skills
---

# Using Gemini CLI - Headless Guide

## Overview
Headless mode runs Gemini CLI non-interactively from scripts and CI. It accepts prompts via flags or stdin and returns text, JSON, or streaming JSON events—ideal for automation, logging, and tool-driven workflows.

## When to Use
- Automating prompts in shell scripts or CI/CD
- Needing structured output (JSON or streaming JSON) for downstream tools
- Piping files, git diffs, or logs into Gemini
- Building dashboards that monitor model/tool activity in real time
- Not for interactive chat; use normal Gemini CLI for conversational sessions

## Run a Task (minimal steps)
1. Confirm model and output format if unspecified (speed: `gemini-2.5-flash`; depth: `gemini-3-pro-preview`; formats: `text`, `json`, `stream-json`).
2. Build the command:
   - Direct prompt: `gemini -p "What is machine learning?"`
   - From stdin: `echo "Explain this code" | gemini`
   - File + prompt: `cat README.md | gemini -p "Summarize this documentation" --output-format json`
   - Add repo context: `gemini -p "Review repository risks" --include-directories src,docs`
3. Optional safety/verbosity:
   - `-m, --model <model>` (e.g., `gemini-2.5-flash`, `gemini-3-pro-preview`)
   - `--output-format json|stream-json`
   - `--yolo` or `--approval-mode auto_edit` to auto-approve actions (use cautiously)
   - `--debug` for verbose logging
4. Capture output:
   - Text: `... > result.txt`
   - JSON: `... --output-format json | jq '.response'`
   - Streaming: `... --output-format stream-json > events.jsonl`

## Quick Reference
| Use case | Command pattern |
| --- | --- |
| Fast Q&A (text) | `gemini -p "question"` |
| Structured output for scripts | `gemini -p "query" --output-format json` |
| Stream live events | `gemini -p "task" --output-format stream-json` |
| Analyze file content | `cat file | gemini -p "prompt"` |
| Review git diff | `git diff | gemini -p "Review these changes" --output-format json` |
| Generate commit message | `git diff --cached | gemini -p "Write a concise commit message" --output-format json` |
| API doc draft | `cat api/routes.js | gemini -p "Generate OpenAPI spec" --output-format json` |
| Batch file analysis | `for f in src/*.py; do cat "$f" | gemini -p "Find bugs" --output-format json > reports/$(basename "$f").json; done` |

## Output Formats
- **text (default):** human-readable response.
- **json:** structured object `{ response, stats, error? }` including per-model token usage, tool stats, and file line deltas—ideal for automation pipelines.
- **stream-json:** newline-delimited events (`init`, `message`, `tool_use`, `tool_result`, `error`, `result`) emitted immediately for progress UIs and event-driven scripts.

Example stream pipeline:
```
gemini --output-format stream-json --prompt "List files" | jq -r '.type'
```

## Common Options
- `-p, --prompt`: set prompt (headless trigger)
- `--output-format text|json|stream-json`
- `-m, --model <model>`: choose Gemini model
- `--include-directories dir1,dir2`: add repo folders to context
- `--debug`: verbose logging
- `--yolo`: auto-approve actions
- `--approval-mode <mode>`: control approvals (e.g., `auto_edit`)

## Workflow Patterns
- **Code review:** `git diff | gemini -p "Review for bugs and security issues" --output-format json`
- **Commit message:** `git diff --cached | gemini -p "Write a concise commit message" --output-format json | jq -r '.response'`
- **Log triage:** `grep "ERROR" app.log | tail -50 | gemini -p "Find root cause and fixes" > error-analysis.txt`
- **Release notes:** `git log --oneline v1.0.0..HEAD | gemini -p "Generate release notes" --output-format json | jq -r '.response' >> CHANGELOG.md`
- **Usage tracking:** 
```
result=$(gemini -p "Explain this database schema" --include-directories db --output-format json)
total_tokens=$(echo "$result" | jq -r '.stats.models // {} | to_entries | map(.value.tokens.total) | add // 0')
models_used=$(echo "$result" | jq -r '.stats.models // {} | keys | join(", ") | if . == "" then "none" else . end')
tool_calls=$(echo "$result" | jq -r '.stats.tools.totalCalls // 0')
echo "$(date): $total_tokens tokens, $tool_calls tool calls (models: $models_used)" >> usage.log
echo "$result" | jq -r '.response' > schema-docs.md
```

## Common Mistakes
- Forgetting `--output-format json` when piping to `jq`, causing parse errors.
- Assuming pro-level depth without setting `--model`; default may be `gemini-2.5-flash`.
- Sending both a prompt and unrelated stdin, which muddies context.
- Using `--yolo` in production scripts without safeguards—can auto-accept tool actions.
- Ignoring non-zero exit codes in CI; always fail the job on errors.

## Resources
- Headless mode docs: https://geminicli.com/docs/cli/headless/
- Configuration guide: https://geminicli.com/docs/get-started/configuration
- Authentication: https://geminicli.com/docs/get-started/authentication

## Code Review Workflow
0. IMPORTANT/DO NOT SKIP: Always run the command `code-review.sh --help` and read the help message before using the script.
1. Ask user for model preference (`gemini-2.5-flash` for speed, `gemini-3-pro-preview` for depth; default is `gemini-3-pro-preview`)
2. Run the code-review script (located at `scripts/code-review.sh` in the skill directory): `code-review.sh [--model MODEL] [--output-format json] "<request>" [files...]`
3. The script automatically:
   - Includes BOTH staged and unstaged git changes in the review
   - Uses a structured prompt from `~/.gemini/prompts/code-review.md` (or `$GEMINI_PROMPTS_DIR/prompts/code-review.md`)
   - Pipes all context to Gemini CLI via stdin with `--prompt` flag
   - Uses `--output-format json` if specified for structured parsing
4. After completion, inform user of the review results and any issues found
5. For follow-up questions, run a new Gemini command with the same context or ask specific questions

**Note**: The script reviews ALL changes (both staged and unstaged). Users can stage specific files first if they want to review only certain changes.

## Following Up
- After every `gemini` command, immediately use `AskUserQuestion` to confirm next steps or collect clarifications.
- For follow-up analysis, run a new `gemini` command with additional context or specific questions.
- Restate the chosen model and output format when proposing follow-up actions.

## Error Handling
- Stop and report failures whenever `gemini --version` or a `gemini` command exits non-zero; request direction before retrying.
- Before you use high-impact flags (`--yolo`, `--approval-mode auto_edit`) ask the user for permission using AskUserQuestion unless it was already given.
- When output includes warnings or partial results, summarize them and ask how to adjust using `AskUserQuestion`.
- Always check for non-zero exit codes in CI/CD pipelines and fail the job on errors.

## Additional References
- [Gemini CLI Headless Mode Documentation](https://geminicli.com/docs/cli/headless/) - Complete guide to non-interactive execution
- [Gemini CLI Configuration Guide](https://geminicli.com/docs/get-started/configuration) - Configuration options, settings files, and environment variables
- [Gemini CLI Authentication](https://geminicli.com/docs/get-started/authentication) - Setup authentication for Gemini CLI

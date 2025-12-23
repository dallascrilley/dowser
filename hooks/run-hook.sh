#!/usr/bin/env bash
set -euo pipefail

script_path="${1:-}"
if [[ -z "${script_path}" ]]; then
  echo "run-hook.sh: missing script path argument" >&2
  exit 2
fi

plugin_root="${CLAUDE_PLUGIN_ROOT:-}"
if [[ -z "${plugin_root}" ]]; then
  plugin_root="$(cd "$(dirname "$0")/.." && pwd)"
fi

cd "${plugin_root}"

if [[ ! -d "node_modules" ]]; then
  bun install --silent
fi

exec bun run "${script_path}"


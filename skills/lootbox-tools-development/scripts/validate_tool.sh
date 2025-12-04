#!/bin/bash
# Validate Lootbox Tool File
# Usage: ./validate_tool.sh <path-to-tool.ts>

TOOL_FILE="$1"

if [ -z "$TOOL_FILE" ]; then
  echo "Usage: validate_tool.sh <path-to-tool.ts>"
  exit 1
fi

if [ ! -f "$TOOL_FILE" ]; then
  echo "ERROR: File not found: $TOOL_FILE"
  exit 1
fi

echo "Validating $TOOL_FILE..."
echo ""

WARNINGS=0
ERRORS=0

# Check 1: File extension
if [[ ! "$TOOL_FILE" == *.ts ]]; then
  echo "❌ File must have .ts extension"
  ((ERRORS++))
fi
echo "✓ File has .ts extension"

# Check 2: File in correct directory
if [[ ! "$TOOL_FILE" == *".lootbox/tools/"* ]]; then
  echo "⚠️  Warning: Tool should be in .lootbox/tools/ directory"
  ((WARNINGS++))
fi

# Check 3: Has export keyword
if ! grep -q "export" "$TOOL_FILE"; then
  echo "❌ ERROR: No exports found. Tool must export interfaces and functions."
  ((ERRORS++))
fi
echo "✓ File has exports"

# Check 4: Has interface declarations
INTERFACE_COUNT=$(grep -c "export interface" "$TOOL_FILE" || echo "0")
if [ "$INTERFACE_COUNT" -eq 0 ]; then
  echo "❌ ERROR: No exported interfaces found. Need <FunctionName>Args and <FunctionName>Result"
  ((ERRORS++))
else
  echo "✓ Found $INTERFACE_COUNT interfaces"
fi

# Check 5: Has async functions
FUNCTION_COUNT=$(grep -c "export async function" "$TOOL_FILE" || echo "0")
if [ "$FUNCTION_COUNT" -eq 0 ]; then
  echo "❌ ERROR: No exported async functions found"
  ((ERRORS++))
else
  echo "✓ Found $FUNCTION_COUNT async functions"
fi

# Check 6: Args/Result naming convention
ARGS_COUNT=$(grep -c "Args {" "$TOOL_FILE" || echo "0")
RESULT_COUNT=$(grep -c "Result {" "$TOOL_FILE" || echo "0")
if [ "$ARGS_COUNT" -eq 0 ] && [ "$RESULT_COUNT" -eq 0 ]; then
  echo "⚠️  Warning: No Args or Result interfaces found. Check naming convention."
  ((WARNINGS++))
fi

# Check 7: TypeScript syntax (basic check)
if ! grep -q ":" "$TOOL_FILE"; then
  echo "⚠️  Warning: No type annotations found. Ensure proper TypeScript syntax."
  ((WARNINGS++))
fi

# Check 8: Promise return types
if ! grep -q "Promise<" "$TOOL_FILE"; then
  echo "⚠️  Warning: Functions should return Promise<>. Ensure they are async."
  ((WARNINGS++))
fi

# ============================================================================
# Anti-Pattern Detection (NEW)
# ============================================================================

echo ""
echo "--- Anti-Pattern Checks ---"

# Anti-Pattern 1: Multiple parameters (these functions will be silently excluded!)
MULTI_PARAM_FUNCS=$(grep -E "export async function \w+\([^)]+,[^)]+\)" "$TOOL_FILE" | sed 's/export async function /  - /' | cut -d'(' -f1)
if [ -n "$MULTI_PARAM_FUNCS" ]; then
  echo "⚠️  WARNING: Functions with multiple parameters will be EXCLUDED from RpcClient:"
  echo "$MULTI_PARAM_FUNCS"
  echo "   → Fix: Use single object parameter with Args interface"
  ((WARNINGS++))
else
  echo "✓ No multi-parameter functions (good)"
fi

# Anti-Pattern 2: Promise<unknown> return type (weak typing)
WEAK_TYPING=$(grep -E "Promise<unknown>" "$TOOL_FILE")
if [ -n "$WEAK_TYPING" ]; then
  echo "⚠️  Warning: Found Promise<unknown> return types (weak typing):"
  grep -n "Promise<unknown>" "$TOOL_FILE" | sed 's/^/   Line /'
  echo "   → Fix: Use typed Result interface (e.g., Promise<GetResult>)"
  ((WARNINGS++))
else
  echo "✓ No Promise<unknown> return types (good)"
fi

# Anti-Pattern 3: Check for inline types instead of named interfaces
INLINE_ARGS=$(grep -E 'export async function [a-zA-Z]+\(args: \{' "$TOOL_FILE" || true)
if [ -n "$INLINE_ARGS" ]; then
  echo "⚠️  Warning: Found functions with inline type arguments instead of named interfaces:"
  grep -nE 'export async function [a-zA-Z]+\(args: \{' "$TOOL_FILE" | sed 's/^/   Line /' | cut -d'{' -f1
  echo "   → Recommend: Use named <FunctionName>Args interface"
  ((WARNINGS++))
else
  echo "✓ No inline argument types (good)"
fi

# Check for inline return types
INLINE_RETURNS=$(grep -E 'Promise<\{' "$TOOL_FILE" || true)
if [ -n "$INLINE_RETURNS" ]; then
  echo "⚠️  Warning: Found functions with inline return types instead of named interfaces:"
  grep -nE 'Promise<\{' "$TOOL_FILE" | sed 's/^/   Line /'
  echo "   → Recommend: Use named <FunctionName>Result interface"
  ((WARNINGS++))
else
  echo "✓ No inline return types (good)"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "===================="
if [ "$ERRORS" -gt 0 ]; then
  echo "❌ Validation FAILED: $ERRORS error(s), $WARNINGS warning(s)"
  echo ""
  echo "Fix errors before proceeding."
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  echo "⚠️  Validation PASSED with $WARNINGS warning(s)"
  echo ""
  echo "Warnings may cause issues. Review and fix if possible."
else
  echo "✓ Validation PASSED"
fi
echo "===================="

echo ""
echo "Next steps:"
echo "1. Restart lootbox server if it's running (Ctrl+C, then 'lootbox server')"
echo "2. Run: lootbox tools"
echo "3. Verify your namespace appears in the list"
echo "4. Run: lootbox tools types <namespace>"
echo "5. Fix any errors shown"
echo "6. Test: lootbox exec 'await tools.<namespace>.<function>({})'"

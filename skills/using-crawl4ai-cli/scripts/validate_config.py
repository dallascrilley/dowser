#!/usr/bin/env python3
"""
Validate crawl4ai configuration and schema files.

Checks JSON schema structure and YAML config syntax before running crawl4ai.
Catches common errors early to prevent failed crawls.
"""

import sys
import json
import argparse
from typing import List, Dict, Any, Tuple
from pathlib import Path


def validate_json(filepath: str) -> Tuple[bool, List[str]]:
    """Validate JSON syntax and structure."""
    errors = []

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Check if it's a CSS schema
        if isinstance(data, dict) and "baseSelector" in data:
            # Validate CSS schema structure
            if "name" not in data:
                errors.append("Missing required field: 'name'")

            if "fields" not in data:
                errors.append("Missing required field: 'fields'")
            elif not isinstance(data["fields"], list):
                errors.append("'fields' must be an array")
            else:
                # Validate each field
                for i, field in enumerate(data["fields"]):
                    if not isinstance(field, dict):
                        errors.append(f"Field {i} must be an object")
                        continue

                    if "name" not in field:
                        errors.append(f"Field {i} missing 'name'")

                    if "selector" not in field:
                        errors.append(f"Field {i} missing 'selector'")

                    if "type" not in field:
                        errors.append(f"Field {i} missing 'type'")
                    elif field["type"] not in ["text", "html", "attribute"]:
                        errors.append(
                            f"Field {i} has invalid type '{field['type']}' "
                            "(must be text, html, or attribute)"
                        )

                    if field.get("type") == "attribute" and "attribute" not in field:
                        errors.append(
                            f"Field {i} has type 'attribute' but missing 'attribute' key"
                        )

    except json.JSONDecodeError as e:
        errors.append(f"JSON syntax error: {e}")
    except FileNotFoundError:
        errors.append(f"File not found: {filepath}")
    except Exception as e:
        errors.append(f"Error reading file: {e}")

    return len(errors) == 0, errors


def validate_yaml(filepath: str) -> Tuple[bool, List[str]]:
    """Validate YAML syntax (basic check without PyYAML dependency)."""
    errors = []

    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Basic YAML syntax checks
        if not content.strip():
            errors.append("File is empty")
            return False, errors

        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue

            # Check for basic YAML structure
            if ':' not in line and stripped:
                # Might be a multi-line value, but warn
                if not line.startswith(' ') and not line.startswith('-'):
                    errors.append(f"Line {i}: Possibly malformed (no key:value pair)")

        # Check for common config keys
        config_keys = [
            "cache_mode", "wait_until", "page_timeout",
            "delay_before_return_html", "scan_full_page"
        ]

        has_config_key = any(key in content for key in config_keys)

        if not has_config_key:
            errors.append(
                "Warning: No recognized config keys found. "
                "Expected keys like: cache_mode, wait_until, page_timeout"
            )

    except FileNotFoundError:
        errors.append(f"File not found: {filepath}")
    except Exception as e:
        errors.append(f"Error reading file: {e}")

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate crawl4ai configuration and schema files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate CSS schema
  %(prog)s schema.json

  # Validate extraction config
  %(prog)s extract_css.yml

  # Validate multiple files
  %(prog)s schema.json extract_css.yml crawler.yml
        """
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="Files to validate"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()

    all_valid = True
    total_errors = 0
    total_warnings = 0

    for filepath in args.files:
        path = Path(filepath)

        print(f"\n{'='*60}")
        print(f"Validating: {filepath}")
        print(f"{'='*60}")

        if not path.exists():
            print(f"✗ File not found: {filepath}")
            all_valid = False
            total_errors += 1
            continue

        # Determine file type and validate
        if path.suffix in ['.json']:
            valid, errors = validate_json(filepath)
        elif path.suffix in ['.yml', '.yaml']:
            valid, errors = validate_yaml(filepath)
        else:
            print(f"⚠ Unknown file type: {path.suffix}")
            print(f"  Supported: .json, .yml, .yaml")
            continue

        if valid and not errors:
            print(f"✓ Valid: {filepath}")
        else:
            for error in errors:
                if error.startswith("Warning:"):
                    print(f"⚠ {error}")
                    total_warnings += 1
                    if args.strict:
                        all_valid = False
                else:
                    print(f"✗ {error}")
                    total_errors += 1
                    all_valid = False

    # Summary
    print(f"\n{'='*60}")
    print(f"Validation Summary")
    print(f"{'='*60}")
    print(f"Files checked: {len(args.files)}")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {total_warnings}")

    if all_valid:
        print("\n✓ All files valid")
        sys.exit(0)
    else:
        print("\n✗ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

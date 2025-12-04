#!/usr/bin/env python3
"""
Generate crawler configuration for crawl4ai CLI.

Creates YAML crawler configs from presets (basic, dynamic, monitoring).
Allows customization of common parameters.
"""

import sys
import argparse
from typing import Dict, Any


PRESETS = {
    "basic": {
        "cache_mode": "bypass",
        "wait_until": "load",
        "page_timeout": 30000,
        "delay_before_return_html": 0.5,
        "word_count_threshold": 100,
        "scan_full_page": False,
        "scroll_delay": 0.3,
        "verbose": True
    },
    "dynamic": {
        "cache_mode": "bypass",
        "wait_until": "networkidle",
        "page_timeout": 60000,
        "delay_before_return_html": 2.0,
        "scan_full_page": True,
        "scroll_delay": 0.5,
        "remove_overlay_elements": True,
        "magic": True,
        "verbose": True
    },
    "monitoring": {
        "cache_mode": "bypass",
        "wait_until": "networkidle",
        "page_timeout": 30000,
        "delay_before_return_html": 1.0,
        "word_count_threshold": 50,
        "scan_full_page": False,
        "scroll_delay": 0.3,
        "verbose": False
    }
}


def dict_to_yaml(data: Dict[str, Any], indent: int = 0) -> str:
    """Convert dict to YAML string with proper formatting."""
    lines = []
    for key, value in data.items():
        if isinstance(value, bool):
            value_str = "true" if value else "false"
        elif isinstance(value, str):
            value_str = f'"{value}"'
        else:
            value_str = str(value)

        lines.append(f"{' ' * indent}{key}: {value_str}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate crawler configuration for crawl4ai CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Presets:
  basic      - Standard crawler settings for static sites
  dynamic    - For JavaScript-heavy sites with infinite scroll
  monitoring - Optimized for frequent content monitoring

Examples:
  %(prog)s --preset basic
  %(prog)s --preset dynamic --output dynamic_crawler.yml
  %(prog)s --preset monitoring --timeout 45000
        """
    )

    parser.add_argument(
        "--preset",
        choices=["basic", "dynamic", "monitoring"],
        default="basic",
        help="Configuration preset to use (default: basic)"
    )

    parser.add_argument(
        "--output",
        "-o",
        default="crawler.yml",
        help="Output filename (default: crawler.yml)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        help="Override page_timeout value (milliseconds)"
    )

    parser.add_argument(
        "--delay",
        type=float,
        help="Override delay_before_return_html value (seconds)"
    )

    parser.add_argument(
        "--scan",
        action="store_true",
        help="Enable full page scanning"
    )

    parser.add_argument(
        "--no-scan",
        action="store_true",
        help="Disable full page scanning"
    )

    args = parser.parse_args()

    # Get preset config
    config = PRESETS[args.preset].copy()

    # Apply overrides
    if args.timeout:
        config["page_timeout"] = args.timeout

    if args.delay:
        config["delay_before_return_html"] = args.delay

    if args.scan:
        config["scan_full_page"] = True

    if args.no_scan:
        config["scan_full_page"] = False

    # Generate YAML
    yaml_content = dict_to_yaml(config)

    # Save to file
    try:
        with open(args.output, 'w') as f:
            f.write(yaml_content)
            f.write("\n")

        print(f"✓ Created {args.preset} crawler config: {args.output}")
        print(f"\nContents:")
        print(yaml_content)
        print(f"\nUsage:")
        print(f"  crwl https://example.com -C {args.output} -o markdown")

    except IOError as e:
        print(f"✗ Error writing file: {e}")
        print(f"\nConfig output:")
        print(yaml_content)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

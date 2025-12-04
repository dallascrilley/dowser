#!/usr/bin/env python3
"""
Generate extraction configuration for crawl4ai CLI.

Creates YAML extraction configs for CSS or LLM-based extraction.
"""

import sys
import argparse


CSS_TEMPLATE = """type: "json-css"
params:
  verbose: true
"""

LLM_TEMPLATE = """type: "llm"
provider: "{provider}"
instruction: "{instruction}"
api_token: "{api_token}"
params:
  temperature: {temperature}
  max_tokens: {max_tokens}
"""


def create_css_config(output: str, verbose: bool = True):
    """Create CSS extraction config."""
    config = f"""type: "json-css"
params:
  verbose: {'true' if verbose else 'false'}
"""

    try:
        with open(output, 'w') as f:
            f.write(config)

        print(f"✓ Created CSS extraction config: {output}")
        print(f"\nContents:")
        print(config)
        print(f"\nNext steps:")
        print(f"  1. Create schema: python scripts/generate_schema.py")
        print(f"  2. Extract data: crwl URL -e {output} -s schema.json -o json")

    except IOError as e:
        print(f"✗ Error writing file: {e}")
        print(f"\nConfig output:")
        print(config)
        sys.exit(1)


def create_llm_config(
    output: str,
    provider: str,
    instruction: str,
    api_token: str,
    temperature: float,
    max_tokens: int
):
    """Create LLM extraction config."""
    config = f"""type: "llm"
provider: "{provider}"
instruction: "{instruction}"
api_token: "{api_token}"
params:
  temperature: {temperature}
  max_tokens: {max_tokens}
"""

    try:
        with open(output, 'w') as f:
            f.write(config)

        print(f"✓ Created LLM extraction config: {output}")
        print(f"\nContents:")
        print(config)
        print(f"\nUsage:")
        print(f"  crwl URL -e {output} -s llm_schema.json -o json")

    except IOError as e:
        print(f"✗ Error writing file: {e}")
        print(f"\nConfig output:")
        print(config)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate extraction configuration for crawl4ai CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Extraction Types:
  css  - Extract data using CSS selectors (requires schema.json)
  llm  - Extract data using LLM (requires LLM schema and API key)

Examples:
  # CSS extraction
  %(prog)s --type css

  # LLM extraction
  %(prog)s --type llm \\
    --provider "openai/gpt-4" \\
    --instruction "Extract article titles and summaries" \\
    --api-token "sk-your-key"
        """
    )

    parser.add_argument(
        "--type",
        "-t",
        choices=["css", "llm"],
        required=True,
        help="Extraction type"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output filename (default: extract_{type}.yml)"
    )

    # LLM-specific arguments
    llm_group = parser.add_argument_group("LLM options")

    llm_group.add_argument(
        "--provider",
        default="openai/gpt-4",
        help="LLM provider (default: openai/gpt-4)"
    )

    llm_group.add_argument(
        "--instruction",
        default="Extract structured data from this page",
        help="Extraction instruction"
    )

    llm_group.add_argument(
        "--api-token",
        default="your-api-token-here",
        help="API token for LLM provider"
    )

    llm_group.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="LLM temperature (default: 0.3)"
    )

    llm_group.add_argument(
        "--max-tokens",
        type=int,
        default=1000,
        help="Max tokens for LLM (default: 1000)"
    )

    # CSS-specific arguments
    css_group = parser.add_argument_group("CSS options")

    css_group.add_argument(
        "--no-verbose",
        action="store_true",
        help="Disable verbose output"
    )

    args = parser.parse_args()

    # Determine output filename
    if args.output:
        output = args.output
    else:
        output = f"extract_{args.type}.yml"

    # Create config based on type
    if args.type == "css":
        create_css_config(output, verbose=not args.no_verbose)
    else:  # llm
        create_llm_config(
            output,
            args.provider,
            args.instruction,
            args.api_token,
            args.temperature,
            args.max_tokens
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

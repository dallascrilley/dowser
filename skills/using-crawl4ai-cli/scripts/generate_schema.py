#!/usr/bin/env python3
"""
Generate CSS extraction schema for crawl4ai CLI.

Interactive tool to create valid schema.json files with proper structure.
Handles user input validation and provides example outputs.
"""

import json
import sys
from typing import List, Dict, Any


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default value."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def get_field_type() -> str:
    """Get valid field type from user."""
    while True:
        print("\nField types:")
        print("  1. text - Extract text content")
        print("  2. html - Extract HTML markup")
        print("  3. attribute - Extract attribute value")

        choice = input("Choose field type (1-3): ").strip()

        type_map = {"1": "text", "2": "html", "3": "attribute"}
        if choice in type_map:
            return type_map[choice]
        print("Invalid choice. Please enter 1, 2, or 3.")


def create_field() -> Dict[str, Any]:
    """Create a single field definition."""
    print("\n--- Add Field ---")

    name = get_input("Field name (e.g., 'title', 'price')")
    while not name:
        print("Field name cannot be empty.")
        name = get_input("Field name")

    selector = get_input("CSS selector (e.g., 'h2.title', '.price-current')")
    while not selector:
        print("Selector cannot be empty.")
        selector = get_input("CSS selector")

    field_type = get_field_type()

    field = {
        "name": name,
        "selector": selector,
        "type": field_type
    }

    # Add attribute field for attribute type
    if field_type == "attribute":
        attribute = get_input("Attribute name (e.g., 'href', 'src', 'data-id')")
        while not attribute:
            print("Attribute name cannot be empty for attribute type.")
            attribute = get_input("Attribute name")
        field["attribute"] = attribute

    return field


def main():
    """Main schema generation workflow."""
    print("=== Crawl4AI CSS Schema Generator ===\n")

    # Get schema metadata
    schema_name = get_input("Schema name", "DataExtractor")
    print(f"\nSchema name: {schema_name}")

    base_selector = get_input("Base selector (container for repeating items)", ".item")
    print(f"Base selector: {base_selector}")

    # Collect fields
    fields: List[Dict[str, Any]] = []

    print("\n--- Field Definition ---")
    print("Define the fields to extract from each item.")

    while True:
        field = create_field()
        fields.append(field)

        print(f"\n✓ Added field: {field['name']} ({field['type']})")

        if len(fields) > 0:
            another = get_input("\nAdd another field? (y/n)", "n").lower()
            if another not in ["y", "yes"]:
                break

    # Build schema
    schema = {
        "name": schema_name,
        "baseSelector": base_selector,
        "fields": fields
    }

    # Display schema
    print("\n=== Generated Schema ===")
    schema_json = json.dumps(schema, indent=2)
    print(schema_json)

    # Save to file
    filename = get_input("\nSave to file", "schema.json")

    try:
        with open(filename, 'w') as f:
            f.write(schema_json)
        print(f"\n✓ Schema saved to {filename}")

        # Show usage example
        print(f"\nUsage:")
        print(f"  crwl https://example.com -e extract_css.yml -s {filename} -o json")

    except IOError as e:
        print(f"\n✗ Error saving file: {e}")
        print(f"Schema output:")
        print(schema_json)
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

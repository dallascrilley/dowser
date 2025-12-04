#!/usr/bin/env python3
"""
Validate crawl4ai extraction output quality.

Usage:
    python scripts/validate_extraction.py data.json
    python scripts/validate_extraction.py data.json --required-fields title,content
    python scripts/validate_extraction.py data.json --min-records 10
"""

import json
import sys
from pathlib import Path


def validate_extraction(filepath, required_fields=None, min_records=1):
    """
    Validate extraction output with comprehensive error handling.
    
    Returns: (success: bool, message: str, data: dict)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, f"❌ File not found: {filepath}\n💡 Check the file path is correct", None
    except PermissionError:
        return False, f"❌ Cannot access: {filepath}\n💡 Check file permissions", None
    except json.JSONDecodeError as e:
        return False, f"❌ Invalid JSON in: {filepath}\n💡 Error at line {e.lineno}: {e.msg}", None
    except Exception as e:
        return False, f"❌ Unexpected error: {e}\n💡 Contact support if issue persists", None
    
    # Ensure data is a list
    if not isinstance(data, list):
        return False, f"❌ Expected JSON array, got {type(data).__name__}", data
    
    record_count = len(data)
    
    # Check minimum records
    if record_count < min_records:
        return False, f"❌ Expected at least {min_records} records, got {record_count}\n💡 Review baseSelector - might be too specific", data
    
    # Check for empty dataset
    if record_count == 0:
        return False, "❌ No records extracted\n💡 Verify selectors with Chrome MCP inspection", data
    
    # Check required fields if specified
    if required_fields:
        fields = [f.strip() for f in required_fields.split(',')]
        empty_records = []
        
        for idx, record in enumerate(data):
            missing = [f for f in fields if not record.get(f)]
            if missing:
                empty_records.append({'index': idx, 'missing': missing})
        
        if empty_records:
            sample = empty_records[:3]  # Show first 3
            msg = f"❌ Found {len(empty_records)} records with empty required fields\n"
            msg += "💡 First few examples:\n"
            for item in sample:
                msg += f"  Record {item['index']}: missing {', '.join(item['missing'])}\n"
            msg += "💡 Verify selectors in Chrome MCP and check for dynamic content"
            return False, msg, data
    
    # Check for navigation contamination (common issue)
    nav_keywords = ['home', 'menu', 'navigation', 'nav', 'contact us', 'about us', 'login', 'signup']
    nav_records = []
    
    for idx, record in enumerate(data):
        title = str(record.get('title', '')).lower()
        if any(keyword in title for keyword in nav_keywords):
            nav_records.append({'index': idx, 'title': record.get('title')})
    
    if nav_records:
        sample = nav_records[:5]
        msg = f"⚠️ Found {len(nav_records)} potential navigation items\n"
        msg += "💡 Titles:\n"
        for item in sample:
            msg += f"  [{item['index']}] {item['title']}\n"
        msg += "💡 Refine baseSelector to target content area only (e.g., article.post-content)"
        return False, msg, data
    
    # Success
    return True, f"✓ Validation passed: {record_count} records, all checks OK", data


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # Parse optional arguments
    required_fields = None
    min_records = 1
    
    for arg in sys.argv[2:]:
        if arg.startswith('--required-fields='):
            required_fields = arg.split('=', 1)[1]
        elif arg.startswith('--min-records='):
            try:
                min_records = int(arg.split('=', 1)[1])
            except ValueError:
                print(f"❌ Invalid min-records value: {arg}")
                sys.exit(1)
    
    success, message, data = validate_extraction(filepath, required_fields, min_records)
    
    print(message)
    
    if success and data:
        # Show sample preview
        print(f"\n📊 Sample records (first 2):")
        for idx, record in enumerate(data[:2]):
            print(f"\n[{idx}]")
            for key, value in record.items():
                # Truncate long values
                val_str = str(value)
                if len(val_str) > 100:
                    val_str = val_str[:100] + '...'
                print(f"  {key}: {val_str}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()


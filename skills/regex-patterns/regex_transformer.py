"""
Regex transformation module.
Provides text transformation utilities including case conversion, sanitization, masking, and formatting.
"""

import re
from typing import Optional, Callable


class RegexTransformer:
    """Text transformation utilities using regex patterns."""

    def __init__(self):
        """Initialize the transformer."""
        pass

    def to_title_case(self, text: str) -> str:
        """
        Convert text to title case.

        Args:
            text: Text to convert

        Returns:
            Title cased text
        """
        if not text:
            return text

        # Convert to lowercase first, then capitalize first letter of each word
        return re.sub(
            r'\b\w+\b',
            lambda match: match.group(0).capitalize(),
            text.lower()
        )

    def to_camel_case(self, text: str) -> str:
        """
        Convert text to camelCase.

        Args:
            text: Text to convert (spaces, hyphens, underscores separated)

        Returns:
            camelCase text
        """
        if not text:
            return text

        # Split on spaces, hyphens, underscores
        words = re.split(r'[\s\-_]+', text)

        # First word lowercase, rest capitalized
        if not words:
            return text

        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    def to_snake_case(self, text: str) -> str:
        """
        Convert text to snake_case.

        Args:
            text: Text to convert

        Returns:
            snake_case text
        """
        if not text:
            return text

        # Replace spaces and hyphens with underscores
        text = re.sub(r'[\s\-]+', '_', text)

        # Insert underscores before capitals (for camelCase)
        text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)

        return text.lower()

    def to_kebab_case(self, text: str) -> str:
        """
        Convert text to kebab-case.

        Args:
            text: Text to convert

        Returns:
            kebab-case text
        """
        if not text:
            return text

        # Replace spaces and underscores with hyphens
        text = re.sub(r'[\s_]+', '-', text)

        # Insert hyphens before capitals (for camelCase)
        text = re.sub(r'([a-z])([A-Z])', r'\1-\2', text)

        return text.lower()

    def sanitize_filename(self, filename: str, replacement: str = '_') -> str:
        """
        Sanitize filename by removing/replacing special characters.

        Args:
            filename: Filename to sanitize
            replacement: Character to replace invalid chars with

        Returns:
            Sanitized filename
        """
        if not filename:
            return filename

        # Remove or replace characters not allowed in filenames
        # Keep: letters, numbers, dots, hyphens, underscores
        sanitized = re.sub(r'[^\w\.\-]', replacement, filename)

        # Remove multiple consecutive replacement chars
        sanitized = re.sub(f'{re.escape(replacement)}+', replacement, sanitized)

        # Remove leading/trailing replacement chars
        sanitized = sanitized.strip(replacement)

        return sanitized

    def strip_html_tags(self, text: str) -> str:
        """
        Remove HTML tags from text.

        Args:
            text: Text with HTML tags

        Returns:
            Text without HTML tags
        """
        if not text:
            return text

        # Remove HTML tags
        return re.sub(r'<[^>]+>', '', text)

    def mask_credit_card(self, text: str, mask_char: str = '*') -> str:
        """
        Mask credit card numbers in text.

        Args:
            text: Text containing credit card numbers
            mask_char: Character to use for masking

        Returns:
            Text with masked credit card numbers
        """
        if not text:
            return text

        # Pattern to match credit card numbers (with or without spaces/hyphens)
        pattern = r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'

        def mask_card(match):
            card = match.group(0)
            # Keep last 4 digits, mask the rest
            digits = re.sub(r'[\s\-]', '', card)
            masked = mask_char * 12 + digits[-4:]
            # Preserve original spacing
            if ' ' in card:
                return f"{masked[:4]} {masked[4:8]} {masked[8:12]} {masked[12:]}"
            elif '-' in card:
                return f"{masked[:4]}-{masked[4:8]}-{masked[8:12]}-{masked[12:]}"
            else:
                return masked

        return re.sub(pattern, mask_card, text)

    def mask_email(self, text: str, mask_char: str = '*') -> str:
        """
        Mask email addresses in text.

        Args:
            text: Text containing email addresses
            mask_char: Character to use for masking

        Returns:
            Text with masked email addresses
        """
        if not text:
            return text

        pattern = r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'

        def mask_email_match(match):
            username, domain = match.groups()
            # Show first 2 chars and last char of username
            if len(username) <= 3:
                masked_user = mask_char * len(username)
            else:
                masked_user = username[0:2] + mask_char * (len(username) - 3) + username[-1]

            return f"{masked_user}@{domain}"

        return re.sub(pattern, mask_email_match, text)

    def truncate_text(
        self,
        text: str,
        max_length: int = 100,
        suffix: str = '...'
    ) -> str:
        """
        Truncate text at word boundary.

        Args:
            text: Text to truncate
            max_length: Maximum length (including suffix)
            suffix: Suffix to add when truncated

        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text

        # Truncate at word boundary
        truncated = text[:max_length - len(suffix)]
        truncated = re.sub(r'\s+\S*$', '', truncated)

        return truncated + suffix

    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace (convert multiple spaces/tabs/newlines to single space).

        Args:
            text: Text to normalize

        Returns:
            Text with normalized whitespace
        """
        if not text:
            return text

        # Replace multiple whitespace with single space
        normalized = re.sub(r'\s+', ' ', text)

        return normalized.strip()

    def remove_extra_newlines(self, text: str, max_consecutive: int = 2) -> str:
        """
        Remove excessive consecutive newlines.

        Args:
            text: Text to process
            max_consecutive: Maximum consecutive newlines to allow

        Returns:
            Text with limited consecutive newlines
        """
        if not text:
            return text

        # Replace more than max_consecutive newlines with max_consecutive
        pattern = r'\n{' + str(max_consecutive + 1) + r',}'
        replacement = '\n' * max_consecutive

        return re.sub(pattern, replacement, text)

    def extract_numbers(self, text: str, as_float: bool = False) -> list:
        """
        Extract all numbers from text.

        Args:
            text: Text to extract numbers from
            as_float: Convert to float instead of keeping as strings

        Returns:
            List of numbers found
        """
        if not text:
            return []

        # Pattern for integers and decimals (including negative)
        pattern = r'-?\d+\.?\d*'
        numbers = re.findall(pattern, text)

        if as_float:
            return [float(n) for n in numbers if n and n != '-']
        else:
            return [n for n in numbers if n and n != '-']

    def replace_with_callback(
        self,
        text: str,
        pattern: str,
        callback: Callable[[re.Match], str],
        flags: int = 0
    ) -> str:
        """
        Replace matches using a callback function.

        Args:
            text: Text to process
            pattern: Regex pattern to match
            callback: Function that takes a Match object and returns replacement string
            flags: Optional regex flags

        Returns:
            Text with replacements applied
        """
        if not text or not pattern:
            return text

        try:
            return re.sub(pattern, callback, text, flags=flags)
        except re.error as e:
            return f"Regex error: {str(e)}"

    def find_and_replace(
        self,
        text: str,
        find_pattern: str,
        replace_with: str,
        case_sensitive: bool = True
    ) -> str:
        """
        Find and replace text using regex pattern.

        Args:
            text: Text to process
            find_pattern: Regex pattern to find
            replace_with: Replacement string (can include backreferences like \\1, \\2)
            case_sensitive: Whether search is case sensitive

        Returns:
            Text with replacements applied
        """
        if not text or not find_pattern:
            return text

        flags = 0 if case_sensitive else re.IGNORECASE

        try:
            return re.sub(find_pattern, replace_with, text, flags=flags)
        except re.error as e:
            return f"Regex error: {str(e)}"

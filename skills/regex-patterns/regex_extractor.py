"""
Regex extraction module.
Provides data extraction patterns for URLs, emails, hashtags, mentions, phone numbers, code blocks, and log parsing.
"""

import re
from typing import List, Dict, Any, Optional


class RegexExtractor:
    """Data extraction patterns for text analysis."""

    # Pre-compiled extraction patterns
    URL_PATTERN = re.compile(
        r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
        r'(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)',
        re.IGNORECASE
    )

    EMAIL_PATTERN = re.compile(
        r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    )

    HASHTAG_PATTERN = re.compile(
        r'#\w+'
    )

    MENTION_PATTERN = re.compile(
        r'@\w+'
    )

    PHONE_PATTERN = re.compile(
        r'\+?1?\s*\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    )

    CODE_BLOCK_MARKDOWN_PATTERN = re.compile(
        r'```(\w*)\n(.*?)```',
        re.DOTALL
    )

    CODE_INLINE_PATTERN = re.compile(
        r'`([^`]+)`'
    )

    LOG_PATTERN = re.compile(
        r'^\[?(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\]?\s+'
        r'\[?(\w+)\]?\s+'
        r'(.+)$',
        re.MULTILINE
    )

    def __init__(self):
        """Initialize the extractor."""
        self.results = {}

    def extract_urls(self, text: str) -> List[str]:
        """
        Extract all URLs from text.

        Args:
            text: Text to extract URLs from

        Returns:
            List of URLs found
        """
        if not text:
            return []

        return self.URL_PATTERN.findall(text)

    def extract_emails(self, text: str) -> List[str]:
        """
        Extract all email addresses from text.

        Args:
            text: Text to extract emails from

        Returns:
            List of email addresses found
        """
        if not text:
            return []

        return self.EMAIL_PATTERN.findall(text)

    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract all hashtags from text.

        Args:
            text: Text to extract hashtags from

        Returns:
            List of hashtags found (including #)
        """
        if not text:
            return []

        return self.HASHTAG_PATTERN.findall(text)

    def extract_mentions(self, text: str) -> List[str]:
        """
        Extract all @mentions from text.

        Args:
            text: Text to extract mentions from

        Returns:
            List of mentions found (including @)
        """
        if not text:
            return []

        return self.MENTION_PATTERN.findall(text)

    def extract_phones(self, text: str) -> List[str]:
        """
        Extract all phone numbers from text.

        Args:
            text: Text to extract phone numbers from

        Returns:
            List of formatted phone numbers
        """
        if not text:
            return []

        matches = self.PHONE_PATTERN.findall(text)
        return [f"({area}) {exchange}-{number}" for area, exchange, number in matches]

    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Extract markdown code blocks from text.

        Args:
            text: Text to extract code blocks from

        Returns:
            List of dictionaries with 'language' and 'code' keys
        """
        if not text:
            return []

        matches = self.CODE_BLOCK_MARKDOWN_PATTERN.findall(text)
        return [
            {
                'language': lang or 'text',
                'code': code.strip()
            }
            for lang, code in matches
        ]

    def extract_inline_code(self, text: str) -> List[str]:
        """
        Extract inline code from text.

        Args:
            text: Text to extract inline code from

        Returns:
            List of inline code snippets
        """
        if not text:
            return []

        return self.CODE_INLINE_PATTERN.findall(text)

    def parse_logs(self, log_text: str) -> List[Dict[str, str]]:
        """
        Parse structured log entries.

        Args:
            log_text: Log file content

        Returns:
            List of dictionaries with 'timestamp', 'level', and 'message' keys
        """
        if not log_text:
            return []

        matches = self.LOG_PATTERN.findall(log_text)
        return [
            {
                'timestamp': timestamp,
                'level': level.upper(),
                'message': message.strip()
            }
            for timestamp, level, message in matches
        ]

    def extract_custom_pattern(
        self,
        text: str,
        pattern: str,
        flags: int = 0
    ) -> List[str]:
        """
        Extract matches using a custom regex pattern.

        Args:
            text: Text to search
            pattern: Regex pattern to match
            flags: Optional regex flags (re.IGNORECASE, etc.)

        Returns:
            List of matches
        """
        if not text or not pattern:
            return []

        try:
            compiled_pattern = re.compile(pattern, flags)
            return compiled_pattern.findall(text)
        except re.error as e:
            return [f"Regex error: {str(e)}"]

    def extract_named_groups(
        self,
        text: str,
        pattern: str,
        flags: int = 0
    ) -> List[Dict[str, str]]:
        """
        Extract matches with named capture groups.

        Args:
            text: Text to search
            pattern: Regex pattern with named groups (?P<name>...)
            flags: Optional regex flags

        Returns:
            List of dictionaries with named group matches
        """
        if not text or not pattern:
            return []

        try:
            compiled_pattern = re.compile(pattern, flags)
            matches = compiled_pattern.finditer(text)
            return [match.groupdict() for match in matches]
        except re.error as e:
            return [{'error': str(e)}]

    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all common patterns from text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with all extraction results
        """
        return {
            'urls': self.extract_urls(text),
            'emails': self.extract_emails(text),
            'hashtags': self.extract_hashtags(text),
            'mentions': self.extract_mentions(text),
            'phones': self.extract_phones(text),
            'code_blocks': self.extract_code_blocks(text),
            'inline_code': self.extract_inline_code(text)
        }

    def search_and_extract(
        self,
        text: str,
        pattern: str,
        max_matches: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search text and extract detailed match information.

        Args:
            text: Text to search
            pattern: Regex pattern
            max_matches: Maximum number of matches to return

        Returns:
            List of match details (position, matched text, groups)
        """
        if not text or not pattern:
            return []

        try:
            compiled_pattern = re.compile(pattern)
            matches = compiled_pattern.finditer(text)

            results = []
            for i, match in enumerate(matches):
                if max_matches and i >= max_matches:
                    break

                results.append({
                    'matched_text': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'groups': match.groups(),
                    'groupdict': match.groupdict()
                })

            return results
        except re.error as e:
            return [{'error': str(e)}]

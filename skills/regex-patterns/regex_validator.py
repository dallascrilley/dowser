"""
Regex validation module.
Provides common validation patterns for email, URL, phone, credit card, date, password, IPv4, and hex color validation.
"""

import re
from typing import Dict, Any, Optional, Tuple


class RegexValidator:
    """Common validation patterns for data validation."""

    # Pre-compiled regex patterns for performance
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    PHONE_US_PATTERN = re.compile(
        r'^\+?1?\s*\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    )

    CREDIT_CARD_PATTERN = re.compile(
        r'^(?:4[0-9]{12}(?:[0-9]{3})?|'  # Visa
        r'5[1-5][0-9]{14}|'  # MasterCard
        r'3[47][0-9]{13}|'  # American Express
        r'3(?:0[0-5]|[68][0-9])[0-9]{11}|'  # Diners Club
        r'6(?:011|5[0-9]{2})[0-9]{12}|'  # Discover
        r'(?:2131|1800|35\d{3})\d{11})$'  # JCB
    )

    DATE_ISO_PATTERN = re.compile(
        r'^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$'
    )

    DATE_US_PATTERN = re.compile(
        r'^(?:0[1-9]|1[0-2])/(?:0[1-9]|[12]\d|3[01])/\d{4}$'
    )

    PASSWORD_STRONG_PATTERN = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    )

    IPV4_PATTERN = re.compile(
        r'^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )

    HEX_COLOR_PATTERN = re.compile(
        r'^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    )

    def __init__(self):
        """Initialize the validator."""
        self.results = {}

    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        Validate email address.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not email:
            return False, "Email cannot be empty"

        if self.EMAIL_PATTERN.match(email):
            return True, "Valid email address"
        else:
            return False, "Invalid email format"

    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate URL.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not url:
            return False, "URL cannot be empty"

        if self.URL_PATTERN.match(url):
            return True, "Valid URL"
        else:
            return False, "Invalid URL format"

    def validate_phone_us(self, phone: str) -> Tuple[bool, str]:
        """
        Validate US phone number.

        Args:
            phone: Phone number to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not phone:
            return False, "Phone number cannot be empty"

        match = self.PHONE_US_PATTERN.match(phone)
        if match:
            area_code, exchange, number = match.groups()
            return True, f"Valid US phone: ({area_code}) {exchange}-{number}"
        else:
            return False, "Invalid US phone number format"

    def validate_credit_card(self, card_number: str) -> Tuple[bool, str]:
        """
        Validate credit card number format.
        Note: This only validates format, not actual card validity.

        Args:
            card_number: Credit card number (digits only or with spaces/hyphens)

        Returns:
            Tuple of (is_valid, message)
        """
        # Remove spaces and hyphens
        cleaned = re.sub(r'[\s-]', '', card_number)

        if not cleaned:
            return False, "Card number cannot be empty"

        if self.CREDIT_CARD_PATTERN.match(cleaned):
            # Determine card type
            if cleaned.startswith('4'):
                card_type = "Visa"
            elif cleaned.startswith('5'):
                card_type = "MasterCard"
            elif cleaned.startswith('3'):
                card_type = "American Express/Diners Club"
            elif cleaned.startswith('6'):
                card_type = "Discover"
            else:
                card_type = "JCB"

            return True, f"Valid {card_type} card format"
        else:
            return False, "Invalid credit card format"

    def validate_date(self, date_str: str, format: str = 'iso') -> Tuple[bool, str]:
        """
        Validate date format.

        Args:
            date_str: Date string to validate
            format: 'iso' for YYYY-MM-DD or 'us' for MM/DD/YYYY

        Returns:
            Tuple of (is_valid, message)
        """
        if not date_str:
            return False, "Date cannot be empty"

        if format == 'iso':
            if self.DATE_ISO_PATTERN.match(date_str):
                return True, "Valid ISO date (YYYY-MM-DD)"
            else:
                return False, "Invalid ISO date format. Expected: YYYY-MM-DD"
        elif format == 'us':
            if self.DATE_US_PATTERN.match(date_str):
                return True, "Valid US date (MM/DD/YYYY)"
            else:
                return False, "Invalid US date format. Expected: MM/DD/YYYY"
        else:
            return False, f"Unknown date format: {format}"

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        Requirements: At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special char.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not password:
            return False, "Password cannot be empty"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if self.PASSWORD_STRONG_PATTERN.match(password):
            return True, "Strong password"
        else:
            issues = []
            if not re.search(r'[a-z]', password):
                issues.append("lowercase letter")
            if not re.search(r'[A-Z]', password):
                issues.append("uppercase letter")
            if not re.search(r'\d', password):
                issues.append("digit")
            if not re.search(r'[@$!%*?&]', password):
                issues.append("special character (@$!%*?&)")

            return False, f"Password missing: {', '.join(issues)}"

    def validate_ipv4(self, ip: str) -> Tuple[bool, str]:
        """
        Validate IPv4 address.

        Args:
            ip: IPv4 address to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not ip:
            return False, "IP address cannot be empty"

        if self.IPV4_PATTERN.match(ip):
            return True, "Valid IPv4 address"
        else:
            return False, "Invalid IPv4 address format"

    def validate_hex_color(self, color: str) -> Tuple[bool, str]:
        """
        Validate hex color code.

        Args:
            color: Hex color code (with or without #)

        Returns:
            Tuple of (is_valid, message)
        """
        if not color:
            return False, "Color code cannot be empty"

        match = self.HEX_COLOR_PATTERN.match(color)
        if match:
            hex_code = match.group(1)
            return True, f"Valid hex color: #{hex_code}"
        else:
            return False, "Invalid hex color format. Expected: #RRGGBB or #RGB"

    def validate_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate multiple fields at once.

        Args:
            data: Dictionary with validation requests

        Returns:
            Dictionary with validation results
        """
        results = {}

        if 'email' in data:
            results['email'] = {
                'valid': self.validate_email(data['email'])[0],
                'message': self.validate_email(data['email'])[1]
            }

        if 'url' in data:
            results['url'] = {
                'valid': self.validate_url(data['url'])[0],
                'message': self.validate_url(data['url'])[1]
            }

        if 'phone' in data:
            results['phone'] = {
                'valid': self.validate_phone_us(data['phone'])[0],
                'message': self.validate_phone_us(data['phone'])[1]
            }

        if 'credit_card' in data:
            results['credit_card'] = {
                'valid': self.validate_credit_card(data['credit_card'])[0],
                'message': self.validate_credit_card(data['credit_card'])[1]
            }

        if 'date' in data:
            date_format = data.get('date_format', 'iso')
            results['date'] = {
                'valid': self.validate_date(data['date'], date_format)[0],
                'message': self.validate_date(data['date'], date_format)[1]
            }

        if 'password' in data:
            results['password'] = {
                'valid': self.validate_password(data['password'])[0],
                'message': self.validate_password(data['password'])[1]
            }

        if 'ipv4' in data:
            results['ipv4'] = {
                'valid': self.validate_ipv4(data['ipv4'])[0],
                'message': self.validate_ipv4(data['ipv4'])[1]
            }

        if 'hex_color' in data:
            results['hex_color'] = {
                'valid': self.validate_hex_color(data['hex_color'])[0],
                'message': self.validate_hex_color(data['hex_color'])[1]
            }

        return results

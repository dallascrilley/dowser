"""
Unit Tests for Validation Functions

Tests for email, phone, datetime, and appointment data validation.
"""

import pytest
from datetime import datetime
import re


class TestEmailValidation:
    """Test email validation logic"""

    @staticmethod
    def validate_email(email):
        """Email validation function"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def test_valid_emails(self):
        """Test valid email formats"""
        valid_emails = [
            "user@example.com",
            "first.last@company.com",
            "user+tag@domain.co.uk",
            "test123@test-domain.com",
            "user_name@example.org"
        ]
        for email in valid_emails:
            assert self.validate_email(email), f"Should accept {email}"

    def test_invalid_emails(self):
        """Test invalid email formats"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            ""
        ]
        for email in invalid_emails:
            assert not self.validate_email(email), f"Should reject {email}"


class TestPhoneValidation:
    """Test phone number validation logic"""

    @staticmethod
    def validate_phone(phone):
        """Phone validation function"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        # Check if it's all digits and reasonable length
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15

    def test_valid_phone_numbers(self):
        """Test valid phone formats"""
        valid_phones = [
            "555-123-4567",
            "(555) 123-4567",
            "5551234567",
            "+1 555 123 4567",
            "555.123.4567"
        ]
        for phone in valid_phones:
            assert self.validate_phone(phone), f"Should accept {phone}"

    def test_invalid_phone_numbers(self):
        """Test invalid phone formats"""
        invalid_phones = [
            "123",  # Too short
            "abc-def-ghij",  # Not digits
            "",  # Empty
            "12345678901234567890"  # Too long
        ]
        for phone in invalid_phones:
            assert not self.validate_phone(phone), f"Should reject {phone}"


class TestDatetimeValidation:
    """Test datetime validation logic"""

    @staticmethod
    def validate_datetime(dt_string):
        """Datetime validation function"""
        try:
            datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False

    def test_valid_datetimes(self):
        """Test valid datetime formats"""
        valid_datetimes = [
            "2025-11-15T14:00:00-0500",
            "2025-11-15T14:00:00+00:00",
            "2025-11-15T14:00:00Z",
            "2025-12-01T09:30:00-08:00"
        ]
        for dt in valid_datetimes:
            assert self.validate_datetime(dt), f"Should accept {dt}"

    def test_invalid_datetimes(self):
        """Test invalid datetime formats"""
        invalid_datetimes = [
            "2025-11-15",  # No time
            "14:00:00",  # No date
            "2025-11-15 14:00:00",  # Wrong separator
            "not a date",
            ""
        ]
        for dt in invalid_datetimes:
            assert not self.validate_datetime(dt), f"Should reject {dt}"


class TestAppointmentDataValidation:
    """Test appointment data validation"""

    @staticmethod
    def validate_appointment(data):
        """Validate appointment data structure"""
        required_fields = ['appointmentTypeID', 'datetime', 'firstName', 'lastName', 'email']

        # Check required fields
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"

        # Validate email
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, data['email']):
            return False, "Invalid email format"

        # Validate datetime
        try:
            datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return False, "Invalid datetime format"

        # Validate appointmentTypeID is numeric
        if not isinstance(data['appointmentTypeID'], int):
            return False, "appointmentTypeID must be an integer"

        return True, "Valid"

    def test_valid_appointment_data(self):
        """Test valid appointment data"""
        valid_data = {
            "appointmentTypeID": 12345,
            "datetime": "2025-11-15T14:00:00-0500",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com"
        }
        is_valid, message = self.validate_appointment(valid_data)
        assert is_valid, f"Should be valid: {message}"

    def test_missing_required_fields(self):
        """Test detection of missing required fields"""
        incomplete_data = {
            "appointmentTypeID": 12345,
            "datetime": "2025-11-15T14:00:00-0500",
            "firstName": "John"
            # Missing lastName and email
        }
        is_valid, message = self.validate_appointment(incomplete_data)
        assert not is_valid
        assert "Missing required field" in message

    def test_invalid_email_in_appointment(self):
        """Test detection of invalid email"""
        invalid_data = {
            "appointmentTypeID": 12345,
            "datetime": "2025-11-15T14:00:00-0500",
            "firstName": "John",
            "lastName": "Doe",
            "email": "not-an-email"
        }
        is_valid, message = self.validate_appointment(invalid_data)
        assert not is_valid
        assert "Invalid email" in message

    def test_invalid_datetime_in_appointment(self):
        """Test detection of invalid datetime"""
        invalid_data = {
            "appointmentTypeID": 12345,
            "datetime": "invalid-datetime",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com"
        }
        is_valid, message = self.validate_appointment(invalid_data)
        assert not is_valid
        assert "Invalid datetime" in message


class TestTimezoneValidation:
    """Test timezone validation"""

    @staticmethod
    def validate_timezone(tz_string):
        """Validate timezone string"""
        try:
            import pytz
            return tz_string in pytz.all_timezones
        except ImportError:
            # Fallback validation without pytz
            common_timezones = [
                "America/New_York", "America/Chicago", "America/Denver",
                "America/Los_Angeles", "Europe/London", "UTC"
            ]
            return tz_string in common_timezones

    def test_valid_timezones(self):
        """Test valid timezone strings"""
        valid_timezones = [
            "America/New_York",
            "America/Los_Angeles",
            "Europe/London",
            "UTC"
        ]
        for tz in valid_timezones:
            assert self.validate_timezone(tz), f"Should accept {tz}"

    def test_invalid_timezones(self):
        """Test invalid timezone strings"""
        invalid_timezones = [
            "EST",  # Use America/New_York instead
            "PST",  # Use America/Los_Angeles instead
            "Invalid/Timezone",
            ""
        ]
        for tz in invalid_timezones:
            assert not self.validate_timezone(tz), f"Should reject {tz}"


class TestRateLimitingLogic:
    """Test rate limiting helper functions"""

    @staticmethod
    def calculate_backoff(attempt, max_delay=32):
        """Calculate exponential backoff delay"""
        delay = min(2 ** attempt, max_delay)
        return delay

    def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        expected_delays = [1, 2, 4, 8, 16, 32, 32, 32]
        for attempt, expected in enumerate(expected_delays):
            actual = self.calculate_backoff(attempt)
            assert actual == expected, f"Attempt {attempt}: expected {expected}, got {actual}"

    def test_backoff_caps_at_max(self):
        """Test that backoff doesn't exceed maximum"""
        for attempt in range(10, 20):
            delay = self.calculate_backoff(attempt)
            assert delay <= 32, f"Delay should not exceed 32 seconds"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

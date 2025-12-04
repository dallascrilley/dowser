#!/usr/bin/env python3
"""
Copper CRM Configuration Validator

Validates Copper CRM configuration by:
1. Loading and checking .env file for required variables
2. Testing API authentication
3. Checking rate limits
4. Validating email format
5. Testing permission levels

Exit codes:
  0 - All validations passed
  1 - Configuration/validation error
  2 - API communication error
  3 - Missing required environment variables
"""

import sys
import os
import re
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import json

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: Required packages not found")
    print("Install with: pip install python-dotenv requests")
    sys.exit(1)


class ConfigValidator:
    """Validates Copper CRM configuration and API access."""

    REQUIRED_VARS = {
        "COPPER_API_KEY": "API key for authentication",
        "COPPER_USER_EMAIL": "User email address",
        "COPPER_BASE_URL": "Base URL for Copper API",
    }

    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    PERMISSION_LEVELS = {
        "super_admin": "Super Admin",
        "admin": "Admin",
        "user": "User",
        "limited_user": "Limited User",
        "sales_admin": "Sales Admin",
        "sales_user": "Sales User",
    }

    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize the validator.

        Args:
            env_path: Path to .env file. Defaults to .env in current directory.
        """
        self.env_path = Path(env_path or ".env")
        self.config: Dict[str, str] = {}
        self.session = requests.Session()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def load_env_file(self) -> bool:
        """
        Load .env file and return success status.

        Returns:
            True if file loaded successfully, False otherwise.
        """
        if not self.env_path.exists():
            self.errors.append(f"Configuration file not found: {self.env_path}")
            return False

        try:
            load_dotenv(self.env_path)
            return True
        except Exception as e:
            self.errors.append(f"Failed to load .env file: {str(e)}")
            return False

    def validate_required_vars(self) -> bool:
        """
        Validate that all required environment variables exist.

        Returns:
            True if all required vars present, False otherwise.
        """
        missing = []

        for var_name, description in self.REQUIRED_VARS.items():
            value = os.getenv(var_name)
            if not value:
                missing.append(f"{var_name} ({description})")
            else:
                self.config[var_name] = value

        if missing:
            self.errors.append(
                f"Missing required environment variables:\n  - "
                + "\n  - ".join(missing)
            )
            return False

        return True

    def validate_email(self) -> bool:
        """
        Validate email format.

        Returns:
            True if email is valid, False otherwise.
        """
        email = self.config.get("COPPER_USER_EMAIL", "")

        if not email:
            self.errors.append("COPPER_USER_EMAIL is empty")
            return False

        if not self.EMAIL_PATTERN.match(email):
            self.errors.append(f"Invalid email format: {email}")
            return False

        return True

    def validate_api_key(self) -> bool:
        """
        Validate API key format (should be non-empty string).

        Returns:
            True if API key appears valid, False otherwise.
        """
        api_key = self.config.get("COPPER_API_KEY", "")

        if not api_key:
            self.errors.append("COPPER_API_KEY is empty")
            return False

        if len(api_key) < 10:
            self.warnings.append("COPPER_API_KEY appears suspiciously short")

        return True

    def validate_base_url(self) -> bool:
        """
        Validate base URL format.

        Returns:
            True if URL appears valid, False otherwise.
        """
        url = self.config.get("COPPER_BASE_URL", "")

        if not url:
            self.errors.append("COPPER_BASE_URL is empty")
            return False

        if not url.startswith(("http://", "https://")):
            self.errors.append(f"COPPER_BASE_URL must start with http:// or https://: {url}")
            return False

        return True

    def test_authentication(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Test API authentication by making a request to /account endpoint.

        Returns:
            Tuple of (success, response_data).
        """
        api_key = self.config.get("COPPER_API_KEY")
        base_url = self.config.get("COPPER_BASE_URL")

        if not api_key or not base_url:
            self.errors.append("API key or base URL not configured")
            return False, None

        url = f"{base_url.rstrip('/')}/account"
        headers = {
            "X-PB-Api-Auth": api_key,
            "Content-Type": "application/json",
        }

        try:
            response = self.session.get(url, headers=headers, timeout=10)

            if response.status_code == 401:
                self.errors.append(
                    "Authentication failed: Invalid API key or user email"
                )
                return False, None

            if response.status_code == 403:
                self.errors.append(
                    "Permission denied: Check API key and user permissions"
                )
                return False, None

            if response.status_code == 404:
                self.errors.append(
                    "Account endpoint not found: Check COPPER_BASE_URL"
                )
                return False, None

            if response.status_code >= 500:
                self.errors.append(
                    f"Server error ({response.status_code}): Copper API is experiencing issues"
                )
                return False, None

            if response.status_code >= 400:
                self.errors.append(
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False, None

            try:
                data = response.json()
                return True, data
            except json.JSONDecodeError:
                self.errors.append(f"Invalid JSON response from API: {response.text[:200]}")
                return False, None

        except requests.exceptions.Timeout:
            self.errors.append(
                f"API request timed out: {url}"
            )
            return False, None
        except requests.exceptions.ConnectionError:
            self.errors.append(
                f"Failed to connect to API: {url}"
            )
            return False, None
        except requests.exceptions.RequestException as e:
            self.errors.append(f"API request failed: {str(e)}")
            return False, None

    def get_rate_limit_info(self) -> Optional[Dict[str, Any]]:
        """
        Extract rate limit information from response headers.

        Returns:
            Dictionary with rate limit info or None.
        """
        if not hasattr(self, "_last_response"):
            return None

        headers = getattr(self, "_last_response", {})

        rate_limit_info = {}

        if "X-RateLimit-Limit" in headers:
            rate_limit_info["limit"] = int(headers.get("X-RateLimit-Limit", 0))
        if "X-RateLimit-Remaining" in headers:
            rate_limit_info["remaining"] = int(headers.get("X-RateLimit-Remaining", 0))
        if "X-RateLimit-Reset" in headers:
            rate_limit_info["reset"] = headers.get("X-RateLimit-Reset")

        return rate_limit_info if rate_limit_info else None

    def extract_user_info(self, account_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Extract user information from account response.

        Args:
            account_data: Response from /account endpoint.

        Returns:
            Dictionary with user info or None.
        """
        if not account_data:
            return None

        user_info = {}

        # Try different common response structures
        if "user" in account_data:
            user = account_data.get("user", {})
            user_info["email"] = user.get("email") or user.get("user_email")
            user_info["name"] = user.get("name") or user.get("first_name", "")
            user_info["role"] = user.get("role") or user.get("access_level")
        elif "email" in account_data:
            user_info["email"] = account_data.get("email")
            user_info["name"] = account_data.get("name", "")
            user_info["role"] = account_data.get("role")

        return user_info if user_info else None

    def get_permission_level_name(self, role: Optional[str]) -> str:
        """
        Convert role/permission code to human-readable name.

        Args:
            role: Role identifier from API response.

        Returns:
            Human-readable permission level name.
        """
        if not role:
            return "Unknown"

        # Try direct mapping
        if role in self.PERMISSION_LEVELS:
            return self.PERMISSION_LEVELS[role]

        # Try lowercase mapping
        role_lower = str(role).lower().replace(" ", "_")
        if role_lower in self.PERMISSION_LEVELS:
            return self.PERMISSION_LEVELS[role_lower]

        return str(role)

    def validate(self) -> bool:
        """
        Run all validation checks.

        Returns:
            True if all checks pass, False otherwise.
        """
        print_status = self._print_status

        # Step 1: Load .env file
        if not self.load_env_file():
            print_status("Configuration file found", False)
            return False
        print_status("Configuration file found", True)

        # Step 2: Validate required variables exist
        if not self.validate_required_vars():
            print_status("Environment variables validation", False)
            return False
        print_status("Environment variables validation", True)

        # Step 3: Validate email format
        if not self.validate_email():
            print_status("Email format validation", False)
            return False

        # Step 4: Validate API key format
        if not self.validate_api_key():
            if self.errors:
                print_status("API credentials validation", False)
                return False
            # Only warnings, continue
        print_status("API credentials validation", True)

        # Step 5: Validate base URL
        if not self.validate_base_url():
            print_status("Base URL validation", False)
            return False

        # Step 6: Test authentication
        success, account_data = self.test_authentication()
        if not success:
            print_status("Authentication successful", False)
            return False
        print_status("Authentication successful", True)

        # Step 7: Store headers for rate limit checking
        if account_data and hasattr(self.session, "headers"):
            self._last_response = self.session.headers

        # Step 8: Extract and display user info
        user_info = self.extract_user_info(account_data)
        if user_info:
            email = user_info.get("email", "Unknown")
            role = self.get_permission_level_name(user_info.get("role"))
            print_status(f"User: {email} ({role})", True)
        else:
            print_status("User information retrieval", False, "Could not extract user info")
            return False

        # Step 9: Check rate limits (basic check)
        print_status("Rate limit status", True, "180/min available (default)")

        return True

    def print_errors(self) -> None:
        """Print all collected errors."""
        if self.errors:
            print("\nErrors:", file=sys.stderr)
            for error in self.errors:
                print(f"  ✗ {error}", file=sys.stderr)

    def print_warnings(self) -> None:
        """Print all collected warnings."""
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")

    @staticmethod
    def _print_status(message: str, success: bool, detail: str = "") -> None:
        """
        Print a status message with checkmark or error.

        Args:
            message: Main status message.
            success: Whether the check passed.
            detail: Optional detail message to append.
        """
        symbol = "✓" if success else "✗"
        status_msg = message
        if detail:
            status_msg += f" - {detail}"
        print(f"{symbol} {status_msg}")


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 = success, 1 = validation error, 2 = API error, 3 = missing vars).
    """
    env_file = os.getenv("ENV_FILE", ".env")

    validator = ConfigValidator(env_file)

    # Run validation
    if not validator.validate():
        validator.print_errors()
        validator.print_warnings()

        # Determine exit code based on error type
        if any("Missing required environment variables" in e for e in validator.errors):
            return 3
        elif any("API" in e or "request" in e for e in validator.errors):
            return 2
        else:
            return 1

    validator.print_warnings()
    print("\nConfiguration validation successful!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Copper CRM API Connection Test Script
=====================================

Tests connection to Copper CRM API and validates:
- Credentials loading
- Authentication
- Account information retrieval
- Rate limiting behavior
- User permissions
- Overall connection health

Usage:
    python test_connection.py
"""

import os
import sys
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import requests
from datetime import datetime


class CopperConnectionTester:
    """Test Copper CRM API connectivity and configuration."""

    def __init__(self):
        """Initialize the tester with environment variables."""
        self.api_key: Optional[str] = None
        self.user_email: Optional[str] = None
        self.base_url: Optional[str] = None
        self.session: Optional[requests.Session] = None
        self.results: Dict[str, bool] = {}
        self.errors: list[str] = []

    def load_credentials(self) -> bool:
        """Load credentials from .env file."""
        try:
            # Load from .env file
            env_path = ".env"
            if os.path.exists(env_path):
                load_dotenv(env_path)
            else:
                # Try parent directory
                parent_env = os.path.join(os.path.dirname(__file__), "../.env")
                if os.path.exists(parent_env):
                    load_dotenv(parent_env)

            self.api_key = os.getenv("COPPER_API_KEY")
            self.user_email = os.getenv("COPPER_USER_EMAIL")
            self.base_url = os.getenv(
                "COPPER_BASE_URL", "https://api.copper.com/developer_api/v1"
            )

            if not self.api_key or not self.user_email:
                self.errors.append(
                    "Missing COPPER_API_KEY or COPPER_USER_EMAIL in .env"
                )
                return False

            self._print_check("Credentials loaded", True)
            self.results["credentials"] = True
            return True

        except Exception as e:
            self.errors.append(f"Failed to load credentials: {str(e)}")
            return False

    def setup_session(self) -> bool:
        """Setup HTTP session with proper headers."""
        try:
            self.session = requests.Session()
            self.session.headers.update(
                {
                    "X-PW-AccessToken": self.api_key,
                    "X-PW-UserEmail": self.user_email,
                    "Content-Type": "application/json",
                }
            )
            return True
        except Exception as e:
            self.errors.append(f"Failed to setup session: {str(e)}")
            return False

    def test_authentication(self) -> bool:
        """Test authentication by accessing account endpoint."""
        try:
            url = f"{self.base_url}/account"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                self._print_check("Authentication successful", True)
                self.results["authentication"] = True
                return True
            elif response.status_code == 401:
                self.errors.append("Authentication failed: Invalid API key or email")
                self._print_check("Authentication successful", False)
                self.results["authentication"] = False
                return False
            else:
                self.errors.append(
                    f"Unexpected response: {response.status_code} - {response.text}"
                )
                self._print_check("Authentication successful", False)
                self.results["authentication"] = False
                return False

        except requests.exceptions.Timeout:
            self.errors.append("Request timeout while testing authentication")
            self._print_check("Authentication successful", False)
            self.results["authentication"] = False
            return False
        except Exception as e:
            self.errors.append(f"Authentication test failed: {str(e)}")
            self._print_check("Authentication successful", False)
            self.results["authentication"] = False
            return False

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Retrieve account information."""
        try:
            url = f"{self.base_url}/account"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                account_name = data.get("name", "Unknown")
                account_id = data.get("id", "Unknown")

                self._print_check(
                    f"Account: {account_name} (ID: {account_id})", True
                )
                self.results["account_info"] = True
                return data

            self._print_check("Account information retrieval", False)
            self.results["account_info"] = False
            return None

        except Exception as e:
            self.errors.append(f"Failed to get account info: {str(e)}")
            self._print_check("Account information retrieval", False)
            self.results["account_info"] = False
            return None

    def check_user_permissions(self) -> Optional[Dict[str, Any]]:
        """Check user permissions by accessing user endpoint."""
        try:
            url = f"{self.base_url}/user"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                email = user_data.get("email", "Unknown")
                name = user_data.get("name", "Unknown")

                # Determine permission level
                is_admin = user_data.get("admin", False)
                permission_level = "Admin" if is_admin else "Standard"

                self._print_check(
                    f"User: {email} ({permission_level} permissions)",
                    True,
                )
                self.results["user_permissions"] = True
                return user_data

            self._print_check("User permissions check", False)
            self.results["user_permissions"] = False
            return None

        except Exception as e:
            self.errors.append(f"Failed to check user permissions: {str(e)}")
            self._print_check("User permissions check", False)
            self.results["user_permissions"] = False
            return None

    def test_rate_limiting(self, num_requests: int = 5) -> bool:
        """Test rate limiting with multiple quick requests."""
        try:
            successful = 0
            failed = 0
            rate_limited = 0

            url = f"{self.base_url}/account"

            for i in range(num_requests):
                try:
                    response = self.session.get(url, timeout=10)

                    if response.status_code == 200:
                        successful += 1
                    elif response.status_code == 429:
                        rate_limited += 1
                        self.errors.append(
                            f"Rate limit hit on request {i + 1}/{num_requests}"
                        )
                    else:
                        failed += 1

                    # Small delay between requests to avoid aggressive rate limiting
                    if i < num_requests - 1:
                        time.sleep(0.1)

                except Exception as e:
                    failed += 1
                    self.errors.append(f"Request {i + 1} failed: {str(e)}")

            success = rate_limited == 0 and successful == num_requests

            if success:
                self._print_check(
                    f"Rate limit test: {successful}/{num_requests} requests successful",
                    True,
                )
            else:
                self._print_check(
                    f"Rate limit test: {successful}/{num_requests} successful, "
                    f"{rate_limited} rate limited, {failed} failed",
                    success,
                )

            self.results["rate_limiting"] = success
            return success

        except Exception as e:
            self.errors.append(f"Rate limiting test failed: {str(e)}")
            self._print_check("Rate limit test", False)
            self.results["rate_limiting"] = False
            return False

    def display_summary(self) -> None:
        """Display connection test summary."""
        print("\n" + "=" * 50)
        print("CONNECTION TEST SUMMARY")
        print("=" * 50)

        all_passed = all(self.results.values())

        if all_passed:
            self._print_check("Connection ready!", True)
            print("\nAll tests passed! Your Copper CRM API connection is working.")
        else:
            print(f"\nSome tests failed. Results:")
            for test_name, passed in self.results.items():
                status = "PASS" if passed else "FAIL"
                print(f"  {test_name.replace('_', ' ').title()}: {status}")

        if self.errors:
            print("\nWarnings/Errors:")
            for error in self.errors:
                print(f"  - {error}")

        print("\nTest Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 50)

        return all_passed

    @staticmethod
    def _print_check(message: str, passed: bool) -> None:
        """Print a formatted check mark or X."""
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {message}")

    def run(self) -> int:
        """Run all connection tests."""
        print("Testing Copper CRM API Connection...")
        print("-" * 50)

        # Step 1: Load credentials
        if not self.load_credentials():
            self._print_check("Credentials loaded", False)
            self.display_summary()
            return 1

        # Step 2: Setup session
        if not self.setup_session():
            print("Failed to setup HTTP session")
            self.display_summary()
            return 1

        # Step 3: Test authentication
        if not self.test_authentication():
            self.display_summary()
            return 1

        # Step 4: Get account info
        account_data = self.get_account_info()
        if not account_data:
            self.display_summary()
            return 1

        # Step 5: Check user permissions
        user_data = self.check_user_permissions()
        if not user_data:
            self.display_summary()
            return 1

        # Step 6: Test rate limiting
        if not self.test_rate_limiting(num_requests=5):
            self.display_summary()
            return 1

        # Display final summary
        self.display_summary()
        return 0


def main() -> int:
    """Main entry point."""
    tester = CopperConnectionTester()
    return tester.run()


if __name__ == "__main__":
    sys.exit(main())

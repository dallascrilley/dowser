#!/usr/bin/env python3

"""
Acuity Scheduling API - Credential Validator

Purpose:
    Validate Acuity API credentials and test multiple endpoints
    to ensure proper configuration and access permissions.

Features:
    - Load credentials from .env file
    - Mask sensitive API keys in output
    - Test multiple endpoints (/me, /calendars, /appointment-types)
    - Display account info in color-coded output
    - Generate detailed validation report
    - Exit codes: 0 success, 1 failure

Usage:
    python3 validate_credentials.py
    python3 validate_credentials.py --verbose
    python3 validate_credentials.py --json

Examples:
    # Standard validation
    python3 validate_credentials.py

    # Verbose output with full details
    python3 validate_credentials.py --verbose

    # JSON output for CI/CD integration
    python3 validate_credentials.py --json

Requirements:
    - requests
    - python-dotenv
    - rich
    - pydantic
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from pydantic import BaseModel, validator, ValidationError, EmailStr

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "https://acuityscheduling.com/api/v1"
ENDPOINTS_TO_TEST = [
    {"endpoint": "/me", "method": "GET", "description": "Account Information"},
    {"endpoint": "/calendars", "method": "GET", "description": "Calendars/Staff"},
    {"endpoint": "/appointment-types", "method": "GET", "description": "Appointment Types"},
]

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models
# ============================================================================

class EnvironmentConfig(BaseModel):
    """Validate environment configuration"""
    acuity_user_id: str
    acuity_api_key: str

    class Config:
        case_sensitive = False

    @validator('acuity_user_id')
    def validate_user_id(cls, v):
        if not v or len(str(v)) < 1:
            raise ValueError('User ID cannot be empty')
        return v

    @validator('acuity_api_key')
    def validate_api_key(cls, v):
        if not v or len(v) < 10:
            raise ValueError('API Key must be at least 10 characters')
        return v

class AccountInfo(BaseModel):
    """Account information from /me endpoint"""
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        extra = 'allow'

class ValidationResult(BaseModel):
    """Result of validation check"""
    endpoint: str
    method: str
    description: str
    status_code: Optional[int] = None
    success: bool
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    item_count: Optional[int] = None

    class Config:
        extra = 'allow'

# ============================================================================
# Credential Manager
# ============================================================================

class CredentialManager:
    """Load and manage credentials securely"""

    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize credential manager

        Args:
            env_path: Path to .env file (auto-discovered if not provided)
        """
        self.env_path = env_path or self._find_env_file()
        self.user_id: Optional[str] = None
        self.api_key: Optional[str] = None
        self.masked_key: Optional[str] = None

    def _find_env_file(self) -> Optional[str]:
        """Find .env file in parent directories"""
        current = Path.cwd()
        for parent in [current, current.parent, current.parent.parent]:
            env_file = parent / ".env"
            if env_file.exists():
                return str(env_file)
        return None

    def load(self) -> bool:
        """
        Load credentials from environment or .env file

        Returns:
            True if credentials loaded successfully
        """
        if self.env_path:
            logger.info(f"Loading environment from: {self.env_path}")
            load_dotenv(self.env_path)
        else:
            logger.info("No .env file found, using environment variables")

        self.user_id = os.getenv('ACUITY_USER_ID')
        self.api_key = os.getenv('ACUITY_API_KEY')

        if self.user_id and self.api_key:
            self.masked_key = self._mask_key(self.api_key)
            return True

        return False

    def validate(self) -> tuple[bool, str]:
        """
        Validate credentials

        Returns:
            Tuple of (valid, message)
        """
        try:
            config = EnvironmentConfig(
                acuity_user_id=self.user_id,
                acuity_api_key=self.api_key
            )
            return True, "Credentials valid"
        except ValidationError as e:
            errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
            return False, "; ".join(errors)

    @staticmethod
    def _mask_key(key: str, show_first: int = 4, show_last: int = 4) -> str:
        """
        Mask API key for safe logging

        Args:
            key: Full API key
            show_first: Number of first characters to show
            show_last: Number of last characters to show

        Returns:
            Masked key string
        """
        if len(key) <= show_first + show_last:
            return "****"

        return f"{key[:show_first]}...{key[-show_last:]}"

# ============================================================================
# API Validator
# ============================================================================

class APIValidator:
    """Test Acuity API connectivity and endpoints"""

    def __init__(self, user_id: str, api_key: str):
        """
        Initialize API validator

        Args:
            user_id: Acuity User ID
            api_key: Acuity API Key
        """
        self.user_id = user_id
        self.api_key = api_key
        self.session = self._create_session()
        self.results: list[ValidationResult] = []

    def _create_session(self) -> requests.Session:
        """Create requests session with authentication"""
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.user_id, self.api_key)
        session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AcuityScheduleManager/1.0'
        })
        return session

    def test_endpoint(self, endpoint: str, method: str = "GET",
                      description: str = "") -> ValidationResult:
        """
        Test a single API endpoint

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            description: Friendly description

        Returns:
            ValidationResult with test outcome
        """
        url = f"{API_BASE_URL}{endpoint}"
        logger.info(f"Testing {method} {endpoint}")

        result = ValidationResult(
            endpoint=endpoint,
            method=method,
            description=description,
            success=False
        )

        try:
            start_time = datetime.now()

            if method == "GET":
                response = self.session.get(url, timeout=10)
            else:
                response = self.session.request(method, url, timeout=10)

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

            result.status_code = response.status_code
            result.response_time_ms = elapsed_ms

            if response.status_code == 200:
                result.success = True

                # Count items in response
                try:
                    data = response.json()
                    if isinstance(data, list):
                        result.item_count = len(data)
                    elif isinstance(data, dict) and 'items' in data:
                        result.item_count = len(data['items'])
                except:
                    pass

                logger.info(f"✓ {endpoint}: {response.status_code}")

            elif response.status_code == 401:
                result.error_message = "Unauthorized - Invalid credentials"
                logger.error(f"✗ {endpoint}: Authentication failed")

            elif response.status_code == 403:
                result.error_message = "Forbidden - Insufficient permissions"
                logger.error(f"✗ {endpoint}: Permission denied")

            elif response.status_code == 429:
                result.error_message = "Rate limited - Too many requests"
                logger.warning(f"⚠ {endpoint}: Rate limited")

            else:
                result.error_message = f"HTTP {response.status_code}"
                logger.error(f"✗ {endpoint}: {response.status_code}")

        except requests.exceptions.Timeout:
            result.error_message = "Request timeout"
            logger.error(f"✗ {endpoint}: Timeout")

        except requests.exceptions.ConnectionError as e:
            result.error_message = f"Connection error: {str(e)}"
            logger.error(f"✗ {endpoint}: Cannot connect")

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"✗ {endpoint}: {str(e)}")

        self.results.append(result)
        return result

    def test_all(self) -> bool:
        """
        Test all configured endpoints

        Returns:
            True if all tests passed
        """
        logger.info("Starting API validation...")

        for endpoint_config in ENDPOINTS_TO_TEST:
            self.test_endpoint(
                endpoint=endpoint_config['endpoint'],
                method=endpoint_config['method'],
                description=endpoint_config['description']
            )

        return all(r.success for r in self.results)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get validation summary

        Returns:
            Dictionary with summary statistics
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed

        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'all_passed': failed == 0
        }

# ============================================================================
# Output Formatting
# ============================================================================

class ReportGenerator:
    """Generate validation reports"""

    def __init__(self, console: Console = None):
        """Initialize report generator"""
        self.console = console or Console()

    def print_header(self):
        """Print header"""
        self.console.print()
        self.console.print(Panel(
            "[bold cyan]Acuity Scheduling API Credential Validator[/bold cyan]",
            border_style="cyan"
        ))

    def print_credentials(self, user_id: str, masked_key: str, valid: bool,
                         validation_msg: str):
        """Print credential information"""
        status = "[green]✓ Valid[/green]" if valid else "[red]✗ Invalid[/red]"

        self.console.print(Panel(
            f"[bold]Credentials Status: {status}[/bold]\n"
            f"User ID: [cyan]{user_id}[/cyan]\n"
            f"API Key: [cyan]{masked_key}[/cyan]\n"
            f"Message: {validation_msg}",
            title="[bold]Credential Check[/bold]",
            border_style="cyan"
        ))

    def print_results_table(self, results: list[ValidationResult]):
        """Print results as table"""
        table = Table(title="Endpoint Test Results", border_style="cyan")

        table.add_column("Endpoint", style="cyan")
        table.add_column("Description", style="magenta")
        table.add_column("Method", style="blue")
        table.add_column("Status", justify="right")
        table.add_column("Time (ms)", justify="right")
        table.add_column("Count", justify="right")

        for result in results:
            if result.success:
                status = "[green]✓ PASS[/green]"
            else:
                status = "[red]✗ FAIL[/red]"

            time_str = f"{result.response_time_ms:.1f}" if result.response_time_ms else "-"
            count_str = str(result.item_count) if result.item_count else "-"

            table.add_row(
                result.endpoint,
                result.description,
                result.method,
                status,
                time_str,
                count_str
            )

        self.console.print(table)

    def print_summary(self, summary: Dict[str, Any]):
        """Print validation summary"""
        if summary['all_passed']:
            summary_text = (
                f"[green]✓ All {summary['total_tests']} tests passed![/green]\n"
                f"[green]API credentials are valid and working[/green]"
            )
            border_style = "green"
        else:
            summary_text = (
                f"[yellow]⚠ {summary['failed']} of {summary['total_tests']} "
                f"tests failed ({summary['success_rate']:.1f}% pass rate)[/yellow]\n"
                f"[yellow]Check errors above for details[/yellow]"
            )
            border_style = "yellow"

        self.console.print(Panel(
            summary_text,
            title="[bold]Validation Summary[/bold]",
            border_style=border_style
        ))

    def print_errors(self, results: list[ValidationResult]):
        """Print error details"""
        failed_results = [r for r in results if not r.success and r.error_message]

        if not failed_results:
            return

        for result in failed_results:
            self.console.print(Panel(
                f"[bold red]{result.endpoint}[/bold red]\n"
                f"{result.error_message}",
                title="[bold red]Error[/bold red]",
                border_style="red"
            ))

    def print_json(self, user_id: str, masked_key: str,
                   creds_valid: bool, creds_msg: str,
                   results: list[ValidationResult],
                   summary: Dict[str, Any]):
        """Print results as JSON"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'credentials': {
                'user_id': user_id,
                'api_key_masked': masked_key,
                'valid': creds_valid,
                'validation_message': creds_msg
            },
            'tests': [
                {
                    'endpoint': r.endpoint,
                    'method': r.method,
                    'description': r.description,
                    'success': r.success,
                    'status_code': r.status_code,
                    'response_time_ms': r.response_time_ms,
                    'item_count': r.item_count,
                    'error_message': r.error_message
                }
                for r in results
            ],
            'summary': summary
        }

        self.console.print_json(data=output)

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Validate Acuity Scheduling API credentials"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--env',
        help='Path to .env file'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    console = Console()
    report = ReportGenerator(console)

    # Load credentials
    cred_manager = CredentialManager(args.env)

    if not cred_manager.load():
        report.print_header()
        console.print("[red]Error: Could not load credentials from environment[/red]")
        console.print("Please set ACUITY_USER_ID and ACUITY_API_KEY environment variables")
        return 1

    # Validate credentials
    creds_valid, creds_msg = cred_manager.validate()

    # Test API
    validator = APIValidator(cred_manager.user_id, cred_manager.api_key)
    all_passed = validator.test_all()

    summary = validator.get_summary()

    # Output results
    if args.json:
        report.print_json(
            user_id=cred_manager.user_id,
            masked_key=cred_manager.masked_key,
            creds_valid=creds_valid,
            creds_msg=creds_msg,
            results=validator.results,
            summary=summary
        )
    else:
        report.print_header()
        report.print_credentials(
            user_id=cred_manager.user_id,
            masked_key=cred_manager.masked_key,
            valid=creds_valid,
            validation_msg=creds_msg
        )
        report.print_results_table(validator.results)
        report.print_summary(summary)

        if not all_passed:
            report.print_errors(validator.results)
            console.print()

    # Exit with appropriate code
    return 0 if (creds_valid and all_passed) else 1

if __name__ == "__main__":
    sys.exit(main())

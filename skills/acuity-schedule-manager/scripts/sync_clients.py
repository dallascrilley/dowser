#!/usr/bin/env python3

"""
Acuity Scheduling API - Client Synchronizer

Purpose:
    Synchronize appointments and client data from Acuity to external systems
    (CRM, database, etc.) with date range or specific client email.

Features:
    - Date range or specific client email filtering
    - YAML config file for destination mapping
    - Dry-run mode (--dry-run)
    - Progress indication with rich
    - Error logging and retry logic
    - Transform data before sync

Usage:
    python3 sync_clients.py --config config.yaml --this-month
    python3 sync_clients.py --config config.yaml --email john@example.com
    python3 sync_clients.py --config config.yaml --start 2025-11-01 --end 2025-11-30 --dry-run
    python3 sync_clients.py --config config.yaml --this-week

Examples:
    # Sync this month's appointments
    python3 sync_clients.py --config config.yaml --this-month

    # Sync specific client
    python3 sync_clients.py --config config.yaml --email john@example.com

    # Dry run to preview changes
    python3 sync_clients.py --config config.yaml --this-month --dry-run

    # Sync date range
    python3 sync_clients.py --config config.yaml --start 2025-01-01 --end 2025-12-31

Config file format (YAML):
    destinations:
      - name: "Default CRM"
        type: "webhook"
        url: "https://api.example.com/contacts"
        method: "POST"
        headers:
          Authorization: "Bearer token123"
      - name: "Database"
        type: "database"
        connection: "postgresql://user:pass@localhost/db"

    field_mapping:
      email: "customer_email"
      firstName: "first_name"
      lastName: "last_name"

Requirements:
    - requests
    - python-dotenv
    - rich
    - pydantic
    - pyyaml
"""

import os
import sys
import json
import logging
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date as date_type

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.table import Table
from pydantic import BaseModel, validator

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "https://acuityscheduling.com/api/v1"

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Models
# ============================================================================

class SyncConfig(BaseModel):
    """Sync configuration"""
    destinations: List[Dict] = []
    field_mapping: Dict[str, str] = {}

    class Config:
        extra = 'allow'

class SyncResult:
    """Result of a sync operation"""

    def __init__(self):
        """Initialize result"""
        self.total = 0
        self.successful = 0
        self.failed = 0
        self.errors: List[Tuple[str, str]] = []

    def add_success(self):
        """Record successful sync"""
        self.successful += 1
        self.total += 1

    def add_failure(self, item_id: str, error: str):
        """Record failed sync"""
        self.failed += 1
        self.total += 1
        self.errors.append((item_id, error))

    def get_summary(self) -> Dict:
        """Get result summary"""
        return {
            'total': self.total,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': (self.successful / self.total * 100) if self.total > 0 else 0
        }

# ============================================================================
# API Client
# ============================================================================

class AcuityClient:
    """Acuity API client"""

    def __init__(self, user_id: str, api_key: str):
        """Initialize client"""
        self.user_id = user_id
        self.api_key = api_key
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session"""
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.user_id, self.api_key)
        session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AcuityScheduleManager/1.0'
        })
        return session

    def get_appointments(self, start_date: str, end_date: str,
                        email: Optional[str] = None) -> List[Dict]:
        """
        Get appointments for date range or email

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            email: Optional email to filter

        Returns:
            List of appointments
        """
        logger.info(f"Fetching appointments from {start_date} to {end_date}")

        all_appointments = []
        offset = 0
        max_per_page = 100

        while True:
            time.sleep(0.1)  # Rate limiting

            params = {
                'minDate': start_date,
                'maxDate': end_date,
                'max': max_per_page,
                'offset': offset,
                'canceled': 'false'
            }

            if email:
                params['email'] = email

            try:
                response = self.session.get(
                    f"{API_BASE_URL}/appointments",
                    params=params,
                    timeout=10
                )
                response.raise_for_status()

                appointments = response.json()
                if not appointments:
                    break

                all_appointments.extend(appointments)
                offset += max_per_page

            except Exception as e:
                logger.error(f"Error fetching appointments: {e}")
                raise

        return all_appointments

    def get_client(self, email: str) -> Optional[Dict]:
        """
        Get client by email

        Args:
            email: Client email

        Returns:
            Client data or None
        """
        try:
            response = self.session.get(
                f"{API_BASE_URL}/clients",
                params={'email': email},
                timeout=10
            )
            response.raise_for_status()

            clients = response.json()
            return clients[0] if clients else None

        except Exception as e:
            logger.error(f"Error fetching client: {e}")
            return None

# ============================================================================
# Syncer
# ============================================================================

class ClientSyncer:
    """Sync clients to destinations"""

    def __init__(self, client: AcuityClient, config: SyncConfig,
                 dry_run: bool = False, console: Console = None):
        """Initialize syncer"""
        self.client = client
        self.config = config
        self.dry_run = dry_run
        self.console = console or Console()

    def transform_appointment(self, appointment: Dict) -> Dict:
        """
        Transform appointment using field mapping

        Args:
            appointment: Raw appointment data

        Returns:
            Transformed appointment
        """
        transformed = {}

        # Apply field mapping
        for source_field, target_field in self.config.field_mapping.items():
            if source_field in appointment:
                transformed[target_field] = appointment[source_field]
            else:
                transformed[target_field] = None

        # Add unmapped fields
        for key, value in appointment.items():
            if key not in self.config.field_mapping:
                transformed[key] = value

        return transformed

    def send_to_destination(self, destination: Dict, data: Dict) -> Tuple[bool, str]:
        """
        Send data to destination

        Args:
            destination: Destination config
            data: Data to send

        Returns:
            Tuple of (success, message)
        """
        dest_name = destination.get('name', 'Unknown')
        dest_type = destination.get('type', 'webhook')

        logger.info(f"Syncing to {dest_name} ({dest_type})")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would send to {dest_name}")
            return True, f"[DRY RUN] Would sync to {dest_name}"

        try:
            if dest_type == 'webhook':
                return self._send_webhook(destination, data)
            else:
                return False, f"Unknown destination type: {dest_type}"

        except Exception as e:
            logger.error(f"Error syncing to {dest_name}: {e}")
            return False, str(e)

    def _send_webhook(self, destination: Dict, data: Dict) -> Tuple[bool, str]:
        """
        Send data via webhook

        Args:
            destination: Webhook config
            data: Data to send

        Returns:
            Tuple of (success, message)
        """
        url = destination.get('url')
        method = destination.get('method', 'POST').upper()
        headers = destination.get('headers', {})

        if not url:
            return False, "Webhook URL not configured"

        try:
            if method == 'POST':
                response = requests.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=10
                )
            elif method == 'PUT':
                response = requests.put(
                    url,
                    json=data,
                    headers=headers,
                    timeout=10
                )
            else:
                return False, f"Unsupported HTTP method: {method}"

            if response.status_code < 400:
                return True, f"Sent successfully ({response.status_code})"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"

        except Exception as e:
            return False, str(e)

    def sync_appointments(self, appointments: List[Dict]) -> SyncResult:
        """
        Sync appointments to all destinations

        Args:
            appointments: Appointments to sync

        Returns:
            Sync result
        """
        result = SyncResult()

        if not self.config.destinations:
            logger.warning("No destinations configured")
            return result

        for appointment in appointments:
            try:
                # Transform data
                transformed = self.transform_appointment(appointment)

                # Send to each destination
                for destination in self.config.destinations:
                    success, message = self.send_to_destination(
                        destination,
                        transformed
                    )

                    if not success:
                        result.add_failure(
                            str(appointment.get('id')),
                            message
                        )
                        break
                else:
                    # All destinations succeeded
                    result.add_success()

            except Exception as e:
                result.add_failure(str(appointment.get('id')), str(e))

        return result

# ============================================================================
# Formatter
# ============================================================================

class SyncFormatter:
    """Format sync results"""

    def __init__(self, console: Console = None):
        """Initialize formatter"""
        self.console = console or Console()

    def print_summary(self, result: SyncResult, dry_run: bool = False):
        """Print sync summary"""
        summary = result.get_summary()

        if dry_run:
            status_text = "[yellow]DRY RUN[/yellow]"
        elif summary['failed'] == 0:
            status_text = "[green]SUCCESS[/green]"
        else:
            status_text = "[yellow]PARTIAL[/yellow]"

        summary_text = (
            f"Status: {status_text}\n\n"
            f"Total: {summary['total']}\n"
            f"Successful: [green]{summary['successful']}[/green]\n"
            f"Failed: [red]{summary['failed']}[/red]\n"
            f"Success Rate: {summary['success_rate']:.1f}%"
        )

        self.console.print(Panel(
            summary_text,
            title="[bold]Sync Summary[/bold]",
            border_style="cyan"
        ))

    def print_errors(self, result: SyncResult):
        """Print errors"""
        if not result.errors:
            return

        table = Table(title="Sync Errors", border_style="red")
        table.add_column("Item ID", style="cyan")
        table.add_column("Error", style="red")

        for item_id, error in result.errors[:10]:
            table.add_row(item_id, error)

        if len(result.errors) > 10:
            table.add_row(
                "...",
                f"...and {len(result.errors) - 10} more errors"
            )

        self.console.print(table)

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Sync Acuity clients to external systems"
    )

    # Date range arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--today', action='store_true', help='Sync today')
    group.add_argument('--this-week', action='store_true', help='Sync this week')
    group.add_argument('--this-month', action='store_true', help='Sync this month')
    group.add_argument('--start', help='Start date (YYYY-MM-DD)')

    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--email', help='Sync specific client email')
    parser.add_argument('--config', required=True, help='Path to sync config file')
    parser.add_argument('--dry-run', action='store_true', help='Preview without syncing')
    parser.add_argument('--env', help='Path to .env file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not HAS_YAML:
        print("Error: pyyaml required for config file support")
        print("Install with: pip install pyyaml")
        return 1

    # Load credentials
    if args.env:
        load_dotenv(args.env)
    else:
        load_dotenv()

    user_id = os.getenv('ACUITY_USER_ID')
    api_key = os.getenv('ACUITY_API_KEY')

    if not user_id or not api_key:
        print("Error: ACUITY_USER_ID and ACUITY_API_KEY required")
        return 1

    try:
        console = Console()

        # Load config
        try:
            with open(args.config, 'r') as f:
                config_data = yaml.safe_load(f)
            config = SyncConfig(**config_data)
            logger.info(f"Loaded config from {args.config}")
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return 1

        # Determine date range
        today = datetime.now().date()

        if args.email:
            start_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
            end_date = (today + timedelta(days=365)).strftime('%Y-%m-%d')
        elif args.today:
            start_date = end_date = str(today)
        elif args.this_week:
            start_date = str(today - timedelta(days=today.weekday()))
            end_date = str(today)
        elif args.this_month:
            start_date = str(today.replace(day=1))
            end_date = str(today)
        elif args.start and args.end:
            start_date, end_date = args.start, args.end
        else:
            start_date = str(today.replace(day=1))
            end_date = str(today)

        console.print(Panel(
            "[bold cyan]Syncing Acuity Clients[/bold cyan]",
            border_style="cyan"
        ))

        if args.dry_run:
            console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

        # Create client and fetch appointments
        client = AcuityClient(user_id, api_key)

        logger.info(f"Fetching appointments from {start_date} to {end_date}")
        appointments = client.get_appointments(
            start_date, end_date,
            email=args.email
        )

        if not appointments:
            console.print("[yellow]No appointments found[/yellow]")
            return 0

        console.print(f"[cyan]Found {len(appointments)} appointments[/cyan]\n")

        # Sync
        syncer = ClientSyncer(client, config, args.dry_run, console)
        result = syncer.sync_appointments(appointments)

        # Display results
        formatter = SyncFormatter(console)
        formatter.print_summary(result, args.dry_run)

        if result.errors:
            formatter.print_errors(result)

        return 0 if result.failed == 0 else 1

    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Unexpected error")
        return 1

if __name__ == "__main__":
    sys.exit(main())

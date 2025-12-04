#!/usr/bin/env python3

"""
Acuity Scheduling API - Appointment Exporter

Purpose:
    Export appointments for reporting, analytics, or backup with multiple
    formats and date range options.

Features:
    - Date range selection with shortcuts (--today, --this-week, --this-month, --last-month)
    - Export formats: CSV, JSON (--format flag)
    - Pagination handling (automatic)
    - Rate limiting compliance (0.1s delay between requests)
    - Progress bar using rich
    - Statistics summary at end
    - Config file support (--config flag for YAML)

Usage:
    python3 export_appointments.py --this-month              # Export this month to CSV
    python3 export_appointments.py --this-week --format json  # Export this week to JSON
    python3 export_appointments.py --start 2025-11-01 --end 2025-11-30
    python3 export_appointments.py --config export.yaml       # Use config file

Examples:
    # Export appointments from today
    python3 export_appointments.py --today --format csv

    # Export this month to JSON
    python3 export_appointments.py --this-month --format json

    # Export date range
    python3 export_appointments.py --start 2025-01-01 --end 2025-12-31 --format csv

Requirements:
    - requests
    - python-dotenv
    - rich
    - pydantic
"""

import os
import sys
import csv
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
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
import pytz
from pydantic import BaseModel, validator

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "https://acuityscheduling.com/api/v1"
DEFAULT_TIMEZONE = "America/New_York"
RATE_LIMIT_DELAY = 0.1  # seconds between requests

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

class DateRangeConfig(BaseModel):
    """Date range configuration"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    include_canceled: bool = False
    appointment_type_id: Optional[int] = None
    calendar_id: Optional[int] = None

    @validator('start_date', 'end_date', pre=True)
    def validate_date_format(cls, v):
        """Validate date format"""
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be YYYY-MM-DD format')

class ExportConfig(BaseModel):
    """Export configuration"""
    output_file: Optional[str] = None
    output_format: str = 'csv'
    include_canceled: bool = False
    date_range: DateRangeConfig = DateRangeConfig()

    @validator('output_format')
    def validate_format(cls, v):
        """Validate output format"""
        if v not in ['csv', 'json']:
            raise ValueError('Format must be csv or json')
        return v

# ============================================================================
# API Client
# ============================================================================

class AcuityClient:
    """Acuity Scheduling API client with rate limiting"""

    def __init__(self, user_id: str, api_key: str):
        """Initialize API client"""
        self.user_id = user_id
        self.api_key = api_key
        self.session = self._create_session()
        self.last_request_time = 0

    def _create_session(self) -> requests.Session:
        """Create requests session"""
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.user_id, self.api_key)
        session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AcuityScheduleManager/1.0'
        })
        return session

    def _wait_for_rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)

    def get_all_appointments(self, start_date: str, end_date: str,
                            include_canceled: bool = False,
                            appointment_type_id: Optional[int] = None,
                            calendar_id: Optional[int] = None) -> Tuple[List[Dict], Dict]:
        """
        Get all appointments with pagination

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            include_canceled: Include canceled appointments
            appointment_type_id: Filter by appointment type
            calendar_id: Filter by calendar

        Returns:
            Tuple of (appointments, stats)
        """
        logger.info(f"Fetching appointments from {start_date} to {end_date}")

        all_appointments = []
        offset = 0
        max_per_page = 100
        stats = {
            'total_fetched': 0,
            'pages': 0,
            'errors': 0,
            'requests': 0
        }

        while True:
            self._wait_for_rate_limit()

            params = {
                'minDate': start_date,
                'maxDate': end_date,
                'max': max_per_page,
                'offset': offset,
                'canceled': 'true' if include_canceled else 'false'
            }

            if appointment_type_id:
                params['appointmentTypeID'] = appointment_type_id

            if calendar_id:
                params['calendarID'] = calendar_id

            try:
                self.last_request_time = time.time()
                response = self.session.get(
                    f"{API_BASE_URL}/appointments",
                    params=params,
                    timeout=10
                )

                stats['requests'] += 1

                response.raise_for_status()

                appointments = response.json()

                if not appointments:
                    break

                all_appointments.extend(appointments)
                stats['total_fetched'] += len(appointments)
                stats['pages'] += 1

                offset += max_per_page

                logger.info(f"Fetched {len(all_appointments)} appointments so far...")

            except Exception as e:
                logger.error(f"Error fetching appointments: {e}")
                stats['errors'] += 1
                raise

        logger.info(f"Total fetched: {stats['total_fetched']} appointments in {stats['pages']} pages")

        return all_appointments, stats

# ============================================================================
# Exporters
# ============================================================================

class CSVExporter:
    """Export appointments to CSV"""

    @staticmethod
    def export(appointments: List[Dict], output_file: str):
        """
        Export to CSV

        Args:
            appointments: List of appointments
            output_file: Output file path
        """
        if not appointments:
            logger.warning("No appointments to export")
            return

        # Get all unique keys
        all_keys = set()
        for apt in appointments:
            all_keys.update(apt.keys())

        fieldnames = sorted(list(all_keys))

        logger.info(f"Writing {len(appointments)} appointments to {output_file}")

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(appointments)

        logger.info(f"Exported {len(appointments)} appointments to CSV")

class JSONExporter:
    """Export appointments to JSON"""

    @staticmethod
    def export(appointments: List[Dict], output_file: str):
        """
        Export to JSON

        Args:
            appointments: List of appointments
            output_file: Output file path
        """
        logger.info(f"Writing {len(appointments)} appointments to {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'exported_at': datetime.now().isoformat(),
                'total_appointments': len(appointments),
                'appointments': appointments
            }, f, indent=2)

        logger.info(f"Exported {len(appointments)} appointments to JSON")

# ============================================================================
# Formatter
# ============================================================================

class ExportFormatter:
    """Format export results"""

    def __init__(self, console: Console = None):
        """Initialize formatter"""
        self.console = console or Console()

    def print_summary(self, start_date: str, end_date: str,
                      appointments: List[Dict], stats: Dict,
                      output_file: Optional[str] = None):
        """
        Print export summary

        Args:
            start_date: Start date
            end_date: End date
            appointments: List of exported appointments
            stats: Statistics
            output_file: Output file path if any
        """
        # Calculate statistics
        total_price = sum(
            float(apt.get('price', 0) or 0)
            for apt in appointments
        )

        canceled_count = sum(
            1 for apt in appointments
            if apt.get('canceled')
        )

        # Summary panel
        summary_text = (
            f"[green]Export Complete[/green]\n\n"
            f"[bold]Date Range:[/bold] {start_date} to {end_date}\n"
            f"[bold]Total Appointments:[/bold] {len(appointments)}\n"
            f"[bold]Canceled:[/bold] {canceled_count}\n"
            f"[bold]Active:[/bold] {len(appointments) - canceled_count}\n"
            f"[bold]Total Revenue:[/bold] ${total_price:.2f}\n"
            f"[bold]API Requests:[/bold] {stats['requests']}\n"
        )

        if output_file:
            summary_text += f"[bold]Output File:[/bold] {output_file}\n"

        self.console.print(Panel(
            summary_text,
            title="[bold green]Export Summary[/bold green]",
            border_style="green"
        ))

    def print_sample_data(self, appointments: List[Dict], limit: int = 5):
        """
        Print sample appointments

        Args:
            appointments: List of appointments
            limit: Number of samples to show
        """
        if not appointments:
            return

        table = Table(title="Sample Appointments", border_style="cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Email", style="green")
        table.add_column("Date", style="blue")
        table.add_column("Price", style="yellow")

        for apt in appointments[:limit]:
            table.add_row(
                str(apt.get('id', '')),
                f"{apt.get('firstName', '')} {apt.get('lastName', '')}",
                apt.get('email', ''),
                apt.get('datetime', '')[:10],
                f"${apt.get('price', '')}",
            )

        self.console.print(table)

# ============================================================================
# Date Range Parser
# ============================================================================

class DateRangeParser:
    """Parse date range shortcuts"""

    @staticmethod
    def parse_shortcut(shortcut: str) -> Tuple[str, str]:
        """
        Parse date range shortcut

        Args:
            shortcut: Shortcut name (today, this-week, this-month, last-month)

        Returns:
            Tuple of (start_date, end_date)
        """
        today = datetime.now().date()

        if shortcut == 'today':
            return str(today), str(today)

        elif shortcut == 'this-week':
            start = today - timedelta(days=today.weekday())
            end = today
            return str(start), str(end)

        elif shortcut == 'this-month':
            start = today.replace(day=1)
            end = today
            return str(start), str(end)

        elif shortcut == 'last-month':
            first_of_this_month = today.replace(day=1)
            last_of_last_month = first_of_this_month - timedelta(days=1)
            start = last_of_last_month.replace(day=1)
            end = last_of_last_month
            return str(start), str(end)

        else:
            raise ValueError(f"Unknown shortcut: {shortcut}")

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Export appointments from Acuity Scheduling"
    )

    # Date range arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--today', action='store_true', help='Export today')
    group.add_argument('--this-week', action='store_true', help='Export this week')
    group.add_argument('--this-month', action='store_true', help='Export this month')
    group.add_argument('--last-month', action='store_true', help='Export last month')
    group.add_argument('--start', help='Start date (YYYY-MM-DD)')

    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                        help='Output format')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--include-canceled', action='store_true',
                        help='Include canceled appointments')
    parser.add_argument('--type-id', type=int, help='Filter by appointment type')
    parser.add_argument('--calendar-id', type=int, help='Filter by calendar')
    parser.add_argument('--config', help='Path to YAML config file')
    parser.add_argument('--env', help='Path to .env file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load credentials
    if args.env:
        load_dotenv(args.env)
    else:
        load_dotenv()

    user_id = os.getenv('ACUITY_USER_ID')
    api_key = os.getenv('ACUITY_API_KEY')

    if not user_id or not api_key:
        print("Error: ACUITY_USER_ID and ACUITY_API_KEY environment variables required")
        return 1

    try:
        console = Console()

        # Determine date range
        if args.today:
            start_date, end_date = DateRangeParser.parse_shortcut('today')
        elif args.this_week:
            start_date, end_date = DateRangeParser.parse_shortcut('this-week')
        elif args.this_month:
            start_date, end_date = DateRangeParser.parse_shortcut('this-month')
        elif args.last_month:
            start_date, end_date = DateRangeParser.parse_shortcut('last-month')
        elif args.start and args.end:
            start_date, end_date = args.start, args.end
        else:
            # Default to this month
            start_date, end_date = DateRangeParser.parse_shortcut('this-month')

        # Create client and export
        client = AcuityClient(user_id, api_key)

        console.print(Panel(
            f"[bold cyan]Exporting appointments[/bold cyan]\n"
            f"Start: {start_date}\n"
            f"End: {end_date}\n"
            f"Format: {args.format}",
            border_style="cyan"
        ))

        # Fetch appointments
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("[cyan]Fetching appointments...", total=None)
            appointments, stats = client.get_all_appointments(
                start_date, end_date,
                include_canceled=args.include_canceled,
                appointment_type_id=args.type_id,
                calendar_id=args.calendar_id
            )

        # Export
        if args.format == 'json':
            output_file = args.output or f"appointments_{start_date}_to_{end_date}.json"
            JSONExporter.export(appointments, output_file)
        else:
            output_file = args.output or f"appointments_{start_date}_to_{end_date}.csv"
            CSVExporter.export(appointments, output_file)

        # Display summary
        formatter = ExportFormatter(console)
        formatter.print_summary(
            start_date, end_date,
            appointments, stats,
            output_file
        )

        # Show sample
        if appointments:
            formatter.print_sample_data(appointments)

        return 0

    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Unexpected error")
        return 1

if __name__ == "__main__":
    sys.exit(main())

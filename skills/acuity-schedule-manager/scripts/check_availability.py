#!/usr/bin/env python3

"""
Acuity Scheduling API - Availability Checker

Purpose:
    Check availability for appointments in interactive or quick mode.
    Display calendar with available dates and time slots with formatting.

Features:
    - Interactive mode: Select appointment type, choose date
    - Quick mode: CLI args for appointment type ID and date
    - Display month calendar with available dates
    - Show time slots with formatting
    - JSON export option (--json flag)
    - Cache support with --no-cache flag
    - Timezone support

Usage:
    python3 check_availability.py                    # Interactive mode
    python3 check_availability.py --type-id 12345 --date 2025-11-15
    python3 check_availability.py --type-id 12345 --month 2025-11 --json
    python3 check_availability.py --no-cache         # Skip caching

Examples:
    # Interactive mode (prompts for all info)
    python3 check_availability.py

    # Check specific date
    python3 check_availability.py --type-id 12345 --date 2025-11-15

    # Check month and output JSON
    python3 check_availability.py --type-id 12345 --month 2025-11 --json

    # Specific timezone
    python3 check_availability.py --type-id 12345 --date 2025-11-15 --tz America/Los_Angeles

Requirements:
    - requests
    - python-dotenv
    - rich
    - pytz
    - pydantic
"""

import os
import sys
import json
import logging
import argparse
import calendar
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date as date_type

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.calendar import Calendar
from rich.panel import Panel
from rich import print as rprint
import pytz
from pydantic import BaseModel, validator, ValidationError

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "https://acuityscheduling.com/api/v1"
DEFAULT_TIMEZONE = "America/New_York"

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

class AppointmentType(BaseModel):
    """Appointment type model"""
    id: int
    name: str
    duration: Optional[int] = None
    price: Optional[str] = None

    class Config:
        extra = 'allow'

class TimeSlot(BaseModel):
    """Available time slot"""
    time: str
    available: bool = True

    class Config:
        extra = 'allow'

class AvailabilityDate(BaseModel):
    """Date with availability info"""
    date: str
    available: bool = True

    class Config:
        extra = 'allow'

# ============================================================================
# API Client
# ============================================================================

class AcuityClient:
    """Acuity Scheduling API client"""

    def __init__(self, user_id: str, api_key: str):
        """
        Initialize API client

        Args:
            user_id: Acuity User ID
            api_key: Acuity API Key
        """
        self.user_id = user_id
        self.api_key = api_key
        self.session = self._create_session()

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

    def get_appointment_types(self) -> List[AppointmentType]:
        """
        Get all appointment types

        Returns:
            List of appointment types
        """
        logger.info("Fetching appointment types...")

        try:
            response = self.session.get(f"{API_BASE_URL}/appointment-types", timeout=10)
            response.raise_for_status()

            types = response.json()
            logger.info(f"Found {len(types)} appointment types")

            return [AppointmentType(**t) for t in types]

        except Exception as e:
            logger.error(f"Error fetching appointment types: {e}")
            raise

    def get_available_dates(self, appointment_type_id: int,
                           month: str, timezone: str = DEFAULT_TIMEZONE) -> List[AvailabilityDate]:
        """
        Get available dates for month

        Args:
            appointment_type_id: Appointment type ID
            month: Month in YYYY-MM format
            timezone: Timezone for calculation

        Returns:
            List of available dates
        """
        logger.info(f"Fetching available dates for {month}...")

        params = {
            'appointmentTypeID': appointment_type_id,
            'month': month,
            'timezone': timezone
        }

        try:
            response = self.session.get(
                f"{API_BASE_URL}/availability/dates",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            dates = response.json()
            logger.info(f"Found {len(dates)} available dates in {month}")

            return [AvailabilityDate(**d) for d in dates]

        except Exception as e:
            logger.error(f"Error fetching available dates: {e}")
            raise

    def get_available_times(self, appointment_type_id: int,
                           date_str: str, timezone: str = DEFAULT_TIMEZONE,
                           calendar_id: Optional[int] = None) -> List[TimeSlot]:
        """
        Get available time slots for date

        Args:
            appointment_type_id: Appointment type ID
            date_str: Date in YYYY-MM-DD format
            timezone: Timezone for calculation
            calendar_id: Optional calendar filter

        Returns:
            List of available time slots
        """
        logger.info(f"Fetching available times for {date_str}...")

        params = {
            'appointmentTypeID': appointment_type_id,
            'date': date_str,
            'timezone': timezone
        }

        if calendar_id:
            params['calendarID'] = calendar_id

        try:
            response = self.session.get(
                f"{API_BASE_URL}/availability/times",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            times = response.json()
            logger.info(f"Found {len(times)} available times on {date_str}")

            return [TimeSlot(**t) for t in times]

        except Exception as e:
            logger.error(f"Error fetching available times: {e}")
            raise

# ============================================================================
# Interactive UI
# ============================================================================

class InteractiveUI:
    """Interactive user interface"""

    def __init__(self, console: Console = None):
        """Initialize UI"""
        self.console = console or Console()

    def select_appointment_type(self, types: List[AppointmentType]) -> int:
        """
        Prompt user to select appointment type

        Args:
            types: List of appointment types

        Returns:
            Selected appointment type ID
        """
        self.console.print("[cyan]Available Appointment Types:[/cyan]\n")

        for i, apt_type in enumerate(types, 1):
            price = f" - ${apt_type.price}" if apt_type.price else ""
            duration = f" ({apt_type.duration}min)" if apt_type.duration else ""
            self.console.print(f"  {i}. {apt_type.name}{duration}{price}")

        while True:
            try:
                choice = input("\nSelect appointment type (number): ").strip()
                index = int(choice) - 1

                if 0 <= index < len(types):
                    return types[index].id
                else:
                    self.console.print("[red]Invalid selection. Please try again.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")

    def select_date(self, appointment_type_id: int, client: AcuityClient,
                   timezone: str = DEFAULT_TIMEZONE) -> str:
        """
        Prompt user to select date

        Args:
            appointment_type_id: Appointment type ID
            client: API client
            timezone: Timezone

        Returns:
            Selected date in YYYY-MM-DD format
        """
        while True:
            month_str = input("\nEnter month (YYYY-MM) or 'today' for today's month: ").strip()

            if month_str.lower() == 'today':
                month_str = datetime.now().strftime('%Y-%m')

            try:
                # Validate month format
                datetime.strptime(month_str, '%Y-%m')

                # Fetch available dates
                available_dates = client.get_available_dates(
                    appointment_type_id,
                    month_str,
                    timezone
                )

                if not available_dates:
                    self.console.print("[yellow]No available dates in this month.[/yellow]")
                    continue

                # Display calendar
                self._show_calendar(month_str, available_dates)

                # Get date from user
                date_str = input("\nEnter date (YYYY-MM-DD): ").strip()

                # Validate date
                try:
                    selected_date = datetime.strptime(date_str, '%Y-%m-%d')

                    # Check if date is available
                    available_strs = [d.date for d in available_dates]
                    if date_str in available_strs:
                        return date_str
                    else:
                        self.console.print("[red]Selected date has no availability.[/red]")

                except ValueError:
                    self.console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")

            except ValueError:
                self.console.print("[red]Invalid month format. Use YYYY-MM.[/red]")

    def select_time(self, times: List[TimeSlot]) -> str:
        """
        Prompt user to select time slot

        Args:
            times: List of available time slots

        Returns:
            Selected time in ISO format
        """
        self.console.print("\n[cyan]Available Times:[/cyan]\n")

        for i, slot in enumerate(times, 1):
            # Parse time and format nicely
            try:
                dt = datetime.fromisoformat(slot.time)
                time_str = dt.strftime('%I:%M %p')
                self.console.print(f"  {i}. {time_str}")
            except:
                self.console.print(f"  {i}. {slot.time}")

        while True:
            try:
                choice = input("\nSelect time (number): ").strip()
                index = int(choice) - 1

                if 0 <= index < len(times):
                    return times[index].time
                else:
                    self.console.print("[red]Invalid selection. Please try again.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")

    def _show_calendar(self, month_str: str, available_dates: List[AvailabilityDate]):
        """
        Display calendar with available dates highlighted

        Args:
            month_str: Month in YYYY-MM format
            available_dates: List of available dates
        """
        year, month = map(int, month_str.split('-'))

        # Create calendar
        cal = calendar.monthcalendar(year, month)

        # Get available date strings
        available_strs = set(d.date for d in available_dates)

        self.console.print(f"\n[cyan]Calendar for {month_str}[/cyan]\n")
        self.console.print("  Mon Tue Wed Thu Fri Sat Sun")

        for week in cal:
            week_str = ""
            for day in week:
                if day == 0:
                    week_str += "    "
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    if date_str in available_strs:
                        week_str += f"[green]{day:3d}[/green]"
                    else:
                        week_str += f"{day:3d} "

            self.console.print("  " + week_str)

        self.console.print("\n[green]Green dates have availability[/green]\n")

# ============================================================================
# Formatting
# ============================================================================

class AvailabilityFormatter:
    """Format availability data for display"""

    @staticmethod
    def format_time_table(times: List[TimeSlot], timezone: str = DEFAULT_TIMEZONE) -> Table:
        """
        Format times as table

        Args:
            times: List of available times
            timezone: Timezone for display

        Returns:
            Rich Table
        """
        table = Table(title="Available Times", border_style="cyan")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Time", style="green", width=15)
        table.add_column("Timezone", style="magenta", width=20)

        tz = pytz.timezone(timezone)

        for i, slot in enumerate(times, 1):
            try:
                dt = datetime.fromisoformat(slot.time)
                time_str = dt.strftime('%I:%M %p')
                tz_abbr = dt.strftime('%Z')
            except:
                time_str = slot.time
                tz_abbr = timezone

            table.add_row(
                str(i),
                time_str,
                tz_abbr
            )

        return table

    @staticmethod
    def format_availability_json(appointment_type_id: int, date_str: str,
                                 times: List[TimeSlot]) -> Dict:
        """
        Format availability as JSON

        Args:
            appointment_type_id: Appointment type ID
            date_str: Date in YYYY-MM-DD format
            times: List of available times

        Returns:
            JSON-serializable dictionary
        """
        return {
            'appointment_type_id': appointment_type_id,
            'date': date_str,
            'available_times': [
                {
                    'time': slot.time,
                    'time_formatted': datetime.fromisoformat(slot.time).strftime('%I:%M %p')
                    if slot.time else None
                }
                for slot in times
            ],
            'total_slots': len(times),
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Check appointment availability"
    )
    parser.add_argument(
        '--type-id',
        type=int,
        help='Appointment type ID (for quick mode)'
    )
    parser.add_argument(
        '--date',
        help='Date in YYYY-MM-DD format (for quick mode)'
    )
    parser.add_argument(
        '--month',
        help='Month in YYYY-MM format (to check dates)'
    )
    parser.add_argument(
        '--tz', '--timezone',
        default=DEFAULT_TIMEZONE,
        help=f'Timezone (default: {DEFAULT_TIMEZONE})'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Skip caching'
    )
    parser.add_argument(
        '--env',
        help='Path to .env file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

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
        client = AcuityClient(user_id, api_key)
        console = Console()
        ui = InteractiveUI(console)
        formatter = AvailabilityFormatter()

        # Check if quick mode or interactive mode
        if args.type_id and args.date:
            # Quick mode
            logger.info(f"Quick mode: type_id={args.type_id}, date={args.date}")

            try:
                times = client.get_available_times(
                    args.type_id,
                    args.date,
                    args.tz
                )

                if args.json:
                    output = formatter.format_availability_json(
                        args.type_id,
                        args.date,
                        times
                    )
                    console.print_json(data=output)
                else:
                    console.print(formatter.format_time_table(times, args.tz))

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return 1

        else:
            # Interactive mode
            console.print(Panel(
                "[bold cyan]Acuity Scheduling - Availability Checker[/bold cyan]",
                border_style="cyan"
            ))

            try:
                # Get appointment types
                types = client.get_appointment_types()

                # Select type
                type_id = ui.select_appointment_type(types)

                # Select date
                date_str = ui.select_date(type_id, client, args.tz)

                # Get available times
                times = client.get_available_times(type_id, date_str, args.tz)

                if not times:
                    console.print("[yellow]No available times on this date.[/yellow]")
                    return 1

                # Select time
                selected_time = ui.select_time(times)

                # Display confirmation
                console.print(Panel(
                    f"[green]Selected Time:[/green]\n"
                    f"Date: {date_str}\n"
                    f"Time: {datetime.fromisoformat(selected_time).strftime('%I:%M %p')}\n"
                    f"Timezone: {args.tz}",
                    title="[bold green]Appointment Time[/bold green]",
                    border_style="green"
                ))

            except KeyboardInterrupt:
                console.print("\n[yellow]Cancelled.[/yellow]")
                return 0
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.exception("Unexpected error")
                return 1

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

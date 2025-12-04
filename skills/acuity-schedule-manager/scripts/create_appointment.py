#!/usr/bin/env python3

"""
Acuity Scheduling API - Appointment Creator

Purpose:
    Create new appointments with validation and confirmation.
    Supports interactive guided mode and batch mode from JSON file.

Features:
    - Interactive guided mode: Step-by-step prompts
    - Batch mode: Read from JSON file
    - Real-time availability verification before creation
    - Pydantic validation for all inputs (email, phone, datetime)
    - Confirmation prompt before API call
    - Generate appointment receipt/confirmation
    - Handle custom fields

Usage:
    python3 create_appointment.py                         # Interactive mode
    python3 create_appointment.py --batch appointments.json
    python3 create_appointment.py --type-id 12345 --date 2025-11-15T14:00:00

Examples:
    # Interactive mode
    python3 create_appointment.py

    # Batch create from JSON
    python3 create_appointment.py --batch appointments.json

    # Specific appointment
    python3 create_appointment.py --type-id 12345 --date 2025-11-15T14:00:00 \\
        --first John --last Doe --email john@example.com --phone 555-0123

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
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
import pytz
from pydantic import BaseModel, validator, ValidationError, EmailStr

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

class AppointmentCreateRequest(BaseModel):
    """Appointment creation request with validation"""
    appointmentTypeID: int
    datetime: str
    firstName: str
    lastName: str
    email: EmailStr
    phone: str
    timezone: str = DEFAULT_TIMEZONE
    notes: Optional[str] = None
    fields: Optional[List[Dict]] = None

    @validator('firstName', 'lastName')
    def validate_name(cls, v):
        """Validate name fields"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        if len(v) > 100:
            raise ValueError('Name too long (max 100 characters)')
        return v.strip()

    @validator('email')
    def validate_email_format(cls, v):
        """Validate email format and reject disposable addresses"""
        try:
            validate_email(v)
        except EmailNotValidError as e:
            raise ValueError(f'Invalid email: {str(e)}')

        # Reject disposable email domains
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', 'throwaway.email', 'yopmail.com'
        ]

        domain = v.split('@')[1].lower()
        if domain in disposable_domains:
            raise ValueError(f'Disposable email addresses not allowed')

        return v.lower()

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number"""
        # Remove common formatting
        cleaned = re.sub(r'[\s\-\(\)\.+]', '', v)

        # Check length (min 10 digits for US, flexible for international)
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError(f'Phone must have 10-15 digits')

        # Check it contains only digits
        if not cleaned.isdigit():
            raise ValueError(f'Phone must contain only digits and formatting')

        return v.strip()

    @validator('datetime')
    def validate_datetime(cls, v):
        """Validate datetime is ISO format and in future"""
        try:
            dt = datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Datetime must be ISO format (e.g., 2025-11-15T14:00:00-0500)')

        # Check it's in future
        if dt <= datetime.now(dt.tzinfo or pytz.UTC):
            raise ValueError('Appointment must be in the future')

        return v

    @validator('timezone')
    def validate_timezone(cls, v):
        """Validate timezone"""
        try:
            pytz.timezone(v)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f'Unknown timezone: {v}')
        return v

class AppointmentResponse(BaseModel):
    """Appointment response from API"""
    id: int
    datetime: str
    firstName: str
    lastName: str
    email: str
    appointmentTypeID: int
    calendarID: int
    confirmed: bool
    price: Optional[str] = None

    class Config:
        extra = 'allow'

# ============================================================================
# API Client
# ============================================================================

class AcuityClient:
    """Acuity Scheduling API client"""

    def __init__(self, user_id: str, api_key: str):
        """Initialize API client"""
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

    def check_availability(self, appointment_type_id: int, date_str: str,
                          timezone: str = DEFAULT_TIMEZONE) -> List[Dict]:
        """
        Check if time slot is available

        Args:
            appointment_type_id: Appointment type ID
            date_str: Date in YYYY-MM-DD format
            timezone: Timezone

        Returns:
            List of available times
        """
        logger.info(f"Checking availability for {date_str}")

        params = {
            'appointmentTypeID': appointment_type_id,
            'date': date_str.split('T')[0],  # Extract date from datetime
            'timezone': timezone
        }

        try:
            response = self.session.get(
                f"{API_BASE_URL}/availability/times",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            times = response.json()
            logger.info(f"Found {len(times)} available times")

            return times

        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            raise

    def create_appointment(self, appointment_data: AppointmentCreateRequest) -> AppointmentResponse:
        """
        Create appointment in Acuity

        Args:
            appointment_data: Validated appointment data

        Returns:
            Created appointment
        """
        logger.info(f"Creating appointment for {appointment_data.email}")

        data = {
            'appointmentTypeID': appointment_data.appointmentTypeID,
            'datetime': appointment_data.datetime,
            'firstName': appointment_data.firstName,
            'lastName': appointment_data.lastName,
            'email': appointment_data.email,
            'phone': appointment_data.phone
        }

        if appointment_data.notes:
            data['notes'] = appointment_data.notes

        if appointment_data.fields:
            data['fields'] = appointment_data.fields

        try:
            response = self.session.post(
                f"{API_BASE_URL}/appointments",
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Appointment created: ID {result.get('id')}")
                return AppointmentResponse(**result)
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('message', response.text)
                raise Exception(f"API error {response.status_code}: {error_msg}")

        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            raise

# ============================================================================
# Interactive UI
# ============================================================================

class AppointmentCreatorUI:
    """Interactive appointment creation UI"""

    def __init__(self, client: AcuityClient, console: Console = None):
        """Initialize UI"""
        self.client = client
        self.console = console or Console()

    def get_appointment_type_id(self) -> int:
        """
        Prompt for appointment type

        Returns:
            Appointment type ID
        """
        try:
            response = self.client.session.get(
                f"{API_BASE_URL}/appointment-types",
                timeout=10
            )
            response.raise_for_status()

            types = response.json()

            self.console.print("[cyan]Available Appointment Types:[/cyan]\n")

            for i, apt_type in enumerate(types, 1):
                price = f" - ${apt_type.get('price', '')}" if apt_type.get('price') else ""
                duration = f" ({apt_type.get('duration', '')}min)" if apt_type.get('duration') else ""
                self.console.print(f"  {i}. {apt_type.get('name')}{duration}{price}")

            while True:
                try:
                    choice = input("\nSelect appointment type (number): ").strip()
                    index = int(choice) - 1

                    if 0 <= index < len(types):
                        return types[index]['id']
                    else:
                        self.console.print("[red]Invalid selection.[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a valid number.[/red]")

        except Exception as e:
            self.console.print(f"[red]Error loading appointment types: {e}[/red]")
            raise

    def get_appointment_details(self) -> Dict:
        """
        Prompt for appointment details

        Returns:
            Dictionary with appointment details
        """
        data = {}

        # Appointment type
        data['appointmentTypeID'] = self.get_appointment_type_id()

        # Date and time
        while True:
            datetime_str = input("\nEnter appointment datetime (YYYY-MM-DDTHH:MM:SS±HH:MM): ").strip()
            try:
                dt = datetime.fromisoformat(datetime_str)
                data['datetime'] = datetime_str
                break
            except ValueError:
                self.console.print("[red]Invalid format. Use: 2025-11-15T14:00:00-0500[/red]")

        # Check availability
        self.console.print("\n[cyan]Checking availability...[/cyan]")
        try:
            available_times = self.client.check_availability(
                data['appointmentTypeID'],
                data['datetime']
            )

            # Check if requested time is available
            available_time_strs = [t.get('time') for t in available_times]
            if data['datetime'] not in available_time_strs:
                self.console.print(
                    "[yellow]⚠  Warning: Requested time may not be available.[/yellow]"
                )
                if not input("Continue anyway? (y/n): ").lower().startswith('y'):
                    return self.get_appointment_details()

        except Exception as e:
            self.console.print(f"[yellow]Could not verify availability: {e}[/yellow]")

        # Personal information
        data['firstName'] = input("\nFirst name: ").strip()
        data['lastName'] = input("Last name: ").strip()
        data['email'] = input("Email address: ").strip()
        data['phone'] = input("Phone number: ").strip()

        # Optional fields
        timezone = input("Timezone (default: America/New_York): ").strip()
        if timezone:
            data['timezone'] = timezone

        notes = input("Notes (optional): ").strip()
        if notes:
            data['notes'] = notes

        return data

    def confirm_appointment(self, data: Dict) -> bool:
        """
        Show confirmation prompt

        Args:
            data: Appointment data

        Returns:
            True if user confirms
        """
        table = Table(title="Appointment Details", border_style="cyan")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", f"{data.get('firstName')} {data.get('lastName')}")
        table.add_row("Email", data.get('email'))
        table.add_row("Phone", data.get('phone'))
        table.add_row("Datetime", data.get('datetime'))
        table.add_row("Timezone", data.get('timezone', DEFAULT_TIMEZONE))

        self.console.print(table)
        self.console.print()

        confirm = input("Create appointment? (y/n): ").lower().startswith('y')
        return confirm

# ============================================================================
# Formatter
# ============================================================================

class ReceiptFormatter:
    """Format appointment confirmation receipt"""

    @staticmethod
    def print_receipt(appointment: AppointmentResponse, console: Console = None):
        """
        Print appointment receipt

        Args:
            appointment: Created appointment
            console: Rich console
        """
        console = console or Console()

        receipt_text = (
            f"[green]✓ Appointment Created Successfully![/green]\n\n"
            f"[bold]Appointment ID:[/bold] {appointment.id}\n"
            f"[bold]Name:[/bold] {appointment.firstName} {appointment.lastName}\n"
            f"[bold]Email:[/bold] {appointment.email}\n"
            f"[bold]Date & Time:[/bold] {appointment.datetime}\n"
        )

        if appointment.price:
            receipt_text += f"[bold]Price:[/bold] ${appointment.price}\n"

        receipt_text += f"[bold]Status:[/bold] {'Confirmed' if appointment.confirmed else 'Pending'}"

        console.print(Panel(
            receipt_text,
            title="[bold green]Appointment Confirmation[/bold green]",
            border_style="green"
        ))

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Create new appointment in Acuity Scheduling"
    )
    parser.add_argument(
        '--type-id',
        type=int,
        help='Appointment type ID'
    )
    parser.add_argument(
        '--date',
        help='Date in YYYY-MM-DDTHH:MM:SS±HH:MM format'
    )
    parser.add_argument(
        '--first',
        help='First name'
    )
    parser.add_argument(
        '--last',
        help='Last name'
    )
    parser.add_argument(
        '--email',
        help='Email address'
    )
    parser.add_argument(
        '--phone',
        help='Phone number'
    )
    parser.add_argument(
        '--batch',
        help='Path to JSON file with batch appointments'
    )
    parser.add_argument(
        '--tz', '--timezone',
        default=DEFAULT_TIMEZONE,
        help=f'Timezone (default: {DEFAULT_TIMEZONE})'
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

        # Batch mode
        if args.batch:
            logger.info(f"Batch mode: {args.batch}")

            try:
                with open(args.batch, 'r') as f:
                    batch_data = json.load(f)

                if not isinstance(batch_data, list):
                    batch_data = [batch_data]

                results = {'success': [], 'failed': []}

                for i, apt_data in enumerate(batch_data, 1):
                    try:
                        apt_request = AppointmentCreateRequest(**apt_data)
                        apt = client.create_appointment(apt_request)
                        results['success'].append({
                            'index': i,
                            'id': apt.id,
                            'email': apt.email
                        })
                        console.print(f"[green]✓ Appointment {i} created (ID: {apt.id})[/green]")

                    except ValidationError as e:
                        results['failed'].append({
                            'index': i,
                            'errors': e.errors()
                        })
                        console.print(f"[red]✗ Appointment {i} validation failed[/red]")

                    except Exception as e:
                        results['failed'].append({
                            'index': i,
                            'error': str(e)
                        })
                        console.print(f"[red]✗ Appointment {i} creation failed: {e}[/red]")

                # Summary
                console.print(Panel(
                    f"[green]Success: {len(results['success'])}[/green]\n"
                    f"[red]Failed: {len(results['failed'])}[/red]",
                    title="Batch Results"
                ))

                return 0 if len(results['failed']) == 0 else 1

            except Exception as e:
                console.print(f"[red]Error reading batch file: {e}[/red]")
                return 1

        # Quick mode (all args provided)
        elif all([args.type_id, args.date, args.first, args.last,
                  args.email, args.phone]):
            logger.info("Quick mode")

            try:
                apt_data = AppointmentCreateRequest(
                    appointmentTypeID=args.type_id,
                    datetime=args.date,
                    firstName=args.first,
                    lastName=args.last,
                    email=args.email,
                    phone=args.phone,
                    timezone=args.tz
                )

                apt = client.create_appointment(apt_data)
                ReceiptFormatter.print_receipt(apt, console)
                return 0

            except ValidationError as e:
                console.print("[red]Validation failed:[/red]")
                for error in e.errors():
                    console.print(f"  - {error}")
                return 1

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return 1

        # Interactive mode
        else:
            console.print(Panel(
                "[bold cyan]Acuity Scheduling - Create Appointment[/bold cyan]",
                border_style="cyan"
            ))

            try:
                ui = AppointmentCreatorUI(client, console)

                # Get details
                apt_data = ui.get_appointment_details()

                # Confirm
                if not ui.confirm_appointment(apt_data):
                    console.print("[yellow]Cancelled.[/yellow]")
                    return 0

                # Create
                console.print("\n[cyan]Creating appointment...[/cyan]")
                apt_request = AppointmentCreateRequest(**apt_data)
                apt = client.create_appointment(apt_request)

                # Display receipt
                ReceiptFormatter.print_receipt(apt, console)

                return 0

            except ValidationError as e:
                console.print("[red]Validation failed:[/red]")
                for error in e.errors():
                    console.print(f"  - {error}")
                return 1

            except KeyboardInterrupt:
                console.print("\n[yellow]Cancelled.[/yellow]")
                return 0

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.exception("Unexpected error")
                return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

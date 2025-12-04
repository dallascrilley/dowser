#!/usr/bin/env python3

"""
Acuity Scheduling API - Webhook Tester

Purpose:
    Generate sample webhook payloads, create HMAC signatures, and test
    webhook delivery to local or remote endpoints.

Features:
    - Generate sample webhook payloads for all event types
    - HMAC signature generation for testing
    - Send test payload to local or remote endpoint
    - Verify endpoint response and timing
    - Test signature validation
    - Support multiple event types via CLI args

Usage:
    python3 test_webhook.py --endpoint http://localhost:5000/webhooks/acuity
    python3 test_webhook.py --endpoint https://api.example.com/webhooks/acuity --event scheduled
    python3 test_webhook.py --generate-only                  # Just generate payload
    python3 test_webhook.py --event appointment.rescheduled

Examples:
    # Test local webhook endpoint
    python3 test_webhook.py --endpoint http://localhost:5000/webhooks/acuity

    # Test with specific event type
    python3 test_webhook.py --endpoint https://api.example.com/webhooks \\
        --event appointment.canceled

    # Generate payload without sending
    python3 test_webhook.py --generate-only --event appointment.scheduled

Requirements:
    - requests
    - python-dotenv
    - rich
    - pydantic
"""

import os
import sys
import json
import hmac
import hashlib
import logging
import argparse
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pydantic import BaseModel

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_WEBHOOK_SECRET = "test_webhook_secret"

EVENT_TYPES = {
    'scheduled': 'appointment.scheduled',
    'rescheduled': 'appointment.rescheduled',
    'canceled': 'appointment.canceled',
    'changed': 'appointment.changed',
    'order_completed': 'order.completed'
}

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

class WebhookPayload(BaseModel):
    """Webhook payload structure"""
    id: int
    action: str
    appointmentTypeID: Optional[int] = None
    datetime: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    calendarID: Optional[int] = None
    timezone: Optional[str] = None
    confirmationPage: Optional[str] = None
    notes: Optional[str] = None
    canceled: Optional[bool] = None

    class Config:
        extra = 'allow'

# ============================================================================
# Payload Generator
# ============================================================================

class WebhookPayloadGenerator:
    """Generate test webhook payloads"""

    @staticmethod
    def generate_appointment_scheduled() -> Dict:
        """Generate appointment.scheduled payload"""
        appointment_datetime = (datetime.now() + timedelta(days=7)).isoformat()

        return {
            'id': 123456789,
            'action': 'scheduled',
            'appointmentTypeID': 12345,
            'datetime': appointment_datetime,
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test@example.com',
            'phone': '+1-555-0123',
            'calendarID': 67890,
            'timezone': 'America/New_York',
            'confirmationPage': 'https://example.com/confirm/123456789',
            'notes': 'Test appointment scheduled',
            'canceled': False
        }

    @staticmethod
    def generate_appointment_rescheduled() -> Dict:
        """Generate appointment.rescheduled payload"""
        appointment_datetime = (datetime.now() + timedelta(days=14)).isoformat()

        return {
            'id': 123456789,
            'action': 'rescheduled',
            'appointmentTypeID': 12345,
            'datetime': appointment_datetime,
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test@example.com',
            'phone': '+1-555-0123',
            'calendarID': 67890,
            'notes': 'Appointment rescheduled by client',
            'canceled': False
        }

    @staticmethod
    def generate_appointment_canceled() -> Dict:
        """Generate appointment.canceled payload"""
        return {
            'id': 123456789,
            'action': 'canceled',
            'appointmentTypeID': 12345,
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test@example.com',
            'phone': '+1-555-0123',
            'calendarID': 67890,
            'notes': 'Appointment canceled by client',
            'canceled': True,
            'dateCanceled': datetime.now().isoformat()
        }

    @staticmethod
    def generate_order_completed() -> Dict:
        """Generate order.completed payload"""
        return {
            'id': 987654321,
            'action': 'completed',
            'email': 'test@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'phone': '+1-555-0123',
            'total': '99.99',
            'lineItems': [
                {
                    'id': 111,
                    'productName': 'Service Package',
                    'quantity': 1,
                    'price': '99.99'
                }
            ]
        }

    @classmethod
    def generate(cls, event_type: str) -> Dict:
        """
        Generate payload for event type

        Args:
            event_type: Event type (scheduled, rescheduled, canceled, etc.)

        Returns:
            Event payload dictionary
        """
        if event_type == 'scheduled' or event_type == 'appointment.scheduled':
            return cls.generate_appointment_scheduled()
        elif event_type == 'rescheduled' or event_type == 'appointment.rescheduled':
            return cls.generate_appointment_rescheduled()
        elif event_type == 'canceled' or event_type == 'appointment.canceled':
            return cls.generate_appointment_canceled()
        elif event_type == 'changed' or event_type == 'appointment.changed':
            return cls.generate_appointment_scheduled()
        elif event_type == 'order_completed' or event_type == 'order.completed':
            return cls.generate_order_completed()
        else:
            raise ValueError(f"Unknown event type: {event_type}")

# ============================================================================
# Signature Handler
# ============================================================================

class SignatureHandler:
    """Handle webhook signature generation and verification"""

    @staticmethod
    def generate_signature(payload_json: str, secret: str) -> str:
        """
        Generate HMAC signature for webhook

        Args:
            payload_json: JSON payload string
            secret: Webhook secret (API key)

        Returns:
            Hex-encoded signature
        """
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    @staticmethod
    def verify_signature(payload_json: str, signature: str, secret: str) -> bool:
        """
        Verify webhook signature

        Args:
            payload_json: JSON payload string
            signature: Signature from header
            secret: Webhook secret

        Returns:
            True if signature is valid
        """
        expected_signature = SignatureHandler.generate_signature(payload_json, secret)
        return hmac.compare_digest(signature, expected_signature)

# ============================================================================
# Webhook Tester
# ============================================================================

class WebhookTester:
    """Test webhook delivery"""

    def __init__(self, console: Console = None):
        """Initialize tester"""
        self.console = console or Console()

    def send_webhook(self, endpoint: str, payload: Dict,
                    secret: Optional[str] = None) -> Tuple[bool, Dict]:
        """
        Send webhook to endpoint

        Args:
            endpoint: Webhook endpoint URL
            payload: Webhook payload
            secret: Secret for signature (optional)

        Returns:
            Tuple of (success, result_info)
        """
        logger.info(f"Sending webhook to {endpoint}")

        # Convert payload to JSON
        payload_json = json.dumps(payload)

        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'AcuityScheduleManager/1.0'
        }

        # Add signature if secret provided
        if secret:
            signature = SignatureHandler.generate_signature(payload_json, secret)
            headers['X-Acuity-Signature'] = signature
            logger.info(f"Generated signature: {signature}")

        result = {
            'endpoint': endpoint,
            'status_code': None,
            'response_time_ms': None,
            'response_body': None,
            'error': None,
            'success': False
        }

        try:
            start_time = time.time()

            response = requests.post(
                endpoint,
                data=payload_json,
                headers=headers,
                timeout=10
            )

            elapsed_ms = (time.time() - start_time) * 1000

            result['status_code'] = response.status_code
            result['response_time_ms'] = elapsed_ms
            result['response_body'] = response.text[:500]  # First 500 chars

            if response.status_code < 400:
                result['success'] = True
                logger.info(f"Webhook delivered successfully ({response.status_code})")
            else:
                logger.error(f"Webhook delivery failed ({response.status_code})")
                result['error'] = response.text

        except requests.exceptions.Timeout:
            result['error'] = 'Request timeout'
            logger.error("Webhook request timed out")

        except requests.exceptions.ConnectionError as e:
            result['error'] = f'Connection error: {str(e)}'
            logger.error(f"Cannot connect to endpoint: {e}")

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error sending webhook: {e}")

        return result['success'], result

    def display_payload(self, payload: Dict):
        """Display payload"""
        self.console.print(Panel(
            f"[bold cyan]Webhook Payload[/bold cyan]\n\n"
            f"[code]{json.dumps(payload, indent=2)}[/code]",
            border_style="cyan"
        ))

    def display_signature(self, payload_json: str, secret: str):
        """Display signature"""
        signature = SignatureHandler.generate_signature(payload_json, secret)

        self.console.print(Panel(
            f"[bold cyan]Signature Information[/bold cyan]\n\n"
            f"[bold]Secret:[/bold] {secret}\n"
            f"[bold]Signature:[/bold] {signature}\n"
            f"[bold]Header:[/bold] X-Acuity-Signature: {signature}",
            border_style="cyan"
        ))

    def display_result(self, result: Dict):
        """Display delivery result"""
        if result['success']:
            status = "[green]✓ SUCCESS[/green]"
            border = "green"
        else:
            status = "[red]✗ FAILED[/red]"
            border = "red"

        result_text = (
            f"[bold]{status}[/bold]\n\n"
            f"[bold]Endpoint:[/bold] {result['endpoint']}\n"
            f"[bold]Status Code:[/bold] {result['status_code']}\n"
            f"[bold]Response Time:[/bold] {result['response_time_ms']:.1f}ms\n"
        )

        if result['response_body']:
            result_text += f"[bold]Response:[/bold] {result['response_body']}\n"

        if result['error']:
            result_text += f"[bold red]Error:[/bold red] {result['error']}"

        self.console.print(Panel(
            result_text,
            title="[bold]Delivery Result[/bold]",
            border_style=border
        ))

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Test Acuity Scheduling webhooks"
    )
    parser.add_argument(
        '--endpoint',
        help='Webhook endpoint URL'
    )
    parser.add_argument(
        '--event',
        default='scheduled',
        help='Event type (scheduled, rescheduled, canceled, order_completed)'
    )
    parser.add_argument(
        '--secret',
        help='Webhook secret (API key for signature)'
    )
    parser.add_argument(
        '--generate-only',
        action='store_true',
        help='Only generate payload, don\'t send'
    )
    parser.add_argument(
        '--signature-only',
        action='store_true',
        help='Only generate signature'
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

    # Load credentials if secret not provided
    if not args.secret:
        if args.env:
            load_dotenv(args.env)
        else:
            load_dotenv()

        args.secret = os.getenv('ACUITY_API_KEY') or DEFAULT_WEBHOOK_SECRET

    try:
        console = Console()
        generator = WebhookPayloadGenerator()
        tester = WebhookTester(console)

        console.print(Panel(
            "[bold cyan]Acuity Scheduling - Webhook Tester[/bold cyan]",
            border_style="cyan"
        ))

        # Generate payload
        payload = generator.generate(args.event)
        payload_json = json.dumps(payload)

        logger.info(f"Generated payload for event: {args.event}")

        # Display payload
        tester.display_payload(payload)

        # Display signature
        tester.display_signature(payload_json, args.secret)

        # Send if endpoint provided and not generate-only
        if args.endpoint and not args.generate_only:
            console.print()
            success, result = tester.send_webhook(args.endpoint, payload, args.secret)
            tester.display_result(result)

            return 0 if success else 1

        return 0

    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Unexpected error")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///

"""
Send PandaDoc documents to recipients with customizable messages.

This script sends documents to recipients with status verification, recipient
validation, and delivery confirmation.

Usage:
    # Send with default message
    uv run send_document.py --document-id "abc123"

    # Send with custom subject and message
    uv run send_document.py \\
        --document-id "abc123" \\
        --subject "Proposal for Review" \\
        --message "Please review and sign by Friday"

    # Send silently (no email notification)
    uv run send_document.py \\
        --document-id "abc123" \\
        --silent
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load .env file from project root
def load_env_file():
    """Load environment variables from .env file at project root."""
    # Get project root (one level up from scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)

# Load .env before reading environment variables
load_env_file()

# Configuration
BASE_URL = os.environ.get("PANDADOC_BASE_URL", "https://api.pandadoc.com/public/v1")
API_KEY = os.environ.get("PANDADOC_API_KEY", "")
RATE_LIMIT_DELAY = 6  # seconds (for 10 req/min limit)

# Set up logging
logger = logging.getLogger(__name__)


class PandaDocException(Exception):
    """Base exception for PandaDoc API errors."""
    pass


class AuthenticationError(PandaDocException):
    """Raised when authentication fails."""
    pass


class DocumentNotFoundError(PandaDocException):
    """Raised when document is not found."""
    pass


class InvalidDocumentStatusError(PandaDocException):
    """Raised when document is not in valid state for sending."""
    pass


class SendError(PandaDocException):
    """Raised when document send fails."""
    pass


class RateLimiter:
    """Implements rate limiting for API requests."""

    def __init__(self, requests_per_minute: int = 10):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.request_times: List[float] = []

    def wait_if_needed(self) -> None:
        """Wait if rate limit is reached."""
        now = time.time()
        minute_ago = now - 60

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if t > minute_ago]

        # Check if limit reached
        if len(self.request_times) >= self.requests_per_minute:
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest) + 1
            logger.warning(
                f"Rate limit reached. Waiting {wait_time:.1f} seconds..."
            )
            time.sleep(wait_time)

        # Record this request
        self.request_times.append(now)


rate_limiter = RateLimiter()


def configure_logging(verbose: bool = False) -> None:
    """Configure logging level.

    Args:
        verbose: If True, set to DEBUG level; otherwise INFO
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def validate_api_key() -> None:
    """Validate API key is configured.

    Raises:
        AuthenticationError: If API key is not set
    """
    if not API_KEY:
        raise AuthenticationError(
            "PANDADOC_API_KEY environment variable not set. "
            "Please set your API key before running this script."
        )
    logger.debug("API key validated")


def get_headers() -> Dict[str, str]:
    """Get HTTP headers for API requests.

    Returns:
        Dictionary of headers
    """
    return {
        "Authorization": f"API-Key {API_KEY}",
        "Content-Type": "application/json"
    }


def get_document_status(document_id: str) -> Dict[str, Any]:
    """Get document status information.

    Args:
        document_id: Document ID

    Returns:
        Document data dictionary

    Raises:
        DocumentNotFoundError: If document not found
        AuthenticationError: If authentication fails
    """
    rate_limiter.wait_if_needed()

    logger.debug(f"Fetching document status for {document_id}")
    url = f"{BASE_URL}/documents/{document_id}"
    headers = get_headers()

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif e.response.status_code == 404:
            raise DocumentNotFoundError(f"Document not found: {document_id}")
        else:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise
    except requests.exceptions.RequestException as e:
        raise PandaDocException(f"Request failed: {e}")

    return response.json()


def validate_document_for_sending(document_id: str) -> Dict[str, Any]:
    """Validate document is ready to send.

    Args:
        document_id: Document ID

    Returns:
        Document data dictionary

    Raises:
        InvalidDocumentStatusError: If document not in draft status
    """
    logger.info(f"Validating document {document_id}")
    doc = get_document_status(document_id)

    status = doc.get("status")
    logger.debug(f"Document status: {status}")

    # Check if document is in draft status
    if status != "document.draft":
        raise InvalidDocumentStatusError(
            f"Document is not ready to send. "
            f"Current status: {status}. "
            f"Expected: document.draft"
        )

    # Validate recipients
    recipients = doc.get("recipients", [])
    if not recipients:
        raise InvalidDocumentStatusError("Document has no recipients")

    logger.info(f"Document is ready. Recipients: {len(recipients)}")
    for i, recipient in enumerate(recipients, 1):
        email = recipient.get("email")
        role = recipient.get("role", "Unknown")
        logger.info(f"  {i}. {email} ({role})")

    return doc


def send_document(
    document_id: str,
    subject: Optional[str] = None,
    message: Optional[str] = None,
    silent: bool = False
) -> Dict[str, Any]:
    """Send document to recipients.

    Args:
        document_id: Document ID
        subject: Email subject
        message: Email message body
        silent: If True, don't send email notifications

    Returns:
        Response data

    Raises:
        SendError: If send fails
    """
    rate_limiter.wait_if_needed()

    # Use default subject/message if not provided
    if not subject:
        subject = "Document for Review and Signature"
    if not message:
        message = "Please review the attached document and sign if you agree to the terms."

    logger.info(f"Sending document {document_id}")
    logger.debug(f"Subject: {subject}")
    logger.debug(f"Message: {message}")

    url = f"{BASE_URL}/documents/{document_id}/send"
    headers = get_headers()

    payload = {
        "subject": subject,
        "message": message,
        "silent": silent,
        "forwarding_settings": {
            "forwarding_allowed": True
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif e.response.status_code == 404:
            raise DocumentNotFoundError(f"Document not found: {document_id}")
        elif e.response.status_code == 409:
            raise InvalidDocumentStatusError(
                f"Document cannot be sent in its current state. "
                f"Error: {e.response.text}"
            )
        else:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise SendError(f"Failed to send document: {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise SendError(f"Request failed: {e}")

    data = response.json()
    logger.info(f"Document sent successfully")
    logger.debug(f"Response: {json.dumps(data, indent=2)}")

    return data


def format_recipients(doc: Dict[str, Any]) -> str:
    """Format recipient information for display.

    Args:
        doc: Document data

    Returns:
        Formatted recipient string
    """
    recipients = doc.get("recipients", [])
    lines = ["Recipients:"]
    for i, recipient in enumerate(recipients, 1):
        email = recipient.get("email")
        role = recipient.get("role", "Unknown")
        status = recipient.get("recipient_status", "pending")
        lines.append(f"  {i}. {email} ({role}) - {status}")
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Send PandaDoc documents to recipients",
        epilog="""
Examples:
  # Send with default message
  python send_document.py --document-id "abc123"

  # Send with custom subject and message
  python send_document.py \\
    --document-id "abc123" \\
    --subject "Proposal for Review" \\
    --message "Please review and sign by Friday"

  # Send silently (no email)
  python send_document.py \\
    --document-id "abc123" \\
    --silent

  # With verbose logging
  python send_document.py \\
    --document-id "abc123" \\
    -v
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--document-id",
        required=True,
        help="Document ID to send"
    )
    parser.add_argument(
        "--subject",
        help="Email subject line (default: 'Document for Review and Signature')"
    )
    parser.add_argument(
        "--message",
        help="Email message body"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Don't send email notifications"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = parse_arguments()
    configure_logging(args.verbose)

    try:
        # Validate API key
        validate_api_key()

        # Validate document is ready to send
        doc = validate_document_for_sending(args.document_id)

        # Send document
        result = send_document(
            args.document_id,
            subject=args.subject,
            message=args.message,
            silent=args.silent
        )

        # Display success information
        print(f"SUCCESS: Document sent")
        print(f"Document ID: {args.document_id}")
        print(f"Status: {result.get('status')}")
        print()
        print(format_recipients(result))

        return 0

    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        return 1
    except (
        AuthenticationError,
        DocumentNotFoundError,
        InvalidDocumentStatusError,
        SendError,
        PandaDocException
    ) as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

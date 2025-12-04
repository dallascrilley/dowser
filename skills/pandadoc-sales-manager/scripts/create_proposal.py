#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///

"""
Create PandaDoc proposals from templates with field mapping and status polling.

This script creates sales proposals from PandaDoc templates with automatic field
validation, status polling, rate limit handling, and progress display.

Usage:
    # Create from command-line arguments
    uv run create_proposal.py \\
        --template "Sales Proposal" \\
        --customer-name "Acme Corp" \\
        --customer-email "client@acme.com" \\
        --amount "50000" \\
        --effective-date "2024-01-15"

    # Create from JSON file
    uv run create_proposal.py \\
        --template "Sales Proposal" \\
        --data customer.json

    # Create with verbose logging
    uv run create_proposal.py \\
        --template "Sales Proposal" \\
        --customer-name "Acme Corp" \\
        --customer-email "client@acme.com" \\
        -v
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
POLL_INTERVAL = 2  # seconds
POLL_TIMEOUT = 60  # seconds
RATE_LIMIT_DELAY = 6  # seconds (for 10 req/min limit)

# Set up logging
logger = logging.getLogger(__name__)


class PandaDocException(Exception):
    """Base exception for PandaDoc API errors."""
    pass


class AuthenticationError(PandaDocException):
    """Raised when authentication fails."""
    pass


class TemplateNotFoundError(PandaDocException):
    """Raised when template is not found."""
    pass


class DocumentCreationError(PandaDocException):
    """Raised when document creation fails."""
    pass


class StatusPollingError(PandaDocException):
    """Raised when status polling times out."""
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


def load_template_mappings(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load template mappings from configuration file.

    Args:
        config_path: Path to template mappings file

    Returns:
        Dictionary of template mappings
    """
    if not config_path:
        # Try default locations
        candidates = [
            Path.home() / ".claude/skills/pandadoc-sales-manager/config/template_mappings.json",
            Path.home() / ".claude/skills/pandadoc-sales-manager/config/template_mappings.yml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = candidate
                break

    if config_path and Path(config_path).exists():
        logger.debug(f"Loading template mappings from {config_path}")
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.json'):
                    return json.load(f)
                else:
                    # Simple YAML support (basic)
                    import yaml
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load template mappings: {e}")

    return {}


def validate_customer_data(
    data: Dict[str, Any],
    required_fields: Optional[List[str]] = None
) -> None:
    """Validate customer data has required fields.

    Args:
        data: Customer data dictionary
        required_fields: List of required field names

    Raises:
        ValueError: If required fields are missing or empty
    """
    if not required_fields:
        required_fields = ["customer_email"]

    missing = []
    empty = []

    for field in required_fields:
        if field not in data:
            missing.append(field)
        elif not data[field]:
            empty.append(field)

    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    if empty:
        raise ValueError(f"Empty required fields: {', '.join(empty)}")

    # Validate email format
    if "customer_email" in data:
        email = data.get("customer_email", "")
        if "@" not in email or "." not in email:
            raise ValueError(f"Invalid email format: {email}")

    logger.debug("Customer data validation passed")


def create_document_request(
    template_uuid: str,
    customer_data: Dict[str, Any],
    template_mappings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build document creation request.

    Args:
        template_uuid: Template UUID
        customer_data: Customer information
        template_mappings: Optional template field mappings

    Returns:
        Request payload dictionary
    """
    # Build recipients list
    recipients = [
        {
            "email": customer_data.get("customer_email"),
            "first_name": customer_data.get("customer_name", "").split()[0] if customer_data.get("customer_name") else "",
            "last_name": customer_data.get("customer_name", "").split()[-1] if customer_data.get("customer_name") else "",
            "role": "Client"
        }
    ]

    # Build fields dictionary
    fields = {}
    if template_mappings and "field_mappings" in template_mappings:
        mappings = template_mappings["field_mappings"]
        for data_field, doc_field in mappings.items():
            if data_field in customer_data:
                fields[doc_field] = str(customer_data[data_field])
    else:
        # Default field mapping
        field_map = {
            "customer_name": "Company Name",
            "amount": "Proposal Amount",
            "effective_date": "Effective Date",
            "discount_percent": "Discount Percentage",
        }
        for data_field, doc_field in field_map.items():
            if data_field in customer_data:
                fields[doc_field] = str(customer_data[data_field])

    # Build tokens
    tokens = []
    if "sales_rep_name" in customer_data:
        tokens.append({
            "name": "SalesRep.Name",
            "value": customer_data["sales_rep_name"]
        })

    # Build metadata
    metadata = {}
    if "opportunity_id" in customer_data:
        metadata["opportunity_id"] = customer_data["opportunity_id"]

    # Build request
    request = {
        "name": f"Proposal - {customer_data.get('customer_name', 'Unknown')}",
        "template_uuid": template_uuid,
        "recipients": recipients,
        "fields": fields,
    }

    if tokens:
        request["tokens"] = tokens
    if metadata:
        request["metadata"] = metadata

    logger.debug(f"Created document request: {json.dumps(request, indent=2)}")
    return request


def create_document(request: Dict[str, Any]) -> str:
    """Create document via API.

    Args:
        request: Document creation request

    Returns:
        Document ID

    Raises:
        DocumentCreationError: If creation fails
    """
    rate_limiter.wait_if_needed()

    logger.info(f"Creating document: {request['name']}")
    url = f"{BASE_URL}/documents"
    headers = get_headers()

    try:
        response = requests.post(url, json=request, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif e.response.status_code == 404:
            raise TemplateNotFoundError(f"Template not found: {request['template_uuid']}")
        else:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise DocumentCreationError(f"Failed to create document: {e}")
    except requests.exceptions.RequestException as e:
        raise DocumentCreationError(f"Request failed: {e}")

    data = response.json()
    document_id = data.get("id")
    logger.info(f"Document created: {document_id} (status: {data.get('status')})")
    return document_id


def wait_for_draft_status(document_id: str, timeout: int = POLL_TIMEOUT) -> str:
    """Poll until document reaches draft status.

    Args:
        document_id: Document ID
        timeout: Timeout in seconds

    Returns:
        Final status

    Raises:
        StatusPollingError: If polling times out
    """
    logger.info(f"Polling for document ready status (max {timeout}s)...")
    headers = get_headers()
    url = f"{BASE_URL}/documents/{document_id}"
    start_time = time.time()
    poll_count = 0

    while True:
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise StatusPollingError(
                f"Document not ready after {timeout} seconds. "
                "This may be a server issue. Please check manually."
            )

        # Wait before polling
        time.sleep(POLL_INTERVAL)
        poll_count += 1

        rate_limiter.wait_if_needed()

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Poll attempt {poll_count} failed: {e}. Retrying...")
            continue

        data = response.json()
        status = data.get("status")
        logger.debug(f"Poll {poll_count}: {status} (elapsed: {elapsed:.1f}s)")

        # Check for ready status
        if status == "document.draft":
            logger.info(f"Document ready after {elapsed:.1f}s ({poll_count} polls)")
            return status

        # Check for error
        if status and status.startswith("document.error"):
            raise DocumentCreationError(f"Document creation error: {status}")

    return status


def load_customer_data_from_file(file_path: str) -> Dict[str, Any]:
    """Load customer data from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Customer data dictionary
    """
    logger.info(f"Loading customer data from {file_path}")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.debug(f"Loaded customer data: {data}")
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Could not load customer data from {file_path}: {e}")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Create PandaDoc proposals from templates",
        epilog="""
Examples:
  # Create from command-line arguments
  python create_proposal.py \\
    --template "Sales Proposal" \\
    --customer-name "Acme Corp" \\
    --customer-email "client@acme.com" \\
    --amount "50000" \\
    --effective-date "2024-01-15"

  # Create from JSON file
  python create_proposal.py \\
    --template "Sales Proposal" \\
    --data customer.json

  # With verbose logging
  python create_proposal.py \\
    --template "Sales Proposal" \\
    --customer-name "Acme Corp" \\
    --customer-email "client@acme.com" \\
    -v
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--template",
        required=True,
        help="Template name or UUID"
    )
    parser.add_argument(
        "--template-uuid",
        help="Explicit template UUID (overrides template name lookup)"
    )
    parser.add_argument(
        "--customer-name",
        help="Customer/company name"
    )
    parser.add_argument(
        "--customer-email",
        help="Customer email address"
    )
    parser.add_argument(
        "--amount",
        help="Proposal amount"
    )
    parser.add_argument(
        "--effective-date",
        help="Effective date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--discount-percent",
        help="Discount percentage"
    )
    parser.add_argument(
        "--data",
        help="Load customer data from JSON file"
    )
    parser.add_argument(
        "--opportunity-id",
        help="Opportunity ID for tracking"
    )
    parser.add_argument(
        "--sales-rep-name",
        help="Sales representative name"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--config",
        help="Path to template mappings configuration file"
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

        # Load customer data
        customer_data = {}
        if args.data:
            customer_data = load_customer_data_from_file(args.data)
        else:
            # Build from command-line arguments
            if args.customer_email:
                customer_data["customer_email"] = args.customer_email
            if args.customer_name:
                customer_data["customer_name"] = args.customer_name
            if args.amount:
                customer_data["amount"] = args.amount
            if args.effective_date:
                customer_data["effective_date"] = args.effective_date
            if args.discount_percent:
                customer_data["discount_percent"] = args.discount_percent
            if args.opportunity_id:
                customer_data["opportunity_id"] = args.opportunity_id
            if args.sales_rep_name:
                customer_data["sales_rep_name"] = args.sales_rep_name

        # Validate customer data
        validate_customer_data(customer_data)

        # Load template mappings
        template_mappings = load_template_mappings(args.config)

        # Get template UUID
        template_uuid = args.template_uuid or args.template
        if not template_uuid.startswith(("abc", "xyz")) and template_mappings:
            # Try to look up UUID by name
            for tpl_data in template_mappings.get("templates", {}).values():
                if tpl_data.get("name") == args.template:
                    template_uuid = tpl_data.get("uuid")
                    break

        # Create document request
        request = create_document_request(
            template_uuid,
            customer_data,
            template_mappings
        )

        # Create document
        document_id = create_document(request)

        # Wait for draft status
        status = wait_for_draft_status(document_id)

        # Success
        print(f"SUCCESS: Proposal created and ready")
        print(f"Document ID: {document_id}")
        print(f"Status: {status}")
        return 0

    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        return 1
    except (
        AuthenticationError,
        TemplateNotFoundError,
        DocumentCreationError,
        StatusPollingError,
        ValueError
    ) as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///

"""
Batch create PandaDoc documents from template with rate limiting and error recovery.

This script creates multiple documents in batches with queue management, parallel
processing support, progress tracking, and error recovery.

Usage:
    # Create from CSV file
    uv run bulk_create_documents.py \\
        --template "Sales Proposal" \\
        --customers customers.csv \\
        --batch-size 50

    # Create with custom delay (6 seconds for rate limiting)
    uv run bulk_create_documents.py \\
        --template "Sales Proposal" \\
        --customers customers.json \\
        --delay 6

    # Resume previous batch
    uv run bulk_create_documents.py \\
        --template "Sales Proposal" \\
        --customers customers.csv \\
        --resume
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


def load_customers_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """Load customer data from CSV file.

    Args:
        file_path: Path to CSV file

    Returns:
        List of customer dictionaries
    """
    logger.info(f"Loading customers from CSV: {file_path}")
    customers = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Remove empty values
                row = {k: v for k, v in row.items() if v}
                if row:
                    customers.append(row)
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Could not read CSV file: {e}")

    logger.info(f"Loaded {len(customers)} customer records")
    return customers


def load_customers_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load customer data from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        List of customer dictionaries
    """
    logger.info(f"Loading customers from JSON: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both list and dict with 'customers' key
            if isinstance(data, list):
                customers = data
            elif isinstance(data, dict) and "customers" in data:
                customers = data["customers"]
            else:
                customers = [data]
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")

    logger.info(f"Loaded {len(customers)} customer records")
    return customers


def load_customers(file_path: str) -> List[Dict[str, Any]]:
    """Load customer data from file (auto-detect format).

    Args:
        file_path: Path to customer data file (CSV or JSON)

    Returns:
        List of customer dictionaries
    """
    if file_path.endswith(".json"):
        return load_customers_from_json(file_path)
    else:
        return load_customers_from_csv(file_path)


def validate_customer(customer: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate customer data.

    Args:
        customer: Customer dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if not customer.get("customer_email"):
        return False, "Missing customer_email"

    # Validate email format
    email = customer.get("customer_email", "")
    if "@" not in email or "." not in email:
        return False, f"Invalid email format: {email}"

    return True, ""


def create_document(
    template_uuid: str,
    customer: Dict[str, Any]
) -> Optional[str]:
    """Create a single document.

    Args:
        template_uuid: Template UUID
        customer: Customer data

    Returns:
        Document ID or None if creation failed
    """
    rate_limiter.wait_if_needed()

    # Validate customer
    is_valid, error = validate_customer(customer)
    if not is_valid:
        logger.warning(f"Skipping invalid customer: {error}")
        return None

    # Build request
    recipients = [
        {
            "email": customer.get("customer_email"),
            "first_name": customer.get("customer_name", "").split()[0] if customer.get("customer_name") else "",
            "last_name": customer.get("customer_name", "").split()[-1] if customer.get("customer_name") else "",
            "role": "Client"
        }
    ]

    fields = {}
    field_map = {
        "customer_name": "Company Name",
        "amount": "Proposal Amount",
        "effective_date": "Effective Date",
    }
    for data_field, doc_field in field_map.items():
        if data_field in customer:
            fields[doc_field] = str(customer[data_field])

    request = {
        "name": f"Proposal - {customer.get('customer_name', 'Unknown')}",
        "template_uuid": template_uuid,
        "recipients": recipients,
        "fields": fields,
    }

    # Create document
    logger.debug(f"Creating document for {customer.get('customer_email')}")
    url = f"{BASE_URL}/documents"
    headers = get_headers()

    try:
        response = requests.post(url, json=request, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create document: {e}")
        return None

    data = response.json()
    document_id = data.get("id")
    logger.info(f"Created document {document_id} for {customer.get('customer_email')}")
    return document_id


def wait_for_draft_status(document_id: str, timeout: int = POLL_TIMEOUT) -> bool:
    """Poll until document reaches draft status.

    Args:
        document_id: Document ID
        timeout: Timeout in seconds

    Returns:
        True if ready, False if timeout
    """
    headers = get_headers()
    url = f"{BASE_URL}/documents/{document_id}"
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            logger.warning(f"Document {document_id} not ready after {timeout}s")
            return False

        time.sleep(POLL_INTERVAL)
        rate_limiter.wait_if_needed()

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Poll failed: {e}")
            continue

        data = response.json()
        status = data.get("status")

        if status == "document.draft":
            logger.debug(f"Document {document_id} ready after {elapsed:.1f}s")
            return True

        if status and status.startswith("document.error"):
            logger.error(f"Document {document_id} error: {status}")
            return False


def load_progress(progress_file: str) -> Dict[str, Any]:
    """Load batch progress from file.

    Args:
        progress_file: Path to progress file

    Returns:
        Progress dictionary
    """
    if Path(progress_file).exists():
        try:
            with open(progress_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load progress: {e}")

    return {
        "completed": [],
        "failed": [],
        "in_progress": []
    }


def save_progress(progress: Dict[str, Any], progress_file: str) -> None:
    """Save batch progress to file.

    Args:
        progress: Progress dictionary
        progress_file: Path to progress file
    """
    try:
        with open(progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save progress: {e}")


def generate_report(
    results: Dict[str, Any],
    output_path: Optional[str] = None
) -> str:
    """Generate batch completion report.

    Args:
        results: Results dictionary
        output_path: Optional path to save report

    Returns:
        Report text
    """
    total = len(results["completed"]) + len(results["failed"])
    success_rate = (len(results["completed"]) / total * 100) if total > 0 else 0

    lines = [
        "",
        "=" * 60,
        "BATCH COMPLETION REPORT",
        "=" * 60,
        f"Timestamp: {datetime.now().isoformat()}",
        f"Total Documents: {total}",
        f"Successfully Created: {len(results['completed'])}",
        f"Failed: {len(results['failed'])}",
        f"Success Rate: {success_rate:.1f}%",
        "=" * 60,
    ]

    if results["completed"]:
        lines.append("")
        lines.append("SUCCESSFUL DOCUMENTS:")
        for doc_id in results["completed"][:10]:
            lines.append(f"  - {doc_id}")
        if len(results["completed"]) > 10:
            lines.append(f"  ... and {len(results['completed']) - 10} more")

    if results["failed"]:
        lines.append("")
        lines.append("FAILED DOCUMENTS:")
        for item in results["failed"][:10]:
            if isinstance(item, dict):
                lines.append(f"  - {item.get('customer', 'Unknown')}: {item.get('error')}")
            else:
                lines.append(f"  - {item}")
        if len(results["failed"]) > 10:
            lines.append(f"  ... and {len(results['failed']) - 10} more")

    lines.append("=" * 60)

    report = "\n".join(lines)

    if output_path:
        try:
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Report saved: {output_path}")
        except Exception as e:
            logger.warning(f"Could not save report: {e}")

    return report


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Batch create PandaDoc documents with rate limiting",
        epilog="""
Examples:
  # Create from CSV file
  python bulk_create_documents.py \\
    --template "Sales Proposal" \\
    --customers customers.csv \\
    --batch-size 50

  # Create from JSON with custom delay
  python bulk_create_documents.py \\
    --template "Sales Proposal" \\
    --customers customers.json \\
    --delay 6

  # Resume from last position
  python bulk_create_documents.py \\
    --template "Sales Proposal" \\
    --customers customers.csv \\
    --resume
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
        help="Explicit template UUID"
    )
    parser.add_argument(
        "--customers",
        required=True,
        help="Customer data file (CSV or JSON)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size (default: 50)"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=6,
        help="Delay between requests in seconds (default: 6)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last saved progress"
    )
    parser.add_argument(
        "--output",
        help="Output report file path"
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

        # Load customers
        customers = load_customers(args.customers)
        logger.info(f"Processing {len(customers)} customers in batches of {args.batch_size}")

        # Get template UUID
        template_uuid = args.template_uuid or args.template

        # Initialize results
        results = {
            "completed": [],
            "failed": []
        }

        progress_file = ".batch_progress.json"
        if args.resume:
            results = load_progress(progress_file)
            logger.info(f"Resuming: {len(results['completed'])} completed, {len(results['failed'])} failed")

        # Process customers
        print(f"Creating documents for {len(customers)} customers...")
        print(f"Batch size: {args.batch_size}, Delay: {args.delay}s")
        print()

        batch_num = 1
        for i, customer in enumerate(customers, 1):
            # Create document
            doc_id = create_document(template_uuid, customer)

            if doc_id:
                # Wait for draft status
                if wait_for_draft_status(doc_id):
                    results["completed"].append(doc_id)
                    logger.info(f"[{i}/{len(customers)}] Document {doc_id} ready")
                else:
                    results["failed"].append({
                        "customer": customer.get("customer_email"),
                        "error": "Status polling timeout"
                    })
                    logger.error(f"[{i}/{len(customers)}] Document ready timeout")
            else:
                results["failed"].append({
                    "customer": customer.get("customer_email"),
                    "error": "Creation failed"
                })
                logger.error(f"[{i}/{len(customers)}] Creation failed")

            # Add delay between requests (rate limiting)
            if i < len(customers):
                time.sleep(args.delay)

            # Save progress periodically
            if i % args.batch_size == 0:
                batch_num += 1
                logger.info(f"Batch {batch_num} progress saved")
                save_progress(results, progress_file)

        # Final save
        save_progress(results, progress_file)

        # Generate report
        report = generate_report(results, args.output)
        print(report)

        return 0 if not results["failed"] else 1

    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        save_progress(results, progress_file)
        return 1
    except (AuthenticationError, ValueError) as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

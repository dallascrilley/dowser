#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///

"""
Download completed PandaDoc documents within a date range.

This script downloads all completed or approved documents in a specified date range
with batch processing, retry logic, and customizable naming patterns.

Usage:
    # Download from date range
    uv run download_completed.py \\
        --from "2024-01-01" \\
        --to "2024-01-31" \\
        --output ./downloads

    # Download with custom naming pattern
    uv run download_completed.py \\
        --from "2024-01-01" \\
        --to "2024-12-31" \\
        --output ./downloads \\
        --pattern "{date}_{customer}_{id}.pdf"

    # Download only completed (not approved)
    uv run download_completed.py \\
        --from "2024-01-01" \\
        --to "2024-01-31" \\
        --status "document.completed" \\
        --output ./downloads
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
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


def list_documents(
    status: str = "document.completed",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List documents matching criteria.

    Args:
        status: Document status filter
        date_from: From date (YYYY-MM-DD)
        date_to: To date (YYYY-MM-DD)

    Returns:
        List of document dictionaries
    """
    logger.info(f"Listing documents (status: {status}, from: {date_from}, to: {date_to})")

    documents = []
    page = 1
    per_page = 100

    # Convert status name to status code if needed
    status_code = None
    status_map = {
        "document.completed": 2,
        "document.approved": 7,
        "document.draft": 0,
        "document.sent": 1,
    }
    if status in status_map:
        status_code = status_map[status]

    while True:
        rate_limiter.wait_if_needed()

        # Build query params
        params = {
            "count": per_page,
            "page": page,
        }
        if status_code is not None:
            params["status"] = status_code

        # Note: Date filtering via API is limited, so we filter locally
        url = f"{BASE_URL}/documents"

        try:
            response = requests.get(url, headers=get_headers(), params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list documents: {e}")
            raise

        data = response.json()
        results = data.get("results", [])

        # Filter by date range locally
        for doc in results:
            created = doc.get("date_created", "")
            if date_from or date_to:
                # Parse date (format: YYYY-MM-DDTHH:MM:SS)
                if created:
                    doc_date = created.split("T")[0] if "T" in created else created
                    if date_from and doc_date < date_from:
                        continue
                    if date_to and doc_date > date_to:
                        continue
            documents.append(doc)

        # Check for more pages
        next_url = data.get("next")
        if not next_url:
            break

        page += 1

    logger.info(f"Found {len(documents)} documents")
    return documents


def download_document(document_id: str, output_path: str) -> bool:
    """Download a document.

    Args:
        document_id: Document ID
        output_path: Path to save PDF file

    Returns:
        True if successful, False otherwise
    """
    rate_limiter.wait_if_needed()

    logger.debug(f"Downloading document {document_id} to {output_path}")
    url = f"{BASE_URL}/documents/{document_id}/download"
    headers = get_headers()

    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"Document not found: {document_id}")
        else:
            logger.error(f"Download failed: {e}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Download error: {e}")
        return False

    # Save to file
    try:
        # Create directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Downloaded: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return False


def generate_filename(
    pattern: str,
    document: Dict[str, Any],
    index: int
) -> str:
    """Generate filename from pattern.

    Args:
        pattern: Filename pattern
        document: Document dictionary
        index: Document index

    Returns:
        Generated filename
    """
    # Extract date from document
    date_str = ""
    if document.get("date_created"):
        date_str = document["date_created"].split("T")[0]

    # Extract customer from document name
    name = document.get("name", "document")
    # Try to extract customer name from proposal name
    customer = ""
    if " - " in name:
        customer = name.split(" - ")[1]
    else:
        customer = name.replace("Proposal ", "").replace("Document ", "")
    customer = re.sub(r"[^a-zA-Z0-9_-]", "", customer)[:50]

    # Build replacements
    replacements = {
        "{date}": date_str,
        "{customer}": customer,
        "{id}": document.get("id", "unknown")[:8],
        "{name}": name[:30].replace(" ", "_"),
        "{index}": str(index).zfill(4),
        "{status}": document.get("status", "unknown").replace("document.", ""),
    }

    filename = pattern
    for key, value in replacements.items():
        filename = filename.replace(key, value)

    # Ensure .pdf extension
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    return filename


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Download completed PandaDoc documents from date range",
        epilog="""
Examples:
  # Download from date range
  python download_completed.py \\
    --from "2024-01-01" \\
    --to "2024-01-31" \\
    --output ./downloads

  # With custom filename pattern
  python download_completed.py \\
    --from "2024-01-01" \\
    --to "2024-12-31" \\
    --output ./downloads \\
    --pattern "{date}_{customer}_{id}.pdf"

  # Only completed (not approved)
  python download_completed.py \\
    --from "2024-01-01" \\
    --to "2024-01-31" \\
    --status "document.completed" \\
    --output ./downloads

  # Available pattern variables:
    {date} - Document creation date
    {customer} - Customer/company name
    {id} - Document ID (first 8 chars)
    {name} - Document name
    {index} - Sequential index (0001, 0002, ...)
    {status} - Document status
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--from",
        required=True,
        help="From date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--to",
        required=True,
        help="To date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory"
    )
    parser.add_argument(
        "--status",
        default="document.completed",
        help="Status filter (default: document.completed). "
             "Can also use: document.approved"
    )
    parser.add_argument(
        "--pattern",
        default="{date}_{customer}_{id}.pdf",
        help="Filename pattern (default: {date}_{customer}_{id}.pdf)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip already downloaded files"
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

        # Validate date format
        try:
            datetime.strptime(args.__dict__["from"], "%Y-%m-%d")
            datetime.strptime(args.to, "%Y-%m-%d")
        except ValueError:
            logger.error("Invalid date format. Use YYYY-MM-DD")
            return 1

        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # List documents
        print(f"Searching for documents...")
        print(f"  Date range: {args.__dict__['from']} to {args.to}")
        print(f"  Status: {args.status}")
        print()

        documents = list_documents(
            status=args.status,
            date_from=args.__dict__["from"],
            date_to=args.to
        )

        if not documents:
            print("No documents found")
            return 0

        print(f"Found {len(documents)} documents")
        print(f"Downloading to: {output_dir}")
        print()

        # Download documents
        successful = 0
        failed = 0
        skipped = 0

        for i, doc in enumerate(documents, 1):
            doc_id = doc.get("id")
            doc_name = doc.get("name", "Unknown")

            # Generate filename
            filename = generate_filename(args.pattern, doc, i)
            output_path = output_dir / filename

            # Check if file exists
            if args.skip_existing and output_path.exists():
                logger.info(f"[{i}/{len(documents)}] Skipping existing: {filename}")
                skipped += 1
                continue

            # Download
            logger.info(f"[{i}/{len(documents)}] Downloading: {doc_name}")
            if download_document(doc_id, str(output_path)):
                successful += 1
            else:
                failed += 1

            # Rate limiting
            if i < len(documents):
                time.sleep(1)

        # Summary
        print()
        print("=" * 60)
        print("DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"Total: {len(documents)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        print(f"Output: {output_dir}")
        print("=" * 60)

        return 0 if failed == 0 else 1

    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        return 1
    except (AuthenticationError, ValueError) as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

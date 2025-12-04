#!/usr/bin/env python3
"""
Bulk Import Helper for Copper CRM

Import CSV files for leads, people, companies, and opportunities with:
- Data validation
- Duplicate detection (UPSERT)
- Batch processing with rate limiting
- Error recovery and retries
- Progress tracking and reporting
"""

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table


# Configure constants
BATCH_SIZE = 10
RATE_LIMIT = 3  # requests per second
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# CSV Headers for each entity type
ENTITY_HEADERS = {
    "leads": ["name", "email", "company_name", "title", "phone"],
    "people": ["name", "email", "company_name", "title"],
    "companies": ["name", "email_domain", "address"],
    "opportunities": ["name", "primary_contact_email", "monetary_value"],
}

console = Console()


@dataclass
class ImportRecord:
    """Represents a single record to import"""
    row_num: int
    data: Dict[str, Any]
    entity_type: str
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def is_valid(self) -> bool:
        """Check if record has no validation errors"""
        return len(self.errors) == 0


@dataclass
class ImportResult:
    """Represents the result of a single record import"""
    row_num: int
    success: bool
    record_id: Optional[str] = None
    is_duplicate: bool = False
    error_message: Optional[str] = None
    retry_count: int = 0


class CopperCRMClient:
    """Handles Copper CRM API interactions"""

    def __init__(self, api_key: str, api_url: str = "https://api.copper.com/developer_api/v1"):
        self.api_key = api_key
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            "X-PB-API-KEY": api_key,
            "Content-Type": "application/json",
        })
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting (3 requests per second)"""
        elapsed = time.time() - self.last_request_time
        min_interval = 1.0 / RATE_LIMIT
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Tuple[int, Dict]:
        """Make API request with rate limiting"""
        self._rate_limit()
        url = f"{self.api_url}{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return response.status_code, response.json() if response.text else {}
        except Exception as e:
            return 500, {"error": str(e)}

    def find_duplicate(self, entity_type: str, record: Dict) -> Optional[str]:
        """
        Check if a record already exists using entity-specific criteria
        Returns the record ID if found, None otherwise
        """
        if entity_type == "leads":
            return self._find_lead(record.get("email"))
        elif entity_type == "people":
            return self._find_person(record.get("email"))
        elif entity_type == "companies":
            return self._find_company(record.get("name"))
        elif entity_type == "opportunities":
            return self._find_opportunity(record.get("name"))

    def _find_lead(self, email: str) -> Optional[str]:
        """Find lead by email"""
        if not email:
            return None
        status, response = self._make_request("POST", "/leads/search", {
            "email": email
        })
        if status == 200 and response.get("leads"):
            return str(response["leads"][0]["id"])
        return None

    def _find_person(self, email: str) -> Optional[str]:
        """Find person by email"""
        if not email:
            return None
        status, response = self._make_request("POST", "/people/search", {
            "email": email
        })
        if status == 200 and response.get("people"):
            return str(response["people"][0]["id"])
        return None

    def _find_company(self, name: str) -> Optional[str]:
        """Find company by name"""
        if not name:
            return None
        status, response = self._make_request("POST", "/companies/search", {
            "name": name
        })
        if status == 200 and response.get("companies"):
            return str(response["companies"][0]["id"])
        return None

    def _find_opportunity(self, name: str) -> Optional[str]:
        """Find opportunity by name"""
        if not name:
            return None
        status, response = self._make_request("POST", "/opportunities/search", {
            "name": name
        })
        if status == 200 and response.get("opportunities"):
            return str(response["opportunities"][0]["id"])
        return None

    def upsert_record(self, entity_type: str, record: Dict,
                      duplicate_id: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create or update a record (UPSERT)
        Returns: (success, record_id, error_message)
        """
        endpoint = f"/{entity_type}"

        if duplicate_id:
            # Update existing record
            status, response = self._make_request("PUT", f"{endpoint}/{duplicate_id}", record)
        else:
            # Create new record
            status, response = self._make_request("POST", endpoint, record)

        if status in (200, 201):
            record_id = response.get("id") or duplicate_id
            return True, str(record_id) if record_id else None, None
        else:
            error = response.get("error", {})
            error_msg = error.get("message") if isinstance(error, dict) else str(error)
            return False, None, error_msg


class BulkImporter:
    """Handles bulk import orchestration"""

    def __init__(self, entity_type: str, csv_path: str, api_key: str, mode: str = "upsert"):
        self.entity_type = entity_type
        self.csv_path = Path(csv_path)
        self.api_key = api_key
        self.mode = mode
        self.client = CopperCRMClient(api_key)
        self.results: List[ImportResult] = []
        self.failed_records: List[ImportRecord] = []

    def validate_csv_headers(self, headers: List[str]) -> List[str]:
        """Validate CSV headers against expected fields"""
        expected = set(ENTITY_HEADERS.get(self.entity_type, []))
        actual = set(h.strip().lower() for h in headers)

        missing = expected - actual
        if missing:
            console.print(f"[red]Error:[/red] Missing required columns: {', '.join(missing)}")
            console.print(f"[yellow]Expected:[/yellow] {', '.join(sorted(expected))}")
            console.print(f"[cyan]Actual:[/cyan] {', '.join(sorted(actual))}")
            return []

        return [h.strip().lower() for h in headers]

    def load_records(self) -> List[ImportRecord]:
        """Load and validate records from CSV"""
        records = []

        if not self.csv_path.exists():
            console.print(f"[red]Error: File not found: {self.csv_path}")
            return records

        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = self.validate_csv_headers(reader.fieldnames or [])

                if not headers:
                    return records

                for row_num, row in enumerate(reader, start=2):
                    # Normalize row keys to lowercase
                    normalized_row = {k.lower(): v.strip() if v else "" for k, v in row.items()}

                    record = ImportRecord(
                        row_num=row_num,
                        data=normalized_row,
                        entity_type=self.entity_type,
                    )

                    self._validate_record(record)
                    records.append(record)

        except Exception as e:
            console.print(f"[red]Error reading CSV: {e}")
            return []

        return records

    def _validate_record(self, record: ImportRecord):
        """Validate individual record"""
        required_fields = ENTITY_HEADERS.get(self.entity_type, [])

        for field in required_fields:
            if not record.data.get(field):
                record.errors.append(f"Missing required field: {field}")

        # Entity-specific validation
        if self.entity_type == "leads":
            self._validate_lead(record)
        elif self.entity_type == "people":
            self._validate_person(record)
        elif self.entity_type == "companies":
            self._validate_company(record)
        elif self.entity_type == "opportunities":
            self._validate_opportunity(record)

    def _validate_lead(self, record: ImportRecord):
        """Validate lead-specific fields"""
        email = record.data.get("email", "")
        if email and "@" not in email:
            record.errors.append(f"Invalid email format: {email}")

    def _validate_person(self, record: ImportRecord):
        """Validate person-specific fields"""
        email = record.data.get("email", "")
        if email and "@" not in email:
            record.errors.append(f"Invalid email format: {email}")

    def _validate_company(self, record: ImportRecord):
        """Validate company-specific fields"""
        pass  # Add company-specific validation as needed

    def _validate_opportunity(self, record: ImportRecord):
        """Validate opportunity-specific fields"""
        try:
            value = record.data.get("monetary_value", "0")
            if value:
                float(value)
        except ValueError:
            record.errors.append(f"Invalid monetary_value: {value}")

    def import_batch(self, batch: List[ImportRecord]) -> List[ImportResult]:
        """Import a batch of records with retry logic"""
        batch_results = []

        for record in batch:
            result = self._import_record_with_retry(record)
            batch_results.append(result)

        return batch_results

    def _import_record_with_retry(self, record: ImportRecord) -> ImportResult:
        """Import a single record with retry logic"""
        if not record.is_valid():
            return ImportResult(
                row_num=record.row_num,
                success=False,
                error_message="; ".join(record.errors),
            )

        for attempt in range(MAX_RETRIES):
            # Check for duplicates in UPSERT mode
            duplicate_id = None
            is_duplicate = False

            if self.mode == "upsert":
                duplicate_id = self.client.find_duplicate(self.entity_type, record.data)
                is_duplicate = duplicate_id is not None

            # Perform UPSERT
            success, record_id, error_msg = self.client.upsert_record(
                self.entity_type,
                record.data,
                duplicate_id,
            )

            if success:
                return ImportResult(
                    row_num=record.row_num,
                    success=True,
                    record_id=record_id,
                    is_duplicate=is_duplicate,
                    retry_count=attempt,
                )

            # Retry logic
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return ImportResult(
                    row_num=record.row_num,
                    success=False,
                    error_message=error_msg,
                    retry_count=attempt + 1,
                )

        # Should not reach here
        return ImportResult(
            row_num=record.row_num,
            success=False,
            error_message="Unknown error",
            retry_count=MAX_RETRIES,
        )

    def run(self):
        """Execute the bulk import"""
        # Load records
        console.print(f"[cyan]Loading CSV file:[/cyan] {self.csv_path}")
        records = self.load_records()

        if not records:
            console.print("[red]No records to import[/red]")
            return

        console.print(f"[green]Loaded {len(records)} records[/green]\n")

        # Validate records
        valid_records = [r for r in records if r.is_valid()]
        invalid_records = [r for r in records if not r.is_valid()]

        if invalid_records:
            console.print(f"[yellow]Warning: {len(invalid_records)} invalid record(s)[/yellow]")
            for record in invalid_records:
                console.print(f"  Row {record.row_num}: {'; '.join(record.errors)}")
            console.print()

        # Process batches with progress bar
        total_batches = (len(valid_records) + BATCH_SIZE - 1) // BATCH_SIZE

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Importing {len(valid_records)} records...[/cyan]",
                total=len(valid_records),
            )

            for batch_num in range(total_batches):
                start_idx = batch_num * BATCH_SIZE
                end_idx = min(start_idx + BATCH_SIZE, len(valid_records))
                batch = valid_records[start_idx:end_idx]

                batch_results = self.import_batch(batch)
                self.results.extend(batch_results)

                # Update progress
                progress.update(task, advance=len(batch))

        # Generate report
        self._print_report()

    def _print_report(self):
        """Print import summary report"""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        duplicates = [r for r in successful if r.is_duplicate]

        console.print("\n" + "=" * 60)
        console.print("[bold]Import Summary Report[/bold]")
        console.print("=" * 60)

        # Create summary table
        summary_table = Table(show_header=False, box=None)
        summary_table.add_row("Total Records:", f"[cyan]{len(self.results)}[/cyan]")
        summary_table.add_row("Successful:", f"[green]{len(successful)}[/green]")
        summary_table.add_row("Duplicates Updated:", f"[blue]{len(duplicates)}[/blue]")
        summary_table.add_row("Failed:", f"[red]{len(failed)}[/red]")
        summary_table.add_row("Success Rate:", f"[yellow]{len(successful) / len(self.results) * 100:.1f}%[/yellow]")

        console.print(summary_table)

        # Show failed records if any
        if failed:
            console.print("\n[bold red]Failed Records:[/bold red]")
            failed_table = Table(title="Failed Imports")
            failed_table.add_column("Row", style="cyan")
            failed_table.add_column("Error", style="red")

            for result in failed:
                failed_table.add_row(str(result.row_num), result.error_message or "Unknown error")

            console.print(failed_table)

        console.print("=" * 60)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Bulk import data into Copper CRM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bulk_import.py leads import.csv --mode upsert
  python bulk_import.py people contacts.csv --mode create
  python bulk_import.py companies companies.csv
  python bulk_import.py opportunities deals.csv --api-key YOUR_KEY
        """
    )

    parser.add_argument(
        "entity_type",
        choices=["leads", "people", "companies", "opportunities"],
        help="Type of entity to import",
    )
    parser.add_argument(
        "csv_file",
        help="Path to CSV file to import",
    )
    parser.add_argument(
        "--mode",
        choices=["create", "upsert"],
        default="upsert",
        help="Import mode: create (new only) or upsert (update existing)",
    )
    parser.add_argument(
        "--api-key",
        help="Copper CRM API key (uses COPPER_API_KEY env var if not provided)",
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("COPPER_API_KEY")
    if not api_key:
        console.print("[red]Error: Copper API key not provided[/red]")
        console.print("Use --api-key flag or set COPPER_API_KEY environment variable")
        sys.exit(1)

    # Run import
    try:
        importer = BulkImporter(
            entity_type=args.entity_type,
            csv_path=args.csv_file,
            api_key=api_key,
            mode=args.mode,
        )
        importer.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Import cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

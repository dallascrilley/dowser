#!/usr/bin/env python3
"""
Copper CRM Interactive CLI Tool

A comprehensive command-line interface for managing Copper CRM operations including:
- CRUD operations on Leads, People, Companies, and Opportunities
- Advanced search with filtering
- Bulk CSV import with UPSERT mode
- Error handling with automatic retry logic
- Progress indicators for long-running operations
"""

import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

# Initialize rich console for beautiful output
console = Console()

# Load environment variables
load_dotenv()

# Constants
API_BASE_URL = "https://api.copper.com/developer_api/v1"
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2
TIMEOUT = 30

# Entity configurations
ENTITIES = {
    "leads": {
        "endpoint": "/leads",
        "fields": ["name", "email", "phone", "company_name", "status"],
        "required": ["name"],
    },
    "people": {
        "endpoint": "/people",
        "fields": ["first_name", "last_name", "email", "phone", "company_id"],
        "required": ["first_name", "last_name"],
    },
    "companies": {
        "endpoint": "/companies",
        "fields": ["name", "email", "phone", "website", "address"],
        "required": ["name"],
    },
    "opportunities": {
        "endpoint": "/opportunities",
        "fields": ["name", "company_id", "person_id", "stage", "status", "value"],
        "required": ["name"],
    },
}


class CopperAPIClient:
    """Copper CRM API client with retry logic and error handling."""

    def __init__(self, api_token: str):
        """
        Initialize the API client.

        Args:
            api_token: Copper API token from environment
        """
        self.api_token = api_token
        self.base_url = API_BASE_URL
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=RETRY_ATTEMPTS,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "X-PW-AccessToken": self.api_token,
            "X-PW-Application": "copper_cli",
            "Content-Type": "application/json",
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate errors.

        Args:
            response: The response object from requests

        Returns:
            Parsed JSON response

        Raises:
            click.ClickException: For API errors
        """
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                console.print(
                    "[yellow]Rate limited. Please wait before retrying.[/yellow]"
                )
            elif response.status_code == 500:
                console.print("[red]Server error. Please try again later.[/red]")
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", str(e))
                except (json.JSONDecodeError, AttributeError):
                    error_msg = str(e)
                console.print(f"[red]API Error: {error_msg}[/red]")
            raise click.ClickException(f"API Error: {e}")

        try:
            return response.json()
        except json.JSONDecodeError:
            return {"status": "success"}

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(
            url,
            headers=self._get_headers(),
            params=params,
            timeout=TIMEOUT,
        )
        return self._handle_response(response)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(
            url,
            headers=self._get_headers(),
            json=data,
            timeout=TIMEOUT,
        )
        return self._handle_response(response)

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a PUT request to the API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(
            url,
            headers=self._get_headers(),
            json=data,
            timeout=TIMEOUT,
        )
        return self._handle_response(response)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request to the API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(
            url,
            headers=self._get_headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(response)


def get_api_client() -> CopperAPIClient:
    """Get or create an API client instance."""
    api_token = os.getenv("COPPER_API_TOKEN")
    if not api_token:
        console.print(
            "[red]Error: COPPER_API_TOKEN not found in environment variables[/red]"
        )
        console.print(
            "[yellow]Please set COPPER_API_TOKEN in .env or environment[/yellow]"
        )
        raise click.ClickException("Missing COPPER_API_TOKEN")
    return CopperAPIClient(api_token)


def validate_entity(entity: str) -> None:
    """Validate that entity type is supported."""
    if entity.lower() not in ENTITIES:
        raise click.BadParameter(
            f"Entity must be one of: {', '.join(ENTITIES.keys())}"
        )


def display_record(record: Dict[str, Any], entity: str) -> None:
    """Display a single record in a formatted table."""
    table = Table(title=f"{entity.upper()} Record", show_header=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")

    for key, value in record.items():
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)
        table.add_row(key, value_str)

    console.print(table)


def display_records_table(records: List[Dict[str, Any]], entity: str) -> None:
    """Display multiple records in a table format."""
    if not records:
        console.print("[yellow]No records found.[/yellow]")
        return

    # Get fields from entity config
    fields = ENTITIES[entity.lower()]["fields"]

    # Create table
    table = Table(title=f"{entity.upper()} Records")
    table.add_column("ID", style="cyan")

    for field in fields:
        if field in ["custom_fields"]:
            continue
        table.add_column(field.replace("_", " ").title(), style="magenta")

    # Add rows
    for record in records[:100]:  # Limit to first 100
        row = [str(record.get("id", "N/A"))]

        for field in fields:
            value = record.get(field, "")
            if isinstance(value, (dict, list)):
                value = json.dumps(value)[:30] + "..."
            row.append(str(value)[:50])

        table.add_row(*row)

    console.print(table)
    if len(records) > 100:
        console.print(
            f"[yellow]Showing first 100 of {len(records)} records[/yellow]"
        )


def interactive_field_input(entity: str) -> Dict[str, Any]:
    """Interactively prompt for field inputs."""
    config = ENTITIES[entity.lower()]
    data = {}

    console.print(f"\n[bold cyan]Creating new {entity}[/bold cyan]")
    console.print(
        f"[dim]Required fields: {', '.join(config['required'])}[/dim]\n"
    )

    for field in config["fields"]:
        is_required = field in config["required"]
        prompt_text = f"{field.replace('_', ' ').title()}"
        if is_required:
            prompt_text += " [required]"

        value = Prompt.ask(prompt_text, default="" if not is_required else None)

        if value:
            # Try to convert to int for numeric fields
            if field.endswith("_id") or field == "value":
                try:
                    data[field] = int(value)
                except ValueError:
                    data[field] = value
            else:
                data[field] = value

    return data


@click.group()
@click.version_option()
def cli():
    """Copper CRM Interactive CLI - Manage your CRM data from the command line."""
    pass


@cli.command()
@click.argument("entity")
def create(entity: str) -> None:
    """Create a new record interactively."""
    validate_entity(entity)

    try:
        client = get_api_client()
        data = interactive_field_input(entity)

        if not data:
            console.print("[yellow]No data provided. Aborting.[/yellow]")
            return

        with console.status(f"[bold green]Creating {entity}...", spinner="dots"):
            result = client.post(ENTITIES[entity.lower()]["endpoint"], data)

        console.print(f"\n[green]Successfully created {entity}![/green]")
        display_record(result, entity)

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("entity")
@click.option(
    "--query",
    "-q",
    help="Search query (name, email, etc.)",
)
@click.option(
    "--field",
    "-f",
    multiple=True,
    help="Filter by field (format: field=value)",
)
@click.option(
    "--limit",
    "-l",
    default=10,
    type=int,
    help="Number of results to return",
)
def search(
    entity: str,
    query: Optional[str],
    field: Tuple[str, ...],
    limit: int,
) -> None:
    """Search for records with filters."""
    validate_entity(entity)

    try:
        client = get_api_client()

        # Build search parameters
        params = {"limit": limit}

        if query:
            params["name"] = query

        # Add field filters
        for filter_item in field:
            if "=" in filter_item:
                key, value = filter_item.split("=", 1)
                params[key.strip()] = value.strip()

        with console.status("[bold green]Searching...", spinner="dots"):
            result = client.get(ENTITIES[entity.lower()]["endpoint"], params)

        records = result if isinstance(result, list) else [result]
        display_records_table(records, entity)

        console.print(f"\n[cyan]Found {len(records)} record(s)[/cyan]")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("entity")
@click.argument("record_id", type=int)
def update(entity: str, record_id: int) -> None:
    """Update an existing record interactively."""
    validate_entity(entity)

    try:
        client = get_api_client()
        endpoint = ENTITIES[entity.lower()]["endpoint"]

        # Fetch current record
        with console.status("[bold green]Fetching record...", spinner="dots"):
            current = client.get(f"{endpoint}/{record_id}")

        console.print("\n[bold cyan]Current record:[/bold cyan]")
        display_record(current, entity)

        console.print("\n[bold cyan]Update fields (leave blank to skip):[/bold cyan]\n")

        update_data = {}
        for field in ENTITIES[entity.lower()]["fields"]:
            current_value = current.get(field, "")
            prompt_text = f"{field.replace('_', ' ').title()} [{current_value}]"

            value = Prompt.ask(prompt_text, default="")

            if value:
                # Try to convert to int for numeric fields
                if field.endswith("_id") or field == "value":
                    try:
                        update_data[field] = int(value)
                    except ValueError:
                        update_data[field] = value
                else:
                    update_data[field] = value

        if not update_data:
            console.print("[yellow]No updates provided. Aborting.[/yellow]")
            return

        if Confirm.ask("[yellow]Confirm update?[/yellow]"):
            with console.status("[bold green]Updating record...", spinner="dots"):
                result = client.put(f"{endpoint}/{record_id}", update_data)

            console.print(f"\n[green]Successfully updated {entity}![/green]")
            display_record(result, entity)
        else:
            console.print("[yellow]Update cancelled.[/yellow]")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("entity")
@click.argument("record_id", type=int)
def delete(entity: str, record_id: int) -> None:
    """Delete a record."""
    validate_entity(entity)

    try:
        client = get_api_client()
        endpoint = ENTITIES[entity.lower()]["endpoint"]

        # Fetch record to show what we're deleting
        with console.status("[bold green]Fetching record...", spinner="dots"):
            record = client.get(f"{endpoint}/{record_id}")

        console.print(f"\n[bold red]Warning: About to delete:[/bold red]")
        display_record(record, entity)

        if Confirm.ask(
            f"\n[red]Are you sure you want to delete this {entity}?[/red]",
            default=False,
        ):
            with console.status("[bold red]Deleting record...", spinner="dots"):
                client.delete(f"{endpoint}/{record_id}")

            console.print(f"\n[green]Successfully deleted {entity}![/green]")
        else:
            console.print("[yellow]Delete cancelled.[/yellow]")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@cli.command("bulk-import")
@click.argument("csv_file", type=click.Path(exists=True))
@click.option(
    "--entity",
    "-e",
    required=True,
    type=click.Choice(list(ENTITIES.keys())),
    help="Entity type to import",
)
@click.option(
    "--upsert",
    is_flag=True,
    default=False,
    help="Use UPSERT mode to prevent duplicates",
)
@click.option(
    "--upsert-field",
    "-u",
    default="email",
    help="Field to use for UPSERT matching (default: email)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview import without making changes",
)
def bulk_import(
    csv_file: str,
    entity: str,
    upsert: bool,
    upsert_field: str,
    dry_run: bool,
) -> None:
    """Bulk import records from CSV file."""
    validate_entity(entity)

    try:
        client = get_api_client()
        endpoint = ENTITIES[entity]["endpoint"]

        # Read CSV
        records = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)

        if not records:
            console.print("[yellow]CSV file is empty.[/yellow]")
            return

        # Validate CSV has required fields
        config = ENTITIES[entity]
        csv_headers = set(records[0].keys())
        missing_required = set(config["required"]) - csv_headers

        if missing_required:
            console.print(
                f"[red]CSV missing required fields: {', '.join(missing_required)}[/red]"
            )
            raise click.ClickException("Invalid CSV format")

        console.print(f"\n[cyan]Importing {len(records)} records as {entity}[/cyan]")
        if upsert:
            console.print(
                f"[cyan]UPSERT mode enabled (matching on: {upsert_field})[/cyan]"
            )
        if dry_run:
            console.print("[yellow]DRY RUN - No changes will be made[/yellow]")

        console.print()

        success_count = 0
        error_count = 0
        skipped_count = 0
        errors_list = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[green]Processing {entity}...",
                total=len(records),
            )

            for idx, record in enumerate(records, 1):
                try:
                    # Clean up record - remove empty values
                    clean_record = {k: v for k, v in record.items() if v}

                    if not clean_record:
                        skipped_count += 1
                        progress.update(task, advance=1)
                        continue

                    if upsert:
                        # Search for existing record
                        if upsert_field in clean_record:
                            search_params = {
                                upsert_field: clean_record[upsert_field]
                            }
                            existing = client.get(endpoint, search_params)
                            existing_records = (
                                existing
                                if isinstance(existing, list)
                                else [existing]
                                if existing
                                else []
                            )

                            if existing_records:
                                # Update existing
                                existing_id = existing_records[0]["id"]
                                if not dry_run:
                                    client.put(
                                        f"{endpoint}/{existing_id}",
                                        clean_record,
                                    )
                                success_count += 1
                            else:
                                # Create new
                                if not dry_run:
                                    client.post(endpoint, clean_record)
                                success_count += 1
                        else:
                            skipped_count += 1
                    else:
                        # Regular import - just create
                        if not dry_run:
                            client.post(endpoint, clean_record)
                        success_count += 1

                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {idx}: {str(e)[:100]}"
                    errors_list.append(error_msg)

                progress.update(task, advance=1)

        # Summary
        console.print("\n[bold cyan]Import Summary:[/bold cyan]")
        summary_table = Table(show_header=False)
        summary_table.add_row("Total Records", str(len(records)))
        summary_table.add_row("Successful", f"[green]{success_count}[/green]")
        summary_table.add_row("Failed", f"[red]{error_count}[/red]")
        summary_table.add_row("Skipped", f"[yellow]{skipped_count}[/yellow]")
        if dry_run:
            summary_table.add_row("Mode", "[yellow]DRY RUN[/yellow]")

        console.print(summary_table)

        if errors_list:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in errors_list[:10]:
                console.print(f"  [red]{error}[/red]")
            if len(errors_list) > 10:
                console.print(
                    f"  [yellow]... and {len(errors_list) - 10} more errors[/yellow]"
                )

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@cli.command()
def interactive():
    """Launch interactive menu mode."""
    while True:
        console.clear() if sys.platform != "win32" else None
        console.print(
            Panel(
                "[bold cyan]Copper CRM Interactive Menu[/bold cyan]",
                expand=False,
            )
        )

        choices = {
            "1": ("Create Record", create_menu),
            "2": ("Search Records", search_menu),
            "3": ("Update Record", update_menu),
            "4": ("Delete Record", delete_menu),
            "5": ("Bulk Import", bulk_import_menu),
            "6": ("Exit", None),
        }

        for key, (label, _) in choices.items():
            console.print(f"  [cyan]{key}[/cyan] - {label}")

        choice = Prompt.ask("\nSelect option").strip()

        if choice == "6":
            console.print("[cyan]Goodbye![/cyan]")
            break
        elif choice in choices:
            handler = choices[choice][1]
            if handler:
                try:
                    handler()
                except click.ClickException:
                    console.print(
                        "[yellow]Press Enter to continue...[/yellow]"
                    )
                    input()
                except KeyboardInterrupt:
                    console.print("[yellow]Cancelled.[/yellow]")
                    input()
        else:
            console.print("[red]Invalid option.[/red]")
            input()


def create_menu() -> None:
    """Interactive menu for creating records."""
    console.print("\n[bold cyan]Select Entity Type:[/bold cyan]")
    entities_list = list(ENTITIES.keys())
    for idx, entity in enumerate(entities_list, 1):
        console.print(f"  {idx} - {entity.capitalize()}")

    choice = Prompt.ask("Select").strip()
    try:
        entity = entities_list[int(choice) - 1]
        ctx = click.Context(create)
        ctx.invoke(create, entity=entity)
        input("[yellow]Press Enter to continue...[/yellow]")
    except (ValueError, IndexError):
        console.print("[red]Invalid selection.[/red]")


def search_menu() -> None:
    """Interactive menu for searching records."""
    console.print("\n[bold cyan]Select Entity Type:[/bold cyan]")
    entities_list = list(ENTITIES.keys())
    for idx, entity in enumerate(entities_list, 1):
        console.print(f"  {idx} - {entity.capitalize()}")

    choice = Prompt.ask("Select").strip()
    try:
        entity = entities_list[int(choice) - 1]

        query = Prompt.ask(
            "Enter search query (or leave blank for all)",
            default="",
        )
        limit = int(
            Prompt.ask(
                "Number of results",
                default="10",
            )
        )

        ctx = click.Context(search)
        ctx.invoke(
            search,
            entity=entity,
            query=query if query else None,
            field=(),
            limit=limit,
        )
        input("[yellow]Press Enter to continue...[/yellow]")
    except (ValueError, IndexError):
        console.print("[red]Invalid selection.[/red]")


def update_menu() -> None:
    """Interactive menu for updating records."""
    console.print("\n[bold cyan]Select Entity Type:[/bold cyan]")
    entities_list = list(ENTITIES.keys())
    for idx, entity in enumerate(entities_list, 1):
        console.print(f"  {idx} - {entity.capitalize()}")

    choice = Prompt.ask("Select").strip()
    try:
        entity = entities_list[int(choice) - 1]
        record_id = int(Prompt.ask("Enter record ID"))

        ctx = click.Context(update)
        ctx.invoke(update, entity=entity, record_id=record_id)
        input("[yellow]Press Enter to continue...[/yellow]")
    except (ValueError, IndexError):
        console.print("[red]Invalid input.[/red]")


def delete_menu() -> None:
    """Interactive menu for deleting records."""
    console.print("\n[bold cyan]Select Entity Type:[/bold cyan]")
    entities_list = list(ENTITIES.keys())
    for idx, entity in enumerate(entities_list, 1):
        console.print(f"  {idx} - {entity.capitalize()}")

    choice = Prompt.ask("Select").strip()
    try:
        entity = entities_list[int(choice) - 1]
        record_id = int(Prompt.ask("Enter record ID"))

        ctx = click.Context(delete)
        ctx.invoke(delete, entity=entity, record_id=record_id)
        input("[yellow]Press Enter to continue...[/yellow]")
    except (ValueError, IndexError):
        console.print("[red]Invalid input.[/red]")


def bulk_import_menu() -> None:
    """Interactive menu for bulk import."""
    csv_path = Prompt.ask("Enter path to CSV file")

    if not Path(csv_path).exists():
        console.print("[red]File not found.[/red]")
        return

    entities_list = list(ENTITIES.keys())
    console.print("\n[bold cyan]Select Entity Type:[/bold cyan]")
    for idx, entity in enumerate(entities_list, 1):
        console.print(f"  {idx} - {entity.capitalize()}")

    choice = Prompt.ask("Select").strip()
    try:
        entity = entities_list[int(choice) - 1]
        use_upsert = Confirm.ask("Use UPSERT mode?", default=True)
        upsert_field = (
            Prompt.ask("UPSERT field", default="email")
            if use_upsert
            else "email"
        )
        dry_run = Confirm.ask("Dry run?", default=False)

        ctx = click.Context(bulk_import)
        ctx.invoke(
            bulk_import,
            csv_file=csv_path,
            entity=entity,
            upsert=use_upsert,
            upsert_field=upsert_field,
            dry_run=dry_run,
        )
        input("[yellow]Press Enter to continue...[/yellow]")
    except (ValueError, IndexError):
        console.print("[red]Invalid input.[/red]")


if __name__ == "__main__":
    cli()

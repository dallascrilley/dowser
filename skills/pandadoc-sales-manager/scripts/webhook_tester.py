#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///

"""
Test PandaDoc webhook endpoints with payload validation and signature verification.

This script provides tools to test webhook endpoints, validate payloads, and verify
webhook signatures locally.

Usage:
    # Send test event to webhook
    uv run webhook_tester.py test \\
        --url "https://your-server.com/webhooks/pandadoc" \\
        --event "document_completed"

    # Test with signature verification
    uv run webhook_tester.py test \\
        --url "https://your-server.com/webhooks/pandadoc" \\
        --event "document_completed" \\
        --verify-signature

    # Test with custom payload
    uv run webhook_tester.py test \\
        --url "https://your-server.com/webhooks/pandadoc" \\
        --event "document_completed" \\
        --payload custom_payload.json

    # Run local webhook server for testing
    uv run webhook_tester.py serve --port 8000
"""

import argparse
import hashlib
import hmac
import json
import logging
import os
import sys
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, Optional
from pathlib import Path

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
WEBHOOK_SIGNATURE_HEADER = "X-Webhook-Signature"
WEBHOOK_TIMESTAMP_HEADER = "X-Webhook-Timestamp"

# Set up logging
logger = logging.getLogger(__name__)


class WebhookTestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for webhook testing server."""

    def do_POST(self) -> None:
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Log request
        logger.info(f"Received webhook: {self.path}")
        logger.debug(f"Headers: {dict(self.headers)}")
        logger.debug(f"Body: {body.decode('utf-8')}")

        # Parse JSON
        try:
            payload = json.loads(body.decode('utf-8'))
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            self.send_response(400)
            self.end_headers()
            return

        # Verify signature if present
        signature = self.headers.get(WEBHOOK_SIGNATURE_HEADER)
        timestamp = self.headers.get(WEBHOOK_TIMESTAMP_HEADER)

        if signature and timestamp:
            logger.info("Signature present - verify with your shared key")
            logger.info(f"Signature: {signature}")
            logger.info(f"Timestamp: {timestamp}")

        # Return success
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))

    def log_message(self, format, *args) -> None:
        """Suppress default logging."""
        logger.debug(format % args)


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


def generate_sample_payload(event_type: str) -> Dict[str, Any]:
    """Generate sample webhook payload.

    Args:
        event_type: Type of event

    Returns:
        Sample payload dictionary
    """
    base_payload = {
        "event_id": "evt_" + hashlib.md5(
            str(time.time()).encode()
        ).hexdigest()[:16],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
    }

    # Event-specific payloads
    if event_type == "document_completed":
        return {
            **base_payload,
            "data": {
                "document_id": "doc_abc123def456",
                "document_name": "Sales Proposal - Acme Corp",
                "status": "document.completed",
                "recipients": [
                    {
                        "email": "client@acme.com",
                        "name": "John Doe",
                        "role": "Client",
                        "status": "completed",
                        "signed_at": datetime.utcnow().isoformat() + "Z"
                    }
                ]
            }
        }

    elif event_type == "document_sent":
        return {
            **base_payload,
            "data": {
                "document_id": "doc_abc123def456",
                "document_name": "Sales Proposal - Acme Corp",
                "status": "document.sent",
                "recipients": [
                    {
                        "email": "client@acme.com",
                        "name": "John Doe",
                        "role": "Client",
                        "status": "sent",
                        "sent_at": datetime.utcnow().isoformat() + "Z"
                    }
                ]
            }
        }

    elif event_type == "document_viewed":
        return {
            **base_payload,
            "data": {
                "document_id": "doc_abc123def456",
                "document_name": "Sales Proposal - Acme Corp",
                "status": "document.viewed",
                "recipients": [
                    {
                        "email": "client@acme.com",
                        "name": "John Doe",
                        "role": "Client",
                        "status": "viewed",
                        "viewed_at": datetime.utcnow().isoformat() + "Z"
                    }
                ]
            }
        }

    elif event_type == "document_state_changed":
        return {
            **base_payload,
            "data": {
                "document_id": "doc_abc123def456",
                "old_status": "document.draft",
                "new_status": "document.sent",
                "changed_at": datetime.utcnow().isoformat() + "Z"
            }
        }

    else:
        # Generic payload
        return {
            **base_payload,
            "data": {
                "document_id": "doc_abc123def456",
                "message": f"Sample {event_type} event"
            }
        }


def generate_signature(payload: str, shared_key: str) -> str:
    """Generate webhook signature.

    Args:
        payload: JSON payload as string
        shared_key: Shared secret key

    Returns:
        Signature hex string
    """
    signature = hmac.new(
        shared_key.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_signature(
    payload: str,
    signature: str,
    shared_key: str
) -> bool:
    """Verify webhook signature.

    Args:
        payload: JSON payload as string
        signature: Signature to verify
        shared_key: Shared secret key

    Returns:
        True if signature is valid
    """
    expected = generate_signature(payload, shared_key)
    return hmac.compare_digest(signature, expected)


def load_payload_from_file(file_path: str) -> Dict[str, Any]:
    """Load webhook payload from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Payload dictionary
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def test_webhook(
    url: str,
    payload: Dict[str, Any],
    shared_key: Optional[str] = None,
    verify_signature_enabled: bool = False
) -> None:
    """Send test webhook and display results.

    Args:
        url: Webhook URL
        payload: Webhook payload
        shared_key: Optional shared key for signature
        verify_signature_enabled: Whether to include signature
    """
    payload_json = json.dumps(payload)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Timestamp": str(int(time.time())),
    }

    # Add signature if requested
    if verify_signature_enabled:
        if shared_key:
            signature = generate_signature(payload_json, shared_key)
            headers[WEBHOOK_SIGNATURE_HEADER] = signature
            logger.info(f"Generated signature: {signature}")
        else:
            logger.warning("Signature requested but no shared key provided")

    # Send request
    logger.info(f"Sending webhook to: {url}")
    logger.debug(f"Payload: {payload_json}")
    logger.debug(f"Headers: {headers}")

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )

        # Display results
        print()
        print("=" * 60)
        print("WEBHOOK TEST RESULT")
        print("=" * 60)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        print()
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()
        print("Response Body:")
        try:
            resp_json = response.json()
            print(json.dumps(resp_json, indent=2))
        except json.JSONDecodeError:
            print(response.text)
        print("=" * 60)

        if response.status_code == 200:
            logger.info("SUCCESS: Webhook received (200 OK)")
            return 0
        else:
            logger.warning(f"Unexpected status code: {response.status_code}")
            return 1

    except requests.exceptions.Timeout:
        logger.error("Webhook request timed out")
        return 1
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to webhook URL")
        return 1
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook request failed: {e}")
        return 1


def cmd_test(args: argparse.Namespace) -> int:
    """Test webhook endpoint.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        # Load or generate payload
        if args.payload:
            payload = load_payload_from_file(args.payload)
        else:
            payload = generate_sample_payload(args.event)

        # Test webhook
        return test_webhook(
            args.url,
            payload,
            shared_key=args.shared_key,
            verify_signature_enabled=args.verify_signature
        )

    except ValueError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


def cmd_serve(args: argparse.Namespace) -> int:
    """Run local webhook test server.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        server_address = ("127.0.0.1", args.port)
        httpd = HTTPServer(server_address, WebhookTestHandler)

        print()
        print("=" * 60)
        print("WEBHOOK TEST SERVER")
        print("=" * 60)
        print(f"Listening on: http://127.0.0.1:{args.port}")
        print()
        print("Use this URL in your webhook configuration:")
        print(f"  http://localhost:{args.port}/webhooks/pandadoc")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()

        httpd.serve_forever()
        return 0

    except KeyboardInterrupt:
        logger.info("Server stopped")
        return 0
    except OSError as e:
        logger.error(f"Server error: {e}")
        return 1


def cmd_sign(args: argparse.Namespace) -> int:
    """Generate webhook signature.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        if not args.payload:
            logger.error("--payload is required")
            return 1

        if not args.shared_key:
            logger.error("--shared-key is required")
            return 1

        # Load payload
        payload_dict = load_payload_from_file(args.payload)
        payload_json = json.dumps(payload_dict, separators=(',', ':'))

        # Generate signature
        signature = generate_signature(payload_json, args.shared_key)

        print()
        print("=" * 60)
        print("WEBHOOK SIGNATURE")
        print("=" * 60)
        print(f"Payload: {args.payload}")
        print(f"Signature: {signature}")
        print()
        print("Use this header:")
        print(f"  {WEBHOOK_SIGNATURE_HEADER}: {signature}")
        print("=" * 60)

        return 0

    except ValueError as e:
        logger.error(f"Error: {e}")
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify webhook signature.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        if not args.payload:
            logger.error("--payload is required")
            return 1

        if not args.signature:
            logger.error("--signature is required")
            return 1

        if not args.shared_key:
            logger.error("--shared-key is required")
            return 1

        # Load payload
        payload_dict = load_payload_from_file(args.payload)
        payload_json = json.dumps(payload_dict, separators=(',', ':'))

        # Verify signature
        is_valid = verify_signature(payload_json, args.signature, args.shared_key)

        print()
        print("=" * 60)
        print("SIGNATURE VERIFICATION")
        print("=" * 60)
        print(f"Payload: {args.payload}")
        print(f"Signature: {args.signature}")
        print(f"Valid: {'YES' if is_valid else 'NO'}")
        print("=" * 60)

        return 0 if is_valid else 1

    except ValueError as e:
        logger.error(f"Error: {e}")
        return 1


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Test PandaDoc webhook endpoints",
        epilog="""
Commands:
  test              Send test webhook to endpoint
  serve             Run local webhook test server
  sign              Generate webhook signature
  verify            Verify webhook signature

Examples:
  # Send test event
  python webhook_tester.py test \\
    --url "https://your-server.com/webhooks/pandadoc" \\
    --event "document_completed"

  # Test with signature
  python webhook_tester.py test \\
    --url "https://your-server.com/webhooks/pandadoc" \\
    --event "document_completed" \\
    --verify-signature \\
    --shared-key "your_shared_key"

  # Run local server
  python webhook_tester.py serve --port 8000

  # Generate signature
  python webhook_tester.py sign \\
    --payload payload.json \\
    --shared-key "your_shared_key"

  # Verify signature
  python webhook_tester.py verify \\
    --payload payload.json \\
    --signature "abc123..." \\
    --shared-key "your_shared_key"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test webhook endpoint")
    test_parser.add_argument(
        "--url",
        required=True,
        help="Webhook URL to test"
    )
    test_parser.add_argument(
        "--event",
        default="document_completed",
        help="Event type (default: document_completed)"
    )
    test_parser.add_argument(
        "--payload",
        help="Custom payload file (JSON)"
    )
    test_parser.add_argument(
        "--verify-signature",
        action="store_true",
        help="Include signature in request"
    )
    test_parser.add_argument(
        "--shared-key",
        help="Shared key for signature generation"
    )

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Run test server")
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)"
    )

    # Sign command
    sign_parser = subparsers.add_parser("sign", help="Generate signature")
    sign_parser.add_argument(
        "--payload",
        required=True,
        help="Payload file (JSON)"
    )
    sign_parser.add_argument(
        "--shared-key",
        required=True,
        help="Shared key"
    )

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify signature")
    verify_parser.add_argument(
        "--payload",
        required=True,
        help="Payload file (JSON)"
    )
    verify_parser.add_argument(
        "--signature",
        required=True,
        help="Signature to verify"
    )
    verify_parser.add_argument(
        "--shared-key",
        required=True,
        help="Shared key"
    )

    # Global options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    args = parse_arguments()
    configure_logging(args.verbose)

    try:
        if args.command == "test":
            return cmd_test(args)
        elif args.command == "serve":
            return cmd_serve(args)
        elif args.command == "sign":
            return cmd_sign(args)
        elif args.command == "verify":
            return cmd_verify(args)
        else:
            print("No command specified. Use -h for help.")
            return 1

    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

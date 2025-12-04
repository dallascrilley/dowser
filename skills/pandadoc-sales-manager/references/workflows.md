# PandaDoc Sales Workflows Guide

**Document Version:** 1.0
**Last Updated:** 2024-11-11

Complete guide to common sales workflows using PandaDoc API integration.

---

## Table of Contents

1. [Document Lifecycle Workflow](#document-lifecycle-workflow)
2. [Approval Workflow](#approval-workflow)
3. [Bulk Document Creation](#bulk-document-creation)
4. [Attachment Handling](#attachment-handling)
5. [Webhook Integration](#webhook-integration)
6. [CRM Integration](#crm-integration)
7. [Advanced Workflows](#advanced-workflows)

---

## Document Lifecycle Workflow

### Complete Proposal Creation and Sending

The most common workflow: create a proposal from template, send to customer, track completion.

**Step 1: Create Document from Template**

```python
import requests
import time
import json

API_KEY = "your_api_key"
BASE_URL = "https://api.pandadoc.com/public/v1"
HEADERS = {
    "Authorization": f"API-Key {API_KEY}",
    "Content-Type": "application/json"
}

def create_proposal(customer_data):
    """Create a proposal document from template."""

    payload = {
        "name": f"Proposal - {customer_data['customer_name']}",
        "template_uuid": "your_template_id",
        "recipients": [
            {
                "email": customer_data['customer_email'],
                "first_name": customer_data['first_name'],
                "last_name": customer_data['last_name'],
                "role": "Client"
            }
        ],
        "fields": {
            "Company Name": customer_data['customer_name'],
            "Proposal Amount": customer_data['amount'],
            "Effective Date": customer_data['date']
        },
        "metadata": {
            "opportunity_id": customer_data.get('opportunity_id'),
            "sales_rep": customer_data.get('sales_rep')
        }
    }

    response = requests.post(f"{BASE_URL}/documents", headers=HEADERS, json=payload)
    response.raise_for_status()

    document = response.json()
    print(f"Document created: {document['id']}")
    print(f"Status: {document['status']}")

    return document['id']
```

**Step 2: Wait for Draft Status (CRITICAL)**

```python
def wait_for_draft(document_id, timeout=60):
    """Poll until document is ready (document.draft status)."""

    max_attempts = timeout // 2  # Check every 2 seconds
    start_time = time.time()

    for attempt in range(max_attempts):
        time.sleep(2)

        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=HEADERS
        )
        response.raise_for_status()

        doc = response.json()
        elapsed = time.time() - start_time

        print(f"[{elapsed:.1f}s] Attempt {attempt + 1}: {doc['status']}")

        if doc['status'] == 'document.draft':
            print("Document ready!")
            return True

        if doc['status'].startswith('document.error'):
            raise Exception(f"Document creation failed: {doc['status']}")

    raise TimeoutError(f"Document not ready after {timeout} seconds")
```

**Step 3: Send Document**

```python
def send_proposal(document_id, subject="Review Proposal", message="Please review"):
    """Send document to recipients."""

    payload = {
        "subject": subject,
        "message": message,
        "silent": False  # Send email notifications
    }

    response = requests.post(
        f"{BASE_URL}/documents/{document_id}/send",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()

    result = response.json()
    print(f"Document sent successfully!")
    print(f"Recipients: {len(result.get('recipients', []))}")

    return result
```

**Step 4: Track Status**

```python
def track_document_status(document_id, poll_interval=30, max_duration=86400):
    """Track document status until completion."""

    start_time = time.time()

    while True:
        elapsed = time.time() - start_time

        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=HEADERS
        )
        response.raise_for_status()

        doc = response.json()
        status = doc['status']

        print(f"[{elapsed/3600:.1f}h] Status: {status}")

        # Check if completed
        if status in ['document.completed', 'document.declined', 'document.voided']:
            print(f"Document {status.split('.')[-1]}!")
            return doc

        # Check timeout
        if elapsed > max_duration:
            print(f"Timeout waiting for completion")
            return doc

        # Wait before next check
        time.sleep(poll_interval)
```

**Step 5: Download Document**

```python
def download_document(document_id, output_path):
    """Download completed document as PDF."""

    # Check status first
    response = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        headers=HEADERS
    )
    doc = response.json()

    if doc['status'] != 'document.completed':
        raise ValueError(f"Document not completed: {doc['status']}")

    # Download
    response = requests.get(
        f"{BASE_URL}/documents/{document_id}/download",
        headers={"Authorization": HEADERS["Authorization"]}
    )
    response.raise_for_status()

    # Save to file
    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"Document downloaded: {output_path}")
```

**Complete Workflow Example:**

```python
def complete_proposal_workflow():
    """Execute complete proposal workflow."""

    customer_data = {
        "customer_name": "Acme Corp",
        "customer_email": "john@acme.com",
        "first_name": "John",
        "last_name": "Doe",
        "amount": "$50,000",
        "date": "2024-01-15",
        "opportunity_id": "opp_12345",
        "sales_rep": "Jane Smith"
    }

    # Step 1: Create
    print("Creating proposal...")
    doc_id = create_proposal(customer_data)

    # Step 2: Wait for ready
    print("Waiting for document to be ready...")
    wait_for_draft(doc_id)

    # Step 3: Send
    print("Sending proposal...")
    send_proposal(doc_id)

    # Step 4: Track
    print("Tracking status...")
    final_doc = track_document_status(doc_id)

    # Step 5: Download
    if final_doc['status'] == 'document.completed':
        print("Downloading signed proposal...")
        download_document(doc_id, f"proposal_{doc_id}.pdf")

    print("Workflow complete!")
```

---

## Approval Workflow

### Multi-Step Approval Process

Document requires internal approval before sending to client.

**Workflow: Manager Reviews → Director Approves → Client Signs**

```python
def create_approval_workflow_document(customer_data):
    """Create document with multi-step approval."""

    payload = {
        "name": f"Approval Document - {customer_data['customer_name']}",
        "template_uuid": "your_template_id",
        "recipients": [
            # Step 1: Manager reviews first
            {
                "email": customer_data['manager_email'],
                "first_name": "Manager",
                "last_name": "Review",
                "role": "Manager",
                "signing_order": 1  # First to sign
            },
            # Step 2: Director approves
            {
                "email": customer_data['director_email'],
                "first_name": "Director",
                "last_name": "Approval",
                "role": "Director",
                "signing_order": 1  # Can sign in parallel with manager
            },
            # Step 3: Client signs
            {
                "email": customer_data['customer_email'],
                "first_name": customer_data['first_name'],
                "last_name": customer_data['last_name'],
                "role": "Client",
                "signing_order": 2  # Signs after internal approvals
            }
        ],
        "fields": {
            "Company Name": customer_data['customer_name'],
            "Amount": customer_data['amount']
        }
    }

    response = requests.post(f"{BASE_URL}/documents", headers=HEADERS, json=payload)
    response.raise_for_status()

    doc = response.json()
    print(f"Approval workflow document created: {doc['id']}")

    return doc['id']
```

**Monitor Approval Progress:**

```python
def get_approval_status(document_id):
    """Get approval status for each recipient."""

    response = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        headers=HEADERS
    )
    doc = response.json()

    print(f"Document: {doc['name']}")
    print(f"Overall Status: {doc['status']}")
    print("\nRecipient Status:")

    for recipient in doc.get('recipients', []):
        print(f"  {recipient['email']} ({recipient['role']})")
        print(f"    Status: {recipient.get('status', 'unknown')}")
        print(f"    Completed: {recipient.get('completed_at', 'Pending')}")
```

---

## Bulk Document Creation

### Create Multiple Proposals from Customer List

```python
import csv
import time
from typing import List, Dict

def load_customer_data(csv_file: str) -> List[Dict]:
    """Load customer data from CSV."""

    customers = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers.append(row)

    return customers

def bulk_create_documents(csv_file: str, template_id: str, batch_size=50):
    """Create multiple documents with rate limiting."""

    customers = load_customer_data(csv_file)
    total = len(customers)

    print(f"Creating {total} documents...")
    print(f"Batch size: {batch_size}")
    print(f"Rate limit: 10 req/min (1 req per 6 seconds)")

    created_docs = []
    failed_docs = []
    start_time = time.time()

    for i, customer in enumerate(customers):
        try:
            # Rate limiting: 10 req/min = 6 seconds between requests
            if i > 0:
                time.sleep(6)

            # Create document
            payload = {
                "name": f"Proposal - {customer['company_name']}",
                "template_uuid": template_id,
                "recipients": [
                    {
                        "email": customer['email'],
                        "first_name": customer['first_name'],
                        "last_name": customer['last_name'],
                        "role": "Client"
                    }
                ],
                "fields": {
                    "Company Name": customer['company_name'],
                    "Proposal Amount": customer['amount'],
                    "Effective Date": customer['date']
                },
                "metadata": {
                    "opportunity_id": customer.get('opportunity_id')
                }
            }

            response = requests.post(f"{BASE_URL}/documents", headers=HEADERS, json=payload)
            response.raise_for_status()

            doc = response.json()
            created_docs.append({
                "id": doc['id'],
                "customer": customer['company_name'],
                "status": "created"
            })

            elapsed = time.time() - start_time
            completed = i + 1
            remaining = total - completed
            rate = completed / elapsed if elapsed > 0 else 0
            eta_seconds = remaining / rate if rate > 0 else 0

            print(f"[{completed}/{total}] Created: {doc['id']} "
                  f"({customer['company_name']}) "
                  f"ETA: {eta_seconds/60:.1f}m")

        except Exception as e:
            print(f"ERROR creating document for {customer['company_name']}: {str(e)}")
            failed_docs.append({
                "customer": customer['company_name'],
                "error": str(e)
            })

    # Summary
    print(f"\nCompleted:")
    print(f"  Created: {len(created_docs)}")
    print(f"  Failed: {len(failed_docs)}")
    print(f"  Total time: {(time.time() - start_time)/60:.1f} minutes")

    # Save results
    with open('bulk_creation_results.json', 'w') as f:
        json.dump({
            "created": created_docs,
            "failed": failed_docs,
            "summary": {
                "total": total,
                "created": len(created_docs),
                "failed": len(failed_docs),
                "duration_seconds": int(time.time() - start_time)
            }
        }, f, indent=2)

    return created_docs, failed_docs
```

---

## Attachment Handling

### Add Attachments to Document

```python
def add_attachment_to_document(document_id: str, file_path: str, file_name: str):
    """Add file attachment to document."""

    # Step 1: Wait for draft status
    wait_for_draft(document_id)

    # Step 2: Upload attachment
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_name, f, 'application/octet-stream')
        }
        data = {
            'name': file_name
        }

        response = requests.post(
            f"{BASE_URL}/documents/{document_id}/attachments?upload",
            headers={"Authorization": HEADERS["Authorization"]},
            files=files,
            data=data
        )

    response.raise_for_status()
    print(f"Attachment added: {file_name}")

    return response.json()

def create_document_with_attachments(template_id, customer_data, attachments):
    """Create document and add attachments."""

    # Create document
    doc_id = create_proposal(customer_data)

    # Add attachments
    for attachment_path, attachment_name in attachments:
        print(f"Adding attachment: {attachment_name}")
        add_attachment_to_document(doc_id, attachment_path, attachment_name)

    return doc_id
```

---

## Webhook Integration

### Real-Time Document Status Updates

Instead of polling, webhooks notify your system of document events instantly.

**Setup Webhook:**

```python
def create_webhook_subscription(webhook_url: str):
    """Register webhook for real-time events."""

    payload = {
        "name": "Document Status Tracker",
        "url": webhook_url,
        "triggers": [
            "document_state_changed",
            "document_sent",
            "document_viewed",
            "document_completed",
            "document_declined"
        ],
        "payload": ["metadata", "fields", "recipients"]
    }

    response = requests.post(
        f"{BASE_URL}/webhook-subscriptions",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()

    webhook = response.json()
    print(f"Webhook created: {webhook['id']}")
    print(f"URL: {webhook_url}")

    return webhook['id']
```

**Webhook Handler:**

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SHARED_KEY = "your_webhook_shared_key"

def verify_webhook_signature(payload, signature):
    """Verify webhook signature from PandaDoc."""

    expected = hmac.new(
        WEBHOOK_SHARED_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)

@app.route('/webhooks/pandadoc', methods=['POST'])
def handle_webhook():
    """Handle incoming webhook from PandaDoc."""

    # Verify signature
    signature = request.headers.get('X-Pandadoc-Signature', '')
    payload = request.get_data(as_text=True)

    if not verify_webhook_signature(payload, signature):
        return {'error': 'Invalid signature'}, 401

    # Parse event
    event = request.json
    event_type = event.get('event_type')
    document_id = event['document']['id']
    status = event['document']['status']

    print(f"Event: {event_type}")
    print(f"Document: {document_id}")
    print(f"Status: {status}")

    # Handle event
    if event_type == 'document_completed':
        handle_document_completed(document_id, event)
    elif event_type == 'document_sent':
        handle_document_sent(document_id, event)
    elif event_type == 'document_declined':
        handle_document_declined(document_id, event)

    return {'success': True}, 200

def handle_document_completed(document_id, event):
    """Document signed and completed."""

    print(f"Document completed: {document_id}")
    # Update CRM, send confirmation email, etc.

def handle_document_sent(document_id, event):
    """Document sent to recipients."""

    print(f"Document sent: {document_id}")
    # Send internal notification, log event, etc.

def handle_document_declined(document_id, event):
    """Recipient declined to sign."""

    print(f"Document declined: {document_id}")
    # Alert sales team, trigger follow-up, etc.

if __name__ == '__main__':
    app.run(port=8080)
```

---

## CRM Integration

### Sync Document Status to CRM

```python
class CRMIntegration:
    """Integration with CRM system (Salesforce example)."""

    def __init__(self, salesforce_client):
        self.sf = salesforce_client

    def update_opportunity_with_document(self, opportunity_id, document_id):
        """Link PandaDoc document to CRM opportunity."""

        # Get document status
        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=HEADERS
        )
        doc = response.json()

        # Update Salesforce opportunity
        self.sf.Opportunity.update(
            opportunity_id,
            {
                'PandaDoc_Document_ID__c': document_id,
                'Document_Status__c': doc['status'],
                'Document_Sent_Date__c': doc.get('sent_at'),
                'Document_Updated_Date__c': doc.get('updated_at')
            }
        )

        print(f"Updated opportunity {opportunity_id} with document {document_id}")

    def sync_document_completion(self, document_id, opportunity_id):
        """When document is signed, update CRM opportunity."""

        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=HEADERS
        )
        doc = response.json()

        if doc['status'] == 'document.completed':
            # Move opportunity to closed/won stage
            self.sf.Opportunity.update(
                opportunity_id,
                {
                    'StageName': 'Closed Won',
                    'CloseDate': time.strftime('%Y-%m-%d'),
                    'Document_Signed_Date__c': doc.get('completed_at')
                }
            )

            print(f"Opportunity {opportunity_id} marked as closed won")

            # Download and attach signed document
            self.download_and_attach_document(opportunity_id, document_id)

    def download_and_attach_document(self, opportunity_id, document_id):
        """Download signed document and attach to opportunity."""

        # Download document
        response = requests.get(
            f"{BASE_URL}/documents/{document_id}/download",
            headers={"Authorization": HEADERS["Authorization"]}
        )
        pdf_content = response.content

        # Attach to Salesforce
        attachment = {
            'ParentId': opportunity_id,
            'Name': f'Signed_Proposal_{document_id}.pdf',
            'Body': base64.b64encode(pdf_content).decode()
        }

        self.sf.Attachment.create(attachment)
        print(f"Attached signed document to opportunity {opportunity_id}")
```

---

## Advanced Workflows

### Conditional Workflow Based on Response

```python
def smart_follow_up_workflow(document_id, customer_email):
    """Handle follow-up based on document status."""

    # Track document
    status_checks = 0
    max_checks = 60  # 60 checks = 10 hours at 10-minute intervals

    while status_checks < max_checks:
        status_checks += 1

        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=HEADERS
        )
        doc = response.json()

        if doc['status'] == 'document.completed':
            # Document signed - send congratulations email
            print(f"Document signed by {customer_email}!")
            send_email(customer_email, "Congratulations!", "Thank you for signing!")
            break

        elif doc['status'] == 'document.viewed':
            # Customer viewed but didn't sign
            # Check if viewed for more than 2 hours
            if status_checks > 12:
                print(f"Sending reminder to {customer_email}...")
                send_email(customer_email, "Reminder", "Please sign the document")

        elif doc['status'] == 'document.declined':
            # Document declined
            print(f"Document declined by {customer_email}")
            send_email(customer_email, "Next Steps", "Let's discuss alternatives")
            break

        # Wait 10 minutes before next check
        time.sleep(600)
```

---

## Workflow Summary Table

| Workflow | Duration | Complexity | Best For |
|----------|----------|-----------|----------|
| Document Lifecycle | Hours/Days | Medium | Standard proposals |
| Approval Process | Hours/Days | High | Complex deals |
| Bulk Creation | Minutes/Hours | High | Sales campaigns |
| Webhook Integration | Real-time | Medium | Live tracking |
| CRM Sync | Real-time | High | Integrated systems |
| Conditional Follow-up | Hours/Days | High | Smart automation |

---

## Best Practices

1. **Always poll for draft status** before sending documents
2. **Implement rate limiting** (6+ seconds between requests for sandbox)
3. **Use webhooks** instead of polling for production systems
4. **Log all operations** for audit trail and debugging
5. **Handle errors gracefully** with appropriate retries
6. **Test with sandbox** environment before production
7. **Monitor document status** for completion or decline
8. **Download documents** only when status is "completed"

---

## See Also

- [Endpoints Reference](./endpoints-reference.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Webhook Integration Guide](./webhook-integration-guide.md)

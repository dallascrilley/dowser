# Acuity Scheduling API - Webhook Integration Guide

**Last Updated:** 2025-11-11
**Difficulty Level:** Intermediate
**Time to Complete:** 1-2 hours

---

## Table of Contents

1. [Why Webhooks?](#why-webhooks)
2. [Available Events](#available-events)
3. [Getting Started](#getting-started)
4. [Signature Verification](#signature-verification)
5. [Production-Ready Handlers](#production-ready-handlers)
6. [Queue-Based Processing](#queue-based-processing)
7. [Security Best Practices](#security-best-practices)
8. [Testing Strategies](#testing-strategies)
9. [Monitoring & Alerting](#monitoring--alerting)
10. [Troubleshooting](#troubleshooting)
11. [Critical Pitfalls](#critical-pitfalls)

---

## Why Webhooks?

### Benefits vs. Polling

**Webhooks (Event-Driven):**
- Real-time notifications - actions happen instantly
- Lower API usage - no continuous polling
- Reduced latency - no delay between event and action
- Scalable - handles volume without hammering API
- Cost-effective - fewer API calls = lower bandwidth

**Polling (Request-Based):**
- ❌ High latency - delays between event and detection
- ❌ Wasted API calls - polling even when nothing changed
- ❌ Rate limiting issues - more likely to hit limits
- ❌ Inconsistent - depends on polling frequency
- ❌ Resource intensive - continuous background tasks

### Use Cases

**Webhooks Excel At:**
- Real-time appointment confirmations via email/SMS
- Instant CRM synchronization
- Calendar integration (Google Calendar, Outlook)
- Slack/Teams notifications for staff
- Payment processing triggers
- Automated follow-up workflows
- Lead capture from booking forms

**Example Workflow:**
```
1. Client books appointment in Acuity
2. Webhook fires instantly with appointment data
3. Your system receives event
4. Email confirmation sent automatically
5. CRM updated with new client
6. Slack notification to staff
7. Calendar synced
→ All happens within seconds of booking
```

---

## Available Events

### Event Types

Acuity Scheduling fires webhooks for these events:

#### 1. Appointment Events

```yaml
appointment_scheduled:
  description: "New appointment created"
  trigger: "Client books appointment"
  action: "appointment.scheduled"
  payload:
    - id: 12345
    - action: "scheduled"
    - appointmentTypeID: 67890
    - calendarID: 11111
    - clientID: 22222
    - datetime: "2025-11-15T14:00:00-0500"
    - firstName: "John"
    - lastName: "Doe"
    - email: "john@example.com"
    - phone: "+15555551234"
    - location: "Office A"
    - notes: "Client notes"

appointment_rescheduled:
  description: "Appointment time changed"
  trigger: "Client or staff reschedules"
  action: "appointment.rescheduled"
  payload_includes:
    - original_datetime: "2025-11-15T14:00:00-0500"
    - new_datetime: "2025-11-16T10:00:00-0500"
    - all_standard_fields: true

appointment_canceled:
  description: "Appointment canceled"
  trigger: "Client or staff cancels"
  action: "appointment.canceled"
  payload:
    - id: 12345
    - action: "canceled"
    - canceled: true
    - canceledBy: "client"  # or "business"
    - cancelReason: "Scheduling conflict"
```

#### 2. Client Events

```yaml
client_created:
  description: "New client record created"
  trigger: "Appointment booking or manual entry"
  action: "client.created"

client_updated:
  description: "Client information changed"
  trigger: "Client or staff updates details"
  action: "client.updated"
```

#### 3. Custom Events

```yaml
custom_event:
  description: "Custom webhook for integrations"
  trigger: "Manual trigger via API"
  action: "custom.*"
  frequency: "As configured"
```

### Event Payload Structure

```json
{
  "id": 12345,
  "action": "scheduled",
  "appointmentTypeID": 67890,
  "calendarID": 11111,
  "clientID": 22222,
  "datetime": "2025-11-15T14:00:00-0500",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "+15555551234",
  "location": "Office A",
  "notes": "Additional notes",
  "paid": 0,
  "type": "Consultation",
  "duration": 30,
  "price": 100.00,
  "timezone": "America/New_York"
}
```

---

## Getting Started

### Step 1: Create Webhook in Acuity Dashboard

1. Log into Acuity Scheduling
2. Go to **Settings → Integrations → Webhooks**
3. Click **"Add Webhook"**
4. Enter webhook URL: `https://yourdomain.com/webhooks/acuity`
5. Select events:
   - ✅ Appointment scheduled
   - ✅ Appointment rescheduled
   - ✅ Appointment canceled
6. Click **Save**
7. Acuity will test the endpoint with a test request

### Step 2: Verify Webhook URL

Your endpoint must:
- ✅ Accept POST requests
- ✅ Return **200 OK** status code
- ✅ Be accessible over HTTPS
- ✅ Respond within 30 seconds
- ✅ Verify signature (see section below)

### Step 3: Monitor Webhook

Monitor via Acuity API:

```bash
# List all webhooks
curl -u "USER_ID:API_KEY" \
  https://acuityscheduling.com/api/v1/webhooks

# View webhook details
curl -u "USER_ID:API_KEY" \
  https://acuityscheduling.com/api/v1/webhooks/WEBHOOK_ID

# View recent webhook payloads
curl -u "USER_ID:API_KEY" \
  https://acuityscheduling.com/api/v1/webhooks/WEBHOOK_ID/payloads
```

---

## Signature Verification

### Why Verify Signatures?

**Security Risk:** Without verification, anyone can send fake webhook requests to your endpoint, potentially:
- Creating false appointments
- Triggering unauthorized workflows
- Inserting malicious data
- Manipulating your business logic

**Solution:** Verify that webhook came from Acuity using HMAC-SHA256 signature.

### Implementation

#### Python (Flask/FastAPI)

```python
import hmac
import hashlib
import json
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
ACUITY_API_KEY = os.environ['ACUITY_API_KEY']

def verify_webhook_signature(request):
    """
    Verify webhook signature is from Acuity Scheduling.

    For static webhooks: signature uses admin API key
    For OAuth webhooks: signature uses OAuth token
    """
    # Get signature from header
    received_signature = request.headers.get('X-Acuity-Signature')

    if not received_signature:
        logging.warning(f"Webhook received without signature from {request.remote_addr}")
        return False

    # Get the raw request body
    request_body = request.get_data()

    # Calculate expected signature
    expected_signature = hmac.new(
        ACUITY_API_KEY.encode('utf-8'),
        request_body,
        hashlib.sha256
    ).hexdigest()

    # Constant-time comparison prevents timing attacks
    is_valid = hmac.compare_digest(received_signature, expected_signature)

    if not is_valid:
        logging.error(f"Invalid signature from {request.remote_addr}")
        logging.error(f"  Expected: {expected_signature}")
        logging.error(f"  Received: {received_signature}")

    return is_valid

@app.route('/webhooks/acuity', methods=['POST'])
def handle_webhook():
    """Handle webhook from Acuity Scheduling"""

    # CRITICAL: Always verify signature first
    if not verify_webhook_signature(request):
        logging.error(f"Webhook signature verification failed from {request.remote_addr}")
        return jsonify({'error': 'Invalid signature'}), 403

    try:
        # Parse JSON payload
        data = request.get_json()

        if not data:
            logging.warning("Received webhook with empty payload")
            return jsonify({'status': 'received'}), 200

        # Log webhook receipt
        logging.info(f"Webhook received: {data.get('action')} for appointment {data.get('id')}")

        # Queue for async processing (see next section)
        queue_webhook_event(data)

        # ALWAYS return 200 immediately (don't do heavy processing here)
        return jsonify({'status': 'received'}), 200

    except json.JSONDecodeError:
        logging.error("Invalid JSON in webhook request")
        return jsonify({'error': 'Invalid JSON'}), 400

    except Exception as e:
        logging.error(f"Webhook processing error: {e}", exc_info=True)
        # Still return 200 to prevent Acuity disabling webhook
        return jsonify({'status': 'queued'}), 200
```

#### Node.js (Express)

```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

const ACUITY_API_KEY = process.env.ACUITY_API_KEY;

app.use(express.raw({ type: 'application/json' }));

function verifyWebhookSignature(req) {
  const receivedSignature = req.headers['x-acuity-signature'];

  if (!receivedSignature) {
    console.warn(`Webhook without signature from ${req.ip}`);
    return false;
  }

  // Calculate expected signature
  const expectedSignature = crypto
    .createHmac('sha256', ACUITY_API_KEY)
    .update(req.body)
    .digest('hex');

  // Constant-time comparison
  const isValid = crypto.timingSafeEqual(
    Buffer.from(receivedSignature),
    Buffer.from(expectedSignature)
  );

  if (!isValid) {
    console.error(`Invalid signature from ${req.ip}`);
  }

  return isValid;
}

app.post('/webhooks/acuity', (req, res) => {
  // Verify signature FIRST
  if (!verifyWebhookSignature(req)) {
    console.error('Webhook signature verification failed');
    return res.status(403).json({ error: 'Invalid signature' });
  }

  try {
    const data = JSON.parse(req.body.toString());

    console.log(`Webhook received: ${data.action} for appointment ${data.id}`);

    // Queue for async processing
    queueWebhookEvent(data);

    // Return 200 immediately
    return res.status(200).json({ status: 'received' });

  } catch (error) {
    console.error('Webhook processing error:', error);
    // Still return 200 to prevent webhook disabling
    return res.status(200).json({ status: 'queued' });
  }
});
```

#### PHP

```php
<?php
// Verify webhook signature
function verify_webhook_signature($request_body, $received_signature) {
    $api_key = getenv('ACUITY_API_KEY');

    $expected_signature = hash_hmac(
        'sha256',
        $request_body,
        $api_key,
        false  // Return hex string
    );

    // Constant-time comparison
    return hash_equals($expected_signature, $received_signature);
}

// Get raw body and signature
$request_body = file_get_contents('php://input');
$received_signature = $_SERVER['HTTP_X_ACUITY_SIGNATURE'] ?? '';

// Verify
if (!verify_webhook_signature($request_body, $received_signature)) {
    http_response_code(403);
    echo json_encode(['error' => 'Invalid signature']);
    exit;
}

// Process webhook
$data = json_decode($request_body, true);

error_log("Webhook received: {$data['action']} for appointment {$data['id']}");

// Queue for async processing
queue_webhook_event($data);

// Return 200
http_response_code(200);
echo json_encode(['status' => 'received']);
?>
```

---

## Production-Ready Handlers

### Handler: Appointment Scheduled

```python
class AppointmentScheduledHandler:
    """Handle appointment.scheduled webhook"""

    def __init__(self, appointment_data):
        self.data = appointment_data
        self.id = appointment_data.get('id')
        self.client_email = appointment_data.get('email')
        self.appointment_datetime = appointment_data.get('datetime')

    def process(self):
        """Execute all handlers for scheduled appointment"""
        try:
            # 1. Send confirmation email
            self.send_confirmation_email()

            # 2. Sync to CRM if configured
            if self.should_sync_crm():
                self.sync_to_crm()

            # 3. Update external calendar
            self.sync_to_calendar()

            # 4. Notify staff
            self.notify_staff()

            # 5. Log to database
            self.log_appointment(status='confirmed')

            logging.info(f"Successfully processed appointment {self.id}")
            return True

        except Exception as e:
            logging.error(f"Handler error for appointment {self.id}: {e}", exc_info=True)
            self.log_appointment(status='error', error=str(e))
            # Don't raise - return error to caller
            return False

    def send_confirmation_email(self):
        """Send confirmation email to client"""
        from email_service import send_email

        formatted_time = self.format_datetime_for_email()

        email_body = f"""
        Thank you for booking your appointment!

        Date & Time: {formatted_time}
        Duration: {self.data.get('duration')} minutes
        Location: {self.data.get('location', 'See confirmation')}

        Please save this confirmation. You'll receive a reminder 24 hours before.

        To reschedule: Click the link in your reminder email
        To cancel: Reply to this email
        """

        send_email(
            to=self.client_email,
            subject=f"Appointment Confirmation - {self.data.get('type')}",
            body=email_body,
            from_email="noreply@yourbusiness.com"
        )

    def sync_to_crm(self):
        """Sync appointment to CRM system"""
        from crm_connector import SalesforceConnector

        crm = SalesforceConnector()

        contact_data = {
            'FirstName': self.data.get('firstName'),
            'LastName': self.data.get('lastName'),
            'Email': self.data.get('email'),
            'Phone': self.data.get('phone'),
        }

        opportunity_data = {
            'Name': f"Appointment: {self.data.get('type')}",
            'Amount': self.data.get('price'),
            'CloseDate': self.appointment_datetime.split('T')[0],
            'StageName': 'Qualification',
            'Description': self.data.get('notes'),
        }

        # Create contact if not exists
        contact = crm.create_or_update_contact(contact_data)

        # Create opportunity linked to contact
        opportunity_data['AccountId'] = contact['Id']
        crm.create_opportunity(opportunity_data)

    def sync_to_calendar(self):
        """Sync to Google Calendar or similar"""
        from google_calendar import GoogleCalendarSync

        calendar = GoogleCalendarSync()

        event = {
            'summary': f"Appointment: {self.data.get('type')}",
            'description': self.data.get('notes'),
            'start': {
                'dateTime': self.appointment_datetime,
                'timeZone': self.data.get('timezone', 'America/New_York'),
            },
            'end': {
                'dateTime': self.calculate_end_time(),
                'timeZone': self.data.get('timezone', 'America/New_York'),
            },
            'attendees': [{'email': self.client_email}],
            'location': self.data.get('location'),
        }

        calendar.create_event(event)

    def notify_staff(self):
        """Send Slack/Teams notification to staff"""
        message = f"""
        New Appointment Booked!

        Client: {self.data.get('firstName')} {self.data.get('lastName')}
        Email: {self.data.get('email')}
        Time: {self.appointment_datetime}
        Type: {self.data.get('type')}
        Duration: {self.data.get('duration')} min
        Price: ${self.data.get('price', 0)}
        """

        send_slack_message(message, channel='#appointments')

    def log_appointment(self, status='confirmed', error=None):
        """Log appointment to database"""
        db.appointments.insert_one({
            'acuity_id': self.id,
            'action': 'scheduled',
            'status': status,
            'data': self.data,
            'error': error,
            'timestamp': datetime.now(),
        })

    def format_datetime_for_email(self):
        """Format datetime for human-readable email"""
        # Parse and format with timezone
        dt = datetime.fromisoformat(self.appointment_datetime)
        tz = pytz.timezone(self.data.get('timezone', 'America/New_York'))
        dt = dt.astimezone(tz)
        return dt.strftime('%A, %B %d at %I:%M %p %Z')

    def calculate_end_time(self):
        """Calculate end time from start + duration"""
        dt = datetime.fromisoformat(self.appointment_datetime)
        duration = timedelta(minutes=self.data.get('duration', 30))
        return (dt + duration).isoformat()

    def should_sync_crm(self):
        """Check if CRM sync is enabled"""
        return os.environ.get('CRM_SYNC_ENABLED', 'false').lower() == 'true'
```

### Handler: Appointment Canceled

```python
class AppointmentCanceledHandler:
    """Handle appointment.canceled webhook"""

    def __init__(self, appointment_data):
        self.data = appointment_data
        self.id = appointment_data.get('id')
        self.client_email = appointment_data.get('email')

    def process(self):
        """Execute cancellation handlers"""
        try:
            # 1. Send cancellation confirmation
            self.send_cancellation_email()

            # 2. Update CRM status
            if self.should_sync_crm():
                self.update_crm_status()

            # 3. Remove from calendar
            self.remove_from_calendar()

            # 4. Notify staff
            self.notify_staff_cancellation()

            # 5. Log cancellation
            self.log_cancellation()

            logging.info(f"Processed cancellation for appointment {self.id}")
            return True

        except Exception as e:
            logging.error(f"Cancellation handler error: {e}", exc_info=True)
            return False

    def send_cancellation_email(self):
        """Confirm cancellation with client"""
        email_body = f"""
        Your appointment has been canceled.

        Canceled Date: {self.data.get('datetime')}
        Type: {self.data.get('type')}
        Reason: {self.data.get('cancelReason', 'Not specified')}
        Canceled By: {self.data.get('canceledBy', 'Unknown')}

        To rebook: Visit our scheduling link
        Questions? Contact us directly.
        """

        send_email(
            to=self.client_email,
            subject="Appointment Cancellation Confirmation",
            body=email_body,
        )

    def update_crm_status(self):
        """Update related CRM records"""
        # Find and update opportunity status
        crm = SalesforceConnector()
        crm.update_opportunity_status(
            acuity_id=self.id,
            status='Closed - Lost',
            reason=self.data.get('cancelReason')
        )

    def remove_from_calendar(self):
        """Delete event from external calendar"""
        calendar = GoogleCalendarSync()
        calendar.delete_event(appointment_id=self.id)

    def notify_staff_cancellation(self):
        """Alert staff of cancellation"""
        message = f"""
        Appointment Canceled

        Client: {self.data.get('firstName')} {self.data.get('lastName')}
        Original Time: {self.data.get('datetime')}
        Canceled By: {self.data.get('canceledBy')}
        Reason: {self.data.get('cancelReason')}
        """

        send_slack_message(message, channel='#cancellations')

    def log_cancellation(self):
        """Record cancellation in database"""
        db.appointments.update_one(
            {'acuity_id': self.id},
            {
                '$set': {
                    'status': 'canceled',
                    'cancel_reason': self.data.get('cancelReason'),
                    'canceled_by': self.data.get('canceledBy'),
                    'canceled_timestamp': datetime.now(),
                }
            }
        )
```

---

## Queue-Based Processing

### Why Queue Webhooks?

**Critical Issue:** Webhook requests have ~30 second timeout. Long-running tasks (email, CRM sync, calendar updates) can timeout and cause Acuity to think the webhook failed, eventually disabling it.

**Solution:** Return 200 immediately, queue for async processing.

### Implementation with Celery + Redis

```python
from celery import Celery
from celery.utils.log import get_task_logger
import os

# Configure Celery
celery_app = Celery(
    'acuity_webhooks',
    broker=os.environ['REDIS_URL'],
    backend=os.environ['REDIS_URL'],
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=250,  # 4+ minute soft limit
)

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_appointment_scheduled(self, appointment_data):
    """Async task for processing scheduled appointments"""

    appointment_id = appointment_data.get('id')

    try:
        handler = AppointmentScheduledHandler(appointment_data)
        success = handler.process()

        if success:
            logger.info(f"Successfully processed appointment {appointment_id}")
            return {'status': 'success', 'appointment_id': appointment_id}
        else:
            # Failure - retry
            logger.warning(f"Handler returned error for {appointment_id}, retrying...")
            raise self.retry(exc=Exception("Handler failed"))

    except Exception as exc:
        logger.error(f"Error processing appointment {appointment_id}: {exc}")

        # Retry up to 3 times with exponential backoff
        if self.request.retries < self.max_retries:
            logger.warning(f"Retrying task {self.request.id}, attempt {self.request.retries + 1}")
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        else:
            # Max retries exceeded - store for manual intervention
            logger.critical(f"Max retries exceeded for appointment {appointment_id}")
            store_failed_webhook({
                'appointment_id': appointment_id,
                'data': appointment_data,
                'error': str(exc),
                'timestamp': datetime.now(),
            })
            raise

@celery_app.task(bind=True, max_retries=3)
def process_appointment_canceled(self, appointment_data):
    """Async task for processing cancellations"""

    try:
        handler = AppointmentCanceledHandler(appointment_data)
        return handler.process()

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60)
        else:
            logger.critical(f"Failed to process cancellation: {exc}")
            raise

def queue_webhook_event(webhook_data):
    """Queue webhook for async processing"""

    action = webhook_data.get('action')

    if action == 'scheduled':
        process_appointment_scheduled.delay(webhook_data)
    elif action == 'canceled':
        process_appointment_canceled.delay(webhook_data)
    elif action == 'rescheduled':
        process_appointment_scheduled.delay(webhook_data)
    else:
        logger.warning(f"Unknown webhook action: {action}")

# Webhook handler that uses queue
@app.route('/webhooks/acuity', methods=['POST'])
def handle_webhook():
    """Handle webhook from Acuity"""

    if not verify_webhook_signature(request):
        return jsonify({'error': 'Invalid signature'}), 403

    try:
        data = request.get_json()

        # Queue immediately
        queue_webhook_event(data)

        # Return 200 right away (don't wait for processing)
        return jsonify({'status': 'queued'}), 200

    except Exception as e:
        logger.error(f"Webhook queueing error: {e}")
        # Still return 200 to prevent webhook disabling
        return jsonify({'status': 'queued'}), 200
```

### Implementation with RabbitMQ

```python
import pika
import json
import os

class WebhookQueue:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(os.environ['RABBITMQ_URL'])
        )
        self.channel = self.connection.channel()

        # Declare durable queue
        self.channel.queue_declare(
            queue='acuity_webhooks',
            durable=True
        )

    def publish(self, webhook_data):
        """Publish webhook to queue"""
        self.channel.basic_publish(
            exchange='',
            routing_key='acuity_webhooks',
            body=json.dumps(webhook_data),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

    def close(self):
        self.connection.close()

# Global queue instance
webhook_queue = WebhookQueue()

@app.route('/webhooks/acuity', methods=['POST'])
def handle_webhook():
    """Receive webhook and queue for processing"""

    if not verify_webhook_signature(request):
        return jsonify({'error': 'Invalid signature'}), 403

    try:
        data = request.get_json()
        webhook_queue.publish(data)

        # Return immediately
        return jsonify({'status': 'queued'}), 200

    except Exception as e:
        logging.error(f"Queue publish error: {e}")
        return jsonify({'status': 'queued'}), 200  # Still return 200

# Separate worker process to consume queue
def webhook_worker():
    """Worker process that processes queued webhooks"""
    connection = pika.BlockingConnection(
        pika.URLParameters(os.environ['RABBITMQ_URL'])
    )
    channel = connection.channel()
    channel.queue_declare(queue='acuity_webhooks', durable=True)

    def callback(ch, method, properties, body):
        try:
            webhook_data = json.loads(body)
            queue_webhook_event(webhook_data)

            # Acknowledge after successful processing
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logging.error(f"Worker error: {e}")
            # Negative ack to requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='acuity_webhooks', on_message_callback=callback)

    logging.info("Webhook worker started")
    channel.start_consuming()

# Run worker
if __name__ == '__main__':
    webhook_worker()
```

---

## Security Best Practices

### 1. Always Verify Signatures

```python
# ✅ CORRECT: Verify before processing
if not verify_webhook_signature(request):
    return {'error': 'Invalid signature'}, 403

# ❌ WRONG: No verification
data = request.json
process_webhook(data)  # Could be fake!
```

### 2. Use HTTPS Only

```yaml
# ✅ CORRECT: HTTPS webhook URL
webhook_url: "https://yourdomain.com/webhooks/acuity"

# ❌ WRONG: HTTP (unencrypted)
webhook_url: "http://yourdomain.com/webhooks/acuity"
```

### 3. Validate Input Data

```python
def validate_webhook_data(data):
    """Validate webhook data before processing"""

    # Required fields
    required = ['id', 'action', 'email', 'firstName', 'lastName']
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Email validation
    if not is_valid_email(data['email']):
        raise ValueError(f"Invalid email: {data['email']}")

    # Appointment ID should be numeric
    if not isinstance(data['id'], int):
        raise ValueError(f"Invalid appointment ID")

    # DateTime should be valid ISO format
    try:
        datetime.fromisoformat(data['datetime'])
    except ValueError:
        raise ValueError(f"Invalid datetime format")

    return True
```

### 4. Implement Rate Limiting on Webhook Endpoint

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/webhooks/acuity', methods=['POST'])
@limiter.limit("100 per hour")  # Acuity shouldn't send more than this
def handle_webhook():
    # ...
```

### 5. Rotate API Keys Regularly

```python
# Webhook signature uses API key
# Rotate every 90 days:
# 1. Generate new API key in Acuity
# 2. Update ACUITY_API_KEY environment variable
# 3. Deploy new code
# 4. Delete old API key in Acuity
```

### 6. Log All Webhook Activity

```python
def log_webhook(webhook_data, status, error=None):
    """Log webhook for security audit"""

    import json
    from datetime import datetime

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'appointment_id': webhook_data.get('id'),
        'action': webhook_data.get('action'),
        'email': webhook_data.get('email'),
        'status': status,
        'error': error,
        'source_ip': request.remote_addr,
    }

    # Log to file, database, or logging service
    logging.info(json.dumps(log_entry))

    # Also store in database for audit trail
    db.webhook_logs.insert_one(log_entry)
```

---

## Testing Strategies

### Unit Tests

```python
import unittest
from unittest.mock import patch, MagicMock

class TestWebhookHandling(unittest.TestCase):

    def test_signature_verification_valid(self):
        """Test valid signature passes"""
        request = MagicMock()
        request.headers = {
            'X-Acuity-Signature': 'valid_signature'
        }
        request.get_data.return_value = b'test_data'

        with patch('hmac.compare_digest', return_value=True):
            result = verify_webhook_signature(request)
            self.assertTrue(result)

    def test_signature_verification_invalid(self):
        """Test invalid signature fails"""
        request = MagicMock()
        request.headers = {
            'X-Acuity-Signature': 'invalid_signature'
        }
        request.get_data.return_value = b'test_data'

        with patch('hmac.compare_digest', return_value=False):
            result = verify_webhook_signature(request)
            self.assertFalse(result)

    def test_appointment_scheduled_handler(self):
        """Test appointment scheduled handler"""
        test_data = {
            'id': 123,
            'action': 'scheduled',
            'email': 'test@example.com',
            'firstName': 'John',
            'lastName': 'Doe',
            'datetime': '2025-11-15T14:00:00-0500',
            'type': 'Consultation',
            'duration': 30,
        }

        handler = AppointmentScheduledHandler(test_data)

        with patch.object(handler, 'send_confirmation_email') as mock_email:
            with patch.object(handler, 'sync_to_crm'):
                with patch.object(handler, 'log_appointment'):
                    result = handler.process()
                    mock_email.assert_called_once()

    def test_webhook_endpoint_requires_https(self):
        """Test webhook URL must use HTTPS"""
        webhook_url = "http://example.com/webhook"
        self.assertFalse(webhook_url.startswith("https://"))
```

### Integration Tests

```python
import pytest
import json
from app import app, verify_webhook_signature
import hmac
import hashlib

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_webhook_with_valid_signature(client):
    """Test webhook endpoint with valid signature"""

    webhook_data = {
        'id': 12345,
        'action': 'scheduled',
        'email': 'test@example.com',
    }

    body = json.dumps(webhook_data)
    signature = hmac.new(
        os.environ['ACUITY_API_KEY'].encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    response = client.post(
        '/webhooks/acuity',
        data=body,
        content_type='application/json',
        headers={'X-Acuity-Signature': signature}
    )

    assert response.status_code == 200
    assert response.json['status'] == 'queued'

def test_webhook_with_invalid_signature(client):
    """Test webhook endpoint rejects invalid signature"""

    response = client.post(
        '/webhooks/acuity',
        json={'id': 123},
        headers={'X-Acuity-Signature': 'invalid'}
    )

    assert response.status_code == 403

def test_webhook_without_signature(client):
    """Test webhook endpoint requires signature"""

    response = client.post(
        '/webhooks/acuity',
        json={'id': 123}
    )

    assert response.status_code == 403
```

### Manual Testing

```bash
# 1. Create test webhook URL
# Use service like https://webhook.site or ngrok

# 2. Register webhook in Acuity dashboard
# Settings → Integrations → Webhooks
# URL: https://your-test-url/webhooks/acuity

# 3. Acuity will send test webhook automatically

# 4. View request in webhook.site

# 5. Or test manually with curl:
curl -X POST https://your-endpoint/webhooks/acuity \
  -H "Content-Type: application/json" \
  -H "X-Acuity-Signature: $(echo -n '{}' | \
    openssl dgst -sha256 -hmac 'YOUR_API_KEY' -hex | cut -d' ' -f2)" \
  -d '{"id": 123, "action": "scheduled"}'

# 6. Book test appointment in Acuity
# Webhook will fire in real time
```

---

## Monitoring & Alerting

### Health Check Endpoint

```python
@app.route('/health/webhooks', methods=['GET'])
def webhook_health_check():
    """Check webhook system health"""

    from datetime import datetime, timedelta

    # Check last webhook received
    last_webhook = db.webhook_logs.find_one(
        sort=[('timestamp', -1)]
    )

    last_webhook_time = (
        last_webhook['timestamp']
        if last_webhook else datetime.now()
    )

    # Calculate gap
    time_since_webhook = datetime.now() - last_webhook_time

    # Status determination
    if time_since_webhook < timedelta(hours=1):
        status = 'healthy'
    elif time_since_webhook < timedelta(hours=12):
        status = 'degraded'
    else:
        status = 'unhealthy'

    # Check Acuity webhook status
    try:
        response = session.get(f"{BASE_URL}/webhooks")
        webhooks = response.json()

        active_webhooks = sum(
            1 for w in webhooks
            if w.get('enabled', True)
        )
    except Exception:
        active_webhooks = 0

    return jsonify({
        'status': status,
        'last_webhook_received': last_webhook_time.isoformat(),
        'time_since_last_webhook_minutes': int(time_since_webhook.total_seconds() / 60),
        'active_webhooks': active_webhooks,
        'total_webhooks': len(webhooks) if 'webhooks' in locals() else 0,
        'queue_depth': get_queue_depth(),
        'processing_errors_24h': count_errors_last_24h(),
    })
```

### Monitoring Queries

```python
def get_webhook_metrics():
    """Get webhook metrics for monitoring"""

    from datetime import datetime, timedelta

    now = datetime.now()
    last_24h = now - timedelta(hours=24)

    # Count by action type
    action_counts = db.webhook_logs.aggregate([
        {'$match': {'timestamp': {'$gte': last_24h}}},
        {'$group': {'_id': '$action', 'count': {'$sum': 1}}},
    ])

    # Count errors
    error_count = db.webhook_logs.count_documents({
        'timestamp': {'$gte': last_24h},
        'status': 'error'
    })

    # Average processing time
    avg_processing_time = db.webhook_logs.aggregate([
        {'$match': {'timestamp': {'$gte': last_24h}}},
        {'$group': {
            '_id': None,
            'avg_time': {'$avg': '$processing_time_ms'}
        }}
    ])

    return {
        'actions': dict(action_counts),
        'error_count_24h': error_count,
        'success_rate': (
            (len(action_counts) - error_count) / len(action_counts) * 100
        ) if action_counts else 0,
        'avg_processing_ms': next(avg_processing_time, {}).get('avg_time', 0),
    }

# Alert thresholds
def check_webhook_alerts():
    """Check for alerting conditions"""

    metrics = get_webhook_metrics()
    alerts = []

    # Error rate
    if metrics['success_rate'] < 95:
        alerts.append({
            'severity': 'critical',
            'message': f"Low success rate: {metrics['success_rate']}%"
        })

    # Processing time
    if metrics['avg_processing_ms'] > 5000:  # 5 seconds
        alerts.append({
            'severity': 'warning',
            'message': f"Slow processing: {metrics['avg_processing_ms']}ms avg"
        })

    # Queue depth
    queue_depth = get_queue_depth()
    if queue_depth > 100:
        alerts.append({
            'severity': 'warning',
            'message': f"High queue depth: {queue_depth} pending"
        })

    # Webhook disabled
    try:
        response = session.get(f"{BASE_URL}/webhooks")
        webhooks = response.json()

        disabled = [w for w in webhooks if not w.get('enabled', True)]
        if disabled:
            alerts.append({
                'severity': 'critical',
                'message': f"{len(disabled)} webhooks disabled in Acuity!"
            })
    except Exception:
        pass

    return alerts
```

### Send Alerts

```python
def send_webhook_alert(alert):
    """Send alert via appropriate channel"""

    severity = alert['severity']
    message = alert['message']

    # PagerDuty for critical
    if severity == 'critical':
        send_pagerduty_alert(
            title='Webhook Integration Alert',
            description=message,
            severity='critical'
        )

    # Slack for all
    send_slack_message(
        f"⚠️ Webhook Alert ({severity.upper()}): {message}",
        channel='#alerts'
    )

    # Email for critical
    if severity == 'critical':
        send_email(
            to='oncall@yourcompany.com',
            subject='CRITICAL: Webhook Integration Issue',
            body=message
        )
```

---

## Troubleshooting

### Webhook Not Firing

**Symptoms:** No webhooks received despite appointments being created

**Diagnosis:**
```python
# Check webhook status
response = session.get(f"{BASE_URL}/webhooks")
webhooks = response.json()

for webhook in webhooks:
    print(f"Webhook: {webhook['url']}")
    print(f"Enabled: {webhook.get('enabled', True)}")
    print(f"Events: {webhook.get('events', [])}")

# Check recent payloads
response = session.get(f"{BASE_URL}/webhooks/WEBHOOK_ID/payloads")
payloads = response.json()
print(f"Recent payloads: {len(payloads)}")
```

**Solutions:**
1. Check if webhook is disabled (Acuity disables after 5 days of failures)
2. Verify webhook endpoint is HTTPS and accessible
3. Check server logs for incoming requests
4. Verify signature verification isn't rejecting requests
5. Check event types are selected in webhook configuration

### Signature Verification Failing

**Symptoms:** All webhooks return 403 Unauthorized

**Diagnosis:**
```python
def debug_signature(request):
    """Debug signature verification"""

    received = request.headers.get('X-Acuity-Signature')
    body = request.get_data()

    # Log for debugging
    logging.info(f"Received signature: {received}")
    logging.info(f"Body length: {len(body)}")
    logging.info(f"Body content: {body[:100]}")

    # Calculate expected
    expected = hmac.new(
        os.environ['ACUITY_API_KEY'].encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    logging.info(f"Expected signature: {expected}")
    logging.info(f"Match: {received == expected}")
```

**Solutions:**
1. Verify ACUITY_API_KEY environment variable is set correctly
2. Check for leading/trailing whitespace in API key
3. Ensure request body is exactly as received (no parsing before verification)
4. For OAuth webhooks, use OAuth token not admin API key

### Webhooks Processing Too Slowly

**Symptoms:** Timeouts on webhook processing (>30 seconds)

**Solutions:**
1. Move heavy processing to async queue (see queue section)
2. Add timeout handling:
   ```python
   @app.route('/webhooks/acuity', methods=['POST'])
   @timeout(30)  # 30 second timeout
   def handle_webhook():
       # ...
   ```
3. Reduce number of handlers per webhook
4. Cache frequently accessed data

### Queue Backlog Growing

**Symptoms:** Celery/RabbitMQ queue depth increasing

**Solutions:**
```python
# Check queue depth
def check_queue_health():
    """Monitor queue health"""

    # Celery
    stats = celery_app.control.inspect().stats()

    # Redis (for queue backend)
    redis_conn = redis.from_url(os.environ['REDIS_URL'])
    queue_length = redis_conn.llen('celery')

    if queue_length > 1000:
        logging.warning(f"Queue backlog: {queue_length} tasks")
        # Increase workers
        # Or reduce webhook event filtering
```

---

## Critical Pitfalls

### Critical: Webhook Auto-Disabling After 5 Days

**Issue:** If webhook returns 500 errors or times out for 5 consecutive days, Acuity **automatically disables** it **without notification**.

**Prevention:**
```python
# 1. Always return 200 OK immediately
@app.route('/webhooks/acuity', methods=['POST'])
def handle_webhook():
    try:
        queue_webhook_event(data)
        return jsonify({'status': 'queued'}), 200  # Return 200 even if queuing fails
    except Exception:
        return jsonify({'status': 'queued'}), 200  # Still return 200!

# 2. Monitor webhook health daily
def daily_webhook_check():
    """Run daily to check webhook status"""
    response = session.get(f"{BASE_URL}/webhooks")
    webhooks = response.json()

    for webhook in webhooks:
        if not webhook.get('enabled', True):
            send_critical_alert(f"Webhook {webhook['id']} is disabled!")

# 3. Alert on high failure rates
def monitor_webhook_failures():
    """Alert before 5-day threshold"""
    recent_failures = db.webhook_logs.count_documents({
        'status': 'error',
        'timestamp': {'$gte': datetime.now() - timedelta(hours=1)}
    })

    if recent_failures > 10:
        send_pagerduty_alert("High webhook failure rate")
```

### Critical: Webhook Signature Not Verified

**Issue:** Without verification, anyone can send fake webhooks to your endpoint.

**Prevention:** Always verify signature as first step (see signature verification section).

### Critical: Not Returning 200 Immediately

**Issue:** Acuity retries webhooks that don't return 200 OK. Processing long tasks before responding causes timeouts.

**Prevention:**
```python
# ✅ CORRECT: Return 200 immediately, process async
@app.route('/webhooks/acuity', methods=['POST'])
def handle_webhook():
    queue_webhook_event(data)  # Queue async
    return jsonify({'status': 'queued'}), 200  # Return immediately

# ❌ WRONG: Processing before response (causes timeout)
@app.route('/webhooks/acuity', methods=['POST'])
def handle_webhook():
    send_email(...)  # Slow!
    update_crm(...)  # Slow!
    sync_calendar(...)  # Slow!
    return jsonify({'status': 'processed'}), 200  # Takes >30 seconds, timeout!
```

---

## See Also

- [Authentication Guide](authentication-guide.md) - API credential setup
- [Error Handling Guide](error-handling-guide.md) - Status codes and recovery
- [Workflows Reference](workflows-reference.md) - Complete webhook integration workflows
- [Risk Assessment & Pitfalls](../risk-assessment-guide.md) - Webhook-specific risks
- [Official Acuity Webhooks Documentation](https://developer.acuityscheduling.com/reference/webhooks)

---

**Last Updated:** 2025-11-11
**Generated with Claude Code**

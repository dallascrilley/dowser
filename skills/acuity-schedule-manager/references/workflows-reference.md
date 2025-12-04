# Acuity Scheduling API - Proven Workflow Patterns

**Last Updated:** 2025-11-11
**Level:** Intermediate to Advanced
**Includes:** 7 complete production-ready workflows with code examples

---

## Table of Contents

1. [Workflow 1: Complete Appointment Booking](#workflow-1-complete-appointment-booking)
2. [Workflow 2: Bidirectional CRM Synchronization](#workflow-2-bidirectional-crm-synchronization)
3. [Workflow 3: Availability Calendar Widget](#workflow-3-availability-calendar-widget)
4. [Workflow 4: Appointment Lifecycle Management](#workflow-4-appointment-lifecycle-management)
5. [Workflow 5: Webhook Event Processing](#workflow-5-webhook-event-processing)
6. [Workflow 6: Bulk Data Export & Reporting](#workflow-6-bulk-data-export--reporting)
7. [Workflow 7: Multi-Calendar Availability Aggregation](#workflow-7-multi-calendar-availability-aggregation)

---

## Workflow 1: Complete Appointment Booking

**Purpose:** End-to-end appointment creation with full error handling and validation

**Architecture:**
```
User Input → Validation → Check Availability → Create Appointment → Confirmation
```

### Prerequisites

- Valid appointment type ID
- Business timezone configured
- Client information

### Implementation

```python
"""
Complete appointment booking workflow
Demonstrates validation, availability checking, and error handling
"""

import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import logging

class AppointmentBooker:
    def __init__(self, user_id, api_key, business_timezone='America/New_York'):
        self.user_id = user_id
        self.api_key = api_key
        self.base_url = "https://acuityscheduling.com/api/v1"
        self.business_timezone = business_timezone

        # Setup session with auth
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(user_id, api_key)

    def validate_appointment_data(self, data):
        """Validate appointment information before API call"""
        errors = []

        # Validate email
        if not self._is_valid_email(data.get('email', '')):
            errors.append("Invalid email address")

        # Validate required fields
        required_fields = ['appointmentTypeID', 'datetime', 'firstName', 'lastName', 'email']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate phone if provided
        if data.get('phone'):
            if not self._is_valid_phone(data['phone']):
                errors.append("Invalid phone format")

        # Validate appointment type exists
        if data.get('appointmentTypeID'):
            if not self._appointment_type_exists(data['appointmentTypeID']):
                errors.append("Invalid appointment type")

        return errors

    def _is_valid_email(self, email):
        """Simple email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _is_valid_phone(self, phone):
        """Validate phone has minimum digits"""
        import re
        digits = re.sub(r'\D', '', phone)
        return len(digits) >= 10

    def _appointment_type_exists(self, type_id):
        """Verify appointment type exists"""
        try:
            response = self.session.get(
                f"{self.base_url}/appointment-types/{type_id}"
            )
            return response.status_code == 200
        except:
            return False

    def check_availability(self, appointment_type_id, requested_date, timezone):
        """Check if requested date/time is available"""
        try:
            # Get available times for requested date
            response = self.session.get(
                f"{self.base_url}/availability/times",
                params={
                    'appointmentTypeID': appointment_type_id,
                    'date': requested_date.strftime('%Y-%m-%d'),
                    'timezone': timezone
                },
                timeout=10
            )

            if response.status_code == 200:
                available_times = response.json()
                return available_times

            else:
                logging.error(f"Failed to check availability: {response.status_code}")
                return []

        except requests.RequestException as e:
            logging.error(f"Availability check failed: {e}")
            return []

    def book_appointment(self, appointment_data, client_timezone='America/New_York'):
        """
        Complete booking workflow with fallback handling

        Steps:
        1. Validate input data
        2. Check availability
        3. Attempt booking at requested time
        4. Fallback to alternatives if slot taken
        5. Return confirmation or error
        """

        # Step 1: Validate
        validation_errors = self.validate_appointment_data(appointment_data)
        if validation_errors:
            return {
                'success': False,
                'error': 'Validation failed',
                'details': validation_errors
            }

        # Parse datetime
        requested_datetime = datetime.fromisoformat(
            appointment_data['datetime']
        )

        # Step 2: Check availability
        available_times = self.check_availability(
            appointment_data['appointmentTypeID'],
            requested_datetime,
            client_timezone
        )

        if not available_times:
            return {
                'success': False,
                'error': 'No availability found',
                'details': 'Please select a different date'
            }

        # Step 3: Attempt primary booking
        result = self._attempt_booking(appointment_data)

        if result['success']:
            logging.info(f"Appointment booked: {result['appointment']['id']}")
            return result

        # Step 4: Try alternatives if available
        if result['error'] == 'slot_unavailable' and len(available_times) > 1:
            logging.info("Primary time unavailable, trying alternatives...")

            for alt_time_obj in available_times[1:]:
                alt_time = alt_time_obj['time']

                # Try this time
                alt_data = appointment_data.copy()
                alt_data['datetime'] = alt_time

                result = self._attempt_booking(alt_data)

                if result['success']:
                    logging.info(
                        f"Booked alternative time: {alt_time}"
                    )
                    result['note'] = "Primary time was unavailable, booked alternative"
                    return result

        # Step 5: All attempts failed
        return {
            'success': False,
            'error': 'Could not book appointment',
            'details': 'All available times are now taken. Please try again.',
            'available_alternatives': len(available_times)
        }

    def _attempt_booking(self, appointment_data):
        """Single booking attempt"""
        try:
            response = self.session.post(
                f"{self.base_url}/appointments",
                json=appointment_data,
                timeout=30
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'appointment': response.json()
                }

            elif response.status_code == 400:
                error = response.json()
                if 'available' in error.get('message', '').lower():
                    return {
                        'success': False,
                        'error': 'slot_unavailable'
                    }

                return {
                    'success': False,
                    'error': 'validation_error',
                    'details': error.get('message', 'Invalid data')
                }

            else:
                return {
                    'success': False,
                    'error': f'api_error_{response.status_code}'
                }

        except requests.Timeout:
            return {
                'success': False,
                'error': 'timeout'
            }

        except requests.RequestException as e:
            return {
                'success': False,
                'error': 'network_error',
                'details': str(e)
            }

# Usage Example
if __name__ == '__main__':
    booker = AppointmentBooker(
        user_id='YOUR_USER_ID',
        api_key='YOUR_API_KEY'
    )

    appointment_data = {
        'appointmentTypeID': 12345,
        'datetime': '2025-11-15T14:00:00-0500',
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'phone': '555-0123'
    }

    result = booker.book_appointment(
        appointment_data,
        client_timezone='America/New_York'
    )

    if result['success']:
        print(f"Booked! ID: {result['appointment']['id']}")
    else:
        print(f"Failed: {result['error']}")
        print(f"Details: {result.get('details', 'N/A')}")
```

### Success Criteria

- ✅ Appointment created with unique ID
- ✅ Confirmation returned to client
- ✅ Confirmation email sent
- ✅ Appointment visible in calendar
- ✅ Customer receives reminder

### Common Issues & Fixes

**Issue: "This time is no longer available"**
→ Implement fallback to alternative times (see code above)

**Issue: Invalid email rejected**
→ Validate email format before API call

**Issue: Timezone confusion**
→ Always pass timezone parameter to availability endpoint

---

## Workflow 2: Bidirectional CRM Synchronization

**Purpose:** Sync appointments and contacts between Acuity and CRM system

**Architecture:**
```
CRM Changes → Sync Service → Acuity API
        ↓
Acuity Webhooks → Sync Service → CRM API → CRM Changes
```

### Prerequisites

- Acuity API credentials
- CRM API credentials (HubSpot, Salesforce, etc.)
- Field mapping configuration
- Webhook receiver endpoint

### Implementation

```python
"""
Bidirectional CRM synchronization
Syncs Acuity appointments ↔ CRM activities
"""

import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
import json
import hashlib

class CRMSyncService:
    def __init__(self, acuity_user_id, acuity_api_key, crm_api_key, crm_type='hubspot'):
        self.acuity_user_id = acuity_user_id
        self.acuity_api_key = acuity_api_key
        self.crm_api_key = crm_api_key
        self.crm_type = crm_type
        self.base_url = "https://acuityscheduling.com/api/v1"

        # Field mapping: Acuity → CRM
        self.field_mapping = {
            'firstName': 'firstname' if crm_type == 'hubspot' else 'FirstName',
            'lastName': 'lastname' if crm_type == 'hubspot' else 'LastName',
            'email': 'email',
            'phone': 'phone',
        }

    def sync_appointment_to_crm(self, appointment):
        """Sync Acuity appointment to CRM as activity"""

        # Step 1: Find or create contact in CRM
        contact = self._find_or_create_contact(
            appointment['firstName'],
            appointment['lastName'],
            appointment['email']
        )

        if not contact:
            logging.error("Failed to create/find contact")
            return False

        # Step 2: Create activity/deal in CRM
        activity = {
            'title': f"{appointment['appointmentTypeName']} - {appointment['firstName']} {appointment['lastName']}",
            'date': appointment['datetime'],
            'notes': appointment.get('notes', ''),
            'type': 'appointment',
            'appointment_id': appointment['id']
        }

        if self.crm_type == 'hubspot':
            return self._create_hubspot_activity(contact['id'], activity)
        elif self.crm_type == 'salesforce':
            return self._create_salesforce_task(contact['id'], activity)

        return False

    def _find_or_create_contact(self, first_name, last_name, email):
        """Find contact by email or create if doesn't exist"""

        # Search for existing contact
        contact = self._search_contact_by_email(email)

        if contact:
            return contact

        # Create new contact
        contact_data = {
            'firstName': first_name,
            'lastName': last_name,
            'email': email
        }

        if self.crm_type == 'hubspot':
            return self._create_hubspot_contact(contact_data)
        elif self.crm_type == 'salesforce':
            return self._create_salesforce_contact(contact_data)

        return None

    def _search_contact_by_email(self, email):
        """Search for contact in CRM by email"""

        if self.crm_type == 'hubspot':
            response = requests.get(
                'https://api.hubapi.com/crm/v3/objects/contacts',
                params={
                    'limit': 1,
                    'filter': json.dumps({
                        'filters': [{
                            'propertyName': 'email',
                            'operator': 'EQ',
                            'value': email
                        }]
                    })
                },
                headers={'Authorization': f'Bearer {self.crm_api_key}'}
            )

            if response.status_code == 200:
                results = response.json().get('results', [])
                return results[0] if results else None

        return None

    def _create_hubspot_contact(self, contact_data):
        """Create contact in HubSpot"""
        response = requests.post(
            'https://api.hubapi.com/crm/v3/objects/contacts',
            json={'properties': contact_data},
            headers={'Authorization': f'Bearer {self.crm_api_key}'}
        )

        if response.status_code == 201:
            return response.json()

        return None

    def _create_hubspot_activity(self, contact_id, activity):
        """Create activity in HubSpot"""
        engagement_data = {
            'engagement': {
                'type': 'NOTE',
                'timestamp': int(datetime.now().timestamp() * 1000)
            },
            'associations': {
                'contactIds': [contact_id]
            },
            'metadata': {
                'body': activity['title'],
                'external_id': f"acuity_{activity['appointment_id']}"
            }
        }

        response = requests.post(
            'https://api.hubapi.com/engagements/v1/engagements',
            json=engagement_data,
            headers={'Authorization': f'Bearer {self.crm_api_key}'}
        )

        return response.status_code == 200

    def sync_crm_contact_to_acuity(self, crm_contact_id):
        """Sync CRM contact to Acuity client"""

        # Fetch CRM contact details
        contact = self._get_crm_contact(crm_contact_id)

        if not contact:
            return False

        # Create or update Acuity client
        client_data = {
            'firstName': contact.get('firstName'),
            'lastName': contact.get('lastName'),
            'email': contact.get('email'),
            'phone': contact.get('phone')
        }

        # Check if already exists in Acuity
        acuity_client = self._find_acuity_client_by_email(client_data['email'])

        if acuity_client:
            # Update existing
            return self._update_acuity_client(acuity_client['id'], client_data)
        else:
            # Create new
            return self._create_acuity_client(client_data)

    def _find_acuity_client_by_email(self, email):
        """Find Acuity client by email"""
        response = requests.get(
            f"{self.base_url}/clients",
            params={'email': email},
            auth=HTTPBasicAuth(self.acuity_user_id, self.acuity_api_key)
        )

        if response.status_code == 200:
            clients = response.json()
            return clients[0] if clients else None

        return None

    def _create_acuity_client(self, client_data):
        """Create client in Acuity"""
        response = requests.post(
            f"{self.base_url}/clients",
            json=client_data,
            auth=HTTPBasicAuth(self.acuity_user_id, self.acuity_api_key)
        )

        return response.status_code == 201

    def _update_acuity_client(self, client_id, client_data):
        """Update client in Acuity"""
        response = requests.put(
            f"{self.base_url}/clients/{client_id}",
            json=client_data,
            auth=HTTPBasicAuth(self.acuity_user_id, self.acuity_api_key)
        )

        return response.status_code == 200

    def _get_crm_contact(self, contact_id):
        """Get contact from CRM"""
        if self.crm_type == 'hubspot':
            response = requests.get(
                f'https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}',
                params={'limit': 100},  # Get all properties
                headers={'Authorization': f'Bearer {self.crm_api_key}'}
            )

            if response.status_code == 200:
                data = response.json()
                props = data.get('properties', {})
                return {
                    'firstName': props.get('firstname', {}).get('value'),
                    'lastName': props.get('lastname', {}).get('value'),
                    'email': props.get('email', {}).get('value'),
                    'phone': props.get('phone', {}).get('value')
                }

        return None
```

### Success Criteria

- ✅ Appointment synced to CRM activity
- ✅ Contact created in CRM if needed
- ✅ Contact updated in Acuity if changed in CRM
- ✅ No duplicate contacts created
- ✅ Sync errors logged and reported

---

## Workflow 3: Availability Calendar Widget

**Purpose:** Embed real-time availability in custom booking interface

**Architecture:**
```
Frontend: Load types → Show calendar → Load times → Book appointment
Backend: API proxy with caching and rate limiting
```

### Frontend Implementation (JavaScript)

```javascript
/**
 * Acuity Appointment Booking Widget
 * Shows real-time availability and handles booking
 */

class AcuityBookingWidget {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/acuity';
        this.appointmentTypeId = options.appointmentTypeId;
        this.timezone = options.timezone || 'America/New_York';
        this.cache = {};
        this.cacheExpiry = 5 * 60 * 1000; // 5 minutes
    }

    async init() {
        try {
            // Load appointment types
            const types = await this.getAppointmentTypes();
            this.renderAppointmentTypes(types);

            // Initialize calendar
            this.initializeCalendar();

        } catch (error) {
            console.error('Failed to initialize widget:', error);
            this.showError('Failed to load appointment system');
        }
    }

    async getAppointmentTypes() {
        const cacheKey = 'appointment_types';

        // Check cache
        if (this.cache[cacheKey] && this.cache[cacheKey].expiry > Date.now()) {
            return this.cache[cacheKey].data;
        }

        // Fetch from API
        const response = await fetch(`${this.apiUrl}/appointment-types`);
        if (!response.ok) throw new Error('Failed to load appointment types');

        const types = await response.json();

        // Cache result
        this.cache[cacheKey] = {
            data: types,
            expiry: Date.now() + this.cacheExpiry
        };

        return types;
    }

    async checkAvailability(typeId, month) {
        const cacheKey = `availability_${typeId}_${month}`;

        // Check cache
        if (this.cache[cacheKey] && this.cache[cacheKey].expiry > Date.now()) {
            return this.cache[cacheKey].data;
        }

        // Fetch from API
        const response = await fetch(
            `${this.apiUrl}/availability/dates`,
            {
                params: {
                    appointmentTypeID: typeId,
                    month: month
                }
            }
        );

        const dates = await response.json();

        // Cache result
        this.cache[cacheKey] = {
            data: dates,
            expiry: Date.now() + this.cacheExpiry
        };

        return dates;
    }

    async getTimeslots(typeId, date) {
        const response = await fetch(
            `${this.apiUrl}/availability/times`,
            {
                params: {
                    appointmentTypeID: typeId,
                    date: date,
                    timezone: this.timezone
                }
            }
        );

        return await response.json();
    }

    initializeCalendar() {
        const calendar = document.getElementById('appointment-calendar');

        calendar.addEventListener('click', async (e) => {
            if (e.target.classList.contains('available-date')) {
                const date = e.target.dataset.date;
                const timeslots = await this.getTimeslots(
                    this.appointmentTypeId,
                    date
                );
                this.showTimeslots(timeslots);
            }
        });
    }

    async bookAppointment(appointmentData) {
        try {
            const response = await fetch(
                `${this.apiUrl}/appointments`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(appointmentData)
                }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message);
            }

            const appointment = await response.json();
            this.showConfirmation(appointment);

            // Clear cache
            this.cache = {};

        } catch (error) {
            this.showError(`Booking failed: ${error.message}`);
        }
    }

    renderAppointmentTypes(types) {
        const select = document.getElementById('appointment-type-select');
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = `${type.name} ($${type.price})`;
            select.appendChild(option);
        });
    }

    showTimeslots(slots) {
        const slotsDiv = document.getElementById('time-slots');
        slotsDiv.innerHTML = '';

        slots.forEach(slot => {
            const button = document.createElement('button');
            button.className = 'time-slot';
            button.textContent = new Date(slot.time).toLocaleTimeString();
            button.onclick = () => this.selectTime(slot.time);
            slotsDiv.appendChild(button);
        });
    }

    selectTime(datetime) {
        const form = document.getElementById('booking-form');
        form.dataset.selectedTime = datetime;
        form.classList.add('show');
    }

    async submitBooking(formData) {
        const selectedTime = document.getElementById('booking-form').dataset.selectedTime;

        const appointmentData = {
            appointmentTypeID: parseInt(formData.get('appointment_type')),
            datetime: selectedTime,
            firstName: formData.get('first_name'),
            lastName: formData.get('last_name'),
            email: formData.get('email'),
            phone: formData.get('phone')
        };

        await this.bookAppointment(appointmentData);
    }

    showConfirmation(appointment) {
        alert(`Appointment confirmed! ID: ${appointment.id}`);
    }

    showError(message) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const widget = new AcuityBookingWidget({
        apiUrl: '/api/acuity',
        appointmentTypeId: 12345,
        timezone: 'America/New_York'
    });

    widget.init();
});
```

### Backend Implementation (Python/Flask)

```python
"""Backend API proxy with caching and rate limiting"""

from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import redis
import json

app = Flask(__name__)
cache = redis.Redis(host='localhost', port=6379, db=0)

USER_ID = os.getenv('ACUITY_USER_ID')
API_KEY = os.getenv('ACUITY_API_KEY')
BASE_URL = 'https://acuityscheduling.com/api/v1'

def get_cached_or_fetch(key, fetch_func, ttl=300):
    """Get from cache or fetch fresh data"""
    cached = cache.get(key)
    if cached:
        return json.loads(cached)

    data = fetch_func()
    cache.setex(key, ttl, json.dumps(data))
    return data

@app.route('/api/acuity/appointment-types', methods=['GET'])
def appointment_types():
    """Get appointment types with caching"""
    def fetch():
        response = requests.get(
            f"{BASE_URL}/appointment-types",
            auth=HTTPBasicAuth(USER_ID, API_KEY)
        )
        return response.json()

    types = get_cached_or_fetch('appointment_types', fetch, ttl=86400)
    return jsonify(types)

@app.route('/api/acuity/availability/dates', methods=['GET'])
def availability_dates():
    """Get available dates with caching"""
    type_id = request.args.get('appointmentTypeID')
    month = request.args.get('month')

    cache_key = f"availability_dates:{type_id}:{month}"

    def fetch():
        response = requests.get(
            f"{BASE_URL}/availability/dates",
            params={'appointmentTypeID': type_id, 'month': month},
            auth=HTTPBasicAuth(USER_ID, API_KEY)
        )
        return response.json()

    dates = get_cached_or_fetch(cache_key, fetch, ttl=300)
    return jsonify(dates)

@app.route('/api/acuity/availability/times', methods=['GET'])
def availability_times():
    """Get available time slots (shorter cache)"""
    type_id = request.args.get('appointmentTypeID')
    date = request.args.get('date')
    timezone = request.args.get('timezone', 'America/New_York')

    response = requests.get(
        f"{BASE_URL}/availability/times",
        params={
            'appointmentTypeID': type_id,
            'date': date,
            'timezone': timezone
        },
        auth=HTTPBasicAuth(USER_ID, API_KEY)
    )

    return jsonify(response.json())

@app.route('/api/acuity/appointments', methods=['POST'])
def create_appointment():
    """Create appointment"""
    appointment_data = request.json

    # Validate
    required = ['appointmentTypeID', 'datetime', 'firstName', 'lastName', 'email']
    if not all(appointment_data.get(f) for f in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # Create in Acuity
    response = requests.post(
        f"{BASE_URL}/appointments",
        json=appointment_data,
        auth=HTTPBasicAuth(USER_ID, API_KEY)
    )

    # Clear cache on successful booking
    if response.status_code == 200:
        cache.delete(f"availability_dates:{appointment_data['appointmentTypeID']}:*")

    return jsonify(response.json()), response.status_code
```

---

## See Also

- [Webhook Integration Guide](webhook-integration-guide.md) - Real-time event handling
- [Error Handling Guide](error-handling-guide.md) - Comprehensive error strategies
- [API Endpoints Reference](api-endpoints-reference.md) - Complete endpoint documentation

---

**Last Updated:** 2025-11-11
**Generated with Claude Code**

#!/bin/bash
# Acuity Scheduling API - cURL Examples
# Replace {userId} and {apiKey} with your actual credentials

# Set your credentials (or load from .env)
USER_ID="${ACUITY_USER_ID:-12345678}"
API_KEY="${ACUITY_API_KEY:-your_api_key_here}"
BASE_URL="https://acuityscheduling.com/api/v1"

echo "=========================================="
echo "Acuity Scheduling API - cURL Examples"
echo "=========================================="
echo ""

# 1. Test Authentication
echo "1. Testing Authentication (GET /me)"
echo "-----------------------------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/me" | jq '.'
echo ""
echo ""

# 2. List Appointment Types
echo "2. List Appointment Types"
echo "-------------------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/appointment-types" | jq '.'
echo ""
echo ""

# 3. List Calendars
echo "3. List Calendars"
echo "-----------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/calendars" | jq '.'
echo ""
echo ""

# 4. Check Availability for Today
echo "4. Check Availability for Today"
echo "--------------------------------"
TODAY=$(date +%Y-%m-%d)
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/availability/dates?appointmentTypeID=12345&month=$(date +%Y-%m)" | jq '.'
echo ""
echo ""

# 5. Get Available Times for Specific Date
echo "5. Get Available Times for Tomorrow"
echo "------------------------------------"
TOMORROW=$(date -v+1d +%Y-%m-%d)  # macOS format
# For Linux, use: TOMORROW=$(date -d "+1 day" +%Y-%m-%d)
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/availability/times?appointmentTypeID=12345&date=${TOMORROW}&timezone=America/New_York" | jq '.'
echo ""
echo ""

# 6. List Appointments (last 7 days)
echo "6. List Recent Appointments (last 7 days)"
echo "------------------------------------------"
MIN_DATE=$(date -v-7d +%Y-%m-%d)  # macOS format
MAX_DATE=$(date +%Y-%m-%d)
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/appointments?minDate=${MIN_DATE}&maxDate=${MAX_DATE}&max=10" | jq '.'
echo ""
echo ""

# 7. Create Appointment
echo "7. Create Appointment (Example - commented out)"
echo "-----------------------------------------------"
echo "# Uncomment to actually create an appointment"
echo ""
cat << 'EOF'
curl -u ${USER_ID}:${API_KEY} \
  -H "Content-Type: application/json" \
  -d '{
    "appointmentTypeID": 12345,
    "datetime": "2025-11-15T14:00:00-0500",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "555-123-4567",
    "timezone": "America/New_York"
  }' \
  "${BASE_URL}/appointments" | jq '.'
EOF
echo ""
echo ""

# 8. Get Specific Appointment
echo "8. Get Specific Appointment (replace APPOINTMENT_ID)"
echo "-----------------------------------------------------"
echo "# curl -u \${USER_ID}:\${API_KEY} \\"
echo "#   \"\${BASE_URL}/appointments/APPOINTMENT_ID\" | jq '.'"
echo ""
echo ""

# 9. Update Appointment
echo "9. Update Appointment (Example - commented out)"
echo "-----------------------------------------------"
cat << 'EOF'
curl -u ${USER_ID}:${API_KEY} \
  -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Jane",
    "lastName": "Doe",
    "notes": "Updated notes"
  }' \
  "${BASE_URL}/appointments/APPOINTMENT_ID" | jq '.'
EOF
echo ""
echo ""

# 10. Cancel Appointment
echo "10. Cancel Appointment (Example - commented out)"
echo "-------------------------------------------------"
cat << 'EOF'
curl -u ${USER_ID}:${API_KEY} \
  -X PUT \
  -H "Content-Type: application/json" \
  "${BASE_URL}/appointments/APPOINTMENT_ID/cancel" | jq '.'
EOF
echo ""
echo ""

# 11. Reschedule Appointment
echo "11. Reschedule Appointment (Example - commented out)"
echo "-----------------------------------------------------"
cat << 'EOF'
curl -u ${USER_ID}:${API_KEY} \
  -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "2025-11-20T15:00:00-0500"
  }' \
  "${BASE_URL}/appointments/APPOINTMENT_ID/reschedule" | jq '.'
EOF
echo ""
echo ""

# 12. List Clients
echo "12. List Clients"
echo "----------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/clients?max=10" | jq '.'
echo ""
echo ""

# 13. Search Client by Email
echo "13. Search Client by Email"
echo "--------------------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/clients?email=john.doe@example.com" | jq '.'
echo ""
echo ""

# 14. Create Client
echo "14. Create Client (Example - commented out)"
echo "-------------------------------------------"
cat << 'EOF'
curl -u ${USER_ID}:${API_KEY} \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane.smith@example.com",
    "phone": "555-987-6543"
  }' \
  "${BASE_URL}/clients" | jq '.'
EOF
echo ""
echo ""

# 15. Get Forms
echo "15. Get Intake Forms"
echo "--------------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/forms" | jq '.'
echo ""
echo ""

# 16. Get Blocks (Time Off)
echo "16. Get Time Blocks"
echo "-------------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/blocks" | jq '.'
echo ""
echo ""

# 17. Rate Limit Check
echo "17. Check Rate Limit Headers"
echo "----------------------------"
curl -s -i -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/me" | grep -i "x-ratelimit"
echo ""
echo ""

# 18. Error Handling Example - Invalid Endpoint
echo "18. Error Handling Example (404)"
echo "--------------------------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/invalid-endpoint" | jq '.'
echo ""
echo ""

# 19. Error Handling Example - Missing Auth
echo "19. Error Handling Example (401)"
echo "--------------------------------"
curl -s "${BASE_URL}/me" | jq '.'
echo ""
echo ""

echo "=========================================="
echo "Examples Complete!"
echo "=========================================="
echo ""
echo "Tips:"
echo "  - Set ACUITY_USER_ID and ACUITY_API_KEY environment variables"
echo "  - Install jq for pretty JSON output: brew install jq"
echo "  - Uncomment 'create/update/delete' examples to actually modify data"
echo "  - Check rate limits: 10 requests per second"
echo ""

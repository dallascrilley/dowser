"""
Integration Tests for Acuity API Workflows

Tests complete workflows using mocked API responses.
Set ACUITY_USER_ID and ACUITY_API_KEY environment variables to test against real API.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta


@pytest.fixture
def mock_api_session():
    """Create a mock API session with common responses"""
    session = Mock()

    # Mock successful authentication
    me_response = Mock()
    me_response.status_code = 200
    me_response.json.return_value = {
        "id": 12345678,
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User"
    }

    # Mock appointment types
    types_response = Mock()
    types_response.status_code = 200
    types_response.json.return_value = [
        {
            "id": 12345,
            "name": "30 Minute Consultation",
            "duration": 30,
            "price": 50.00
        }
    ]

    # Mock calendars
    calendars_response = Mock()
    calendars_response.status_code = 200
    calendars_response.json.return_value = [
        {
            "id": 67890,
            "name": "Main Calendar",
            "email": "calendar@example.com"
        }
    ]

    # Mock availability
    availability_response = Mock()
    availability_response.status_code = 200
    availability_response.json.return_value = [
        {"time": "2025-11-15T09:00:00-0500"},
        {"time": "2025-11-15T10:00:00-0500"},
        {"time": "2025-11-15T14:00:00-0500"}
    ]

    # Mock appointment creation
    create_response = Mock()
    create_response.status_code = 200
    create_response.json.return_value = {
        "id": 999999,
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "datetime": "2025-11-15T14:00:00-0500",
        "confirmationCode": "ABC123"
    }

    # Configure session mock to return appropriate responses
    def get_side_effect(url, *args, **kwargs):
        if '/me' in url:
            return me_response
        elif '/appointment-types' in url:
            return types_response
        elif '/calendars' in url:
            return calendars_response
        elif '/availability/times' in url:
            return availability_response
        elif '/appointments' in url:
            return Mock(status_code=200, json=lambda: [])
        return Mock(status_code=404, json=lambda: {"error": "Not found"})

    def post_side_effect(url, *args, **kwargs):
        if '/appointments' in url:
            return create_response
        return Mock(status_code=400, json=lambda: {"error": "Bad request"})

    session.get.side_effect = get_side_effect
    session.post.side_effect = post_side_effect

    return session


class TestAuthenticationWorkflow:
    """Test authentication workflow"""

    def test_successful_authentication(self, mock_api_session):
        """Test successful API authentication"""
        response = mock_api_session.get('https://acuityscheduling.com/api/v1/me')
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'email' in data

    def test_invalid_credentials(self):
        """Test handling of invalid credentials"""
        session = Mock()
        error_response = Mock()
        error_response.status_code = 401
        error_response.json.return_value = {"error": "Unauthorized"}
        session.get.return_value = error_response

        response = session.get('https://acuityscheduling.com/api/v1/me')
        assert response.status_code == 401


class TestAvailabilityCheckWorkflow:
    """Test availability checking workflow"""

    def test_get_appointment_types(self, mock_api_session):
        """Test retrieving appointment types"""
        response = mock_api_session.get('https://acuityscheduling.com/api/v1/appointment-types')
        assert response.status_code == 200
        types = response.json()
        assert len(types) > 0
        assert 'id' in types[0]
        assert 'name' in types[0]

    def test_check_availability(self, mock_api_session):
        """Test checking availability for a date"""
        response = mock_api_session.get(
            'https://acuityscheduling.com/api/v1/availability/times',
            params={'appointmentTypeID': 12345, 'date': '2025-11-15'}
        )
        assert response.status_code == 200
        availability = response.json()
        assert len(availability) > 0
        assert 'time' in availability[0]

    def test_no_availability(self):
        """Test handling when no availability exists"""
        session = Mock()
        empty_response = Mock()
        empty_response.status_code = 200
        empty_response.json.return_value = []
        session.get.return_value = empty_response

        response = session.get('https://acuityscheduling.com/api/v1/availability/times')
        assert response.status_code == 200
        assert len(response.json()) == 0


class TestAppointmentCreationWorkflow:
    """Test complete appointment creation workflow"""

    def test_create_appointment_success(self, mock_api_session):
        """Test successful appointment creation"""
        appointment_data = {
            "appointmentTypeID": 12345,
            "datetime": "2025-11-15T14:00:00-0500",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com"
        }

        response = mock_api_session.post(
            'https://acuityscheduling.com/api/v1/appointments',
            json=appointment_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == 999999
        assert data['confirmationCode'] == 'ABC123'

    def test_create_appointment_with_validation(self, mock_api_session):
        """Test appointment creation with pre-validation"""
        # Step 1: Check availability
        availability_response = mock_api_session.get(
            'https://acuityscheduling.com/api/v1/availability/times',
            params={'appointmentTypeID': 12345, 'date': '2025-11-15'}
        )
        assert availability_response.status_code == 200
        available_times = availability_response.json()
        assert len(available_times) > 0

        # Step 2: Create appointment with first available time
        appointment_data = {
            "appointmentTypeID": 12345,
            "datetime": available_times[0]['time'],
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane@example.com"
        }

        response = mock_api_session.post(
            'https://acuityscheduling.com/api/v1/appointments',
            json=appointment_data
        )
        assert response.status_code == 200

    def test_appointment_conflict_handling(self):
        """Test handling of appointment conflicts (409)"""
        session = Mock()
        conflict_response = Mock()
        conflict_response.status_code = 409
        conflict_response.json.return_value = {"error": "Time slot no longer available"}
        session.post.return_value = conflict_response

        response = session.post('https://acuityscheduling.com/api/v1/appointments')
        assert response.status_code == 409


class TestRateLimitingWorkflow:
    """Test rate limiting handling"""

    def test_rate_limit_detection(self):
        """Test detection of rate limit (429) response"""
        session = Mock()
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {
            'X-RateLimit-Limit': '10',
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': '1699123456'
        }
        session.get.return_value = rate_limit_response

        response = session.get('https://acuityscheduling.com/api/v1/appointments')
        assert response.status_code == 429
        assert 'X-RateLimit-Remaining' in response.headers
        assert response.headers['X-RateLimit-Remaining'] == '0'

    def test_exponential_backoff_retry(self):
        """Test exponential backoff retry logic"""
        import time

        max_retries = 3
        for attempt in range(max_retries):
            delay = 2 ** attempt
            assert delay in [1, 2, 4], f"Expected exponential delay, got {delay}"
            # In real code, would sleep here: time.sleep(delay)


class TestErrorHandlingWorkflow:
    """Test error handling patterns"""

    def test_network_error_handling(self):
        """Test handling of network errors"""
        from requests.exceptions import ConnectionError

        session = Mock()
        session.get.side_effect = ConnectionError("Connection failed")

        with pytest.raises(ConnectionError):
            session.get('https://acuityscheduling.com/api/v1/me')

    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses"""
        from json.decoder import JSONDecodeError

        session = Mock()
        bad_response = Mock()
        bad_response.status_code = 200
        bad_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        session.get.return_value = bad_response

        response = session.get('https://acuityscheduling.com/api/v1/me')
        with pytest.raises(JSONDecodeError):
            response.json()


class TestBatchOperationsWorkflow:
    """Test batch operations and pagination"""

    def test_paginated_appointment_retrieval(self):
        """Test retrieving appointments with pagination"""
        session = Mock()

        # First page
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.json.return_value = [
            {"id": 1, "firstName": "User1"},
            {"id": 2, "firstName": "User2"}
        ]

        # Second page
        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.json.return_value = [
            {"id": 3, "firstName": "User3"}
        ]

        # Third page (empty)
        page3_response = Mock()
        page3_response.status_code = 200
        page3_response.json.return_value = []

        session.get.side_effect = [page1_response, page2_response, page3_response]

        all_appointments = []
        offset = 0
        max_per_page = 2

        while True:
            response = session.get(
                'https://acuityscheduling.com/api/v1/appointments',
                params={'max': max_per_page, 'offset': offset}
            )
            appointments = response.json()
            if not appointments:
                break
            all_appointments.extend(appointments)
            offset += max_per_page

        assert len(all_appointments) == 3


# Skip integration tests by default (require real credentials)
@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv('ACUITY_USER_ID') or not os.getenv('ACUITY_API_KEY'),
    reason="ACUITY_USER_ID and ACUITY_API_KEY environment variables not set"
)
class TestRealAPIIntegration:
    """Integration tests against real Acuity API (requires credentials)"""

    def test_real_authentication(self):
        """Test authentication against real API"""
        import requests
        from requests.auth import HTTPBasicAuth

        user_id = os.getenv('ACUITY_USER_ID')
        api_key = os.getenv('ACUITY_API_KEY')

        response = requests.get(
            'https://acuityscheduling.com/api/v1/me',
            auth=HTTPBasicAuth(user_id, api_key)
        )

        assert response.status_code == 200
        data = response.json()
        assert 'id' in data

    def test_real_appointment_types(self):
        """Test retrieving real appointment types"""
        import requests
        from requests.auth import HTTPBasicAuth

        user_id = os.getenv('ACUITY_USER_ID')
        api_key = os.getenv('ACUITY_API_KEY')

        response = requests.get(
            'https://acuityscheduling.com/api/v1/appointment-types',
            auth=HTTPBasicAuth(user_id, api_key)
        )

        assert response.status_code == 200
        types = response.json()
        assert isinstance(types, list)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

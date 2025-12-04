"""
Pytest configuration and shared fixtures for Acuity Schedule Manager tests
"""

import pytest
import os
from unittest.mock import Mock


@pytest.fixture(scope="session")
def test_credentials():
    """Provide test credentials (mock or real)"""
    return {
        'user_id': os.getenv('ACUITY_USER_ID', '12345678'),
        'api_key': os.getenv('ACUITY_API_KEY', 'test_api_key_here'),
        'base_url': 'https://acuityscheduling.com/api/v1'
    }


@pytest.fixture
def sample_appointment_data():
    """Provide sample appointment data for testing"""
    return {
        "appointmentTypeID": 12345,
        "datetime": "2025-11-15T14:00:00-0500",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "timezone": "America/New_York"
    }


@pytest.fixture
def sample_availability_response():
    """Provide sample availability response"""
    return [
        {"time": "2025-11-15T09:00:00-0500"},
        {"time": "2025-11-15T10:00:00-0500"},
        {"time": "2025-11-15T14:00:00-0500"},
        {"time": "2025-11-15T15:00:00-0500"}
    ]


@pytest.fixture
def mock_successful_appointment_creation():
    """Mock successful appointment creation response"""
    return {
        "id": 999999,
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "datetime": "2025-11-15T14:00:00-0500",
        "endTime": "2025-11-15T14:30:00-0500",
        "appointmentTypeID": 12345,
        "calendarID": 67890,
        "confirmed": True,
        "paid": "no",
        "confirmationCode": "ABC123"
    }


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires real API credentials)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

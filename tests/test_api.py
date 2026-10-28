"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_submit_application_success(client):
    """Test successful application submission."""
    application_data = {
        "applicant_profile": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "date_of_birth": "1990-01-01",
            "ssn": "123456789",
            "address": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
        },
        "employment_info": {
            "employment_type": "full_time",
            "employer_name": "Tech Corp",
            "job_title": "Software Engineer",
            "years_employed": 5,
            "annual_income": 120000,
        },
        "credit_record": {
            "credit_score": 750,
            "years_of_credit_history": 10,
            "number_of_accounts": 5,
            "delinquencies_last_24_months": 0,
            "public_records": 0,
            "current_debt": 15000,
        },
        "loan_details": {
            "loan_amount": 50000,
            "loan_purpose": "Home improvement",
            "loan_term_months": 60,
        },
    }

    response = client.post("/api/applications", json=application_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "submitted"
    assert "application_id" in data
    assert data["submitted_at"] is not None


def test_get_application_success(client):
    """Test retrieving application."""
    application_data = {
        "applicant_profile": {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone": "0987654321",
            "date_of_birth": "1985-05-15",
            "ssn": "987654321",
            "address": "456 Oak Ave",
            "city": "Shelbyville",
            "state": "IL",
            "zip_code": "62702",
        },
        "employment_info": {
            "employment_type": "full_time",
            "employer_name": "Finance Corp",
            "job_title": "Analyst",
            "years_employed": 3,
            "annual_income": 85000,
        },
        "credit_record": {
            "credit_score": 700,
            "years_of_credit_history": 8,
            "number_of_accounts": 4,
            "delinquencies_last_24_months": 0,
            "public_records": 0,
            "current_debt": 10000,
        },
        "loan_details": {
            "loan_amount": 30000,
            "loan_purpose": "Car purchase",
            "loan_term_months": 48,
        },
    }

    submit_response = client.post("/api/applications", json=application_data)
    application_id = submit_response.json()["application_id"]

    get_response = client.get(f"/api/applications/{application_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["application_id"] == application_id
    assert data["status"] == "submitted"


def test_get_application_not_found(client):
    """Test retrieving non-existent application."""
    response = client.get("/api/applications/nonexistent-id")
    assert response.status_code == 404


def test_list_applications(client):
    """Test listing applications."""
    response = client.get("/api/applications")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "applications" in data
    assert "skip" in data
    assert "limit" in data

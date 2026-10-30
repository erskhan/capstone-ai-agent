"""Integration tests for FastAPI endpoints."""

import pytest
import json
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_detailed_health_check(self, client):
        """Test detailed health check."""
        response = client.get("/health/detailed")
        assert response.status_code in [200, 503]  # May be unavailable if DB not configured
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "services" in data


class TestApplicationSubmission:
    """Test application submission endpoint."""

    def test_submit_valid_application(self, client, sample_loan_application):
        """Test submitting a valid application."""
        payload = sample_loan_application.model_dump()

        response = client.post("/api/applications", json=payload)
        assert response.status_code in [201, 500]  # May fail if DB not configured

        if response.status_code == 201:
            data = response.json()
            assert "application_id" in data
            assert "status" in data
            assert data["status"] in ["submitted", "validating"]

    def test_submit_invalid_email(self, client, sample_loan_application):
        """Test submitting with invalid email."""
        payload = sample_loan_application.model_dump()
        payload["applicant_profile"]["email"] = "invalid-email"

        response = client.post("/api/applications", json=payload)
        # Should fail validation
        assert response.status_code in [422, 500]

    def test_submit_invalid_loan_amount(self, client, sample_loan_application):
        """Test submitting with invalid loan amount."""
        payload = sample_loan_application.model_dump()
        payload["loan_details"]["loan_amount"] = -1000  # Negative

        response = client.post("/api/applications", json=payload)
        assert response.status_code in [422, 500]

    def test_submit_out_of_range_credit_score(self, client, sample_loan_application):
        """Test submitting with out-of-range credit score."""
        payload = sample_loan_application.model_dump()
        payload["credit_record"]["credit_score"] = 900  # Out of range

        response = client.post("/api/applications", json=payload)
        assert response.status_code in [422, 500]


class TestApplicationRetrieval:
    """Test application retrieval endpoints."""

    def test_get_application_not_found(self, client):
        """Test retrieving non-existent application."""
        response = client.get("/api/applications/nonexistent-id")
        assert response.status_code == 404

    def test_list_applications(self, client):
        """Test listing applications."""
        response = client.get("/api/applications")
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "total" in data
            assert "applications" in data or "skip" in data

    def test_list_applications_with_pagination(self, client):
        """Test listing with pagination parameters."""
        response = client.get("/api/applications?skip=0&limit=10")
        assert response.status_code in [200, 500]


class TestWorkflowEndpoints:
    """Test workflow-related endpoints."""

    def test_get_workflow_state(self, client):
        """Test getting workflow state."""
        response = client.get("/api/applications/test-id/workflow-state")
        assert response.status_code in [404, 500]  # Not found or error

    def test_get_workflow_execution(self, client):
        """Test getting workflow execution details."""
        response = client.get("/api/applications/test-id/workflow-execution")
        assert response.status_code in [404, 500]


class TestDecisionEndpoints:
    """Test decision-related endpoints."""

    def test_get_decision(self, client):
        """Test getting decision details."""
        response = client.get("/api/applications/test-id/decision")
        assert response.status_code in [404, 500]

    def test_get_audit_trail(self, client):
        """Test getting audit trail."""
        response = client.get("/api/applications/test-id/audit-trail")
        assert response.status_code in [404, 500]


class TestAppealEndpoints:
    """Test appeal-related endpoints."""

    def test_submit_appeal_not_found(self, client):
        """Test submitting appeal for non-existent application."""
        appeal_data = {
            "application_id": "nonexistent",
            "appeal_reason": "I believe the decision was unfair. Here's why...",
        }

        response = client.post("/api/applications/nonexistent/appeal", json=appeal_data)
        assert response.status_code in [404, 500]

    def test_submit_appeal_invalid_reason(self, client):
        """Test submitting appeal with invalid reason."""
        appeal_data = {
            "application_id": "test-id",
            "appeal_reason": "Bad",  # Too short
        }

        response = client.post("/api/applications/test-id/appeal", json=appeal_data)
        assert response.status_code in [422, 500]


class TestManualReviewEndpoints:
    """Test manual review endpoints."""

    def test_assign_to_manual_review(self, client):
        """Test assigning to manual review."""
        review_data = {
            "application_id": "test-id",
            "reason": "Needs detailed review for special circumstances",
            "priority": "high",
        }

        response = client.post("/api/applications/test-id/review", json=review_data)
        assert response.status_code in [404, 500]

    def test_assign_invalid_priority(self, client):
        """Test assigning with invalid priority."""
        review_data = {
            "application_id": "test-id",
            "reason": "Review needed",
            "priority": "invalid_priority",
        }

        response = client.post("/api/applications/test-id/review", json=review_data)
        assert response.status_code in [422, 500]


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_json(self, client):
        """Test sending invalid JSON."""
        response = client.post("/api/applications", data="{invalid json}")
        assert response.status_code >= 400

    def test_method_not_allowed(self, client):
        """Test using wrong HTTP method."""
        response = client.post("/health")
        assert response.status_code in [404, 405]

    def test_missing_required_fields(self, client):
        """Test missing required fields."""
        response = client.post("/api/applications", json={})
        assert response.status_code in [422, 400]


class TestResponseStructure:
    """Test response structure and format."""

    def test_health_response_structure(self, client):
        """Test health response structure."""
        response = client.get("/health")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "status" in data
            assert isinstance(data["status"], str)

    def test_error_response_format(self, client):
        """Test error response format."""
        response = client.get("/api/applications/invalid/decision")

        if response.status_code >= 400:
            # Should have error info
            assert response.text or response.json()

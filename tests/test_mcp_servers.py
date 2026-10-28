"""Tests for MCP servers."""

import pytest

from mcp_servers.applicant_db_server import ApplicantDBServer


@pytest.fixture
def applicant_db_server():
    """Create an applicant database server instance."""
    return ApplicantDBServer()


@pytest.mark.asyncio
async def test_validate_applicant_valid(applicant_db_server):
    """Test validating a valid applicant."""
    applicant_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "ssn": "123456789",
    }

    result = await applicant_db_server.validate_applicant(applicant_data)
    assert result["valid"] is True
    assert len(result["errors"]) == 0


@pytest.mark.asyncio
async def test_validate_applicant_invalid(applicant_db_server):
    """Test validating an invalid applicant."""
    applicant_data = {
        "first_name": "John",
        "email": "john@example.com",
    }

    result = await applicant_db_server.validate_applicant(applicant_data)
    assert result["valid"] is False
    assert len(result["errors"]) > 0


@pytest.mark.asyncio
async def test_calculate_income_stability_high(applicant_db_server):
    """Test income stability calculation for stable employment."""
    employment_data = {
        "job_title": "Engineer",
        "years_employed": 7,
    }

    result = await applicant_db_server.calculate_income_stability(employment_data)
    assert result["stability_score"] == 0.9
    assert result["assessment"] == "Stable"


@pytest.mark.asyncio
async def test_calculate_income_stability_low(applicant_db_server):
    """Test income stability calculation for unstable employment."""
    employment_data = {
        "job_title": "Contractor",
        "years_employed": 0.5,
    }

    result = await applicant_db_server.calculate_income_stability(employment_data)
    assert result["stability_score"] == 0.3
    assert result["assessment"] == "Unstable"


@pytest.mark.asyncio
async def test_get_tools(applicant_db_server):
    """Test retrieving available tools."""
    tools = await applicant_db_server.get_tools()
    assert len(tools) >= 2
    tool_names = [tool["name"] for tool in tools]
    assert "validate_applicant" in tool_names
    assert "calculate_income_stability" in tool_names

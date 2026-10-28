#!/usr/bin/env python3
"""Example usage of the Applicant Profile Agent.

This script demonstrates how to use the ApplicantProfileAgent to analyze
loan applicants and generate risk assessments.
"""

import json
from datetime import datetime
from agents.applicant_agent import ApplicantProfileAgent
from models.schemas import (
    ApplicantProfile,
    EmploymentInfo,
    CreditRecord,
    EmploymentType,
)


def example_qualified_applicant():
    """Example: Analysis of a well-qualified applicant."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Well-Qualified Applicant")
    print("=" * 80)

    # Create applicant data
    applicant = ApplicantProfile(
        first_name="Sarah",
        last_name="Johnson",
        email="sarah.johnson@example.com",
        phone="555-123-4567",
        date_of_birth="1985-03-15",
        ssn="123-45-6789",
        address="456 Oak Avenue",
        city="San Francisco",
        state="CA",
        zip_code="94105",
    )

    employment = EmploymentInfo(
        employment_type=EmploymentType.FULL_TIME,
        employer_name="TechCorp Industries",
        job_title="Senior Software Engineer",
        years_employed=8.5,
        annual_income=180000.0,
        monthly_income=15000.0,
    )

    credit = CreditRecord(
        credit_score=780,
        years_of_credit_history=15.0,
        number_of_accounts=8,
        delinquencies_last_24_months=0,
        public_records=0,
        current_debt=8000.0,
    )

    # Analyze
    agent = ApplicantProfileAgent()
    result = agent.analyze(applicant, employment, credit)

    # Display results
    print(f"\nApplicant: {applicant.first_name} {applicant.last_name}")
    print(f"Email: {applicant.email}")
    print(f"\nValidation Status: {result['validation_status']}")
    print(f"Profile Completeness: {result['profile_completeness']:.1f}%")
    print(f"\nIncome Stability Score: {result['income_stability_score']:.0f}/100 ({result['income_stability_level']})")
    print(f"Employment Risk Score: {result['employment_risk_score']:.0f}/100 ({result['employment_risk_level']})")
    print(f"\nCredit Summary:")
    print(f"  Score: {result['credit_summary']['score']} ({result['credit_summary']['score_category']})")
    print(f"  Risk Level: {result['credit_summary']['score_risk_level']}")
    print(f"  Accounts: {result['credit_summary']['number_of_accounts']}")
    print(f"  Recent Delinquencies: {result['credit_summary']['recent_delinquencies']}")
    print(f"\nCritical Issues: {len(result['critical_issues'])}")
    for issue in result['critical_issues']:
        print(f"  - {issue}")
    print(f"\nWarnings: {len(result['warnings'])}")
    for warning in result['warnings']:
        print(f"  - {warning}")
    print(f"\nAnomalies: {len(result['anomalies'])}")
    for anomaly in result['anomalies']:
        print(f"  - {anomaly}")
    print(f"\nAI Reasoning:\n{result['reasoning']}")


def example_risky_applicant():
    """Example: Analysis of a higher-risk applicant."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Higher-Risk Applicant")
    print("=" * 80)

    applicant = ApplicantProfile(
        first_name="Michael",
        last_name="Chen",
        email="m.chen@example.com",
        phone="555-987-6543",
        date_of_birth="1992-07-22",
        ssn="987-65-4321",
        address="789 Pine Street",
        city="Detroit",
        state="MI",
        zip_code="48201",
    )

    employment = EmploymentInfo(
        employment_type=EmploymentType.SELF_EMPLOYED,
        employer_name="Chen Consulting LLC",
        job_title="Consultant",
        years_employed=1.2,
        annual_income=55000.0,
        monthly_income=4583.33,
    )

    credit = CreditRecord(
        credit_score=620,
        years_of_credit_history=4.0,
        number_of_accounts=3,
        delinquencies_last_24_months=1,
        public_records=0,
        current_debt=32000.0,
    )

    # Analyze
    agent = ApplicantProfileAgent()
    result = agent.analyze(applicant, employment, credit)

    # Display results
    print(f"\nApplicant: {applicant.first_name} {applicant.last_name}")
    print(f"Email: {applicant.email}")
    print(f"\nValidation Status: {result['validation_status']}")
    print(f"Profile Completeness: {result['profile_completeness']:.1f}%")
    print(f"\nIncome Stability Score: {result['income_stability_score']:.0f}/100 ({result['income_stability_level']})")
    print(f"Employment Risk Score: {result['employment_risk_score']:.0f}/100 ({result['employment_risk_level']})")
    print(f"\nCredit Summary:")
    print(f"  Score: {result['credit_summary']['score']} ({result['credit_summary']['score_category']})")
    print(f"  Risk Level: {result['credit_summary']['score_risk_level']}")
    print(f"  Accounts: {result['credit_summary']['number_of_accounts']}")
    print(f"  Recent Delinquencies: {result['credit_summary']['recent_delinquencies']}")
    print(f"  Debt-to-Income Ratio: {result['credit_summary'].get('debt_to_income_ratio', 'N/A')}")
    print(f"\nCritical Issues: {len(result['critical_issues'])}")
    for issue in result['critical_issues']:
        print(f"  - {issue}")
    print(f"\nWarnings: {len(result['warnings'])}")
    for warning in result['warnings']:
        print(f"  - {warning}")
    print(f"\nAnomalies: {len(result['anomalies'])}")
    for anomaly in result['anomalies']:
        print(f"  - {anomaly}")
    print(f"\nAI Reasoning:\n{result['reasoning']}")


def example_incomplete_application():
    """Example: Analysis of incomplete application data."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Incomplete Application")
    print("=" * 80)

    applicant = ApplicantProfile(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="555-555-5555",
        date_of_birth="1990-01-01",
        ssn="111-11-1111",
        address="",  # Empty
        city="",     # Empty
        state="CA",
        zip_code="",  # Empty
    )

    employment = EmploymentInfo(
        employment_type=EmploymentType.FULL_TIME,
        employer_name="Unknown Corp",
        job_title="Employee",
        years_employed=0.5,
        annual_income=45000.0,
        monthly_income=None,  # Not provided
    )

    credit = CreditRecord(
        credit_score=600,
        years_of_credit_history=1.0,
        number_of_accounts=1,
        delinquencies_last_24_months=0,
        public_records=0,
        current_debt=5000.0,
    )

    # Analyze
    agent = ApplicantProfileAgent()
    result = agent.analyze(applicant, employment, credit)

    # Display results
    print(f"\nApplicant: {applicant.first_name} {applicant.last_name}")
    print(f"Email: {applicant.email}")
    print(f"\nValidation Status: {result['validation_status']}")
    print(f"Profile Completeness: {result['profile_completeness']:.1f}%")
    print(f"\nIncome Stability Score: {result['income_stability_score']:.0f}/100 ({result['income_stability_level']})")
    print(f"Employment Risk Score: {result['employment_risk_score']:.0f}/100 ({result['employment_risk_level']})")
    print(f"\nCritical Issues: {len(result['critical_issues'])}")
    for issue in result['critical_issues']:
        print(f"  - {issue}")
    print(f"\nWarnings: {len(result['warnings'])}")
    for warning in result['warnings']:
        print(f"  - {warning}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  Applicant Profile Agent - Usage Examples".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        example_qualified_applicant()
        example_risky_applicant()
        example_incomplete_application()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        print("Make sure to:")
        print("1. Set ANTHROPIC_API_KEY environment variable")
        print("2. Install dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    main()

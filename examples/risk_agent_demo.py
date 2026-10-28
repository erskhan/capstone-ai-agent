#!/usr/bin/env python3
"""
Demonstration of the Financial Risk Analysis Agent.

This script shows how to use the risk agent in various scenarios
and demonstrates the analysis results.
"""

import asyncio
from datetime import datetime

from agents.risk_agent import get_risk_agent
from models.schemas import (
    ApplicantProfile,
    EmploymentInfo,
    CreditRecord,
    LoanDetails,
    LoanApplicationRequest,
    EmploymentType,
)


def create_sample_applications():
    """Create sample loan applications for demonstration."""

    # Applicant 1: Strong profile - likely approval
    strong_applicant = LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="Sarah",
            last_name="Anderson",
            email="sarah.anderson@email.com",
            phone="555-0123",
            date_of_birth="1985-03-15",
            ssn="123-45-6789",
            address="456 Oak Drive",
            city="Springfield",
            state="IL",
            zip_code="62701",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.FULL_TIME,
            employer_name="Fortune 500 Tech",
            job_title="Senior Software Architect",
            years_employed=8.5,
            annual_income=150000.0,
            monthly_income=12500.0,
        ),
        credit_record=CreditRecord(
            credit_score=785,
            years_of_credit_history=16.0,
            number_of_accounts=9,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=25000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=50000.0,
            loan_purpose="Home improvement",
            loan_term_months=84,
            interest_rate=4.25,
        ),
    )

    # Applicant 2: Weak profile - likely rejection/review
    weak_applicant = LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="Marcus",
            last_name="Thompson",
            email="marcus.t@email.com",
            phone="555-9876",
            date_of_birth="1992-07-22",
            ssn="987-65-4321",
            address="789 Pine Street",
            city="Shelbyville",
            state="IL",
            zip_code="62702",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.SELF_EMPLOYED,
            employer_name="Freelance Consulting",
            job_title="Independent Consultant",
            years_employed=1.2,
            annual_income=42000.0,
            monthly_income=3500.0,
        ),
        credit_record=CreditRecord(
            credit_score=585,
            years_of_credit_history=3.5,
            number_of_accounts=2,
            delinquencies_last_24_months=3,
            public_records=1,
            current_debt=32000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=200000.0,
            loan_purpose="Debt consolidation",
            loan_term_months=120,
            interest_rate=11.5,
        ),
    )

    # Applicant 3: Moderate profile - requires review
    moderate_applicant = LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="Jennifer",
            last_name="Chen",
            email="j.chen@email.com",
            phone="555-5555",
            date_of_birth="1988-11-08",
            ssn="555-55-5555",
            address="321 Elm Avenue",
            city="Capital City",
            state="IL",
            zip_code="62701",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.FULL_TIME,
            employer_name="Regional Manufacturing",
            job_title="Plant Operations Manager",
            years_employed=4.2,
            annual_income=72000.0,
            monthly_income=6000.0,
        ),
        credit_record=CreditRecord(
            credit_score=680,
            years_of_credit_history=6.0,
            number_of_accounts=5,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=22000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=40000.0,
            loan_purpose="Vehicle purchase",
            loan_term_months=60,
            interest_rate=6.75,
        ),
    )

    return [
        ("Strong Applicant", strong_applicant),
        ("Weak Applicant", weak_applicant),
        ("Moderate Applicant", moderate_applicant),
    ]


async def analyze_application(name: str, application: LoanApplicationRequest):
    """Analyze a single application and print results."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {name}")
    print(f"{'='*80}\n")

    agent = get_risk_agent()

    # Print applicant info
    print(f"Applicant: {application.applicant_profile.first_name} "
          f"{application.applicant_profile.last_name}")
    print(f"Email: {application.applicant_profile.email}")
    print(f"Phone: {application.applicant_profile.phone}")
    print()

    # Print employment info
    print("Employment Information:")
    print(f"  Employment Type: {application.employment_info.employment_type.value}")
    print(f"  Employer: {application.employment_info.employer_name}")
    print(f"  Job Title: {application.employment_info.job_title}")
    print(f"  Years Employed: {application.employment_info.years_employed:.1f}")
    print(f"  Annual Income: ${application.employment_info.annual_income:,.2f}")
    print()

    # Print credit info
    print("Credit Information:")
    print(f"  Credit Score: {application.credit_record.credit_score}")
    print(f"  Years of Credit History: {application.credit_record.years_of_credit_history:.1f}")
    print(f"  Number of Accounts: {application.credit_record.number_of_accounts}")
    print(f"  Delinquencies (last 24mo): {application.credit_record.delinquencies_last_24_months}")
    print(f"  Public Records: {application.credit_record.public_records}")
    print(f"  Current Debt: ${application.credit_record.current_debt:,.2f}")
    print()

    # Print loan details
    print("Loan Details:")
    print(f"  Loan Amount: ${application.loan_details.loan_amount:,.2f}")
    print(f"  Loan Purpose: {application.loan_details.loan_purpose}")
    print(f"  Loan Term: {application.loan_details.loan_term_months} months")
    print(f"  Interest Rate: {application.loan_details.interest_rate}%")
    print()

    print("Performing Risk Analysis...")
    print("-" * 80)

    try:
        result = await agent.analyze(application)

        # Print risk assessment results
        print("\nRISK ASSESSMENT RESULTS:")
        print(f"  Overall Risk Score: {result['risk_score']:.1f}/100")

        risk_category = (
            "HIGH" if result['risk_score'] >= 70
            else "MEDIUM" if result['risk_score'] >= 40
            else "LOW"
        )
        print(f"  Risk Category: {risk_category}")
        print()

        print("DTI Analysis:")
        print(f"  DTI Ratio: {result['dti_ratio']:.2f}%")
        print(f"  DTI Risk Level: {result['dti_risk_level'].upper()}")
        print()

        print("Credit Assessment:")
        print(f"  Credit Score: {result['credit_score_value']}")
        print(f"  Credit Risk Level: {result['credit_risk'].upper()}")
        print()

        print("Loan Amount Risk:")
        print(f"  Risk Level: {result['loan_amount_risk'].upper()}")
        print()

        if result['anomalies']:
            print("Anomalies Detected:")
            for i, anomaly in enumerate(result['anomalies'], 1):
                print(f"  {i}. {anomaly}")
            print()
        else:
            print("Anomalies Detected: None")
            print()

        if result['risk_factors']:
            print("Risk Factors:")
            for i, factor in enumerate(result['risk_factors'], 1):
                print(f"  {i}. {factor}")
            print()

        if result['positive_factors']:
            print("Positive Factors:")
            for i, factor in enumerate(result['positive_factors'], 1):
                print(f"  {i}. {factor}")
            print()

        if result.get('claude_analysis'):
            print("Claude AI Pattern Analysis:")
            print("-" * 40)
            # Print first 500 chars of analysis
            analysis = result['claude_analysis']
            if len(analysis) > 500:
                print(analysis[:500] + "...")
            else:
                print(analysis)
            print()

        print("Analysis completed at:", result['analyzed_at'])
        print()

        # Recommendation
        print("RECOMMENDATION:")
        if result['risk_score'] < 40:
            print("  Status: LIKELY APPROVAL")
            print("  Suggested Interest Rate: 4.5% - 5.5%")
        elif result['risk_score'] < 70:
            print("  Status: REQUIRES MANUAL REVIEW")
            print("  Recommended Action: Loan officer review and verification")
        else:
            print("  Status: LIKELY REJECTION OR MANUAL REVIEW")
            print("  Recommended Action: Request additional documentation or decline")

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run the demonstration."""
    print("\n" + "=" * 80)
    print("FINANCIAL RISK ANALYSIS AGENT DEMONSTRATION")
    print("=" * 80)
    print()
    print("This demonstration shows the risk assessment capabilities of the")
    print("Financial Risk Analysis Agent for the Intelligent Loan Approval System.")
    print()

    applications = create_sample_applications()

    for name, application in applications:
        await analyze_application(name, application)
        await asyncio.sleep(1)  # Small delay between analyses

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETED")
    print("=" * 80)
    print()
    print("Summary:")
    print("- The Financial Risk Analysis Agent successfully processed 3 sample applications")
    print("- Each application was analyzed across multiple risk dimensions")
    print("- Risk scores were calculated using weighted factors")
    print("- Anomalies were detected where applicable")
    print("- Claude AI provided pattern analysis and insights")
    print()
    print("Next Steps:")
    print("1. Integration with Orchestrator for workflow management")
    print("2. Integration with Decision Agent for final determination")
    print("3. API endpoint exposure for external systems")
    print("4. Compliance and audit logging")
    print()


if __name__ == "__main__":
    asyncio.run(main())

"""Loan Application Submission Page."""

import streamlit as st
import requests
import json
from datetime import date
from typing import Dict, Any

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Submit Application", page_icon="📝", layout="wide")

st.title("📝 Submit Loan Application")
st.markdown("*Fill out the form below to apply for a loan*")


def validate_form(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate form data."""
    errors = []

    if not data["first_name"] or not data["last_name"]:
        errors.append("First and last names are required")

    if not data["email"] or "@" not in data["email"]:
        errors.append("Valid email is required")

    if not data["ssn"] or len(data["ssn"].replace("-", "")) != 9:
        errors.append("Valid SSN (9 digits) is required")

    if data["annual_income"] <= 0:
        errors.append("Annual income must be greater than 0")

    if data["loan_amount"] <= 0 or data["loan_amount"] > 10_000_000:
        errors.append("Loan amount must be between $1 and $10,000,000")

    if 300 > data["credit_score"] > 850:
        errors.append("Credit score must be between 300 and 850")

    return len(errors) == 0, "\n".join(errors)


def submit_application(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit application to API."""
    try:
        response = requests.post(f"{API_URL}/api/applications", json=form_data, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    """Main application submission form."""
    with st.form("loan_application_form"):
        # Applicant Information Section
        st.subheader("👤 Applicant Information")
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name *")
            email = st.text_input("Email Address *")
            dob = st.date_input("Date of Birth *", min_value=date(1920, 1, 1), max_value=date.today())

        with col2:
            last_name = st.text_input("Last Name *")
            phone = st.text_input("Phone Number *")
            ssn = st.text_input("Social Security Number * (9 digits)", type="password")

        # Address Section
        st.subheader("🏠 Address Information")
        address = st.text_input("Street Address *")
        col1, col2, col3 = st.columns(3)

        with col1:
            city = st.text_input("City *")
        with col2:
            state = st.selectbox(
                "State *",
                [
                    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
                ],
            )
        with col3:
            zip_code = st.text_input("ZIP Code *")

        # Employment Section
        st.subheader("💼 Employment Information")
        col1, col2 = st.columns(2)

        with col1:
            employment_type = st.selectbox(
                "Employment Type *",
                ["full_time", "part_time", "self_employed", "retired", "student", "unemployed"],
            )
            employer_name = st.text_input("Employer Name *")
            years_employed = st.number_input("Years Employed *", min_value=0.0, max_value=70.0, value=5.0)

        with col2:
            job_title = st.text_input("Job Title *")
            annual_income = st.number_input("Annual Income ($) *", min_value=0, value=60000)
            monthly_income = st.number_input("Monthly Income ($) (optional)", min_value=0)

        # Credit Information Section
        st.subheader("📊 Credit Information")
        col1, col2 = st.columns(2)

        with col1:
            credit_score = st.slider("Credit Score *", min_value=300, max_value=850, value=700)
            years_of_credit = st.number_input("Years of Credit History *", min_value=0.0, max_value=80.0, value=10.0)
            number_of_accounts = st.number_input("Number of Credit Accounts *", min_value=0, value=5)

        with col2:
            delinquencies = st.number_input("Delinquencies (last 24 months) *", min_value=0, value=0)
            public_records = st.number_input("Public Records *", min_value=0, value=0)
            current_debt = st.number_input("Current Total Debt ($) *", min_value=0, value=0)

        # Loan Details Section
        st.subheader("💳 Loan Details")
        col1, col2 = st.columns(2)

        with col1:
            loan_amount = st.number_input("Loan Amount ($) *", min_value=1000, max_value=10_000_000, value=200_000)
            loan_purpose = st.selectbox(
                "Loan Purpose *",
                ["Home", "Auto", "Business", "Debt Consolidation", "Personal", "Education", "Other"],
            )

        with col2:
            loan_term_months = st.selectbox(
                "Loan Term (months) *",
                [6, 12, 24, 36, 48, 60, 84, 120, 180, 360],
            )
            interest_rate = st.number_input("Expected Interest Rate (%) (optional)", min_value=0.0, max_value=30.0)

        # Additional Notes
        st.subheader("📝 Additional Information")
        additional_notes = st.text_area("Additional Notes (optional, max 1000 chars)", max_chars=1000)

        # Form Submission
        submitted = st.form_submit_button("🚀 Submit Application", use_container_width=True, type="primary")

    if submitted:
        # Validate form
        form_data = {
            "applicant_profile": {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "date_of_birth": dob.isoformat(),
                "ssn": ssn,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
            },
            "employment_info": {
                "employment_type": employment_type,
                "employer_name": employer_name,
                "job_title": job_title,
                "years_employed": years_employed,
                "annual_income": float(annual_income),
                "monthly_income": float(monthly_income) if monthly_income > 0 else None,
            },
            "credit_record": {
                "credit_score": int(credit_score),
                "years_of_credit_history": years_of_credit,
                "number_of_accounts": int(number_of_accounts),
                "delinquencies_last_24_months": int(delinquencies),
                "public_records": int(public_records),
                "current_debt": float(current_debt),
            },
            "loan_details": {
                "loan_amount": float(loan_amount),
                "loan_purpose": loan_purpose,
                "loan_term_months": int(loan_term_months),
                "interest_rate": float(interest_rate) if interest_rate > 0 else None,
            },
            "additional_notes": additional_notes if additional_notes else None,
        }

        is_valid, error_message = validate_form(form_data)

        if not is_valid:
            st.error(f"❌ Form Validation Error:\n{error_message}")
        else:
            with st.spinner("📤 Submitting your application..."):
                result = submit_application(form_data)

                if "error" in result:
                    st.error(f"❌ Error submitting application: {result['error']}")
                elif "application_id" in result:
                    st.success("✅ Application submitted successfully!")
                    st.info(f"**Your Application ID:** `{result['application_id']}`")
                    st.info(f"**Status:** {result['status']}")
                    st.info("You can check your application status using your Application ID.")

                    # Store in session for easy access
                    st.session_state.last_application_id = result['application_id']
                else:
                    st.error(f"❌ Unexpected response: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()

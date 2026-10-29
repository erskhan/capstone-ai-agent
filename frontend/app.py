"""Streamlit frontend application."""

import streamlit as st
import requests
from datetime import datetime
from datetime import date

today = date.today()

st.set_page_config(
    page_title="Loan Approval System",
    page_icon="💰",
    layout="wide",
)

st.title("💰 Intelligent Loan Approval System")
st.markdown("*Powered by Agentic AI*")

API_URL = "http://localhost:8000"


def main():
    """Main application function."""
    tab1, tab2, tab3 = st.tabs(
        ["Submit Application", "Check Status", "Application History"]
    )

    with tab1:
        st.header("Submit New Loan Application")

        with st.form("application_form"):
            st.subheader("Applicant Information")
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("First Name", key="first_name")
                email = st.text_input("Email", key="email")
                date_of_birth = st.date_input(
                    "Date of Birth", key="dob",
                    min_value=date(today.year -100, 1, 1),
                    max_value=today
                    )

            with col2:
                last_name = st.text_input("Last Name", key="last_name")
                phone = st.text_input("Phone Number", key="phone")
                ssn = st.text_input("Social Security Number", type="password", key="ssn")

            st.subheader("Address")
            address = st.text_input("Street Address", key="address")
            col1, col2, col3 = st.columns(3)
            with col1:
                city = st.text_input("City", key="city")
            with col2:
                state = st.text_input("State", max_chars=10, key="state")
            with col3:
                zip_code = st.text_input("ZIP Code", key="zip_code")

            st.subheader("Employment Information")
            col1, col2 = st.columns(2)
            with col1:
                employment_type = st.selectbox(
                    "Employment Type",
                    ["full_time", "part_time", "self_employed", "retired"],
                    key="emp_type",
                )
                employer_name = st.text_input("Employer Name", key="employer")
                years_employed = st.number_input(
                    "Years Employed", min_value=0.0, max_value=70.0, key="years_emp"
                )
            with col2:
                job_title = st.text_input("Job Title", key="job_title")
                annual_income = st.number_input(
                    "Annual Income", min_value=0, key="annual_income"
                )

            st.subheader("Credit Information")
            col1, col2 = st.columns(2)
            with col1:
                credit_score = st.slider(
                    "Credit Score", min_value=300, max_value=850, value=700, key="credit_score"
                )
                years_of_credit = st.number_input(
                    "Years of Credit History", min_value=0.0, max_value=80.0, key="credit_years"
                )
                number_of_accounts = st.number_input(
                    "Number of Accounts", min_value=0, key="num_accounts"
                )
            with col2:
                delinquencies = st.number_input(
                    "Delinquencies (last 24 months)", min_value=0, key="delinquencies"
                )
                public_records = st.number_input(
                    "Public Records", min_value=0, key="public_records"
                )
                current_debt = st.number_input(
                    "Current Debt", min_value=0, key="current_debt"
                )

            st.subheader("Loan Details")
            col1, col2 = st.columns(2)
            with col1:
                loan_amount = st.number_input(
                    "Loan Amount", min_value=1000, key="loan_amount"
                )
                loan_purpose = st.text_input("Loan Purpose", key="loan_purpose")
            with col2:
                loan_term = st.slider(
                    "Loan Term (months)", min_value=6, max_value=360, value=60, key="loan_term"
                )

            submitted = st.form_submit_button("Submit Application", type="primary")

            if submitted:
                try:
                    application_data = {
                        "applicant_profile": {
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                            "phone": phone,
                            "date_of_birth": date_of_birth.strftime("%Y-%m-%d"),
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
                            "annual_income": annual_income,
                        },
                        "credit_record": {
                            "credit_score": credit_score,
                            "years_of_credit_history": years_of_credit,
                            "number_of_accounts": number_of_accounts,
                            "delinquencies_last_24_months": delinquencies,
                            "public_records": public_records,
                            "current_debt": current_debt,
                        },
                        "loan_details": {
                            "loan_amount": loan_amount,
                            "loan_purpose": loan_purpose,
                            "loan_term_months": loan_term,
                        },
                    }

                    response = requests.post(
                        f"{API_URL}/api/applications",
                        json=application_data,
                        timeout=10,
                    )

                    if response.status_code == 201:
                        st.success("✅ Application submitted successfully!")
                        result = response.json()
                        st.info(f"**Application ID:** {result['application_id']}")
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        """st.write(response.text)"""
                except Exception as e:
                    st.error(f"❌ Error submitting application: {str(e)}")

    with tab2:
        st.header("Check Application Status")

        application_id = st.text_input(
            "Enter Application ID",
            key="check_app_id",
            placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000",
        )

        if st.button("Search", key="search_btn"):
            try:
                response = requests.get(
                    f"{API_URL}/api/applications/{application_id}",
                    timeout=10,
                )

                if response.status_code == 200:
                    app_data = response.json()

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Status", app_data["status"])
                    with col2:
                        st.metric("Submitted", app_data["submitted_at"][:10])
                    with col3:
                        st.metric("Updated", app_data["updated_at"][:10])

                    if app_data.get("decision"):
                        st.subheader("Decision Details")
                        decision = app_data["decision"]
                        st.write(f"**Classification:** {decision['classification']}")
                        st.write(
                            f"**Confidence:** {decision['confidence_score']:.2%}"
                        )
                        st.write(f"**Reasoning:** {decision['reasoning']}")
                else:
                    st.error("❌ Application not found")
            except Exception as e:
                st.error(f"❌ Error fetching application: {str(e)}")

    with tab3:
        st.header("Application History")

        try:
            response = requests.get(f"{API_URL}/api/applications", timeout=10)

            if response.status_code == 200:
                data = response.json()
                st.metric("Total Applications", data["total"])

                if data["applications"]:
                    for app in data["applications"]:
                        with st.expander(
                            f"ID: {app['application_id']} - {app['status']}"
                        ):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Status:** {app['status']}")
                                st.write(f"**Submitted:** {app['submitted_at']}")
                            with col2:
                                st.write(f"**Updated:** {app['updated_at']}")
                else:
                    st.info("No applications found")
        except Exception as e:
            st.error(f"❌ Error fetching applications: {str(e)}")


if __name__ == "__main__":
    main()

"""Appeal Submission Page."""

import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Submit Appeal", page_icon="🗣️", layout="wide")

st.title("🗣️ Submit Appeal")
st.markdown("*You have 30 days to appeal a rejected application*")


def submit_appeal(application_id: str, appeal_data: dict):
    """Submit appeal to API."""
    try:
        response = requests.post(
            f"{API_URL}/api/applications/{application_id}/appeal",
            json=appeal_data,
            timeout=10,
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    """Main appeal submission interface."""
    # Application ID Input
    col1, col2 = st.columns([3, 1])

    with col1:
        application_id = st.text_input(
            "Application ID *",
            value=st.session_state.get("appeal_application_id", ""),
            placeholder="Enter the application ID to appeal",
        )

    with col2:
        st.write("")  # Spacing
        st.write("")

    if not application_id:
        st.info("ℹ️ Please enter an application ID to proceed with the appeal.")
        return

    # Appeal Form
    st.subheader("📝 Appeal Details")

    with st.form("appeal_form"):
        st.markdown(
            """
            **Why are you appealing?**

            Please provide a detailed explanation of why you believe the decision should be reconsidered.
            Be specific about any circumstances that might not have been fully considered.
            """
        )

        appeal_reason = st.text_area(
            "Appeal Reason (required - minimum 20 characters) *",
            height=200,
            placeholder="Explain why you believe the decision should be reconsidered...",
            max_chars=2000,
        )

        st.markdown("---")
        st.markdown("**Additional Information**")

        additional_docs = st.text_area(
            "Additional Documentation (optional)",
            height=150,
            placeholder="Upload or describe any additional documents that support your appeal...",
            max_chars=5000,
        )

        st.markdown("---")
        st.markdown("**Contact Information**")

        col1, col2 = st.columns(2)
        with col1:
            contact_email = st.text_input("Contact Email (optional)")
        with col2:
            contact_phone = st.text_input("Contact Phone (optional)")

        # Acknowledgment
        st.markdown("---")
        acknowledge = st.checkbox(
            "I certify that the information provided in this appeal is true and accurate"
        )

        # Submit Button
        submitted = st.form_submit_button("🗣️ Submit Appeal", use_container_width=True, type="primary")

    if submitted:
        # Validation
        if len(appeal_reason.strip()) < 20:
            st.error("❌ Appeal reason must be at least 20 characters long")
        elif not acknowledge:
            st.error("❌ You must acknowledge that the information is accurate")
        else:
            appeal_data = {
                "application_id": application_id,
                "appeal_reason": appeal_reason,
                "additional_documentation": additional_docs if additional_docs else None,
                "contact_email": contact_email if contact_email else None,
                "contact_phone": contact_phone if contact_phone else None,
            }

            with st.spinner("📤 Submitting your appeal..."):
                result = submit_appeal(application_id, appeal_data)

                if "error" in result:
                    st.error(f"❌ Error submitting appeal: {result['error']}")
                elif "appeal_id" in result:
                    st.success("✅ Appeal submitted successfully!")
                    st.info(f"**Appeal ID:** `{result['appeal_id']}`")
                    st.info(f"**Status:** {result['status']}")
                    st.info(
                        f"**Expected Decision:** {result.get('expected_decision_date', 'Within 15 business days')}"
                    )

                    st.markdown("---")
                    st.success(
                        """
                        **Thank you for your appeal!**

                        **What happens next:**
                        1. Your appeal has been received and assigned to a reviewer
                        2. A senior loan officer will review your appeal and any additional documentation
                        3. You will receive a decision within 15 business days
                        4. You will be notified by email at the address provided

                        **What you can do:**
                        - Check your email for updates on your appeal
                        - Contact us if you have questions: 1-800-LOAN-APP
                        """
                    )
                else:
                    st.error(f"❌ Unexpected error: {result}")

    # Appeal Rights Information
    with st.expander("📚 Appeal Rights & Process", expanded=False):
        st.markdown(
            """
            ### Your Appeal Rights

            Under the Fair Credit Reporting Act (FCRA) and Equal Credit Opportunity Act (ECOA),
            you have the right to appeal a loan decision.

            **Timeline:**
            - You have **30 days** from the date of the decision to submit an appeal
            - We will review your appeal within **15 business days**
            - You will be notified of the outcome via email and phone

            **What We Review:**
            - New or additional information you provide
            - Your credit report for accuracy
            - All decision factors from the original evaluation
            - Any circumstances that may have been overlooked

            **Possible Outcomes:**
            - ✅ Appeal Approved: Your loan is approved with new terms
            - ❌ Appeal Denied: The original decision is upheld
            - ⏳ Further Review: We request additional information

            **Questions?**
            Contact our Appeals Department:
            - Phone: 1-800-LOAN-APP
            - Email: appeals@loanapp.com
            - Hours: Monday - Friday, 9 AM - 5 PM EST
            """
        )


if __name__ == "__main__":
    main()

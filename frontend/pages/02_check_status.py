"""Application Status Checking Page."""

import streamlit as st
import requests
from datetime import datetime

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Check Status", page_icon="🔍", layout="wide")

st.title("🔍 Check Application Status")
st.markdown("*Enter your application ID to check the status*")


def get_application_status(application_id: str):
    """Get application status from API."""
    try:
        response = requests.get(f"{API_URL}/api/applications/{application_id}", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_workflow_state(application_id: str):
    """Get workflow execution state."""
    try:
        response = requests.get(f"{API_URL}/api/applications/{application_id}/workflow-state", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_decision(application_id: str):
    """Get full decision details."""
    try:
        response = requests.get(f"{API_URL}/api/applications/{application_id}/decision", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def format_status_badge(status: str) -> str:
    """Format status as a color-coded badge."""
    badges = {
        "submitted": "⏳ Submitted",
        "validating": "🔄 Validating",
        "under_review": "👀 Under Review",
        "approved": "✅ Approved",
        "rejected": "❌ Rejected",
        "manual_review": "👨‍⚖️ Manual Review",
        "appealed": "🗣️ Appealed",
    }
    return badges.get(status, status)


def main():
    """Main status checking interface."""
    col1, col2 = st.columns([3, 1])

    with col1:
        application_id = st.text_input(
            "Enter Application ID",
            value=st.session_state.get("last_application_id", ""),
            placeholder="e.g., a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        )

    with col2:
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")

    if search_button and application_id:
        with st.spinner("Loading application details..."):
            # Get status
            status_result = get_application_status(application_id)
            workflow_result = get_workflow_state(application_id)
            decision_result = get_decision(application_id)

            if "error" in status_result:
                st.error(f"❌ Error: {status_result['error']}")
            else:
                # Application Status Card
                st.subheader("📋 Application Status")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Application ID", application_id[:8] + "...")
                with col2:
                    status = status_result.get("status", "Unknown")
                    st.metric("Status", format_status_badge(status))
                with col3:
                    submitted_at = status_result.get("submitted_at", "N/A")
                    if submitted_at:
                        st.metric("Submitted", submitted_at[:10])
                    else:
                        st.metric("Submitted", "N/A")
                with col4:
                    updated_at = status_result.get("updated_at", "N/A")
                    if updated_at:
                        st.metric("Updated", updated_at[:10])
                    else:
                        st.metric("Updated", "N/A")

                # Workflow State Details
                if "error" not in workflow_result:
                    st.subheader("⚙️ Workflow Execution")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Workflow State",
                            workflow_result.get("workflow_state", "unknown"),
                        )
                    with col2:
                        st.metric(
                            "Current Step",
                            workflow_result.get("current_step", "unknown"),
                        )
                    with col3:
                        st.metric(
                            "Attempt #",
                            workflow_result.get("attempt_number", 0),
                        )

                    # Timeline
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        started = workflow_result.get("started_at")
                        st.text(f"Started: {started[:10] if started else 'N/A'}")
                    with col2:
                        completed = workflow_result.get("completed_at")
                        st.text(f"Completed: {completed[:10] if completed else 'N/A'}")
                    with col3:
                        if workflow_result.get("error_message"):
                            st.error(f"Error: {workflow_result['error_message']}")

                # Decision Details
                if "error" not in decision_result and decision_result.get("classification"):
                    st.subheader("📊 Decision Details")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        classification = decision_result.get("classification", "unknown")
                        if classification == "approved":
                            st.success(f"**Classification: {classification.upper()}**")
                        elif classification == "rejected":
                            st.error(f"**Classification: {classification.upper()}**")
                        else:
                            st.warning(f"**Classification: {classification.upper()}**")

                    with col2:
                        confidence = decision_result.get("confidence_score", 0)
                        st.metric("Confidence Score", f"{confidence:.1%}")

                    with col3:
                        risk_score = decision_result.get("risk_score", 0)
                        st.metric("Risk Score", f"{risk_score:.0f}/100")

                    # Decision Reasoning
                    if decision_result.get("reasoning"):
                        with st.expander("📝 Decision Reasoning"):
                            st.write(decision_result["reasoning"])

                    # Decision Factors
                    if decision_result.get("decision_factors"):
                        factors = decision_result["decision_factors"]
                        col1, col2 = st.columns(2)

                        with col1:
                            if factors.get("positive_factors"):
                                st.success("✅ Positive Factors")
                                for factor in factors["positive_factors"]:
                                    st.write(f"• {factor}")

                        with col2:
                            if factors.get("risk_factors"):
                                st.error("⚠️ Risk Factors")
                                for factor in factors["risk_factors"]:
                                    st.write(f"• {factor}")

                    # Loan Terms (if approved)
                    if classification == "approved":
                        st.subheader("💰 Approved Loan Terms")
                        col1, col2 = st.columns(2)

                        with col1:
                            approved_amount = decision_result.get("approved_loan_amount")
                            if approved_amount:
                                st.metric("Approved Amount", f"${approved_amount:,.2f}")

                        with col2:
                            rate = decision_result.get("recommended_rate")
                            if rate:
                                st.metric("Recommended Rate", f"{rate:.2f}%")

                        # Conditions
                        if decision_result.get("conditions"):
                            st.info("**Loan Conditions:**")
                            for condition in decision_result["conditions"]:
                                st.write(f"• {condition}")

                    # Next Steps
                    st.subheader("📌 Next Steps")
                    if classification == "approved":
                        st.info(
                            """
                            🎉 **Congratulations!** Your loan has been approved.

                            **Next steps:**
                            1. A loan officer will contact you within 1 business day
                            2. Review and sign the loan documents
                            3. Funds will be disbursed within 5-7 business days
                            """
                        )
                    elif classification == "rejected":
                        st.error(
                            """
                            😢 **Application Rejected**

                            **You have the right to:**
                            1. Review your credit report
                            2. Appeal this decision within 30 days
                            3. Reapply after 6 months with improved credit

                            **To Appeal:** Click the "Submit Appeal" button on the home page
                            """
                        )
                    else:
                        st.warning(
                            """
                            ⏳ **Application Under Review**

                            **What to expect:**
                            1. Our team is reviewing your application
                            2. You may receive requests for additional information
                            3. A decision will be made within 3-5 business days

                            Check back soon for an update!
                            """
                        )

                    # Appeal Button (if rejected)
                    if classification == "rejected":
                        if st.button("🗣️ Submit Appeal", use_container_width=True):
                            st.session_state.appeal_application_id = application_id
                            st.switch_page("pages/03_view_decision.py")


if __name__ == "__main__":
    main()

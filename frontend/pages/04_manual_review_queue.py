"""Manual Review Queue for Loan Officers - Admin Only."""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Manual Review Queue", page_icon="👨‍⚖️", layout="wide")

# Check if user is logged in as admin
if st.session_state.get("user_type") != "admin":
    st.error("❌ Please login as Admin to access the Manual Review Queue")
    st.info("Go back to home page and login with admin password")
    st.stop()

st.title("👨‍⚖️ Manual Review Queue")
st.markdown("*Review applications requiring manual decision*")

# Show logout button
col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🔓 Logout", key="manual_review_top_logout"):
        st.session_state.user_type = None
        st.session_state.admin_authenticated = False
        st.rerun()

st.markdown("---")

if True:  # Removed authentication check since it's done above
    # Get all applications
    def get_all_applications():
        """Get all applications from API."""
        try:
            response = requests.get(f"{API_URL}/api/applications?limit=1000", timeout=10)
            data = response.json()
            return data.get("applications", [])
        except Exception as e:
            st.error(f"Error fetching applications: {e}")
            return []

    def get_application_full_details(application_id: str):
        """Get full application details including decision."""
        try:
            status_resp = requests.get(f"{API_URL}/api/applications/{application_id}", timeout=10)
            decision_resp = requests.get(f"{API_URL}/api/applications/{application_id}/decision", timeout=10)
            workflow_resp = requests.get(f"{API_URL}/api/applications/{application_id}/workflow-state", timeout=10)

            return {
                "status": status_resp.json() if status_resp.status_code == 200 else {},
                "decision": decision_resp.json() if decision_resp.status_code == 200 else {},
                "workflow": workflow_resp.json() if workflow_resp.status_code == 200 else {},
            }
        except Exception as e:
            st.error(f"Error fetching details: {e}")
            return {}

    def submit_manual_review(application_id: str, decision_data: dict):
        """Submit manual review decision to API."""
        try:
            response = requests.post(
                f"{API_URL}/api/applications/{application_id}/manual-review",
                json=decision_data,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    # Stats Section
    st.subheader("📊 Queue Statistics")

    applications = get_all_applications()

    if applications:
        # Filter for applications needing manual review
        manual_review_apps = [
            app for app in applications
            if app.get("status") in ["under_review", "manual_review"]
        ]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total in Queue", len(manual_review_apps))

        with col2:
            pending = sum(1 for app in manual_review_apps if app.get("status") == "under_review")
            st.metric("Pending Review", pending)

        with col3:
            total_apps = len(applications)
            st.metric("Total Applications", total_apps)

        with col4:
            approval_rate = sum(1 for app in applications if app.get("status") == "approved") / max(total_apps, 1) * 100
            st.metric("Approval Rate", f"{approval_rate:.1f}%")

        # Applications Table
        st.subheader("📋 Applications Requiring Review")

        if manual_review_apps:
            # Create dataframe for display
            display_data = []
            for app in manual_review_apps:
                # API returns application_id, not id
                app_id = app.get("application_id") or app.get("id", "")
                if not app_id:
                    continue

                # Get decision details for risk score
                details = get_application_full_details(app_id)
                risk_score = details.get("decision", {}).get("risk_score", "N/A")

                display_data.append({
                    "App ID": app_id[:8] + "...",
                    "Full ID": app_id,
                    "Status": app.get("status", "unknown").replace("_", " ").title(),
                    "Risk Score": f"{risk_score:.0f}/100" if isinstance(risk_score, (int, float)) else "N/A",
                    "Submitted": app.get("submitted_at", "")[:10] if app.get("submitted_at") else "N/A",
                    "Updated": app.get("updated_at", "")[:10] if app.get("updated_at") else "N/A",
                })

            if display_data:
                df = pd.DataFrame(display_data)

                # Display table
                st.dataframe(df[["App ID", "Status", "Risk Score", "Submitted", "Updated"]],
                            use_container_width=True, hide_index=True)

                # Review Selection
                st.subheader("🔍 Review Application")

                col1, col2 = st.columns([3, 1])

                with col1:
                    selected_index = st.selectbox(
                        "Select application to review:",
                        range(len(df)),
                        format_func=lambda i: f"{df.iloc[i]['App ID']} - Risk: {df.iloc[i]['Risk Score']} - {df.iloc[i]['Status']}"
                    )

                with col2:
                    if st.button("📂 Load Details", use_container_width=True, type="primary"):
                        selected_app_id = df.iloc[selected_index]["Full ID"]
                        if selected_app_id:
                            st.session_state.selected_app_id = selected_app_id

                # Application Details Panel
                if "selected_app_id" in st.session_state:
                    app_id = st.session_state.selected_app_id
                    if not app_id:
                        st.warning("⚠️ No application selected")
                    else:
                        st.markdown("---")
                        st.subheader("📝 Review Details")

                        details = get_application_full_details(app_id)

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Application ID", app_id[:12] + "...")

                        with col2:
                            risk_score = details.get("decision", {}).get("risk_score", "N/A")
                            st.metric("Risk Score", f"{risk_score:.0f}/100" if isinstance(risk_score, (int, float)) else "N/A")

                        with col3:
                            confidence = details.get("decision", {}).get("confidence_score", "N/A")
                            st.metric("AI Confidence", f"{confidence:.0%}" if isinstance(confidence, (int, float)) else "N/A")

                        # Decision Analysis
                        st.subheader("🧠 Agent Analysis")

                        decision = details.get("decision", {})

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("**✅ Positive Factors**")
                            positive_factors = decision.get("positive_factors", [])
                            if positive_factors:
                                for factor in positive_factors:
                                    st.write(f"• {factor}")
                            else:
                                st.write("No positive factors identified")

                        with col2:
                            st.markdown("**⚠️ Risk Factors**")
                            risk_factors = decision.get("risk_factors", [])
                            if risk_factors:
                                for factor in risk_factors:
                                    st.write(f"• {factor}")
                            else:
                                st.write("No risk factors identified")

                        # Decision Reasoning
                        if decision.get("reasoning"):
                            with st.expander("📋 Full Decision Reasoning"):
                                st.write(decision["reasoning"])

                        # Workflow State
                        workflow = details.get("workflow", {})
                        if workflow:
                            st.subheader("⚙️ Workflow Status")
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.text(f"State: {workflow.get('workflow_state', 'N/A')}")

                            with col2:
                                st.text(f"Current Step: {workflow.get('current_step', 'N/A')}")

                            with col3:
                                st.text(f"Attempts: {workflow.get('attempt_number', 0)}")

                        # Manual Review Form
                        st.markdown("---")
                        st.subheader("✅ Make Your Decision")

                        with st.form(f"review_form_{app_id}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                decision_type = st.radio(
                                    "Decision",
                                    ["approve", "reject", "request_info"],
                                    format_func=lambda x: {
                                        "approve": "✅ Approve",
                                        "reject": "❌ Reject",
                                        "request_info": "📋 Request More Information"
                                    }.get(x, x)
                                )

                            with col2:
                                priority = st.selectbox(
                                    "Priority for Communication",
                                    ["normal", "high", "urgent"],
                                    format_func=lambda x: {
                                        "normal": "🟢 Normal",
                                        "high": "🟡 High",
                                        "urgent": "🔴 Urgent"
                                    }.get(x, x)
                                )

                            # Decision-specific fields
                            if decision_type == "approve":
                                st.markdown("**Approval Details**")
                                col1, col2 = st.columns(2)

                                with col1:
                                    approved_amount = st.number_input(
                                        "Approved Loan Amount ($)",
                                        min_value=1000,
                                        max_value=10000000,
                                        value=250000,
                                        step=10000
                                    )

                                with col2:
                                    recommended_rate = st.number_input(
                                        "Recommended Interest Rate (%)",
                                        min_value=1.0,
                                        max_value=20.0,
                                        value=6.5,
                                        step=0.1
                                    )

                                conditions = st.text_area(
                                    "Loan Conditions (one per line)",
                                    value="Maintain employment for 6 months\nKeep debt-to-income below 45%",
                                    height=100
                                )

                            elif decision_type == "reject":
                                st.markdown("**Rejection Details**")
                                rejection_reason = st.selectbox(
                                    "Rejection Reason",
                                    [
                                        "Insufficient income",
                                        "High debt-to-income ratio",
                                        "Low credit score",
                                        "Employment verification failed",
                                        "Fraud indicators detected",
                                        "Unable to verify information",
                                        "Other - See notes"
                                    ]
                                )

                            else:  # request_info
                                st.markdown("**Information Request**")
                                documents = st.multiselect(
                                    "Requested Documents",
                                    [
                                        "Recent pay stubs (last 3 months)",
                                        "Tax returns (last 2 years)",
                                        "Employment verification letter",
                                        "Bank statements",
                                        "Proof of assets",
                                        "Identification documents",
                                        "Address verification",
                                        "Other - See notes"
                                    ],
                                    default=["Recent pay stubs (last 3 months)"]
                                )

                                deadline_days = st.slider(
                                    "Response Deadline (days)",
                                    min_value=1,
                                    max_value=30,
                                    value=7
                                )

                            # General notes
                            reviewer_notes = st.text_area(
                                "Reviewer Notes & Comments",
                                placeholder="Enter any additional notes about your decision...",
                                height=100
                            )

                            # Submit button
                            submitted = st.form_submit_button("📤 Submit Review Decision", type="primary", use_container_width=True)

                            if submitted:
                                # Build decision data
                                decision_data = {
                                    "decision": decision_type,
                                    "reviewer_notes": reviewer_notes,
                                    "reviewer_id": st.session_state.get("reviewer_id", "unknown"),
                                    "priority": priority,
                                }

                                if decision_type == "approve":
                                    decision_data.update({
                                        "approved_amount": float(approved_amount),
                                        "recommended_rate": float(recommended_rate),
                                        "conditions": [c.strip() for c in conditions.split("\n") if c.strip()],
                                    })

                                elif decision_type == "reject":
                                    decision_data.update({
                                        "rejection_reason": rejection_reason,
                                    })

                                else:  # request_info
                                    decision_data.update({
                                        "requested_documents": documents,
                                        "deadline_days": int(deadline_days),
                                    })

                                # Submit to API
                                with st.spinner("Processing your review decision..."):
                                    result = submit_manual_review(app_id, decision_data)

                                    if "error" in result:
                                        st.error(f"❌ Error submitting review: {result['error']}")
                                    else:
                                        st.success(f"✅ Review decision submitted successfully!")
                                        st.json(result)
                                        st.session_state.selected_app_id = None
                                        st.rerun()

        else:
            st.info("✅ No applications currently requiring manual review!")
            st.balloons()

    # Logout
    st.markdown("---")
    if st.button("🔓 Logout", key="manual_review_logout"):
        st.session_state.review_authenticated = False
        st.rerun()

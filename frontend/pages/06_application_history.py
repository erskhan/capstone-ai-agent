"""Application History & Search Page - Applicant Only."""

import streamlit as st
import requests
import pandas as pd

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Application History", page_icon="📚", layout="wide")

# Check if user is logged in as applicant
if st.session_state.get("user_type") != "applicant":
    st.error("❌ Please login as an Applicant to view your history")
    st.info("Go back to home page and login with your email")
    st.stop()

st.title("📚 Your Application History")
st.markdown("*View and search your own loan applications*")

# Show logout button
col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🔓 Logout", key="application_history_logout"):
        st.session_state.user_type = None
        st.session_state.user_email = None
        st.rerun()

st.markdown(f"**Logged in as:** {st.session_state.user_email}")
st.markdown("---")


def get_applications(user_email: str, skip: int = 0, limit: int = 20):
    """Get applications list from API filtered by email."""
    try:
        response = requests.get(
            f"{API_URL}/api/applications",
            params={"skip": skip, "limit": limit, "user_email": user_email},
            timeout=10,
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_audit_trail(application_id: str):
    """Get audit trail for an application."""
    try:
        response = requests.get(
            f"{API_URL}/api/applications/{application_id}/audit-trail",
            timeout=10,
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def format_status_badge(status: str) -> str:
    """Format status as a badge."""
    badges = {
        "submitted": "⏳",
        "validating": "🔄",
        "under_review": "👀",
        "approved": "✅",
        "rejected": "❌",
        "manual_review": "👨‍⚖️",
        "appealed": "🗣️",
    }
    return badges.get(status, "❓") + f" {status.replace('_', ' ').title()}"


def main():
    """Main application history interface."""
    # Filters
    st.subheader("🔍 Search & Filter")
    col1, col2, col3 = st.columns(3)

    with col1:
        search_id = st.text_input("Search by Application ID")

    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "submitted", "validating", "under_review", "approved", "rejected", "manual_review", "appealed"],
        )

    with col3:
        results_limit = st.selectbox("Results per page", [10, 20, 50, 100])

    # Get Applications (filtered by logged-in user's email)
    with st.spinner("Loading your applications..."):
        result = get_applications(user_email=st.session_state.user_email, skip=0, limit=results_limit)

        if "error" in result:
            st.error(f"❌ Error loading applications: {result['error']}")
        else:
            total = result.get("total", 0)
            applications = result.get("applications", [])

            if not applications:
                st.info("📭 No applications found")
            else:
                # Display Statistics
                st.subheader("📊 Summary")
                col1, col2, col3, col4 = st.columns(4)

                statuses = [app["status"] for app in applications]
                approved_count = sum(1 for s in statuses if s == "approved")
                rejected_count = sum(1 for s in statuses if s == "rejected")
                under_review_count = sum(1 for s in statuses if s == "under_review")

                with col1:
                    st.metric("Total Applications", total)
                with col2:
                    st.metric("✅ Approved", approved_count)
                with col3:
                    st.metric("❌ Rejected", rejected_count)
                with col4:
                    st.metric("👀 Under Review", under_review_count)

                # Applications Table
                st.subheader("📋 Applications")

                for app in applications:
                    app_id = app["application_id"]

                    # Check filter
                    if status_filter != "All" and app["status"] != status_filter:
                        continue

                    # Check search
                    if search_id and search_id.lower() not in app_id.lower():
                        continue

                    with st.expander(
                        f"{format_status_badge(app['status'])} | {app_id[:8]}... | {app['submitted_at'][:10]}"
                    ):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Application ID", app_id)
                        with col2:
                            st.metric("Status", format_status_badge(app["status"]))
                        with col3:
                            st.metric("Submitted", app["submitted_at"][:10])

                        # Audit Trail
                        audit_result = get_audit_trail(app_id)
                        if "error" not in audit_result and audit_result.get("entries"):
                            st.write("**Activity Timeline:**")
                            for entry in audit_result["entries"][:5]:
                                timestamp = entry["timestamp"][:10]
                                action = entry["action"]
                                st.write(f"• {timestamp}: {action}")

                        # Action Buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"📊 View Details", key=f"detail_{app_id}"):
                                st.session_state.auto_load_app_id = app_id
                                st.switch_page("pages/02_check_status.py")

                        with col2:
                            if app["status"] == "rejected":
                                if st.button(f"🗣️ Appeal", key=f"appeal_{app_id}"):
                                    st.session_state.auto_load_app_id = app_id
                                    st.switch_page("pages/03_submit_appeal.py")

                # Pagination
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    page_info = f"Showing {len(applications)} of {total} applications"
                    st.text(page_info)


if __name__ == "__main__":
    main()

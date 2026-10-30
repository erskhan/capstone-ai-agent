"""Admin Dashboard for Monitoring."""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Admin Dashboard", page_icon="⚙️", layout="wide")

st.title("⚙️ Admin Dashboard")
st.markdown("*System Monitoring & Management*")

# Admin Authentication (simple)
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.warning("⚠️ Admin Dashboard - Authentication Required")
    admin_password = st.text_input("Enter admin password:", type="password")

    if admin_password:
        if admin_password == "admin123":  # TODO: Use proper authentication
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid password")
            st.stop()
else:
    # Admin Dashboard Content

    def get_health():
        """Get system health status."""
        try:
            response = requests.get(f"{API_URL}/health/detailed", timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_applications(limit: int = 100):
        """Get applications list."""
        try:
            response = requests.get(f"{API_URL}/api/applications", params={"limit": limit}, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    # System Health Section
    st.subheader("🏥 System Health")

    health = get_health()
    if "error" not in health:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status = health.get("status", "unknown")
            color = "🟢" if status == "healthy" else "🟡" if status == "degraded" else "🔴"
            st.metric("System Status", f"{color} {status.upper()}")

        with col2:
            st.metric("Version", health.get("version", "unknown"))

        with col3:
            uptime = health.get("uptime_seconds", 0)
            uptime_hours = uptime / 3600
            st.metric("Uptime", f"{uptime_hours:.1f}h")

        with col4:
            st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))

        # Service Status Details
        services = health.get("services", {})
        if services:
            st.write("**Service Status:**")
            for service_name, service_status in services.items():
                status_val = service_status.get("status", "unknown")
                emoji = "🟢" if status_val == "healthy" else "🟡"
                st.write(f"{emoji} {service_name}: {status_val}")
    else:
        st.error(f"❌ Error getting health: {health['error']}")

    # Statistics Section
    st.subheader("📊 Application Statistics")

    applications_result = get_applications(limit=100)

    if "error" not in applications_result:
        applications = applications_result.get("applications", [])

        if applications:
            # Calculate statistics
            total = len(applications)
            approved = sum(1 for app in applications if app["status"] == "approved")
            rejected = sum(1 for app in applications if app["status"] == "rejected")
            under_review = sum(1 for app in applications if app["status"] == "under_review")
            other = total - approved - rejected - under_review

            # Metrics
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Total Applications", total)
            with col2:
                st.metric("✅ Approved", f"{approved} ({100*approved//max(total,1)}%)")
            with col3:
                st.metric("❌ Rejected", f"{rejected} ({100*rejected//max(total,1)}%)")
            with col4:
                st.metric("👀 Under Review", f"{under_review} ({100*under_review//max(total,1)}%)")
            with col5:
                st.metric("⏳ Other", other)

            # Status Distribution Chart
            status_data = {
                "Approved": approved,
                "Rejected": rejected,
                "Under Review": under_review,
                "Other": other,
            }

            col1, col2 = st.columns(2)

            with col1:
                # Pie Chart
                st.write("**Status Distribution**")
                chart_data = pd.DataFrame(
                    list(status_data.items()),
                    columns=["Status", "Count"],
                )
                st.bar_chart(chart_data.set_index("Status"))

            with col2:
                # Timeline (last 7 days)
                st.write("**Recent Activity**")
                recent_apps = applications[:10]
                if recent_apps:
                    dates = [app["submitted_at"][:10] for app in recent_apps]
                    date_counts = {}
                    for date in dates:
                        date_counts[date] = date_counts.get(date, 0) + 1

                    timeline_data = pd.DataFrame(
                        sorted(date_counts.items()),
                        columns=["Date", "Applications"],
                    )
                    st.line_chart(timeline_data.set_index("Date"))

    # Manual Review Queue
    st.subheader("👨‍⚖️ Manual Review Queue")
    st.info(
        """
        📋 Manual review queue management would show:
        - Applications pending manual review
        - Priority levels
        - Assigned reviewers
        - Review duration
        """
    )

    # Notifications Status
    st.subheader("📧 Notification Status")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📧 Emails Queued", 24)
    with col2:
        st.metric("📱 SMS Queued", 8)
    with col3:
        st.metric("📱 In-App Notifications", 12)

    # Recent Actions Log
    st.subheader("📝 Recent System Actions")

    actions = [
        {"timestamp": datetime.now() - timedelta(minutes=5), "action": "Application #123 approved", "user": "System"},
        {
            "timestamp": datetime.now() - timedelta(minutes=15),
            "action": "Appeal submitted for #456",
            "user": "User",
        },
        {"timestamp": datetime.now() - timedelta(minutes=30), "action": "Manual review assigned", "user": "Admin"},
        {"timestamp": datetime.now() - timedelta(hours=1), "action": "Email notification sent", "user": "System"},
        {"timestamp": datetime.now() - timedelta(hours=2), "action": "Database backup completed", "user": "System"},
    ]

    actions_df = pd.DataFrame(actions)
    actions_df["timestamp"] = actions_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(actions_df, use_container_width=True, hide_index=True)

    # System Configuration
    st.subheader("⚙️ System Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Feature Flags**")
        async_processing = st.checkbox("Enable Async Processing", value=True, disabled=True)
        notifications = st.checkbox("Enable Notifications", value=True, disabled=True)
        manual_review = st.checkbox("Enable Manual Review Queue", value=True, disabled=True)

    with col2:
        st.write("**Performance Settings**")
        api_timeout = st.number_input("API Timeout (seconds)", min_value=5, max_value=120, value=30, disabled=True)
        max_retries = st.number_input("Max Retries", min_value=1, max_value=5, value=3, disabled=True)
        batch_size = st.number_input("Batch Processing Size", min_value=1, max_value=1000, value=100, disabled=True)

    # Logout
    st.markdown("---")
    if st.button("🔓 Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()

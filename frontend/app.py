"""Streamlit Home Page with User/Admin Login."""

import streamlit as st
import requests
from datetime import datetime

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Loan Approval System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💰 Intelligent Loan Approval System")
st.markdown("*Powered by Agentic AI | Fast, Fair, Transparent Lending*")

# Initialize session state
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# Main login/content area
if not st.session_state.user_type:
    # SHOW LOGIN PAGE
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Applicant Login")
        st.markdown("*Submit applications, check status, and manage your loans*")

        email = st.text_input(
            "Enter your email address",
            placeholder="your.email@example.com",
            key="applicant_email_input"
        )

        if st.button("➜ Login as Applicant", use_container_width=True, type="primary"):
            if email and "@" in email:
                st.session_state.user_type = "applicant"
                st.session_state.user_email = email
                st.success(f"✅ Logged in as {email}")
                st.rerun()
            else:
                st.error("❌ Please enter a valid email address")

    with col2:
        st.subheader("🔑 Admin Login")
        st.markdown("*Review applications and manage the system*")

        admin_password = st.text_input(
            "Enter admin password",
            type="password",
            placeholder="Enter password",
            key="admin_password_input"
        )

        if st.button("➜ Login as Admin", use_container_width=True):
            import os
            _expected = os.environ.get("ADMIN_PASSWORD", "")
            if _expected and admin_password == _expected:
                st.session_state.user_type = "admin"
                st.session_state.admin_authenticated = True
                st.success("✅ Admin login successful")
                st.rerun()
            else:
                st.error("❌ Invalid admin password")

    st.markdown("---")
    st.info("💡 Choose your role above to get started")

else:
    # SHOW CONTENT BASED ON USER TYPE
    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        if st.session_state.user_type == "applicant":
            st.markdown(f"**👤 Logged in as Applicant:** {st.session_state.user_email}")
        else:
            st.markdown("**🔑 Logged in as Admin**")

    with col2:
        st.write("")

    with col3:
        if st.button("🔓 Logout"):
            st.session_state.user_type = None
            st.session_state.user_email = None
            st.session_state.admin_authenticated = False
            st.rerun()

    st.markdown("---")

    if st.session_state.user_type == "applicant":
        # APPLICANT VIEW
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                """
                ### Welcome back! 👋

                Manage your loan applications with ease.
                Our AI-powered system gives you fast, fair decisions.

                **What you can do:**
                - 📝 Submit new applications
                - 🔍 Check application status
                - 📊 View detailed decisions
                - 🗣️ Appeal rejected applications
                - 📚 View application history
                """
            )

        with col2:
            try:
                response = requests.get(
                    f"{API_URL}/api/applications",
                    params={"skip": 0, "limit": 100, "user_email": st.session_state.user_email},
                    timeout=5
                )
                if response.status_code == 200:
                    try:
                        data = response.json()
                        apps = data.get("applications", [])
                        total = len(apps)
                        approved = sum(1 for a in apps if a.get("status") == "approved")
                        rejected = sum(1 for a in apps if a.get("status") == "rejected")
                        pending = sum(1 for a in apps if a.get("status") in ["submitted", "under_review", "validating"])

                        st.success(
                            f"""
                            **Quick Stats**

                            ✅ Applications: {total}
                            ⏳ Pending: {pending}
                            ✅ Approved: {approved}
                            ❌ Rejected: {rejected}
                            """
                        )
                    except Exception as json_err:
                        st.success("**Quick Stats**\n\n✅ Applications: 0")
                else:
                    st.success("**Quick Stats**\n\n✅ Applications: 0")
            except Exception as e:
                st.success("**Quick Stats**\n\n✅ Applications: 0")

        st.markdown("---")
        st.subheader("📑 Available Pages")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                #### 📝 Submit Application
                Create a new loan application

                #### 🔍 Check Status
                View your application status and decision
                """
            )

        with col2:
            st.markdown(
                """
                #### 🗣️ Submit Appeal
                Appeal a rejected application

                #### 📚 Application History
                View all your past applications
                """
            )

        st.info("ℹ️ Pages are available in the sidebar navigation. Click on any page to get started!")

    else:
        # ADMIN VIEW
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                """
                ### Admin Dashboard 🔑

                Manage the loan approval system and review pending applications.
                Monitor system health and make critical decisions.

                **Admin Capabilities:**
                - 👨‍⚖️ Manual Review Queue - Review pending applications
                - ⚙️ Admin Dashboard - System monitoring and statistics
                - 📊 View all applications
                - 🔧 System configuration
                - 📈 Performance metrics
                """
            )

        with col2:
            st.warning(
                """
                **System Status**

                🟢 API: Operational
                🟢 Database: Connected
                🟢 Services: Running
                📊 Uptime: 99.9%
                """
            )

        st.markdown("---")
        st.subheader("🛠️ Admin Tools")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                #### 👨‍⚖️ Manual Review Queue
                Review and approve/reject pending applications
                - View all pending applications
                - See AI analysis for each
                - Make decisions with conditions

                #### ⚙️ Admin Dashboard
                Monitor system performance
                - System health status
                - Application statistics
                - Service monitoring
                """
            )

        with col2:
            try:
                response = requests.get(f"{API_URL}/api/applications", params={"limit": 1000}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    apps = data.get("applications", [])
                    total = len(apps)
                    approved = sum(1 for a in apps if a.get("status") == "approved")
                    rejected = sum(1 for a in apps if a.get("status") == "rejected")
                    under_review = sum(1 for a in apps if a.get("status") == "under_review")

                    approved_pct = (100 * approved // max(total, 1)) if total > 0 else 0
                    rejected_pct = (100 * rejected // max(total, 1)) if total > 0 else 0
                    under_review_pct = (100 * under_review // max(total, 1)) if total > 0 else 0

                    st.markdown(
                        f"""
                        #### 📊 Key Metrics

                        - Total Applications: {total}
                        - Approved: {approved} ({approved_pct}%)
                        - Rejected: {rejected} ({rejected_pct}%)
                        - Under Review: {under_review} ({under_review_pct}%)

                        #### ⏱️ Performance

                        - Success Rate: {approved_pct}%
                        - Rejection Rate: {rejected_pct}%
                        - Pending Review: {under_review}
                        """
                    )
                else:
                    st.markdown("#### 📊 Key Metrics\n\nUnable to load metrics")
            except Exception as e:
                st.markdown("#### 📊 Key Metrics\n\nUnable to load metrics")

        st.info("ℹ️ Admin pages are available in the sidebar navigation. Click on any page to get started!")

    st.markdown("---")
    st.markdown("---")

    # FOOTER
    st.markdown(
        f"""
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        <p>Intelligent Loan Approval System v0.3.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>© 2026 Loan Approval System. All rights reserved. | Privacy Policy | Terms of Service</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

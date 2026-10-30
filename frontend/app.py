"""Streamlit Home Page for Loan Approval System."""

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Loan Approval System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💰 Intelligent Loan Approval System")
st.markdown("*Powered by Agentic AI | Fast, Fair, Transparent Lending*")

# Main Hero Section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(
        """
        ### Welcome to the Loan Approval System

        Our intelligent AI-powered system processes your loan application in minutes,
        not days. Get a fair decision based on comprehensive financial analysis.

        **Why choose us?**
        - ⚡ **Fast Processing**: Decisions in minutes
        - 🤖 **AI-Powered**: Advanced risk assessment
        - 📊 **Transparent**: See your decision factors
        - 🏛️ **Compliant**: Full regulatory compliance (FCRA, ECOA, Dodd-Frank)
        - 🔐 **Secure**: Your data is encrypted and protected
        """
    )

with col2:
    st.info(
        """
        **Get Started**

        1. 📝 Submit Application
        2. 🔍 Check Status
        3. 📊 View Decision
        4. 🗣️ Appeal if needed
        """
    )

st.markdown("---")

# Quick Stats
st.subheader("📊 System Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🟢 System", "Operational")
with col2:
    st.metric("⏱️ Avg Processing", "< 10s")
with col3:
    st.metric("✅ Success Rate", "> 95%")
with col4:
    st.metric("👥 Active Users", "1000+")

st.markdown("---")

# Features Section
st.subheader("✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        ### 📱 Easy Application

        - Multi-step form
        - Real-time validation
        - Auto-fill support
        - Progress tracking
        """
    )

with col2:
    st.markdown(
        """
        ### 🔍 Instant Decisions

        - AI-powered analysis
        - Multi-factor assessment
        - Parallel processing
        - Instant feedback
        """
    )

with col3:
    st.markdown(
        """
        ### 🛡️ Full Compliance

        - FCRA compliance
        - ECOA & Reg B
        - Audit trails
        - Appeal rights
        """
    )

st.markdown("---")

# Navigation Guide
st.subheader("🗂️ Navigation Guide")

tabs = st.tabs(
    ["📝 Submit Application", "🔍 Check Status", "🗣️ Appeal", "📚 History", "⚙️ Admin"]
)

with tabs[0]:
    st.markdown(
        """
        **Submit a new loan application**

        - Fill out your personal and financial information
        - Upload supporting documents (if needed)
        - Get instant validation
        - Receive your Application ID

        [→ Go to Submit Application](01_submit_application)
        """
    )

with tabs[1]:
    st.markdown(
        """
        **Check your application status**

        - Enter your Application ID
        - View real-time status updates
        - See decision details (when available)
        - Track workflow progress

        [→ Go to Check Status](02_check_status)
        """
    )

with tabs[2]:
    st.markdown(
        """
        **Appeal a decision**

        - Appeal rejected applications (30-day window)
        - Provide additional information
        - Request manual review
        - Track appeal progress

        [→ Go to Submit Appeal](03_submit_appeal)
        """
    )

with tabs[3]:
    st.markdown(
        """
        **View your application history**

        - See all past applications
        - Search by Application ID
        - Filter by status
        - Download decision letters

        [→ Go to Application History](04_application_history)
        """
    )

with tabs[4]:
    st.markdown(
        """
        **System administration dashboard**

        - Monitor system health
        - View application statistics
        - Manage manual review queue
        - Configure system settings

        [→ Go to Admin Dashboard](05_admin_dashboard)
        """
    )

st.markdown("---")

# FAQs
st.subheader("❓ Frequently Asked Questions")

with st.expander("How long does it take to get a decision?"):
    st.write(
        """
        Most loan applications are processed within 10 minutes.
        Complex applications may require 1-2 hours of manual review.
        """
    )

with st.expander("What information do I need to apply?"):
    st.write(
        """
        - Personal information (name, SSN, DOB, address)
        - Employment details (employer, job title, income)
        - Credit information (we'll check your credit report)
        - Loan details (amount, purpose, term)
        """
    )

with st.expander("How is my decision made?"):
    st.write(
        """
        Our AI system analyzes multiple factors:
        1. **Applicant Profile**: Income stability, employment history
        2. **Credit Risk**: Credit score, payment history, delinquencies
        3. **Loan Factors**: Amount, purpose, term
        4. **Anomaly Detection**: Unusual patterns in your application

        All decisions follow strict regulatory guidelines (FCRA, ECOA, etc.)
        """
    )

with st.expander("What if I'm rejected?"):
    st.write(
        """
        You have the right to:
        1. Request a copy of your credit report
        2. Appeal the decision within 30 days
        3. Request manual review by a loan officer
        4. Reapply after improving your credit

        An appeals officer will carefully review your case.
        """
    )

with st.expander("Is my information secure?"):
    st.write(
        """
        Yes! We use:
        - 256-bit SSL encryption for all data in transit
        - AES encryption for sensitive data at rest
        - Secure database with role-based access control
        - Regular security audits and compliance checks
        - PCI DSS compliance for payment data
        """
    )

st.markdown("---")

# Contact Section
st.subheader("📞 Contact & Support")

col1, col2, col3 = st.columns(3)

with col1:
    st.write(
        """
        **Phone Support**

        1-800-LOAN-APP
        (9 AM - 5 PM EST, Mon-Fri)
        """
    )

with col2:
    st.write(
        """
        **Email Support**

        support@loanapp.com
        (Response within 24 hours)
        """
    )

with col3:
    st.write(
        """
        **Live Chat**

        Available on weekdays
        (Chat with a representative)
        """
    )

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>Intelligent Loan Approval System v0.2.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>© 2026 Loan Approval System. All rights reserved. | Privacy Policy | Terms of Service</p>
    </div>
    """,
    unsafe_allow_html=True,
)

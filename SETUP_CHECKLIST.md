# LangSmith Integration - Setup Checklist

Complete this checklist to ensure your LangSmith integration is properly configured and ready for use.

---

## 📋 Pre-Setup (Before Starting)

- [ ] Create LangSmith account at https://smith.langchain.com
- [ ] Confirm free tier is available for your use case
- [ ] Note the region where your account is created
- [ ] Have your project name ready: "loan_approval_system"

---

## 🔑 Step 1: Get LangSmith Credentials

- [ ] Log in to LangSmith dashboard: https://smith.langchain.com
- [ ] Navigate to **Settings** → **API Keys**
- [ ] Click **"Create API Key"**
- [ ] Copy the generated key (format: `sk_...`)
- [ ] **IMPORTANT**: Save this key securely - you won't see it again
- [ ] Note the Base URL: `https://api.smith.langchain.com`

---

## 🔧 Step 2: Configure Environment

### Create `.env` File

- [ ] Navigate to project root: `cd /home/ubuntu/Desktop/CapStone`
- [ ] Copy template: `cp .env.example .env`
- [ ] Open in editor: `nano .env` (or your preferred editor)

### Add LangSmith Variables

In the `.env` file, locate the LangSmith Configuration section and update:

```ini
LANGSMITH_API_KEY=sk_your_actual_api_key_here
LANGSMITH_BASE_URL=https://api.smith.langchain.com
LANGSMITH_PROJECT=loan_approval_system
LANGSMITH_TRACING=true
```

**Checklist for .env**:
- [ ] `LANGSMITH_API_KEY` is not empty and starts with `sk_`
- [ ] `LANGSMITH_BASE_URL` is exactly `https://api.smith.langchain.com`
- [ ] `LANGSMITH_PROJECT` is set to `loan_approval_system`
- [ ] `LANGSMITH_TRACING` is set to `true`
- [ ] No typos in variable names
- [ ] No extra spaces after `=`
- [ ] File saved successfully

### Verify Database Configuration

- [ ] `DATABASE_URL` points to correct MySQL instance
- [ ] MySQL credentials are correct: `root:<your-db-password>`
- [ ] Database name is `loan_approval_dev`
- [ ] MySQL service is running

---

## 📦 Step 3: Install Dependencies

- [ ] Install Poetry: `pip install poetry`
- [ ] Install project dependencies: `poetry install`
- [ ] Wait for installation to complete
- [ ] No errors during installation
- [ ] Confirm installed packages: `poetry list`

---

## ✅ Step 4: Verify Configuration

### Test Configuration Loading

```bash
python -c "from shared.config import get_settings; \
s = get_settings(); \
print(f'API Key: {\"✓\" if s.langsmith_api_key else \"✗\"}'); \
print(f'Base URL: {s.langsmith_base_url}'); \
print(f'Project: {s.langsmith_project}'); \
print(f'Tracing: {s.langsmith_tracing}')"
```

- [ ] API Key shows: ✓
- [ ] Base URL is correct
- [ ] Project name is correct
- [ ] Tracing is: True

### Test Agent Initialization

```bash
python -c "from agents.applicant_agent import ApplicantProfileAgent; \
agent = ApplicantProfileAgent(); \
print('✅ ApplicantProfileAgent initialized')"
```

- [ ] Agent initializes without errors
- [ ] No "LANGSMITH_API_KEY not configured" error
- [ ] Success message displayed

---

## 🚀 Step 5: Start the Application

### Terminal 1 - API Server

```bash
export DATABASE_URL="mysql+pymysql://root:<your-db-password>@localhost:3306/loan_approval_dev"
uvicorn backend.main:app --reload
```

**Checklist**:
- [ ] API server starts successfully
- [ ] No errors in startup logs
- [ ] Server listening on `127.0.0.1:8000`
- [ ] API documentation available at `http://127.0.0.1:8000/docs`

### Terminal 2 - Frontend

```bash
streamlit run frontend/app.py
```

**Checklist**:
- [ ] Streamlit starts successfully
- [ ] Frontend available at `http://127.0.0.1:8501`
- [ ] No connection errors to API
- [ ] Form loads without errors

---

## 🧪 Step 6: Test the System

### Submit Test Application

1. Open: http://127.0.0.1:8501
2. Fill in the application form with test data:
   - First Name: John
   - Last Name: Doe
   - Email: john.doe@test.com
   - Phone: 555-123-4567
   - Date of Birth: 1990-01-01
   - Employment: Full-Time at TestCorp
   - Credit Score: 750
   - Annual Income: $75,000

**Checklist**:
- [ ] Form submits successfully
- [ ] Receive application ID
- [ ] Status shows "pending" or "submitted"
- [ ] No errors in console

### Check Status

- [ ] Use "Check Status" feature
- [ ] Retrieve the submitted application
- [ ] See application details displayed
- [ ] No errors retrieving status

---

## 📊 Step 7: Verify LangSmith Integration

### Access LangSmith Dashboard

1. Open: https://smith.langchain.com
2. Log in to your account
3. Select project: **loan_approval_system**

**Checklist**:
- [ ] Can log in to LangSmith
- [ ] Project is visible in dashboard
- [ ] Can navigate to project
- [ ] Dashboard loads without errors

### Check Traces

1. Click on **"Traces"** tab
2. Look for traces from your test application

**Checklist**:
- [ ] Traces are appearing in dashboard
- [ ] Can see Claude API calls
- [ ] Trace details are visible
- [ ] Timestamps match your test
- [ ] Request/response data is logged
- [ ] Latency information is shown

### Monitor Metrics

1. Click on **"Metrics"** or **"Analytics"**
2. Check token usage

**Checklist**:
- [ ] Token usage is tracked
- [ ] Cost estimation is displayed
- [ ] Performance metrics are visible
- [ ] No anomalies detected

---

## 🔐 Step 8: Security Verification

### .env File Security

- [ ] `.env` file is NOT in git repository
- [ ] `.gitignore` includes `.env`
- [ ] File permissions are restrictive: `chmod 600 .env`
- [ ] No `.env` file in git history
- [ ] Confirm with: `git status | grep -i env` (should show nothing)

### Secret Rotation Plan

- [ ] Rotation schedule documented (quarterly recommended)
- [ ] Multiple team members don't have API key
- [ ] Production key is different from staging
- [ ] Staging key is different from development
- [ ] Process documented for key rotation

---

## 🐛 Step 9: Error Handling Check

### Test Missing Configuration

1. Temporarily remove LANGSMITH_API_KEY from .env
2. Try to initialize agent

**Checklist**:
- [ ] Proper error message: "LANGSMITH_API_KEY not configured"
- [ ] Error comes from correct agent class
- [ ] Application doesn't crash with stack trace
- [ ] Error message is helpful

### Restore Configuration

- [ ] Add LANGSMITH_API_KEY back to .env
- [ ] Restart API server
- [ ] Confirm it works again

---

## 📚 Step 10: Documentation Review

Read the following documentation:

- [ ] [LANGSMITH_QUICK_REFERENCE.md](LANGSMITH_QUICK_REFERENCE.md) - Quick overview
- [ ] [LANGSMITH_SETUP_GUIDE.md](LANGSMITH_SETUP_GUIDE.md) - Complete guide
- [ ] [ENV_CONFIGURATION_TEMPLATE.md](ENV_CONFIGURATION_TEMPLATE.md) - Config examples
- [ ] [LANGSMITH_MIGRATION_SUMMARY.md](LANGSMITH_MIGRATION_SUMMARY.md) - Technical details

---

## 🎯 Step 11: Production Readiness

### Code Review

- [ ] All Anthropic API references replaced with LangSmith
- [ ] No hardcoded API keys in code
- [ ] Error handling is appropriate
- [ ] Logging includes relevant information

### Performance

- [ ] API responds within acceptable time
- [ ] Agent initialization is fast
- [ ] No memory leaks detected
- [ ] Concurrent requests handled properly

### Monitoring

- [ ] Can view traces in LangSmith
- [ ] Can monitor token usage
- [ ] Alert system for anomalies configured
- [ ] Team knows how to respond to alerts

---

## 🚢 Step 12: Deployment Preparation

### Staging Deployment

- [ ] Deploy to staging environment
- [ ] Configure staging LangSmith project
- [ ] Run full integration tests
- [ ] Monitor for 24 hours
- [ ] Document any issues found
- [ ] Create runbooks for common issues

### Production Deployment

- [ ] Create production LangSmith project
- [ ] Set up higher rate limits (if needed)
- [ ] Configure monitoring and alerts
- [ ] Have rollback plan ready
- [ ] Schedule deployment during low-traffic time
- [ ] Have team on standby for 2 hours

---

## 📝 Final Verification

- [ ] Configuration is correct
- [ ] Application starts without errors
- [ ] LangSmith integration is working
- [ ] Traces are appearing in dashboard
- [ ] Security best practices are followed
- [ ] Team understands the setup
- [ ] Documentation is complete
- [ ] Monitoring is configured

---

## 🎉 Success Criteria

✅ **All checklist items completed**
- Application is running
- LangSmith traces are visible
- Team can monitor performance
- Security is properly configured
- Documentation is available
- Rollback plan is ready

---

## 📞 Troubleshooting Quick Reference

| Issue | Solution | Docs |
|-------|----------|------|
| API key not configured | Add to .env | LANGSMITH_SETUP_GUIDE.md |
| Connection refused | Check base URL | LANGSMITH_QUICK_REFERENCE.md |
| Unauthorized error | Regenerate API key | LANGSMITH_SETUP_GUIDE.md |
| No traces in dashboard | Restart app, check LANGSMITH_TRACING=true | LANGSMITH_QUICK_REFERENCE.md |
| Port already in use | Use different port | LANGSMITH_QUICK_REFERENCE.md |

---

## 📋 Sign-Off

**Setup Completed By**: ___________________  
**Date**: ___________________  
**Verified By**: ___________________  
**Notes**: ___________________

---

**Next Steps**:
1. Add this checklist to your deployment procedure
2. Update team with new process
3. Schedule regular reviews (monthly)
4. Plan key rotation (quarterly)

---

**Last Updated**: 2026-10-29  
**Version**: 1.0  
**Status**: Ready for production deployment ✅

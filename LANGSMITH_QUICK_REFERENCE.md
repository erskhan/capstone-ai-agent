# LangSmith Integration - Quick Reference Card

## 🚀 Quick Start (5 Minutes)

### 1. Get Credentials
```
1. Go to https://smith.langchain.com
2. Sign up/login
3. Create project "loan_approval_system"
4. Go to Settings → API Keys
5. Create and copy API key (looks like sk_...)
```

### 2. Configure `.env`
```bash
cd /home/ubuntu/Desktop/CapStone
cp .env.example .env
nano .env  # or open in your editor
```

### 3. Add Credentials to `.env`
```ini
LANGSMITH_API_KEY=sk_your_actual_key_here
LANGSMITH_BASE_URL=https://api.smith.langchain.com
LANGSMITH_PROJECT=loan_approval_system
LANGSMITH_TRACING=true
```

### 4. Start Application
```bash
# Terminal 1: API
export DATABASE_URL="mysql+pymysql://root:<your-db-password>@localhost:3306/loan_approval_dev"
uvicorn backend.main:app --reload

# Terminal 2: Frontend
streamlit run frontend/app.py
```

### 5. Monitor
Visit: https://smith.langchain.com → Your Project → Traces

---

## 📋 File Changes Summary

| File | Change |
|------|--------|
| `shared/config.py` | ✅ Use `langsmith_api_key` + `langsmith_base_url` |
| `agents/applicant_agent.py` | ✅ Use LangSmith credentials |
| `agents/risk_agent.py` | ✅ Use LangSmith credentials |
| `.env.example` | ✅ LangSmith variables |

---

## 🔑 Environment Variables

### Required
```ini
LANGSMITH_API_KEY=sk_...           # From LangSmith dashboard
LANGSMITH_BASE_URL=https://api.smith.langchain.com
```

### Optional but Recommended
```ini
LANGSMITH_PROJECT=loan_approval_system
LANGSMITH_TRACING=true
```

---

## ⚠️ Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "LANGSMITH_API_KEY not configured" | Add key to `.env` file |
| "Connection refused" | Check base URL is `https://api.smith.langchain.com` |
| "Unauthorized" | Regenerate API key in LangSmith dashboard |
| "No traces in dashboard" | Set `LANGSMITH_TRACING=true` |
| Port already in use | Use `--port 8001` for API or `--server.port 8502` for Streamlit |

---

## 📊 Monitoring Checklist

- [ ] API server running (`http://127.0.0.1:8000`)
- [ ] Streamlit running (`http://127.0.0.1:8501`)
- [ ] MySQL database connected
- [ ] `.env` file configured with LangSmith key
- [ ] Submit test application
- [ ] Check traces in LangSmith dashboard
- [ ] View token usage and costs

---

## 🔗 Important Links

| Resource | URL |
|----------|-----|
| LangSmith Dashboard | https://smith.langchain.com |
| LangSmith Docs | https://docs.smith.langchain.com |
| Anthropic API Docs | https://docs.anthropic.com |
| Your Project API Docs | http://127.0.0.1:8000/docs |

---

## 🛡️ Security Reminders

- ⚠️ **Never commit `.env` to git**
- 🔐 **Keep API key secret**
- 🔄 **Rotate keys quarterly**
- 👁️ **Monitor usage for anomalies**
- 🔒 **Use strong SECRET_KEY** (32+ chars)

---

## 📖 Full Documentation

- **Setup Guide**: [LANGSMITH_SETUP_GUIDE.md](LANGSMITH_SETUP_GUIDE.md)
- **Migration Details**: [LANGSMITH_MIGRATION_SUMMARY.md](LANGSMITH_MIGRATION_SUMMARY.md)
- **Env Templates**: [ENV_CONFIGURATION_TEMPLATE.md](ENV_CONFIGURATION_TEMPLATE.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

---

## ✅ Verification Commands

```bash
# Check .env file
cat .env | grep LANGSMITH

# Test configuration
python -c "from shared.config import get_settings; s = get_settings(); print('✅ Ready!' if s.langsmith_api_key else '❌ Missing key')"

# Start API with verbose logging
LOG_LEVEL=DEBUG uvicorn backend.main:app --reload

# Health check
curl http://127.0.0.1:8000/health
```

---

## 🎯 Next Steps After Setup

1. ✅ Submit test loan application via UI
2. ✅ Check application status
3. ✅ View traces in LangSmith dashboard
4. ✅ Check token usage metrics
5. ✅ Monitor agent behavior
6. ✅ Run tests: `pytest`
7. ✅ Deploy to staging/production

---

**Status**: ✅ All agents configured for LangSmith
**Last Updated**: 2026-10-29

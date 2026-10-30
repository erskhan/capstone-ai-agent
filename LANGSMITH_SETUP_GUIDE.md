# LangSmith API Integration Setup Guide

This guide explains how to configure your Agentic AI Intelligent Loan Approval System to use LangSmith API instead of direct Anthropic API calls.

## What is LangSmith?

LangSmith is a platform by LangChain that provides:
- **API Gateway**: Unified endpoint for Claude API calls
- **Observability**: Track all LLM interactions and agent behavior
- **Debugging**: Analyze traces and logs for troubleshooting
- **Monitoring**: Track performance metrics and token usage
- **Rate Limiting**: Built-in rate limiting and quotas

## Prerequisites

1. **LangSmith Account**: Create one at https://smith.langchain.com
2. **API Key**: Generate an API key from your LangSmith dashboard
3. **Base URL**: The LangSmith API endpoint (usually `https://api.smith.langchain.com`)

## Step 1: Get Your LangSmith Credentials

1. Go to [LangSmith Dashboard](https://smith.langchain.com)
2. Sign in or create an account
3. Navigate to **Settings** → **API Keys**
4. Click **Create API Key**
5. Copy the generated API key (keep it secret!)
6. Note the Base URL (typically `https://api.smith.langchain.com`)

## Step 2: Configure Environment Variables

### Option A: Using `.env` file (Recommended for Local Development)

1. Copy the example environment file:
```bash
cd /home/ubuntu/Desktop/CapStone
cp .env.example .env
```

2. Edit `.env` and add your LangSmith credentials:
```bash
# LangSmith Configuration
LANGSMITH_API_KEY=your-actual-langsmith-api-key
LANGSMITH_BASE_URL=https://api.smith.langchain.com
LANGSMITH_PROJECT=loan_approval_system
LANGSMITH_TRACING=true
```

### Option B: Using Environment Variables (Production)

Export the variables in your shell:
```bash
export LANGSMITH_API_KEY="your-actual-langsmith-api-key"
export LANGSMITH_BASE_URL="https://api.smith.langchain.com"
export LANGSMITH_PROJECT="loan_approval_system"
export LANGSMITH_TRACING="true"
```

## Step 3: Install Dependencies

```bash
pip install poetry
poetry install
```

This will install all required packages including:
- `langchain-anthropic` - LangChain's Anthropic integration
- `anthropic` - Anthropic SDK (works with LangSmith)
- Other dependencies

## Step 4: Verify Configuration

Create a test script to verify your setup:

```python
# test_langsmith_config.py
import os
from shared.config import get_settings

settings = get_settings()

print(f"LangSmith API Key configured: {bool(settings.langsmith_api_key)}")
print(f"LangSmith Base URL: {settings.langsmith_base_url}")
print(f"LangSmith Project: {settings.langsmith_project}")
print(f"LangSmith Tracing: {settings.langsmith_tracing}")

if settings.langsmith_api_key:
    print("\n✅ LangSmith configuration is ready!")
else:
    print("\n❌ LANGSMITH_API_KEY is not configured")
```

Run it:
```bash
python test_langsmith_config.py
```

## Step 5: Run Your Application

### Start the API Server:

```bash
export DATABASE_URL="mysql+pymysql://root:<your-db-password>@localhost:3306/loan_approval_dev"
uvicorn backend.main:app --reload
```

### Start the Frontend (in another terminal):

```bash
streamlit run frontend/app.py
```

## Step 6: Monitor Your Usage in LangSmith

1. Go to [LangSmith Dashboard](https://smith.langchain.com)
2. Navigate to your project: **loan_approval_system**
3. View:
   - **Traces**: See all LLM calls and agent interactions
   - **Metrics**: Token usage, latency, costs
   - **Logs**: Debug information and errors
   - **Analytics**: Performance trends

## Files Changed

The following files have been updated to use LangSmith:

### Configuration
- **`shared/config.py`**: 
  - Removed `anthropic_api_key`
  - Added `langsmith_api_key`
  - Added `langsmith_base_url`
  - Enabled `langsmith_tracing` by default

### Agent Files
- **`agents/applicant_agent.py`**: Now uses `langsmith_api_key` and `langsmith_base_url`
- **`agents/risk_agent.py`**: Now uses `langsmith_api_key` and `langsmith_base_url`

### Environment
- **`.env.example`**: Updated with LangSmith variables instead of Anthropic

### Documentation
- **`examples/applicant_agent_example.py`**: Updated error messages

## How the Integration Works

When you create a ChatAnthropic instance with LangSmith credentials:

```python
self.llm = ChatAnthropic(
    api_key=settings.langsmith_api_key,
    base_url=settings.langsmith_base_url,
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    timeout=settings.agent_timeout_seconds,
)
```

The system:
1. Routes your request through LangSmith's base URL
2. Authenticates using your LangSmith API key
3. Forwards the request to Anthropic's Claude API
4. Returns the response to your application
5. Logs everything to LangSmith for observability

## Troubleshooting

### Error: "LANGSMITH_API_KEY not configured"

**Solution**: Make sure your `.env` file has the correct API key:
```bash
grep LANGSMITH_API_KEY .env
# Should output: LANGSMITH_API_KEY=sk-...
```

### Error: "Connection refused" or "Invalid base_url"

**Solution**: Verify your base URL is correct:
```bash
# Should be:
LANGSMITH_BASE_URL=https://api.smith.langchain.com

# NOT:
LANGSMITH_BASE_URL=https://smith.langchain.com  # This is the dashboard, not API
```

### Error: "Unauthorized" or "Invalid API key"

**Solution**: Your API key might be invalid or expired:
1. Go to LangSmith dashboard
2. Regenerate your API key
3. Update `.env` file with the new key
4. Restart your application

### No traces appearing in LangSmith

**Solution**: Make sure `LANGSMITH_TRACING=true` in your environment:
```bash
grep LANGSMITH_TRACING .env
# Should output: LANGSMITH_TRACING=true
```

## Environment File Reference

Here's a complete `.env.example` showing all LangSmith-related settings:

```ini
# Local Development Configuration
PYTHONUNBUFFERED=1
DEBUG=True
LOG_LEVEL=INFO

# Database Configuration - MySQL (Local)
DATABASE_URL=mysql+pymysql://root:<your-db-password>@localhost:3306/loan_approval_dev

# API Configuration - Local
API_HOST=127.0.0.1
API_PORT=8000
API_WORKERS=1

# Streamlit Configuration - Local
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=127.0.0.1

# LangSmith Configuration
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_BASE_URL=https://api.smith.langchain.com
LANGSMITH_PROJECT=loan_approval_system
LANGSMITH_TRACING=true

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@loanapproval.com

# Feature Flags
ENABLE_ASYNC_PROCESSING=true
ENABLE_NOTIFICATIONS=false
ENABLE_MANUAL_REVIEW_QUEUE=true

# Performance Configuration
AGENT_TIMEOUT_SECONDS=30
WORKFLOW_TIMEOUT_SECONDS=60
API_RATE_LIMIT_PER_MINUTE=100
```

## API Key Security Best Practices

1. **Never commit `.env` file to git**: Add it to `.gitignore`
2. **Use different keys for environments**:
   - Development key (lower rate limits)
   - Staging key
   - Production key (with higher rate limits and monitoring)
3. **Rotate keys regularly**: Regenerate in LangSmith every quarter
4. **Monitor usage**: Check LangSmith dashboard for unusual activity
5. **Use environment variables in production**: Don't store keys in code

## Next Steps

1. ✅ Configure `.env` with LangSmith credentials
2. ✅ Start your API server: `uvicorn backend.main:app --reload`
3. ✅ Start your frontend: `streamlit run frontend/app.py`
4. ✅ Submit a test loan application
5. ✅ Check LangSmith dashboard to see traces

## Support

- **LangSmith Documentation**: https://docs.smith.langchain.com
- **Anthropic API Docs**: https://docs.anthropic.com
- **LangChain Docs**: https://python.langchain.com

---

**Last Updated**: 2026-10-29
**Status**: ✅ All agents configured to use LangSmith

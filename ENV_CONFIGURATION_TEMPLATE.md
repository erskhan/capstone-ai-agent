# Environment Configuration Template

This document provides example `.env` configurations for different deployment scenarios.

## Local Development Setup

### `.env` (Local Development)
```ini
# Local Development Configuration
PYTHONUNBUFFERED=1
DEBUG=True
LOG_LEVEL=INFO

# Database Configuration - MySQL (Local)
DATABASE_URL=mysql+pymysql://root:WP@12345@localhost:3306/loan_approval_dev

# API Configuration - Local
API_HOST=127.0.0.1
API_PORT=8000
API_WORKERS=1

# Streamlit Configuration - Local
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=127.0.0.1

# LangSmith Configuration (REQUIRED - Get credentials from https://smith.langchain.com)
LANGSMITH_API_KEY=sk_your_actual_langsmith_api_key_here
LANGSMITH_BASE_URL=https://api.smith.langchain.com
LANGSMITH_PROJECT=loan_approval_system
LANGSMITH_TRACING=true

# Security Configuration
SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
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

## Staging Environment Setup

### `.env` (Staging)
```ini
# Staging Environment Configuration
PYTHONUNBUFFERED=1
DEBUG=False
LOG_LEVEL=WARNING

# Database Configuration - MySQL (Staging)
DATABASE_URL=mysql+pymysql://staging_user:staging_password@staging-db.example.com:3306/loan_approval_staging

# API Configuration - Staging
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Streamlit Configuration - Staging
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# LangSmith Configuration (Staging Key)
LANGSMITH_API_KEY=sk_staging_langsmith_api_key_here
LANGSMITH_BASE_URL=https://api.smith.langchain.com
LANGSMITH_PROJECT=loan_approval_system_staging
LANGSMITH_TRACING=true

# Security Configuration
SECRET_KEY=staging-secret-key-rotate-regularly
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=staging@loanapproval.com
SMTP_PASSWORD=staging-email-password
SMTP_FROM_EMAIL=noreply-staging@loanapproval.com

# Feature Flags
ENABLE_ASYNC_PROCESSING=true
ENABLE_NOTIFICATIONS=true
ENABLE_MANUAL_REVIEW_QUEUE=true

# Performance Configuration
AGENT_TIMEOUT_SECONDS=45
WORKFLOW_TIMEOUT_SECONDS=120
API_RATE_LIMIT_PER_MINUTE=1000
```

## Production Environment Setup

### `.env` (Production)
```ini
# Production Environment Configuration
PYTHONUNBUFFERED=1
DEBUG=False
LOG_LEVEL=INFO

# Database Configuration - MySQL (Production)
DATABASE_URL=mysql+pymysql://prod_user:prod_secure_password@prod-db.example.com:3306/loan_approval_prod

# API Configuration - Production
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=8

# Streamlit Configuration - Production
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# LangSmith Configuration (Production Key - with higher limits)
LANGSMITH_API_KEY=sk_prod_langsmith_api_key_here
LANGSMITH_BASE_URL=https://api.smith.langchain.com
LANGSMITH_PROJECT=loan_approval_system_prod
LANGSMITH_TRACING=true

# Security Configuration (MUST CHANGE)
SECRET_KEY=production-secret-key-min-32-chars-change-immediately
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email Configuration
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@loanapproval.com

# Feature Flags
ENABLE_ASYNC_PROCESSING=true
ENABLE_NOTIFICATIONS=true
ENABLE_MANUAL_REVIEW_QUEUE=true

# Performance Configuration
AGENT_TIMEOUT_SECONDS=60
WORKFLOW_TIMEOUT_SECONDS=180
API_RATE_LIMIT_PER_MINUTE=10000
```

## How to Get LangSmith Credentials

### Step 1: Create Account
1. Go to https://smith.langchain.com
2. Click "Sign Up" or "Sign In"
3. Use GitHub or email to register

### Step 2: Create Project
1. After login, go to "Projects"
2. Click "Create Project" or use default "default"
3. Name it something like "loan_approval_system"

### Step 3: Generate API Key
1. Click on your project
2. Go to "Settings" → "API Keys"
3. Click "Create API Key"
4. Copy the generated key (looks like `sk_...`)
5. **SAVE THIS SECURELY** - you won't see it again!

### Step 4: Get Base URL
- The base URL is always: `https://api.smith.langchain.com`
- This is the standard LangSmith API endpoint

## Step-by-Step Setup for Local Development

```bash
# 1. Clone and enter project directory
cd /home/ubuntu/Desktop/CapStone

# 2. Copy the example env file
cp .env.example .env

# 3. Edit .env file with your LangSmith credentials
nano .env
# Or use your preferred editor (vim, code, etc.)

# 4. Update these lines in .env:
# LANGSMITH_API_KEY=sk_your_actual_key_from_langsmith
# LANGSMITH_BASE_URL=https://api.smith.langchain.com
# (leave the rest as default)

# 5. Verify your configuration
cat .env | grep LANGSMITH

# 6. Install dependencies
pip install poetry
poetry install

# 7. Test the configuration
python -c "
from shared.config import get_settings
settings = get_settings()
print('✅ LangSmith API Key:', 'Configured' if settings.langsmith_api_key else 'Missing')
print('✅ LangSmith Base URL:', settings.langsmith_base_url)
print('✅ LangSmith Project:', settings.langsmith_project)
"

# 8. Start the API server
export DATABASE_URL="mysql+pymysql://root:WP@12345@localhost:3306/loan_approval_dev"
uvicorn backend.main:app --reload

# 9. In another terminal, start the frontend
streamlit run frontend/app.py

# 10. Visit http://127.0.0.1:8501
```

## Environment Variables Reference

### LangSmith Variables (Required)

| Variable | Example | Description |
|----------|---------|-------------|
| `LANGSMITH_API_KEY` | `sk_...` | Your LangSmith API key from https://smith.langchain.com |
| `LANGSMITH_BASE_URL` | `https://api.smith.langchain.com` | LangSmith API endpoint |
| `LANGSMITH_PROJECT` | `loan_approval_system` | Project name for organization |
| `LANGSMITH_TRACING` | `true` | Enable trace logging (true for dev, can be false for prod) |

### Database Variables (Required)

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `mysql+pymysql://user:pass@host:3306/db` | MySQL connection string |

### API Variables (Optional)

| Variable | Example | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `API_WORKERS` | `4` | Number of worker processes |

### Streamlit Variables (Optional)

| Variable | Example | Description |
|----------|---------|-------------|
| `STREAMLIT_SERVER_PORT` | `8501` | Streamlit server port |
| `STREAMLIT_SERVER_ADDRESS` | `127.0.0.1` | Streamlit server address |

### Security Variables (Recommended)

| Variable | Example | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `your-secret-key` | JWT signing secret (min 32 chars) |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_EXPIRATION_HOURS` | `24` | JWT token expiration |

## Security Best Practices

### ⚠️ DO NOT:
- ❌ Commit `.env` file to git repository
- ❌ Share your `LANGSMITH_API_KEY` with anyone
- ❌ Use same credentials for dev, staging, and production
- ❌ Store credentials in code files
- ❌ Use weak `SECRET_KEY` values

### ✅ DO:
- ✅ Add `.env` to `.gitignore`
- ✅ Use different API keys for each environment
- ✅ Rotate keys regularly (quarterly minimum)
- ✅ Store secrets in a secure vault (AWS Secrets Manager, HashiCorp Vault, etc.)
- ✅ Use strong `SECRET_KEY` (min 32 characters, random)
- ✅ Review LangSmith usage regularly for anomalies

## Troubleshooting Configuration

### Error: "LANGSMITH_API_KEY not configured"
```bash
# Check if .env file exists and has the key
cat .env | grep LANGSMITH_API_KEY

# Verify the key is not empty
grep -v "^#" .env | grep -v "^$" | grep LANGSMITH_API_KEY
```

### Error: "Invalid base URL"
```bash
# Verify the URL format
echo $LANGSMITH_BASE_URL
# Should be: https://api.smith.langchain.com

# Test connectivity
curl -H "Authorization: Bearer $LANGSMITH_API_KEY" \
  "$LANGSMITH_BASE_URL/health"
```

### Error: "Unauthorized"
```bash
# Verify your API key is correct
# Re-generate key from LangSmith dashboard if needed
# Update .env file
# Restart application
```

## Docker Environment (if needed)

```dockerfile
# In your Dockerfile
FROM python:3.11-slim

# Copy environment file
COPY .env .env

# Install dependencies
RUN pip install poetry && poetry install

# Run your app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
```

```bash
# Build and run with env file
docker build -t loan-app .
docker run --env-file .env -p 8000:8000 loan-app
```

---

**Last Updated**: 2026-10-29
**Version**: 1.0
**Status**: ✅ Ready for deployment

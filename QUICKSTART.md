# 🚀 Quick Start Guide

Get the Agentic AI Intelligent Loan Approval System running in minutes!

## Prerequisites

- Docker and Docker Compose installed
- Anthropic API key (get one from https://console.anthropic.com)

## 1️⃣ Clone and Setup (Already Done!)

The project structure has been created with:
- ✅ Backend (FastAPI)
- ✅ Frontend (Streamlit)
- ✅ Database models (SQLAlchemy)
- ✅ Configuration files
- ✅ Test suite structure
- ✅ Docker setup

## 2️⃣ Configure Environment

```bash
cd /home/ubuntu/Desktop/CapStone

# Copy example env file
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-...
```

## 3️⃣ Start with Docker Compose

```bash
# Start all services
docker-compose up

# Services will be available at:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:8501
```

## 4️⃣ Test the API

In a new terminal:

```bash
# Health check
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

## 5️⃣ Test the Frontend

Open browser to: http://localhost:8501

Try submitting a test application:
- Fill in the form with sample data
- Click "Submit Application"
- Get your application ID
- Use "Check Status" to retrieve your application

## 6️⃣ Run Tests

```bash
# Install dependencies locally (optional)
pip install poetry
poetry install

# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific tests
pytest tests/test_api.py -v
```

## 📊 Project Status - Phase 1 Complete ✅

**Foundation & Architecture Setup** is complete with:

- ✅ Project structure initialized
- ✅ Core data models defined (LoanApplication, ApplicantProfile, CreditRecord, etc.)
- ✅ Database schema with SQLAlchemy ORM
- ✅ FastAPI base server with core endpoints
- ✅ Streamlit UI framework
- ✅ MCP server scaffolding
- ✅ Configuration management
- ✅ Structured logging
- ✅ Docker setup for local development
- ✅ Test framework and sample tests
- ✅ README and documentation

## 🔧 Current Capabilities

### API Endpoints
- `GET /health` - Health check
- `POST /api/applications` - Submit new application
- `GET /api/applications/{id}` - Get application status
- `GET /api/applications` - List all applications

### Frontend Features
- Application submission form
- Status checking by ID
- Application history view

### Database Models
- LoanApplicationModel
- ApplicantModel
- EmploymentInfoModel
- CreditRecordModel
- LoanDetailsModel
- RiskAssessmentModel
- LoanDecisionModel
- AuditLogModel

## 📝 Next Steps - Phase 2 Implementation

To continue with Phase 2 (Core Agent Development):

1. **Implement Agent Classes**
   - `agents/applicant_agent.py` - Applicant validation logic
   - `agents/risk_agent.py` - Risk analysis engine
   - `agents/decision_agent.py` - Decision synthesis

2. **Extend MCP Servers**
   - `mcp_servers/risk_rules_server.py` - Risk calculation tools
   - `mcp_servers/decision_server.py` - Decision tools

3. **Add Claude Integration**
   - Use Anthropic SDK for agent reasoning
   - Implement prompt templates
   - Set up agent tools

4. **Expand Tests**
   - Agent logic tests
   - Integration tests
   - MCP server tests

## 🗂️ Key Files

- **Backend**: `backend/main.py` - FastAPI application
- **Models**: `models/schemas.py` - Pydantic request/response schemas
- **Database**: `database/models.py` - SQLAlchemy ORM models
- **Config**: `shared/config.py` - Environment configuration
- **Frontend**: `frontend/app.py` - Streamlit UI

## 🐛 Troubleshooting

### Docker Issues
```bash
# Clear Docker containers and volumes
docker-compose down -v
docker-compose up --build
```

### Database Connection Issues
```bash
# Check if database is running
docker ps

# View logs
docker-compose logs db
```

### API Not Responding
```bash
# Check API logs
docker-compose logs api

# Verify on http://localhost:8000/docs
```

### Frontend Connection Issues
```bash
# Check if Streamlit is running
docker-compose logs streamlit

# Visit http://localhost:8501
```

## 📞 Need Help?

1. Check `Loan_Application_Plan.md` for architecture details
2. View API docs at `http://localhost:8000/docs`
3. Check logs with `docker-compose logs`

## 🎯 What's Configured

```
✅ Python 3.11+ environment
✅ SQLAlchemy 2.0 ORM
✅ FastAPI with async support
✅ Pydantic v2 validation
✅ LangGraph ready (imports configured)
✅ Anthropic SDK ready
✅ Structured JSON logging
✅ Docker containerization
✅ pytest test framework
✅ Environment variable management
```

## 🚀 Running Without Docker

If you prefer local development:

```bash
# Install dependencies
poetry install

# Set environment variables
export DATABASE_URL="sqlite:///./loan_approval.db"
export ANTHROPIC_API_KEY="your-api-key"

# Run API server
uvicorn backend.main:app --reload

# In another terminal, run frontend
streamlit run frontend/app.py
```

---

**You're all set! The foundation is ready. Next: Implement the AI agents in Phase 2! 🎉**

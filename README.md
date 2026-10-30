# 🏦 Agentic AI Intelligent Loan Approval System

A sophisticated multi-agent loan approval system powered by Claude AI, FastAPI, and LangGraph. The system intelligently processes loan applications through specialized agents, providing automated approvals, rejections, or escalations to manual review.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for applicant validation, risk analysis, and decision synthesis
- **LangGraph Orchestration**: Efficient workflow management with parallel agent execution
- **MCP Server Integration**: Model Context Protocol for agent communication
- **FastAPI Backend**: High-performance REST API for loan application processing
- **Streamlit Frontend**: User-friendly web interface for loan submissions and status tracking
- **Comprehensive Audit Logging**: Full decision audit trail for compliance
- **Risk Assessment**: Automated financial risk analysis and scoring
- **Compliance & Notifications**: Document generation and multi-channel notifications

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│                   (User Interface)                          │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│              (REST API, Request Validation)                │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│               LangGraph Orchestrator                        │
│         (Workflow Coordination & State Mgmt)               │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┬─────────────┬──────────────┐
        │                 │             │              │
┌───────▼────────┐ ┌──────▼──────┐ ┌──▼────────────┐  │
│ Applicant      │ │ Financial   │ │ Loan Decision│  │
│ Profile Agent  │ │ Risk Agent  │ │ Agent        │  │
└────────────────┘ └─────────────┘ └──────────────┘  │
        │                 │             │              │
└───────┴─────────────────┴─────────────┴──────────────┘
                 │
     ┌───────────┴────────────┐
     │                        │
┌────▼──────────┐    ┌───────▼────────┐
│ MCP Servers   │    │  PostgreSQL    │
│ (Tools)       │    │  Database      │
└───────────────┘    └────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **LangChain/LangGraph**: AI orchestration and workflow management
- **Anthropic SDK**: Claude AI integration

### Frontend
- **Streamlit**: Rapid web app development
- **Plotly**: Data visualization

### Infrastructure
- **MySQL 8.0+**: Relational database
- **PyMySQL**: MySQL driver for Python

### Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support

## 📂 Project Structure

```
.
├── backend/
│   └── main.py                 # FastAPI application
├── agents/
│   ├── orchestrator.py         # LangGraph workflow
│   ├── applicant_agent.py      # Profile validation agent
│   ├── risk_agent.py           # Risk analysis agent
│   └── decision_agent.py       # Decision synthesis agent
├── mcp_servers/
│   ├── applicant_db_server.py  # Applicant data tools
│   ├── risk_rules_server.py    # Risk calculation tools
│   └── decision_server.py      # Decision tools
├── frontend/
│   └── app.py                  # Streamlit UI
├── database/
│   ├── db.py                   # Database setup
│   └── models.py               # SQLAlchemy models
├── models/
│   └── schemas.py              # Pydantic schemas
├── shared/
│   ├── config.py               # Configuration
│   ├── logger.py               # Logging setup
│   └── exceptions.py           # Custom exceptions
├── tests/
│   ├── test_api.py             # API tests
│   ├── test_mcp_servers.py     # MCP server tests
│   └── test_orchestrator.py    # Orchestrator tests
├── Dockerfile                  # Docker image
├── docker-compose.yml          # Docker compose
├── pyproject.toml              # Poetry dependencies
├── pytest.ini                  # pytest configuration
└── Loan_Application_Plan.md    # Implementation plan
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- MySQL 8.0+ running locally
- Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CapStone
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

3. **Install dependencies**
   ```bash
   pip install poetry
   poetry install
   ```

### Running Locally

#### Step 1: Ensure MySQL is Running

Make sure your MySQL instance is running on localhost:3306:

```bash
# Verify MySQL is running
mysql -u root -p<your-db-password> -h localhost
# Should connect successfully
```

#### Step 2: Start the API Server

```bash
# Set environment variables
export DATABASE_URL="mysql+pymysql://root:<your-db-password>@localhost:3306/loan_approval_dev"
export ANTHROPIC_API_KEY="your-api-key-here"

# Start the API (from project root)
uvicorn backend.main:app --reload
```

API will be available at:
- **API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

#### Step 3: Start the Frontend (in another terminal)

```bash
# From project root
streamlit run frontend/app.py
```

Frontend will be available at:
- **UI**: http://127.0.0.1:8501

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_api.py -v
```

Run async tests only:
```bash
pytest -m asyncio
```

## 📚 API Documentation

### Health Check
```bash
GET /health
```

### Submit Application
```bash
POST /api/applications
Content-Type: application/json

{
  "applicant_profile": { ... },
  "employment_info": { ... },
  "credit_record": { ... },
  "loan_details": { ... }
}
```

### Get Application Status
```bash
GET /api/applications/{application_id}
```

### List Applications
```bash
GET /api/applications?skip=0&limit=10
```

### Get Application Decision
```bash
GET /api/applications/{application_id}/decision
```

### Get Audit Trail
```bash
GET /api/applications/{application_id}/audit-trail
```

Interactive API documentation available at `http://localhost:8000/docs`

## 🔄 Workflow Phases

### Phase 1: Foundation & Architecture ✅
- Project structure setup
- Database schema design
- Core configurations

### Phase 2: Core Agent Development 🚧
- Applicant Profile Agent
- Financial Risk Analysis Agent
- Loan Decision Agent
- MCP server implementations

### Phase 3: Orchestration Engine
- LangGraph workflow setup
- State management
- Error handling

### Phase 4: API Layer
- REST endpoints
- Validation
- Rate limiting

### Phase 5: Frontend UI
- Streamlit interface
- Multi-step forms
- Real-time status

### Phase 6: Compliance & Notifications
- Compliance agent
- Document generation
- Notification system

### Phase 7: Testing & QA
- Unit tests
- Integration tests
- Performance testing

### Phase 8: Deployment & Monitoring
- Docker containerization
- CI/CD pipeline
- Monitoring setup

### Phase 9: Production Hardening
- Performance optimization
- Security hardening
- Cost optimization

## 🔐 Security Considerations

- PII (Social Security Numbers, bank details) should be encrypted at rest
- API authentication using JWT tokens
- Rate limiting on all endpoints
- Input validation on all requests
- HTTPS enforcement in production
- Audit logging for all decisions
- Regular security dependency scanning

## 📊 Success Metrics

- **Performance**: <10s end-to-end processing time
- **Accuracy**: >85% decision accuracy against known dataset
- **Uptime**: 99.9% system availability
- **Code Coverage**: >80% test coverage
- **Throughput**: >1000 applications/day

## 🤝 Contributing

See the implementation plan in `Loan_Application_Plan.md` for detailed guidelines.

## 📝 License

This project is part of the CapStone initiative.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the implementation plan in `Loan_Application_Plan.md`
3. Check logs for detailed error messages

---

**Built with ❤️ using Claude AI and open-source technologies**

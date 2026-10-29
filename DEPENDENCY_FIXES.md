# Dependency Installation Fixed ✅

## Problem

The initial `pyproject.toml` had incompatible dependency versions that caused `poetry install` to fail with:

```
Because loan-approval-system depends on mcp (^0.1.0) which doesn't match any versions, version solving failed.
```

And then:

```
Because loan-approval-system depends on both langchain-anthropic (^0.1.0) and anthropic (^0.7.0), version solving failed.
```

## Root Causes

1. **MCP Package**: The Model Context Protocol package (`mcp ^0.1.0`) was unavailable - this package is still in early development
2. **Anthropic Version Conflict**: Old anthropic version (`^0.7.0`) conflicted with newer langchain-anthropic requirements
3. **LangChain Compatibility**: Multiple LangChain versions had conflicting langchain-core dependencies

## Solution Applied

### Changes Made to `pyproject.toml`

1. **Removed problematic packages**:
   - Removed `mcp` (not needed for current implementation)
   - Removed `langchain` and `langgraph` (not currently used by agents)

2. **Updated to compatible versions**:
   - `anthropic = ">=0.30.0"` (latest stable version)
   - Kept direct Anthropic SDK usage instead of LangChain wrappers

3. **Added package definitions**:
   ```toml
   packages = [
       {include = "backend"},
       {include = "agents"},
       {include = "frontend"},
       {include = "models"},
       {include = "shared"}
   ]
   ```

### Code Changes to Agents

Updated agent implementations to use Anthropic SDK directly instead of LangChain wrappers:

#### `agents/applicant_agent.py`
**Before**:
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

self.llm = ChatAnthropic(
    api_key=settings.langsmith_api_key,
    base_url=settings.langsmith_base_url,
    ...
)

response = self.llm.invoke([SystemMessage(...), message])
```

**After**:
```python
import anthropic

self.client = anthropic.Anthropic(
    api_key=settings.langsmith_api_key,
    base_url=settings.langsmith_base_url,
)

response = self.client.messages.create(
    model=self.model,
    max_tokens=1024,
    system=system_prompt,
    messages=[{"role": "user", "content": "..."}]
)
```

#### `agents/risk_agent.py`
Similar changes applied to use Anthropic SDK directly.

## Current Dependencies

### Core Framework
- `fastapi ^0.104.1` - Web framework
- `streamlit ^1.28.0` - Frontend UI
- `uvicorn ^0.24.0` - ASGI server

### Database
- `sqlalchemy ^2.0.0` - ORM
- `pymysql ^1.1.0` - MySQL driver
- `alembic ^1.12.1` - Database migrations

### API & AI
- `anthropic >=0.30.0` - Anthropic API SDK
- `httpx ^0.25.0` - HTTP client
- `requests ^2.31.0` - HTTP library

### Configuration & Utilities
- `pydantic ^2.4.0` - Data validation
- `pydantic-settings ^2.0.0` - Settings management
- `python-dotenv ^1.0.0` - Environment variables
- `python-json-logger ^2.0.7` - JSON logging

### Security & Auth
- `pyjwt ^2.8.0` - JWT tokens
- `passlib[bcrypt] ^1.7.4` - Password hashing
- `email-validator ^2.1.0` - Email validation

### Utilities
- `reportlab ^4.0.7` - PDF generation
- `slowapi ^0.1.9` - Rate limiting
- `aiohttp ^3.9.0` - Async HTTP
- `async` - Async utilities

### Development & Testing
- `pytest ^7.4.3` - Testing framework
- `pytest-asyncio ^0.21.1` - Async test support
- `pytest-cov ^4.1.0` - Code coverage
- `pytest-mock ^3.12.0` - Mocking support
- `black ^23.12.0` - Code formatter
- `ruff ^0.1.11` - Linter

## Installation Steps

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install Poetry
pip install --upgrade pip poetry

# 4. Install project dependencies
poetry install

# 5. Verify installation
python -c "from agents.applicant_agent import ApplicantProfileAgent; print('✅ Ready')"
```

## Using the Virtual Environment

```bash
# Activate venv (do this each time you start a new terminal)
source venv/bin/activate

# Run API
uvicorn backend.main:app --reload

# Run Frontend (in another terminal)
streamlit run frontend/app.py

# Run tests
pytest

# Deactivate venv when done
deactivate
```

## Benefits of Current Setup

✅ **Direct Anthropic SDK**: Direct access to latest Claude models without LangChain wrapper delays  
✅ **Lighter Dependencies**: Removed unnecessary LangChain stack reduces size and complexity  
✅ **LangSmith Integration**: Full observability through LangSmith API gateway  
✅ **Latest SDK**: Using anthropic >=0.30.0 for latest Claude models and features  
✅ **Type Safety**: Pydantic validation for all data models  
✅ **Async Support**: FastAPI with async capabilities for high performance  

## Troubleshooting

### If Poetry still fails

```bash
# Clear cache
rm -f poetry.lock
rm -rf venv

# Start fresh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip poetry
poetry install
```

### If import errors occur

```bash
# Verify installation
poetry show

# Check specific package
poetry show anthropic

# Reinstall if needed
poetry install --no-cache
```

### Missing .env file

```bash
# If you haven't configured LangSmith yet
cp .env.example .env

# Edit and add your credentials
nano .env

# Add:
# LANGSMITH_API_KEY=sk_your_key
# LANGSMITH_BASE_URL=https://llmgw-wp.tekstac.com
```

## Next Steps

1. ✅ Dependencies installed successfully
2. Update `.env` with your LangSmith credentials  
3. Start the API server
4. Start the Streamlit frontend
5. Submit test application
6. Check LangSmith dashboard for traces

## Reference

- [Anthropic SDK Docs](https://docs.anthropic.com)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Streamlit Docs](https://docs.streamlit.io)
- [Poetry Docs](https://python-poetry.org)

---

**Status**: ✅ Dependencies fixed and installation successful  
**Date**: 2026-10-29  
**Version**: 0.1.0

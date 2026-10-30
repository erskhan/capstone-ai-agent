# Local Development Setup Guide

This project runs completely locally without Docker. Here's how to set it up.

## Prerequisites

- **Python 3.11 or higher** - [Download](https://www.python.org/downloads/)
- **MySQL 8.0+** running on localhost:3306
- **Anthropic API key** - [Get from console.anthropic.com](https://console.anthropic.com)

## Step 1: Verify MySQL is Running

### macOS (Homebrew)
```bash
# Check if MySQL is running
brew services list

# Start MySQL if not running
brew services start mysql

# Connect to verify
mysql -u root -p<your-db-password> -h localhost
# Type 'exit' to quit
```

### Linux (Ubuntu/Debian)
```bash
# Start MySQL
sudo systemctl start mysql

# Verify
sudo systemctl status mysql

# Connect
mysql -u root -p<your-db-password> -h localhost
```

### Windows
```bash
# MySQL 8.0 should be running as a service
# Check Services in Task Manager

# Or start from PowerShell (as Admin)
net start MySQL80

# Connect
mysql -u root -p<your-db-password> -h localhost
```

## Step 2: Clone/Navigate to Project

```bash
cd /home/ubuntu/Desktop/CapStone
```

## Step 3: Setup Python Environment

```bash
# Install Poetry (Python dependency manager)
pip install poetry

# Install all project dependencies
poetry install
```

This installs:
- FastAPI (web framework)
- Streamlit (UI framework)
- SQLAlchemy (ORM)
- PyMySQL (MySQL driver)
- LangChain & LangGraph (AI orchestration)
- And all other dependencies

## Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API key
# On macOS/Linux:
nano .env
# On Windows:
# Use Notepad or your preferred editor

# Add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```

Your `.env` file should contain:
```
DEBUG=True
LOG_LEVEL=INFO
DATABASE_URL=mysql+pymysql://root:<your-db-password>@localhost:3306/loan_approval_dev
API_HOST=127.0.0.1
API_PORT=8000
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=127.0.0.1
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Step 5: Start API Server

Open Terminal 1:

```bash
cd /home/ubuntu/Desktop/CapStone

# Activate environment variables
export DATABASE_URL="mysql+pymysql://root:<your-db-password>@localhost:3306/loan_approval_dev"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Start the API server
uvicorn backend.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Access API

- **API Server**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **API Health Check**: http://127.0.0.1:8000/health

## Step 6: Start Streamlit UI

Open Terminal 2:

```bash
cd /home/ubuntu/Desktop/CapStone

# Start Streamlit
streamlit run frontend/app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://127.0.0.1:8501
```

### Access UI

- **Web UI**: http://127.0.0.1:8501

## Step 7: Test the System

### Via Command Line

```bash
# Test API health
curl http://127.0.0.1:8000/health

# Should return:
# {"status":"healthy","version":"0.1.0"}
```

### Via Web Browser

1. **API Documentation**
   - Visit: http://127.0.0.1:8000/docs
   - Try the endpoints in the interactive documentation

2. **Web UI**
   - Visit: http://127.0.0.1:8501
   - Submit a test loan application
   - Check the status

## Database Verification

```bash
# Connect to MySQL
mysql -u root -p<your-db-password> loan_approval_dev

# View tables
SHOW TABLES;

# Check application data
SELECT * FROM loan_applications;

# Exit
exit
```

## Development Workflow

### Making Code Changes

The API server with `--reload` flag automatically restarts when you modify code.

1. Edit code in your IDE
2. Save the file
3. Check the terminal - it should show the restart
4. Refresh your browser or test again

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov
```

### Checking Logs

**API Server logs** - Check Terminal 1 where you ran `uvicorn`

**Streamlit logs** - Check Terminal 2 where you ran `streamlit`

**Database logs** - Check your MySQL logs:
```bash
# macOS
tail -f /usr/local/var/mysql/$(whoami).err

# Linux
sudo tail -f /var/log/mysql/error.log
```

## Stopping Services

```bash
# To stop the API server:
# Press Ctrl+C in Terminal 1

# To stop Streamlit:
# Press Ctrl+C in Terminal 2

# To stop MySQL (if needed):
# macOS: brew services stop mysql
# Linux: sudo systemctl stop mysql
# Windows: net stop MySQL80
```

## Troubleshooting

### MySQL Connection Failed

**Error**: `Can't connect to MySQL server on 'localhost:3306'`

**Solutions**:
1. Verify MySQL is running: `mysql -u root -p<your-db-password> -h localhost`
2. Check credentials are correct (root / <your-db-password>)
3. Verify port 3306 is not blocked by firewall
4. Restart MySQL service

### Port Already in Use

**Error**: `Address already in use`

**Solutions**:
```bash
# For API (port 8000):
uvicorn backend.main:app --reload --port 8001

# For Streamlit (port 8501):
streamlit run frontend/app.py --server.port 8502
```

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Ensure dependencies are installed:
```bash
poetry install
```

### Tables Not Found

**Error**: `Table 'loan_approval_dev.loan_applications' doesn't exist`

**Solution**: 
1. Verify MySQL database exists:
```bash
mysql -u root -p<your-db-password> -e "SHOW DATABASES;"
```

2. If not found, restart the API - SQLAlchemy will auto-create tables:
```bash
# Kill the API server (Ctrl+C)
# Restart it
uvicorn backend.main:app --reload
```

### Anthropic API Key Error

**Error**: `No API key provided` or `Invalid API key`

**Solution**: 
1. Verify ANTHROPIC_API_KEY is set:
```bash
echo $ANTHROPIC_API_KEY
```

2. Get a key from [console.anthropic.com](https://console.anthropic.com)
3. Update `.env` file
4. Restart the API server

## Performance Tips

1. **Keep MySQL running** - Don't stop it between sessions
2. **Use `--reload`** - Automatic restart speeds up development
3. **Keep debug logs** - They help identify issues quickly
4. **Monitor terminals** - Watch both API and Streamlit logs for errors

## IDE Recommendations

### VS Code
```bash
# Open project in VS Code
code /home/ubuntu/Desktop/CapStone

# Recommended extensions:
# - Python (Microsoft)
# - Pylance
# - FastAPI (Marvin Rudolph)
```

### PyCharm
```bash
# Open project in PyCharm
# Set interpreter to Poetry virtual environment
```

## Next Steps

1. ✅ Start API and Streamlit
2. ✅ Test submission at http://127.0.0.1:8501
3. ✅ Run tests: `pytest`
4. ✅ Read [Loan_Application_Plan.md](./Loan_Application_Plan.md) for architecture
5. ✅ Continue with Phase 2: Implement AI agents

## Quick Reference Commands

```bash
# Start everything (2 terminals)
# Terminal 1:
export DATABASE_URL="mysql+pymysql://root:<your-db-password>@localhost:3306/loan_approval_dev"
export ANTHROPIC_API_KEY="your-key"
uvicorn backend.main:app --reload

# Terminal 2:
streamlit run frontend/app.py

# Stop services:
# Ctrl+C in each terminal

# Run tests:
pytest

# Check MySQL:
mysql -u root -p<your-db-password> -h localhost

# View API docs:
http://127.0.0.1:8000/docs

# Access UI:
http://127.0.0.1:8501
```

## Support

For issues:
1. Check this guide (LOCAL_SETUP.md)
2. Check [README.md](./README.md)
3. Check [MYSQL_MIGRATION.md](./MYSQL_MIGRATION.md)
4. Review log output in terminals
5. Verify MySQL is running

---

**Everything is local! No Docker needed. Pure Python development. 🐍**

# MySQL Migration Guide

## Overview

The Agentic AI Intelligent Loan Approval System has been successfully migrated from PostgreSQL to MySQL 8.0+.

## Changes Made

### 1. **Database Driver** 
- **Before**: `psycopg2-binary` (PostgreSQL driver)
- **After**: `pymysql` (MySQL driver)
- **Updated in**: `pyproject.toml`

### 2. **Connection String Format**
- **Before**: `postgresql://user:password@host:port/database`
- **After**: `mysql+pymysql://user:password@host:port/database`
- **Updated in**: 
  - `.env.example`
  - `shared/config.py`
  - `docker-compose.yml`

### 3. **SQLAlchemy Configuration**
- Added connection pooling for MySQL
- Added `pool_recycle=3600` to prevent timeout issues
- Added MySQL charset configuration (UTF-8 MB4)
- **Updated in**: `database/db.py`

### 4. **Docker Compose**
- **Before**: PostgreSQL 15 Alpine image
- **After**: MySQL 8.0 official image
- Added proper character set configuration
- Added health check for MySQL
- **Updated in**: `docker-compose.yml`

### 5. **Documentation**
- Updated README.md to reflect MySQL
- Updated QUICKSTART.md with MySQL setup
- Updated START_HERE.md with MySQL credentials
- Updated IMPLEMENTATION_STATUS.md

## MySQL Connection Details

```
Host:     localhost
Port:     3306
Username: root
Password: WP@12345
Database: loan_approval_dev
```

## Setup Instructions

### Option 1: Using Docker Compose (Recommended)

```bash
cd /home/ubuntu/Desktop/CapStone
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
docker-compose up
```

Docker Compose will automatically:
- Create and start a MySQL 8.0 container
- Initialize the database schema
- Start the FastAPI backend
- Start the Streamlit frontend

### Option 2: Using Your Local MySQL

1. **Ensure MySQL is running**
   ```bash
   # Check MySQL status
   mysql -u root -p -h localhost
   ```

2. **Create the database** (if it doesn't exist)
   ```bash
   mysql -u root -pWP@12345 -e "CREATE DATABASE IF NOT EXISTS loan_approval_dev;"
   ```

3. **Install Python dependencies**
   ```bash
   pip install poetry
   poetry install
   ```

4. **Set environment variables**
   ```bash
   export DATABASE_URL="mysql+pymysql://root:WP@12345@localhost:3306/loan_approval_dev"
   export ANTHROPIC_API_KEY="your-api-key"
   ```

5. **Run the application**
   ```bash
   # Terminal 1: Start API
   uvicorn backend.main:app --reload

   # Terminal 2: Start UI
   streamlit run frontend/app.py
   ```

## Database Initialization

The database schema is automatically created when the application starts:

1. **First Time Setup**: SQLAlchemy's `Base.metadata.create_all()` creates all tables
2. **Tables Created**:
   - loan_applications
   - applicants
   - employment_info
   - credit_records
   - loan_details
   - risk_assessments
   - loan_decisions
   - audit_logs

3. **Tables Include**:
   - Proper indexes for performance
   - Foreign key relationships
   - JSON field support (for storing complex data)
   - Automatic timestamp fields

## MySQL-Specific Features Enabled

### 1. **Character Set: UTF-8 MB4**
- Supports full range of Unicode characters
- Required for emojis and international characters
- Configured in docker-compose.yml

### 2. **Connection Pooling**
- Pool size: 10 connections
- Max overflow: 20 connections
- Pool recycle: 3600 seconds (prevents stale connections)

### 3. **Connection Health Checks**
- `pool_pre_ping=True` checks connection before use
- Automatically replaces broken connections
- Prevents "MySQL has gone away" errors

## Testing the Setup

### 1. **Health Check**
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status": "healthy", "version": "0.1.0"}
```

### 2. **API Documentation**
Visit: http://localhost:8000/docs

### 3. **Submit Test Application**
Via Streamlit at: http://localhost:8501

### 4. **Check Database**
```bash
mysql -u root -pWP@12345 loan_approval_dev
SHOW TABLES;
SELECT * FROM loan_applications;
```

## Troubleshooting

### MySQL Connection Issues

**Error: "Can't connect to MySQL server"**
```bash
# Verify MySQL is running
docker ps  # If using Docker
# or
mysql -u root -pWP@12345 -h localhost  # If local
```

**Error: "Access denied for user 'root'@'localhost'"**
```bash
# Check password is correct: WP@12345
# Update DATABASE_URL if needed
```

### Database Schema Issues

**Error: "Table doesn't exist"**
```bash
# Restart the application to trigger schema creation
docker-compose restart api
```

**Error: "Column count doesn't match"**
```bash
# Drop and recreate tables
mysql -u root -pWP@12345 loan_approval_dev
DROP TABLE IF EXISTS loan_applications;
# Restart application
```

### Performance Issues

**Slow queries:**
```bash
# Check MySQL slow query log
docker-compose logs db | grep Query_time
```

**Connection pool exhaustion:**
```bash
# Increase pool size in database/db.py if needed
pool_size=10  # Increase this value
max_overflow=20  # Increase this value
```

## Migration from PostgreSQL (if applicable)

If you had a PostgreSQL database, the data structure remains the same. You would need to:

1. Export PostgreSQL data:
   ```bash
   pg_dump -U user -h host loan_approval > backup.sql
   ```

2. Import to MySQL:
   ```bash
   mysql -u root -pWP@12345 loan_approval_dev < backup.sql
   ```

3. Update connection strings everywhere

4. Verify all tables are present:
   ```bash
   mysql -u root -pWP@12345 -e "SHOW TABLES FROM loan_approval_dev;"
   ```

## Files Modified for MySQL

1. ✅ `pyproject.toml` - Changed database driver
2. ✅ `.env.example` - Updated DATABASE_URL
3. ✅ `shared/config.py` - Default MySQL connection
4. ✅ `database/db.py` - MySQL configuration
5. ✅ `docker-compose.yml` - MySQL service
6. ✅ `README.md` - Documentation updates
7. ✅ `QUICKSTART.md` - Setup instructions
8. ✅ `START_HERE.md` - Quick reference

## Next Steps

1. **Verify Setup Works**
   ```bash
   docker-compose up
   curl http://localhost:8000/health
   ```

2. **Test Application Submission**
   - Visit http://localhost:8501
   - Submit a test application
   - Check data appears in MySQL

3. **Run Tests**
   ```bash
   pytest
   ```

4. **Continue Development**
   - Phase 2: Implement core agents
   - Use MySQL for persisting agent results

## Performance Tips

1. **Add indexes** for frequently queried columns
2. **Use ANALYZE** to optimize query plans
3. **Monitor slow logs** for query optimization
4. **Consider connection pooling** for high load
5. **Archive old data** to maintain performance

## MySQL Documentation

- [MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- [SQLAlchemy MySQL Dialect](https://docs.sqlalchemy.org/en/20/dialects/mysql.html)
- [PyMySQL Documentation](https://pymysql.readthedocs.io/)

## Support

If you encounter issues:

1. Check this migration guide first
2. Review error logs: `docker-compose logs`
3. Check MySQL logs: `docker-compose logs db`
4. Verify MySQL is running: `docker ps`
5. Test connection: `mysql -u root -pWP@12345 -h localhost`

---

**Migration Complete! Your system is now running on MySQL 8.0+ 🎉**

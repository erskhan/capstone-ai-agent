# Deployment Guide

## Quick Start

### Local Development
```bash
docker-compose -f docker-compose.yml up
```

### Production Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Prerequisites

- Docker & Docker Compose
- MySQL 8.0+
- Python 3.11+
- 2GB RAM minimum
- Internet connection for API keys

## Environment Configuration

Create `.env` file:
```env
# Database
DB_ROOT_PASSWORD=secure_password
DB_NAME=loan_approval
DB_USER=loanapp
DB_PASSWORD=secure_password

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# LangSmith
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=loan-approval

# SSL Certificates (for production)
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
```

## Service Startup Order

1. Database (MySQL) - health check required
2. API (FastAPI) - depends on database
3. Frontend (Streamlit) - depends on API
4. Nginx (Reverse Proxy) - depends on API & Frontend

## Scaling

Scale API to 3 instances:
```bash
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

Nginx automatically load-balances across instances.

## Monitoring

Check service status:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f api
docker-compose logs -f frontend
```

Health checks:
```bash
curl http://localhost:8000/health
curl http://localhost:8501
```

## Backup & Recovery

Backup database:
```bash
docker-compose exec db mysqldump -u loanapp -p loan_approval > backup.sql
```

Restore database:
```bash
docker-compose exec -T db mysql -u loanapp -p loan_approval < backup.sql
```

## Troubleshooting

### Database connection errors
```bash
docker-compose logs db
# Verify DATABASE_URL environment variable
```

### Port conflicts
```bash
# Change ports in docker-compose.yml
# Or use different compose file
```

### Memory issues
```bash
docker stats  # Monitor resource usage
# Increase Docker memory allocation
```

## Performance Tuning

### Database
- Enable query caching
- Add indexes on frequently queried columns
- Increase connection pool size

### API
- Enable response compression
- Implement decision caching
- Use connection pooling

### Frontend
- Enable caching headers
- Optimize images
- Lazy load components

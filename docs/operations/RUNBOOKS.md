# Operations Runbooks

## Common Issues & Solutions

### API Service Not Starting

**Symptoms**: Container exits immediately

**Diagnosis**:
```bash
docker-compose logs api
```

**Solutions**:
1. Check database connectivity
   ```bash
   docker-compose exec api python -c "from database.db import SessionLocal; SessionLocal()"
   ```

2. Verify environment variables
   ```bash
   docker-compose exec api env | grep DATABASE
   ```

3. Check Python dependencies
   ```bash
   docker-compose exec api pip check
   ```

### High API Response Time

**Symptoms**: Requests taking >10 seconds

**Diagnosis**:
1. Check database performance
   ```sql
   SHOW PROCESSLIST;
   ```

2. Monitor system resources
   ```bash
   docker stats
   ```

**Solutions**:
1. Clear cache: `CacheService.clear_all()`
2. Restart API service: `docker-compose restart api`
3. Scale API: `docker-compose up -d --scale api=3`

### Database Disk Full

**Symptoms**: Database errors, service interruption

**Solutions**:
1. Check disk usage
   ```bash
   docker exec loan-db df -h /var/lib/mysql
   ```

2. Archive old records
   ```sql
   DELETE FROM audit_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
   ```

3. Optimize tables
   ```sql
   OPTIMIZE TABLE workflow_executions;
   ```

### SSL Certificate Errors

**Symptoms**: HTTPS not working

**Solutions**:
1. Verify certificate files
   ```bash
   ls -la ./ssl/
   ```

2. Check certificate expiration
   ```bash
   openssl x509 -in ./ssl/cert.pem -noout -dates
   ```

3. Restart nginx
   ```bash
   docker-compose restart nginx
   ```

## Daily Operations

### Morning Health Check
```bash
# Check all services running
docker-compose ps

# Check logs for errors
docker-compose logs --since 24h | grep ERROR

# Check database status
docker-compose exec db mysqladmin -u root -p status
```

### Evening Backup
```bash
docker-compose exec db mysqldump -u loanapp -p loan_approval | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Weekly Maintenance
1. Clear old logs
2. Optimize database tables
3. Review error rates
4. Update dependencies (non-production)

## Scaling Guide

### Horizontal Scaling (Add API instances)
```bash
docker-compose -f docker-compose.prod.yml up -d --scale api=5
```

Nginx will automatically load-balance.

### Vertical Scaling (Increase resources)
Edit docker-compose.prod.yml:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Database Scaling
For production, consider:
- Database replication
- Read replicas
- Sharding by application_id

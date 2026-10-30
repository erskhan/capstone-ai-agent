# Monitoring & Observability

## Health Metrics

### API Health
```bash
curl http://localhost:8000/health/detailed | jq .
```

### Database Health
```bash
docker-compose exec db mysqladmin -u root -p status
```

### System Resources
```bash
docker stats
```

## Key Metrics to Monitor

### Application Metrics
- Request latency (p50, p95, p99)
- Request count by endpoint
- Error rate (4xx, 5xx)
- Decision distribution (approved/rejected/review)

### Infrastructure Metrics
- CPU usage per service
- Memory usage per service
- Disk I/O
- Network traffic

### Database Metrics
- Query latency
- Connection count
- Slow query log
- Replication lag (if applicable)

## Alerting

### Critical Alerts
- Service down (health check failing)
- Database connection errors
- High error rate (>1%)
- Disk space critical (<10%)

### Warning Alerts
- High latency (>5 seconds)
- Memory usage >80%
- CPU usage >80% sustained

## Logging

### Log Aggregation
All services log to stdout, captured by Docker.

View logs:
```bash
docker-compose logs -f [service]
```

### Structured Logging
All logs include:
- Timestamp
- Service name
- Level (INFO, ERROR, WARNING)
- Correlation ID
- Custom fields (application_id, risk_score, etc.)

## Performance Baseline

Establish baselines:
- Request latency: <2 seconds (p95)
- Decision processing: <10 seconds
- API throughput: >100 req/s
- Database queries: <100ms average

Monitor trends week-over-week.

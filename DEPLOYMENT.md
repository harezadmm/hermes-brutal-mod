# Production Deployment Guide

Complete guide for deploying RedMess in production environments.

---

## Deployment Architectures

### 1. Single-Server Deployment (Small Scale)

**Best for:** Personal use, 1-50 users

```
┌─────────────────────────────────┐
│     Single VPS/Server           │
│  ┌──────────────────────────┐  │
│  │   Telegram Bot Process    │  │
│  │   + RedMess Core          │  │
│  │   + SQLite Database       │  │
│  └──────────────────────────┘  │
│                                 │
│  Resources: 1 CPU, 2GB RAM     │
│  Cost: $5-10/month             │
└─────────────────────────────────┘
```

### 2. Load-Balanced Deployment (Medium Scale)

**Best for:** Public bots, 50-1000 users

```
                  ┌──────────────┐
                  │ Load Balancer│
                  │   (nginx)    │
                  └───────┬──────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ Bot #1  │     │ Bot #2  │     │ Bot #3  │
    │ RedMess │     │ RedMess │     │ RedMess │
    └────┬────┘     └────┬────┘     └────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                  ┌──────────────┐
                  │  PostgreSQL  │
                  │   Database   │
                  └──────────────┘

Resources: 3x 2CPU/4GB + 1x DB server
Cost: $40-60/month
```

### 3. High-Availability Deployment (Large Scale)

**Best for:** Enterprise, 1000+ users

```
┌─────────────────────────────────────────────────┐
│              CDN / DDoS Protection              │
│                 (Cloudflare)                    │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │   Load Balancer   │
        │   (HA Pair)       │
        └─────────┬─────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│ Bot    │   │ Bot    │   │ Bot    │
│ Pool   │   │ Pool   │   │ Pool   │
│ 1-5    │   │ 6-10   │   │11-15   │
└───┬────┘   └───┬────┘   └───┬────┘
    │            │            │
    └────────────┼────────────┘
                 ▼
    ┌────────────────────────┐
    │   Redis Cluster        │
    │   (Caching/Sessions)   │
    └────────────────────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │  PostgreSQL Cluster    │
    │  (Master + Replicas)   │
    └────────────────────────┘

Resources: 15x 4CPU/8GB + 3x DB + 3x Redis
Cost: $500-1000/month
```

---

## Cloud Provider Setup

### AWS Deployment

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure
aws configure

# Create EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name redmess-key \
  --security-group-ids sg-xxxxxx \
  --subnet-id subnet-xxxxxx \
  --user-data file://setup.sh

# SSH into instance
ssh -i redmess-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# Deploy
git clone https://github.com/yourusername/RedMess.git
cd RedMess
./deploy.sh
```

### DigitalOcean Deployment

```bash
# Install doctl
snap install doctl
doctl auth init

# Create droplet
doctl compute droplet create redmess-bot \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --ssh-keys YOUR_SSH_KEY_ID

# Get IP
doctl compute droplet list

# SSH and deploy
ssh root@DROPLET_IP
git clone https://github.com/yourusername/RedMess.git
cd RedMess
./deploy.sh
```

### Vultr Deployment

```bash
# Create server via web UI or API
# OS: Ubuntu 22.04
# Plan: 2 CPU, 4 GB RAM

# SSH
ssh root@SERVER_IP

# Deploy
curl -sSL https://raw.githubusercontent.com/yourusername/RedMess/main/install.sh | bash
cd RedMess
./deploy.sh
```

---

## Docker Production Deployment

### Docker Compose (Production)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  redmess-bot:
    image: ghcr.io/yourusername/redmess:latest
    restart: always
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://redmess:${DB_PASSWORD}@postgres:5432/redmess
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    healthcheck:
      test: ["CMD", "python", "healthcheck.py"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_DB=redmess
      - POSTGRES_USER=redmess
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - redmess-bot

volumes:
  postgres_data:
  redis_data:
```

### Deploy

```bash
# Create .env.prod
cat > .env.prod << EOF
TELEGRAM_BOT_TOKEN=your_token
ANTHROPIC_API_KEY=your_key
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
EOF

# Deploy
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f redmess-bot

# Scale up
docker-compose -f docker-compose.prod.yml up -d --scale redmess-bot=5
```

---

## Kubernetes Deployment

### Kubernetes Manifests

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redmess-bot
  namespace: redmess
spec:
  replicas: 3
  selector:
    matchLabels:
      app: redmess-bot
  template:
    metadata:
      labels:
        app: redmess-bot
    spec:
      containers:
      - name: redmess
        image: ghcr.io/yourusername/redmess:latest
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: redmess-secrets
              key: telegram-token
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: redmess-secrets
              key: anthropic-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: redmess-secrets
              key: database-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: redmess-bot
  namespace: redmess
spec:
  selector:
    app: redmess-bot
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: redmess-bot-hpa
  namespace: redmess
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: redmess-bot
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace redmess

# Create secrets
kubectl create secret generic redmess-secrets \
  --from-literal=telegram-token=YOUR_TOKEN \
  --from-literal=anthropic-key=YOUR_KEY \
  --from-literal=database-url=postgresql://... \
  -n redmess

# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n redmess
kubectl logs -f deployment/redmess-bot -n redmess

# Scale
kubectl scale deployment redmess-bot --replicas=5 -n redmess
```

---

## Database Setup

### PostgreSQL (Production)

```bash
# Install PostgreSQL
sudo apt install postgresql-15 postgresql-contrib

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE redmess;
CREATE USER redmess WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE redmess TO redmess;
\c redmess
GRANT ALL ON SCHEMA public TO redmess;
EOF

# Configure for remote access
sudo nano /etc/postgresql/15/main/postgresql.conf
# Set: listen_addresses = '*'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: host all all 0.0.0.0/0 md5

# Restart
sudo systemctl restart postgresql

# Run migrations
cd RedMess
python migrate.py
```

### Database Backups

```bash
# Automated backup script
cat > /usr/local/bin/backup-redmess.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/redmess"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/redmess_$TIMESTAMP.sql.gz"

mkdir -p $BACKUP_DIR

# Backup
pg_dump -U redmess redmess | gzip > $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "redmess_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_FILE s3://your-bucket/backups/

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x /usr/local/bin/backup-redmess.sh

# Cron job (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/backup-redmess.sh" | crontab -
```

---

## Monitoring & Logging

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"

volumes:
  prometheus_data:
  grafana_data:
```

### Logging (ELK Stack)

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.9.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.9.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.9.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

volumes:
  es_data:
```

---

## Security Hardening

### SSL/TLS Setup

```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d bot.yourdomain.com

# Auto-renewal
echo "0 3 * * * certbot renew --quiet" | sudo crontab -
```

### Firewall Configuration

```bash
# UFW firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Rate limiting (fail2ban)
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Secrets Management

```bash
# Using HashiCorp Vault
docker run -d --name vault \
  -p 8200:8200 \
  --cap-add=IPC_LOCK \
  vault:latest

# Store secrets
vault kv put secret/redmess \
  telegram_token=XXX \
  anthropic_key=XXX \
  db_password=XXX

# Retrieve in app
vault kv get -field=telegram_token secret/redmess
```

---

## Performance Optimization

### Redis Caching

```python
# Enable Redis caching in config.yaml
redis:
  enabled: true
  url: redis://localhost:6379
  cache_ttl: 3600
  
caching:
  enabled: true
  provider: redis
  strategies:
    - user_context: 3600
    - ai_responses: 1800
    - rate_limits: 60
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_expires_at ON subscriptions(expires_at);

-- Analyze tables
ANALYZE users;
ANALYZE subscriptions;
ANALYZE messages;

-- Vacuum
VACUUM ANALYZE;
```

### Connection Pooling

```python
# config.yaml
database:
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600
```

---

## Troubleshooting Production

### Common Issues

**High CPU Usage:**
```bash
# Check processes
top
htop

# Check Docker stats
docker stats

# Solution: Scale horizontally
docker-compose up -d --scale redmess-bot=5
```

**Memory Leaks:**
```bash
# Monitor memory
free -h
docker stats --no-stream

# Restart containers
docker-compose restart redmess-bot
```

**Database Connection Errors:**
```bash
# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Increase max connections
sudo nano /etc/postgresql/15/main/postgresql.conf
# Set: max_connections = 200

sudo systemctl restart postgresql
```

---

## Production Checklist

- [ ] Environment variables secured (not in code)
- [ ] Database backed up automatically
- [ ] SSL/TLS certificates installed
- [ ] Firewall configured
- [ ] Monitoring enabled (Prometheus/Grafana)
- [ ] Logging configured (ELK/Loki)
- [ ] Rate limiting enabled
- [ ] Health checks configured
- [ ] Auto-scaling rules set
- [ ] Disaster recovery plan documented
- [ ] Secrets rotated regularly
- [ ] Updates automated
- [ ] Performance baseline established
- [ ] Security audit completed

---

**Production deployment complete! Monitor metrics and scale as needed.**

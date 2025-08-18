# Production Deployment Guide 🚀

## Overview
Complete production deployment guide for the Japanese Language Learning Application - a full-stack React Native + FastAPI application with voice recognition and learning analytics.

## System Requirements

### Minimum Server Requirements
- **CPU**: 2 cores, 2.4GHz+
- **RAM**: 4GB minimum, 8GB recommended  
- **Storage**: 20GB SSD minimum
- **OS**: Ubuntu 20.04+ or any Docker-compatible Linux distribution

### Required Software
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **SSL Certificate**: For HTTPS (Let's Encrypt recommended)

---

## Quick Production Deployment

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply Docker group changes
```

### 2. Application Deployment
```bash
# Clone repository
git clone <repository-url>
cd speechify

# Setup production environment
cp backend-new/.env.example backend-new/.env
cp frontend/.env.example frontend/.env

# Edit environment files with production values
nano backend-new/.env
nano frontend/.env

# Deploy full stack
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

---

## Environment Configuration

### Backend Environment (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://japanese_user:secure_password@postgres:5432/japanese_learning
REDIS_URL=redis://redis:6379

# Security
JWT_SECRET_KEY=<generate-secure-random-key>
JWT_REFRESH_SECRET_KEY=<generate-secure-random-key>
SECRET_KEY=<generate-secure-random-key>

# Application
ENVIRONMENT=production
API_V1_STR=/api/v1
PROJECT_NAME=Japanese Learning API

# Email (Optional - for password reset)
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# External Services (Optional)
OPENAI_API_KEY=your-openai-key  # For advanced TTS/STT
```

### Frontend Environment (.env)
```bash
# API Configuration
EXPO_PUBLIC_API_BASE_URL=https://your-domain.com/api/v1
EXPO_PUBLIC_WS_BASE_URL=wss://your-domain.com/ws

# App Configuration
EXPO_PUBLIC_APP_NAME=Japanese Learning
EXPO_PUBLIC_APP_VERSION=1.0.0
EXPO_PUBLIC_ENVIRONMENT=production

# Feature Flags
EXPO_PUBLIC_ENABLE_VOICE_FEATURES=true
EXPO_PUBLIC_ENABLE_ANALYTICS=true
EXPO_PUBLIC_ENABLE_DEBUG=false
```

---

## SSL Configuration (HTTPS)

### Using Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Add to crontab for auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Update Nginx Configuration
```nginx
# /etc/nginx/sites-available/japanese-learning
server {
    listen 80;
    server_name your-domain.com api.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Database Management

### Initial Database Setup
```bash
# Create database and user (if using external PostgreSQL)
sudo -u postgres psql

CREATE DATABASE japanese_learning;
CREATE USER japanese_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE japanese_learning TO japanese_user;
\q

# Run migrations
docker-compose exec backend alembic upgrade head

# Create initial admin user (optional)
docker-compose exec backend python scripts/create_admin_user.py
```

### Backup Strategy
```bash
# Create backup script
cat > /opt/backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec postgres pg_dump -U japanese_user -d japanese_learning > $BACKUP_DIR/db_backup_$DATE.sql

# Keep last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/backup-db.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/backup-db.sh
```

---

## Monitoring & Logging

### Health Check Monitoring
```bash
# Create monitoring script
cat > /opt/health-check.sh << 'EOF'
#!/bin/bash
API_URL="https://api.your-domain.com/health"
WEBHOOK_URL="your-slack-webhook-url"  # Optional

if ! curl -f -s $API_URL > /dev/null; then
    echo "API health check failed at $(date)"
    # Send alert (optional)
    curl -X POST -H 'Content-type: application/json' \
         --data '{"text":"Japanese Learning API is down!"}' \
         $WEBHOOK_URL
fi
EOF

chmod +x /opt/health-check.sh

# Add to crontab (check every 5 minutes)
crontab -e
# Add: */5 * * * * /opt/health-check.sh
```

### Log Management
```bash
# Setup log rotation
sudo tee /etc/logrotate.d/japanese-learning << 'EOF'
/var/lib/docker/containers/*/*-json.log {
    rotate 7
    daily
    missingok
    notifempty
    compress
    copytruncate
    maxsize 100M
}
EOF

# View application logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

---

## Security Configuration

### Firewall Setup
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
sudo ufw status
```

### Docker Security
```bash
# Create non-root user for containers
# Add to docker-compose.prod.yml:
# services:
#   backend:
#     user: "1000:1000"  # non-root user
#     security_opt:
#       - no-new-privileges:true
```

---

## Performance Optimization

### Database Optimization
```sql
-- Connect to PostgreSQL and run optimization queries
-- docker-compose exec postgres psql -U japanese_user -d japanese_learning

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_japanese_sentences_difficulty ON japanese_sentences(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON learning_sessions(user_id);

-- Analyze tables for query optimization
ANALYZE users;
ANALYZE japanese_sentences;
ANALYZE user_progress;
ANALYZE learning_sessions;
```

### Redis Configuration
```bash
# Optimize Redis configuration
# Edit redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
tcp-keepalive 60
timeout 0
```

---

## Mobile App Deployment

### Build for Production

#### iOS Build
```bash
cd frontend

# Install dependencies
npm install

# Build for iOS
eas build --platform ios --profile production

# Submit to App Store (after build)
eas submit --platform ios
```

#### Android Build
```bash
# Build for Android
eas build --platform android --profile production

# Submit to Google Play Store (after build)
eas submit --platform android
```

### App Store Configuration
```javascript
// app.config.js
export default {
  expo: {
    name: "Japanese Learning",
    slug: "japanese-learning",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/icon.png",
    splash: {
      image: "./assets/splash.png",
      resizeMode: "contain",
      backgroundColor: "#ffffff"
    },
    updates: {
      fallbackToCacheTimeout: 0
    },
    assetBundlePatterns: [
      "**/*"
    ],
    ios: {
      supportsTablet: true,
      bundleIdentifier: "com.yourcompany.japaneselearning"
    },
    android: {
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#FFFFFF"
      },
      package: "com.yourcompany.japaneselearning"
    }
  }
};
```

---

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database container status
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test database connection
docker-compose exec postgres psql -U japanese_user -d japanese_learning -c "SELECT 1"
```

#### API Connection Issues
```bash
# Check backend container status
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Test API directly
curl -v http://localhost:8000/health
```

#### Memory Issues
```bash
# Check container resource usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
```

### Performance Monitoring
```bash
# Install monitoring tools
docker run -d --name=netdata --restart=always \
  --pid=host --network=host \
  -v /etc/passwd:/host/etc/passwd:ro \
  -v /etc/group:/host/etc/group:ro \
  -v /proc:/host/proc:ro \
  -v /sys:/host/sys:ro \
  netdata/netdata

# Access monitoring dashboard at http://your-server:19999
```

---

## Maintenance Checklist

### Daily
- [ ] Check application health status
- [ ] Monitor disk space usage
- [ ] Review error logs

### Weekly  
- [ ] Review application performance metrics
- [ ] Check backup integrity
- [ ] Update SSL certificates if needed
- [ ] Monitor user activity and system resources

### Monthly
- [ ] Security updates for base system
- [ ] Database optimization and maintenance
- [ ] Review and rotate log files
- [ ] Performance testing and optimization review

---

## Support & Documentation

### API Documentation
- **Production**: https://api.your-domain.com/docs
- **Interactive Testing**: https://api.your-domain.com/redoc

### Application URLs
- **API Base**: https://api.your-domain.com/api/v1
- **Health Check**: https://api.your-domain.com/health
- **Admin Panel**: https://api.your-domain.com/admin (if implemented)

### Contact Information
- **Technical Support**: your-email@domain.com
- **Documentation**: Link to detailed documentation
- **Issue Tracking**: GitHub Issues or your preferred platform

---

## Summary

This production deployment guide provides a complete setup for deploying the Japanese Language Learning Application in a production environment. The application is production-ready with:

✅ **Scalable Architecture**: Docker-based microservices
✅ **Security**: HTTPS, JWT authentication, firewall configuration  
✅ **Monitoring**: Health checks, logging, performance monitoring
✅ **Backup Strategy**: Automated database backups
✅ **Mobile Ready**: iOS and Android app store deployment

For technical support or questions, refer to the main project documentation or contact the development team.
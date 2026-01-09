# Deployment Guide

## Production Deployment

### Prerequisites

- Ubuntu 20.04+ / CentOS 8+ server
- Python 3.9+
- PostgreSQL 14+
- Node.js 18+
- Nginx
- SSL Certificate (Let's Encrypt recommended)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx build-essential cmake -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Database Setup

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE attendance_system;
CREATE USER attendance_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE attendance_system TO attendance_user;
\q
```

### 3. Backend Deployment

```bash
# Clone repository
cd /var/www
git clone <your-repo-url> attendance-system
cd attendance-system/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Initialize database
python init_db.py

# Test application
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4. Frontend Deployment

```bash
cd /var/www/attendance-system/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Output will be in dist/ folder
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/attendance-system`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Frontend
    location / {
        root /var/www/attendance-system/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase upload size for face images
    client_max_body_size 16M;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/attendance-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com
```

### 7. Systemd Service for Backend

Create `/etc/systemd/system/attendance-backend.service`:

```ini
[Unit]
Description=Attendance System Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/attendance-system/backend
Environment="PATH=/var/www/attendance-system/backend/venv/bin"
ExecStart=/var/www/attendance-system/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start attendance-backend
sudo systemctl enable attendance-backend
sudo systemctl status attendance-backend
```

### 8. Security Hardening

1. **Firewall Setup:**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. **PostgreSQL Security:**
```bash
# Edit pg_hba.conf to restrict access
sudo nano /etc/postgresql/14/main/pg_hba.conf
# Change to: host all all 127.0.0.1/32 md5
sudo systemctl restart postgresql
```

3. **Update .env with strong secrets:**
```bash
# Generate strong secret keys
python -c "import secrets; print(secrets.token_hex(32))"
```

### 9. Monitoring & Logs

```bash
# View backend logs
sudo journalctl -u attendance-backend -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 10. Backup Strategy

```bash
# Create backup script at /usr/local/bin/backup-attendance.sh
#!/bin/bash
BACKUP_DIR="/backups/attendance"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -U attendance_user attendance_system > $BACKUP_DIR/db_$DATE.sql

# Face images backup
tar -czf $BACKUP_DIR/faces_$DATE.tar.gz /var/www/attendance-system/backend/uploads/faces/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Make executable and add to cron:
```bash
chmod +x /usr/local/bin/backup-attendance.sh
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-attendance.sh
```

## Docker Deployment (Alternative)

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: attendance_system
      POSTGRES_USER: attendance_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - attendance_network

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://attendance_user:your_secure_password@postgres:5432/attendance_system
    volumes:
      - ./backend/uploads:/app/uploads
    depends_on:
      - postgres
    networks:
      - attendance_network

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - attendance_network

volumes:
  postgres_data:

networks:
  attendance_network:
```

Deploy:
```bash
docker-compose up -d
```

## Performance Optimization

1. **Enable Gzip in Nginx:**
```nginx
gzip on;
gzip_vary on;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;
```

2. **Database Indexing:**
Already included in models (check models.py for indexed fields)

3. **Redis Caching (Optional):**
```bash
sudo apt install redis-server
pip install redis flask-caching
```

## Maintenance

### Update Application

```bash
cd /var/www/attendance-system
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart attendance-backend

cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

### Database Migrations

```bash
cd /var/www/attendance-system/backend
source venv/bin/activate
flask db upgrade
```

## Troubleshooting

### Backend not starting
```bash
sudo journalctl -u attendance-backend -n 50
# Check for Python errors, database connection issues
```

### Database connection errors
```bash
# Test database connection
psql -U attendance_user -d attendance_system -h localhost
```

### Face recognition slow
```bash
# Increase workers in gunicorn
# Edit service file: -w 8 (instead of 4)
```

## Support

For issues, check:
1. System logs: `sudo journalctl -xe`
2. Application logs: `sudo journalctl -u attendance-backend`
3. Nginx logs: `/var/log/nginx/error.log`

# ClaimLens 2.0 - Deployment Guide

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/EmanFatima764/claimlens-2.git
cd claimlens-2

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose up

# Or manually:
cd backend && pip install -r requirements.txt && uvicorn backend.app.main:app --reload
# In another terminal:
cd frontend && npm install && npm run dev
```

## Production Deployment

### Option 1: Render + Netlify (Recommended)

#### Backend on Render

1. Create account at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: claimlens-backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`
   - **Environment Variables**:
     ```
     APP_ENV=production
     SUPABASE_URL=xxx
     SUPABASE_ANON_KEY=xxx
     SUPABASE_SERVICE_ROLE_KEY=xxx
     GEMINI_API_KEY=xxx
     ANTHROPIC_API_KEY=xxx
     TAVILY_API_KEY=xxx
     CORS_ORIGINS=https://yourdomain.com
     ```
5. Deploy

#### Frontend on Netlify

1. Create account at [netlify.com](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Connect your GitHub repo
4. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `.next`
   - **Environment Variables**:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-on-render.com
     ```
5. Deploy

### Option 2: AWS (EC2 + RDS)

```bash
# Launch EC2 instance (Ubuntu 22.04)
# Security group: allow ports 80, 443, 8000

ssh -i key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update && sudo apt install python3-pip nodejs npm nginx

# Clone and setup
git clone https://github.com/EmanFatima764/claimlens-2.git
cd claimlens-2

# Setup backend
cd backend
pip install -r requirements.txt

# Setup systemd service
sudo tee /etc/systemd/system/claimlens-backend.service > /dev/null << EOF
[Unit]
Description=ClaimLens Backend
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/claimlens-2/backend
ExecStart=/usr/bin/python3 -m uvicorn backend.app.main:app --port 8000
Restart=always
Environment="PATH=/home/ubuntu/claimlens-2/backend/venv/bin"
EOF

sudo systemctl daemon-reload
sudo systemctl enable claimlens-backend
sudo systemctl start claimlens-backend

# Setup frontend
cd ../frontend
npm install && npm run build

# Configure nginx
sudo tee /etc/nginx/sites-available/claimlens > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location / {
        root /home/ubuntu/claimlens-2/frontend/.next;
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/claimlens /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option 3: Vercel + Railway

#### Backend on Railway

1. Go to [railway.app](https://railway.app)
2. Create new project
3. Add GitHub repo
4. Set root directory: `backend`
5. Add environment variables
6. Deploy

#### Frontend on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repo
3. Set root directory: `frontend`
4. Add environment variables
5. Deploy

## Database Migrations

```bash
# In Supabase dashboard, go to SQL Editor
# Create new query and paste contents of:
# backend/migrations/001_init_schema.sql

# Or use supabase-cli:
supabase migration new init_schema
# Edit migration file
supabase db push --remote
```

## Monitoring

### Sentry Setup

```python
# In backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=settings.environment,
)
```

### Logs

- Backend: Use Python logging, ship to Axiom/Datadog
- Frontend: Use Sentry, ship browser errors
- Database: Enable Supabase query logging

## Scaling Considerations

### Horizontal Scaling

- Use load balancer (Render/Railway handle this)
- Run multiple backend instances
- Add Redis cache layer

### Database Optimization

- Enable read replicas
- Use connection pooling
- Archive old investigations
- Partition by date

### API Optimization

- Implement caching headers
- Add pagination
- Use compression
- Implement rate limiting

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Enable CORS restrictions
- [ ] Implement rate limiting
- [ ] Add API authentication (future)
- [ ] Sanitize all inputs
- [ ] Use CSRF tokens for forms
- [ ] Enable security headers
- [ ] Regular dependency updates
- [ ] Backup database regularly
- [ ] Monitor API logs

## Troubleshooting

### Backend won't start

```bash
# Check logs
journalctl -u claimlens-backend -n 50

# Verify environment variables
echo $SUPABASE_URL

# Test database connection
python -c "from backend.app.integrations.supabase_client import SupabaseClient; print(SupabaseClient().health_check())"
```

### Frontend not connecting to backend

```bash
# Check CORS
curl -H "Origin: https://your-domain.com" -i http://your-backend/health

# Verify environment variable
echo $NEXT_PUBLIC_API_URL
```

### Database connection issues

```bash
# Verify credentials in .env
# Check Supabase dashboard for connection limits
# Increase connection pool size if needed
```

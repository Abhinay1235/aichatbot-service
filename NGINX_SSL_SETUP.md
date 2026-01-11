# Nginx SSL Setup Guide

This guide covers setting up Nginx as a reverse proxy with SSL certificate for your AI Chatbot API service.

## Overview

- **Nginx** will act as a reverse proxy in front of your FastAPI application
- **Let's Encrypt** will provide free SSL certificates
- API will be accessible at `https://ai-chatbot-service.abhinaykumar.com`
- FastAPI runs on port 8000, Nginx listens on ports 80 and 443

## Prerequisites

- EC2 instance running and accessible
- Domain name pointing to your EC2 instance's Elastic IP
- SSH access to the EC2 instance
- Root/sudo access on the EC2 instance

## Step-by-Step Setup

### Step 1: Install Nginx and Certbot

SSH into your EC2 instance and run:

```bash
# Update system
sudo yum update -y

# Install Nginx
sudo yum install -y nginx

# Install Certbot (for Let's Encrypt SSL certificates)
sudo yum install -y certbot python3-certbot-nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 2: Configure DNS

Ensure your domain's DNS is pointing to your EC2 instance:

1. **In GoDaddy DNS Management:**
   - Add an **A record**:
     - Type: A
     - Name: `ai-chatbot-service`
     - Value: Your EC2 Elastic IP address
     - TTL: 3600 (1 hour)
   - Save changes

2. **Verify DNS propagation:**
   ```bash
   dig ai-chatbot-service.abhinaykumar.com
   # or
   nslookup ai-chatbot-service.abhinaykumar.com
   ```
   
   Should return your EC2 Elastic IP address.

### Step 3: Create Nginx Configuration

Create the Nginx configuration file for your API:

```bash
sudo tee /etc/nginx/conf.d/chatbot-api.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name ai-chatbot-service.abhinaykumar.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ai-chatbot-service.abhinaykumar.com;

    # SSL certificate paths (will be set by certbot)
    ssl_certificate /etc/letsencrypt/live/ai-chatbot-service.abhinaykumar.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai-chatbot-service.abhinaykumar.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy settings
    client_max_body_size 10M;
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Forward to FastAPI application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        
        # WebSocket support (if needed in future)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Buffering
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Health check endpoint (optional - direct access)
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        access_log off;
    }
}
EOF
```

### Step 4: Test Nginx Configuration

```bash
# Test Nginx configuration for syntax errors
sudo nginx -t

# If successful, reload Nginx
sudo systemctl reload nginx
```

### Step 5: Obtain SSL Certificate

Use Certbot to automatically obtain and configure SSL certificate:

```bash
# Obtain SSL certificate (Certbot will modify Nginx config automatically)
sudo certbot --nginx -d ai-chatbot-service.abhinaykumar.com --non-interactive --agree-tos --email your-email@example.com

# Replace your-email@example.com with your actual email address
```

**Note:** Certbot will:
- Automatically obtain SSL certificate from Let's Encrypt
- Modify your Nginx configuration to include SSL paths
- Set up automatic renewal

### Step 6: Verify SSL Certificate

```bash
# Check certificate status
sudo certbot certificates

# Test SSL connection
curl -I https://ai-chatbot-service.abhinaykumar.com/health
```

### Step 7: Set Up Automatic Certificate Renewal

Certbot automatically sets up a cron job, but verify it:

```bash
# Check renewal configuration
sudo certbot renew --dry-run

# Verify cron job exists
sudo systemctl status certbot.timer
# or
sudo crontab -l
```

### Step 8: Update Security Group

Ensure your EC2 security group allows traffic on ports 80 and 443:

**In AWS Console:**
1. Go to EC2 → Security Groups
2. Select your chatbot security group
3. Add inbound rules:
   - **Port 80** (HTTP) from `0.0.0.0/0` - for Let's Encrypt validation
   - **Port 443** (HTTPS) from `0.0.0.0/0` - for HTTPS access

**Or via AWS CLI:**
```bash
aws ec2 authorize-security-group-ingress \
  --group-id <your-security-group-id> \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region us-east-1

aws ec2 authorize-security-group-ingress \
  --group-id <your-security-group-id> \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

### Step 9: Update CloudFormation Template (Optional)

To persist the security group rules in CloudFormation, update `infrastructure/cloudformation-template.yaml`:

The template already includes ports 80 and 443, so no changes needed.

### Step 10: Test the Setup

```bash
# Test HTTP redirect
curl -I http://ai-chatbot-service.abhinaykumar.com/health

# Should redirect to HTTPS

# Test HTTPS
curl https://ai-chatbot-service.abhinaykumar.com/health

# Test API endpoint
curl https://ai-chatbot-service.abhinaykumar.com/docs
```

## Automation Script

For convenience, here's a complete setup script:

```bash
#!/bin/bash
set -e

DOMAIN="ai-chatbot-service.abhinaykumar.com"
EMAIL="your-email@example.com"  # Change this to your email

echo "🔧 Setting up Nginx with SSL for $DOMAIN"

# Install Nginx and Certbot
sudo yum update -y
sudo yum install -y nginx certbot python3-certbot-nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Create Nginx configuration (without SSL first)
sudo tee /etc/nginx/conf.d/chatbot-api.conf > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Test and reload Nginx
sudo nginx -t && sudo systemctl reload nginx

# Obtain SSL certificate
echo "📜 Obtaining SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect

# Test certificate renewal
sudo certbot renew --dry-run

echo "✅ Nginx SSL setup complete!"
echo "Your API is now available at: https://$DOMAIN"
```

**To use the script:**
1. Save it as `setup-nginx-ssl.sh` on your EC2 instance
2. Make it executable: `chmod +x setup-nginx-ssl.sh`
3. Edit the `DOMAIN` and `EMAIL` variables
4. Run: `sudo ./setup-nginx-ssl.sh`

## Update Frontend API URL

After setting up HTTPS, update your frontend to use the new HTTPS endpoint:

**In AWS Amplify:**
1. Go to your Amplify app → Environment variables
2. Update `VITE_API_URL` to: `https://ai-chatbot-service.abhinaykumar.com`

**Or in your constants file:**
```typescript
// src/utils/constants.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://ai-chatbot-service.abhinaykumar.com'
```

## Update Backend CORS

Update your backend CORS configuration to allow your UI domain:

```python
# src/main.py
allowed_origins = [
    "https://yourdomain.com",  # Your UI domain
    "https://www.yourdomain.com",  # www variant
    "https://ai-chatbot-service.abhinaykumar.com",  # API domain (if needed)
    "http://localhost:3000",
    "http://localhost:5173",
]
```

## Verification

After setup, verify everything works:

```bash
# 1. Check Nginx status
sudo systemctl status nginx

# 2. Check SSL certificate
sudo certbot certificates

# 3. Test HTTPS endpoint
curl https://ai-chatbot-service.abhinaykumar.com/health

# 4. Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 5. Verify certificate auto-renewal
sudo certbot renew --dry-run
```

## Troubleshooting

### Certificate Not Obtained

**Issue:** Certbot fails to obtain certificate

**Solutions:**
- Verify DNS is pointing to your EC2 IP: `dig ai-chatbot-service.abhinaykumar.com`
- Ensure port 80 is open in security group (needed for Let's Encrypt validation)
- Check Nginx is running: `sudo systemctl status nginx`
- Verify domain is accessible: `curl http://ai-chatbot-service.abhinaykumar.com`

### Nginx Not Starting

**Issue:** Nginx fails to start

**Solutions:**
```bash
# Check configuration syntax
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Verify port 80/443 are not in use
sudo netstat -tulpn | grep -E ':(80|443)'
```

### SSL Certificate Expired

**Issue:** Certificate expired

**Solutions:**
```bash
# Manually renew certificate
sudo certbot renew

# Check renewal schedule
sudo systemctl status certbot.timer

# Force renewal (before expiry)
sudo certbot renew --force-renewal
```

### 502 Bad Gateway

**Issue:** Nginx returns 502 Bad Gateway

**Solutions:**
- Check FastAPI service is running: `sudo systemctl status chatbot-service`
- Verify FastAPI is listening on port 8000: `curl http://localhost:8000/health`
- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### Connection Refused

**Issue:** Cannot connect to HTTPS endpoint

**Solutions:**
- Verify security group allows port 443
- Check Nginx is running: `sudo systemctl status nginx`
- Verify firewall rules: `sudo iptables -L -n` (if using iptables)
- Test locally: `curl https://localhost/health`

## Maintenance

### Renew Certificates Manually

```bash
sudo certbot renew
sudo systemctl reload nginx
```

### Update Nginx Configuration

After modifying `/etc/nginx/conf.d/chatbot-api.conf`:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### View Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

## Architecture

```
Internet
   │
   ├─ HTTP (port 80) → Redirects to HTTPS
   └─ HTTPS (port 443) → Nginx (SSL termination)
                        │
                        └─ Proxy to FastAPI (port 8000)
```

## Benefits

✅ **SSL/TLS encryption** - All traffic encrypted
✅ **Free SSL certificates** - Let's Encrypt (auto-renewal)
✅ **Better security** - Security headers, HTTPS only
✅ **Reverse proxy** - Nginx handles SSL, FastAPI handles API logic
✅ **Performance** - Nginx handles static files efficiently
✅ **Easy maintenance** - Certbot manages certificate renewal

## Next Steps

1. ✅ Set up Nginx with SSL
2. ⬜ Update frontend API URL to use HTTPS
3. ⬜ Update backend CORS configuration
4. ⬜ Test end-to-end HTTPS flow
5. ⬜ Set up monitoring/alerting for certificate renewal

## References

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Certbot Documentation](https://certbot.eff.org/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

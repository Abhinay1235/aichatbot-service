#!/bin/bash
set -e

DOMAIN="ai-chatbot-service.abhinaykumar.com"
EMAIL="abhinaykumarrao@gmail.com"  # Change this to your email

echo "🔧 Setting up Nginx with SSL for $DOMAIN"
echo "⚠️  Please update the EMAIL variable in this script before running!"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root or with sudo"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
yum update -y

# Install Nginx and Certbot
echo "📦 Installing Nginx and Certbot..."
yum install -y nginx certbot python3-certbot-nginx

# Start and enable Nginx
echo "🚀 Starting Nginx..."
systemctl start nginx
systemctl enable nginx

# Create initial Nginx configuration (HTTP only, for certbot validation)
echo "📝 Creating initial Nginx configuration..."
tee /etc/nginx/conf.d/chatbot-api.conf > /dev/null <<EOF
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

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
if ! nginx -t; then
    echo "❌ Nginx configuration test failed"
    exit 1
fi

# Reload Nginx
systemctl reload nginx

# Obtain SSL certificate
echo "📜 Obtaining SSL certificate from Let's Encrypt..."
if ! certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect; then
    echo "❌ Failed to obtain SSL certificate"
    echo "Please verify:"
    echo "  1. DNS points to this server: dig $DOMAIN"
    echo "  2. Port 80 is open in security group"
    echo "  3. Nginx is accessible from internet: curl http://$DOMAIN"
    exit 1
fi

# Test certificate renewal
echo "🔄 Testing certificate auto-renewal..."
certbot renew --dry-run

echo ""
echo "✅ Nginx SSL setup complete!"
echo ""
echo "Your API is now available at:"
echo "  - HTTP:  http://$DOMAIN (redirects to HTTPS)"
echo "  - HTTPS: https://$DOMAIN"
echo ""
echo "Next steps:"
echo "  1. Update frontend API URL to: https://$DOMAIN"
echo "  2. Update backend CORS configuration"
echo "  3. Test the HTTPS endpoint: curl https://$DOMAIN/health"

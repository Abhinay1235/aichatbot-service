#!/bin/bash
set -e

ENVIRONMENT=${1:-PROD}
AWS_REGION=${2:-us-east-1}
APP_DIR="/opt/chatbot-service"
SERVICE_NAME="chatbot-service"

echo "🚀 Starting deployment for environment: $ENVIRONMENT"
echo "📍 Application directory: $APP_DIR"
echo "🌍 AWS Region: $AWS_REGION"

# Navigate to application directory
cd $APP_DIR

# Install/update Python dependencies
echo "📦 Installing Python dependencies..."
python3.11 -m venv venv || true
source venv/bin/activate

# Set PYTHONPATH before installing to ensure it's available
export PYTHONPATH="$APP_DIR:$PYTHONPATH"

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Verify Python and path
echo "Python location: $(which python)"
echo "PYTHONPATH: $PYTHONPATH"

# Create database directory if it doesn't exist
mkdir -p database

# Check if database exists, if not, load data
if [ ! -f "database/chatbot.db" ]; then
    echo "📊 Database not found, loading data..."
    if [ -f "data/uber_data.csv" ]; then
        # Ensure we're in the right directory and PYTHONPATH is set
        cd $APP_DIR
        export PYTHONPATH="$APP_DIR:$PYTHONPATH"
        # Use venv's python explicitly to ensure correct environment
        $APP_DIR/venv/bin/python scripts/load_data.py data/uber_data.csv
        echo "✅ Database loaded successfully"
    else
        echo "⚠️  Warning: data/uber_data.csv not found. Creating empty database."
        # Create tables only - ensure PYTHONPATH is set
        cd $APP_DIR
        export PYTHONPATH="$APP_DIR:$PYTHONPATH"
        $APP_DIR/venv/bin/python -c "import sys; sys.path.insert(0, '$APP_DIR'); from src.database.session import engine, Base; Base.metadata.create_all(bind=engine)"
        echo "✅ Empty database created"
    fi
else
    echo "✅ Database already exists, skipping data load"
fi

# Create systemd service file
echo "⚙️  Setting up systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=AI Chatbot API Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="PYTHONPATH=$APP_DIR"
Environment="ENVIRONMENT=$ENVIRONMENT"
Environment="AWS_REGION=$AWS_REGION"
EnvironmentFile=-$APP_DIR/.env
# Load OpenAI API key from SSM Parameter Store
Environment="OPENAI_API_KEY=\$(aws ssm get-parameter --name /chatbot/$ENVIRONMENT/OPENAI_API_KEY --with-decryption --region $AWS_REGION --query Parameter.Value --output text 2>/dev/null || echo '')"
ExecStart=$APP_DIR/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and restart service
echo "🔄 Restarting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

# Wait a bit and check status
sleep 5
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service started successfully"
    sudo systemctl status $SERVICE_NAME --no-pager -l | head -20
else
    echo "❌ Service failed to start"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    exit 1
fi

echo "🎉 Deployment complete!"


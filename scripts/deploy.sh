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
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Error: Failed to create virtual environment"
    exit 1
fi
source venv/bin/activate

# Set PYTHONPATH before installing to ensure it's available
export PYTHONPATH="$APP_DIR:$PYTHONPATH"

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Create database directory if it doesn't exist
mkdir -p database

# Check if database exists, if not, create it and optionally load data
if [ ! -f "database/chatbot.db" ]; then
    echo "📊 Database not found, creating database structure..."
    
    # Always create the database structure first (required for service to start)
    export PYTHONPATH="$APP_DIR:$PYTHONPATH"
    if ! $APP_DIR/venv/bin/python -c "import sys; sys.path.insert(0, '$APP_DIR'); from src.database.session import engine, Base; Base.metadata.create_all(bind=engine)"; then
        echo "❌ Error: Failed to create database structure"
        exit 1
    fi
    echo "✅ Database structure created"
    
    # Try to load data if CSV exists (non-fatal - continue deployment even if it fails)
    if [ -f "data/uber_data.csv" ] && [ -f "scripts/load_data.py" ]; then
        echo "Loading data from CSV (this may take a few minutes)..."
        # Use timeout if available, otherwise run directly
        if command -v timeout &> /dev/null; then
            if timeout 600 $APP_DIR/venv/bin/python scripts/load_data.py data/uber_data.csv 2>&1; then
                echo "✅ Database loaded successfully"
            else
                echo "⚠️  Warning: Data loading failed or timed out, but database structure is ready"
                echo "Service will start with empty database. You can load data later if needed"
            fi
        else
            if $APP_DIR/venv/bin/python scripts/load_data.py data/uber_data.csv 2>&1; then
                echo "✅ Database loaded successfully"
            else
                echo "⚠️  Warning: Data loading failed, but database structure is ready"
                echo "Service will start with empty database. You can load data later if needed"
            fi
        fi
    elif [ ! -f "data/uber_data.csv" ]; then
        echo "ℹ️  No data/uber_data.csv found, database is ready but empty"
    fi
else
    echo "✅ Database already exists, skipping data load"
fi

# Create startup script that fetches API key from SSM
echo "📝 Creating startup script..."
sudo tee $APP_DIR/start.sh > /dev/null <<'EOFSCRIPT'
#!/bin/bash
set -e

APP_DIR="/opt/chatbot-service"
ENVIRONMENT="${ENVIRONMENT:-PROD}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Fetch OpenAI API key from SSM Parameter Store
SSM_OUTPUT=$(aws ssm get-parameter \
  --name "/chatbot/$ENVIRONMENT/OPENAI_API_KEY" \
  --with-decryption \
  --region "$AWS_REGION" \
  --query 'Parameter.Value' \
  --output text 2>&1)
SSM_EXIT_CODE=$?

if [ $SSM_EXIT_CODE -ne 0 ] || [ -z "$SSM_OUTPUT" ] || [[ "$SSM_OUTPUT" == *"error"* ]] || [[ "$SSM_OUTPUT" == *"Error"* ]]; then
    echo "❌ Error: Failed to retrieve OPENAI_API_KEY from SSM Parameter Store"
    echo "SSM command output: $SSM_OUTPUT"
    echo "SSM exit code: $SSM_EXIT_CODE"
    exit 1
fi

export OPENAI_API_KEY="$SSM_OUTPUT"

# Start the application
cd $APP_DIR
exec $APP_DIR/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
EOFSCRIPT

sudo chmod +x $APP_DIR/start.sh

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
ExecStart=$APP_DIR/start.sh
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
    echo "=== Service Status ==="
    sudo systemctl status $SERVICE_NAME --no-pager -l
    echo ""
    echo "=== Recent Service Logs ==="
    sudo journalctl -u $SERVICE_NAME -n 50 --no-pager || true
    exit 1
fi

echo "🎉 Deployment complete!"


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
        # Ensure we're in the right directory
        cd $APP_DIR
        
        # Verify the script file exists
        if [ ! -f "scripts/load_data.py" ]; then
            echo "❌ Error: scripts/load_data.py not found!"
            exit 1
        fi
        
        # Use venv's python and explicitly set PYTHONPATH
        # The load_data.py script now uses absolute paths for sys.path modification
        cd $APP_DIR
        export PYTHONPATH="$APP_DIR:$PYTHONPATH"
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

# Create startup script that fetches API key from SSM
echo "📝 Creating startup script..."
sudo tee $APP_DIR/start.sh > /dev/null <<'EOFSCRIPT'
#!/bin/bash
set -e

APP_DIR="/opt/chatbot-service"
ENVIRONMENT="${ENVIRONMENT:-PROD}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Log startup
echo "Starting chatbot service..."
echo "Environment: $ENVIRONMENT"
echo "AWS Region: $AWS_REGION"
echo "App Directory: $APP_DIR"

# Ensure AWS CLI is in PATH and verify it's available
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI not found in PATH"
    echo "PATH: $PATH"
    which aws || echo "aws command not found"
    exit 1
fi
echo "✅ AWS CLI found: $(which aws)"

# Fetch OpenAI API key from SSM Parameter Store
echo "Fetching OpenAI API key from SSM Parameter Store..."
SSM_PARAM_NAME="/chatbot/$ENVIRONMENT/OPENAI_API_KEY"
echo "SSM Parameter: $SSM_PARAM_NAME"

# Try to get the parameter and capture any errors
SSM_OUTPUT=$(aws ssm get-parameter \
  --name "$SSM_PARAM_NAME" \
  --with-decryption \
  --region "$AWS_REGION" \
  --query 'Parameter.Value' \
  --output text 2>&1)
SSM_EXIT_CODE=$?

if [ $SSM_EXIT_CODE -ne 0 ] || [ -z "$SSM_OUTPUT" ] || [ "$SSM_OUTPUT" == "None" ] || [[ "$SSM_OUTPUT" == *"error"* ]] || [[ "$SSM_OUTPUT" == *"Error"* ]]; then
    echo "❌ Error: Failed to retrieve OPENAI_API_KEY from SSM Parameter Store"
    echo "SSM command output: $SSM_OUTPUT"
    echo "SSM exit code: $SSM_EXIT_CODE"
    echo "Checking IAM permissions..."
    aws sts get-caller-identity 2>&1 || echo "Failed to get caller identity"
    echo "Testing SSM list-parameters..."
    aws ssm describe-parameters --region "$AWS_REGION" --query 'Parameters[?contains(Name, `chatbot`)].Name' --output text 2>&1 || echo "Failed to list parameters"
    exit 1
fi

export OPENAI_API_KEY="$SSM_OUTPUT"
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY is empty after retrieval"
    exit 1
fi

echo "✅ Successfully retrieved API key from SSM"

# Verify Python and uvicorn are available
if [ ! -f "$APP_DIR/venv/bin/uvicorn" ]; then
    echo "❌ Error: uvicorn not found at $APP_DIR/venv/bin/uvicorn"
    exit 1
fi

# Start the application
echo "Starting uvicorn server..."
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
echo "Waiting for service to start..."
sleep 10

# Check service status
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service started successfully"
    sudo systemctl status $SERVICE_NAME --no-pager -l | head -20
else
    echo "❌ Service failed to start"
    echo ""
    echo "=== Service Status ==="
    sudo systemctl status $SERVICE_NAME --no-pager -l || true
    echo ""
    echo "=== Recent Service Logs (stdout) ==="
    sudo journalctl -u $SERVICE_NAME -n 100 --no-pager --output=cat || true
    echo ""
    echo "=== Testing startup script manually ==="
    echo "Running: sudo -u ec2-user bash -x $APP_DIR/start.sh"
    sudo -u ec2-user env ENVIRONMENT=$ENVIRONMENT AWS_REGION=$AWS_REGION bash -x $APP_DIR/start.sh 2>&1 || true
    echo ""
    echo "=== Checking startup script permissions ==="
    ls -la $APP_DIR/start.sh || true
    echo ""
    echo "=== Checking if AWS CLI is available ==="
    which aws || echo "AWS CLI not found in PATH"
    aws --version || echo "AWS CLI version check failed"
    echo ""
    echo "=== Testing SSM access ==="
    sudo -u ec2-user aws ssm get-parameter --name /chatbot/$ENVIRONMENT/OPENAI_API_KEY --with-decryption --region $AWS_REGION --query 'Parameter.Value' --output text 2>&1 | head -c 20 || echo "SSM access failed"
    exit 1
fi

echo "🎉 Deployment complete!"


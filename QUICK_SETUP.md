# Quick Setup Checklist for Phase 3

## ✅ Pre-Phase 3 Setup Steps

### 1. Create Virtual Environment (Recommended)
```bash
# Create a virtual environment named 'venv' to isolate project dependencies
python3 -m venv venv

# Activate the virtual environment (macOS/Linux)
# This ensures all packages are installed in this project's environment
source venv/bin/activate

# On Windows, use this instead:
# venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Install all Python packages listed in requirements.txt
# This includes FastAPI, SQLAlchemy, OpenAI, pandas, etc.
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (web framework)
- SQLAlchemy (database ORM)
- Pandas & NumPy (data processing)
- OpenAI (for LLM integration)
- Pydantic (data validation)
- python-dotenv (environment variables)

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
# Create .env file with all configuration variables
# This file stores sensitive data like API keys (not committed to git)
cat > .env << EOF
# Your OpenAI API key - get it from https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Which OpenAI model to use (gpt-3.5-turbo is cost-efficient)
OPENAI_MODEL=gpt-3.5-turbo

# SQLite database file location
DATABASE_URL=sqlite:///./database/chatbot.db

# Application name
APP_NAME=AI Chatbot Service

# Enable debug mode for development
DEBUG=True

# Logging level (INFO shows normal operations)
LOG_LEVEL=INFO

# Maximum conversation history to keep in context
MAX_CONTEXT_MESSAGES=10

# Maximum tokens per LLM response
MAX_TOKENS=500
EOF
```

**Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key!

### 4. Load CSV Data into Database
```bash
# Create the database directory if it doesn't exist
# The -p flag creates parent directories if needed and doesn't error if it exists
mkdir -p database

# Run the data loading script to:
# - Create database tables (uber_trips, sessions, messages)
# - Parse and load all 103,026 rows from the CSV file
# - Create database indexes for fast queries
# This may take 2-5 minutes depending on your system
python scripts/load_data.py data/uber_data.csv
```

This will:
- Create the database tables
- Load all 103,026 rows from the CSV
- Create indexes for fast queries

**Note:** This may take a few minutes depending on your system.

### 5. Verify Setup
```bash
# Test the SQL service to verify:
# - Database connection works
# - Schema information can be retrieved
# - SQL queries can be executed safely
# - SQL validation blocks dangerous queries
python scripts/test_sql_service.py

# Start the FastAPI web server
# --reload enables auto-reload on code changes (development mode)
uvicorn src.main:app --reload

# After starting, visit these URLs in your browser:
# - API Documentation: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
# - Root endpoint: http://localhost:8000
```

## ✅ Ready for Phase 3?

Once you've completed all steps above, you're ready to proceed with Phase 3 (OpenAI Integration)!

## Troubleshooting

**If pip install fails:**
```bash
# Make sure you're in the virtual environment (you should see (venv) in your prompt)
# Upgrade pip to the latest version first
pip install --upgrade pip

# Check Python version (should be 3.9 or higher)
python3 --version
```

**If database loading fails:**
```bash
# Verify the CSV file exists in the data directory
ls data/uber_data.csv

# Check you have write permissions in the project directory
# If not, you may need to fix permissions or run with appropriate access
```

**If OpenAI API key issues:**
```bash
# Get your API key from: https://platform.openai.com/api-keys
# Verify the .env file exists and contains the key
cat .env | grep OPENAI_API_KEY

# Make sure there are no extra spaces around the key
# The format should be: OPENAI_API_KEY=sk-...
```


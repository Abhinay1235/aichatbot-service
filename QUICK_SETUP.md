# Quick Setup Guide

This guide will help you quickly set up and run the AI Chatbot Service locally.

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (get it from https://platform.openai.com/api-keys)
- Car Rides data in CSV format (included in `data/` directory)

## Quick Start

### 1. Create Virtual Environment

```bash
# Create a virtual environment to isolate project dependencies
python3 -m venv venv

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (web framework)
- SQLAlchemy (database ORM)
- Pandas & NumPy (data processing)
- OpenAI (for LLM integration)
- Pydantic (data validation)
- python-dotenv (environment variables)

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Quick method - create minimal .env file
echo "OPENAI_API_KEY=your_key_here" > .env
echo "OPENAI_MODEL=gpt-3.5-turbo" >> .env
echo "DATABASE_URL=sqlite:///./database/chatbot.db" >> .env
```

**Or create manually** with these settings:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./database/chatbot.db
```

**Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key from https://platform.openai.com/api-keys

### 4. Load CSV Data into Database

```bash
# Create the database directory if it doesn't exist
mkdir -p database

# Load data from CSV (this may take 2-5 minutes)
python scripts/load_data.py data/uber_data.csv
```

This will:
- Create the database tables
- Load all rows from the CSV
- Create indexes for fast queries

### 5. Start the API Server

```bash
# Start the FastAPI server with auto-reload (development mode)
uvicorn src.main:app --reload
```

### 6. Access the API

Once the server is running, you can access:

- **Swagger UI (Interactive API Docs):** http://localhost:8000/docs
- **ReDoc (Alternative Docs):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **Root Endpoint:** http://localhost:8000

### 7. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Send a chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many trips are there?"}'
```

## API Endpoints

- `POST /api/chat` - Send a message to the chatbot
- `GET /api/sessions` - List all sessions (with optional `?limit=100` query param)
- `GET /api/sessions/{session_id}` - Get conversation history for a session
- `DELETE /api/sessions/{session_id}` - Delete a session
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API information

## ✅ Setup Complete!

You're now ready to use the AI Chatbot Service locally!

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


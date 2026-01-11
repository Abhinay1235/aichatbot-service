# AI Chatbot Service

AI-powered chatbot backend service for analyzing Uber trip data. Built with FastAPI, SQLite, and OpenAI GPT-3.5-turbo.

## Overview

This service provides:
- **Natural language queries** to analyze car rides data for a particular period
- **Conversation context persistence** - remembers previous questions in a session
- **Cost-efficient architecture** - SQLite database, GPT-3.5-turbo model
- **RESTful API** for chatbot interactions

## Features

- 📊 Analyze Car rides data through natural language questions
- 💬 Maintain conversation context across multiple questions
- 💰 Cost-optimized (SQLite + GPT-3.5-turbo)
- 🚀 Fast API built with FastAPI
- 📝 Auto-generated API documentation (Swagger UI)

## Getting Started

For detailed setup instructions, see [QUICK_SETUP.md](QUICK_SETUP.md).

**Quick Start:**
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
echo "OPENAI_MODEL=gpt-3.5-turbo" >> .env
echo "DATABASE_URL=sqlite:///./database/chatbot.db" >> .env

# 4. Load data into database
python scripts/load_data.py data/uber_data.csv

# 5. Start the server
uvicorn src.main:app --reload
```

The API will be available at:
- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## Prerequisites

- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Car Rides data in CSV format (included in `data/` directory)

## Project Structure

```
aichatbot-service/
├── src/                    # Source code
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration
│   ├── database/           # Database models and session
│   ├── services/           # Business logic
│   ├── api/                # API routes
│   └── utils/              # Utilities
├── scripts/                # Utility scripts
│   ├── load_data.py        # Data loading script
│   └── test_*.py           # Test scripts
├── data/                   # CSV data files
├── database/               # SQLite database (created automatically)
└── tests/                  # Test files
```

## API Endpoints

- `POST /api/chat` - Send a message to the chatbot
- `GET /api/sessions` - List all sessions (with optional `?limit=100` query param)
- `GET /api/sessions/{session_id}` - Get conversation history for a session
- `DELETE /api/sessions/{session_id}` - Delete a session
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API information

**Example API Usage:**
```bash
# Health check
curl http://localhost:8000/health

# Send a chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many trips are there?"}'
```

For more examples, see [API_EXAMPLES.md](API_EXAMPLES.md).

## Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./database/chatbot.db
APP_NAME=AI Chatbot Service
DEBUG=True
```

## Technology Stack

- **Framework:** FastAPI
- **Database:** SQLite
- **AI/LLM:** OpenAI GPT-3.5-turbo
- **Data Processing:** pandas, numpy
- **ORM:** SQLAlchemy
- **Server:** Uvicorn (ASGI)

## Data Source & Credits

The Car Rides data used in this project is sourced from a public dataset on Kaggle:

**Dataset:** [Ola and Uber Ride Booking and Cancellation Data](https://www.kaggle.com/datasets/hetmengar/ola-and-uber-ride-booking-and-cancellation-data)

This dataset contains ride booking and cancellation data for dates from July 01, 2024 to July 31, 2024, used for demonstration and analysis purposes in this portfolio project.

## Additional Resources

- **[QUICK_SETUP.md](QUICK_SETUP.md)** - Quick setup guide for local development
- **[SETUP.md](SETUP.md)** - Comprehensive local development setup
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - API usage examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture documentation
- **[DATA_SCHEMA.md](DATA_SCHEMA.md)** - Database schema documentation
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Development roadmap

## Development

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the complete development plan.

## License

Personal portfolio project.

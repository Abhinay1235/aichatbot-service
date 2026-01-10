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

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Car Rides data in CSV format

### Installation

See [SETUP.md](SETUP.md) for detailed setup instructions.

Quick start:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Run the application
uvicorn src.main:app --reload
```

### Configuration

Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./database/chatbot.db
```

## Project Structure

```
aichatbot-service/
├── src/              # Source code
│   ├── main.py       # FastAPI application
│   ├── config.py     # Configuration
│   ├── database/     # Database models and session
│   ├── services/     # Business logic
│   ├── api/          # API routes
│   └── utils/        # Utilities
├── data/             # CSV data files
├── database/         # SQLite database (created automatically)
├── scripts/          # Utility scripts
└── tests/            # Test files
```

## Usage

1. **Load your Uber CSV data**:
   ```bash
   python scripts/load_data.py data/uber_data.csv
   ```

2. **Start the API server**:
   ```bash
   uvicorn src.main:app --reload
   ```

3. **Access API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

4. **API Endpoints** (to be implemented):
   - `POST /api/chat` - Send a message to the chatbot
   - `GET /api/sessions` - List all sessions
   - `GET /api/sessions/{session_id}` - Get conversation history

## Development

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the complete development plan.

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite
- **AI/LLM**: OpenAI GPT-3.5-turbo
- **Data Processing**: pandas, numpy
- **ORM**: SQLAlchemy

## Cost Optimization

- SQLite (free, file-based database)
- GPT-3.5-turbo (~$0.0015/1K tokens vs GPT-4's ~$0.03/1K tokens)
- Context window limiting
- Query caching

Estimated monthly cost: ~$5-20 for a portfolio project.

## Data Source & Credits

The Car Rides data used in this project is sourced from a public dataset on Kaggle:

**Dataset**: [Ola and Uber Ride Booking and Cancellation Data](https://www.kaggle.com/datasets/hetmengar/ola-and-uber-ride-booking-and-cancellation-data)

This dataset contains ride booking and cancellation data that is used for demonstration and analysis purposes in this portfolio project.

## License

Personal portfolio project.


# AI Chatbot Service - Project Plan

## Recommended Technology Stack

**Primary Language: Python**
- Excellent for data analysis (pandas, numpy)
- Strong OpenAI SDK support
- Easy CSV handling
- Great ecosystem for AI/ML projects
- Fast API framework for modern async APIs

**Key Technologies:**
- **Framework**: FastAPI (modern, fast, async Python web framework) - Free & Open Source
- **Database**: SQLite (file-based, zero cost, perfect for portfolio projects)
- **Data Processing**: pandas, numpy (free libraries)
- **AI/LLM**: OpenAI API (GPT-3.5-turbo recommended for cost efficiency, ~$0.0015/1K tokens)
- **Context Management**: SQLite-backed session storage

---

## Step-by-Step Implementation Plan

### Phase 1: Project Setup & Data Ingestion
1. **Initialize Python project**
   - Set up virtual environment
   - Create `requirements.txt` with dependencies (FastAPI, pandas, openai, sqlalchemy, etc.)
   - Set up project structure (src/, data/, tests/)

2. **CSV Data Analysis & Schema Design**
   - Load and examine the Uber CSV data structure
   - Identify key columns and data types
   - Design database schema to store Uber data efficiently
   - Plan query patterns (what questions users might ask)

3. **Data Loading Pipeline**
   - Create script to parse CSV file
   - Transform and clean data if needed
   - Load data into SQLite database
   - Create indexes for common query patterns

### Phase 2: Database & Data Access Layer
4. **Database Setup**
   - Set up SQLite database connection
   - Create database models using SQLAlchemy ORM
   - Create tables for Uber data
   - Create tables for conversation history/context
   - Set up database migrations (Alembic) - optional for simple projects

5. **Data Access Layer**
   - Create SQL service for safe execution of LLM-generated queries
   - Implement SQL validation and security checks
   - Add schema information retrieval for LLM context
   - Add error handling for query execution

### Phase 3: OpenAI Integration & Query Processing
6. **OpenAI Integration**
   - Set up OpenAI client with API key management
   - Create environment variable configuration
   - Implement basic chat completion function

7. **Natural Language to Query Conversion**
   - Design prompt engineering strategy
   - Create function to convert user questions to SQL queries or data operations
   - Implement query execution and result formatting
   - Add error handling for invalid queries

8. **Response Generation**
   - Format database results into natural language responses
   - Use OpenAI to generate human-readable summaries
   - Handle edge cases (no results, errors, etc.)

### Phase 4: Context Management
9. **Session Management**
   - Design session/conversation tracking system
   - Create database tables for storing conversation history
   - Implement session creation and retrieval

10. **Context Persistence**
    - Store conversation messages (user questions + bot responses)
    - Implement context window management (limit conversation history)
    - Add context retrieval for maintaining conversation flow
    - Pass conversation history to OpenAI API

### Phase 5: API Development
11. **FastAPI Application Setup**
    - Initialize FastAPI app
    - Set up CORS, middleware, error handling
    - Create health check endpoint

12. **Chatbot API Endpoints**
    - `POST /api/chat` - Main chat endpoint (send message, get response)
    - `GET /api/sessions` - List all sessions
    - `GET /api/sessions/{session_id}` - Get conversation history
    - `POST /api/sessions` - Create new session
    - `DELETE /api/sessions/{session_id}` - Delete session

13. **Request/Response Models**
    - Define Pydantic models for requests/responses
    - Add input validation
    - Create response schemas

### Phase 6: Advanced Features
14. **Query Optimization**
    - Add caching for frequent queries
    - Optimize database queries
    - Add query result limits and pagination

15. **Error Handling & Logging**
    - Implement comprehensive error handling
    - Add logging for debugging and monitoring
    - Create user-friendly error messages

16. **Testing**
    - Write unit tests for data access layer
    - Write integration tests for API endpoints
    - Test OpenAI integration (with mocks)
    - Test context persistence

### Phase 7: Documentation & Deployment
17. **Documentation**
    - Update README with setup instructions
    - Document API endpoints (FastAPI auto-generates Swagger docs)
    - Add code comments and docstrings
    - Document environment variables

18. **Deployment Preparation**
    - Create Dockerfile (optional, for containerized deployment)
    - Set up environment configuration
    - Add deployment scripts (for free hosting like Railway, Render, or Fly.io)

---

## Database Location & Configuration

### SQLite (File-Based Database) - Cost-Efficient Choice
- **Location**: `database/chatbot.db` (file-based database in project directory)
- **Type**: Single file database (no separate server needed)
- **Configuration**: Database path specified in `.env` file or config
- **Advantages**: 
  - ✅ **Zero cost** - No database hosting fees
  - ✅ No setup required - Works out of the box
  - ✅ Easy to backup (just copy the file)
  - ✅ Perfect for portfolio projects
  - ✅ Can handle large datasets efficiently
  - ✅ No server maintenance needed

### Database Files Created
1. **Uber Data Tables**: Stores the imported CSV data
2. **Conversation History Tables**: Stores chat sessions and messages
   - `sessions` table: Session metadata
   - `messages` table: Individual messages in conversations

**Note**: SQLite is production-ready for portfolio projects and can handle substantial data volumes. Only consider PostgreSQL if you need concurrent writes from multiple applications.

---

## Project Structure (Recommended)

```
aichatbot-service/
├── .env                    # Environment variables
├── .gitignore
├── README.md
├── requirements.txt
├── Dockerfile              # Optional: for containerized deployment
├── database/               # Database files (SQLite)
│   ├── chatbot.db         # SQLite database file (created automatically)
│   └── migrations/        # Alembic migration files
├── src/
│   ├── __init__.py
│   ├── main.py            # FastAPI app entry point
│   ├── config.py          # Configuration management
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── session.py     # Database session
│   │   └── migrations/    # Alembic migrations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── sql_service.py      # Safe SQL query execution
│   │   ├── openai_service.py  # OpenAI integration
│   │   └── chat_service.py    # Main chat logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py    # Chat endpoints
│   │   │   └── sessions.py # Session endpoints
│   │   └── models.py      # Pydantic models
│   └── utils/
│       ├── __init__.py
│       └── csv_loader.py  # CSV data loading
├── data/
│   └── uber_data.csv      # Your CSV file
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_services.py
│   └── test_data.py
└── scripts/
    └── load_data.py       # Data loading script
```

---

## Cost Optimization Strategies

### OpenAI API Cost Management
1. **Use GPT-3.5-turbo** instead of GPT-4 (10x cheaper: ~$0.0015/1K tokens vs ~$0.03/1K tokens)
2. **Limit context window**: Keep conversation history to last 5-10 messages
3. **Cache common queries**: Store frequently asked questions and their answers
4. **Set token limits**: Limit max tokens per response
5. **Monitor usage**: Track API calls and costs
6. **Use streaming**: For better UX without extra cost

### Infrastructure Costs
- ✅ **SQLite**: Free (file-based, no hosting needed)
- ✅ **FastAPI**: Free (open source)
- ✅ **Free hosting options**: 
  - Railway.app (free tier available)
  - Render.com (free tier)
  - Fly.io (generous free tier)
  - PythonAnywhere (free tier)

### Total Estimated Monthly Cost
- **Database**: $0 (SQLite)
- **Hosting**: $0 (free tier)
- **OpenAI API**: ~$5-20/month (depending on usage, with GPT-3.5-turbo)
- **Total**: ~$5-20/month for a portfolio project

## Key Considerations

1. **Data Privacy**: Ensure sensitive data in CSV is handled securely
2. **Rate Limiting**: Implement rate limiting for OpenAI API calls to control costs
3. **Cost Management**: Monitor OpenAI API usage and set daily/monthly limits
4. **Security**: Secure API keys, validate inputs, sanitize queries
5. **Portfolio Focus**: Optimize for demonstration rather than high-scale production

---

## Next Steps

Once you approve this plan, we can start with Phase 1 and begin implementing step by step.


# System Architecture

## Overview

This is an AI-powered chatbot backend service that analyzes Uber trip data using natural language queries. The system uses OpenAI GPT-3.5-turbo to convert user questions into SQL queries, executes them safely, and generates natural language responses.

## Architecture Decision: Query Approach

### The Question
Do we need predefined query functions when the LLM can generate SQL directly?

### Answer: LLM-Generated SQL Approach

We use **LLM-generated SQL** as the primary method, with strict validation for security.

**Benefits:**
1. ✅ **Flexibility** - Can answer any question without writing functions
2. ✅ **Less Code** - No need for 30+ query functions
3. ✅ **Cost Efficient** - LLM just generates SQL (fewer tokens)
4. ✅ **Security** - Safe with query validation
5. ✅ **Portfolio Friendly** - Shows LLM integration skills

## System Components

### 1. Database Layer (`src/database/`)

**SQLite Database:**
- `uber_trips` table - Stores 103,024 Uber trip records
- `sessions` table - Stores chat session metadata
- `messages` table - Stores conversation history

**Models:**
- `UberTrip` - Trip data with indexes for common queries
- `Session` - Session tracking with timestamps
- `Message` - Individual messages (user/assistant)

### 2. Service Layer (`src/services/`)

#### SQL Service (`sql_service.py`)
- `get_schema_info()` - Returns database schema for LLM context
- `execute_query(sql)` - Safely executes and validates SQL queries
- `validate_sql()` - Security checks (SELECT only, no dangerous operations)
- `format_results_for_llm()` - Formats query results for LLM processing

**Security Features:**
- Only SELECT queries allowed
- Blocks: DROP, DELETE, UPDATE, INSERT, ALTER, etc.
- Prevents SQL injection
- Limits result sets (default: 1000 rows)

#### OpenAI Service (`openai_service.py`)
- `generate_sql_query()` - Converts natural language to SQL
  - Receives: user question + schema info + conversation history
  - Returns: Valid SQL query string
- `generate_response()` - Formats query results into natural language
  - Receives: user question + query results + conversation history
  - Returns: Human-readable response

**Prompt Engineering:**
- System prompts include database schema
- Example queries for guidance
- Context-aware (uses conversation history)

#### Chat Service (`chat_service.py`)
- Orchestrates the complete flow:
  1. Get/create session
  2. Retrieve conversation history
  3. Generate SQL query
  4. Execute query
  5. Generate response
  6. Store messages in session

#### Session Service (`session_service.py`)
- `create_session()` - Creates new chat sessions
- `add_message()` - Stores user/assistant messages
- `get_conversation_history()` - Retrieves full conversation
- `get_recent_conversation_history()` - Gets last N messages (context window)
- `delete_session()` - Removes session and messages

**Context Management:**
- Limits conversation history to last N messages (configurable, default: 10)
- Maintains conversation continuity across requests
- Automatic session creation

### 3. API Layer (`src/api/`)

#### Routes

**Chat Endpoint** (`routes/chat.py`):
- `POST /api/chat` - Send message, get response
  - Accepts: `message`, optional `session_id`, optional `conversation_history`
  - Returns: `response`, `session_id`, `sql_query`, `query_results`

**Session Endpoints** (`routes/sessions.py`):
- `POST /api/sessions` - Create new session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{session_id}` - Get conversation history
- `DELETE /api/sessions/{session_id}` - Delete session

#### Models (`models.py`)
- `ChatRequest` - Request model for chat endpoint
- `ChatResponse` - Response model with session_id
- `SessionResponse` - Session information
- `ConversationResponse` - Full conversation history
- `MessageResponse` - Individual message

### 4. Configuration (`src/config.py`)

**Environment Variables:**
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL` - Model to use (default: gpt-3.5-turbo)
- `DATABASE_URL` - SQLite database path
- `MAX_CONTEXT_MESSAGES` - Conversation history limit (default: 10)
- `MAX_TOKENS` - Max tokens per response (default: 500)

## Complete Request Flow

```
1. User sends message
   POST /api/chat
   {
     "message": "How many total trips are there?",
     "session_id": "optional-session-id"
   }

2. Chat Service receives request
   ├─ Get or create session
   ├─ Retrieve conversation history (if session_id provided)
   └─ Process message

3. SQL Generation
   ├─ OpenAI Service receives:
   │  ├─ User question
   │  ├─ Database schema (columns, types, sample values)
   │  └─ Conversation history (last N messages)
   └─ LLM generates SQL:
      SELECT COUNT(*) FROM uber_trips LIMIT 1000

4. SQL Validation & Execution
   ├─ SQL Service validates query
   │  ├─ Must start with SELECT
   │  ├─ No forbidden keywords
   │  └─ Must reference uber_trips table
   ├─ Execute query safely
   └─ Get results: [{"COUNT(*)": 103024}]

5. Response Generation
   ├─ OpenAI Service receives:
   │  ├─ User question
   │  ├─ Query results
   │  └─ Conversation history
   └─ LLM generates response:
      "There are a total of 103,024 trips in the Uber trip data."

6. Session Storage
   ├─ Store user message in session
   └─ Store assistant response in session

7. Return Response
   {
     "success": true,
     "response": "There are a total of 103,024 trips...",
     "session_id": "uuid-here",
     "sql_query": "SELECT COUNT(*) FROM uber_trips...",
     "query_results": {
       "row_count": 1,
       "columns": ["COUNT(*)"]
     }
   }
```

## Database Schema

### uber_trips Table
- 21 columns including: date, booking_status, vehicle_type, pickup_location, drop_location, booking_value, payment_method, ride_distance, ratings, etc.
- Indexes on: date, booking_status, vehicle_type, customer_id, locations, booking_value, ride_distance
- Composite indexes for common query patterns

### sessions Table
- `id` - Primary key
- `session_id` - Unique UUID identifier
- `created_at` - Session creation timestamp
- `updated_at` - Last message timestamp

### messages Table
- `id` - Primary key
- `session_id` - Foreign key to sessions
- `role` - 'user' or 'assistant'
- `content` - Message text
- `created_at` - Message timestamp

## Security Features

1. **SQL Injection Prevention:**
   - Only SELECT queries allowed
   - Forbidden keywords blocked (DROP, DELETE, UPDATE, etc.)
   - Query validation before execution
   - No multiple statements

2. **Input Validation:**
   - Pydantic models for request validation
   - Type checking and constraints

3. **Error Handling:**
   - Graceful error messages
   - No sensitive data in error responses
   - Logging for debugging

## Technology Stack

- **Framework**: FastAPI (async Python web framework)
- **Database**: SQLite (file-based, zero cost)
- **ORM**: SQLAlchemy 2.0
- **AI/LLM**: OpenAI GPT-3.5-turbo
- **Data Processing**: pandas, numpy
- **Validation**: Pydantic 2.x

## Cost Optimization

- **Database**: SQLite (free)
- **LLM**: GPT-3.5-turbo (~$0.0015/1K tokens vs GPT-4's ~$0.03/1K tokens)
- **Context Management**: Limits conversation history to reduce token usage
- **Query Optimization**: Indexes for fast queries

**Estimated Monthly Cost**: ~$5-20 for a portfolio project

## Example Interactions

### Question 1: "How many total trips are there?"
- SQL: `SELECT COUNT(*) FROM uber_trips LIMIT 1000`
- Response: "There are a total of 103,024 trips in the Uber trip data."

### Question 2: "What is the average booking value?"
- SQL: `SELECT AVG(booking_value) FROM uber_trips WHERE booking_value IS NOT NULL`
- Response: "The average booking value is ₹548.75."

### Question 3: "How many successful rides were there?"
- SQL: `SELECT COUNT(*) FROM uber_trips WHERE booking_status = 'Success'`
- Response: "There were a total of 63,967 successful rides."

## Future Enhancements

- Query caching for frequent questions
- Rate limiting for API endpoints
- Analytics and usage tracking
- Support for multiple data sources
- Advanced query optimization

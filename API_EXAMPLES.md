# API Testing Examples

## Chat Endpoint

### Basic Request
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many total trips are there?"
  }'
```

### With Conversation History
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the average booking value for Prime SUV?",
    "session_id": "session-123",
    "conversation_history": [
      {
        "role": "user",
        "content": "How many successful rides were there?"
      },
      {
        "role": "assistant",
        "content": "There were a total of 63,967 successful rides."
      }
    ]
  }'
```

## Example Questions to Test

### 1. Total Trips
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many total trips are there?"}'
```

### 2. Average Booking Value
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the average booking value?"}'
```

### 3. Successful Rides
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many successful rides were there?"}'
```

### 4. Revenue by Vehicle Type
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the total revenue by vehicle type?"}'
```

### 5. Top Pickup Locations
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the top 5 pickup locations?"}'
```

### 6. Cancellation Rate
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What percentage of rides were canceled?"}'
```

### 7. Average Distance
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the average ride distance?"}'
```

### 8. Payment Method Analysis
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How much revenue came from UPI payments?"}'
```

## Expected Response Format

```json
{
  "success": true,
  "response": "There are a total of 103,024 trips in the Uber trip data.",
  "sql_query": "SELECT COUNT(*) FROM uber_trips LIMIT 1000",
  "query_results": {
    "row_count": 1,
    "columns": ["COUNT(*)"]
  },
  "error": null
}
```

## Error Response Format

```json
{
  "success": false,
  "response": "I encountered an error processing your query...",
  "sql_query": null,
  "query_results": null,
  "error": "Error message here"
}
```

## Postman Setup

1. **Method**: POST
2. **URL**: `http://localhost:8000/api/chat`
3. **Headers**:
   - `Content-Type: application/json`
4. **Body** (raw JSON):
   ```json
   {
     "message": "How many total trips are there?"
   }
   ```

## Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc


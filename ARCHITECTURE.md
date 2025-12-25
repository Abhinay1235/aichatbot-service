# Architecture Decision: Query Approach

## The Question
Do we need predefined query functions when the LLM can generate SQL directly?

## Answer: Hybrid Approach

We'll use **LLM-generated SQL** as the primary method, with a few helper functions for safety and common operations.

## Architecture

### Primary Method: LLM-Generated SQL
- LLM receives user question + database schema
- LLM generates SQL query
- We execute the query with **strict validation**:
  - Only SELECT queries allowed
  - No DROP, DELETE, UPDATE, INSERT
  - Whitelist of allowed SQL keywords
  - Query timeout limits

### Helper Functions (Simplified)
Keep only essential functions:
- `get_database_schema()` - Returns table structure for LLM
- `execute_safe_query(sql)` - Executes validated SQL
- `format_query_results(results)` - Formats results for LLM

### Why This Approach?

**Benefits:**
1. ✅ **Flexibility** - Can answer any question without writing functions
2. ✅ **Less Code** - No need for 30+ query functions
3. ✅ **Cost Efficient** - LLM just generates SQL (fewer tokens)
4. ✅ **Security** - Still safe with query validation
5. ✅ **Portfolio Friendly** - Shows LLM integration skills

**Trade-offs:**
- Need robust SQL validation
- LLM might occasionally generate incorrect SQL (but we can retry/refine)

## Implementation Plan

1. **SQL Generation Service**
   - Prompt LLM with: user question + schema + example queries
   - LLM generates SQL
   - Validate SQL (whitelist approach)
   - Execute query
   - Format results back to LLM for natural language response

2. **Minimal Helper Functions**
   - Schema retrieval
   - Safe query execution
   - Result formatting

3. **Error Handling**
   - If SQL fails, ask LLM to refine it
   - Fallback to simpler queries
   - User-friendly error messages

## Example Flow

```
User: "What's the average booking value for Prime SUV?"

1. LLM receives:
   - Question: "What's the average booking value for Prime SUV?"
   - Schema: uber_trips table structure
   - Context: Previous conversation (if any)

2. LLM generates SQL:
   SELECT AVG(booking_value) 
   FROM uber_trips 
   WHERE vehicle_type = 'Prime SUV' 
   AND booking_status = 'Success'

3. We validate SQL (check for SELECT only, no dangerous operations)

4. Execute query → Get result: 450.25

5. LLM formats response:
   "The average booking value for Prime SUV rides is ₹450.25"
```

## Conclusion

**We'll simplify the data service** to focus on:
- Schema information
- Safe SQL execution
- Result formatting

The LLM will handle query generation, making the system more flexible and requiring less code.


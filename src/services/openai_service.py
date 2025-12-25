"""OpenAI service for LLM integration."""

from typing import List, Dict, Any, Optional
from openai import OpenAI
import logging

from src.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def generate_sql_query(
        self,
        user_question: str,
        schema_info: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate SQL query from natural language question.
        
        Args:
            user_question: User's natural language question
            schema_info: Database schema information
            conversation_history: Previous conversation messages for context
        
        Returns:
            SQL query string
        """
        # Build system prompt with dynamic context resolution
        system_prompt = f"""You are a SQL query generator for analyzing Uber trip data.

Database Schema:
Table: {schema_info['table_name']}
Total Rows: {schema_info['total_rows']:,}

Available Columns (use these for filtering):
"""
        for col in schema_info['columns']:
            system_prompt += f"  - {col['name']}: {col['type']} {'(nullable)' if col['nullable'] else '(required)'}\n"
        
        system_prompt += f"""
Sample Values:
- Booking Status: {', '.join(schema_info['sample_values']['booking_status'])}
- Vehicle Types: {', '.join(schema_info['sample_values']['vehicle_type'])}
- Payment Methods: {', '.join(schema_info['sample_values']['payment_method'])}

CRITICAL: Dynamic Context Resolution from Conversation History
===============================================================
When generating SQL queries, you MUST:

1. **Review ALL conversation history** to understand context and references:
   - If user says "them", "those", "it", "that" - find what it refers to in previous messages
   - Look at previous user questions and assistant responses to understand what filters were applied
   - Extract any column filters (vehicle_type, booking_status, date ranges, locations, etc.) from previous queries

2. **Extract filters dynamically** from conversation history:
   - Scan previous messages for any column values mentioned (vehicle types, locations, statuses, dates, etc.)
   - If a previous query filtered by a column, and current question references "them/those/it", apply the same filter
   - Combine ALL relevant filters from conversation history with the current question's requirements
   - Work with ANY column from the schema above - don't limit to specific columns

3. **Apply context to current query**:
   - If previous message was about "Prime SUV trips" and current question asks "how many of them on weekends"
   - Generate: SELECT COUNT(*) FROM uber_trips WHERE vehicle_type = 'Prime SUV' AND strftime('%w', date) IN ('0', '6')
   - The LLM should automatically know SQLite date functions for weekend detection, date comparisons, etc.

4. **Work with ANY schema column**:
   - Don't limit yourself to specific columns - use any column from the schema above
   - Extract filters for pickup_location, drop_location, customer_id, payment_method, booking_value, ride_distance, etc. if mentioned in history
   - Apply date filters, value ranges, or any other column-based filters from context

5. **Combine multiple context filters**:
   - If conversation mentions multiple filters (vehicle_type AND date AND location), combine them all
   - Use AND to connect filters from context with filters from current question
   - Use OR when appropriate (e.g., pickup_location OR drop_location)

Example Context Resolution:
---------------------------
Previous: "How many Prime SUV trips got booked"
Current: "out of them how many are booked on weekends?"
→ Extract: vehicle_type = 'Prime SUV' from previous
→ Apply: Combine with weekend filter
→ SQL: SELECT COUNT(*) FROM uber_trips WHERE vehicle_type = 'Prime SUV' AND strftime('%w', date) IN ('0', '6')

Previous: "Show me trips from Airport location"
Current: "how many of those were successful?"
→ Extract: pickup_location = 'Airport' OR drop_location = 'Airport' from previous
→ Apply: Combine with booking_status = 'Success'
→ SQL: SELECT COUNT(*) FROM uber_trips WHERE (pickup_location = 'Airport' OR drop_location = 'Airport') AND booking_status = 'Success'

SQL Generation Rules:
---------------------
1. Generate ONLY valid SQL SELECT queries
2. Use the table name 'uber_trips' (not {schema_info['table_name']})
3. For date comparisons, use the 'date' column (DateTime type)
4. Always use proper SQL syntax
5. Return ONLY the SQL query, no explanations or markdown
6. Use LIMIT if the query might return many rows (default: 100)
7. For aggregations, use appropriate functions (COUNT, SUM, AVG, etc.)
8. When combining multiple filters, use AND/OR appropriately

Example queries (without context):
- "How many successful rides?" → SELECT COUNT(*) FROM uber_trips WHERE booking_status = 'Success'
- "Average booking value for Prime SUV" → SELECT AVG(booking_value) FROM uber_trips WHERE vehicle_type = 'Prime SUV' AND booking_status = 'Success' AND booking_value IS NOT NULL
- "Top 5 pickup locations" → SELECT pickup_location, COUNT(*) as count FROM uber_trips WHERE pickup_location IS NOT NULL GROUP BY pickup_location ORDER BY count DESC LIMIT 5
"""
        
        # Build user message with explicit context instruction
        user_message = f"Generate a SQL query for: {user_question}"
        
        # Add explicit instruction to use conversation history if available
        if conversation_history:
            user_message += "\n\nIMPORTANT: Review the conversation history below to extract any filters or context that should be applied to this query. If the question references 'them', 'those', 'it', or 'that', find what it refers to in the previous messages and apply those filters."
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history BEFORE the user message so LLM can see it
        if conversation_history:
            # Include recent history (last N messages for context)
            recent_history = conversation_history[-settings.max_context_messages:]
            messages.extend(recent_history)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for consistent SQL generation
                max_tokens=200,  # SQL queries shouldn't be too long
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up SQL query (remove markdown code blocks if present)
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            elif sql_query.startswith("```"):
                sql_query = sql_query[3:]
            
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            logger.info(f"Generated SQL: {sql_query[:100]}...")
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            raise
    
    def generate_response(
        self,
        user_question: str,
        query_results: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate natural language response from query results.
        
        Args:
            user_question: Original user question
            query_results: Results from SQL query execution
            conversation_history: Previous conversation messages for context
        
        Returns:
            Natural language response
        """
        system_prompt = """You are a helpful data analyst assistant. You analyze Uber trip data and provide clear, concise answers to user questions.

Guidelines:
- Be conversational and friendly
- Use numbers and statistics from the data
- If no results found, explain that clearly
- Format numbers nicely (e.g., ₹1,234.56, 1,234 trips)
- Keep responses concise but informative
- If the data shows interesting patterns, mention them
"""
        
        # Format query results for the LLM
        if not query_results.get('success') or not query_results.get('data'):
            results_text = "No results found in the database."
        else:
            results_text = f"Query returned {query_results['row_count']} rows.\n\n"
            results_text += f"Columns: {', '.join(query_results['columns'])}\n\n"
            
            # Show all rows (or first 20 if many)
            rows_to_show = query_results['data'][:20]
            for i, row in enumerate(rows_to_show, 1):
                results_text += f"Row {i}:\n"
                for col, val in row.items():
                    results_text += f"  {col}: {val}\n"
                results_text += "\n"
            
            if query_results['row_count'] > 20:
                results_text += f"... and {query_results['row_count'] - 20} more rows\n"
        
        user_message = f"""User Question: {user_question}

Query Results:
{results_text}

Please provide a clear, natural language answer to the user's question based on these results."""
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            recent_history = conversation_history[-settings.max_context_messages:]
            messages.extend(recent_history)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Higher temperature for more natural responses
                max_tokens=settings.max_tokens,
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated response: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise


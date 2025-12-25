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
        # Build system prompt with schema information
        system_prompt = f"""You are a SQL query generator for analyzing Uber trip data.

Database Schema:
Table: {schema_info['table_name']}
Total Rows: {schema_info['total_rows']:,}

Columns:
"""
        for col in schema_info['columns']:
            system_prompt += f"  - {col['name']}: {col['type']} {'(nullable)' if col['nullable'] else '(required)'}\n"
        
        system_prompt += f"""
Sample Values:
- Booking Status: {', '.join(schema_info['sample_values']['booking_status'])}
- Vehicle Types: {', '.join(schema_info['sample_values']['vehicle_type'])}
- Payment Methods: {', '.join(schema_info['sample_values']['payment_method'])}

Rules:
1. Generate ONLY valid SQL SELECT queries
2. Use the table name 'uber_trips' (not {schema_info['table_name']})
3. For date comparisons, use the 'date' column (DateTime type)
4. For successful rides, filter by: booking_status = 'Success'
5. Always use proper SQL syntax
6. Return ONLY the SQL query, no explanations or markdown
7. Use LIMIT if the query might return many rows (default: 100)
8. For aggregations, use appropriate functions (COUNT, SUM, AVG, etc.)

Example queries:
- "How many successful rides?" → SELECT COUNT(*) FROM uber_trips WHERE booking_status = 'Success'
- "Average booking value for Prime SUV" → SELECT AVG(booking_value) FROM uber_trips WHERE vehicle_type = 'Prime SUV' AND booking_status = 'Success' AND booking_value IS NOT NULL
- "Top 5 pickup locations" → SELECT pickup_location, COUNT(*) as count FROM uber_trips WHERE pickup_location IS NOT NULL GROUP BY pickup_location ORDER BY count DESC LIMIT 5
"""
        
        # Build user message
        user_message = f"Generate a SQL query for: {user_question}"
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            # Add last few messages for context (limit to avoid token limits)
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


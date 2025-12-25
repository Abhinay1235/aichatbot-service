"""Chat service that combines OpenAI and SQL services."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

from src.services.openai_service import OpenAIService
from src.services.sql_service import SQLService, SQLServiceError

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions with SQL query generation."""
    
    def __init__(self, db: Session):
        """Initialize chat service with database session."""
        self.db = db
        self.openai_service = OpenAIService()
        self.sql_service = SQLService(db)
    
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: User's question/message
            conversation_history: Previous conversation messages
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Step 1: Get schema information for context
            schema_info = self.sql_service.get_schema_info()
            
            # Step 2: Generate SQL query from user question
            logger.info(f"Generating SQL for question: {user_message}")
            sql_query = self.openai_service.generate_sql_query(
                user_question=user_message,
                schema_info=schema_info,
                conversation_history=conversation_history
            )
            
            # Step 3: Execute SQL query safely
            logger.info(f"Executing SQL query: {sql_query}")
            query_results = self.sql_service.execute_query(sql_query)
            
            # Step 4: Generate natural language response
            logger.info("Generating natural language response")
            response_text = self.openai_service.generate_response(
                user_question=user_message,
                query_results=query_results,
                conversation_history=conversation_history
            )
            
            return {
                'success': True,
                'response': response_text,
                'sql_query': sql_query,
                'query_results': {
                    'row_count': query_results['row_count'],
                    'columns': query_results['columns']
                }
            }
            
        except SQLServiceError as e:
            logger.error(f"SQL service error: {e}")
            # Try to get a helpful error message from OpenAI
            try:
                error_response = self.openai_service.generate_response(
                    user_question=user_message,
                    query_results={
                        'success': False,
                        'data': [],
                        'error': str(e)
                    },
                    conversation_history=conversation_history
                )
                return {
                    'success': False,
                    'response': error_response,
                    'error': str(e),
                    'sql_query': None
                }
            except Exception as openai_error:
                logger.error(f"Error generating error response: {openai_error}")
                return {
                    'success': False,
                    'response': f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question.",
                    'error': str(e),
                    'sql_query': None
                }
        
        except Exception as e:
            logger.error(f"Unexpected error in chat service: {e}")
            return {
                'success': False,
                'response': "I'm sorry, I encountered an unexpected error. Please try again.",
                'error': str(e),
                'sql_query': None
            }


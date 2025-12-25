"""Chat service that combines OpenAI and SQL services."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

from src.services.openai_service import OpenAIService
from src.services.sql_service import SQLService, SQLServiceError
from src.services.session_service import SessionService

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions with SQL query generation."""
    
    def __init__(self, db: Session):
        """Initialize chat service with database session."""
        self.db = db
        self.openai_service = OpenAIService()
        self.sql_service = SQLService(db)
        self.session_service = SessionService(db)
    
    def process_message(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: User's question/message
            session_id: Optional session ID for conversation context
            conversation_history: Optional explicit conversation history (overrides session)
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Get or create session
            if session_id:
                if not self.session_service.session_exists(session_id):
                    # Create session with the provided ID if it doesn't exist
                    self.session_service.create_session(session_id=session_id)
                # Get conversation history from session if not explicitly provided
                if conversation_history is None:
                    conversation_history = self.session_service.get_recent_conversation_history(session_id)
            else:
                # Create new session if none provided
                session_id = self.session_service.create_session()
            
            # Step 1: Get schema information for context
            schema_info = self.sql_service.get_schema_info()
            
            # Step 2: Generate SQL query from user question
            logger.info(f"Generating SQL for question: {user_message} (session: {session_id})")
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
            
            # Step 5: Store messages in session
            if session_id:
                self.session_service.add_message(session_id, 'user', user_message)
                self.session_service.add_message(session_id, 'assistant', response_text)
            
            return {
                'success': True,
                'response': response_text,
                'session_id': session_id,
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
                # Store error messages in session too
                if session_id:
                    self.session_service.add_message(session_id, 'user', user_message)
                    self.session_service.add_message(session_id, 'assistant', error_response)
                
                return {
                    'success': False,
                    'response': error_response,
                    'session_id': session_id,
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


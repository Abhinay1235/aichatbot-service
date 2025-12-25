"""Session service for managing conversation sessions."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import uuid
import logging

from src.database.models import Session as SessionModel, Message as MessageModel
from src.config import settings

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing chat sessions and conversation history."""
    
    def __init__(self, db: Session):
        """Initialize session service with database session."""
        self.db = db
        self.max_context_messages = settings.max_context_messages
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new chat session.
        
        Args:
            session_id: Optional session ID (if not provided, generates UUID)
        
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Check if session already exists
        if self.session_exists(session_id):
            logger.warning(f"Session {session_id} already exists")
            return session_id
        
        session = SessionModel(
            session_id=session_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionModel]:
        """Get session by ID."""
        return self.db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return self.get_session(session_id) is not None
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> MessageModel:
        """
        Add a message to a session.
        
        Args:
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
        
        Returns:
            Created message object
        """
        # Ensure session exists
        session = self.get_session(session_id)
        if not session:
            # Create session if it doesn't exist
            session = SessionModel(
                session_id=session_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(session)
            self.db.flush()
        
        # Create message
        message = MessageModel(
            session_id=session_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        
        self.db.add(message)
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        logger.info(f"Added {role} message to session {session_id}")
        return message
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages to return (uses max_context_messages if None)
        
        Returns:
            List of messages in format [{"role": "user", "content": "..."}, ...]
        """
        if limit is None:
            limit = self.max_context_messages
        
        messages = self.db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).order_by(MessageModel.created_at.asc()).limit(limit).all()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def get_recent_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation history (last N messages).
        This is used for context window management.
        
        Args:
            session_id: Session ID
            limit: Maximum number of recent messages (uses max_context_messages if None)
        
        Returns:
            List of recent messages
        """
        if limit is None:
            limit = self.max_context_messages
        
        messages = self.db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).order_by(MessageModel.created_at.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def get_all_sessions(self, limit: int = 100) -> List[SessionModel]:
        """Get all sessions, ordered by most recent."""
        return self.db.query(SessionModel).order_by(
            desc(SessionModel.updated_at)
        ).limit(limit).all()
    
    def get_session_messages(self, session_id: str) -> List[MessageModel]:
        """Get all messages for a session."""
        return self.db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).order_by(MessageModel.created_at.asc()).all()
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages.
        
        Args:
            session_id: Session ID to delete
        
        Returns:
            True if deleted, False if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        
        logger.info(f"Deleted session: {session_id}")
        return True
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a session."""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        messages = self.get_session_messages(session_id)
        user_messages = [m for m in messages if m.role == 'user']
        assistant_messages = [m for m in messages if m.role == 'assistant']
        
        return {
            'session_id': session_id,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat(),
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages)
        }


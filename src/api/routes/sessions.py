"""Session API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database.session import get_db
from src.services.session_service import SessionService
from src.api.models import (
    SessionCreateRequest,
    SessionResponse,
    SessionListResponse,
    ConversationResponse,
    MessageResponse
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    try:
        session_service = SessionService(db)
        session_id = session_service.create_session()
        
        session = session_service.get_session(session_id)
        return SessionResponse(
            session_id=session_id,
            created_at=session.created_at.isoformat(),
            message_count=0
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating session: {str(e)}"
        )


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all chat sessions."""
    try:
        session_service = SessionService(db)
        sessions = session_service.get_all_sessions(limit=limit)
        
        session_responses = []
        for session in sessions:
            messages = session_service.get_session_messages(session.session_id)
            session_responses.append(
                SessionResponse(
                    session_id=session.session_id,
                    created_at=session.created_at.isoformat(),
                    message_count=len(messages)
                )
            )
        
        return SessionListResponse(sessions=session_responses)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing sessions: {str(e)}"
        )


@router.get("/{session_id}", response_model=ConversationResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation history for a session."""
    try:
        session_service = SessionService(db)
        
        if not session_service.session_exists(session_id):
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        messages = session_service.get_session_messages(session_id)
        
        message_responses = [
            MessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ]
        
        return ConversationResponse(
            session_id=session_id,
            messages=message_responses
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting session: {str(e)}"
        )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a session and all its messages."""
    try:
        session_service = SessionService(db)
        
        if not session_service.delete_session(session_id):
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {"message": f"Session {session_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting session: {str(e)}"
        )


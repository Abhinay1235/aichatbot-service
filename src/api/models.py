"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatMessage(BaseModel):
    """Model for a chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's question or message", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    conversation_history: Optional[List[ChatMessage]] = Field(
        None,
        description="Previous conversation messages for context"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    success: bool = Field(..., description="Whether the request was successful")
    response: str = Field(..., description="Chatbot's response")
    sql_query: Optional[str] = Field(None, description="Generated SQL query (for debugging)")
    query_results: Optional[Dict[str, Any]] = Field(
        None,
        description="Query results metadata (row count, columns)"
    )
    error: Optional[str] = Field(None, description="Error message if request failed")


class SessionCreateRequest(BaseModel):
    """Request model for creating a new session."""
    pass  # Sessions are auto-created with unique IDs


class SessionResponse(BaseModel):
    """Response model for session information."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    message_count: int = Field(..., description="Number of messages in session")


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionResponse] = Field(..., description="List of sessions")


class MessageResponse(BaseModel):
    """Response model for a message."""
    id: int
    session_id: str
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    """Response model for conversation history."""
    session_id: str
    messages: List[MessageResponse]


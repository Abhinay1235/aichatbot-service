"""Chat API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from src.database.session import get_db
from src.services.chat_service import ChatService
from src.api.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot and get a response.
    
    The chatbot will:
    1. Convert your natural language question to SQL
    2. Execute the query on the Uber trip data
    3. Generate a natural language response based on the results
    """
    try:
        chat_service = ChatService(db)
        
        # Convert conversation history format if provided
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # Process the message
        result = chat_service.process_message(
            user_message=request.message,
            session_id=request.session_id,
            conversation_history=conversation_history
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )


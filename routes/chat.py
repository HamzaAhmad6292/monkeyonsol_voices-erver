import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import sys
import os

# Add the parent directory to the path to import schemas and services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import ChatRequest, ChatResponse, ChatMessage
from services.groq_service import GroqService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Create a chat completion using Groq API
    """
    try:
        groq_service = GroqService()
        
        # Validate request
        if not request.messages or not isinstance(request.messages, list):
            raise HTTPException(
                status_code=400,
                detail="Messages array is required and must be an array"
            )
        
        if not isinstance(request.model, str) or not request.model.strip():
            raise HTTPException(
                status_code=400,
                detail="Model must be a non-empty string"
            )
        
        if not isinstance(request.temperature, (int, float)) or request.temperature < 0 or request.temperature > 2:
            raise HTTPException(
                status_code=400,
                detail="Temperature must be a number between 0 and 2"
            )
        
        if not isinstance(request.max_tokens, int) or request.max_tokens <= 0:
            raise HTTPException(
                status_code=400,
                detail="max_tokens must be a positive number"
            )
        
        logger.info(f"Processing chat request with model: {request.model}")
        logger.info(f"Messages count: {len(request.messages)}")
        logger.info(f"Temperature: {request.temperature}, Max tokens: {request.max_tokens}")
        
        # Convert Pydantic models to dictionaries for Groq API
        messages = []
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Create chat completion
        result = groq_service.create_chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Convert response back to Pydantic model
        response_message = ChatMessage(
            role=result['message']['role'],
            content=result['message']['content']
        )
        
        return ChatResponse(
            message=response_message,
            usage=result.get('usage')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        ) 
import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from groq import Groq

logger = logging.getLogger(__name__)

class GroqService:
    """Service class for interacting with Groq API"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.error("GROQ_API_KEY is not set")
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.client = Groq(api_key=self.api_key)
    
    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Create a chat completion using Groq API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Groq model to use
            temperature: Temperature for generation (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict containing the response and usage information
        """
        try:
            logger.info(f"Creating chat completion with model: {model}")
            logger.info(f"Messages count: {len(messages)}")
            logger.info(f"Temperature: {temperature}, Max tokens: {max_tokens}")
            
            # Validate inputs
            if not messages or not isinstance(messages, list):
                raise HTTPException(
                    status_code=400,
                    detail="Messages array is required and must be an array"
                )
            
            if not isinstance(model, str) or not model.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Model must be a non-empty string"
                )
            
            if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
                raise HTTPException(
                    status_code=400,
                    detail="Temperature must be a number between 0 and 2"
                )
            
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="max_tokens must be a positive number"
                )
            
            # Create completion
            completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            response_content = completion.choices[0].message.content if completion.choices else None
            
            if not response_content:
                raise HTTPException(
                    status_code=502,
                    detail="No response received from Groq API"
                )
            
            logger.info(f"Successfully generated response: {response_content[:100]}...")
            
            return {
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "usage": completion.usage.dict() if completion.usage else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch completion from Groq API: {str(e)}"
            ) 
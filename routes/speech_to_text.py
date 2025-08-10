import base64
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import sys
import os

# Add the parent directory to the path to import schemas and services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import SpeechToTextRequest, SpeechToTextResponse, ErrorResponse
from services.elevenlabs_service import ElevenLabsService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(
    file: Optional[UploadFile] = File(None),
    model_id: str = Form("scribe_v1"),
    request: Optional[SpeechToTextRequest] = None
):
    """
    Convert speech to text using ElevenLabs API
    
    Supports both multipart form data (file upload) and JSON with base64 audio data
    """
    try:
        elevenlabs_service = ElevenLabsService()
        
        # Check if this is a multipart form data request
        if file:
            logger.info(f"Processing multipart form data: {file.filename}, size: {file.size}")
            
            if not file:
                raise HTTPException(status_code=400, detail="Audio file is required")
            
            # Read file content
            audio_data = await file.read()
            
            if len(audio_data) == 0:
                raise HTTPException(status_code=400, detail="Invalid audio data - empty buffer")
            
            logger.info(f"Audio buffer size: {len(audio_data)} bytes")
            
        else:
            # Handle JSON request with base64 audio data
            if not request or not request.audio:
                raise HTTPException(status_code=400, detail="Audio data is required")
            
            logger.info(f"Processing base64 audio data, format: {request.format}")
            
            # Validate audio data format
            if not isinstance(request.audio, str):
                raise HTTPException(status_code=400, detail="Audio data must be a base64 string")
            
            # Convert base64 to buffer
            try:
                audio_data = base64.b64decode(request.audio)
            except Exception as e:
                raise HTTPException(status_code=400, detail="Invalid base64 audio data")
            
            logger.info(f"Base64 audio length: {len(request.audio)}")
            logger.info(f"Decoded buffer length: {len(audio_data)}")
            
            if len(audio_data) == 0:
                raise HTTPException(status_code=400, detail="Invalid audio data - empty buffer after decoding")
            
            model_id = request.model_id
        
        # Process with ElevenLabs
        result = await elevenlabs_service.speech_to_text(audio_data, model_id)
        
        return SpeechToTextResponse(
            text=result['text'],
            confidence=result['confidence']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech-to-text error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Speech-to-text processing failed: {str(e)}"
        ) 
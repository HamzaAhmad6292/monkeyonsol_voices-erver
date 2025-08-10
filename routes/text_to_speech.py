import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import Dict, Any
import sys
import os

# Add the parent directory to the path to import schemas and services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import TextToSpeechRequest
from services.elevenlabs_service import ElevenLabsService
from services.openai_tts_service import OpenAITTSService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech using the selected provider"""
    try:
        provider = (request.provider or "elevenlabs").lower()
        
        if not request.text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        logger.info(f"Processing text-to-speech provider={provider} voice={request.voice_name}")
        logger.info(f"Text length: {len(request.text)} characters")
        if provider == "openai":
            # OpenAI TTS path
            openai_service = OpenAITTSService()

            # Valid OpenAI voices: alloy, echo, echo, onyx, nova, shimmer
            selected_voice = request.voice_name or "echo"

            # Do not forward ElevenLabs-specific params to OpenAI
            model_id = request.model_id
            if model_id and model_id.startswith("eleven_"):
                logger.info("Ignoring ElevenLabs model id for OpenAI provider")
                model_id = None

            audio_data = await openai_service.text_to_speech(
                text=request.text,
                voice_name=selected_voice,
                model_id=model_id,
                output_format=(request.format or "mp3"),
                voice_settings=None,
            )
        else:
            # ElevenLabs path (default)
            elevenlabs_service = ElevenLabsService()

            # Get available voices
            voices = await elevenlabs_service.get_voices()
            logger.info(f"Available voices: {[v.get('name') for v in voices.get('voices', [])]}")

            # Find the requested voice
            voice = elevenlabs_service.get_voice_by_name(voices, request.voice_name)
            if not voice:
                available_voices = [v.get('name') for v in voices.get('voices', [])]
                raise HTTPException(
                    status_code=400,
                    detail=f"Voice '{request.voice_name}' not found. Available voices: {', '.join(available_voices)}"
                )

            logger.info(f"Found voice: {voice.get('name')} (ID: {voice.get('voice_id')})")

            # Convert voice settings to dict if needed
            voice_settings = None
            if request.voice_settings:
                voice_settings = {
                    "stability": request.voice_settings.stability,
                    "similarity_boost": request.voice_settings.similarity_boost,
                    "style": request.voice_settings.style,
                    "use_speaker_boost": request.voice_settings.use_speaker_boost,
                }

            # Use a valid model ID for ElevenLabs
            model_id = request.model_id or "eleven_multilingual_v2"
            if model_id == "eleven_monolingual_v2":
                model_id = "eleven_multilingual_v2"

            # Generate speech
            audio_data = await elevenlabs_service.text_to_speech(
                text=request.text,
                voice_id=voice['voice_id'],
                model_id=model_id,
                voice_settings=voice_settings,
            )
        
        # Return audio response
        media_type = "audio/mpeg" if (request.format or "mp3").lower() == "mp3" else "audio/wav"
        file_ext = (request.format or "mp3").lower()
        return Response(
            content=audio_data,
            media_type=media_type,
            headers={
                "Content-Length": str(len(audio_data)),
                "Content-Disposition": f"attachment; filename=speech.{file_ext}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text-to-speech error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Text-to-speech processing failed: {str(e)}"
        ) 
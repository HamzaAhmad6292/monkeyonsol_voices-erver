import os
import logging
import aiohttp
import base64
from typing import Optional, Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """Service class for interacting with ElevenLabs API"""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.error("ELEVENLABS_API_KEY is not set")
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
        
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def speech_to_text(self, audio_data: bytes, model_id: str = "scribe_v1") -> Dict[str, Any]:
        """
        Convert speech to text using ElevenLabs API
        
        Args:
            audio_data: Raw audio bytes
            model_id: ElevenLabs model ID
            
        Returns:
            Dict containing text and confidence
        """
        try:
            logger.info(f"Processing speech-to-text with model: {model_id}")
            logger.info(f"Audio data size: {len(audio_data)} bytes")
            
            if len(audio_data) == 0:
                raise HTTPException(status_code=400, detail="Invalid audio data - empty buffer")
            
            # Create form data
            data = aiohttp.FormData()
            data.add_field('file', audio_data, filename='audio.webm', content_type='audio/webm')
            data.add_field('model_id', model_id)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/speech-to-text",
                    headers={'xi-api-key': self.api_key},
                    data=data
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs STT API Error: {error_text}")
                        logger.error(f"Response status: {response.status}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to transcribe audio: {error_text}"
                        )
                    
                    result = await response.json()
                    
                    if not result.get('text'):
                        raise HTTPException(
                            status_code=500,
                            detail="No transcription received from ElevenLabs"
                        )
                    
                    logger.info(f"Successfully transcribed text: {result['text'][:100]}...")
                    return {
                        'text': result['text'],
                        'confidence': result.get('confidence', 0.0)
                    }
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Speech-to-text error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Speech-to-text processing failed: {str(e)}")
    
    async def get_voices(self) -> Dict[str, Any]:
        """
        Get available voices from ElevenLabs
        
        Returns:
            Dict containing available voices
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/voices",
                    headers={'xi-api-key': self.api_key}
                ) as response:
                    if not response.ok:
                        logger.error("Failed to fetch voices from ElevenLabs")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to fetch available voices"
                        )
                    
                    return await response.json()
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching voices: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch voices: {str(e)}")
    
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: str, 
        model_id: str = "eleven_monolingual_v2",
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            model_id: ElevenLabs model ID
            voice_settings: Voice settings dictionary
            
        Returns:
            Audio data as bytes
        """
        try:
            logger.info(f"Processing text-to-speech for voice: {voice_id}")
            logger.info(f"Text length: {len(text)} characters")
            
            if not voice_settings:
                voice_settings = {
                    "stability": 0.3,
                    "similarity_boost": 0.7,
                    "style": 0.8,
                    "use_speaker_boost": True
                }
            
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": voice_settings
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    headers={
                        'xi-api-key': self.api_key,
                        'Content-Type': 'application/json'
                    },
                    json=payload
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs TTS API Error: {error_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to convert text to speech: {error_text}"
                        )
                    
                    audio_data = await response.read()
                    logger.info(f"Successfully generated audio: {len(audio_data)} bytes")
                    return audio_data
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Text-to-speech processing failed: {str(e)}")
    
    def get_voice_by_name(self, voices: Dict[str, Any], voice_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a voice by name from the voices list
        
        Args:
            voices: Voices response from ElevenLabs
            voice_name: Name of the voice to find
            
        Returns:
            Voice dictionary if found, None otherwise
        """
        if not voices.get('voices'):
            return None
        
        for voice in voices['voices']:
            if voice.get('name') == voice_name:
                return voice
        
        return None 
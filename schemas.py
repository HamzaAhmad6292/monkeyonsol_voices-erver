from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

# Speech-to-Text Schemas
class SpeechToTextRequest(BaseModel):
    audio: Optional[str] = Field(None, description="Base64 encoded audio data")
    format: str = Field(default="webm", description="Audio format (webm, mp4, wav)")
    model_id: str = Field(default="scribe_v1", description="ElevenLabs model ID")

class SpeechToTextResponse(BaseModel):
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(default=0.0, description="Confidence score")

# Text-to-Speech Schemas
class VoiceSettings(BaseModel):
    stability: float = Field(default=0.3, ge=0.0, le=1.0, description="Voice stability")
    similarity_boost: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity boost")
    style: float = Field(default=0.8, ge=0.0, le=1.0, description="Style setting")
    use_speaker_boost: bool = Field(default=True, description="Use speaker boost")

class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice_name: str = Field(default="Bill", description="Voice name to use")
    model_id: Optional[str] = Field(
        default=None,
        description=(
            "TTS model ID (provider-specific). Leave null to use provider default. "
            "For ElevenLabs: e.g., 'eleven_multilingual_v2'. For OpenAI: 'tts-1', 'tts-1-hd', 'gpt-4o-mini-tts'."
        ),
    )
    voice_settings: VoiceSettings = Field(default_factory=VoiceSettings, description="Voice settings")
    provider: str = Field(default="elevenlabs", description="TTS provider to use (elevenlabs|openai)")
    format: str = Field(default="mp3", description="Output audio format (mp3|wav|ogg)")

# Chat Schemas
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Array of chat messages")
    model: str = Field(default="llama-3.3-70b-versatile", description="LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int = Field(default=1024, gt=0, description="Maximum tokens to generate")

class ChatResponse(BaseModel):
    message: ChatMessage = Field(..., description="Generated response message")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")

# Error Schemas
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    status: Optional[int] = Field(None, description="HTTP status code")

# Health Check Schemas
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    services: Dict[str, str] = Field(..., description="Service availability") 
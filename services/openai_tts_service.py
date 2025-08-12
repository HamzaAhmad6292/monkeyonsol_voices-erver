import os
import logging
import aiohttp
from typing import Optional, Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class OpenAITTSService:
    """Service class for interacting with OpenAI TTS API"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set")
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Allowed OpenAI TTS models (expand as OpenAI adds more)
        self.allowed_models = {"gpt-4o-mini-tts"}

        # Default model for TTS; use a safe value if an invalid one is configured
        configured_default = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
        if configured_default not in self.allowed_models:
            logger.warning(
                f"Invalid OPENAI_TTS_MODEL '{configured_default}' configured. Falling back to 'gpt-4o-mini-tts'."
            )
            self.default_model = "gpt-4o-mini-tts"
        else:
            self.default_model = configured_default
        self.base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        # Optional style instructions that guide the TTS voice delivery
        # Default to the user's requested behavior
        self.style_instructions = os.getenv(
            "OPENAI_TTS_INSTRUCTIONS", "Speak in a artistic cartoon dog way"
        ).strip()

    def _normalize_voice_name(self, voice_name: str) -> str:
        """Normalize to OpenAI-supported lowercase voice names; map simple aliases."""
        if not voice_name:
            return "ballad"
        name = voice_name.strip().lower()
        alias_to_voice = {
            # Common aliases for a youthful/young-boy style
            "boy": "ballad",
            "young": "ballad",
            "kid": "ballad",
            "child": "ballad",
            "young_boy": "ballad",
            "young-boy": "ballad",
        }
        return alias_to_voice.get(name, name)

    async def text_to_speech(
        self,
        text: str,
        voice_name: str = "ballad",
        model_id: Optional[str] = None,
        output_format: str = "mp3",
        voice_settings: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Convert text to speech using OpenAI TTS
        """
        try:
            # Validate and select model
            if model_id and model_id in self.allowed_models:
                model = model_id
            else:
                if model_id and model_id not in self.allowed_models:
                    logger.warning(
                        f"Ignoring unsupported OpenAI TTS model '{model_id}'. Using default '{self.default_model}'."
                    )
                model = self.default_model

            # Ensure voice is a supported preset (normalize common aliases first)
            voice_name = self._normalize_voice_name(voice_name)
            allowed_voices = {
                "alloy",
                "echo",
                "fable",
                "onyx",
                "nova",
                "shimmer",
                "coral",
                "verse",
                "ballad",
                "ash",
                "sage",
            }
            if voice_name not in allowed_voices:
                logger.warning(
                    f"Unsupported OpenAI voice '{voice_name}'. Falling back to 'ballad'."
                )
                voice_name = "ballad"

            # Validate output format
            allowed_formats = {"mp3", "wav", "ogg", "flac", "aac", "opus", "pcm"}
            if output_format not in allowed_formats:
                logger.warning(
                    f"Unsupported output format '{output_format}'. Falling back to 'mp3'."
                )
                output_format = "mp3"
            # Optionally prepend style instructions to guide delivery
            prompt_text = text
            if self.style_instructions:
                prompt_text = f"[Style: {self.style_instructions}]\n{text}"

            json_payload: Dict[str, Any] = {
                "model": model,
                "voice": voice_name,
                "input": prompt_text,
                "format": output_format,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/audio/speech",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=json_payload,
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"OpenAI TTS API Error: {error_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to convert text to speech: {error_text}",
                        )

                    audio_data = await response.read()
                    logger.info(
                        f"OpenAI TTS: generated audio {len(audio_data)} bytes with model {model} and voice {voice_name}"
                    )
                    return audio_data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OpenAI TTS error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI TTS processing failed: {str(e)}")



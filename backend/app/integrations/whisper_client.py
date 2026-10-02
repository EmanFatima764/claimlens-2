from __future__ import annotations

from typing import Any


class WhisperClient:
    """Placeholder client for speech-to-text and audio transcription.

    This will eventually connect to Whisper or a compatible transcription provider.
    """

    async def transcribe(self, audio_path: str) -> dict[str, Any]:
        return {
            "audio_path": audio_path,
            "transcript": "",
            "status": "not_implemented",
        }

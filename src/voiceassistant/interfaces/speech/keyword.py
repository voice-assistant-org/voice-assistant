"""Keyword detector component."""

import struct

import pvporcupine

from voiceassistant.config import Config
from voiceassistant.exceptions import ConfigValidationError


class KeywordDetector:
    """Keyword detector."""

    def __init__(self) -> None:
        """Create Keyword detector object."""
        keyword = Config.triggerword.picovoice.word

        if keyword not in pvporcupine.KEYWORDS:
            raise ConfigValidationError(f"available keywords are {pvporcupine.KEYWORDS}")

        self._detector = pvporcupine.create(
            keywords=[keyword], sensitivities=[Config.triggerword.picovoice.sensitivity]
        )

        self.rate = self._detector.sample_rate
        self.chunk_size = self._detector.frame_length

    def process(self, audio_chunk: bytes) -> int:
        """Process audio chunk.

        Returns:
            index of a recognized keyword if recognized, -1 otherwise
        """
        pcm = struct.unpack_from("h" * self.chunk_size, audio_chunk)
        return self._detector.process(pcm)  # type: ignore

    def not_detected(self, audio_chunk: bytes) -> bool:
        """Determine if keyword was not detected."""
        return self.process(audio_chunk) < 0

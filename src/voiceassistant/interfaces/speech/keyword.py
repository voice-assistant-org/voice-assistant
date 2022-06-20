"""Keyword detector component."""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING

import pvporcupine

from voiceassistant.exceptions import ConfigValidationError

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


class KeywordDetector:
    """Keyword detector."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Create Keyword detector object."""
        config = vass.config.triggerword.picovoice

        if config.word not in pvporcupine.KEYWORDS:
            raise ConfigValidationError(f"available keywords are {pvporcupine.KEYWORDS}")

        self._detector = pvporcupine.create(
            keywords=[config.word], sensitivities=[config.sensitivity]
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

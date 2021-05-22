"""Keyword detector component."""

import struct

import pvporcupine

from voiceassistant.utils.config import Config


class KeywordDetector:
    """Keyword detector."""

    def __init__(self) -> None:
        """Create Keyword detector object."""
        keyword = Config.get("keyword", "jarvis")
        self._detector = pvporcupine.create(keywords=[keyword])
        self.rate = self._detector.sample_rate
        self.chunk_size = self._detector.frame_length

    def process(self, audio_chunk: bytes) -> int:
        """Process audio chunk.

        Returns:
            index of a recognized keyword if recognized, -1 otherwise
        """
        pcm = struct.unpack_from("h" * self.chunk_size, audio_chunk)
        return self._detector.process(pcm)  # type: ignore

"""Keyword detector component."""

import struct
from typing import List

import pvporcupine


class KeywordDetector:
    """Keyword detector."""

    def __init__(self, keywords: List) -> None:
        """Create Keyword detector object."""
        self._detector = pvporcupine.create(keywords=keywords)
        self.rate = self._detector.sample_rate
        self.chunk_size = self._detector.frame_length

    def process(self, audio_chunk: bytes) -> int:
        """Process audio chunk.

        Returns:
            index of a recognized keyword if recognized, -1 otherwise
        """
        pcm = struct.unpack_from("h" * self.chunk_size, audio_chunk)
        return self._detector.process(pcm)  # type: ignore

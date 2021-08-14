"""Add-On functions for speech interface."""

from usb.core import USBError

from voiceassistant.interfaces.speech import (
    pause_microphone_stream,
    resume_microphone_stream,
)

try:
    from pixel_ring import pixel_ring

    class PixelRingState:
        """Host pixel ring states."""

        off = 0
        speak = 1
        think = 2

    pixel_ring.off()
    ring_state = PixelRingState.off

    _mic_is_respeaker = True
except (USBError, ValueError, FileNotFoundError, PermissionError) as e:
    print(f"No ReSpeaker Microphone detected or not able to connect: {e}")
    _mic_is_respeaker = False


def processing_starts() -> None:
    """Do before NLP starts."""
    if _mic_is_respeaker:
        pixel_ring.speak()
        global ring_state
        ring_state = PixelRingState.speak


def processing_ends() -> None:
    """Do when NLP ends."""
    if _mic_is_respeaker:
        pixel_ring.off()
        global ring_state
        ring_state = PixelRingState.off


def tts_starts() -> None:
    """Do before voice output starts."""
    pause_microphone_stream()
    if _mic_is_respeaker:
        pixel_ring.think()


def tts_ends() -> None:
    """Do when voice output ends."""
    resume_microphone_stream()
    if _mic_is_respeaker:
        if ring_state == PixelRingState.speak:
            pixel_ring.speak()
        else:
            pixel_ring.off()

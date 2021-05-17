"""Add-On functions for speech interface."""

from usb.core import USBError

try:
    from pixel_ring import pixel_ring

    pixel_ring.off()
    _mic_is_respeaker = True
except (USBError, ValueError, FileNotFoundError) as e:
    print(f"No ReSpeaker Microphone detected: {e}")
    _mic_is_respeaker = False


def processing_starts() -> None:
    """Do before NLP starts."""
    if _mic_is_respeaker:
        pixel_ring.speak()


def processing_ends() -> None:
    """Do when NLP ends."""
    if _mic_is_respeaker:
        pixel_ring.off()


def tts_starts() -> None:
    """Do before voice output starts."""
    if _mic_is_respeaker:
        pixel_ring.think()


def tts_ends() -> None:
    """Do when voice output ends."""
    if _mic_is_respeaker:
        pixel_ring.speak()

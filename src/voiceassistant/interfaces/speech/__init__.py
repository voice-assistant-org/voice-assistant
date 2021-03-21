"""Voice interface subpackage."""

from .keyword import KeywordDetector
from .microphone_stream import MicrophoneStream
from .speech_to_text import RecognitionString, SpeechToText
from .text_to_speech import TextToSpeech


class SpeechInterface:
    """Speech interface."""

    def __init__(self, rate: int):
        """Init."""
        self.sst = SpeechToText(rate)
        self.tts = TextToSpeech()

    def output(self, text: str) -> None:
        """Pronounce text."""
        self.tts.say(text)

    def input(self) -> str:
        """Recognize speech."""
        pass


__all__ = [
    "KeywordDetector",
    "RecognitionString",
    "SpeechToText",
    "TextToSpeech",
    "SpeechInterface",
    "MicrophoneStream",
]

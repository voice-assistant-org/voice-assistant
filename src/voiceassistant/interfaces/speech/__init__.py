"""Voice interface subpackage."""

import traceback

from voiceassistant import addons
from voiceassistant.config import Config
from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.nlp import NaturalLanguageProcessor
from voiceassistant.utils.debug import print_and_flush

from .keyword import KeywordDetector
from .microphone_stream import MicrophoneStream
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech


class SpeechInterface(InterfaceIO):
    """Speech interface."""

    def __init__(self) -> None:
        """Init."""
        self.keyword_detector = KeywordDetector()
        self.sst = SpeechToText(self.keyword_detector.rate)
        self.tts = TextToSpeech()

    def input(self) -> str:
        """Recognize speech."""
        pass

    @addons.call_at(start=addons.speech.tts_starts, end=addons.speech.tts_ends)
    def output(self, text: str, cache: bool = False) -> None:
        """Pronounce text."""
        self.tts.say(text, cache)

    def run(self) -> None:
        """Listen for keyword and process speech."""
        while True:
            print("Creating microphone stream")
            with MicrophoneStream(
                rate=self.keyword_detector.rate,
                chunk=self.keyword_detector.chunk_size,
                rolling_window_sec=Config.get("prerecord_seconds", 3),
            ) as stream:
                self.keyword_detector.wait_untill_detected(stream, self)
                self._process_speech(stream)

    @addons.call_at(
        start=addons.speech.processing_starts,
        end=addons.speech.processing_ends,
    )
    def _process_speech(self, stream: MicrophoneStream) -> None:
        with NaturalLanguageProcessor() as nlp:
            try:
                for transcript in self.sst.recognize_from_stream(stream):
                    print_and_flush(transcript)
                    nlp.process_next_transcript(
                        transcript=transcript, interface=self
                    )
            except Exception:
                traceback.print_exc()
                self.output("Error occured", cache=True)


__all__ = ["SpeechInterface"]

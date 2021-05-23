"""Voice Assistant core components."""

import threading
import traceback

import voiceassistant.skills  # NOQA
from voiceassistant.interfaces.http import HttpInterface
from voiceassistant.interfaces.speech import (
    KeywordDetector,
    MicrophoneStream,
    SpeechInterface,
)
from voiceassistant.nlp import NaturalLanguageProcessor
from voiceassistant.utils.config import Config
from voiceassistant.utils.debug import print_and_flush


class VoiceAssistant:
    """Voice Assistant root class."""

    def __init__(self) -> None:
        """Initialize Voice Assistant components."""
        self.keyword_detector = KeywordDetector()
        self.speech = SpeechInterface(rate=self.keyword_detector.rate)
        self.http = HttpInterface(self)

    def run(self) -> None:
        """Run Voice Assistant jobs in separate threads."""
        jobs = (
            self._speech_interface_loop,
            self.http.run,
        )
        for job in jobs:
            threading.Thread(target=job).start()

    def _speech_interface_loop(self) -> None:
        """Listen for keyword and process speech."""
        while True:
            print("Creating microphone stream")
            with MicrophoneStream(
                rate=self.keyword_detector.rate,
                chunk=self.keyword_detector.chunk_size,
                rolling_window_sec=Config.get("prerecord_seconds", 3),
            ) as stream:
                while self.keyword_detector.process(stream.read()) < 0:
                    pass
                print("Hotword detected.")
                with NaturalLanguageProcessor() as nlp:
                    try:
                        for (
                            transcript
                        ) in self.speech.sst.recognize_from_stream(stream):
                            print_and_flush(transcript)
                            nlp.process_next_transcript(
                                transcript=transcript, interface=self.speech
                            )
                    except Exception:
                        traceback.print_exc()
                        self.speech.output("Error occured")

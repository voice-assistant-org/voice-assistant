"""Voice Assistant core components."""

import src.skills  # NOQA
from src.interfaces.speech import (
    KeywordDetector,
    MicrophoneStream,
    SpeechInterface,
)
from src.nlp import NaturalLanguageProcessor
from src.utils.debug import print_and_flush


def run_voice_assistant() -> None:
    """Run Voice Assistant."""
    keyword_detector = KeywordDetector(keywords=["jarvis"])
    speech = SpeechInterface(rate=keyword_detector.rate)

    while True:
        print("Creating microphone stream")
        with MicrophoneStream(
            keyword_detector.rate, keyword_detector.chunk_size
        ) as stream:
            while keyword_detector.process(stream.read()) < 0:
                pass
            print("Hotword detected.")
            with NaturalLanguageProcessor() as nlp:
                for transcript in speech.sst.recognize_from_stream(stream):
                    print_and_flush(transcript)
                    nlp.process_next_transcript(
                        transcript=transcript, interface=speech
                    )

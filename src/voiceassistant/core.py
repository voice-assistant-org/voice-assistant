"""Voice Assistant core components."""

import voiceassistant.skills  # NOQA
from voiceassistant.interfaces.speech import (
    KeywordDetector,
    MicrophoneStream,
    SpeechInterface,
)
from voiceassistant.nlp import NaturalLanguageProcessor
from voiceassistant.utils.debug import print_and_flush


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
                try:
                    for transcript in speech.sst.recognize_from_stream(stream):
                        print_and_flush(transcript)
                        nlp.process_next_transcript(
                            transcript=transcript, interface=speech
                        )
                except Exception as e:
                    print(e)
                    speech.output("Error occured")

"""Voice Assistant core components."""

import threading

import voiceassistant.skills  # NOQA
from voiceassistant.interfaces import HttpInterface, SpeechInterface


class VoiceAssistant:
    """Voice Assistant root class."""

    def __init__(self) -> None:
        """Initialize Voice Assistant components."""
        self.speech = SpeechInterface()
        self.http = HttpInterface(self)

    def run(self) -> None:
        """Run Voice Assistant jobs in separate threads."""
        jobs = (
            self.speech.run,
            self.http.run,
        )
        for job in jobs:
            threading.Thread(target=job).start()

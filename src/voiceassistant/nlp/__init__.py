"""Natural language handler subpackage."""

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, List, Tuple, Type

from voiceassistant.utils.datastruct import RecognitionString

from .base import BaseNLP, NlpResult
from .regex import RegexNLP

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.interfaces.base import InterfaceIO


class NaturalLanguageComponent:
    def __init__(self, vass: VoiceAssistant) -> None:
        self._vass = vass
        self.regex = RegexNLP(vass)
        self._processors = (self.regex,)

    def continuous_handler(self, interface: "InterfaceIO") -> ContinuousLanguageHandler:
        """Get continuos natural language handler.

        Usecase: transcripts from continuos speech recognition.
        """
        return ContinuousLanguageHandler(self._vass, interface, self._processors)

    def process(self, transcript: RecognitionString) -> None:
        """Handle a single transcript.

        Usecase: a message from chatbot interface.
        """
        raise NotImplementedError


class ContinuousLanguageHandler:
    """Class to take action based on natural language text."""

    def __init__(
        self, vass: VoiceAssistant, interface: "InterfaceIO", nlp_processors: Tuple[BaseNLP, ...]
    ) -> None:
        """Init."""
        self._vass = vass
        self._interface = interface
        self._processors = nlp_processors

    def __enter__(self):  # type: ignore
        """Start natural language handler."""
        self._processed_results: List[NlpResult] = []
        self._last_text_length = 0
        return self

    def __exit__(
        self, type: Type[BaseException], value: BaseException, traceback: TracebackType
    ) -> None:
        """Stop natural language processor."""
        pass

    def handle_next(self, transcript: RecognitionString) -> None:
        """Handle a sequence of transcripts.

        Each continuously recognized transcript is processed
        while user is speaking. Skill will be executed in two cases:
            1) transcript is complete (has enough information)
            2) transcript is final (user stopped speaking)
        """
        transcript = self._preprocess_transcript(transcript)

        for nlp_processor in self._processors:
            nlp_result = nlp_processor.process(transcript)

            if not nlp_result:
                continue

            if nlp_result in self._processed_results:
                continue

            if nlp_result.is_complete or transcript.is_final:
                self._make_record(transcript, nlp_result)
                self._vass.skills.run(
                    name=nlp_result.intent,
                    entities=nlp_result.entities,
                    interface=self._interface,
                )

    def _preprocess_transcript(self, text: RecognitionString) -> RecognitionString:
        """Remove part of transcript that was already processed."""
        # fmt: off
        return RecognitionString(
            text[self._last_text_length:].lower(), is_final=text.is_final
        )
        # fmt: on

    def _make_record(self, transcript: RecognitionString, nlp_result: NlpResult) -> None:
        """Make record of a processed transcript."""
        self._processed_results.append(nlp_result)
        self._last_text_length = len(transcript)


__all__ = ["NaturalLanguageHandler"]
